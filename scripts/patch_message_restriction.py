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

def add_import_if_missing(path: Path, import_line: str, marker: str) -> bool:
    """在 marker 之后插入 import_line，如果还没插入过的话。"""
    text = path.read_text(encoding="utf-8")
    if import_line in text:
        print(f"[OK] {import_line} already present in {path}")
        return True
    old = f"{marker}\n"
    new = f"{marker}\n{import_line}\n"
    if old not in text:
        print(f"[FAIL] add_import: marker not found in {path}")
        return False
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"[OK] add_import: added {import_line} to {path}")
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

    # 1. 先添加 SGSimpleSettings 导入（如果还没有）
    ok = add_import_if_missing(
        app_context,
        "import SGSimpleSettings",
        "// MARK: Swiftgram"
    ) and ok

    # 2. 应用消息层限制绕过补丁
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