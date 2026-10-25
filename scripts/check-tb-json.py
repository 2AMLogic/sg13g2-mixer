#!/usr/bin/env python3
"""Validate every sim/*/testbench/tb.json (or the files named on the command line).

Until the harness (and its manifest schema) lands, the structural contract is
the part that does not depend on it: the file is UTF-8 JSON, the top level is a
non-empty object, and no object repeats a key (a silent last-wins override).
The schema check replaces this when the harness ships its schema.

With no bench present the check passes trivially so the first tb.json is
validated the day it lands.

Exit status: 0 ok (or nothing to check), 1 invalid file, 2 usage error.
"""
import glob
import json
import os
import sys


def _no_dup_pairs(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise ValueError("duplicate key %r" % key)
        seen.add(key)
    return dict(pairs)


def validate(path):
    try:
        with open(path, "rb") as fh:
            doc = json.loads(fh.read().decode("utf-8"), object_pairs_hook=_no_dup_pairs)
    except (OSError, ValueError) as exc:  # UnicodeDecodeError is a ValueError
        return "%s: %s" % (path, exc)
    if not isinstance(doc, dict) or not doc:
        return "%s: top level must be a non-empty JSON object" % path
    return None


def main(argv):
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv:
        paths = argv
    else:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        paths = sorted(glob.glob(os.path.join(root, "sim", "*", "testbench", "tb.json")))
    if not paths:
        print("check-tb-json: no sim/*/testbench/tb.json yet; nothing to check.")
        return 0
    bad = [e for e in map(validate, paths) if e]
    for e in bad:
        print("INVALID: " + e, file=sys.stderr)
    if bad:
        return 1
    print("check-tb-json: %d tb.json file(s) valid." % len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
