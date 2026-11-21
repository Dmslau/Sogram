#!/usr/bin/env python3
"""Generate the Sogram build configuration from Actions secrets."""
import argparse
import json
import os
import re
from pathlib import Path

VALID_BUNDLE_ID = re.compile(r"^[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)+$")


def fail(message: str) -> None:
    raise SystemExit(f"build-config error: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--notice", required=True, type=Path)
    args = parser.parse_args()

    api_id = os.environ.get("APIID", "").strip()
    api_hash = os.environ.get("APIHASH", "").strip()
    bundle_id = os.environ.get("APP_BUNDLE_ID", "com.dmslau.sogram").strip()
    if not api_id or not api_hash:
        fail("APIID and APIHASH must come from the shell environment")
    if not api_id.isdecimal() or api_id == "0":
        fail("APIID must be a positive decimal integer")
    if len(api_hash) != 32 or any(ch not in "0123456789abcdefABCDEF" for ch in api_hash):
        fail("APIHASH must be a 32-character hexadecimal string")
    if not VALID_BUNDLE_ID.fullmatch(bundle_id):
        fail("APP_BUNDLE_ID must be a reverse-DNS identifier")
    if bundle_id in {"ph.telegra.Telegraph", "org.telegram.Telegram", "org.telegram.TelegramEnterprise"}:
        fail("APP_BUNDLE_ID must not be an official Telegram bundle identifier")
    if not args.template.is_file():
        fail(f"upstream template not found: {args.template}")

    config = json.loads(args.template.read_text(encoding="utf-8"))
    config.update({
        "bundle_id": bundle_id,
        "api_id": api_id,
        "api_hash": api_hash,
        "team_id": "0000000000",
        "app_center_id": "0",
        "is_internal_build": "true",
        "is_appstore_build": "false",
        "appstore_id": "0",
        "app_specific_url_scheme": "tg",
        "premium_iap_product_id": "",
        "enable_siri": False,
        "enable_icloud": False,
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    os.chmod(args.output, 0o600)
    args.notice.parent.mkdir(parents=True, exist_ok=True)
    args.notice.write_text("APIID 和 APIHASH 来自仓库 Actions secrets，已注入构建配置；值未写入仓库或日志。\n", encoding="utf-8")
    print(f"Sogram build configuration created for bundle ID {bundle_id}. API values were not printed.")


if __name__ == "__main__":
    main()
