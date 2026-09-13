# Agent Guidelines for zmk-urchin

This repository contains a standalone ZMK firmware configuration for an Urchin split keyboard with nice!nano v2 controllers and nice!view/nice-view-gem displays.

When working here, load and follow the local skill at `.pi/skills/zmk-urchin/SKILL.md`.

Run Just tasks through the dev shell, e.g. `nix develop --command just build`.

The local `scripts/flash.sh` helper builds before bootloader mode, authenticates sudo while the keyboard works, detects bootloader USB ID `239a:00b3`, mounts the UF2 device, copies the firmware, and cleans up.

For keymap-only changes, run `nix develop --command just flash left`. When prompted, hold both outer thumb keys and hold `T`.

To flash the right half, run `nix develop --command just flash right`. When prompted, use the same thumb chord and hold `Y`.

Prefer keeping the GitHub Actions plus West workflow simple and reproducible. If adding Nix support, base it on `github:lilyinstarlight/zmk-nix` and document how to update `zephyrDepsHash`.
