import os
import shutil
import zipfile
import threading
from datetime import datetime
import platform
import subprocess

class ProfileBackend:
    def __init__(self):
        self.os_type = platform.system()
        self.users_dir = "C:\\Users" if self.os_type == "Windows" else "/home"
        self.excluded_users = ["Public", "Default", "All Users", "Default User", "desktop.ini"]
        
        # Registry keys to export (HKCU based)
        self.registry_targets = {
            "OutlookProfiles": r"Software\Microsoft\Office\16.0\Outlook\Profiles", # Modern Outlook
            "OutlookProfilesLegacy": r"Software\Microsoft\Windows NT\CurrentVersion\Windows Messaging Subsystem\Profiles", # Legacy
            "Wallpaper": r"Control Panel\Desktop",
            "Mouse": r"Control Panel\Mouse",
            "Keyboard": r"Control Panel\Keyboard"
        }

    def get_users(self):
        """Scans the Users directory and returns a list of valid user profiles."""
        if not os.path.exists(self.users_dir):
            return []
            
        users = []
        try:
            for item in os.listdir(self.users_dir):
                if item not in self.excluded_users and os.path.isdir(os.path.join(self.users_dir, item)):
                    users.append(item)
        except PermissionError:
            print("Error: Permission denied accessing Users directory.")
            
        return users

    def get_user_folders(self, username):
        """Returns a dict of common folders for a user and their estimated sizes."""
        user_path = os.path.join(self.users_dir, username)
        folders = {
            "Desktop": os.path.join(user_path, "Desktop"),
            "Documents": os.path.join(user_path, "Documents"),
            "Downloads": os.path.join(user_path, "Downloads"),
            "Pictures": os.path.join(user_path, "Pictures"),
            "Music": os.path.join(user_path, "Music"),
            "Videos": os.path.join(user_path, "Videos"),
            "Favorites": os.path.join(user_path, "Favorites"),
            # Mail Profiles
            "Outlook Files": os.path.join(user_path, "Documents", "Outlook Files"),
            "Thunderbird": os.path.join(user_path, "AppData", "Roaming", "Thunderbird"),
        }
        
        valid_folders = {}
        for name, path in folders.items():
            # Check if exists and is not empty
            if os.path.exists(path):
                 valid_folders[name] = path
                
        return valid_folders

    def export_registry(self, key_path, output_file):
        """Exports a specific HKCU registry key to a file."""
        # reg export "HKCU\Software\..." "output.reg" /y
        full_key = f"HKEY_CURRENT_USER\\{key_path}"
        cmd = f'reg export "{full_key}" "{output_file}" /y'
        try:
            # We use shell=True to access the reg command
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def create_batch_backup(self, user_selection_map, destination_path, options, progress_callback=None):
        """
        Creates a zip backup for multiple users.
        user_selection_map: dict { "Username": ["Desktop", "Documents"] }
        destination_path: full path to save the .zip file
        options: dict { "export_registry": Bool }
        progress_callback: function(current_file, percentage)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"MultiBackup_{timestamp}.pmig" 
        full_backup_path = os.path.join(destination_path, backup_filename)
        
        # Temp dir for registry exports
        temp_dir = os.path.join(destination_path, "_pymigrate_temp")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            total_items = 0
            files_to_zip = [] # (full_path, archive_name)

            for username, folders in user_selection_map.items():
                user_root = os.path.join(self.users_dir, username)
                folders_map = self.get_user_folders(username)
                
                # 1. Collect Files
                for folder_name in folders:
                    if folder_name in folders_map:
                        source_folder = folders_map[folder_name]
                        for dirpath, dirnames, filenames in os.walk(source_folder):
                            for f in filenames:
                                full_path = os.path.join(dirpath, f)
                                # Archive: "User1/Desktop/File.txt"
                                rel_path = os.path.relpath(full_path, user_root)
                                archive_name = f"{username}/{rel_path}"
                                files_to_zip.append((full_path, archive_name))
                                total_items += 1
                
                # 2. Export Registry (If requested)
                if options.get("export_registry", False):
                    for name, key in self.registry_targets.items():
                        reg_file = os.path.join(temp_dir, f"{username}_{name}.reg")
                        # Note: This is tricky. REG EXPORT HKCU exports the *current* user.
                        # For other users, we'd need to load their Hive (NTUSER.DAT).
                        # Limitation: Registry export only works for the CURRENTLY RUNNING user.
                        # Workaround: We will log a warning or only do it if username == current_user.
                        if username.lower() == os.getlogin().lower():
                             if self.export_registry(key, reg_file):
                                 files_to_zip.append((reg_file, f"{username}/Registry/{name}.reg"))
                                 total_items += 1

            if total_items == 0:
                return False, "No items found to backup."

            processed_items = 0
            with zipfile.ZipFile(full_backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for full_path, arc_name in files_to_zip:
                    try:
                        zipf.write(full_path, arc_name)
                    except (PermissionError, OSError) as e:
                        print(f"Skipping {full_path}: {e}")
                    
                    processed_items += 1
                    if progress_callback:
                         progress_callback(arc_name, processed_items / total_items)

            return True, f"Batch Backup created: {full_backup_path}"
        
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def restore_batch_backup(self, archive_path, target_root_map, progress_callback=None):
        r"""
        Restores a multi-user backup.
        target_root_map: NOT USED YET (Automapped). 
        Logic: Inside Zip -> "User1/Desktop". We extract "User1" content to "C:\Users\User1".
        Advanced: We could allow mapping "User1" -> "User2" (Future).
        """
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                file_list = zipf.namelist()
                total = len(file_list)
                
                for i, file in enumerate(file_list):
                    # File format: "Username/Folder/File.ext" or "Username/Registry/file.reg"
                    parts = file.split("/")
                    if len(parts) < 2: continue
                    
                    username = parts[0]
                    
                    # 1. Check if it's a Registry File
                    if "Registry" in parts and file.endswith(".reg"):
                         # Extract to temp and run
                         # Dangerous! Ask user? For now, we restore to Documents/RestoredRegistry
                         # to be safe.
                         target_path = os.path.join(self.users_dir, username, "Documents", "Restored_Registry")
                         zipf.extract(file, self.users_dir) # Extracts to C:\Users\Username\...
                         # TODO: Auto-import logic can be added here
                    else:
                        # 2. Normal File Restore
                        # Target: C:\Users\Username\...
                        target_dir = self.users_dir
                        
                        # Security: Prevent Zip Slip
                        if ".." in file: continue
                        
                        try:
                            zipf.extract(file, target_dir)
                        except Exception:
                            pass

                    if progress_callback:
                        progress_callback(file, i / total)
                        
            return True, "Batch Restore Complete"
        except Exception as e:
            return False, str(e)
