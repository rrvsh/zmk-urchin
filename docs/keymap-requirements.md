# Keymap requirements

These are current working requirements and preferences for redesigning the Urchin keymap. They are subject to change.

## Fixed / strong preferences

- Start from a simple base layer and add features intentionally.
- Left thumb should have `Space` for sure.
- Number layer should place `1` through `0` on the home row.

## Preferred combos

- `Enter`: middle + ring fingers.
- `Esc`: all four home-row fingers.
- Prefer keeping these as combos rather than dedicated thumb keys if practical.
- Combos are based on finger position and should apply on all layers, not only the base layer.

## Home-row mods

Preferred modifier order on home row:

- Pinky: `Ctrl`
- Ring: `Cmd` / GUI
- Middle: `Opt` / Alt
- Index: `Shift`

This matches the previous home-row-mod style:

```text
Ctrl  Cmd  Opt  Shift     Shift  Opt  Cmd  Ctrl
```

## Gaming concerns

Home-row mods interfere with gaming because holding movement keys such as `WASD` can activate modifiers.

Requirements / open questions for gaming:

- Need `Shift`, `Ctrl`, and `Alt` accessible while gaming/movement is active.
- Avoid accidental home-row-mod activation during movement.
- Switching away from `WASD` is acceptable.
- A dedicated gaming layer may be useful.

## Communication convention

When discussing keymap edits, use global key indices from the rendered HTML.

- Each physical layer has 34 positions.
- Global key index formula: `global = layer * 34 + physical_position`.
- Layer 0 uses indices `0` through `33`.
- Layer 1 uses indices `34` through `67`.
- Layer 2 uses indices `68` through `101`.
- Layer 3 uses indices `102` through `135`.

Examples:

- `31` is layer 0, physical position 31: left thumb right.
- `67` is layer 1, physical position 33: right thumb right.
- `106` is layer 3, physical position 4: left top row inner key.
- `107` is layer 3, physical position 5: right top row inner key.

Combos are the exception: ZMK combos use physical key positions, not global layer indices. For combos, use physical positions such as `11 + 12` for left middle + ring.

## Current open design problem

Find a layout that preserves:

- Comfortable typing with home-row mods.
- Reliable gaming controls without home-row-mod interference.
- Left thumb `Space`.
- Combo-based `Enter` and `Esc`.
- Home-row `1` through `0` number layer.
