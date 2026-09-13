# Agent Guidelines for zmk-urchin

This repository contains a standalone ZMK firmware configuration for an Urchin split keyboard with nice!nano v2 controllers and nice!view/nice-view-gem displays.

When working here, load and follow the local skill at `.pi/skills/zmk-urchin/SKILL.md`.

Run Just tasks through the dev shell, e.g. `nix develop --command just build`.

For keymap-only changes, flash the left half:

1. Run `nix develop --command just flash left`.
2. Hold both outer thumb keys to activate layer 2.
3. Hold `T` to put the left half into bootloader mode.

To flash the right half, run `nix develop --command just flash right`, then use the same thumb chord and hold `Y`.

Prefer keeping the GitHub Actions plus West workflow simple and reproducible. If adding Nix support, base it on `github:lilyinstarlight/zmk-nix` and document how to update `zephyrDepsHash`.
