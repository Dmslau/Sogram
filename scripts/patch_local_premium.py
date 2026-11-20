#!/usr/bin/env python3
"""Enable local-only Telegram Premium for UI debugging via SGSimpleSettings."""
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
    account_context = root / "submodules/TelegramUI/Sources/AccountContext.swift"
    if not account_context.is_file():
        print(f"[FAIL] AccountContext.swift not found")
        return 1

    ok = True

    # Expose a computed property so toggling the setting takes effect immediately.
    old_property = '''    public private(set) var isPremium: Bool'''
    new_property = '''    private var isPremiumValue: Bool
    public var isPremium: Bool {
        // Local-only debug override; never changes the server-side subscription.
        return self.isPremiumValue || SGSimpleSettings.shared.localPremiumEnabled
    }'''
    ok = patch_file(account_context, old_property, new_property, "AccountContext.isPremium: computed local override") and ok

    old_init = '''        self.isPremium = false'''
    new_init = '''        self.isPremiumValue = false'''
    ok = patch_file(account_context, old_init, new_init, "AccountContext.init: backing Premium value") and ok

    # Apply the override to premium user limits too.
    old_limits = '''            let isPremium = peer?.isPremium ?? false
            return self.engine.data.subscribe(TelegramEngine.EngineData.Item.Configuration.UserLimits(isPremium: isPremium))'''
    new_limits = '''            let isPremium = peer?.isPremium ?? false
            let effectivePremium = isPremium || SGSimpleSettings.shared.localPremiumEnabled
            return self.engine.data.subscribe(TelegramEngine.EngineData.Item.Configuration.UserLimits(isPremium: effectivePremium))'''
    ok = patch_file(account_context, old_limits, new_limits, "AccountContext: Premium user limits override") and ok

    old_assignment = '''            self.isPremium = isPremium'''
    new_assignment = '''            self.isPremiumValue = isPremium'''
    ok = patch_file(account_context, old_assignment, new_assignment, "AccountContext: store server Premium status") and ok

    # Also unlock local voice transcription trial behavior.
    old_transcription = '''            let isPremium = peer?.isPremium ?? false
            if isPremium {'''
    new_transcription = '''            let isPremium = peer?.isPremium ?? false
            if isPremium || SGSimpleSettings.shared.localPremiumEnabled {'''
    ok = patch_file(account_context, old_transcription, new_transcription, "AccountContext: transcription Premium override") and ok

    if ok:
        print("Local Premium debug override enabled")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())