# PyMigrate Pro

![CI](https://github.com/DECRUX9812/PyMigrate-Pro/actions/workflows/ci.yml/badge.svg) ![License](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)

> **A lightweight, enterprise-grade migration tool for Windows User Profiles.**

PyMigrate Pro streamlines the process of moving user data between machines. It is designed as a safer, open-source alternative to proprietary tools, featuring batch processing, smart registry handling for Outlook profiles, and an intuitive modern GUI.

---

## � Download

<a href="dist/PyMigratePro.exe">
  <img src="https://img.shields.io/badge/Download-Windows_Standalone_Exe-blue?style=for-the-badge&logo=windows" alt="Download EXE">
</a>

**[Direct Link to Executable (17 MB)](dist/PyMigratePro.exe)**

---

## �🚀 Key Features

* **📂 Batch Processing**: Select and migrate multiple user profiles simultaneously.
* **📧 Smart Registry & Mail**: Automatically captures Outlook profiles and detects `.pst/.ost` files and Thunderbird data.
* **🎨 Variable Theming**: Modern, responsive UI with dark mode support.
* **🛡️ Reliability**: Robust error handling and logging for enterprise environments.
* **📦 Portable**: Can be bundled into a single standalone `.exe` for easy deployment.

## 🛠️ Technology Stack

* **Language**: Python 3.10+
* **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern wrappers for Tkinter)
* **Packaging**: PyInstaller
* **System Interaction**: `winreg` for Registry operations, `shutil` for high-performance file copy.

## 💡 Motivation

I built PyMigrate Pro to address the lack of reliable, scriptable, and modern open-source tools for local user profile migration. While proprietary tools exist, they often lack flexibility. This project demonstrates:

* Building robust desktop applications with Python.
* Interacting with low-level Windows APIs (Registry).
* Structuring a project for maintainability and CI/CD automation.

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
