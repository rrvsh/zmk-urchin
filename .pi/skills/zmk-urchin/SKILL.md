---
name: zmk-urchin
description: Work on this Urchin ZMK firmware config repository. Use for ZMK keymap/config edits, builds, GitHub Actions failures, nice!nano v2, Urchin shields, nice!view/nice-view-gem display setup, ZMK Studio, west manifests, and possible zmk-nix flake work.
---

# ZMK Urchin Skill

## Repository purpose

This repo is a standalone ZMK user config for an Urchin split keyboard:

- MCU board: `nice_nano_v2`.
- Keyboard shields: `urchin_left` and `urchin_right` from `duckyb/urchin-zmk-module`.
- Display shields: `nice_view_adapter nice_view_gem` from `M165437/nice-view-gem`.
- Reset firmware: `settings_reset` for clearing BLE/settings.
- ZMK version: pinned in `config/west.yml`.
- ZMK Studio: enabled only on the central/left half with snippet `studio-rpc-usb-uart` and `-DCONFIG_ZMK_STUDIO=y`.

## File map

- `config/build.yaml`: GitHub Actions build matrix. Keep left/right/settings_reset entries in sync with workflow if the workflow is hand-written.
- `config/west.yml`: West manifest for ZMK plus external modules. Pin ZMK and module revisions rather than tracking moving branches when stability matters.
- `config/urchin.conf`: Kconfig settings. Use `CONFIG_FOO=y`, `CONFIG_FOO=n`, numbers, or quoted strings.
- `config/urchin.keymap`: Devicetree keymap, combos, layers, behaviors, and includes.
- `config/urchin.json`: physical layout metadata for visual editing/ZMK Studio style tooling.
- `.github/workflows/build-zmk.yaml`: containerized build using `zmkfirmware/zmk-build-arm:stable`.

## ZMK mental model

ZMK builds firmware using Zephyr and West.

- Boards are MCU boards or onboard-MCU keyboards. Here the board is `nice_nano_v2`.
- Shields are keyboard PCBs or add-ons. Here the keyboard halves and displays are shields passed via `-DSHIELD`.
- User config is found through `-DZMK_CONFIG=/absolute/path/to/config` and contains `.conf`, `.keymap`, `build.yaml`, `west.yml`, and optional metadata.
- External modules can provide out-of-tree shields, boards, display code, and behaviors. They are declared in `west.yml`; local builds may also need `-DZMK_EXTRA_MODULES` pointing at the workspace/module root.
- Split keyboards must build and flash each half independently. Left/central usually owns USB, BLE profile management, and ZMK Studio.

## Keymap editing rules

- Include key constants from `#include <dt-bindings/zmk/keys.h>`.
- `&kp KEY` sends a key press.
- `&mt MOD KEY` is mod-tap. This repo sets `&mt { flavor = "tap-preferred"; };`.
- `&lt LAYER KEY` is layer-tap.
- `&mo LAYER` momentarily activates a layer.
- `&tog LAYER` toggles a layer.
- `&none` leaves a position empty.
- Combos live under `/ { combos { compatible = "zmk,combos"; ... }; };` and use physical key position numbers.
- Keep each layer binding count equal to the shield layout count. Urchin here is 34 keys: 30 finger keys plus 4 thumbs.
- For ZMK Studio, do not assume runtime edits will change source files. Studio can override stock keymap until stock settings are restored.

## Config editing rules

- Bluetooth/sleep/display options are compile-time Kconfig in `config/urchin.conf`.
- `CONFIG_ZMK_DISPLAY=y` and `CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM=y` are required for nice-view-gem.
- `CONFIG_NICE_VIEW_GEM_ANIMATION=n` disables the peripheral animation to save battery.
- For ZMK Studio builds, set `CONFIG_ZMK_STUDIO=y` through build args or Kconfig and build with the `studio-rpc-usb-uart` snippet on the central side only.

## Current build matrix

Expected firmware builds:

```yaml
include:
  - board: nice_nano_v2
    shield: urchin_left nice_view_adapter nice_view_gem
    snippet: studio-rpc-usb-uart
    cmake-args: -DCONFIG_ZMK_STUDIO=y
  - board: nice_nano_v2
    shield: urchin_right nice_view_adapter nice_view_gem
  - board: nice_nano_v2
    shield: settings_reset
```

## Local West build

The GitHub Actions workflow is the primary build path. For local source builds, use an isolated workspace:

```bash
BASE_DIR=/tmp/zmk-urchin-build
rm -rf "$BASE_DIR"
mkdir -p "$BASE_DIR"
cp -R config "$BASE_DIR/config"
cd "$BASE_DIR"
west init -l config
west update --fetch-opt=--filter=tree:0
west zephyr-export
```

Build left/central with Studio:

```bash
west build -s zmk/app -d build/left -b nice_nano_v2 -S studio-rpc-usb-uart -- \
  -DSHIELD=urchin_left -DSHIELD=nice_view_adapter -DSHIELD=nice_view_gem \
  -DZMK_CONFIG="$BASE_DIR/config" \
  -DZMK_EXTRA_MODULES="$BASE_DIR" \
  -DCONFIG_ZMK_STUDIO=y
```

Build right:

```bash
west build -s zmk/app -d build/right -b nice_nano_v2 -- \
  -DSHIELD=urchin_right -DSHIELD=nice_view_adapter -DSHIELD=nice_view_gem \
  -DZMK_CONFIG="$BASE_DIR/config" \
  -DZMK_EXTRA_MODULES="$BASE_DIR"
```

Build settings reset:

```bash
west build -s zmk/app -d build/settings_reset -b nice_nano_v2 -- \
  -DSHIELD=settings_reset \
  -DZMK_CONFIG="$BASE_DIR/config"
```

Artifacts are normally under `build/<name>/zephyr/zmk.uf2`.

## Flashing workflow

- Put a nice!nano v2 into bootloader mode, usually by double-tapping reset.
- Copy the matching `.uf2` to the mounted UF2 volume.
- Flash both halves after a keymap change.
- Use `settings_reset` on both controllers when Bluetooth pairing/settings are stale, then reflash left and right firmware.

## Nix flakes and zmk-nix

The main community flake is `github:lilyinstarlight/zmk-nix`.

Use it when asked to add Nix builds. Its important pieces:

- `zmk-nix.legacyPackages.${system}.buildKeyboard` for one firmware.
- `zmk-nix.legacyPackages.${system}.buildSplitKeyboard` for left/right split firmware.
- `board = "nice_nano_v2"` for this repo.
- `shield = "urchin_%PART% nice_view_adapter nice_view_gem"` for split builds.
- `enableZmkStudio = true` can handle Studio build flags for the central side in recent zmk-nix.
- `zephyrDepsHash` is a fixed-output hash of West dependencies; initialize with a fake hash, build once to get the expected hash, or use `nix run .#update` if the template/update package is available.
- Keep `src` filtered to ZMK-relevant suffixes such as `.conf`, `.keymap`, `.json`, `.yml`, `.dts`, `.dtsi`, `.overlay`, `.shield`, `.defconfig`, `.cmake`, `.board`.

Do not add a flake that claims to work unless it has a real `zephyrDepsHash` or the README clearly labels it as needing hash update.

## Research references

- ZMK configuration overview: `https://zmk.dev/docs/config`
- ZMK local build/flash docs: `https://zmk.dev/docs/development/local-toolchain/build-flash`
- ZMK modules docs: `https://zmk.dev/docs/features/modules`
- ZMK Studio docs: `https://zmk.dev/docs/features/studio`
- Urchin hardware: `https://github.com/duckyb/urchin`
- Urchin ZMK module: `https://github.com/duckyb/urchin-zmk-module`
- nice-view-gem: `https://github.com/M165437/nice-view-gem`
- zmk-nix: `https://github.com/lilyinstarlight/zmk-nix`
