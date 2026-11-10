#!/usr/bin/env python3
"""Report WCAG 2 contrast ratios for every color pair the website uses.

Reads PALETTE and PAIRS from tools/build.py so the check cannot drift from
the stylesheet. Exits 1 if any pair is below its minimum.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep tools/ free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import PAIRS, PALETTE  # noqa: E402


def luminance(hex_color):
    channels = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(fg, bg):
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main():
    failed = 0
    for fg, bg, minimum, role in PAIRS:
        value = ratio(PALETTE[fg], PALETTE[bg])
        ok = value >= minimum
        failed += not ok
        print(f"{'pass' if ok else 'FAIL'} {value:5.2f}:1 (min {minimum}) {fg} {PALETTE[fg]} on {bg} {PALETTE[bg]} — {role}")
    if failed:
        print(f"{failed} pair(s) below minimum")
        return 1
    print("all pairs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
