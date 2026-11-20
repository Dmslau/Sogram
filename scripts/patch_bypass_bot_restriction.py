#!/usr/bin/env python3
"""Bypass the iOS-only appleterms bot restriction (local debug only)."""
import argparse
import sys
from pathlib import Path


def patch_file(path: Path, old: str, new: str, label: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"[FAIL] {label}: pattern not found in {path}")
        return False
    count = text.count(old)
    if count != 1:
        print(f"[FAIL] {label}: expected 1 match, found {count} in {path}")
        return False
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"[OK] {label}: patched {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True, type=Path)
    args = parser.parse_args()

    root = args.upstream
    peer_utils = root / "submodules/TelegramCore/Sources/Utils/PeerUtils.swift"
    if not peer_utils.is_file():
        print(f"[FAIL] PeerUtils.swift not found")
        return 1

    ok = True

    # Skip appleterms platform rules when the debug switch is enabled.
    old = '''            for rule in restrictionInfo.rules {
                if rule.reason == "sensitive" {
                    continue
                }
'''
    new = '''            for rule in restrictionInfo.rules {
                if rule.reason == "sensitive" {
                    continue
                }
                // Local debug: bypass the iOS-only appleterms bot restriction.
                if SGSimpleSettings.shared.bypassBotRestriction, rule.reason == "appleterms" {
                    continue
                }
'''
    ok = patch_file(peer_utils, old, new, "PeerUtils: bypass appleterms restriction when enabled") and ok

    if ok:
        print("Bot restriction bypass patch applied")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())