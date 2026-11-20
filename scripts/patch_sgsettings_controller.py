#!/usr/bin/env python3
"""Add toggles for hidePinnedMessages and hideSensitiveMediaBlur in SGSettingsController."""
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
    controller = root / "Swiftgram/SGSettingsUI/Sources/SGSettingsController.swift"
    if not controller.is_file():
        print(f"[FAIL] SGSettingsController.swift not found")
        return 1

    ok = True

    # Register the two new toggle identifiers in SGBoolSetting (required by generic entries).
    old_bool_enum = '''    case inputToolbar
}'''
    new_bool_enum = '''    case inputToolbar
    case hidePinnedMessages
    case hideSensitiveMediaBlur
    case localPremiumEnabled
    case disableAds
}'''
    ok = patch_file(controller, old_bool_enum, new_bool_enum, "SGBoolSetting: register hidePinnedMessages & hideSensitiveMediaBlur") and ok

    # Find a good place to insert toggles - before hideAccountInNotifications in .other section
    old_section = '''    entries.append(.toggle(id: id.count, section: .other, settingName: .hideAccountInNotifications, value: SGSimpleSettings.shared.hideAccountInNotifications, text: i18n("Settings.HideAccountInNotifications", lang), enabled: true))
    
    return filterSGItemListUIEntrires(entries: entries, by: state.searchQuery)'''

    new_section = '''    entries.append(.toggle(id: id.count, section: .other, settingName: .hidePinnedMessages, value: SGSimpleSettings.shared.hidePinnedMessages, text: i18n("Settings.HidePinnedMessages", lang), enabled: true))
    entries.append(.toggle(id: id.count, section: .other, settingName: .hideSensitiveMediaBlur, value: SGSimpleSettings.shared.hideSensitiveMediaBlur, text: i18n("Settings.HideSensitiveMediaBlur", lang), enabled: true))
    entries.append(.toggle(id: id.count, section: .other, settingName: .localPremiumEnabled, value: SGSimpleSettings.shared.localPremiumEnabled, text: i18n("Settings.LocalPremiumEnabled", lang), enabled: true))
    entries.append(.toggle(id: id.count, section: .other, settingName: .disableAds, value: SGSimpleSettings.shared.disableAds, text: i18n("Settings.DisableAds", lang), enabled: true))
    entries.append(.toggle(id: id.count, section: .other, settingName: .hideAccountInNotifications, value: SGSimpleSettings.shared.hideAccountInNotifications, text: i18n("Settings.HideAccountInNotifications", lang), enabled: true))
    
    return filterSGItemListUIEntrires(entries: entries, by: state.searchQuery)'''

    ok = patch_file(controller, old_section, new_section, "SGSettingsController: add hidePinnedMessages & hideSensitiveMediaBlur toggles") and ok

    # Add toggle value handling (setBoolValue)
    old_setbool = '''        case .hideAccountInNotifications:
            SGSimpleSettings.shared.hideAccountInNotifications = value'''
    new_setbool = '''        case .hidePinnedMessages:
            SGSimpleSettings.shared.hidePinnedMessages = value
        case .hideSensitiveMediaBlur:
            SGSimpleSettings.shared.hideSensitiveMediaBlur = value
        case .localPremiumEnabled:
            SGSimpleSettings.shared.localPremiumEnabled = value
        case .disableAds:
            SGSimpleSettings.shared.disableAds = value
        case .hideAccountInNotifications:
            SGSimpleSettings.shared.hideAccountInNotifications = value'''
    ok = patch_file(controller, old_setbool, new_setbool, "SGSettingsController: add toggle setBoolValue handling") and ok

    # Add localized titles. Missing languages fall back to English via LocalizationManager.
    for locale, pinned, sensitive, premium, ads in (
        ("en", "Hide Pinned Message Bar", "Reveal Sensitive Media", "Unlock Telegram Premium Locally", "Disable Ads Globally"),
        ("zh-hans", "隐藏置顶消息栏", "敏感媒体去模糊", "本地解锁 Telegram 会员", "全局关闭广告"),
    ):
        strings_path = root / f"Swiftgram/SGStrings/Strings/{locale}.lproj/SGLocalizable.strings"
        if not strings_path.is_file():
            print(f"[FAIL] localization file not found: {strings_path}")
            return 1
        old_hide_phone = '"Settings.HidePhoneInSettingsUI"'
        new_entries = f'''"Settings.HidePinnedMessages" = "{pinned}";
"Settings.HideSensitiveMediaBlur" = "{sensitive}";
"Settings.LocalPremiumEnabled" = "{premium}";
"Settings.DisableAds" = "{ads}";
"Settings.HidePhoneInSettingsUI"'''
        ok = patch_file(strings_path, old_hide_phone, new_entries, f"{locale}: add toggle titles") and ok

    if ok:
        print("SGSettingsController toggles added successfully")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())