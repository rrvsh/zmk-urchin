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

# Update ZMK west dependency revisions and zephyrDepsHash.
update:
    nix run .#update

# Flash split firmware. Pass optional part names, e.g. `just flash left`.
flash *parts:
    nix run .#flash -- {{parts}}

# Remove local Nix build result symlinks.
clean:
    rm -f result result-*
