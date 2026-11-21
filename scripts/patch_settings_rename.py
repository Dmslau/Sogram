#!/usr/bin/env python3
"""Patch SGSettingsController and SGPeerInfoRows to rename Swiftgram to Sogram."""
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

    # Patch 1: SGSettingsController — 设置页面标题 "Swiftgram" → "Sogram"
    settings_controller = root / "Swiftgram/SGSettingsUI/Sources/SGSettingsController.swift"
    if not settings_controller.is_file():
        print(f"[FAIL] SGSettingsController.swift not found")
        return 1

    old_title = '''title: .text("Swiftgram"),'''
    new_title = '''title: .text("Sogram"),'''
    ok = patch_file(settings_controller, old_title, new_title, "SGSettingsController: title Swiftgram → Sogram") and ok

    # Patch 2: SGPeerInfoRows — 主设置菜单入口 "Swiftgram" → "Sogram"
    peer_info_rows = root / "Swiftgram/SGPeerInfoRows/Sources/SGPeerInfoRows.swift"
    if not peer_info_rows.is_file():
        print(f"[FAIL] SGPeerInfoRows.swift not found")
        return 1

    old_entry = '''    items.append(PeerInfoScreenDisclosureItem(id: 1, label: swiftgramLabel, text: "Swiftgram", icon: PresentationResourcesSettings.swiftgram, action: {
        interaction.openSettings(.swiftgram)
    }))'''
    new_entry = '''    items.append(PeerInfoScreenDisclosureItem(id: 1, label: swiftgramLabel, text: "Sogram", icon: PresentationResourcesSettings.swiftgram, action: {
        interaction.openSettings(.swiftgram)
    }))'''
    ok = patch_file(peer_info_rows, old_entry, new_entry, "SGPeerInfoRows: menu entry Swiftgram → Sogram") and ok

    # Patch 3: SGPeerInfoRows — 移除 Pro 入口（因为我们强制设了 Pro 状态，条件始终为真，会导致 Pro 项显示）
    old_pro_entry = '''    if paymentsEnabled || context.sharedContext.immediateSGStatus.status > 1 {
        items.append(PeerInfoScreenDisclosureItem(id: 0, label: .none, text: "Sogram Pro", icon: PresentationResourcesSettings.swiftgramPro, action: {
            interaction.openSettings(.swiftgramPro)
        }))
    }'''
    new_pro_entry = '''    // Sogram: Pro entry removed — all Pro features merged into main settings
    if false {}'''
    ok = patch_file(peer_info_rows, old_pro_entry, new_pro_entry, "SGPeerInfoRows: remove Pro entry") and ok

    if ok:
        print("Settings rename patch applied")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())