#!/usr/bin/env python3
"""Disable sponsored/ad messages globally via SGSimpleSettings.disableAds."""
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

    entries_path = root / "submodules/TelegramUI/Sources/ChatHistoryEntriesForView.swift"
    history_path = root / "submodules/TelegramUI/Sources/ChatHistoryListNode.swift"
    if not entries_path.is_file() or not history_path.is_file():
        print("[FAIL] ad-related source files not found")
        return 1

    ok = True

    old_imports = '''import Display
import TelegramStringFormatting'''
    new_imports = '''import Display
import TelegramStringFormatting
import SGSimpleSettings'''
    ok = patch_file(entries_path, old_imports, new_imports, "ChatHistoryEntriesForView: add SGSimpleSettings import") and ok

    # Do not insert opportunistic sponsored messages into the chat history.
    old_dynamic = '''        if !dynamicAdMessages.isEmpty {'''
    new_dynamic = '''        if !dynamicAdMessages.isEmpty && !SGSimpleSettings.shared.disableAds {'''
    ok = patch_file(entries_path, old_dynamic, new_dynamic, "ChatHistoryEntriesForView: suppress dynamic ads") and ok

    # Do not append the fixed sponsored message at the end of a channel history.
    old_fixed = '''if !entries.isEmpty, case let .MessageEntry(lastMessage, _, _, _, _, _) = entries[entries.count - 1], let message = adMessage {'''
    new_fixed = '''if !entries.isEmpty, case let .MessageEntry(lastMessage, _, _, _, _, _) = entries[entries.count - 1], let message = adMessage, !SGSimpleSettings.shared.disableAds {'''
    ok = patch_file(entries_path, old_fixed, new_fixed, "ChatHistoryEntriesForView: suppress fixed ad") and ok

    # Skip ad management/preloading entirely when globally disabled.
    old_manager = '''    private func beginAdMessageManagement(adMessages: Signal<(interPostInterval: Int32?, messages: [Message], startDelay: Int32?, betweenDelay: Int32?), NoError>) {
        self.adMessagesDisposable = (adMessages'''
    new_manager = '''    private func beginAdMessageManagement(adMessages: Signal<(interPostInterval: Int32?, messages: [Message], startDelay: Int32?, betweenDelay: Int32?), NoError>) {
        if SGSimpleSettings.shared.disableAds {
            self.allAdMessages = (nil, [], self.allAdMessages.version + 1)
            return
        }
        self.adMessagesDisposable = (adMessages'''
    ok = patch_file(history_path, old_manager, new_manager, "ChatHistoryListNode: skip ad management when disabled") and ok

    if ok:
        print("Global ad disable patch applied")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())