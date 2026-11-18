"""Tests for the Swiftgram unsigned-build configuration and re-sign compatibility."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resign = load("apply_resign_compat")


class ResignCompatTests(unittest.TestCase):
    def test_patches_delegate_and_entitlements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delegate = root / "submodules/TelegramUI/Sources/AppDelegate.swift"
            build = root / "Telegram/BUILD"
            delegate.parent.mkdir(parents=True)
            build.parent.mkdir(parents=True)
            delegate.write_text("prefix\n" + resign.APP_GROUP_GUARD + "suffix\n", encoding="utf-8")
            build.write_text(
                resign.APS_LINE + "\n<key>aps-environment</key>\n"
                + resign.APP_GROUPS_FRAGMENT
                + "name = \"ShareExtensionEntitlements\"\n",
                encoding="utf-8",
            )
            resign.patch_app_delegate(delegate)
            resign.patch_entitlements(build)
            delegate_text = delegate.read_text(encoding="utf-8")
            build_text = build.read_text(encoding="utf-8")
            self.assertIn("inkSandboxURL", delegate_text)
            self.assertNotIn("Error 2", delegate_text)
            self.assertIn("INK_RESIGN_NO_PUSH", build_text)
            self.assertNotIn("com.apple.security.application-groups", build_text)
            self.assertIn("application-identifier", build_text)


class ScaffoldTests(unittest.TestCase):
    def test_workflow_uses_secret_credentials_and_sogram_identity(self):
        workflow = (ROOT / ".github/workflows/build-swiftgram-unsigned.yml").read_text(encoding="utf-8")
        self.assertIn("secrets.APIID", workflow)
        self.assertIn("secrets.APIHASH", workflow)
        self.assertIn("com.dmslau.sogram", workflow)
        self.assertEqual(len(list((ROOT / ".github/workflows").glob("*.yml"))), 1)

    def test_swiftgram_config_does_not_read_upstream_api_values(self):
        script = (ROOT / "scripts/generate_build_config_swiftgram.py").read_text(encoding="utf-8")
        self.assertIn("APIID", script)
        self.assertIn("APIHASH", script)
        self.assertNotIn("variables.bzl", script)
        self.assertNotIn("example-configuration", script)


if __name__ == "__main__":
    unittest.main()
