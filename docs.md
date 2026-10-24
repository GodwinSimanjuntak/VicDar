# VicDar documentation

1. [Requirements](#requirements)
2. [Build the ISO](#build-the-iso)
3. [Try it in QEMU](#try-it-in-qemu)
4. [Write it to a USB stick](#write-it-to-a-usb-stick)
5. [Persistence: keep your work](#persistence-keep-your-work)
6. [Default account](#default-account)
7. [What's inside](#whats-inside)
8. [Customizing](#customizing)
9. [How the build works](#how-the-build-works)
10. [Automated tests](#automated-tests)
11. [Project layout](#project-layout)
12. [Known limitations](#known-limitations)

## Requirements

- Debian 13 as the build host: a real machine, a VM, or WSL2 on Windows.
- Root access, about 10 GB of free disk space, and an internet connection.
- `build.sh` installs its own host tools (`debootstrap`, `squashfs-tools`, `xorriso`, GRUB, `mtools`).
- For `run.sh` and `uji.py`: `qemu-system-x86` and `/dev/kvm` (hardware virtualization).
  `uji.py` also needs `python3-pexpect` and `ovmf`.

## Build the ISO

```bash
git clone https://github.com/GodwinSimanjuntak/VicDar.git
cd VicDar
sudo bash build.sh
```

The result is `out/vicdar-0.3-amd64.iso`. The working directory is `/var/tmp/vicdar`. It must
be on a Linux filesystem, so on WSL2 keep it there and not under `/mnt/c`.

## Try it in QEMU

```bash
sudo bash run.sh        # boot the ISO as a live CD
sudo bash run.sh usb    # boot a virtual 4 GB USB stick, to try persistence
```

- If a display is available (a desktop session, or WSLg on Windows), QEMU opens a window.
  Over SSH it falls back to a serial console in the terminal.
- To quit: close the window, or press `Ctrl-A` then `X` in terminal mode.
- The virtual USB stick is `/var/tmp/vicdar-usb.img`. Delete it to start again from the latest ISO.

## Write it to a USB stick

The ISO is a hybrid image: write it to the whole stick, not to a partition.

- **Windows:** Rufus in **DD image** mode, or balenaEtcher.
- **Linux:** `sudo dd if=out/vicdar-0.3-amd64.iso of=/dev/sdX bs=4M status=progress && sync`
  (replace `/dev/sdX` with the stick; everything on it is erased).

Then boot from the stick. On most laptops that means a boot menu key (F12, F9, Esc) and
**Secure Boot turned off** in the firmware settings.

## Persistence: keep your work

By default a live system forgets everything when it shuts down. To keep files, settings and
installed packages:

1. Boot VicDar from the USB stick.
2. Run `sudo vicdar-simpan` and type `YA` to confirm.
3. Reboot and choose the first menu entry.

From the next boot on, every change is saved to the stick. Anything created before that
reboot is not kept.

What `vicdar-simpan` does:

- Finds the stick VicDar booted from, and refuses to run from a CD/DVD.
- Moves the backup GPT header to the real end of the stick (the ISO puts it at the end of the
  image), then adds an ext4 partition labelled `persistence` in the free space.
- Writes `/ union` into its `persistence.conf`, so live-boot overlays the whole system on it.
- The original VicDar partitions are not modified. Running it again only reports that
  persistence already exists.

The boot menu has two entries:

| Entry | Effect |
|---|---|
| `VicDar Linux 0.3` (default) | Uses the persistence partition if there is one |
| `VicDar Linux 0.3 (sesi bersih, tanpa simpan)` | Clean session: nothing is read from or saved to the stick |

## Default account

- User `dev`, password `dev`, member of `sudo`. The root account is locked.
- The desktop logs in automatically (LightDM). The text console on tty1 also logs in
  automatically, which is a useful fallback if graphics fail.
- Change the password with `passwd` once persistence is on.

## What's inside

Everything comes from Debian 13 except VSCodium, which comes from the official VSCodium
repository.

| Group | Packages |
|---|---|
| Desktop | XFCE, LightDM, Firefox ESR, VSCodium (`codium`), PipeWire audio, NetworkManager applet, power manager |
| Development | gcc/g++ (`build-essential`), gdb, CMake, pkg-config, Python 3.13 (pip, venv), Node.js 20 + npm, Go 1.24, Rust 1.85 + Cargo, Podman (rootless), SQLite |
| Command line | git, curl, wget, vim, nano, tmux, htop, jq, ripgrep, fd, tree, rsync, OpenSSH client |
| Hardware | Wi-Fi firmware (Intel, Realtek, Atheros, Broadcom, MediaTek), AMD/Intel GPU firmware, SOF audio, CPU microcode |

The toolchains are Debian's versions, which are stable but not the newest. For the latest
releases, install `rustup`, `nvm` and similar tools on top (keep them with persistence).

## Customizing

All configuration is in `build.sh` and `overlay/`:

- **Name and version:** `NAME`, `ID` and `VERSION` at the top of `build.sh`.
- **Packages:** the `PAKET_SISTEM`, `PAKET_FIRMWARE`, `PAKET_DEV` and `PAKET_DESKTOP` arrays.
  Add or remove Debian package names, then rebuild.
- **Files:** anything under `overlay/` is copied as-is into the root filesystem. For example
  `overlay/etc/lightdm/lightdm.conf.d/50-vicdar-autologin.conf` sets up desktop autologin.

## How the build works

`build.sh` runs eight stages in order. Each one is a shell function named `tahap_N_...`
("stage N").

| Stage | What happens | Why |
|---|---|---|
| 0 `cek` | Check for root, install missing host tools | The build needs debootstrap, squashfs and GRUB on the host |
| 1 `bersihkan` | Refuse to continue if anything is mounted under the work dir, then wipe it | Never `rm -rf` through a mounted `/dev`; every build starts clean |
| 2 `debootstrap` | Download a minimal Debian 13 into `rootfs/` | The base system everything else is installed into |
| 3 `paket` | Set up apt sources, install all packages and VSCodium, create the `dev` user, enable services | Turns the bare base into a developer desktop |
| 4 `identitas` | Write os-release, hostname, issue, motd and locale, copy `overlay/` | Gives the system its own name and settings |
| 5 `squashfs` | Copy the kernel and initrd, compress `rootfs/` into `filesystem.squashfs` | A live system boots from one compressed read-only image |
| 6 `grub` | Write `grub.cfg` with the normal and clean-session entries | Boot menu for laptops plus a serial console for QEMU |
| 7 `iso` | Build a hybrid BIOS + UEFI image with `grub-mkrescue` | One file that boots as a CD or from a USB stick |

Commands inside the root filesystem run through `di_chroot`, which uses
`unshare --mount` so the `/proc`, `/sys` and `/dev` mounts disappear on their own when the
command ends, even if it fails.

## Automated tests

```bash
sudo apt install qemu-system-x86 python3-pexpect ovmf
sudo python3 uji.py out/vicdar-0.3-amd64.iso          # everything
sudo python3 uji.py out/vicdar-0.3-amd64.iso cd       # live CD checks only
sudo python3 uji.py out/vicdar-0.3-amd64.iso usb      # USB + persistence checks only
```

`uji.py` drives QEMU over the serial console and checks:

- **Live CD:** os-release, every toolchain, sudo, networking and DNS, no failed services, the
  XFCE desktop (LightDM, Xorg, panel, network applet, PipeWire) with an auto-login graphical
  session, VSCodium and Firefox, a rootless `podman run`, firmware, and that `vicdar-simpan`
  refuses to run from a CD. It also saves a screenshot of the desktop to
  `/var/tmp/vicdar-desktop.png`.
- **Virtual USB:** `vicdar-simpan` creates the partition, files in `/home` and `/etc` survive
  a reboot, the partition is detected on a second run, and the stick still boots in UEFI mode
  with the saved files.

It prints `OK` or `GAGAL` (failed) per check and ends with `HASIL: SEMUA LULUS` when
everything passes.

## Project layout

| Path | Purpose |
|---|---|
| `build.sh` | Builds the ISO (stages 0 to 7) |
| `run.sh` | Boots the ISO or a virtual USB stick in QEMU |
| `uji.py` | Automated boot and persistence tests |
| `overlay/` | Files copied verbatim into the root filesystem |
| `overlay/usr/local/sbin/vicdar-simpan` | The persistence setup command |
| `docs.md` | This document |

## Known limitations

- Tested in QEMU (BIOS and UEFI). Real laptops are still largely untested.
- Secure Boot is not supported yet: the GRUB EFI image is not signed.
- 64-bit x86 (amd64) only.
- Some text inside the system (welcome message, `vicdar-simpan`, boot menu) is in Indonesian.
- No graphical installer. VicDar is meant to run live from USB.
