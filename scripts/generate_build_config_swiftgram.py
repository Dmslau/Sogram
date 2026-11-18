#!/usr/bin/env python3
import argparse, json, os, re
from pathlib import Path
VALID=re.compile(r'^[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)+$')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--template',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--notice',type=Path,required=True); a=p.parse_args()
 c=json.loads(a.template.read_text())
 bundle=os.environ.get('APP_BUNDLE_ID','').strip() or ('org.swiftgram.' + os.environ.get('GITHUB_RUN_ID','local'))
 if not VALID.fullmatch(bundle): raise SystemExit('invalid bundle configuration')
 # Use the non-secret API values shipped in Swiftgram's example configuration.
 example=(a.template.parent / 'example-configuration' / 'variables.bzl')
 text=example.read_text()
 c['api_id']=re.search(r'telegram_api_id = "([0-9]+)"', text).group(1)
 c['api_hash']=re.search(r'telegram_api_hash = "([0-9a-f]+)"', text).group(1)
 c.update({'bundle_id':bundle,'team_id':'0000000000','is_internal_build':'true','is_appstore_build':'false','appstore_id':'0','app_specific_url_scheme':'tg','premium_iap_product_id':'','enable_siri':False,'enable_icloud':False,'sg_config':''})
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(c)+'\n'); os.chmod(a.output,0o600)
 a.notice.write_text('Swiftgram template API ID/hash were retained; no API values were added to the repository or printed.\n')
 print('Swiftgram build configuration created from the upstream template.')
if __name__=='__main__': main()
