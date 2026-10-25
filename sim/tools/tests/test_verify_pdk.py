"""Negative control: a tampered model file stops the run before ngspice starts."""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.dirname(os.path.dirname(HERE))
RUN = os.path.join(SIM, "smoke-hbt", "run.sh")
MODELS = os.path.join("ihp-sg13g2", "libs.tech", "ngspice", "models")
REAL_ROOT = os.environ.get("PDK_ROOT")


def make_stub(tmp):
    """Fake ngspice: records a batch run (-b); --version alone is not a run."""
    marker = os.path.join(tmp, "ngspice-was-run")
    path = os.path.join(tmp, "ngspice")
    with open(path, "w") as f:
        f.write(f"#!/bin/sh\ncase \"$*\" in *-b*) touch '{marker}';; esac\necho 'ngspice-46 stub'\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path, marker


@unittest.skipUnless(REAL_ROOT, "set PDK_ROOT to a v0.3.0 install")
class TamperedModel(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.root = os.path.join(self.tmp, "pdk")
        os.makedirs(os.path.join(self.root, MODELS))
        src = os.path.join(REAL_ROOT, MODELS)
        for n in os.listdir(src):
            shutil.copy(os.path.join(src, n), os.path.join(self.root, MODELS, n))
        self.ngspice, self.marker = make_stub(self.tmp)

    def run_smoke(self):
        env = dict(os.environ, PDK_ROOT=self.root, NGSPICE=self.ngspice)
        return subprocess.run(["bash", RUN], env=env, capture_output=True, text=True)

    def test_clean_copy_reaches_ngspice(self):
        self.run_smoke()
        self.assertTrue(os.path.exists(self.marker))

    def test_flipped_byte_is_rejected_before_ngspice(self):
        p = os.path.join(self.root, MODELS, "sg13g2_hbt_mod.lib")
        with open(p, "rb") as f:
            data = bytearray(f.read())
        data[2000] ^= 0x01
        with open(p, "wb") as f:
            f.write(data)
        r = self.run_smoke()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("sha256 mismatch", r.stderr)
        self.assertFalse(os.path.exists(self.marker))

    def test_missing_model_file(self):
        os.remove(os.path.join(self.root, MODELS, "sg13g2_hbt_stat.lib"))
        r = self.run_smoke()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing model file", r.stderr)
        self.assertFalse(os.path.exists(self.marker))

    def test_unlisted_include_in_closure(self):
        p = os.path.join(self.root, MODELS, "cornerHBT.lib")
        with open(p, "ab") as f:
            f.write(b"\n.include cornerRES.lib\n")
        r = self.run_smoke()
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(self.marker))

    def test_missing_marker_does_not_fail(self):
        # the copy carries no .fetched-version marker at all
        self.assertFalse(os.path.exists(os.path.join(self.root, "ihp-sg13g2", ".fetched-version")))
        self.run_smoke()
        self.assertTrue(os.path.exists(self.marker))


if __name__ == "__main__":
    unittest.main()
