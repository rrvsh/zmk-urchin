# Agent Guidelines for zmk-urchin

On `feat/dolphin34`, this repository ports the Urchin keymap to the Dolphin34 using ZMK's in-tree Cradio shields and no displays. The original Urchin hardware config remains on `prime`. Read `README.md` and `docs/flashing.md` before touching firmware; do not flash an Urchin UF2 to Dolphin.

When working here, load and follow the local skill at `.pi/skills/zmk-urchin/SKILL.md`.

Run Just tasks through the dev shell, e.g. `nix develop --command just build`.

The local `scripts/flash.sh` helper builds before bootloader mode, checks one matching removable UF2 drive, backs up stock `CURRENT.UF2` read-only on the first flash of each half, then copies firmware and cleans up. The Dolphin bootloader ID has not yet been verified.

On the **stock Dolphin** keymap, press both right thumbs together and press `Q` for the left bootloader or `P` for the right bootloader. Once left is flashed, use a double-tap of the target half's physical reset to enter bootloader mode. Do not assume the factory key chord still applies. Verify the UF2 device before any first flash.

Prefer keeping the GitHub Actions plus West workflow simple and reproducible. If adding Nix support, base it on `github:lilyinstarlight/zmk-nix` and document how to update `zephyrDepsHash`.
