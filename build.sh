#!/bin/bash
set -euo pipefail

NAME="VicDar"; ID="vicdar"; VERSION="0.2"; SUITE="trixie"
MIRROR="http://deb.debian.org/debian"
WORK="/var/tmp/vicdar"           # WAJIB di filesystem Linux, bukan /mnt/c
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/out"
ISO="$OUT/${ID}-${VERSION}-amd64.iso"

PAKET_SISTEM=(linux-image-amd64 live-boot systemd-sysv sudo network-manager wpasupplicant
  iproute2 iputils-ping bind9-dnsutils ca-certificates curl wget openssh-client
  bash-completion man-db less nano vim tmux htop jq ripgrep fd-find tree zip unzip
  xz-utils rsync fdisk e2fsprogs)
PAKET_FIRMWARE=(firmware-linux-free firmware-misc-nonfree firmware-amd-graphics
  firmware-intel-graphics firmware-iwlwifi firmware-realtek firmware-atheros
  firmware-brcm80211 firmware-mediatek firmware-sof-signed amd64-microcode intel-microcode)
PAKET_DEV=(git build-essential gdb cmake pkg-config python3 python3-pip python3-venv
  nodejs npm golang rustc cargo podman uidmap passt fuse-overlayfs sqlite3)

# Memastikan hak akses root dan memasang alat host yang belum tersedia.
tahap_0_cek() {
    echo "== Tahap 0: Cek hak akses dan perkakas host"
    if [ "$(id -u)" -ne 0 ]; then
        echo "Error: Skrip ini harus dijalankan sebagai root!" >&2
        exit 1
    fi

    local tools=(debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools)
    local to_install=()
    for pkg in "${tools[@]}"; do
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            to_install+=("$pkg")
        fi
    done

    if [ ${#to_install[@]} -gt 0 ]; then
        apt-get update
        apt-get install -y --no-install-recommends "${to_install[@]}"
    fi
}

# Membersihkan direktori kerja sebelumnya secara aman dan menyiapkan struktur direktori ISO.
tahap_1_bersihkan() {
    echo "== Tahap 1: Membersihkan direktori kerja"
    # grep tanpa -q: -q bisa memicu SIGPIPE + pipefail sehingga pengaman ini lolos
    if findmnt -rn -o TARGET | grep "^$WORK" >/dev/null; then
        echo "Error: Ditemukan mount point aktif di bawah $WORK! Batalkan." >&2
        exit 1
    fi
    rm -rf "$WORK"
    mkdir -p "$WORK/iso/live" "$WORK/iso/boot/grub" "$OUT"
}

# Mengunduh dan memasang sistem Debian minimal sebagai fondasi rootfs.
tahap_2_debootstrap() {
    echo "== Tahap 2: Menjalankan debootstrap"
    debootstrap --variant=minbase "$SUITE" "$WORK/rootfs" "$MIRROR"
}

di_chroot() {
    local cmd="$1"
    local R="$WORK/rootfs"
    export R DEBIAN_FRONTEND=noninteractive
    unshare --mount --propagation private bash -c '
        set -euo pipefail
        mount -t proc proc "$R/proc"
        mount -t sysfs sys "$R/sys"
        mount --bind /dev "$R/dev"
        mount -t devpts devpts "$R/dev/pts"
        chroot "$R" /bin/bash -c "$1"
    ' bash "$cmd"
}

# Menyiapkan repositori deb822 dan memasang paket sistem, firmware, perkakas developer, serta akun dev.
tahap_3_paket() {
    echo "== Tahap 3: Konfigurasi repositori dan pemasangan paket di chroot"

    rm -f "$WORK/rootfs/etc/apt/sources.list"
    mkdir -p "$WORK/rootfs/etc/apt/sources.list.d"
    cat <<EOF > "$WORK/rootfs/etc/apt/sources.list.d/debian.sources"
Types: deb
URIs: http://deb.debian.org/debian
Suites: $SUITE $SUITE-updates
Components: main non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: http://security.debian.org/debian-security
Suites: $SUITE-security
Components: main non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF

    di_chroot "
        apt-get update
        apt-get install -y --no-install-recommends ${PAKET_SISTEM[*]} ${PAKET_FIRMWARE[*]} ${PAKET_DEV[*]}
        useradd -m -s /bin/bash -G sudo dev
        echo dev:dev | chpasswd
        passwd -l root
        usermod --add-subuids 100000-165535 --add-subgids 100000-165535 dev
        systemctl enable NetworkManager
        apt-get clean
        rm -rf /var/lib/apt/lists/*
    "
}

# Mengatur konfigurasi identitas distro, berkas host, locale, dan menyalin berkas overlay ke rootfs.
tahap_4_identitas() {
    echo "== Tahap 4: Mengatur identitas sistem"

    rm -f "$WORK/rootfs/etc/os-release"
    cat <<EOF > "$WORK/rootfs/etc/os-release"
NAME="$NAME"
PRETTY_NAME="$NAME Linux $VERSION"
ID=$ID
ID_LIKE=debian
VERSION_ID="$VERSION"
VERSION_CODENAME=$SUITE
EOF

    echo "$ID" > "$WORK/rootfs/etc/hostname"

    cat <<EOF > "$WORK/rootfs/etc/hosts"
127.0.0.1 localhost
127.0.1.1 $ID
EOF

    echo "$NAME Linux $VERSION \n \l" > "$WORK/rootfs/etc/issue"
    echo "login: dev  sandi: dev" >> "$WORK/rootfs/etc/issue"
    echo "" >> "$WORK/rootfs/etc/issue"

    cat <<EOF > "$WORK/rootfs/etc/motd"
Selamat datang di $NAME Linux $VERSION.
  Toolchain : git gcc gdb cmake python3 node go rust podman
  Wi-Fi     : sudo nmtui
  Simpan file ke USB (sekali saja): sudo vicdar-simpan
EOF

    rm -f "$WORK/rootfs/etc/resolv.conf"

    echo "LANG=C.UTF-8" > "$WORK/rootfs/etc/default/locale"

    : > "$WORK/rootfs/etc/machine-id"

    cp -r "$ROOT/overlay/." "$WORK/rootfs/"
    chmod 755 "$WORK/rootfs/usr/local/sbin/vicdar-simpan"
}

# Menyalin berkas kernel dan initramfs serta memadatkan rootfs menjadi citra squashfs.
tahap_5_squashfs() {
    echo "== Tahap 5: Membuat berkas squashfs"

    shopt -s nullglob
    local vmlinuz=("$WORK"/rootfs/boot/vmlinuz-*)
    local initrd=("$WORK"/rootfs/boot/initrd.img-*)
    shopt -u nullglob

    if [ ${#vmlinuz[@]} -ne 1 ]; then
        echo "Error: Ditemukan ${#vmlinuz[@]} berkas vmlinuz (harus tepat satu)!" >&2
        exit 1
    fi
    if [ ${#initrd[@]} -ne 1 ]; then
        echo "Error: Ditemukan ${#initrd[@]} berkas initrd (harus tepat satu)!" >&2
        exit 1
    fi

    cp "${vmlinuz[0]}" "$WORK/iso/live/vmlinuz"
    cp "${initrd[0]}" "$WORK/iso/live/initrd.img"

    mksquashfs "$WORK/rootfs" "$WORK/iso/live/filesystem.squashfs" -comp xz -e boot -noappend
}

# Menulis konfigurasi bootloader GRUB untuk live boot dengan opsi persistence dan sesi bersih.
tahap_6_grub() {
    echo "== Tahap 6: Menyiapkan konfigurasi GRUB"
    cat <<EOF > "$WORK/iso/boot/grub/grub.cfg"
serial --unit=0 --speed=115200
terminal_input console serial
terminal_output console serial
set timeout=5
set default=0
menuentry "$NAME Linux $VERSION" {
  linux /live/vmlinuz boot=live persistence console=ttyS0,115200 console=tty0
  initrd /live/initrd.img
}
menuentry "$NAME Linux $VERSION (sesi bersih, tanpa simpan)" {
  linux /live/vmlinuz boot=live console=ttyS0,115200 console=tty0
  initrd /live/initrd.img
}
EOF
}

# Membangun berkas ISO bootable hybrid BIOS dan UEFI menggunakan grub-mkrescue.
tahap_7_iso() {
    echo "== Tahap 7: Membuat citra ISO"
    grub-mkrescue -o "$ISO" "$WORK/iso" -- -volid "${ID^^}_${VERSION//./_}"
    ls -lh "$ISO"
}

tahap_0_cek
tahap_1_bersihkan
tahap_2_debootstrap
tahap_3_paket
tahap_4_identitas
tahap_5_squashfs
tahap_6_grub
tahap_7_iso

echo ""
echo "Pembuatan ISO selesai! Tersimpan di: $ISO"
echo "Untuk menjalankan, ketik: bash run.sh"
