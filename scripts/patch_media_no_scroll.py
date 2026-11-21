#!/usr/bin/env python3
"""彻底修复媒体查看器自动跳回上一个媒体的bug。

根本原因：
- PeerInfoVisualMediaPaneNode 和 PeerInfoMediaGridPaneNode 在列表加载后，
  会根据 initialFocusMessageIndex 执行额外的 scrollToItem 操作。
- 这个额外滚动是多余的：sparseMessageList 已经通过 initialMessageIndex 参数
  让服务器从目标索引附近返回数据，列表本身就会在正确位置附近显示。
- 额外的 scrollToItem 由于比较逻辑问题（<= 而非 ==，或 Index 结构体比较不匹配），
  经常滚到上一个媒体，造成“跳回上一个媒体”的bug。

修复方案：
- 移除整个自动滚动到 initialFocusMessageIndex 的逻辑。
- 保留 self.initialMessageIndex = nil，避免后续逻辑再次触发。
- sparseMessageList 已负责从正确位置开始加载，不需要额外滚动。
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
    ok = True

    # Patch 1: PeerInfoVisualMediaPaneNode.swift - 移除自动滚动逻辑
    target1 = root / "submodules/TelegramUI/Components/PeerInfo/PeerInfoVisualMediaPaneNode/Sources/PeerInfoVisualMediaPaneNode.swift"
    if not target1.is_file():
        print(f"[FAIL] PeerInfoVisualMediaPaneNode.swift not found")
        return 1

    old1 = '''            // MARK: Swiftgram
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

    new1 = '''            // MARK: Sogram
            // 自动滚动到 initialFocusMessageIndex 已移除：
            // sparseMessageList 已通过 initialMessageIndex 从目标位置附近加载数据，
            // 列表本身会在正确位置显示。额外的 scrollToItem 操作会导致跳回上一个媒体。
            self.initialMessageIndex = nil'''

    ok = patch_file(target1, old1, new1, "PeerInfoVisualMediaPaneNode: remove auto-scroll to initial focus") and ok

    # Patch 2: PeerInfoMediaGridPaneNode.swift - 移除自动滚动逻辑
    target2 = root / "submodules/TelegramUI/Components/PeerInfo/PeerInfoVisualMediaPaneNode/Sources/PeerInfoMediaGridPaneNode.swift"
    if not target2.is_file():
        print(f"[FAIL] PeerInfoMediaGridPaneNode.swift not found")
        return 1

    old2 = '''        // MARK: Sogram
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

    new2 = '''        // MARK: Sogram
        // 自动滚动到 initialFocusMessageIndex 已移除：
        // sparseMessageList 已通过 initialMessageIndex 从目标位置附近加载数据，
        // 列表本身会在正确位置显示。额外的 scrollToItem 操作会导致跳回上一个媒体。
        self.initialMessageIndex = nil'''

    ok = patch_file(target2, old2, new2, "PeerInfoMediaGridPaneNode: remove auto-scroll to initial focus") and ok

    if ok:
        print("Media viewer no-scroll fix applied (thorough version)")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())