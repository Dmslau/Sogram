#!/usr/bin/env python3
"""Patch ChatMessageBubbleItemNode to bypass bot restriction in message bubble rendering."""
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
    target = root / "submodules/TelegramUI/Components/Chat/ChatMessageBubbleItemNode/Sources/ChatMessageBubbleItemNode.swift"
    if not target.is_file():
        print(f"[FAIL] ChatMessageBubbleItemNode.swift not found")
        return 1

    ok = True

    # Patch 1: Line 153 - skip restricted bubble rendering when bypassBotRestriction is enabled
    old1 = '''            if let attribute = attribute as? RestrictedContentMessageAttribute, attribute.platformText(platform: "ios", contentSettings: item.context.currentContentSettings.with { $0 }, chatId: message.author?.id.id._internalGetInt64Value()) != nil { // MARK: Swiftgram
                result.append((message, ChatMessageRestrictedBubbleContentNode.self, itemAttributes, BubbleItemAttributes(isAttachment: false, neighborType: .text, neighborSpacing: .default)))
                needReactions = false
                break outer'''
    new1 = '''            // MARK: Swiftgram
            if let attribute = attribute as? RestrictedContentMessageAttribute, attribute.platformText(platform: "ios", contentSettings: item.context.currentContentSettings.with { $0 }, chatId: message.author?.id.id._internalGetInt64Value()) != nil, !SGSimpleSettings.shared.bypassBotRestriction {
                result.append((message, ChatMessageRestrictedBubbleContentNode.self, itemAttributes, BubbleItemAttributes(isAttachment: false, neighborType: .text, neighborSpacing: .default)))
                needReactions = false
                break outer'''
    ok = patch_file(target, old1, new1, "ChatMessageBubbleItemNode: skip restricted bubble when bypass enabled") and ok

    # Patch 2: Line 2232 - skip disabling share/summarize buttons when bypassBotRestriction is enabled
    old2 = '''            if let attribute = attribute as? RestrictedContentMessageAttribute, attribute.platformText(platform: "ios", contentSettings: item.context.currentContentSettings.with { $0 }, chatId: item.content.firstMessage.author?.id.id._internalGetInt64Value()) != nil { // MARK: Swiftgram
                needsShareButton = false
                needsSummarizeButton = false'''
    new2 = '''            // MARK: Swiftgram
            if let attribute = attribute as? RestrictedContentMessageAttribute, attribute.platformText(platform: "ios", contentSettings: item.context.currentContentSettings.with { $0 }, chatId: item.content.firstMessage.author?.id.id._internalGetInt64Value()) != nil, !SGSimpleSettings.shared.bypassBotRestriction { // MARK: Swiftgram
                needsShareButton = false
                needsSummarizeButton = false'''
    ok = patch_file(target, old2, new2, "ChatMessageBubbleItemNode: keep share buttons when bypass enabled") and ok

    if ok:
        print("Message bubble restriction bypass patch applied")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())