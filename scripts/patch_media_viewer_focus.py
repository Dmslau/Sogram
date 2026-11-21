#!/usr/bin/env python3
"""Patch PeerInfoVisualMediaPaneNode to fix media viewer auto-scroll-back bug.

Root cause:
- ChatMessageBubbleItemNode zero-height layout hides filtered messages in chat list.
- Media viewer (PeerInfoVisualMediaPaneNode) loads media list independently from server DB,
  but its scroll-to-initial-focus logic uses `<=` comparison instead of `==`, so when media
  list is sorted ascending by index, it scrolls to the previous media instead of the target.
- initialMessageIndex is set to nil immediately after first scroll attempt, so subsequent
  list updates won't correct the position if the first attempt landed on wrong item.
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
    target = root / "submodules/TelegramUI/Components/PeerInfo/PeerInfoVisualMediaPaneNode/Sources/PeerInfoVisualMediaPaneNode.swift"
    if not target.is_file():
        print(f"[FAIL] PeerInfoVisualMediaPaneNode.swift not found")
        return 1

    ok = True

    # Patch 1: Add hasScrolledToInitialFocus flag declaration after initialMessageIndex
    old_decl = '''    private var initialMessageIndex: EngineMessage.Index?'''
    new_decl = '''    private var initialMessageIndex: EngineMessage.Index?
    // MARK: Swiftgram
    private var hasScrolledToInitialFocus: Bool = false'''
    ok = patch_file(target, old_decl, new_decl, "Add hasScrolledToInitialFocus flag") and ok

    # Patch 2: Replace the scroll-to-initial-focus logic with exact match + flag guard
    old_scroll = '''            if let initialMessageIndexValue = self.initialMessageIndex, items.items.contains(where: { item in
                if let _ = item as? VisualMediaItem {
                    return true
                } else {
                    return false
                }
            }) {
                self.initialMessageIndex = nil
                for item in items.items {
                    if let item = item as? VisualMediaItem {
                        if item.message.index <= initialMessageIndexValue {
                            self.itemGrid.scrollToItem(at: item.index, force: true)
                            break
                        }
                    }
                }
            }'''

    new_scroll = '''            // MARK: Swiftgram
            if !self.hasScrolledToInitialFocus, let initialMessageIndexValue = self.initialMessageIndex {
                var scrolled = false
                // First pass: exact match to target index
                for item in items.items {
                    if let item = item as? VisualMediaItem, item.message.index == initialMessageIndexValue {
                        self.itemGrid.scrollToItem(at: item.index, force: true)
                        scrolled = true
                        break
                    }
                }
                // Fallback: nearest previous item if exact match not found
                if !scrolled {
                    for item in items.items {
                        if let item = item as? VisualMediaItem {
                            if item.message.index <= initialMessageIndexValue {
                                self.itemGrid.scrollToItem(at: item.index, force: true)
                                scrolled = true
                                break
                            }
                        }
                    }
                }
                if scrolled {
                    self.hasScrolledToInitialFocus = true
                }
            }'''

    ok = patch_file(target, old_scroll, new_scroll, "Replace scroll-to-initial-focus with exact match") and ok

    # Patch 3: Set flag in didScrollImpl to stop auto-scroll when user manually scrolls
    old_did_scroll = '''        self.itemGridBinding.didScrollImpl = { [weak self] in
            guard let strongSelf = self else {
                return
            }
            strongSelf.paneDidScroll?()

            strongSelf.cancelPreviewGestures()
        }'''

    new_did_scroll = '''        // MARK: Swiftgram
        self.itemGridBinding.didScrollImpl = { [weak self] in
            guard let strongSelf = self else {
                return
            }
            strongSelf.paneDidScroll?()

            strongSelf.cancelPreviewGestures()

            // User manually scrolled, stop auto-scroll to initial focus
            strongSelf.hasScrolledToInitialFocus = true
        }'''

    ok = patch_file(target, old_did_scroll, new_did_scroll, "Set flag on manual scroll") and ok

    if ok:
        print("Media viewer focus fix applied (complete version)")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())