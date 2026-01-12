[![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white&style=for-the-badge)](#) [![Linux](https://custom-icon-badges.demolab.com/badge/Linux-FCC624?logo=linux&logoColor=black&style=for-the-badge)](#) [![macOS](https://img.shields.io/badge/macOS-DEDEDE?logo=apple&logoColor=666666&style=for-the-badge)](#)

[![Downloads](https://img.shields.io/github/downloads/mudrikam/Image-Tea-nano/total?style=for-the-badge&logo=github)](https://github.com/mudrikam/Image-Tea-nano/releases) [![Release](https://img.shields.io/github/v/release/mudrikam/Image-Tea-nano?style=for-the-badge&logo=github)](https://github.com/mudrikam/Image-Tea-nano/releases) ![WhatsApp Group](https://img.shields.io/badge/Join%20WhatsApp-Group-25D366?logo=whatsapp&style=for-the-badge&link=https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3)

---

> **If you do not speak Indonesian, [click here](README_ENGLISH.md) for the English version.**

# Image Tea Installer
Installer sederhana untuk Image Tea (Windows, macOS, Linux).

## Tautan Unduhan

| Sistem Operasi | Unduh |
|----------------|---------|
| ![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white&style=for-the-badge) | [Unduh Image_Tea_Installer.exe](https://github.com/mudrikam/Image-Tea-Installer/releases/download/latest/Image_Tea_Installer.exe) |
| ![macOS](https://img.shields.io/badge/macOS-DEDEDE?logo=apple&logoColor=666666&style=for-the-badge) | [Unduh Image_Tea_Installer](https://github.com/mudrikam/Image-Tea-Installer/releases/download/latest/Image_Tea_Installer) |
| ![Linux](https://custom-icon-badges.demolab.com/badge/Linux-FCC624?logo=linux&logoColor=black&style=for-the-badge) | [Unduh Image_Tea_Installer-x86_64.AppImage](https://github.com/mudrikam/Image-Tea-Installer/releases/download/latest/Image_Tea_Installer-x86_64.AppImage) |

## Cara Cepat
1. Unduh installer sesuai sistem operasi kamu dari tabel di atas.
2. Jalankan installer:
   - **Windows:** klik dua kali `Image_Tea_Installer.exe`.
   - **macOS:** unzip lalu klik dua kali `Image Tea Installer.app` (jika diblokir, klik kanan → Open).
   - **Linux:** buka terminal, lalu:

        ```bash
        chmod +x Image_Tea_Installer-x86_64.AppImage
        ./Image_Tea_Installer-x86_64.AppImage
        ```

## Apa yang dilakukan installer ini?
- Installer akan otomatis mengunduh paket aplikasi Image-Tea dari GitHub.
- File hasil unduhan akan diekstrak ke folder `Image-Tea` di lokasi yang sama dengan installer.
- Selama proses, kamu akan melihat tampilan kotak (frame) di terminal/command prompt, lengkap dengan progress bar dan konfirmasi cepat (cukup tekan tombol, tidak perlu Enter).
- Setelah selesai, kamu bisa pilih:
  - `L` — Jalankan Image Tea sekarang
  - `R` — Install ulang (unduh & pasang ulang)
  - `U` — Uninstall (hapus folder `Image-Tea`, ada 2x konfirmasi supaya aman)
  - `X` — Keluar

## Cara Membuka Aplikasi
- **Windows:** Buka file `Image Tea.exe` di dalam folder `Image-Tea`.
- **Linux & macOS:** Jalankan `Launcher.sh` di dalam folder `Image-Tea` (bisa lewat terminal: `./Launcher.sh`).
- Atau, jalankan kembali installer dan pilih opsi `L` (Jalankan Image Tea sekarang) di menu utama.

## Cara Uninstall
- Jalankan installer, lalu pilih `U`. Akan ada 2x konfirmasi sebelum folder `Image-Tea` dihapus.
- Atau, hapus manual folder `Image-Tea` di lokasi yang sama dengan installer.

## Troubleshooting
- Launcher tidak bisa dijalankan: di Linux/macOS, jalankan `chmod +x Launcher` atau `chmod +x Launcher.sh`.
- Jika menjalankan dari AppImage atau `.app`, file akan dibuat di folder yang sama dengan installer (bukan di `/tmp`).
- Jika gagal download atau ekstrak, coba jalankan ulang installer dari folder tempat file installer berada.
- **Khusus macOS:**
  - Jika aplikasi tidak bisa dibuka karena muncul pesan "tidak aman" atau "tidak dikenali", klik kanan pada `Image Tea Installer.app` lalu pilih **Open**. Biasanya akan muncul opsi untuk tetap membuka aplikasi.
  - Jika tetap tidak bisa dijalankan, kamu bisa menggunakan git untuk clone repo Image Tea secara manual:

    ```bash
    git clone https://github.com/mudrikam/Image-Tea-nano.git
    ```

    Aplikasi Image Tea sudah support macOS, hanya saja developer kesulitan membuat installer mac yang benar-benar mulus.

## Dukungan
- Rilis & unduhan: https://github.com/mudrikam/Image-Tea-nano/releases

![WhatsApp Group](https://img.shields.io/badge/Join%20WhatsApp-Group-25D366?logo=whatsapp&style=for-the-badge&link=https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3)

## Catatan Penting
Mohon untuk tidak mengirim pesan langsung (DM/japri) ke developer atau kontributor. Jika ada pertanyaan, saran, atau kendala, silakan tanyakan di grup WhatsApp komunitas agar bisa dibantu bersama-sama.