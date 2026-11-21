#!/usr/bin/env python3
"""Patch media grid to respect Pro setting for sensitive content blur."""
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

    media_grid = root / "submodules/TelegramUI/Components/PeerInfo/PeerInfoVisualMediaPaneNode/Sources/PeerInfoMediaGridPaneNode.swift"
    if not media_grid.is_file():
        print(f"[FAIL] PeerInfoMediaGridPaneNode.swift not found")
        return 1

    # 1. Add import SGSimpleSettings
    old_imports = '''import Foundation
import UIKit
import AsyncDisplayKit
import Display
import SwiftSignalKit
import TelegramCore
import TelegramPresentationData
import AccountContext
import ContextUI
import ComponentFlow
import CheckNode
import ChatControllerInteraction
import DirectMediaImageCache
import SparseItemGrid
import TelegramNotices
import TelegramStringFormatting
import PeerInfoPaneNode
import MediaGrid'''

    new_imports = '''import Foundation
import UIKit
import AsyncDisplayKit
import Display
import SwiftSignalKit
import TelegramCore
import TelegramPresentationData
import AccountContext
import ContextUI
import ComponentFlow
import CheckNode
import ChatControllerInteraction
import DirectMediaImageCache
import SparseItemGrid
import TelegramNotices
import TelegramStringFormatting
import PeerInfoPaneNode
import MediaGrid
import SGSimpleSettings'''

    ok1 = patch_file(media_grid, old_imports, new_imports, "PeerInfoMediaGridPaneNode: add SGSimpleSettings import")

    # 2. Patch sensitive content check
    old = '''        var hasSpoiler = rawMessage.attributes.contains(where: { $0 is MediaSpoilerMessageAttribute }) && !self.revealedSpoilerMessageIds.contains(message.id)
        if rawMessage.isSensitiveContent(platform: "ios", contentSettings: self.context.currentContentSettings.with { $0 }) {
            hasSpoiler = true
        }'''

    new = '''        var hasSpoiler = rawMessage.attributes.contains(where: { $0 is MediaSpoilerMessageAttribute }) && !self.revealedSpoilerMessageIds.contains(message.id) && !SGSimpleSettings.shared.hideSensitiveMediaBlur
        if rawMessage.isSensitiveContent(platform: "ios", contentSettings: self.context.currentContentSettings.with { $0 }) {
            // Sogram: don't blur sensitive content when setting enabled
            if !SGSimpleSettings.shared.hideSensitiveMediaBlur {
                hasSpoiler = true
            }
        }'''

    ok2 = patch_file(media_grid, old, new, "PeerInfoMediaGridPaneNode: respect Pro for sensitive content")

    if ok1 and ok2:
        print("Media grid spoiler blur patched to respect Pro setting")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())