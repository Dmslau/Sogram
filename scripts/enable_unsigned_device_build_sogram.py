#!/usr/bin/env python3
import argparse, re
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--make-script',required=True,type=Path); p.add_argument('--rules-apple-root',required=True,type=Path); a=p.parse_args()
s=a.make_script.read_text()
old="combined_arguments += ['--//Telegram:disableProvisioningProfiles']"
new="combined_arguments += ['--//Telegram:disableProvisioningProfiles', '--//Telegram:disableExtensions', '--features=disable_legacy_signing']"
if old in s and new not in s: s=s.replace(old,new,1); a.make_script.write_text(s)
files=list(a.rules_apple_root.rglob('ios_rules.bzl'))
if not files: raise SystemExit('Sogram rules_apple ios_rules.bzl not found')
count=0
pat=re.compile(r'    if platform_prerequisites\.platform\.is_device:\n        processor_partials\.append\(\n            partials\.provisioning_profile_partial\(')
rep='    if platform_prerequisites.platform.is_device and "disable_legacy_signing" not in features:\n        processor_partials.append(\n            partials.provisioning_profile_partial('
for f in files:
 t=f.read_text()
 if 'disable_legacy_signing" not in features' in t: continue
 n=len(pat.findall(t))
 if n: f.write_text(pat.sub(rep,t)); count+=n
print(f'Sogram unsigned mode enabled; patched {count} provisioning branches.')
