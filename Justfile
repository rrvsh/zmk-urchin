set dotenv-load := false

# List available tasks.
default:
    @just --list

# Enter the Nix development shell.
shell:
    nix develop

# Build every firmware artifact into ./result.
build:
    nix build .#all

# Build both split-keyboard firmware outputs.
build-firmware:
    nix build .#urchin-firmware .#dolphin34-firmware

# Build only the Urchin firmware.
build-urchin:
    nix build .#urchin-firmware

# Build only the Dolphin34 firmware.
build-dolphin34:
    nix build .#dolphin34-firmware

# Build only the settings reset firmware.
build-settings-reset:
    nix build .#settings-reset

# Update the rendered shared keymap HTML.
render-keymap:
    python3 scripts/render_keymap.py

# Watch the shared keymap and update the rendered HTML whenever it changes.
watch-keymap:
    python3 scripts/render_keymap.py --watch

# Update the tracked ZMK keysym catalog from the locally built ZMK keys.h.
update-keysyms:
    python3 scripts/update_keysyms_catalog.py

# Update ZMK west dependency revisions and zephyrDepsHash.
update:
    nix run .#update

# Build and flash an explicit keyboard half with the local UF2 helper.
flash keyboard part="left":
    scripts/flash.sh "{{keyboard}}" "{{part}}"

# Remove local Nix build result symlinks.
clean:
    rm -f result result-*
