#!/usr/bin/env python3
"""Patch PeerInfoVisualMediaPaneNode to scroll to exact initialFocusMessageIndex first."""
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

    # 修复：优先精确匹配 initialMessageIndex，避免滚动到上一个媒体
    old = '''            if let initialMessageIndexValue = self.initialMessageIndex, items.items.contains(where: { item in
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

    new = '''            // Swiftgram: scroll to exact initialFocusMessageIndex first to avoid
            // landing on previous media when current message is filtered/hidden.
            if let initialMessageIndexValue = self.initialMessageIndex {
                self.initialMessageIndex = nil
                var scrolled = false
                for item in items.items {
                    if let item = item as? VisualMediaItem, item.message.index == initialMessageIndexValue {
                        self.itemGrid.scrollToItem(at: item.index, force: true)
                        scrolled = true
                        break
                    }
                }
                if !scrolled {
                    for item in items.items {
                        if let item = item as? VisualMediaItem {
                            if item.message.index <= initialMessageIndexValue {
                                self.itemGrid.scrollToItem(at: item.index, force: true)
                                break
                            }
                        }
                    }
                }
            }'''

    ok = patch_file(target, old, new, "PeerInfoVisualMediaPaneNode: exact initial focus match") and ok

    if ok:
        print("Media viewer focus fix applied")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())