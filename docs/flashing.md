# Flashing firmware

The repository builds distinct Urchin and Dolphin34 images. Never flash an image based only on its left/right half: always identify the keyboard too.

Read the hardware-specific instructions first:

- [Urchin flashing](flashing-urchin.md)
- [Dolphin34 flashing](flashing-dolphin34.md)

## Build

```sh
nix develop --command just build
```

The `result/` directory contains two Urchin images, two Dolphin34 images, and one settings-reset image.

## Safe helper commands

The local helper requires an explicit keyboard and half:

```sh
nix develop --command just flash urchin left
nix develop --command just flash urchin right
nix develop --command just flash dolphin34 left
nix develop --command just flash dolphin34 right
```

It builds the selected target before bootloader entry, authenticates `sudo` while the keyboard still works, waits for exactly one removable USB bootloader matching `239a:00b3`, mounts it read-only, and saves `CURRENT.UF2` before writing. Backups are kept separately under:

- `~/Agents/artifacts/zmk-urchin/stock/`
- `~/Agents/artifacts/zmk-dolphin34/stock/`

The helper refuses to continue without an existing backup or readable `CURRENT.UF2`. The only exception is an explicit right-half waiver using `ZMK_FLASH_SKIP_RIGHT_BACKUP=1`.

## Split flashing rule

The left half is central and owns keymap processing for both halves.

- Keymap-only change: flash left only.
- Shield, board, display, split, module, or ZMK change: flash both halves.
- Settings recovery: deliberately flash settings reset to both halves, then restore the matching normal firmware to both halves.

Regular application flashing preserves Bluetooth bonds, selected profiles, split pairing, output selection, and ZMK Studio state. Do not use settings reset unless recovering a specific persistent-state problem.
