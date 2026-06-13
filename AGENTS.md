# Agent Guidelines for zmk-urchin

This repository contains a standalone ZMK firmware configuration for an Urchin split keyboard with nice!nano v2 controllers and nice!view/nice-view-gem displays.

When working here, load and follow the local skill at `.pi/skills/zmk-urchin/SKILL.md`.

Run Just tasks through the dev shell, e.g. `nix develop --command just build`.

Prefer keeping the GitHub Actions plus West workflow simple and reproducible. If adding Nix support, base it on `github:lilyinstarlight/zmk-nix` and document how to update `zephyrDepsHash`.
