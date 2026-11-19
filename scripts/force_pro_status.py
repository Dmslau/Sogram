#!/usr/bin/env python3
"""Force immediateSGStatus.status = 2 (Pro) for self-signed testing."""
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
    parser.add_argument("--upstream", required=True, type=Path, help="Swiftgram upstream root")
    args = parser.parse_args()

    root = args.upstream

    # 1. SGStatus.default: status 1 -> 2
    sg_status = root / "Swiftgram/SGStatus/Sources/SGStatus.swift"
    if not sg_status.is_file():
        print(f"[FAIL] SGStatus.swift not found at {sg_status}")
        return 1
    ok1 = patch_file(
        sg_status,
        'public static var `default`: SGStatus {\n        return SGStatus(status: 1)\n    }',
        'public static var `default`: SGStatus {\n        return SGStatus(status: 2)\n    }',
        "SGStatus.default",
    )

    # 2. SGSimpleSettings groupDefaultValues: status 1 -> 2
    simple_settings = root / "Swiftgram/SGSimpleSettings/Sources/SimpleSettings.swift"
    if not simple_settings.is_file():
        print(f"[FAIL] SimpleSettings.swift not found at {simple_settings}")
        return 1
    ok2 = patch_file(
        simple_settings,
        "Keys.status.rawValue: 1,",
        "Keys.status.rawValue: 2,",
        "SGSimpleSettings groupDefaultValues.status",
    )

    if ok1 and ok2:
        print("Pro status forced to 2 (immediateSGStatus.status > 1 will be true)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())