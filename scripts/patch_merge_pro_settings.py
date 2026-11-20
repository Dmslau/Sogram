#!/usr/bin/env python3
"""Merge the former Swiftgram Pro page into the regular Swiftgram settings page."""
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
    build = root / "Swiftgram/SGSettingsUI/BUILD"
    peer_rows = root / "Swiftgram/SGPeerInfoRows/Sources/SGPeerInfoRows.swift"
    if not controller.is_file() or not build.is_file() or not peer_rows.is_file():
        print("[FAIL] Pro merge source files not found")
        return 1

    ok = True

    old_imports = '''import SGAPIToken

import SGItemListUI'''
    new_imports = '''import SGAPIToken
import SGProUI
import SettingsUI

import SGItemListUI'''
    ok = patch_file(controller, old_imports, new_imports, "SGSettingsController: import Pro controllers") and ok

    old_section = '''    case accountColors
    case other
}'''
    new_section = '''    case accountColors
    case pro
    case other
}'''
    ok = patch_file(controller, old_section, new_section, "SGControllerSection: add Pro section") and ok

    old_bool = '''    case hideAccountInNotifications
}'''
    new_bool = '''    case hideAccountInNotifications
    case inputToolbar
}'''
    ok = patch_file(controller, old_bool, new_bool, "SGBoolSetting: add inputToolbar") and ok

    old_many = '''    case transcriptionBackend
}'''
    new_many = '''    case transcriptionBackend
    case pinnedMessageNotifications
    case mentionsAndRepliesNotifications
}'''
    ok = patch_file(controller, old_many, new_many, "SGOneFromManySetting: add notification policies") and ok

    old_links = '''private enum SGDisclosureLink: String {
    case contentSettings
    case languageSettings
}'''
    new_links = '''private enum SGDisclosureLink: String {
    case contentSettings
    case languageSettings
    case sessionBackupManager
    case messageFilter
    case appIcons
    case appBadges
}'''
    ok = patch_file(controller, old_links, new_links, "SGDisclosureLink: add Pro links") and ok

    old_search = '''    entries.append(.searchInput(id: id.count, section: .search, title: NSAttributedString(string: "🔍"), text: state.searchQuery ?? "", placeholder: strings.Common_Search))'''
    new_search = old_search + '''
    
    // Former Swiftgram Pro page, now available as regular settings.
    entries.append(.header(id: id.count, section: .pro, text: "SWIFTGRAM PRO", badge: nil))
    entries.append(.disclosure(id: id.count, section: .pro, link: .sessionBackupManager, text: "SessionBackup.Title".i18n(lang)))
    entries.append(.disclosure(id: id.count, section: .pro, link: .messageFilter, text: "MessageFilter.Title".i18n(lang)))
    entries.append(.toggle(id: id.count, section: .pro, settingName: .inputToolbar, value: SGSimpleSettings.shared.inputToolbar, text: "InputToolbar.Title".i18n(lang), enabled: true))
    entries.append(.oneFromManySelector(id: id.count, section: .pro, settingName: .pinnedMessageNotifications, text: "Notifications.PinnedMessages.Title".i18n(lang), value: "Notifications.PinnedMessages.value.\\(SGSimpleSettings.shared.pinnedMessageNotifications)".i18n(lang), enabled: true))
    entries.append(.oneFromManySelector(id: id.count, section: .pro, settingName: .mentionsAndRepliesNotifications, text: "Notifications.MentionsAndReplies.Title".i18n(lang), value: "Notifications.MentionsAndReplies.value.\\(SGSimpleSettings.shared.mentionsAndRepliesNotifications)".i18n(lang), enabled: true))
    entries.append(.disclosure(id: id.count, section: .pro, link: .appIcons, text: strings.Appearance_AppIcon))
    entries.append(.disclosure(id: id.count, section: .pro, link: .appBadges, text: "AppBadge.Title".i18n(lang)))
    entries.append(.notice(id: id.count, section: .pro, text: "AppBadge.Notice".i18n(lang)))'''
    ok = patch_file(controller, old_search, new_search, "SGControllerEntries: merge all Pro entries") and ok

    old_setbool = '''        case .hideAccountInNotifications:
            SGSimpleSettings.shared.hideAccountInNotifications = value'''
    new_setbool = '''        case .inputToolbar:
            SGSimpleSettings.shared.inputToolbar = value
        case .hideAccountInNotifications:
            SGSimpleSettings.shared.hideAccountInNotifications = value'''
    ok = patch_file(controller, old_setbool, new_setbool, "SGSettingsController: handle inputToolbar toggle") and ok

    old_many_end = '''        }
        
        presentOneFromManyImpl?(setting, options)
    }, openDisclosureLink:'''
    new_many_end = '''            case .pinnedMessageNotifications:
                let setAction: (String) -> Void = { value in
                    SGSimpleSettings.shared.pinnedMessageNotifications = value
                    SGSimpleSettings.shared.synchronizeShared()
                    simplePromise.set(true)
                }
                for value in SGSimpleSettings.PinnedMessageNotificationsSettings.allCases {
                    options.append(SGOneFromManyOption(title: "Notifications.PinnedMessages.value.\\(value.rawValue)".i18n(presentationData.strings.baseLanguageCode), isSelected: SGSimpleSettings.shared.pinnedMessageNotifications == value.rawValue, action: {
                        setAction(value.rawValue)
                    }))
                }
            case .mentionsAndRepliesNotifications:
                let setAction: (String) -> Void = { value in
                    SGSimpleSettings.shared.mentionsAndRepliesNotifications = value
                    SGSimpleSettings.shared.synchronizeShared()
                    simplePromise.set(true)
                }
                for value in SGSimpleSettings.MentionsAndRepliesNotificationsSettings.allCases {
                    options.append(SGOneFromManyOption(title: "Notifications.MentionsAndReplies.value.\\(value.rawValue)".i18n(presentationData.strings.baseLanguageCode), isSelected: SGSimpleSettings.shared.mentionsAndRepliesNotifications == value.rawValue, action: {
                        setAction(value.rawValue)
                    }))
                }
        }
        
        presentOneFromManyImpl?(setting, options)
    }, openDisclosureLink:'''
    ok = patch_file(controller, old_many_end, new_many_end, "SGSettingsController: handle notification policy selectors") and ok

    old_disclosure_end = '''        switch (link) {
            case .languageSettings:'''
    new_disclosure_end = '''        switch (link) {
            case .sessionBackupManager:
                pushControllerImpl?(sgSessionBackupManagerController(context: context))
            case .messageFilter:
                pushControllerImpl?(sgMessageFilterController(context: context))
            case .appIcons:
                pushControllerImpl?(themeSettingsController(context: context, focusOnItemTag: .icon))
            case .appBadges:
                pushControllerImpl?(sgAppBadgeSettingsController(context: context))
            case .languageSettings:'''
    ok = patch_file(controller, old_disclosure_end, new_disclosure_end, "SGSettingsController: open merged Pro controllers") and ok

    old_build_dep = '''        "//Swiftgram/SGAPIToken:SGAPIToken",'''
    new_build_dep = '''        "//Swiftgram/SGAPIToken:SGAPIToken",
        "//Swiftgram/SGProUI:SGProUI",
        "//submodules/SettingsUI:SettingsUI",'''
    ok = patch_file(build, old_build_dep, new_build_dep, "SGSettingsUI BUILD: add Pro dependencies") and ok

    old_pro_entry = '''    var items: [PeerInfoScreenItem] = []
    if paymentsEnabled || context.sharedContext.immediateSGStatus.status > 1 {
        items.append(PeerInfoScreenDisclosureItem(id: 0, label: swiftgramProLabel, text: "Swiftgram Pro", icon: PresentationResourcesSettings.swiftgramPro, action: {
            interaction.openSettings(.swiftgramPro)
        }))
    }
    items.append(PeerInfoScreenDisclosureItem'''
    new_pro_entry = '''    var items: [PeerInfoScreenItem] = []
    items.append(PeerInfoScreenDisclosureItem'''
    ok = patch_file(peer_rows, old_pro_entry, new_pro_entry, "SGPeerInfoRows: remove separate Pro entry") and ok

    # The Pro label is now unused; this module builds with -warnings-as-errors.
    old_pro_label = '''    let hasNewProFeatures = {
        return false
    }
    let swiftgramProLabel: PeerInfoScreenDisclosureItem.Label
    if hasNewProFeatures() {
        swiftgramProLabel = .titleBadge(presentationData.strings.Settings_New, presentationData.theme.list.itemAccentColor)
    } else {
        swiftgramProLabel = .none
    }

'''
    ok = patch_file(peer_rows, old_pro_label, "", "SGPeerInfoRows: remove unused Pro label") and ok

    if ok:
        print("Pro settings merged into regular Swiftgram settings")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())