# Flashing Urchin ZMK firmware

This repo builds UF2 firmware for an Urchin split keyboard with nice!nano v2 controllers.

## Firmware artifacts

Run:

```sh
just build
```

The `result/` symlink will contain:

- `urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2`

Flash the left file to the left half, the right file to the right half, and the settings reset file to either half only when intentionally clearing persistent settings.

## Prerequisites

For manual flashing:

- A data-capable USB cable.
- A working USB port.
- Ability to access/mount removable USB mass-storage volumes.
- The built `.uf2` files from `just build` or the GitHub Actions `firmware` artifact.

For `just flash` on Linux:

- Nix and this repo's dev shell.
- `udisks2`/`udisksctl` available on the system.
- A user-session automounter or permission to mount removable devices.
- A running user session with polkit/udisks permission to mount removable media.

On my NixOS machines, the `tools` repo should enable `services.udisks2` and the Home Manager `services.udiskie` user service for this.

## Normal manual flashing

The nice!nano v2 uses an nRF52 UF2 bootloader. In bootloader mode it appears as a USB flash drive. Flashing is copying a `.uf2` file to that drive.

1. Build firmware:

   ```sh
   just build
   ```

2. Plug in the target keyboard half with a data-capable USB cable.

3. Put the nice!nano into bootloader mode, usually by double-tapping reset quickly.

4. Wait for the UF2 drive to appear.

5. Copy the matching `.uf2` to the root of the UF2 drive:

   ```sh
   cp result/urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2 /run/media/$USER/<UF2_VOLUME>/
   sync
   ```

6. The bootloader should write the firmware, disconnect the drive, and reboot automatically.

7. Repeat for the other half with the matching file.

## Flashing with Just

The repo exposes zmk-nix's flash helper:

```sh
just flash left
just flash right
```

`just flash` without arguments tries to flash all known split parts.

The helper waits for an `nRF UF2` block device, tries to mount it with `udisksctl`, and copies the correct firmware. If it cannot detect or mount the device, use manual flashing.

The helper is for the normal split firmware only. Use manual copy for `settings_reset-nice_nano_v2-zmk.uf2`.

## Expected file-copy errors

It is normal for Windows, Linux, or macOS to show a copy/I/O error when copying a UF2 file. The bootloader often resets and disconnects before the OS receives final write confirmation.

Treat the flash as successful if the controller reboots and the firmware works.

Known harmless examples:

- Windows file transfer errors after copy.
- Linux I/O errors after the volume disappears.
- macOS Finder errors.
- macOS Sonoma `fcopyfile failed: Input/output error`.

## Split keyboard flashing rules

Urchin is a wireless split keyboard:

- Left is conventionally the central half.
- Right is the peripheral half.
- The central handles keymap processing and host USB/Bluetooth.
- The peripheral sends key events to the central.

Practical rules:

- Initial install: flash both halves.
- Keymap-only change: flashing the left/central half is often enough.
- Config, display, split, module, or ZMK version change: flash both halves.
- When unsure: flash both halves.

## Persistent settings and settings reset

Regular firmware flashing does not clear ZMK persistent settings. ZMK intentionally preserves:

- host Bluetooth bonds;
- selected Bluetooth profile;
- split central/peripheral pairing;
- output selection;
- ZMK Studio runtime edits;
- lighting/power-management settings when applicable.

Use `settings_reset-nice_nano_v2-zmk.uf2` when:

- halves will not pair;
- Bluetooth pairing is broken;
- a controller was replaced;
- central/peripheral roles changed;
- the host shows connected but no keys arrive;
- you want to clear ZMK Studio runtime state at firmware level.

Full reset procedure:

1. Put left into bootloader mode.
2. Flash `settings_reset-nice_nano_v2-zmk.uf2` to left.
3. Put right into bootloader mode.
4. Flash `settings_reset-nice_nano_v2-zmk.uf2` to right.
5. Flash normal left firmware to left.
6. Flash normal right firmware to right.
7. Power-cycle or reset both halves at roughly the same time.
8. On host devices, forget/remove the old keyboard Bluetooth entry.
9. Pair again.

Important: settings-reset firmware has Bluetooth disabled, so the keyboard will not appear in Bluetooth scans until normal firmware has been flashed again.

## Bluetooth profile notes

ZMK has five Bluetooth profiles by default. Pairing a new host does not overwrite an already-bonded profile. Use an empty profile or clear an existing profile with keymap Bluetooth behaviors if they are available.

If host pairing acts stale:

1. Forget/remove the keyboard on the host.
2. Clear keyboard bonds via keymap behavior or settings reset.
3. Pair again.

If a host says the keyboard is connected but no input arrives, stale bond keys are a common cause.

## Bootloader recovery caveats

Normal `.uf2` application flashing is low risk.

Higher-risk operations include:

- flashing bootloader or SoftDevice-level images;
- using snippets/options that erase the SoftDevice on nRF52 boards;
- recovering from a corrupted/missing bootloader.

If double-reset no longer exposes a UF2 drive, recovery may require SWD/J-Link or equivalent hardware to reflash the bootloader.
