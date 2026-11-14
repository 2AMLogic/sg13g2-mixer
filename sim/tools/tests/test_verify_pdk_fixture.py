"""PDK-independent negative control for verify_pdk: a synthetic install tree.

TamperedModel (test_verify_pdk.py) is the integration layer and needs a real
PDK_ROOT install, so all five of its tests skip in CI. These tests build a
three-file fixture tree with hand-written .include lines, hash it into a
throwaway artifact JSON, and drive verify_pdk.verify() and the CLI --artifact
path directly, so the gate's negative control executes — and can fail — on any
machine, including CI with no PDK_ROOT set.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import verify_pdk

TOP = "models/top.lib"
LEAF_A = "models/leaf_a.lib"
LEAF_B = "models/leaf_b.lib"
SUBTREE = "fpdk"


def make_fixture(tmp):
    """Fixture install tree (top.lib includes two leaves) + artifact JSON.

    The artifact hashes are computed at test time from the files just written.
    Returns (pdk_root, artifact_path); pdk_root is the parent of the
    install_subtree ("fpdk"), as verify() joins the two.
    """
    root = os.path.join(tmp, SUBTREE)
    os.makedirs(os.path.join(root, "models"))
    files = {
        TOP: "* fixture top\n.include leaf_a.lib\n.include leaf_b.lib\n",
        LEAF_A: "* fixture leaf A\n.model npna npn (bf=100)\n",
        LEAF_B: "* fixture leaf B\n.model npnb npn (bf=120)\n",
    }
    paths = {}
    for rel, text in files.items():
        full = os.path.join(root, rel)
        with open(full, "w") as f:
            f.write(text)
        paths[rel] = full
    artifact = {
        "_comment": "fixture artifact; hashes derived at test time",
        "upstream": {"repo": "fixture", "tag": "v0.0.0", "commit": "f" * 40},
        "install_subtree": "fpdk",
        "install_marker": {"file": ".fetched-version", "value": "0.0.0"},
        "model_lib": TOP,
        "files": {rel: verify_pdk.sha256(p) for rel, p in paths.items()},
    }
    apath = os.path.join(tmp, "artifact.json")
    with open(apath, "w") as f:
        json.dump(artifact, f)
    return tmp, apath


class FixtureGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.root, self.artifact = make_fixture(self.tmp)
        self.install = os.path.join(self.root, SUBTREE)

    def cli(self):
        return subprocess.run(
            [sys.executable, os.path.join(TOOLS, "verify_pdk.py"),
             "--pdk-root", self.root, "--artifact", self.artifact],
            capture_output=True, text=True)

    def load_artifact(self):
        with open(self.artifact) as f:
            return json.load(f)

    def test_clean_tree_passes(self):
        self.assertEqual(verify_pdk.verify(self.root, self.load_artifact()), [])

    def test_cli_clean_run_exits_zero(self):
        r = self.cli()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PDK integrity OK", r.stdout)

    def test_flipped_byte_is_rejected(self):
        p = os.path.join(self.install, LEAF_A)
        with open(p, "rb") as f:
            data = bytearray(f.read())
        data[4] ^= 0x01
        with open(p, "wb") as f:
            f.write(data)
        self.assertEqual(verify_pdk.verify(self.root, self.load_artifact()),
                         [f"sha256 mismatch: {LEAF_A}"])

    def test_cli_flipped_byte_exits_one(self):
        with open(os.path.join(self.install, LEAF_A), "a") as f:
            f.write("* tampered\n")
        r = self.cli()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(f"FAIL: sha256 mismatch: {LEAF_A}", r.stderr)
        self.assertIn("PDK integrity gate FAILED", r.stderr)

    def test_missing_leaf_is_rejected(self):
        os.remove(os.path.join(self.install, LEAF_B))
        self.assertEqual(verify_pdk.verify(self.root, self.load_artifact()),
                         [f"missing model file: {LEAF_B}"])

    def test_unlisted_include_is_rejected(self):
        p = os.path.join(self.install, TOP)
        with open(p, "a") as f:
            f.write(".include leaf_c.lib\n")
        with open(os.path.join(self.install, "models", "leaf_c.lib"), "w") as f:
            f.write("* on disk but never pinned\n")
        artifact = self.load_artifact()
        artifact["files"][TOP] = verify_pdk.sha256(p)
        self.assertEqual(verify_pdk.verify(self.root, artifact),
                         ["unlisted include in closure: models/leaf_c.lib"])

    def test_pinned_but_unreferenced_file_is_rejected(self):
        p = os.path.join(self.install, "models", "leaf_d.lib")
        with open(p, "w") as f:
            f.write("* pinned but never included\n")
        artifact = self.load_artifact()
        artifact["files"]["models/leaf_d.lib"] = verify_pdk.sha256(p)
        self.assertEqual(verify_pdk.verify(self.root, artifact),
                         ["pinned file not in closure: models/leaf_d.lib"])


if __name__ == "__main__":
    unittest.main()
