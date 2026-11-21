#!/usr/bin/env python3
"""Patch PeerInfoMediaGridPaneNode to fix media viewer auto-scroll-back bug.

Same root cause as PeerInfoVisualMediaPaneNode:
- Uses `<=` comparison instead of `==`, so when media list is sorted ascending,
  it scrolls to the previous media instead of the target.
- initialMessageIndex is set to nil immediately, so subsequent updates won't correct.
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

    # Patch 1: Add hasScrolledToInitialFocus flag declaration after initialMessageIndex
    old_decl = '''    private var initialMessageIndex: EngineMessage.Index?'''
    new_decl = '''    private var initialMessageIndex: EngineMessage.Index?
    // MARK: Sogram
    private var hasScrolledToInitialFocus: Bool = false'''
    ok = patch_file(target, old_decl, new_decl, "Add hasScrolledToInitialFocus flag") and ok

    # Patch 2: Replace the scroll-to-initial-focus logic with exact match + flag guard
    old_scroll = '''        if let initialMessageIndex = self.initialMessageIndex, self.dataSource.hasLoadedMessages {
            self.initialMessageIndex = nil
            for message in self.dataSource.loadedMessages where message.index <= initialMessageIndex {
                if let index = self.dataSource.index(of: message.id) {
                    self.scrollToItem(index: index)
                }
                break
            }
        }'''

    new_scroll = '''        // MARK: Sogram
        if !self.hasScrolledToInitialFocus, let initialMessageIndexValue = self.initialMessageIndex, self.dataSource.hasLoadedMessages {
            var scrolled = false
            // First pass: exact match to target index
            for message in self.dataSource.loadedMessages where message.index == initialMessageIndexValue {
                if let index = self.dataSource.index(of: message.id) {
                    self.scrollToItem(index: index)
                    scrolled = true
                }
                break
            }
            // Fallback: nearest previous item if exact match not found
            if !scrolled {
                for message in self.dataSource.loadedMessages where message.index <= initialMessageIndexValue {
                    if let index = self.dataSource.index(of: message.id) {
                        self.scrollToItem(index: index)
                        scrolled = true
                    }
                    break
                }
            }
            if scrolled {
                self.hasScrolledToInitialFocus = true
            }
            self.initialMessageIndex = nil
        }'''

    ok = patch_file(target, old_scroll, new_scroll, "Replace scroll-to-initial-focus with exact match") and ok

    if ok:
        print("Media grid focus fix applied")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())