#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ] || [[ "$1" != "left" && "$1" != "right" ]]; then
  echo "Usage: $0 left|right" >&2
  exit 2
fi

part="$1"
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
firmware="$repo_root/result/zmk_${part}.uf2"
mountpoint_path="${ZMK_FLASH_MOUNTPOINT:-/mnt/zmk-uf2}"
timeout_seconds="${ZMK_FLASH_TIMEOUT_SECONDS:-120}"
bootloader_vendor_id="239a"
bootloader_product_id="00b3"
bootloader_key="T"
if [ "$part" = "right" ]; then
  bootloader_key="Y"
fi

cd "$repo_root"
echo "Building $part firmware..."
nix build .#firmware

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

printf 'Ready. Hold both outer thumbs, then hold %s for the %s bootloader.\n' "$bootloader_key" "$part"
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
sudo mount "$device" "$mountpoint_path"
echo "Mounted $device at $mountpoint_path"
sudo cp "$firmware" "$mountpoint_path/"
sync
echo "Copied and synced $(basename "$firmware")."
sleep 3
echo "$part flash complete."
