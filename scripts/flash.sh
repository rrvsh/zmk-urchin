#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ] \
  || [[ "$1" != "urchin" && "$1" != "dolphin34" ]] \
  || [[ "$2" != "left" && "$2" != "right" ]]; then
  echo "Usage: $0 urchin|dolphin34 left|right" >&2
  exit 2
fi

keyboard="$1"
part="$2"
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
firmware="$repo_root/result/zmk_${part}.uf2"
mountpoint_path="${ZMK_FLASH_MOUNTPOINT:-/mnt/zmk-uf2}"
timeout_seconds="${ZMK_FLASH_TIMEOUT_SECONDS:-120}"
bootloader_vendor_id="${ZMK_BOOTLOADER_VENDOR_ID:-239a}"
bootloader_product_id="${ZMK_BOOTLOADER_PRODUCT_ID:-00b3}"
backup_dir="${ZMK_FLASH_BACKUP_DIR:-$HOME/Agents/artifacts/zmk-$keyboard/stock}"
stock_key="Q"
if [ "$part" = "right" ]; then
  stock_key="P"
fi

cd "$repo_root"
echo "Building $keyboard $part firmware..."
nix build ".#$keyboard-firmware"

if [ ! -f "$firmware" ]; then
  echo "Missing firmware: $firmware" >&2
  exit 1
fi

# Authenticate while the keyboard can still type.
sudo -v
sudo mkdir -p "$mountpoint_path"

cleanup() {
  status=$?
  trap - EXIT
  if mountpoint -q "$mountpoint_path"; then
    sudo umount "$mountpoint_path" || true
  fi
  sudo rmdir "$mountpoint_path" 2>/dev/null || true
  exit "$status"
}
trap cleanup EXIT

if mountpoint -q "$mountpoint_path"; then
  echo "Refusing to use mounted path: $mountpoint_path" >&2
  exit 1
fi

printf 'Ready. Double-tap reset on the %s %s half if accessible.\n' "$keyboard" "$part"
if [ "$part" = "left" ]; then
  printf 'Shared keymap: hold both outer thumbs, then hold T on the left.\n'
else
  printf 'Shared keymap: hold both outer thumbs, then press / on the right.\n'
fi
if [ "$keyboard" = "dolphin34" ]; then
  printf 'Factory Dolphin keymap only: both right thumbs plus %s.\n' "$stock_key"
fi
printf 'Waiting for one removable USB bootloader with ID %s:%s' "$bootloader_vendor_id" "$bootloader_product_id"
device=""

for ((attempt = 0; attempt < timeout_seconds; attempt++)); do
  devices=()
  while IFS= read -r candidate; do
    removable=$(lsblk -dnro RM "$candidate" 2>/dev/null || true)
    transport=$(lsblk -dnro TRAN "$candidate" 2>/dev/null || true)
    vendor_id=""
    product_id=""
    while IFS='=' read -r property value; do
      case "$property" in
        ID_VENDOR_ID) vendor_id="$value" ;;
        ID_MODEL_ID) product_id="$value" ;;
      esac
    done < <(udevadm info --query=property --name="$candidate" 2>/dev/null || true)

    if [ "$removable" = "1" ] && [ "$transport" = "usb" ] \
      && [ "$vendor_id" = "$bootloader_vendor_id" ] \
      && [ "$product_id" = "$bootloader_product_id" ]; then
      devices+=("$candidate")
    fi
  done < <(lsblk -Sdnpo PATH)

  if [ "${#devices[@]}" -gt 1 ]; then
    printf '\nRefusing: multiple matching USB bootloaders detected.\n' >&2
    exit 1
  fi
  if [ "${#devices[@]}" -eq 1 ]; then
    device="${devices[0]}"
    break
  fi

  printf '.'
  sleep 1
done
printf '\n'

if [ -z "$device" ]; then
  echo "Timed out after $timeout_seconds seconds." >&2
  exit 1
fi

echo "Detected $device"
sudo mount -o ro,uid="$(id -u)",gid="$(id -g)" "$device" "$mountpoint_path"
echo "Mounted $device read-only at $mountpoint_path"

# Keep the existing firmware before writing anything to this half. Never replace
# an earlier backup with a later firmware build.
backup="$backup_dir/${part}-stock.uf2"
if [ ! -f "$backup" ]; then
  if [ -f "$mountpoint_path/CURRENT.UF2" ]; then
    mkdir -p "$backup_dir"
    cp "$mountpoint_path/CURRENT.UF2" "$backup"
    if [ ! -s "$backup" ]; then
      rm -f "$backup"
      echo "Refusing to flash: empty firmware backup." >&2
      exit 1
    fi
    echo "Saved existing $keyboard $part firmware: $backup"
    sha256sum "$backup"
  elif [ "$part" = "right" ] && [ "${ZMK_FLASH_SKIP_RIGHT_BACKUP:-0}" = 1 ]; then
    echo "No CURRENT.UF2 available; skipping right backup as explicitly requested."
  else
    echo "Refusing to flash: no CURRENT.UF2 to back up from this bootloader." >&2
    exit 1
  fi
else
  echo "Preserving existing firmware backup: $backup"
fi

sudo mount -o remount,rw "$mountpoint_path"
sudo cp "$firmware" "$mountpoint_path/"
sync
echo "Copied and synced $(basename "$firmware")."
sleep 3
echo "$keyboard $part flash complete."
