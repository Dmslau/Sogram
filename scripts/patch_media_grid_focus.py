#!/usr/bin/env python3
"""Patch PeerInfoMediaGridPaneNode to fix media viewer auto-scroll-back bug.

Root cause:
- The auto-scroll to initialFocusMessageIndex after list load causes jumping back to previous media.
- sparseMessageList already loads media from initialMessageIndex position via server,
  so no extra scrollToItem is needed.
- Fix: remove the entire auto-scroll block, just clear initialMessageIndex.
"""
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
    target = root / "submodules/TelegramUI/Components/PeerInfo/PeerInfoVisualMediaPaneNode/Sources/PeerInfoMediaGridPaneNode.swift"
    if not target.is_file():
        print(f"[FAIL] PeerInfoMediaGridPaneNode.swift not found")
        return 1

    ok = True

    # Remove the auto-scroll to initialFocusMessageIndex block
    old = '''        if let initialMessageIndex = self.initialMessageIndex, self.dataSource.hasLoadedMessages {
            self.initialMessageIndex = nil
            for message in self.dataSource.loadedMessages where message.index <= initialMessageIndex {
                if let index = self.dataSource.index(of: message.id) {
                    self.scrollToItem(index: index)
                }
                break
            }
        }'''

    new = '''        // MARK: Sogram
        // Auto-scroll to initialFocusMessageIndex removed:
        // sparseMessageList already loads media from initialMessageIndex position via server,
        // so the list will be at the correct position without extra scrollToItem.
        // The extra scroll was causing the "jump back to previous media" bug.
        self.initialMessageIndex = nil'''

    ok = patch_file(target, old, new, "PeerInfoMediaGridPaneNode: remove auto-scroll to initial focus") and ok

    if ok:
        print("Media grid no-scroll fix applied")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())