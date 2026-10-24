# VicDar Linux 0.2

Distro live USB untuk developer berbasis Debian 13 (trixie), dirakit tangan tanpa `live-build` supaya tiap tahap bisa dipelajari. Menghasilkan citra ISO live hybrid (BIOS + UEFI) yang siap dipakai di laptop fisik maupun mesin virtual dengan dukungan toolchain lengkap dan persistence.

## Isi Distro

- **Toolchain**: git, build-essential, gdb, cmake, pkg-config, python3 (pip, venv), nodejs, npm, golang, rustc/cargo, podman (rootless), sqlite3.
- **Firmware**: Wi-Fi (Intel, Realtek, Atheros, Broadcom, MediaTek), audio (SOF), grafis (AMD, Intel), dan CPU microcode.
- **Jaringan**: Wi-Fi dan Ethernet dikelola via NetworkManager (`sudo nmtui`).
- **Kredensial**: Akun `dev` dengan sandi `dev` (akses sudo, tty1 login otomatis).

## Build dan Menjalankan

Butuh Debian 13 (bisa di WSL2 pada Windows), akses root, sekitar 10 GB ruang kosong, dan internet.

```bash
git clone https://github.com/GodwinSimanjuntak/VicDar.git
cd VicDar
sudo bash build.sh      # hasil: out/vicdar-0.2-amd64.iso
sudo bash run.sh        # coba sebagai CD live di QEMU
sudo bash run.sh usb    # coba USB virtual + persistence
```

`run.sh` butuh paket `qemu-system-x86` dan `/dev/kvm`. Keluar dari QEMU: tekan `Ctrl-A` lalu `X`.

## Tulis ke USB Flashdisk

- **Windows**: Gunakan Rufus (pilih mode **DD**) atau balenaEtcher.
- **Linux**: `sudo dd if=out/vicdar-0.2-amd64.iso of=/dev/sdX bs=4M status=progress && sync` (sesuaikan `/dev/sdX`).
- **Persistence**: Boot dari flashdisk, jalankan `sudo vicdar-simpan` sekali untuk membuat partisi penyimpanan permanen di sisa ruang USB, lalu reboot.

## Kustomisasi

- **Paket**: Ubah array `PAKET_SISTEM`, `PAKET_FIRMWARE`, atau `PAKET_DEV` di `build.sh`.
- **Berkas Statis**: Tempatkan berkas pada direktori `overlay/` (disalin otomatis ke rootfs).

## Tabel Tahap Build (0–7)

| Tahap | Apa yang Terjadi | Kenapa |
|---|---|---|
| 0. cek | Periksa hak root & pasang perkakas host yang belum ada | Memastikan lingkungan build host siap dan memiliki dependensi |
| 1. bersihkan | Cek mount aktif lalu bersihkan direktori kerja | Mencegah konflik mount point dan memulai build secara bersih |
| 2. debootstrap | Unduh dan pasang Debian trixie minimal | Membentuk struktur dasar rootfs sistem operasi |
| 3. paket | Repositori deb822, pasang paket sistem/firmware/dev, buat user dev | Menyediakan driver hardware, toolchain lengkap, dan user dev |
| 4. identitas | Tulis identitas, issue, motd, locale C.UTF-8, salin overlay | Menetapkan konfigurasi distro, autologin, dan skrip simpan |
| 5. squashfs | Salin kernel/initrd lalu mksquashfs rootfs | Memadatkan seluruh sistem berkas live untuk berjalan di RAM |
| 6. grub | Konfigurasi grub.cfg dengan opsi persistence & sesi bersih | Mengatur opsi bootloader laptop fisik dan serial console QEMU |
| 7. iso | Bangun ISO hybrid dengan grub-mkrescue | Menghasilkan citra ISO bootable untuk BIOS dan UEFI |

## Uji otomatis

- Menguji di QEMU boot CD dan USB virtual (vicdar-simpan, persistence BIOS dan UEFI).
- Butuh Debian dengan paket `qemu-system-x86 python3-pexpect ovmf`.
- Perintah: `sudo python3 uji.py out/vicdar-0.2-amd64.iso`

## Lisensi

Skrip dan konfigurasi di repo ini berlisensi GPL-3.0 (lihat `LICENSE`).
ISO hasil build berisi paket Debian dengan lisensinya masing-masing, termasuk firmware tertutup dari komponen `non-free-firmware`.

VicDar adalah proyek independen berbasis Debian, bukan proyek resmi Debian.
