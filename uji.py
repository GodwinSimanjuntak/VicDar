# Uji otomatis VicDar di QEMU: boot CD (toolchain + desktop), lalu USB virtual (vicdar-simpan, persistence BIOS + UEFI).
# Jalankan sebagai root di Debian: apt install qemu-system-x86 python3-pexpect ovmf
# sudo python3 uji.py out/vicdar-0.3-amd64.iso [cd|usb]   -> screenshot desktop: /var/tmp/vicdar-desktop.png
import sys, os, re, socket, shutil, subprocess, time, pexpect
iso = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else "all"
MON = "/var/tmp/vicdar-mon.sock"
BASE = ["qemu-system-x86_64", "-enable-kvm", "-m", "3072", "-smp", "2", "-nographic",
        "-nic", "user,model=virtio-net-pci", "-monitor", f"unix:{MON},server,nowait"]
USB = ["-drive", "file=/var/tmp/t-usb.img,format=raw,if=none,id=usb", "-device", "qemu-xhci",
       "-device", "usb-storage,drive=usb"]
UEFI = ["-bios", "/usr/share/ovmf/OVMF.fd"]
PROMPT = r"dev@vicdar:\S*\$ "
log = open("/var/tmp/test2.log", "a")
fails = []

def boot(args, tag):
    log.write(f"\n\n===== {tag} =====\n")
    p = pexpect.spawn(BASE[0], BASE[1:] + args, encoding="utf-8", timeout=240)
    p.logfile_read = log
    p.expect("vicdar login:")
    p.sendline("dev"); p.expect("Password:"); p.sendline("dev"); p.expect(PROMPT)
    return p

def run(p, cmd, timeout=120):
    p.sendline(cmd); p.expect(PROMPT, timeout=timeout)
    out = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", p.before).split("\n", 1)[-1].strip()
    print(f"$ {cmd}\n{out}\n", flush=True)
    return out

def check(cond, what):
    print(("OK   " if cond else "GAGAL ") + what, flush=True)
    if not cond: fails.append(what)

def off(p):
    p.sendline("echo dev | sudo -S -p '' poweroff"); p.expect(pexpect.EOF, timeout=90)

def screenshot(path):
    # screendump lewat monitor QEMU: layar VGA tetap dirender walau -nographic
    if os.path.exists(path): os.remove(path)
    s = socket.socket(socket.AF_UNIX); s.connect(MON)
    s.sendall(f"screendump {path} -f png\n".encode())
    for _ in range(20):
        if os.path.exists(path) and os.path.getsize(path) > 0: break
        time.sleep(0.5)
    s.close()
    return os.path.exists(path) and os.path.getsize(path) > 0

if which in ("all", "cd"):
    p = boot(["-cdrom", iso], "CD BIOS")
    o = run(p, "grep PRETTY /etc/os-release"); check("VicDar Linux" in o, "os-release")
    # komponen desktop menyala bertahap, tunggu sampai semuanya ada (maks 120 dtk)
    o = run(p, "D='Xorg xfce4-session xfce4-panel xfdesktop nm-applet pipewire'; "
               "for i in $(seq 120); do n=0; for x in $D; do pgrep -x $x >/dev/null && n=$((n+1)); done; [ $n -eq 6 ] && break; sleep 1; done; "
               "systemctl is-active lightdm; for x in $D; do pgrep -x $x >/dev/null && echo JALAN:$x || echo MATI:$x; done", timeout=180)
    check("MATI" not in o and o.startswith("active"), "desktop XFCE jalan (lightdm, Xorg, panel, nm-applet, pipewire)")
    o = run(p, "for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do loginctl show-session $s -p Name -p Type -p Seat --value | paste -sd' '; done")
    check(any({"dev", "x11", "seat0"} <= set(l.split()) for l in o.splitlines()), "sesi grafis dev di seat0 (login otomatis)")
    o = run(p, "pgrep -a nm-applet; xfconf-query -c xfce4-panel -p /plugins/plugin-10/items")
    check("--indicator" in o and "vicdar-session.desktop" in o, "rel: ikon jaringan mode indikator + tombol sesi")
    o = run(p, "codium --version 2>/dev/null | head -1; firefox-esr --version 2>/dev/null")
    check("Firefox" in o and re.search(r"^\d+\.\d+", o, re.M) is not None, "VSCodium + Firefox terpasang")
    run(p, "sleep 5")
    check(screenshot("/var/tmp/vicdar-desktop.png"), "screenshot desktop tersimpan")
    # desktop yang sedang dipakai: terminal + VSCodium, lalu menu aplikasi terbuka
    run(p, "export DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority; "
           "(xfce4-terminal --geometry=92x26+90+70 -x bash -c 'go version; podman --version; exec bash' >/dev/null 2>&1 &); "
           "(codium --new-window >/dev/null 2>&1 &); sleep 15", timeout=60)
    check(screenshot("/var/tmp/vicdar-apps.png"), "screenshot aplikasi tersimpan")
    run(p, "xfce4-popup-whiskermenu; sleep 3")
    check(screenshot("/var/tmp/vicdar-menu.png"), "screenshot menu tersimpan")
    o = run(p, "for c in gcc python3 node go rustc cargo podman git cmake gdb; do command -v $c >/dev/null && echo ADA:$c || echo HILANG:$c; done")
    check("HILANG" not in o, "semua toolchain ada")
    run(p, "gcc --version | head -1; python3 --version; node --version; go version; rustc --version; podman --version")
    o = run(p, "echo dev | sudo -S -p '' true && echo SUDO_OK"); check("SUDO_OK" in o, "sudo jalan")
    o = run(p, "sleep 3; nmcli -t -f DEVICE,STATE device"); check(":connected" in o, "NetworkManager terhubung")
    o = run(p, "getent hosts deb.debian.org >/dev/null && echo DNS_OK"); check("DNS_OK" in o, "DNS")
    o = run(p, "systemctl --failed --no-legend | wc -l"); check(o.strip().endswith("0"), "tidak ada unit gagal")
    o = run(p, "sudo vicdar-simpan; echo RC=$?"); check("CD/DVD" in o and "RC=1" in o, "vicdar-simpan menolak CD")
    o = run(p, "podman run --rm docker.io/library/alpine:3.22 echo PODMAN_OK 2>&1 | tail -3", timeout=240)
    check("PODMAN_OK" in o, "podman run (rootless) jalan")
    o = run(p, "ls /lib/firmware | wc -l"); check(int(o.split()[-1]) > 20, "firmware ada")
    off(p)

if which in ("all", "usb"):
    if os.path.exists("/var/tmp/t-usb.img"): os.remove("/var/tmp/t-usb.img")
    shutil.copy(iso, "/var/tmp/t-usb.img"); os.truncate("/var/tmp/t-usb.img", 4 * 1024**3)
    p = boot(USB, "USB BIOS #1")
    o = run(p, "findmnt -no SOURCE /run/live/medium"); print("medium:", o)
    p.sendline("echo dev | sudo -S -p '' true; sudo vicdar-simpan")
    p.expect("Ketik YA"); p.sendline("YA")
    p.expect(PROMPT, timeout=180); out = p.before; print(out)
    check("Selesai" in out, "vicdar-simpan selesai")
    run(p, "lsblk -o NAME,SIZE,LABEL,FSTYPE")
    off(p)
    o = subprocess.run(["sfdisk", "-V", "/var/tmp/t-usb.img"], capture_output=True, text=True)
    print("sfdisk -V:", o.stdout.strip(), o.stderr.strip())
    p = boot(USB, "USB BIOS #2 (persistence aktif, tulis file)")
    o = run(p, "findmnt -rn -o SOURCE,TARGET | grep -i persistence"); check("sda" in o, "partisi persistence dipakai live-boot")
    run(p, "echo bukti-123 > ~/bukti.txt; echo dev | sudo -S -p '' sh -c 'echo root-ok > /etc/bukti-root'; sync")
    off(p)
    p = boot(USB, "USB BIOS #3 (cek)")
    o = run(p, "cat ~/bukti.txt /etc/bukti-root"); check("bukti-123" in o and "root-ok" in o, "file home + /etc tersimpan setelah reboot (BIOS)")
    o = run(p, "echo dev | sudo -S -p '' vicdar-simpan"); check("sudah ada" in o, "vicdar-simpan tahu partisi sudah ada")
    off(p)
    p = boot(USB + UEFI, "USB UEFI (persistence)")
    o = run(p, "cat ~/bukti.txt; test -d /sys/firmware/efi && echo MODE_UEFI")
    check("bukti-123" in o and "MODE_UEFI" in o, "boot UEFI + file tersimpan")
    off(p)

print("HASIL:", "SEMUA LULUS" if not fails else "GAGAL: " + "; ".join(fails))
