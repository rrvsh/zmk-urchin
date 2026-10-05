# Flashing the Dolphin34 port

Build first:

```sh
nix develop --command just build
```

Keep the keyboard connected and working until the build and `sudo` authentication finish. The output is in `result/`:

- `dolphin34_left-nice_nano_v2-zmk.uf2`
- `dolphin34_right-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2` (only for deliberate settings recovery)

## Enter the stock firmware's bootloader

In the [seller's keymap](https://github.com/bigeqali/dolphin34/blob/017db149d5379689e5b46533e5381af744cfc7bf/config/cradio.keymap), pressing the **two right thumb keys together** activates Media. While holding them, press **Q** for the left half or **P** for the right half. Alternatively double-tap the physical reset button on the half you intend to flash. Entering bootloader mode does not erase firmware; copying a UF2 does.

Check its USB identity and UF2 drive before using the flash helper. The helper defaults to the nice!nano UF2 ID `239a:00b3`, but the seller's controller/bootloader ID has not yet been verified. If it differs, pass the observed IDs as `ZMK_BOOTLOADER_VENDOR_ID` and `ZMK_BOOTLOADER_PRODUCT_ID`; never select a disk by name alone.

The bootloader may present `CURRENT.UF2`, a readback of the current application. Save both original halves before the first flash. The helper does this automatically under `~/Agents/artifacts/zmk-dolphin34/stock/left-stock.uf2` and `right-stock.uf2`. It mounts the UF2 device read-only first and refuses to flash if no readback or existing backup is available. If you deliberately waive only the right-half backup, set `ZMK_FLASH_SKIP_RIGHT_BACKUP=1`. Treat backups as private: they may include saved device state.

## First install

```sh
nix develop --command just flash left
nix develop --command just flash right
```

Run one command at a time, and enter bootloader mode on **only the named half** after the helper says it is ready. After flashing left, the new central keymap takes over: use a **double-tap of the physical reset button on the target half**. The factory chord no longer applies.

The helper builds before bootloader entry, authenticates sudo, waits for exactly one matching removable USB device, backs up stock `CURRENT.UF2` if not already saved, remounts read-write, copies the matching firmware, syncs, and unmounts. Do not copy `settings_reset` as part of the normal install.

For later keymap-only edits, flash left/central only. For changes to the shield, board, ZMK version, or split transport, rebuild and flash both halves. ZMK Studio may retain runtime binding overrides from the factory keymap; restore stock bindings in Studio if the source keymap seems not to take effect. Preserve Bluetooth pairings unless a specific issue requires a deliberate settings reset.

If the bootloader ID is absent, stop and investigate rather than bypassing the helper's checks. A missing `CURRENT.UF2` on the right half requires an explicit backup waiver. The old Urchin firmware is not for this board.
