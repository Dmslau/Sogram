#!/usr/bin/env python3
"""Patch to hide pinned message bar permanently via hidePinnedMessages setting."""
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
    panel = root / "submodules/TelegramUI/Sources/ChatInterfaceTitlePanelNodes.swift"
    if not panel.is_file():
        print(f"[FAIL] ChatInterfaceTitlePanelNodes.swift not found")
        return 1

    # 1. Add import
    old_imports = '''import Foundation
import UIKit
import TelegramCore
import AccountContext
import ChatPresentationInterfaceState
import ChatControllerInteraction
import ComponentFlow
import ChatSideTopicsPanel
import LegacyChatHeaderPanelComponent'''

    new_imports = '''import Foundation
import UIKit
import TelegramCore
import AccountContext
import ChatPresentationInterfaceState
import ChatControllerInteraction
import ComponentFlow
import ChatSideTopicsPanel
import LegacyChatHeaderPanelComponent
import SGSimpleSettings'''

    ok1 = patch_file(panel, old_imports, new_imports, "ChatInterfaceTitlePanelNodes: add SGSimpleSettings import")

    # 2. Intercept pinned message panel visibility at call site
    old_call = '''                case .pinnedMessage:
                    if case .pinnedMessages = chatPresentationInterfaceState.subject {
                    } else {
                        if chatPinnedPanelIsVisible(pinnedMessageTopId: chatPresentationInterfaceState.pinnedMessage?.topMessageId, skeletonId: chatPresentationInterfaceState.pinnedMessageSkeletonId, closedPinnedMessageId: chatPresentationInterfaceState.interfaceState.messageActionsState.closedPinnedMessageId, pendingUnpinnedAllMessages: chatPresentationInterfaceState.pendingUnpinnedAllMessages) {
                            selectedContext = context
                            break loop
                        }
                    }'''

    new_call = '''                case .pinnedMessage:
                    if case .pinnedMessages = chatPresentationInterfaceState.subject {
                    } else {
                        // Sogram: hide pinned message bar permanently when setting enabled
                        if !SGSimpleSettings.shared.hidePinnedMessages && chatPinnedPanelIsVisible(pinnedMessageTopId: chatPresentationInterfaceState.pinnedMessage?.topMessageId, skeletonId: chatPresentationInterfaceState.pinnedMessageSkeletonId, closedPinnedMessageId: chatPresentationInterfaceState.interfaceState.messageActionsState.closedPinnedMessageId, pendingUnpinnedAllMessages: chatPresentationInterfaceState.pendingUnpinnedAllMessages) {
                            selectedContext = context
                            break loop
                        }
                    }'''

    ok2 = patch_file(panel, old_call, new_call, "ChatInterfaceTitlePanelNodes: hide pinned bar when setting enabled")

    if ok1 and ok2:
        print("Pinned message bar hiding patch applied")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())