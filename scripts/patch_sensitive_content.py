#!/usr/bin/env python3
"""Patch to disable sensitive content blur (show sensitive media directly)."""
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

    # 1. ChatHistoryListNode: override showSensitiveContent when Pro enabled
    chat_history = root / "submodules/TelegramUI/Sources/ChatHistoryListNode.swift"
    if not chat_history.is_file():
        print(f"[FAIL] ChatHistoryListNode.swift not found")
        return 1

    old_sensitive = '''let associatedData = extractAssociatedData(translateToLanguageSG: translateToLanguageSG, translationSettings: translationSettings, /* MARK: Swiftgram */ chatLocation: chatLocation, view: view, automaticDownloadNetworkType: networkType, preferredStoryHighQuality: preferredStoryHighQuality, animatedEmojiStickers: animatedEmojiStickers, additionalAnimatedEmojiStickers: additionalAnimatedEmojiStickers, premiumGiftStickers: premiumGiftStickers, tonGiftStickers: tonGiftStickers, subject: subject, currentlyPlayingMessageId: currentlyPlayingMessageIdAndType?.0, isCopyProtectionEnabled: isCopyProtectionEnabled, availableReactions: availableReactions, availableMessageEffects: availableMessageEffects, savedMessageTags: savedMessageTags, defaultReaction: defaultReaction.0, areStarReactionsEnabled: defaultReaction.1, isPremium: isPremium, alwaysDisplayTranscribeButton: alwaysDisplayTranscribeButton, accountPeer: accountPeer, topicAuthorId: topicAuthorId, hasBots: chatHasBots, translateToLanguage: translateToLanguage?.toLang, maxReadStoryId: maxReadStoryId, recommendedChannels: recommendedChannels, audioTranscriptionTrial: audioTranscriptionTrial, chatThemes: chatThemes, deviceContactsNumbers: deviceContactsNumbers, isInline: !rotated, showSensitiveContent: contentSettings.ignoreContentRestrictionReasons.contains("sensitive"), isSuspiciousPeer: isSuspiciousPeer, accountCountry: accountCountry)'''

    new_sensitive = '''let associatedData = extractAssociatedData(translateToLanguageSG: translateToLanguageSG, translationSettings: translationSettings, /* MARK: Swiftgram */ chatLocation: chatLocation, view: view, automaticDownloadNetworkType: networkType, preferredStoryHighQuality: preferredStoryHighQuality, animatedEmojiStickers: animatedEmojiStickers, additionalAnimatedEmojiStickers: additionalAnimatedEmojiStickers, premiumGiftStickers: premiumGiftStickers, tonGiftStickers: tonGiftStickers, subject: subject, currentlyPlayingMessageId: currentlyPlayingMessageIdAndType?.0, isCopyProtectionEnabled: isCopyProtectionEnabled, availableReactions: availableReactions, availableMessageEffects: availableMessageEffects, savedMessageTags: savedMessageTags, defaultReaction: defaultReaction.0, areStarReactionsEnabled: defaultReaction.1, isPremium: isPremium, alwaysDisplayTranscribeButton: alwaysDisplayTranscribeButton, accountPeer: accountPeer, topicAuthorId: topicAuthorId, hasBots: chatHasBots, translateToLanguage: translateToLanguage?.toLang, maxReadStoryId: maxReadStoryId, recommendedChannels: recommendedChannels, audioTranscriptionTrial: audioTranscriptionTrial, chatThemes: chatThemes, deviceContactsNumbers: deviceContactsNumbers, isInline: !rotated, showSensitiveContent: SGSimpleSettings.shared.ephemeralStatus > 1 || contentSettings.ignoreContentRestrictionReasons.contains("sensitive"), isSuspiciousPeer: isSuspiciousPeer, accountCountry: accountCountry)'''

    ok1 = patch_file(chat_history, old_sensitive, new_sensitive, "ChatHistoryListNode.showSensitiveContent (always show when Pro)")

    # 2. Patch the spoiler media (MediaSpoilerMessageAttribute) to not show overlay when Pro
    interactive_media = root / "submodules/TelegramUI/Components/Chat/ChatMessageInteractiveMediaNode/Sources/ChatMessageInteractiveMediaNode.swift"
    if not interactive_media.is_file():
        print(f"[FAIL] ChatMessageInteractiveMediaNode.swift not found")
        return 1

    # Patch the displaySpoiler logic for MediaSpoilerMessageAttribute
    old_spoiler = '''        } else if message.attributes.contains(where: { $0 is MediaSpoilerMessageAttribute }) {
            displaySpoiler = true
        } else if isSecretMedia'''

    new_spoiler = '''        } else if message.attributes.contains(where: { $0 is MediaSpoilerMessageAttribute }) {
            // Swiftgram Pro: don't blur spoiler media when Pro enabled
            if SGSimpleSettings.shared.ephemeralStatus <= 1 {
                displaySpoiler = true
            }
        } else if isSecretMedia'''

    ok2 = patch_file(interactive_media, old_spoiler, new_spoiler, "InteractiveMediaNode: disable spoiler blur when Pro")

    # 3. Patch secret media (self-destructing) blur
    old_secret = '''        } else if isSecretMedia {
            displaySpoiler = true
        } else if let context = self.context, message.isSensitiveContent'''

    new_secret = '''        } else if isSecretMedia {
            // Swiftgram Pro: don't blur secret media when Pro enabled
            if SGSimpleSettings.shared.ephemeralStatus <= 1 {
                displaySpoiler = true
            }
        } else if let context = self.context, message.isSensitiveContent'''

    ok3 = patch_file(interactive_media, old_secret, new_secret, "InteractiveMediaNode: disable secret media blur when Pro")

    if ok1 and ok2 and ok3:
        print("Sensitive content blur disabled for Pro users")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())