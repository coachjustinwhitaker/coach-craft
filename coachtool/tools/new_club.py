"""Starts a new club: python3 tools/new_club.py <club id>. Writes a labeled blank theme/<id>/club.yaml and an overlay folder."""
import sys, re, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) != 2 or not re.fullmatch(r'[a-z0-9-]+', sys.argv[1]): sys.exit('Usage: python3 tools/new_club.py <club id, lowercase letters, numbers, hyphens>')
cid = sys.argv[1]; d = ROOT / 'theme' / cid
if d.exists(): sys.exit(f'theme/{cid} already exists')
spec = yaml.safe_load((ROOT / 'rules' / 'club-fields.yaml').read_text(encoding='utf-8')); (d / 'overlay').mkdir(parents=True)
out, sec = [f'# {cid}: everything this club supplies. Required fields are marked. Run: python3 tools/club_check.py {cid}'], None
for f in spec['fields']:
    if f['section'] != sec: sec = f['section']; out += ['', f'# ---- {sec} ----']
    out += [f"# {'REQUIRED. ' if f['required'] else 'Recommended. '}{f['what']}. Example: {f['example']}", f"{f['key']}: {repr(cid) if f['key'] == 'id' else repr('')}"]
(d / 'club.yaml').write_text('\n'.join(out) + '\n', encoding='utf-8')
(d / 'overlay' / 'README.txt').write_text('One file per age, named like u10.yaml. Only what differs by age:\n' + '\n'.join(f"  {k['key']}: {k['what']}. Example: {k['example']}" if 'example' in k else f"  {k['key']}: {k['what']}" for k in spec['overlay']['keys']) + '\n', encoding='utf-8')
print(f'Created theme/{cid}/. Fill in club.yaml, add logo files, then run: python3 tools/club_check.py {cid}')
