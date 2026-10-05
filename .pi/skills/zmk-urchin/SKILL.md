---
name: zmk-urchin
description: Work on the shared Urchin and Dolphin34 ZMK firmware repository, including keymaps, builds, flashing, nice!nano v2, displays, Cradio shields, ZMK Studio, West, and zmk-nix.
---

# Urchin and Dolphin34 ZMK skill

## Repository purpose

This repository builds one shared 34-position keymap for two keyboards:

- Urchin: `urchin_left` and `urchin_right` with `nice_view_adapter nice_view_gem`.
- Dolphin34: ZMK's in-tree `cradio_left` and `cradio_right` shields without displays.
- Both use `nice_nano_v2` and pinned ZMK dependencies from `config/west.yml`.
- ZMK Studio is enabled only on each split's left/central half.

## File map

- `config/shared.keymap.dtsi`: shared behaviors, macros, combos, and layers.
- `config/urchin.keymap`: thin Urchin entry point that includes the shared keymap.
- `config/cradio.keymap`: thin Dolphin34 entry point that includes the shared keymap.
- `config/urchin.conf` and `config/urchin.json`: Urchin and display configuration.
- `config/cradio.conf` and `config/cradio_left.conf`: Dolphin34 configuration.
- `config/build.yaml`: reference matrix for both keyboards and settings reset.
- `flake.nix`: zmk-nix packages for both split keyboards and settings reset.
- `docs/keymap.html`: rendered shared layout.
- `docs/flashing.md`: overview with links to hardware-specific instructions.

## Keymap rules

- Edit bindings only in `config/shared.keymap.dtsi` unless the hardware layouts genuinely diverge.
- Keep both `.keymap` files as thin includes so the layouts cannot drift.
- The layout has 34 positions: 30 finger keys and four thumb keys.
- Keep every layer at exactly 34 bindings.
- Combos use physical position numbers and apply on all layers unless explicitly restricted.
- ZMK Studio runtime edits do not update source and can override compiled bindings.
- Run `nix develop --command just render-keymap` after a keymap edit and inspect `docs/keymap.html`.

## Build

Use Nix and Just:

```bash
nix develop --command just build
nix develop --command just build-urchin
nix develop --command just build-dolphin34
nix develop --command just build-settings-reset
```

`just build` must produce:

- `urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `dolphin34_left-nice_nano_v2-zmk.uf2`
- `dolphin34_right-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2`

Urchin requires the external Urchin and nice-view-gem modules plus its Nix ARM compiler compatibility flags. Dolphin34 uses the in-tree Cradio shields and must not inherit display-specific configuration.

`zephyrDepsHash` pins the resolved West dependency graph. Update it after changing `config/west.yml`. Do not leave the flake claiming to work unless `just build` succeeds.

## Flashing safety

Read the relevant hardware page linked from `docs/flashing.md` before flashing.

The command requires both keyboard and half:

```bash
nix develop --command just flash urchin left
nix develop --command just flash dolphin34 left
```

Never infer the keyboard from `left` or `right`. The helper must keep hardware-specific backup directories and refuse multiple matching bootloaders.

Keymap-only changes need the left/central half only. Flash both halves after shield, board, display, split, module, or ZMK changes. Do not reset persistent settings unless recovering a specific pairing or Studio-state problem.

## ZMK model

- `&kp KEY` sends a key press.
- `&mt MOD KEY` is mod-tap; this keymap uses tap-preferred behavior.
- `&lt LAYER KEY` is layer-tap.
- `&mo LAYER` momentarily activates a layer.
- `&none` disables a position.
- Split halves build independently; the central half handles host output and keymap processing.
- West owns modules listed in `config/west.yml`; do not pass the whole workspace through `ZMK_EXTRA_MODULES`.

## References

- ZMK configuration: `https://zmk.dev/docs/config`
- ZMK build and flash: `https://zmk.dev/docs/development/local-toolchain/build-flash`
- zmk-nix: `https://github.com/lilyinstarlight/zmk-nix`
- Urchin: `https://github.com/duckyb/urchin`
- Dolphin34 seller config: `https://github.com/bigeqali/dolphin34`
