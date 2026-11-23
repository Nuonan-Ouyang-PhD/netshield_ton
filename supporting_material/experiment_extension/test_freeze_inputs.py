import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("freeze_inputs.py")
SPEC = importlib.util.spec_from_file_location("freeze_extension_inputs", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FreezeInputTests(unittest.TestCase):
    def test_roundtrip_changed_input_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact, manifest = root / "private-model.bin", root / "frozen.json"
            artifact.write_bytes(b"SYNTHETIC_FIXTURE_MODEL_BYTES")
            inputs = MODULE.input_map([f"model={artifact}"])
            MODULE.freeze(inputs, manifest, "SYNTHETIC_FIXTURE")
            self.assertEqual(MODULE.verify(inputs, manifest)["files_verified"], 1)
            self.assertNotIn(str(root), manifest.read_text())
            self.assertNotIn("SYNTHETIC_FIXTURE_MODEL_BYTES", manifest.read_text())
            with self.assertRaises(ValueError):
                MODULE.freeze(inputs, manifest, "overwrite")
            artifact.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                MODULE.verify(inputs, manifest)

    def test_missing_extra_duplicate_and_symlink_inputs_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact, manifest = root / "a", root / "frozen.json"
            artifact.write_bytes(b"fixture")
            inputs = MODULE.input_map([f"runtime={artifact}"])
            MODULE.freeze(inputs, manifest, "fixture")
            with self.assertRaises(ValueError):
                MODULE.verify({"different": artifact}, manifest)
            with self.assertRaises(ValueError):
                MODULE.input_map([f"runtime={artifact}", f"runtime={artifact}"])
            linked = root / "link"
            linked.symlink_to(artifact)
            with self.assertRaises(ValueError):
                MODULE.input_map([f"runtime={linked}"])


if __name__ == "__main__":
    unittest.main()
