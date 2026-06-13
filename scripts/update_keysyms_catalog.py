#!/usr/bin/env python3
"""Build a tracked ZMK keysym catalog from ZMK's keys.h."""

from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "zmk-keysyms.json"
KEYS_HEADER_GLOB = "/nix/store/*urchin-firmware-west-deps/zmk/app/include/dt-bindings/zmk/keys.h"

CATEGORY_ORDER = [
    "Letters",
    "Numbers",
    "Symbols",
    "Shifted symbols",
    "Modifiers",
    "Navigation/editing",
    "Whitespace/editing",
    "Function keys",
    "Keypad",
    "Consumer/media",
    "System/power",
    "International/language",
    "Other keyboard keys",
    "Other",
]


def keys_header_path(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if path.exists():
            return path
        raise FileNotFoundError(path)

    paths = [Path(path) for path in glob.glob(KEYS_HEADER_GLOB)]
    paths = [path for path in paths if path.exists()]
    if not paths:
        raise FileNotFoundError("Could not find ZMK keys.h. Build firmware first or pass --keys-h.")
    return max(paths, key=lambda path: path.stat().st_mtime)


def logical_define_lines(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    logical_lines: list[str] = []
    current = ""
    for line in lines:
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            current += stripped[:-1] + " "
            continue
        logical_lines.append(current + stripped)
        current = ""
    return logical_lines


def parse_defines(path: Path) -> tuple[dict[str, str], set[str]]:
    defines: dict[str, str] = {}
    deprecated: set[str] = set()
    for line in logical_define_lines(path):
        match = re.match(r"#define\s+([A-Z][A-Z0-9_]*)\s+(.+)$", line)
        if not match:
            continue
        name, value = match.groups()
        value = value.split("//", 1)[0].strip()
        if not value or "(" not in value:
            continue
        defines[name] = value
        if "DEPRECATED" in line:
            deprecated.add(name)
    return defines, deprecated


def resolve_define(name: str, defines: dict[str, str], seen: set[str] | None = None) -> str:
    seen = seen or set()
    value = defines[name]
    alias = re.fullmatch(r"\(?([A-Z][A-Z0-9_]*)\)?", value)
    if alias and alias.group(1) in defines and alias.group(1) not in seen:
        return resolve_define(alias.group(1), defines, seen | {name})
    return re.sub(r"\s+", " ", value)


def title_usage(text: str) -> str:
    return text.replace("KEYBOARD_", "").replace("CONSUMER_", "").replace("GD_", "").replace("_", " ").title()


def usage_name(value: str) -> str:
    usage = re.search(r"HID_USAGE_(?:KEY|CONSUMER|GD)_([A-Z0-9_]+)", value)
    return title_usage(usage.group(1)) if usage else value


def category(name: str, value: str) -> str:
    if re.fullmatch(r"[A-Z]", name):
        return "Letters"
    if re.fullmatch(r"N[0-9]", name) or name.startswith("NUMBER_"):
        return "Numbers"
    if "HID_USAGE_CONSUMER" in value:
        return "Consumer/media"
    if "HID_USAGE_GD_SYSTEM" in value:
        return "System/power"
    if any(marker in value for marker in ["LEFT_CONTROL", "LEFTCONTROL", "LEFT_SHIFT", "LEFTSHIFT", "LEFT_ALT", "LEFTALT", "LEFT_GUI", "LEFTGUI", "RIGHT_CONTROL", "RIGHTCONTROL", "RIGHT_SHIFT", "RIGHTSHIFT", "RIGHT_ALT", "RIGHTALT", "RIGHT_GUI", "RIGHTGUI"]):
        return "Modifiers"
    if value.startswith("LS("):
        return "Shifted symbols"
    if "_KEYPAD_" in value:
        return "Keypad"
    if re.search(r"_F\d+", value):
        return "Function keys"
    if any(marker in value for marker in ["LEFT_ARROW", "RIGHT_ARROW", "UP_ARROW", "DOWN_ARROW", "HOME", "END", "PAGE", "DELETE", "INSERT"]):
        return "Navigation/editing"
    if any(marker in value for marker in ["ENTER", "ESCAPE", "BACKSPACE", "TAB", "SPACEBAR"]):
        return "Whitespace/editing"
    if any(marker in value for marker in ["INTERNATIONAL", "LANG", "NON_US"]):
        return "International/language"
    if "HID_USAGE_KEY_KEYBOARD" in value:
        if any(marker in name for marker in ["MINUS", "EQUAL", "BRACKET", "BACKSLASH", "SEMICOLON", "QUOTE", "GRAVE", "COMMA", "DOT", "SLASH"]):
            return "Symbols"
        return "Other keyboard keys"
    return "Other"


def explanation(name: str, value: str) -> str:
    shifted = re.match(r"LS\(ZMK_HID_USAGE\(HID_USAGE_KEY, HID_USAGE_KEY_(.*?)\)\)", value)
    if shifted:
        return "Shift + " + title_usage(shifted.group(1))

    if "HID_USAGE_CONSUMER" in value:
        return "Consumer/media control: " + usage_name(value)
    if "HID_USAGE_GD_SYSTEM" in value:
        return "System control: " + usage_name(value)
    if "_KEYPAD_" in value:
        return "Keypad/numpad key: " + usage_name(value)
    if category(name, value) == "Modifiers":
        return "Modifier key: " + usage_name(value)
    if category(name, value) == "Navigation/editing":
        return "Navigation/editing key: " + usage_name(value)
    if category(name, value) == "Function keys":
        return "Function key: " + usage_name(value)
    if category(name, value) == "Letters":
        return f"Letter key {name}"
    if category(name, value) == "Numbers":
        return "Top-row number key: " + usage_name(value)
    return usage_name(value)


def sort_key(item: dict[str, object]) -> tuple[int, str]:
    category_index = CATEGORY_ORDER.index(str(item["category"])) if item["category"] in CATEGORY_ORDER else 999
    return category_index, str(item["keysym"])


def build_catalog(path: Path) -> dict[str, object]:
    defines, deprecated = parse_defines(path)
    groups: dict[str, list[str]] = {}
    for name in defines:
        groups.setdefault(resolve_define(name, defines), []).append(name)

    keysyms: list[dict[str, object]] = []
    for value, names in groups.items():
        preferred = [name for name in names if name not in deprecated]
        if not preferred:
            preferred = names
        canonical = min(preferred, key=lambda name: (len(name), name))
        aliases = sorted(name for name in names if name != canonical)
        keysyms.append(
            {
                "keysym": canonical,
                "category": category(canonical, value),
                "description": explanation(canonical, value),
                "aliases": aliases,
                "deprecated_aliases": sorted(name for name in aliases if name in deprecated),
                "all_names": sorted(names),
                "expression": value,
            }
        )

    return {
        "source": str(path),
        "note": "Deduped by resolved HID expression from ZMK keys.h. Descriptions are local human-readable summaries.",
        "category_order": CATEGORY_ORDER,
        "keysyms": sorted(keysyms, key=sort_key),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keys-h", help="Path to ZMK app/include/dt-bindings/zmk/keys.h")
    args = parser.parse_args()

    path = keys_header_path(args.keys_h)
    catalog = build_catalog(path)
    OUTPUT.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} from {path}")


if __name__ == "__main__":
    main()
