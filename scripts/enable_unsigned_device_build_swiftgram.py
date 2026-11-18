#!/usr/bin/env python3
import argparse
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--make-script',required=True,type=Path); p.add_argument('--rules-apple-root',required=True,type=Path); a=p.parse_args()
s=a.make_script.read_text()
if '--disableProvisioningProfiles' not in s or 'set_disable_provisioning_profiles' not in s: raise SystemExit('Swiftgram Make.py lacks unsigned build support')
# Swiftgram already forwards the unsigned flag; add legacy-signing disable to its existing target args.
old="combined_arguments += ['--//Telegram:disableProvisioningProfiles']"
new="combined_arguments += ['--//Telegram:disableProvisioningProfiles', '--//Telegram:disableExtensions', '--features=disable_legacy_signing']"
if old in s and new not in s: s=s.replace(old,new,1); a.make_script.write_text(s)
print('Swiftgram unsigned mode enabled using its native provisioning-profile switch.')
