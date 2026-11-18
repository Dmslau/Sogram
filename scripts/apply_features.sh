#!/usr/bin/env bash
# Apply the Sogram extension overlay to a Telegram-iOS checkout.
# This first integration keeps all additions local and deterministic.
set -euo pipefail

UPSTREAM="$1"
ROOT="$2"

python3 "$ROOT/scripts/apply_custom_client_ui.py" --upstream "$UPSTREAM"
python3 "$ROOT/scripts/apply_global_wallpaper.py" --upstream "$UPSTREAM"

# Existing runtime overlay is optional when its ML Kit vendor package is absent.
# The Sogram Extensions stage must remain buildable without network-only vendors.
if [[ -f "$UPSTREAM/submodules/CueChatAutomation/MLKitVendor/targets.json" && -f "$UPSTREAM/submodules/CueChatAutomation/MLKitVendor/BUILD" ]]; then
  python3 "$ROOT/scripts/apply_runtime_features.py" --upstream "$UPSTREAM" --repo-root "$ROOT"
else
  echo "Sogram Extensions: skipping optional ML Kit runtime overlay (vendor package not staged)."
fi

printf '%s\n' 'Sogram local extension overlay applied.'
