[![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white&style=for-the-badge)](#) [![Linux](https://custom-icon-badges.demolab.com/badge/Linux-FCC624?logo=linux&logoColor=black&style=for-the-badge)](#) [![macOS](https://img.shields.io/badge/macOS-DEDEDE?logo=apple&logoColor=666666&style=for-the-badge)](#)

[![Downloads](https://img.shields.io/github/downloads/mudrikam/Image-Tea-nano/total?style=for-the-badge&logo=github)](https://github.com/mudrikam/Image-Tea-nano/releases) [![Release](https://img.shields.io/github/v/release/mudrikam/Image-Tea-nano?style=for-the-badge&logo=github)](https://github.com/mudrikam/Image-Tea-nano/releases) ![WhatsApp Group](https://img.shields.io/badge/Join%20WhatsApp-Group-25D366?logo=whatsapp&style=for-the-badge&link=https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3)

---

# Image Tea Installer
A simple installer for Image Tea (Windows, macOS, Linux).

## Download Links

| Operating System | Download |
|------------------|---------|
| ![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white&style=for-the-badge) | [Download Image_Tea_Installer.exe](https://github.com/mudrikam/Image-Tea-Installer/releases/download/latest/Image_Tea_Installer.exe) |
| ![macOS](https://img.shields.io/badge/macOS-DEDEDE?logo=apple&logoColor=666666&style=for-the-badge) | [Download Image_Tea_Installer](https://github.com/mudrikam/Image-Tea-Installer/releases/download/latest/Image_Tea_Installer) |
| ![Linux](https://custom-icon-badges.demolab.com/badge/Linux-FCC624?logo=linux&logoColor=black&style=for-the-badge) | [Download Image_Tea_Installer-x86_64.AppImage](https://github.com/mudrikam/Image-Tea-Installer/releases/download/latest/Image_Tea_Installer-x86_64.AppImage) |

## Quick Start
1. Download the installer for your operating system from the table above.
2. Run the installer:
   - **Windows:** Double-click `Image_Tea_Installer.exe`.
  - **macOS:** Open Terminal, then run:

      ```bash
      chmod +x Image_Tea_Installer
      ./Image_Tea_Installer
      ```
    If blocked by security, open System Preferences → Security & Privacy → Open Anyway.
   - **Linux:** Open terminal, then:

        ```bash
        chmod +x Image_Tea_Installer-x86_64.AppImage
        ./Image_Tea_Installer-x86_64.AppImage
        ```

## How to Open the App
- **Windows:** Open `Image Tea.exe` inside the `Image-Tea` folder.
- **Linux & macOS:** Run `Launcher.sh` inside the `Image-Tea` folder (via terminal: `./Launcher.sh`).
- Or, re-run the installer and choose `L` (Launch Image Tea now) from the main menu.

## What does this installer do?
- Automatically downloads the Image-Tea app package from GitHub.
- Extracts the downloaded files to an `Image-Tea` folder in the same location as the installer.
- Shows a GUI-style frame in the terminal/command prompt, with progress bar and instant keypress confirmation (no need to press Enter).
- After completion, you can choose:
  - `L` — Launch Image Tea now
  - `R` — Reinstall (download & reinstall)
  - `U` — Uninstall (delete `Image-Tea` folder, with 2x confirmation for safety)
  - `X` — Exit

## Uninstall
- Run the installer and choose `U`. There will be 2x confirmation before deleting the `Image-Tea` folder.
- Or, manually delete the `Image-Tea` folder in the same location as the installer.

## Troubleshooting
- Launcher not executable: on Linux/macOS, run `chmod +x Launcher` or `chmod +x Launcher.sh`.
- If running from AppImage or `.app`, files will be created in the same folder as the installer (not in `/tmp`).
- If download or extraction fails, try running the installer again from the folder where the installer is located.
- **macOS only:**
  - If the installer can't be opened due to "untrusted" or "not recognized" warning, open System Preferences → Security & Privacy, then click **Open Anyway** for `Image_Tea_Installer`.
  - If it still can't be opened, you can use git to clone the Image Tea repo manually:

    ```bash
    git clone https://github.com/mudrikam/Image-Tea-nano.git
    ```

    Image Tea supports macOS, but the developer has trouble making a perfectly smooth mac installer.

## Support
- Releases & downloads: https://github.com/mudrikam/Image-Tea-nano/releases

![WhatsApp Group](https://img.shields.io/badge/Join%20WhatsApp-Group-25D366?logo=whatsapp&style=for-the-badge&link=https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3)

## Note
Please do not send direct/private messages (DM) to the developer or contributors. For any questions, suggestions, or issues, please ask in the WhatsApp community group so everyone can help together.
