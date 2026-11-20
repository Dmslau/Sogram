#!/usr/bin/env python3
"""Patch ApplicationContext.swift to bypass bot restriction in message rendering."""
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
    app_context = root / "submodules/TelegramUI/Sources/ApplicationContext.swift"
    if not app_context.is_file():
        print(f"[FAIL] ApplicationContext.swift not found")
        return 1

    ok = True

    # Patch the message-level restriction check to respect bypassBotRestriction
    # Changed condition: if restrictionReason != nil { return }
    # New condition:     if restrictionReason != nil && !bypassBotRestriction { return }
    # This means: when bypassBotRestriction is enabled, don't hide the message even if there's a restriction
    old = '''                            if firstMessage.restrictionReason(platform: "ios", contentSettings: strongSelf.context.currentContentSettings.with { $0 }) != nil {
                                return
                            }'''
    new = '''                            // MARK: Swiftgram
                            if firstMessage.restrictionReason(platform: "ios", contentSettings: strongSelf.context.currentContentSettings.with { $0 }) != nil && !SGSimpleSettings.shared.bypassBotRestriction {
                                return
                            }'''
    ok = patch_file(app_context, old, new, "ApplicationContext: bypass bot restriction in message rendering") and ok

    if ok:
        print("Message restriction bypass patch applied")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())