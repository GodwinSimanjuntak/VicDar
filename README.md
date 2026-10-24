# VicDar Linux

**A live USB Linux for developers.** Plug it into any PC, boot, and you get a full coding
environment (compilers, runtimes, containers, an editor and a browser), with your work saved
back to the same USB stick.

Built on Debian 13 "trixie" · version 0.3 · early stage · GPL-3.0

## What it's for

- **Coding on any computer.** Campus labs, office PCs, a borrowed laptop: boot VicDar from USB
  and work in your own environment without installing anything on the machine.
- **Workshops and classrooms.** Give everyone the same USB image and every participant has the
  same tools and versions. No setup session needed.
- **A spare dev machine in your pocket.** Keep working when your main system breaks, or check
  a laptop's hardware before you buy it.
- **Learning how a Linux distro is made.** The whole distro comes from one readable shell
  script, stage by stage, with no live-build or other framework hiding the steps.

## Why VicDar

- **Ready to code on first boot.** gcc/g++, gdb, CMake, Python 3.13, Node.js 20, Go 1.24,
  Rust 1.85, Git and Podman are already installed.
- **Your work survives reboots, set up with one command.** Run `sudo vicdar-simpan` once inside
  the live system. It turns the free space on the USB stick into storage for your files,
  settings and installed packages.
- **Light desktop.** XFCE with Firefox ESR and VSCodium, login is automatic, and Wi-Fi is one
  click away in the panel.
- **Made for real laptops.** Wi-Fi, GPU and audio firmware plus CPU microcode are included, and
  the same image boots on BIOS and UEFI machines.
- **Rootless containers.** `podman run` works for the default user out of the box.
- **Stable base.** Plain Debian 13 packages with Debian security updates underneath.
- **Free to share.** Every component in the image may be redistributed. That is why the editor
  is VSCodium (the open source build of VS Code) and not Microsoft's VS Code, whose license
  forbids redistribution.

## What other live systems don't give you

| | VicDar | Typical live ISO (Ubuntu, Fedora) |
|---|---|---|
| Compiler and language toolchains preinstalled | Yes | No, you install them again every session |
| Persistence switched on from inside the running system | Yes, one command | No, decided when writing the USB, with extra tools |
| Entire build readable in a single ~230-line script | Yes | No, large build tooling |
| Boot test you can run at home (CD, USB, BIOS, UEFI, persistence) | Yes, `uji.py` | No |

## Quick start

```bash
git clone https://github.com/GodwinSimanjuntak/VicDar.git
cd VicDar
sudo bash build.sh    # -> out/vicdar-0.3-amd64.iso
sudo bash run.sh      # try it in QEMU
```

Default login: `dev` / `dev`. Building, writing to USB, persistence, customizing and testing
are all covered in **[docs.md](docs.md)**.

## Status

- Early stage. Every build is checked automatically in QEMU, but VicDar has not yet been tested
  on many physical laptops. Hardware reports are welcome in Issues.
- Secure Boot must be turned off for now (the boot loader is not signed yet).
- No prebuilt ISO yet. Building one takes a few minutes on a fast connection.
- Made in Indonesia: some system messages are still in Indonesian.

## License

The build scripts and configuration in this repository are licensed under GPL-3.0 (see
[LICENSE](LICENSE)). A built ISO contains Debian packages under their own licenses, including
closed firmware from Debian's `non-free-firmware` component.

VicDar is an independent project based on Debian. It is not affiliated with or endorsed by
the Debian Project.
