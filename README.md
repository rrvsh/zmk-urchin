# zmk-urchin

Standalone ZMK firmware configuration for an Urchin split keyboard.

Hardware/configuration in this repo:

- Keyboard shield: `urchin_left` / `urchin_right` from `duckyb/urchin-zmk-module`
- Controller board: `nice_nano_v2`
- Displays: `nice_view_adapter nice_view_gem` from `M165437/nice-view-gem`
- ZMK: pinned to `v0.2.0` in `config/west.yml`
- ZMK Studio: enabled for the left/central half via `studio-rpc-usb-uart` and `-DCONFIG_ZMK_STUDIO=y`

## Layout

- `config/build.yaml`: build matrix for left, right, and settings reset firmware.
- `config/west.yml`: West manifest with ZMK and external modules.
- `config/urchin.conf`: Kconfig options for Bluetooth, sleep, display, and nice-view-gem.
- `config/urchin.keymap`: layers, home-row mods, combos, and thumb keys.
- `config/urchin.json`: physical layout metadata for visual tools/ZMK Studio.
- `flake.nix`: Nix/zmk-nix firmware packages and development shell.
- `Justfile`: build, update, flash, and cleanup commands.
- `.github/workflows/build-zmk.yaml`: GitHub Actions wrapper that runs the Just/Nix build.
- `.pi/skills/zmk-urchin/SKILL.md`: local Pi skill for working on this repo.

## Nix and Just build

Enter the development shell:

```sh
nix develop
```

Build all firmware into the `result` symlink:

```sh
just build
```

Useful tasks:

```sh
just build            # build all .uf2 files
just build-firmware   # build only left/right Urchin firmware
just build-settings-reset
just update           # update West deps and zephyrDepsHash
just flash left       # flash via zmk-nix helper
just clean            # remove result symlinks
```

Current output files:

- `urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2`

## GitHub Actions build

Push or run the workflow manually. The workflow installs Nix and runs `nix develop --command just build`. It builds artifacts for:

- `urchin_left nice_view_adapter nice_view_gem` on `nice_nano_v2`
- `urchin_right nice_view_adapter nice_view_gem` on `nice_nano_v2`
- `settings_reset` on `nice_nano_v2`

Download the `firmware` artifact from the workflow run and flash the `.uf2` files by putting the matching controller into bootloader mode and copying the `.uf2` to the mounted drive. See [docs/flashing.md](docs/flashing.md) for prerequisites, normal flashing, `just flash`, and settings-reset procedures.

## Local west build sketch

The Nix/Just flow is the canonical build path. For manual source builds without Nix, initialize a West workspace from this config and build each side separately:

```sh
BASE_DIR=/tmp/zmk-urchin-build
mkdir -p "$BASE_DIR"
cp -R config "$BASE_DIR/config"
cd "$BASE_DIR"
west init -l config
west update --fetch-opt=--filter=tree:0
west zephyr-export
west build -s zmk/app -d build/left -b nice_nano_v2 -S studio-rpc-usb-uart -- \
  -DSHIELD="urchin_left nice_view_adapter nice_view_gem" \
  -DZMK_CONFIG="$BASE_DIR/config" \
  -DCONFIG_ZMK_STUDIO=y
west build -s zmk/app -d build/right -b nice_nano_v2 -- \
  -DSHIELD="urchin_right nice_view_adapter nice_view_gem" \
  -DZMK_CONFIG="$BASE_DIR/config"
```

## Nix note

This repo uses `github:lilyinstarlight/zmk-nix` with `buildSplitKeyboard` for the Urchin halves and `buildKeyboard` for `settings_reset`. `zephyrDepsHash` pins the resolved West dependency tree. If `config/west.yml` changes, run `just update` or temporarily use a fake hash and rebuild to get the expected hash.

The Nix build currently enables `CONFIG_NEWLIB_LIBC=y` and suppresses implicit function declaration diagnostics to keep `nice-view-gem v0.3.0` building with nixpkgs' newer `arm-none-eabi-gcc`. If nice-view-gem becomes too expensive to maintain, remove `nice_view_adapter nice_view_gem` from the shield strings and remove the display-specific Kconfig options while keeping `config/urchin.keymap` intact.
