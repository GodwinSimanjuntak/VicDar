# Product

<!-- impeccable:product-schema 1 -->

## Platform

linux-desktop

(Native XFCE 4.20 / GTK3 desktop of a live-USB Linux distribution. Not web, iOS or Android: Impeccable's HTML tooling does not apply directly.)

## Users

Three groups, confirmed as equally important:

- IT students coding in campus labs, internet cafés, or on modest laptops.
- Professional developers who need a spare machine in their pocket: main system broken, client office, borrowed laptop.
- Workshop and class participants who all receive the same USB stick from an instructor.

The audience is international. Indonesian origin is mentioned in the README only.

## Product Purpose

VicDar Linux is a live USB Linux for developers, built on Debian 13. Boot any PC from the stick and get a full coding environment (compilers, runtimes, containers, editor, browser), with work saved back to the same stick. Success: a developer boots an unfamiliar machine, is productive within minutes, and finds their work there next time.

## Positioning

- Toolchains preinstalled: gcc/gdb/CMake, Python 3.13, Node.js 20, Go 1.24, Rust 1.85, Podman (rootless).
- Persistence switched on from inside the running system with one command: `sudo vicdar-simpan`.
- The whole distro is built by one readable shell script of about 230 lines, without live-build.
- A boot test anyone can run at home: `uji.py` (CD, USB, BIOS, UEFI, persistence).

## Operating Context

- Booted from a USB stick on machines the user does not own: lab PCs, office PCs, older laptops (4 GB RAM, old Intel graphics). Also run in QEMU and other VMs.
- Sessions are often short and on unfamiliar hardware; screens range from 1366x768 laptops to 1080p monitors.
- The desktop logs in automatically as user `dev`. Main daily apps: terminal, VSCodium, Firefox ESR, Thunar file manager.

## Capabilities and Constraints

- Desktop stack: XFCE 4.20 (GTK3), xfwm4, xfce4-panel, LightDM with lightdm-gtk-greeter, xfce4-terminal, Thunar, NetworkManager applet, PipeWire, xfce4-power-manager, Whisker menu available.
- Must run smoothly on old laptops (confirmed): no reliance on blur, heavy transparency, compositing effects or heavy animation.
- Every component must be redistributable (GPL-3.0 repository, public ISO releases planned): no proprietary fonts, icons or artwork. Debian's own branding (`desktop-base`) is not used.
- Built only from Debian 13 packages plus files shipped in the repository's `overlay/` directory.
- amd64 only; Secure Boot unsupported for now.
- Undecided: whether system text that is currently Indonesian (welcome message, `vicdar-simpan`, boot menu) gets translated to English.

## Brand Commitments

- Name: VicDar (full: VicDar Linux), technical ID `vicdar`.
- Neutral, international identity (confirmed).
- Must not copy the Windows or macOS look one-to-one; inspiration is allowed (user's explicit requirement).
- Must not imitate Debian branding: VicDar is an independent project, not affiliated with Debian.
- No logo exists yet.

## Evidence on Hand

- `README.md`, `docs.md`, `build.sh`, `uji.py` in the repository.
- Screenshot of the current stock XFCE desktop: `out/vicdar-0.3-desktop.png` (black background, top panel, bottom launcher dock).
- No logo, no user base, no testimonials, no published ISO downloads yet. Do not fabricate any of these.

## Product Principles

1. Ready to work within minutes on someone else's machine.
2. Light enough for old hardware: clarity before effects.
3. Everything shareable and inspectable: open source, readable build.
4. Your work follows you between machines and sessions.
