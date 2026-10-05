# Urchin and Dolphin34 ZMK firmware

This repository builds the same 34-position keymap for two split keyboards:

- **Urchin:** `urchin_left` and `urchin_right` with nice!view/nice-view-gem displays.
- **Dolphin34:** ZMK's in-tree `cradio_left` and `cradio_right` shields without displays.

Both use `nice_nano_v2` and ZMK `v0.2.0`. The shared behaviors, combos, macros, and layers live in `config/shared.keymap.dtsi`. The shield-specific `config/urchin.keymap` and `config/cradio.keymap` files only include that shared layout.

## Repository layout

- `config/shared.keymap.dtsi`: shared 34-key layout.
- `config/urchin.keymap`, `config/urchin.conf`, `config/urchin.json`: Urchin entry point and hardware configuration.
- `config/cradio.keymap`, `config/cradio.conf`, `config/cradio_left.conf`: Dolphin34 entry point and hardware configuration.
- `config/build.yaml`: reference build matrix for both keyboards and settings reset.
- `config/west.yml`: pinned ZMK, Urchin, and display modules.
- `flake.nix`: Nix builds for both keyboards.
- `docs/keymap.html`: rendered shared layout.
- `docs/flashing.md`: flashing overview and links to hardware-specific instructions.

## Build

Run commands through the Nix development shell:

```sh
nix develop --command just build
nix develop --command just render-keymap
```

`just build` writes five files under `result/`:

- `urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `dolphin34_left-nice_nano_v2-zmk.uf2`
- `dolphin34_right-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2`

Targeted builds are also available:

```sh
nix develop --command just build-urchin
nix develop --command just build-dolphin34
nix develop --command just build-settings-reset
```

## Flash

Read [`docs/flashing.md`](docs/flashing.md) before flashing. The helper requires an explicit keyboard and half so it cannot silently select the wrong firmware:

```sh
nix develop --command just flash urchin left
nix develop --command just flash dolphin34 left
```

A keymap-only change normally requires flashing only the left/central half. Hardware, display, split, module, or ZMK changes require both halves.

The helper builds the selected keyboard, verifies one removable UF2 bootloader, saves the existing firmware under a hardware-specific private backup directory, and then copies the matching image. It never chooses a keyboard target implicitly.

## Updating dependencies

`zephyrDepsHash` pins the resolved West dependency tree. After changing `config/west.yml`, run `nix develop --command just update` and validate `just build`. Urchin keeps the compatibility flags needed to build nice-view-gem with the current Nix ARM toolchain; Dolphin34 does not use them.
