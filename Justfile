set dotenv-load := false

# List available tasks.
default:
    @just --list

# Enter the Nix development shell.
shell:
    nix develop

# Build all firmware artifacts into ./result.
build:
    nix build .#all

# Build only the left/right Urchin firmware.
build-firmware:
    nix build .#firmware

# Build only the settings reset firmware.
build-settings-reset:
    nix build .#settings-reset

# Update the rendered keymap HTML.
render-keymap:
    python3 scripts/render_keymap.py

# Watch the keymap and update the rendered HTML whenever it changes.
watch-keymap:
    python3 scripts/render_keymap.py --watch

# Update the tracked ZMK keysym catalog from the locally built ZMK keys.h.
update-keysyms:
    python3 scripts/update_keysyms_catalog.py

# Update ZMK west dependency revisions and zephyrDepsHash.
update:
    nix run .#update

# Build and flash one split half with the local UF2 helper.
flash part="left":
    scripts/flash.sh "{{part}}"

# Remove local Nix build result symlinks.
clean:
    rm -f result result-*
