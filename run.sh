#!/bin/bash
set -euo pipefail

OUT="$(cd "$(dirname "$0")" && pwd)/out"
ISO="$(ls -t "$OUT"/*.iso 2>/dev/null | head -n 1 || true)"

if [ -z "$ISO" ] || [ ! -f "$ISO" ]; then
    echo "Error: Berkas ISO tidak ditemukan di $OUT." >&2
    echo "Silakan jalankan build.sh terlebih dahulu:" >&2
    echo "  bash build.sh" >&2
    exit 1
fi

if [ "$#" -eq 0 ]; then
    echo "Keluar QEMU: Ctrl-A lalu X"
    qemu-system-x86_64 -enable-kvm -m 2048 -smp 2 -cdrom "$ISO" -nographic -nic user,model=virtio-net-pci
elif [ "$#" -eq 1 ] && [ "$1" = "usb" ]; then
    IMG="/var/tmp/vicdar-usb.img"   # di filesystem Linux supaya sparse, bukan /mnt/c
    [ -f "$IMG" ] || { cp "$ISO" "$IMG"; truncate -s 4G "$IMG"; }
    echo "USB virtual: $IMG (hapus file ini untuk mulai ulang dari ISO terbaru)"
    echo "Keluar QEMU: Ctrl-A lalu X"
    qemu-system-x86_64 -enable-kvm -m 2048 -smp 2 -nographic -nic user,model=virtio-net-pci \
        -drive file="$IMG",format=raw,if=none,id=usb -device qemu-xhci -device usb-storage,drive=usb
else
    echo "Cara pakai: $0 [usb]" >&2
    echo "  (tanpa argumen) : Boot ISO sebagai CD live" >&2
    echo "  usb             : Boot USB virtual (mencoba persistence)" >&2
    exit 1
fi
