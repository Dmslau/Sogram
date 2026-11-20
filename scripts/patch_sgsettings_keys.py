#!/usr/bin/env python3
"""Add hidePinnedMessages and hideSensitiveMediaBlur keys to SGSimpleSettings."""
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
    settings = root / "Swiftgram/SGSimpleSettings/Sources/SimpleSettings.swift"
    if not settings.is_file():
        print(f"[FAIL] SimpleSettings.swift not found")
        return 1

    ok = True

    # 1. Add Keys enum cases
    old_keys = '''        case videoControlsInFooter
        case combinedMediaViewer
        case hideAccountInNotifications
    }'''
    new_keys = '''        case videoControlsInFooter
        case combinedMediaViewer
        case hideAccountInNotifications
        case hidePinnedMessages
        case hideSensitiveMediaBlur
        case localPremiumEnabled
        case disableAds
    }'''
    ok = patch_file(settings, old_keys, new_keys, "Keys enum: add hidePinnedMessages & hideSensitiveMediaBlur") and ok

    # 2. Add defaultValues
    old_defaults = '''        Keys.combinedMediaViewer.rawValue: false,
    ]'''
    new_defaults = '''        Keys.combinedMediaViewer.rawValue: false,
        Keys.hidePinnedMessages.rawValue: false,
        Keys.hideSensitiveMediaBlur.rawValue: false,
        Keys.localPremiumEnabled.rawValue: false,
        Keys.disableAds.rawValue: false,
    ]'''
    ok = patch_file(settings, old_defaults, new_defaults, "defaultValues: add hidePinnedMessages & hideSensitiveMediaBlur") and ok

    # 3. Add property declarations (before the closing brace of class)
    old_props = '''    @UserDefault(key: Keys.hideAccountInNotifications.rawValue, userDefaults: UserDefaults(suiteName: APP_GROUP_IDENTIFIER) ?? .standard)
    public var hideAccountInNotifications: Bool
}'''
    new_props = '''    @UserDefault(key: Keys.hideAccountInNotifications.rawValue, userDefaults: UserDefaults(suiteName: APP_GROUP_IDENTIFIER) ?? .standard)
    public var hideAccountInNotifications: Bool

    @UserDefault(key: Keys.hidePinnedMessages.rawValue)
    public var hidePinnedMessages: Bool

    @UserDefault(key: Keys.hideSensitiveMediaBlur.rawValue)
    public var hideSensitiveMediaBlur: Bool

    @UserDefault(key: Keys.localPremiumEnabled.rawValue)
    public var localPremiumEnabled: Bool

    @UserDefault(key: Keys.disableAds.rawValue)
    public var disableAds: Bool
}'''
    ok = patch_file(settings, old_props, new_props, "Properties: add hidePinnedMessages & hideSensitiveMediaBlur") and ok

    if ok:
        print("SGSimpleSettings keys added successfully")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())