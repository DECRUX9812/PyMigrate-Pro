import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox, BooleanVar

from .backend import ProfileBackend

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PyMigrateApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyMigrate Pro - Enterprise Migration Tool")
        self.geometry("900x700")
        self.resizable(False, False)

        self.backend = ProfileBackend()
        self.selected_mode = None

        # State
        self.selected_users = {}  # { "Username": [Folders] }
        self.backup_options = {
            "export_registry": False,
            "backup_mail": True,
        }

        # UI Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="PyMigrate PRO", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.frames = {}
        for F in (
            WelcomePage,
            ModeSelectionPage,
            BatchUserPage,
            BackupProgressPage,
            RestorePage,
        ):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=1, sticky="nsew")

        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        frame.on_show()

    def set_mode(self, mode):
        self.selected_mode = mode
        if mode == "backup":
            self.show_frame("BatchUserPage")
        else:
            self.show_frame("RestorePage")


class WelcomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(
            self, text="PyMigrate Pro", font=ctk.CTkFont(size=28, weight="bold")
        )
        label.pack(pady=40)

        desc = ctk.CTkLabel(
            self,
            text=(
                "Enterprise User Profile Migration Tool\n\n"
                "Suppports: Batch Transfer, Outlook Profiles, Registry Settings"
            ),
            font=ctk.CTkFont(size=16),
        )
        desc.pack(pady=20)

        btn = ctk.CTkButton(
            self,
            text="Start Migration",
            width=200,
            height=40,
            font=ctk.CTkFont(size=15),
            command=lambda: controller.show_frame("ModeSelectionPage"),
        )
        btn.pack(pady=40)

    def on_show(self):
        pass


class ModeSelectionPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Select Mode", font=ctk.CTkFont(size=24))
        label.pack(pady=40)

        backup_btn = ctk.CTkButton(
            self,
            text="📤 Batch Backup",
            width=220,
            height=60,
            font=ctk.CTkFont(size=18),
            command=lambda: controller.set_mode("backup"),
        )
        backup_btn.pack(pady=20)

        restore_btn = ctk.CTkButton(
            self,
            text="📥 Batch Restore",
            width=220,
            height=60,
            font=ctk.CTkFont(size=18),
            command=lambda: controller.set_mode("restore"),
        )
        restore_btn.pack(pady=20)

    def on_show(self):
        pass


class BatchUserPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        label = ctk.CTkLabel(
            self, text="Select Users & Data", font=ctk.CTkFont(size=24)
        )
        label.pack(pady=10)

        # Main Content: Split 50/50 Users and Options
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Left: User List
        left_panel = ctk.CTkFrame(content)
        left_panel.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            left_panel, text="Profiles Found:", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        self.user_scroll = ctk.CTkScrollableFrame(left_panel)
        self.user_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.user_checks = {}  # "User": CheckBox

        # Right: Options
        right_panel = ctk.CTkFrame(content)
        right_panel.pack(side="right", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            right_panel, text="Advanced Options:", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        self.reg_var = BooleanVar(value=True)
        ctk.CTkCheckBox(
            right_panel,
            text="Export Registry (Outlook / Wallpaper)",
            variable=self.reg_var,
        ).pack(anchor="w", pady=10, padx=10)

        self.mail_var = BooleanVar(value=True)
        ctk.CTkCheckBox(
            right_panel, text="Include Mail Profiles (OST/PST)", variable=self.mail_var
        ).pack(anchor="w", pady=10, padx=10)

        ctk.CTkLabel(
            right_panel,
            text=(
                "Note: Registry export only works\nfor the currently logged in user.\n"
                "Others will be skipped."
            ),
            text_color="gray",
            font=("Arial", 12),
        ).pack(anchor="w", padx=10)

        # Footer
        next_btn = ctk.CTkButton(
            self,
            text="Next: Backup Selected",
            command=self.prepare_backup,
            width=200,
            height=40,
        )
        next_btn.pack(pady=20)

    def on_show(self):
        # Refresh User List
        for c in self.user_checks.values():
            c.destroy()
        self.user_checks = {}

        users = self.controller.backend.get_users()
        for user in users:
            var = BooleanVar(value=False)
            # Pre-select current user
            try:
                if user.lower() == os.getlogin().lower():
                    var.set(True)
            except OSError:
                # os.getlogin() may fail in some environments; ignore
                pass

            cb = ctk.CTkCheckBox(self.user_scroll, text=user, variable=var)
            cb.pack(anchor="w", pady=5, padx=5)
            self.user_checks[user] = var

    def prepare_backup(self):
        # Build Selection Map
        selection_map = {}
        target_users = [u for u, v in self.user_checks.items() if v.get()]

        if not target_users:
            messagebox.showwarning("No Selection", "Please select at least one user.")
            return

        for user in target_users:
            # Default to ALL valid folders + Mail
            folders_to_backup = [
                "Desktop",
                "Documents",
                "Downloads",
                "Pictures",
                "Music",
                "Videos",
                "Favorites",
            ]
            if self.mail_var.get():
                folders_to_backup.extend(["Outlook Files", "Thunderbird"])

            selection_map[user] = folders_to_backup

        self.controller.selected_users = selection_map  # Map of User -> Folders
        self.controller.backup_options["export_registry"] = self.reg_var.get()
        self.controller.show_frame("BackupProgressPage")


class BackupProgressPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.status = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=18))
        self.status.pack(pady=30)

        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.log = ctk.CTkTextbox(self, width=600, height=300)
        self.log.pack(pady=10)

        self.btn = ctk.CTkButton(self, text="Start Batch Backup", command=self.start)
        self.btn.pack(pady=20)

    def on_show(self):
        count = len(self.controller.selected_users)
        self.status.configure(text=f"Ready to backup {count} user profile(s)")
        self.log.delete("1.0", "end")
        self.btn.configure(state="normal", text="Start Batch Backup")

    def start(self):
        dest = filedialog.askdirectory(title="Save Backup To...")
        if not dest:
            return

        self.btn.configure(state="disabled")
        self.log.insert("end", f"Starting Batch Backup to: {dest}\n\n")

        def run():
            def cb(fname, pct):
                self.progress.set(pct)
                if pct > 0 and (int(pct * 100) % 5 == 0):
                    # Log throttle
                    self.log.see("end")

            success, msg = self.controller.backend.create_batch_backup(
                self.controller.selected_users,
                dest,
                self.controller.backup_options,
                cb,
            )

            self.log.insert("end", f"\n{msg}\n")
            self.progress.set(1)
            self.btn.configure(
                state="normal",
                text="Done (Main Menu)",
                command=lambda: self.controller.show_frame("WelcomePage"),
            )

        threading.Thread(target=run, daemon=True).start()


class RestorePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Batch Restore", font=ctk.CTkFont(size=24)).pack(
            pady=20
        )

        self.file_lbl = ctk.CTkLabel(self, text="No File Selected")
        self.file_lbl.pack(pady=10)

        ctk.CTkButton(self, text="Select .pmig File", command=self.pick_file).pack(
            pady=10
        )

        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.pack(pady=30)
        self.progress.set(0)

        self.run_btn = ctk.CTkButton(
            self, text="Start Restore", state="disabled", command=self.run
        )
        self.run_btn.pack(pady=20)
        self.selected = None

    def on_show(self):
        pass

    def pick_file(self):
        f = filedialog.askopenfilename(filetypes=[("Backup", "*.pmig")])
        if f:
            self.selected = f
            self.file_lbl.configure(text=os.path.basename(f))
            self.run_btn.configure(state="normal")

    def run(self):
        if not self.selected:
            return
        self.run_btn.configure(state="disabled")

        def work():
            s, m = self.controller.backend.restore_batch_backup(
                self.selected, {}, lambda n, p: self.progress.set(p)
            )
            self.run_btn.configure(text="Restored!", state="normal")

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    app = PyMigrateApp()
    app.mainloop()
