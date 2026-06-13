#!/usr/bin/env python3
"""Render config/urchin.keymap to docs/keymap.html."""

from __future__ import annotations

import argparse
import html
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYMAP = ROOT / "config" / "urchin.keymap"
OUTPUT = ROOT / "docs" / "keymap.html"

DISPLAY = {
    "LCTRL": "Ctrl",
    "RCTRL": "Ctrl",
    "LGUI": "Cmd",
    "RGUI": "Cmd",
    "LALT": "Opt",
    "RALT": "Opt",
    "LSHIFT": "Shift",
    "RSHIFT": "Shift",
    "SPACE": "Space",
    "BACKSPACE": "Backspace",
    "RETURN": "Enter",
    "ESC": "Esc",
    "TAB": "Tab",
    "SEMICOLON": ";",
    "COMMA": ",",
    "DOT": ".",
    "SLASH": "/",
    "N1": "1",
    "N2": "2",
    "N3": "3",
    "N4": "4",
    "N5": "5",
    "N6": "6",
    "N7": "7",
    "N8": "8",
    "N9": "9",
    "N0": "0",
}

POSITION_NAMES = {
    10: "A", 11: "S", 12: "D", 13: "F",
    16: "J", 17: "K", 18: "L", 19: ";",
}


def token_display(tokens: list[str], index: int) -> tuple[str, int]:
    token = tokens[index]
    if token == "&kp":
        key = tokens[index + 1]
        return DISPLAY.get(key, key), index + 2
    if token == "&mo":
        return f"MO {tokens[index + 1]}", index + 2
    if token == "&bootloader":
        return "Bootload", index + 1
    if token == "&none":
        return "--", index + 1
    if token == "&trans":
        return "↧", index + 1
    if token in {"&tog", "&to", "&sl"}:
        return f"{token[1:].upper()} {tokens[index + 1]}", index + 2
    return token, index + 1


def parse_layers(text: str) -> list[tuple[int, list[str]]]:
    layers: list[tuple[int, list[str]]] = []
    pattern = re.compile(r"layer_(\d+)\s*\{.*?bindings\s*=\s*<(.*?)>;", re.S)
    for match in pattern.finditer(text):
        layer = int(match.group(1))
        tokens = match.group(2).split()
        keys: list[str] = []
        index = 0
        while index < len(tokens):
            label, index = token_display(tokens, index)
            keys.append(label)
        if len(keys) != 34:
            raise ValueError(f"layer_{layer} has {len(keys)} bindings, expected 34")
        layers.append((layer, keys))
    return layers


def parse_combos(text: str) -> list[tuple[str, str]]:
    combos: list[tuple[str, str]] = []
    pattern = re.compile(r"combo_[\w_]+\s*\{(.*?)\};", re.S)
    for match in pattern.finditer(text):
        block = match.group(1)
        positions_match = re.search(r"key-positions\s*=\s*<([^>]+)>;", block)
        binding_match = re.search(r"bindings\s*=\s*<([^>]+)>;", block)
        if not positions_match or not binding_match:
            continue
        positions = [int(pos) for pos in positions_match.group(1).split()]
        binding_tokens = binding_match.group(1).split()
        binding, _ = token_display(binding_tokens, 0)
        keys = " + ".join(POSITION_NAMES.get(pos, str(pos)) for pos in positions)
        combos.append((keys, binding))
    return combos


def cells(labels: list[str]) -> str:
    return "".join(f"<td>{html.escape(label)}</td>" for label in labels)


def render_layer(layer: int, keys: list[str]) -> str:
    return f"""
<section>
  <h2>Layer {layer}</h2>
  <div class="keyboard">
    <div class="side left-side">
      <table class="half left">
        <tr>{cells(keys[0:5])}</tr>
        <tr>{cells(keys[10:15])}</tr>
        <tr>{cells(keys[20:25])}</tr>
      </table>
      <table class="thumbs left-thumbs"><tr>{cells(keys[30:32])}</tr></table>
    </div>
    <div class="side right-side">
      <table class="half right">
        <tr>{cells(keys[5:10])}</tr>
        <tr>{cells(keys[15:20])}</tr>
        <tr>{cells(keys[25:30])}</tr>
      </table>
      <table class="thumbs right-thumbs"><tr>{cells(keys[32:34])}</tr></table>
    </div>
  </div>
</section>
"""


def render_html(layers: list[tuple[int, list[str]]], combos: list[tuple[str, str]]) -> str:
    combo_items = "\n".join(
        f"      <li><code>{html.escape(keys)}</code> → {html.escape(binding)}</li>" for keys, binding in combos
    )
    layer_html = "\n".join(render_layer(layer, keys) for layer, keys in layers)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Urchin Keymap</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
    section {{ margin-bottom: 2rem; }}
    .keyboard {{ display: flex; gap: 3rem; align-items: flex-start; }}
    .side {{ display: flex; flex-direction: column; }}
    .left-side {{ align-items: flex-end; }}
    .right-side {{ align-items: flex-start; }}
    .thumbs {{ margin-top: 1rem; }}
    table {{ border-collapse: collapse; }}
    td {{ border: 1px solid #666; min-width: 4.5rem; height: 2.5rem; text-align: center; padding: 0.25rem; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  </style>
</head>
<body>
  <h1>Urchin Keymap</h1>
  <p>Generated from <code>config/urchin.keymap</code>.</p>
  {layer_html}
  <section>
    <h2>Combos</h2>
    <ul>
{combo_items}
    </ul>
  </section>
</body>
</html>
"""


def render() -> None:
    text = KEYMAP.read_text()
    layers = parse_layers(text)
    combos = parse_combos(text)
    OUTPUT.write_text(render_html(layers, combos))
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


def watch(interval: float) -> None:
    last_mtime = 0.0
    print(f"watching {KEYMAP.relative_to(ROOT)}")
    while True:
        mtime = KEYMAP.stat().st_mtime
        if mtime != last_mtime:
            render()
            last_mtime = mtime
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="store_true", help="rerender whenever config/urchin.keymap changes")
    parser.add_argument("--interval", type=float, default=0.5, help="watch polling interval in seconds")
    args = parser.parse_args()

    if args.watch:
        watch(args.interval)
    else:
        render()


if __name__ == "__main__":
    main()
