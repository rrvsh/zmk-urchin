#!/usr/bin/env python3
"""Render config/urchin.keymap to docs/keymap.html."""

from __future__ import annotations

import argparse
import html
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYMAP = ROOT / "config" / "urchin.keymap"
OUTPUT = ROOT / "docs" / "keymap.html"
KEYSYMS_CATALOG = ROOT / "docs" / "zmk-keysyms.json"

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
    "GRAVE": "`",
    "MINUS": "-",
    "EQUAL": "=",
    "BSLH": "\\",
    "SQT": "'",
    "LBKT": "[",
    "RBKT": "]",
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

PHYSICAL_ROWS = [
    list(range(0, 5)),
    list(range(10, 15)),
    list(range(20, 25)),
    list(range(5, 10)),
    list(range(15, 20)),
    list(range(25, 30)),
    [30, 31],
    [32, 33],
]


def token_display(tokens: list[str], index: int) -> tuple[str, int]:
    token = tokens[index]
    if token == "&kp":
        key = tokens[index + 1]
        return DISPLAY.get(key, key), index + 2
    if token == "&mo":
        return f"hold L{tokens[index + 1]}", index + 2
    if token == "&lt":
        layer = tokens[index + 1]
        key = DISPLAY.get(tokens[index + 2], tokens[index + 2])
        return f"{key}\nhold L{layer}", index + 3
    if token == "&mt":
        mod = DISPLAY.get(tokens[index + 1], tokens[index + 1])
        key = DISPLAY.get(tokens[index + 2], tokens[index + 2])
        return f"{key}\nhold {mod}", index + 3
    if token == "&mt_none":
        mod = DISPLAY.get(tokens[index + 1], tokens[index + 1])
        return f"--\nhold {mod}", index + 3
    if token == "&mt_bootloader":
        mod = DISPLAY.get(tokens[index + 1], tokens[index + 1])
        return f"Bootload\nhold {mod}", index + 3
    if token == "&bootloader":
        return "Bootload", index + 1
    if token == "&none":
        return "--", index + 1
    if token == "&trans":
        return "↧", index + 1
    if token in {"&tog", "&to", "&sl"}:
        return f"{token[1:].upper()} {tokens[index + 1]}", index + 2
    return token, index + 1


def keymap_keysyms(text: str) -> set[str]:
    tokens = text.replace("<", " < ").replace(">", " > ").split()
    used: set[str] = set()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "&kp" and index + 1 < len(tokens):
            used.add(tokens[index + 1])
            index += 2
        elif token == "&lt" and index + 2 < len(tokens):
            used.add(tokens[index + 2])
            index += 3
        elif token == "&mt" and index + 2 < len(tokens):
            used.add(tokens[index + 1])
            used.add(tokens[index + 2])
            index += 3
        elif token in {"&mt_none", "&mt_bootloader"} and index + 2 < len(tokens):
            used.add(tokens[index + 1])
            index += 3
        else:
            index += 1
    return used


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


def parse_combos(text: str) -> list[dict[str, object]]:
    combos: list[dict[str, object]] = []
    pattern = re.compile(r"(combo_[\w_]+)\s*\{(.*?)\};", re.S)
    for match in pattern.finditer(text):
        name = match.group(1).removeprefix("combo_").replace("_", " ").title()
        block = match.group(2)
        positions_match = re.search(r"key-positions\s*=\s*<([^>]+)>;", block)
        binding_match = re.search(r"bindings\s*=\s*<([^>]+)>;", block)
        layers_match = re.search(r"layers\s*=\s*<([^>]+)>;", block)
        if not positions_match or not binding_match:
            continue
        positions = [int(pos) for pos in positions_match.group(1).split()]
        binding_tokens = binding_match.group(1).split()
        binding, _ = token_display(binding_tokens, 0)
        layers = "all layers"
        if layers_match:
            layers = ", ".join(f"Layer {layer}" for layer in layers_match.group(1).split())
        combos.append({"name": name, "positions": positions, "binding": binding, "layers": layers})
    return combos


def cell(label: str, index: int) -> str:
    lines = "".join(f'<span>{html.escape(line)}</span>' for line in label.split("\n"))
    return f'<td><span class="label">{lines}</span><sub>{index}</sub></td>'


def cells(keys: list[str], positions: list[int], layer: int) -> str:
    return "".join(cell(keys[position], layer * 34 + position) for position in positions)


def combo_cells(row: list[int], active: set[int]) -> str:
    return "".join(
        f'<td class="{"active" if position in active else ""}"><sub>{position}</sub></td>' for position in row
    )


def render_combo(combo: dict[str, object]) -> str:
    active = set(combo["positions"])
    return f"""
    <article class="combo">
      <h3>{html.escape(str(combo["name"]))} → {html.escape(str(combo["binding"]))}</h3>
      <p>Active on: {html.escape(str(combo["layers"]))}</p>
      <div class="keyboard combo-map">
        <div class="side left-side">
          <table>
            <tr>{combo_cells(PHYSICAL_ROWS[0], active)}</tr>
            <tr>{combo_cells(PHYSICAL_ROWS[1], active)}</tr>
            <tr>{combo_cells(PHYSICAL_ROWS[2], active)}</tr>
          </table>
          <table class="thumbs"><tr>{combo_cells(PHYSICAL_ROWS[6], active)}</tr></table>
        </div>
        <div class="side right-side">
          <table>
            <tr>{combo_cells(PHYSICAL_ROWS[3], active)}</tr>
            <tr>{combo_cells(PHYSICAL_ROWS[4], active)}</tr>
            <tr>{combo_cells(PHYSICAL_ROWS[5], active)}</tr>
          </table>
          <table class="thumbs"><tr>{combo_cells(PHYSICAL_ROWS[7], active)}</tr></table>
        </div>
      </div>
    </article>
"""


def render_layer(layer: int, keys: list[str]) -> str:
    return f"""
<section>
  <h2>Layer {layer}</h2>
  <div class="keyboard">
    <div class="side left-side">
      <table class="half left">
        <tr>{cells(keys, list(range(0, 5)), layer)}</tr>
        <tr>{cells(keys, list(range(10, 15)), layer)}</tr>
        <tr>{cells(keys, list(range(20, 25)), layer)}</tr>
      </table>
      <table class="thumbs left-thumbs"><tr>{cells(keys, [30, 31], layer)}</tr></table>
    </div>
    <div class="side right-side">
      <table class="half right">
        <tr>{cells(keys, list(range(5, 10)), layer)}</tr>
        <tr>{cells(keys, list(range(15, 20)), layer)}</tr>
        <tr>{cells(keys, list(range(25, 30)), layer)}</tr>
      </table>
      <table class="thumbs right-thumbs"><tr>{cells(keys, [32, 33], layer)}</tr></table>
    </div>
  </div>
</section>
"""


def load_keysyms() -> list[dict[str, object]]:
    if not KEYSYMS_CATALOG.exists():
        return []
    catalog = json.loads(KEYSYMS_CATALOG.read_text())
    return catalog["keysyms"]


def render_missing_keysyms(used: set[str], keysyms: list[dict[str, object]]) -> str:
    if not keysyms:
        return """
  <section>
    <h2>Missing ZMK keysyms</h2>
    <p>Could not find <code>docs/zmk-keysyms.json</code>. Run <code>python3 scripts/update_keysyms_catalog.py</code> to create it.</p>
  </section>
"""

    missing = [item for item in keysyms if not (set(item["all_names"]) & used)]

    def alias_cell(item: dict[str, object]) -> str:
        aliases = item["aliases"]
        if not aliases:
            return ""
        return ", ".join(f"<code>{html.escape(alias)}</code>" for alias in aliases)

    def missing_row(item: dict[str, object]) -> str:
        return "\n".join(
            [
                "      <tr>",
                f"        <td><code>{html.escape(str(item['keysym']))}</code></td>",
                f"        <td>{html.escape(str(item['description']))}</td>",
                f"        <td>{alias_cell(item)}</td>",
                "      </tr>",
            ]
        )

    grouped: dict[str, list[dict[str, object]]] = {}
    for item in missing:
        grouped.setdefault(str(item["category"]), []).append(item)

    rows = "\n".join(
        "\n".join(
            [
                f'      <tr class="category"><th colspan="3">{html.escape(category)} ({len(items)})</th></tr>',
                *[missing_row(item) for item in items],
            ]
        )
        for category, items in grouped.items()
    )
    return f"""
  <section>
    <h2>Missing ZMK keysyms</h2>
    <p>Loaded from tracked <code>docs/zmk-keysyms.json</code>. If any alias for a keysym is used in the keymap, that keysym is considered present.</p>
    <p>Used {len(keysyms) - len(missing)} of {len(keysyms)} deduped keysyms; missing {len(missing)}.</p>
    <table class="missing-keysyms">
      <thead>
        <tr>
          <th>Keysym</th>
          <th>Meaning</th>
          <th>Aliases</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </section>
"""


def render_html(
    layers: list[tuple[int, list[str]]],
    combos: list[dict[str, object]],
    missing_keysyms_html: str,
) -> str:
    combo_items = "\n".join(render_combo(combo) for combo in combos)
    layer_html = "\n".join(render_layer(layer, keys) for layer, keys in layers)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Urchin Keymap</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
    section {{ margin-bottom: 2rem; }}
    .keyboard {{ display: flex; gap: 4rem; align-items: flex-start; }}
    .side {{ display: flex; flex-direction: column; }}
    .left-side {{ align-items: flex-end; }}
    .right-side {{ align-items: flex-start; }}
    .thumbs {{ margin-top: 1rem; }}
    table {{ border-collapse: collapse; }}
    td {{ border: 1px solid #666; min-width: 5.5rem; height: 3.6rem; text-align: center; padding: 0.4rem 0.5rem 0.65rem; position: relative; }}
    td .label {{ display: flex; flex-direction: column; gap: 0.25rem; align-items: center; justify-content: center; min-height: 3rem; }}
    td .label span + span {{ color: #555; font-size: 0.82rem; }}
    td sub {{ position: absolute; right: 0.35rem; bottom: 0.2rem; color: #666; font-size: 0.68rem; }}
    .combo {{ margin: 1.5rem 0; }}
    .combo h3 {{ margin-bottom: 0.25rem; }}
    .combo p {{ margin-top: 0; }}
    .combo-map td {{ background: #f7f7f7; }}
    .combo-map td.active {{ background: #ffd166; border-color: #9a6700; }}
    .combo-map td.active sub {{ color: #222; font-weight: 700; }}
    .missing-keysyms {{ width: 100%; table-layout: fixed; }}
    .missing-keysyms th, .missing-keysyms td {{ height: auto; min-width: 0; text-align: left; vertical-align: top; padding: 0.4rem 0.6rem; overflow-wrap: anywhere; }}
    .missing-keysyms th {{ background: #eee; }}
    .missing-keysyms tr.category th {{ background: #d9e8ff; font-size: 1.05rem; padding-top: 0.7rem; padding-bottom: 0.7rem; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  </style>
</head>
<body>
  <h1>Urchin Keymap</h1>
  <p>Generated from <code>config/urchin.keymap</code>.</p>
  <section>
    <h2>Legend</h2>
    <ul>
      <li><code>hold Ln</code>: hold the key to activate layer <code>n</code>.</li>
      <li>Two-line keys are dual-use: the first line is tap behavior, the second line is hold behavior.</li>
      <li><code>--</code>: disabled key.</li>
      <li><code>↧</code>: transparent key that falls through to a lower layer.</li>
      <li><code>Bootload</code>: reset that half into UF2 bootloader mode.</li>
      <li>Small bottom-right numbers are global key indices: <code>layer * 34 + physical position</code>.</li>
    </ul>
  </section>
  {layer_html}
  <section>
    <h2>Combos</h2>
    <p>Combos are based on physical finger position. Highlighted boxes show the physical positions used by each combo.</p>
{combo_items}
  </section>
{missing_keysyms_html}
</body>
</html>
"""


def render() -> None:
    text = KEYMAP.read_text()
    layers = parse_layers(text)
    combos = parse_combos(text)
    used = keymap_keysyms(text)
    missing_keysyms_html = render_missing_keysyms(used, load_keysyms())
    OUTPUT.write_text(render_html(layers, combos, missing_keysyms_html))
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
