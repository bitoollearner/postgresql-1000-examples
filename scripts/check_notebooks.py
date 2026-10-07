#!/usr/bin/env python3
"""
Check the notebooks are valid and carry no solution SQL.

Run in CI. The notebooks are deliberately problems-only: a change that started
emitting solutions would otherwise publish the book's core asset, and nothing
downstream would notice.
"""
import json
import pathlib
import re
import sys

NB = pathlib.Path(__file__).resolve().parent.parent / "notebooks"

# An answer cell is the empty prompt. Anything else in a %%sql cell means a
# solution has been published.
PROMPT = re.compile(r"^%%sql\s*\n--\s*Example \d+\. Your answer here\.\s*$")


def main():
    books = sorted(NB.glob("*/*.ipynb"))   # one folder per chapter
    if not books:
        print("no notebooks found")
        return 1

    bad, cells, prompts = [], 0, 0
    for p in books:
        try:
            nb = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            bad.append(f"{p.name}: invalid JSON -- {e}")
            continue
        if nb.get("nbformat") != 4:
            bad.append(f"{p.name}: nbformat {nb.get('nbformat')}, expected 4")
        for c in nb.get("cells", []):
            cells += 1
            if c["cell_type"] != "code":
                continue
            src = "".join(c["source"]).strip()
            if not src.startswith("%%sql"):
                continue          # the connection cell
            prompts += 1
            if not PROMPT.match(src):
                bad.append(f"{p.name}: a %%sql cell is not an empty prompt:\n"
                           f"    {src[:120]}")

    print(f"{len(books)} notebooks, {cells} cells, {prompts} answer prompts")
    if bad:
        print("\nFAILED:")
        for b in bad[:20]:
            print(f"  {b}")
        return 1
    print("all notebooks valid, no solution SQL published")
    return 0


if __name__ == "__main__":
    sys.exit(main())
