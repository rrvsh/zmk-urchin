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
- `.github/workflows/build-zmk.yaml`: GitHub Actions firmware build.
- `.pi/skills/zmk-urchin/SKILL.md`: local Pi skill for working on this repo.

## GitHub Actions build

Push or run the workflow manually. It builds artifacts for:

- `urchin_left nice_view_adapter nice_view_gem` on `nice_nano_v2`
- `urchin_right nice_view_adapter nice_view_gem` on `nice_nano_v2`
- `settings_reset` on `nice_nano_v2`

Download the `firmware` artifact from the workflow run and flash the `.uf2` files by putting the matching controller into bootloader mode and copying the `.uf2` to the mounted drive.

## Local west build sketch

The workflow is the canonical build path. For local source builds, initialize a West workspace from this config and build each side separately:

```sh
BASE_DIR=/tmp/zmk-urchin-build
mkdir -p "$BASE_DIR"
cp -R config "$BASE_DIR/config"
cd "$BASE_DIR"
west init -l config
west update --fetch-opt=--filter=tree:0
west zephyr-export
west build -s zmk/app -d build/left -b nice_nano_v2 -S studio-rpc-usb-uart -- \
  -DSHIELD=urchin_left -DSHIELD=nice_view_adapter -DSHIELD=nice_view_gem \
  -DZMK_CONFIG="$BASE_DIR/config" \
  -DZMK_EXTRA_MODULES="$BASE_DIR" \
  -DCONFIG_ZMK_STUDIO=y
west build -s zmk/app -d build/right -b nice_nano_v2 -- \
  -DSHIELD=urchin_right -DSHIELD=nice_view_adapter -DSHIELD=nice_view_gem \
  -DZMK_CONFIG="$BASE_DIR/config" \
  -DZMK_EXTRA_MODULES="$BASE_DIR"
```

## Nix note

`zmk-nix` is the main Nix flake ecosystem project for ZMK firmware builds. This repo intentionally keeps the GitHub Actions/West workflow as the source of truth for now. If adding a flake later, use `github:lilyinstarlight/zmk-nix`, `buildSplitKeyboard`, `board = "nice_nano_v2"`, `shield = "urchin_%PART% nice_view_adapter nice_view_gem"`, and set/update `zephyrDepsHash` with `nix run .#update`.
