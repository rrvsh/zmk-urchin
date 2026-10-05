# Agent Guidelines for zmk-urchin

This repository builds one shared 34-position ZMK keymap for both Urchin and Dolphin34 hardware. Urchin uses external shields and nice-view-gem displays; Dolphin34 uses ZMK's in-tree Cradio shields without displays.

When working here, load and follow `.pi/skills/zmk-urchin/SKILL.md`. Read `README.md` and the relevant hardware page linked from `docs/flashing.md` before touching firmware.

Run Just tasks through the dev shell, for example `nix develop --command just build`.

Edit shared bindings in `config/shared.keymap.dtsi`. Keep `config/urchin.keymap` and `config/cradio.keymap` as thin hardware entry points so the layouts cannot drift.

The flash helper requires both keyboard and half, for example `just flash urchin left` or `just flash dolphin34 left`. Never weaken this requirement or flash an image based only on its half name.

The helper builds first, checks one matching removable UF2 drive, preserves existing firmware under a hardware-specific backup directory, then copies the selected image. Do not bypass its checks without explicit approval.

Prefer a thin GitHub Actions workflow that calls the Nix/Just build. Update `zephyrDepsHash` whenever the West dependency graph changes, and do not claim the build works until `just build` succeeds.
