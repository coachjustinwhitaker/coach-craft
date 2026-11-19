"""Checks a club folder against rules/club-fields.yaml. Returns (errors, warnings). Run: python3 tools/club_check.py <club>"""
import re, sys, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parent.parent
def club_report(club):
    d = ROOT / 'theme' / club; errs, warns = [], []
    if not (d / 'club.yaml').exists(): return [f'theme/{club}/club.yaml is missing. Run: python3 tools/new_club.py {club}'], []
    c = yaml.safe_load((d / 'club.yaml').read_text(encoding='utf-8')) or {}
    spec = yaml.safe_load((ROOT / 'rules' / 'club-fields.yaml').read_text(encoding='utf-8'))
    for f in spec['fields']:
        v = c.get(f['key']); blank = v is None or str(v).strip() == ''
        if blank: (errs if f['required'] else warns).append(f"{f['key']} is blank ({f['section']}): {f['what']}")
    for k in ('logo_file', 'logo_small_file'):
        if c.get(k) and not (d / c[k]).exists(): errs.append(f'{k}: file {c[k]} not found in theme/{club}/')
    for k in ('navy', 'navy_dark', 'gold'):
        if c.get(k) and not re.fullmatch(r'#[0-9a-fA-F]{6}', str(c[k])): errs.append(f'{k}: {c[k]} is not a hex color like #384959')
    if c.get('help_email') and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', str(c['help_email'])): errs.append('help_email does not look like an email address')
    if c.get('feedback_url') and not str(c['feedback_url']).startswith('https://'): errs.append('feedback_url must start with https://')
    if c.get('suggest_form_url') and not str(c['suggest_form_url']).startswith('https://'): errs.append('suggest_form_url must start with https://')
    if c.get('id') and c['id'] != club: errs.append(f"id {c['id']} does not match the folder name {club}")
    keys = {k['key'] for k in spec['overlay']['keys']}
    for f in sorted((d / 'overlay').glob('*.yaml')) if (d / 'overlay').exists() else []:
        o = yaml.safe_load(f.read_text(encoding='utf-8')) or {}
        for k in o:
            if k not in keys: errs.append(f'overlay/{f.name}: unknown key {k}')
        for r in o.get('rules', []):
            if not (r.get('label') and r.get('text')): errs.append(f'overlay/{f.name}: every rule needs a label and text')
    plans = {yaml.safe_load(p.read_text(encoding='utf-8'))['age'] for p in (ROOT / 'data' / 'plans').glob('*.yaml')}
    for a in sorted(plans, key=lambda x: int(re.sub(r'\D', '', x))):
        if not (d / 'overlay' / f'{a}.yaml').exists(): warns.append(f'overlay/{a}.yaml is missing: no game format, local rules or pathway text for {a.upper()}')
    return errs, warns
if __name__ == '__main__':
    club = sys.argv[1] if len(sys.argv) > 1 else 'coach-craft'; e, w = club_report(club)
    for x in e: print('ERROR  ', x)
    for x in w: print('missing', x)
    print(f'{club}: {len(e)} errors, {len(w)} recommended items blank'); sys.exit(1 if e else 0)
