# Flashing Urchin firmware

Urchin uses `urchin_left` and `urchin_right` with nice!view adapters and nice-view-gem displays.

## Firmware

Build only Urchin:

```sh
nix develop --command just build-urchin
```

The split output exposed by that command contains `zmk_left.uf2` and `zmk_right.uf2`. A full `just build` also produces these named files under `result/`:

- `urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`

## Flash with the helper

```sh
nix develop --command just flash urchin left
nix develop --command just flash urchin right
```

Run one command at a time and enter bootloader mode only on the named half after the helper is ready. Double-tap the half's reset control, or use the shared keymap's bootloader binding:

- Left: hold both outer thumbs, then hold `T`.
- Right: hold both outer thumbs, then press `/`.

The helper saves existing firmware under `~/Agents/artifacts/zmk-urchin/stock/` before writing.

For shared-keymap changes, flash only the left/central half. Flash both halves after Urchin configuration, display, module, split, board, or ZMK changes.
