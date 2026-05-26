# Turing Smart Screen — autostart & control

How the 3.5" system-stats display is set up to run automatically on this Fedora 44 / KDE machine, and how to control it.

## What's running

- **Theme:** `MinimalDark35` (in `res/themes/MinimalDark35/`)
- **Config:** `config.yaml` — `THEME: MinimalDark35`, `REVISION: A`, `COM_PORT: AUTO`
- **Launcher:** a **systemd `--user` service**, not a desktop autostart entry.

## Why a systemd service (not KDE Autostart)

We originally used a `~/.config/autostart/*.desktop` entry, but it only fires at a
fresh login and has no crash recovery. On **suspend/resume** the USB screen briefly
drops off the bus, the app dies, and nothing restarts it. The systemd service fixes
both: it starts at login **and** retries every 5s (`Restart=always`), so when the
screen re-appears on USB, `COM_PORT: AUTO` re-discovers it with no intervention.

> Note: if the screen is *physically* gone (unplugged / bad cable), the service just
> loops harmlessly until it's reachable again.

## Service file

`~/.config/systemd/user/turing-smart-screen.service`

```ini
[Unit]
Description=Turing Smart Screen system stats display (MinimalDark35 theme)
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
WorkingDirectory=/home/ben/turing-smart-screen-python
ExecStart=/home/ben/turing-smart-screen-python/venv/bin/python /home/ben/turing-smart-screen-python/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
```

It runs the project's **venv** Python (`venv/bin/python`), so its dependencies
(psutil, babel, etc.) are available.

## Controlling it

```bash
systemctl --user status  turing-smart-screen      # is it running?
systemctl --user restart turing-smart-screen      # after a theme/config change
systemctl --user stop    turing-smart-screen      # stop until next login
systemctl --user start   turing-smart-screen      # start now
systemctl --user disable --now turing-smart-screen # stop AND don't start at login
systemctl --user enable  --now turing-smart-screen # re-enable + start
journalctl --user -u turing-smart-screen -f        # live logs
```

After editing the `.service` file, reload first:

```bash
systemctl --user daemon-reload && systemctl --user restart turing-smart-screen
```

## Running `configure.py` (stop the service first!)

`configure.py` opens the **same display device** the service is using. A USB display
(`REVISION: TUR_USB`, e.g. the 8.8") can only be claimed by **one** process at a time,
so a running service will make configure fail with a busy / `Access denied` error.
Stop the service first, then hand the display back when done:

```bash
systemctl --user stop  turing-smart-screen   # free the display
python configure.py                           # make changes, save & quit
systemctl --user start turing-smart-screen    # service picks up the new config
```

`stop` does **not** trigger the `Restart=always` loop — the service stays down until
you `start` it, so configure won't be fighting a respawn every 5s in the background.

## Changing the theme / display

1. Edit `config.yaml` (theme name, brightness, network interfaces, etc.).
2. To regenerate the `MinimalDark35` layout: edit constants in
   `res/themes/MinimalDark35/_gen_theme.py`, then
   `python3 _gen_theme.py` (and `make_background.py` for the background image).
3. `systemctl --user restart turing-smart-screen`.

To preview without hardware, set `REVISION: SIMU` in `config.yaml`, run
`./venv/bin/python main.py`, and open <http://localhost:5678> (writes `screencap.png`).
Set it back to `REVISION: A` for the real screen.

## Troubleshooting: screen doesn't return after suspend

If it drops off USB on *every* suspend (not just a one-off cable issue), that's USB
autosuspend powering down the port. Identify the device and pin it with a udev rule:

```bash
lsusb              # find the screen's vendor:product, e.g. 1a86:7523 (CH340 serial)
```

Then create `/etc/udev/rules.d/99-turing-screen.rules` (root):

```
# disable USB autosuspend for the Turing smart screen
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="1a86", ATTR{idProduct}=="7523", TEST=="power/control", ATTR{power/control}="on"
```

`sudo udevadm control --reload && sudo udevadm trigger`, then replug.
