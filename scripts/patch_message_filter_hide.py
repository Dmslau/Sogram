#!/usr/bin/env python3
"""Patch message filter to HIDE messages instead of dimming them."""
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

    # 1. ChatMessageItemView.setupItem: remove alpha dimming, keep matchedFilterKeyword as flag
    chat_msg_view = root / "submodules/TelegramUI/Components/Chat/ChatMessageItemView/Sources/ChatMessageItemView.swift"
    if not chat_msg_view.is_file():
        print(f"[FAIL] ChatMessageItemView.swift not found")
        return 1

    old_setup = '''    open func setupItem(_ item: ChatMessageItem, synchronousLoad: Bool) {
        self.item = item
        
        if !self.wasFilteredKeywordTested && !SGSimpleSettings.shared.messageFilterKeywords.isEmpty && SGSimpleSettings.shared.ephemeralStatus > 1 {
            let incomingMessage = item.message.effectivelyIncoming(item.context.account.peerId)
            if incomingMessage {
                if let matchedKeyword = SGSimpleSettings.shared.messageFilterKeywords.first(where: { item.message.text.contains($0) }) {
                     self.matchedFilterKeyword = matchedKeyword
                     self.alpha = item.presentationData.theme.theme.overallDarkAppearance ? 0.2 : 0.3
                }
            }
        }
        self.wasFilteredKeywordTested = true
    }'''

    new_setup = '''    open func setupItem(_ item: ChatMessageItem, synchronousLoad: Bool) {
        self.item = item
        
        if !self.wasFilteredKeywordTested && !SGSimpleSettings.shared.messageFilterKeywords.isEmpty && SGSimpleSettings.shared.ephemeralStatus > 1 {
            let incomingMessage = item.message.effectivelyIncoming(item.context.account.peerId)
            if incomingMessage {
                if let matchedKeyword = SGSimpleSettings.shared.messageFilterKeywords.first(where: { item.message.text.contains($0) }) {
                     self.matchedFilterKeyword = matchedKeyword
                     // Message will be hidden via zero-height layout in ChatMessageBubbleItemNode
                }
            }
        }
        self.wasFilteredKeywordTested = true
    }'''

    ok1 = patch_file(chat_msg_view, old_setup, new_setup, "ChatMessageItemView.setupItem (remove alpha dimming)")

    # 2. ChatMessageBubbleItemNode.beginLayout: add zero-height layout for filtered messages
    chat_bubble_node = root / "submodules/TelegramUI/Components/Chat/ChatMessageBubbleItemNode/Sources/ChatMessageBubbleItemNode.swift"
    if not chat_bubble_node.is_file():
        print(f"[FAIL] ChatMessageBubbleItemNode.swift not found")
        return 1

    # Patch inside beginLayout static function - add check at the very start of function body
    old_body_start = '''        let isPreview = item.presentationData.isPreview
        let accessibilityData = ChatMessageAccessibilityData(item: item, isSelected: isSelected)'''

    new_body_start = '''        // Swiftgram Pro: hide filtered messages completely (zero height)
        if let node = selfReference.value, node.matchedFilterKeyword != nil {
            return (ListViewItemNodeLayout(contentSize: CGSize(width: params.width, height: 0), insets: UIEdgeInsets()), { _, _, _ in })
        }
        let isPreview = item.presentationData.isPreview
        let accessibilityData = ChatMessageAccessibilityData(item: item, isSelected: isSelected)'''

    ok2 = patch_file(chat_bubble_node, old_body_start, new_body_start, "ChatMessageBubbleItemNode.beginLayout (early return for filtered)")

    if ok1 and ok2:
        print("Message filter changed from dimming to hiding completely")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())