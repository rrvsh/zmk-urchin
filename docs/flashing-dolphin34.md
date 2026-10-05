# Flashing Dolphin34 firmware

Dolphin34 uses ZMK's in-tree `cradio_left` and `cradio_right` shields with no displays.

## Firmware

Build only Dolphin34:

```sh
nix develop --command just build-dolphin34
```

The split output exposed by that command contains `zmk_left.uf2` and `zmk_right.uf2`. A full `just build` also produces these named files under `result/`:

- `dolphin34_left-nice_nano_v2-zmk.uf2`
- `dolphin34_right-nice_nano_v2-zmk.uf2`

## Factory bootloader binding

The seller's factory keymap activates Media by pressing both right thumb keys together. While holding them, press `Q` for the left bootloader or `P` for the right bootloader. Double-tapping the target half's physical reset is an alternative when it is accessible.

The left bootloader has been verified as nice!nano UF2 `239a:00b3`. The right bootloader has not been verified independently.

## Flash with the helper

```sh
nix develop --command just flash dolphin34 left
nix develop --command just flash dolphin34 right
```

Run one command at a time and enter bootloader mode only on the named half after the helper is ready. The helper saves existing firmware under `~/Agents/artifacts/zmk-dolphin34/stock/` before writing.

Once the shared keymap is installed, its bootloader bindings are:

- Left: hold both outer thumbs, then hold `T`.
- Right: hold both outer thumbs, then press `/`.

The corrected left firmware has been flashed and enumerates as `ZMK Project Dolphin`. The right half remains on factory firmware, so full split behavior is not yet verified. Do not flash the right half without deliberately resuming that validation.

For shared-keymap changes, flash only the left/central half. Flash both halves after Dolphin34 configuration, split, board, or ZMK changes.
