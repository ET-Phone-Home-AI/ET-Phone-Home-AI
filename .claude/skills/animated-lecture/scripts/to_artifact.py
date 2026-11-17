#!/usr/bin/env python3
"""Usage: python to_artifact.py deck.html fragment.html
Strips the <!DOCTYPE>/<html>/<head>/<body> wrapper so the page can be published with a tool
that adds its own wrapper (for example Claude Code's Artifact tool). The standalone deck.html
is the file to download and present; the fragment is only for publishing."""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
a, b = "<!--ARTIFACT-FRAGMENT-START-->", "<!--ARTIFACT-FRAGMENT-END-->"
if a not in src or b not in src:
    sys.exit("markers not found: keep the two ARTIFACT-FRAGMENT comments from the template")
open(sys.argv[2], "w", encoding="utf-8").write(src.split(a, 1)[1].split(b, 1)[0].strip() + "\n")
print("wrote", sys.argv[2])
