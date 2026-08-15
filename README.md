# PyMigrate Pro

![CI](https://github.com/DECRUX9812/PyMigrate-Pro/actions/workflows/ci.yml/badge.svg) ![License](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)

> A Windows utility for copying user profiles between machines.

PyMigrate Pro copies user data between Windows machines. The current implementation includes batch processing, Outlook profile registry handling, PST/OST and Thunderbird data detection, and a CustomTkinter interface.

---

## � Download

<a href="dist/PyMigratePro.exe">
  <img src="https://img.shields.io/badge/Download-Windows_Standalone_Exe-blue?style=for-the-badge&logo=windows" alt="Download EXE">
</a>

**[Direct Link to Executable (17 MB)](dist/PyMigratePro.exe)**

---

## �🚀 Key Features

* **Batch processing**: Select and migrate multiple user profiles.
* **Profile data**: Copy user files and selected application data.
* **Mail data**: Detect Outlook `.pst`/`.ost` files and Thunderbird data.
* **Registry handling**: Capture Outlook profile settings.
* **Portable build**: Package the application as a standalone Windows executable.

## 🛠️ Technology Stack

* **Language**: Python 3.10+
* **GUI framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Packaging**: PyInstaller
* **System Interaction**: `winreg` for Registry operations, `shutil` for high-performance file copy.

## 💡 Motivation

The project is also a practical example of:

* Building a Windows desktop utility in Python.
* Using the Windows Registry through `winreg`.
* Packaging and testing a desktop application with CI.

## 📥 Installation & Usage

**Install via Pip:**

```bash
pip install pymigrate-pro
```

**Run from Source:**

```bash
# Clone the repository
git clone https://github.com/DECRUX9812/PyMigrate-Pro.git
cd PyMigrate-Pro

# Install dependencies
pip install -r requirements.txt

# Launch the App
python -m pymigrate_pro
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
