#!/usr/bin/env python3
"""Integrity gate: verify installed PDK model files against sim/pdk-artifact.json.

Exit 0 only if (a) the .include/.lib closure re-derived from the installed
model_lib equals the pinned file list and (b) every sha256 matches. Any
mismatch, missing file or unlisted include exits 1 and prints why. Run it
before starting a simulator; sim/smoke-hbt/run.sh does.

    verify_pdk.py --pdk-root PDK_ROOT [--artifact sim/pdk-artifact.json]
                  [--toolchain sim/toolchain.json] [--ngspice PATH]
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.dirname(HERE)
_INCLUDE = re.compile(r"^\s*\.(?:include|inc|lib)\s+(.+?)\s*$", re.IGNORECASE)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _target(rest, directive_is_lib):
    rest = rest.strip()
    if rest[:1] in "\"'":
        return rest[1:rest.index(rest[0], 1)]
    toks = rest.split()
    # ".lib name" (one token) opens a section; ".lib file section" loads one.
    if directive_is_lib and len(toks) < 2:
        return None
    return toks[0]


def closure(top, install_root):
    """Relative (to install_root) paths of top and everything it loads."""
    seen, todo = {}, [os.path.normpath(top)]
    while todo:
        rel = todo.pop()
        if rel in seen:
            continue
        full = os.path.join(install_root, rel)
        seen[rel] = full
        if not os.path.isfile(full):
            continue
        with open(full, encoding="latin-1") as f:
            for line in f:
                m = _INCLUDE.match(line)
                if not m:
                    continue
                is_lib = line.lstrip()[:4].lower() == ".lib"
                tgt = _target(m.group(1), is_lib)
                if tgt is None:
                    continue
                nxt = os.path.normpath(os.path.join(os.path.dirname(rel), tgt))
                todo.append(nxt)
    return seen


def verify(pdk_root, artifact):
    errors = []
    install = os.path.join(pdk_root, artifact["install_subtree"])
    pinned = {os.path.normpath(k): v for k, v in artifact["files"].items()}
    marker = os.path.join(install, artifact["install_marker"]["file"])
    if os.path.isfile(marker):
        with open(marker) as f:
            got = f.read().strip()
        if got != artifact["install_marker"]["value"]:
            print(f"note: install marker {got!r} != {artifact['install_marker']['value']!r} (provenance only)")
    else:
        print("note: install marker missing (provenance unknown; hashes decide)")
    derived = closure(artifact["model_lib"], install)
    for rel in sorted(set(derived) - set(pinned)):
        errors.append(f"unlisted include in closure: {rel}")
    for rel in sorted(set(pinned) - set(derived)):
        errors.append(f"pinned file not in closure: {rel}")
    for rel, want in sorted(pinned.items()):
        full = os.path.join(install, rel)
        if not os.path.isfile(full):
            errors.append(f"missing model file: {rel}")
        elif sha256(full) != want:
            errors.append(f"sha256 mismatch: {rel}")
    return errors


def ngspice_note(ngspice, toolchain):
    want = toolchain["ngspice"]["major"]
    try:
        out = subprocess.run([ngspice, "--version"], capture_output=True, text=True, timeout=30)
        m = re.search(r"ngspice-(\d+)", out.stdout + out.stderr)
    except (OSError, subprocess.SubprocessError):
        m = None
    if not m:
        return f"note: could not determine ngspice version (pinned: {want})"
    if int(m.group(1)) != want:
        return f"WARNING: ngspice major {m.group(1)} != pinned {want}; results are not on the pinned toolchain"
    return f"ngspice-{want} (pinned)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pdk-root", required=True)
    ap.add_argument("--artifact", default=os.path.join(SIM, "pdk-artifact.json"))
    ap.add_argument("--toolchain", default=os.path.join(SIM, "toolchain.json"))
    ap.add_argument("--ngspice", help="also report this binary's version against toolchain.json")
    a = ap.parse_args(argv)
    with open(a.artifact) as f:
        artifact = json.load(f)
    errors = verify(a.pdk_root, artifact)
    if a.ngspice:
        with open(a.toolchain) as f:
            print(ngspice_note(a.ngspice, json.load(f)))
    if errors:
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        print("PDK integrity gate FAILED; refusing to run.", file=sys.stderr)
        return 1
    print(f"PDK integrity OK ({len(artifact['files'])} files, commit {artifact['upstream']['commit'][:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
