"""
scripts/generate_architecture_diagram.py
==========================================
Generates the architecture diagram PNG and SVG from docs/architecture.dot
using the Graphviz command-line tool.

Prerequisites:
  - Graphviz must be installed (https://graphviz.org/download/)
  - The 'dot' binary must be on the system PATH

Usage:
    python scripts/generate_architecture_diagram.py

Alternatively, run directly:
    dot -Tsvg docs/architecture.dot -o docs/architecture_diagram.svg
    dot -Tpng docs/architecture.dot -o docs/architecture_diagram.png
"""

import subprocess
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOT_FILE = os.path.join(ROOT, "docs", "architecture.dot")
SVG_FILE = os.path.join(ROOT, "docs", "architecture_diagram.svg")
PNG_FILE = os.path.join(ROOT, "docs", "architecture_diagram.png")


def run(cmd):
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr.strip()}")
        return False
    print(f"  [OK]")
    return True


if __name__ == "__main__":
    # Check Graphviz is available
    check = subprocess.run(["dot", "-V"], capture_output=True, text=True)
    if check.returncode != 0:
        print("[ERROR] Graphviz 'dot' command not found.")
        print("  Install from: https://graphviz.org/download/")
        print("  On Windows:   winget install Graphviz.Graphviz")
        print("  On macOS:     brew install graphviz")
        print("  On Linux:     sudo apt install graphviz")
        print()
        print("  NOTE: A hand-crafted SVG is already provided at:")
        print(f"  {SVG_FILE}")
        sys.exit(1)

    print("Generating architecture diagrams...")
    ok1 = run(["dot", "-Tsvg", DOT_FILE, "-o", SVG_FILE])
    ok2 = run(["dot", "-Tpng", DOT_FILE, "-o", PNG_FILE])

    if ok1 and ok2:
        print(f"\n[OK] SVG: {SVG_FILE}")
        print(f"[OK] PNG: {PNG_FILE}")
    else:
        print("\n[WARN] One or more outputs failed — check Graphviz installation.")
        sys.exit(1)
