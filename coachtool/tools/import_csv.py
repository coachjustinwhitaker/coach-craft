"""Imports activities from a CSV (data/templates/activities-template.csv) or from a batch file
downloaded from the Activity Builder page (.json).
Usage: python3 tools/import_csv.py <file.csv|file.json> [--update]
CSV lists (skills, ages, tracks, levels, pairs_with) are separated by semicolons. A new activity is
skipped if its id exists, unless --update (a builder batch marks its own edits). Everything is checked,
and nothing is kept if the check fails."""
import csv, re, sys, json, base64, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from check import check
def slug(n): return re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')
def lst(v): return v if isinstance(v, list) else [x.strip() for x in str(v or '').split(';') if x.strip()]
def lines(v):
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in str(v or '').splitlines() if x.strip()]
def text_val(v):
    ls = lines(v)
    return None if not ls else ls[0] if len(ls) == 1 else ls
def coach_val(row):
    c = row.get('coach')
    if isinstance(c, list): return [{'cue': str(x['cue']).strip(), 'ask': str(x['ask']).strip()} for x in c if x.get('cue') or x.get('ask')]
    out = []
    for ln in lines(c):
        cue, _, ask = ln.partition('::'); out.append({'cue': cue.strip(), 'ask': ask.strip()})
    if not out and (row.get('look_for') or row.get('question')): out = [{'cue': str(row.get('look_for') or '').strip(), 'ask': str(row.get('question') or '').strip()}]
    return out
PROG = re.compile(r'^(.*?)(?:\s*\((\d+)\s*min\))?\s*::\s*(.*)$')
def prog_val(v):
    out = []
    if isinstance(v, list):
        for x in v:
            s = {'title': str(x.get('title') or '').strip(), 'text': str(x.get('text') or '').strip()}
            if x.get('minutes'): s['minutes'] = int(x['minutes'])
            out.append(s)
        return out
    for ln in lines(v):
        m = PROG.match(ln)
        if not m: out.append({'title': ln, 'text': ''}); continue
        s = {'title': m.group(1).strip(), 'text': m.group(3).strip()}
        if m.group(2): s['minutes'] = int(m.group(2))
        out.append(s)
    return out
def rows_from(src):
    if src.suffix.lower() == '.json':
        return [dict(r) for r in json.loads(src.read_text(encoding='utf-8'))['activities']]
    out = []
    for row in csv.DictReader(src.open(encoding='utf-8-sig')):
        row = {k.strip(): (v or '').strip() for k, v in row.items() if k}
        if row.get('name') and not row['name'].startswith('Example'): out.append(row)
    return out
def main():
    src = pathlib.Path(sys.argv[1]); update_all = '--update' in sys.argv
    adir = ROOT / 'data' / 'activities'; ddir = ROOT / 'data' / 'diagrams'; ddir.mkdir(exist_ok=True)
    existing = {f.stem: yaml.safe_load(f.read_text(encoding='utf-8')) for f in adir.glob('*.yaml')}
    order = max([a['order'] for a in existing.values()] + [0])
    backup = {}; written = []; skipped = []; newfiles = []
    for row in rows_from(src):
        i = row.get('id') or slug(row['name'])
        if i in existing and not (update_all or row.get('update')): skipped.append(i); continue
        old = existing.get(i)
        if old: order_n = old['order']; backup[i] = (adir / f'{i}.yaml').read_text(encoding='utf-8')
        else: order += 1; order_n = order
        new = {'id': i, 'order': order_n, 'name': row['name'], 'block': str(row['block']).upper(), 'skills': lst(row['skills']),
             'ages': lst(row['ages']), 'tracks': lst(row['tracks']), 'levels': lst(row['levels']),
             'players': {'min': int(row['players_min']), 'max': int(row['players_max'])}, 'space': str(row['space']).lower(),
             'minutes': int(row.get('minutes') or 15), 'pairs_with': lst(row.get('pairs_with')), 'equipment': row['equipment']}
        a = dict(old) if old else {}; a.update(new)
        for _k in ('setup', 'rules', 'scoring', 'coach_note'):
            if _k in row or _k == 'setup':
                tv = text_val(row.get(_k))
                if tv is not None: a[_k] = tv
        cv = coach_val(row)
        if cv: a['coach'] = cv
        a.pop('look_for', None); a.pop('question', None)
        if row.get('progression'): a['progression'] = prog_val(row['progression'])
        if (row.get('diagram') or '').strip():
            ds = [x.strip() for x in row['diagram'].split(';') if x.strip()]
            a['diagram'] = ds[0] if len(ds) == 1 else ds
        if (row.get('video') or '').strip(): a['video'] = row['video'].strip()
        if (row.get('source') or '').strip(): a['source'] = row['source'].strip()
        if (row.get('type') or '').strip(): a['type'] = row['type'].strip().lower()
        if (row.get('objective') or '').strip(): a['objective'] = row['objective'].strip()
        if (row.get('diagram_caption') or '').strip():
            cl = lines(row['diagram_caption']); a['diagram_caption'] = cl[0] if len(cl) == 1 else cl
        if row.get('diagram_data') and isinstance(a.get('diagram'), str):
            f = ddir / a['diagram']
            if not f.exists(): newfiles.append(f)
            f.write_bytes(base64.b64decode(row['diagram_data'].split(',', 1)[1]))
        (adir / f'{i}.yaml').write_text(yaml.safe_dump(a, sort_keys=False, allow_unicode=True, width=100), encoding='utf-8'); written.append(i)
    errs, _ = check()
    if errs:
        for i in written:
            f = adir / f'{i}.yaml'
            if i in backup: f.write_text(backup[i], encoding='utf-8')
            else: f.unlink()
        for f in newfiles: f.unlink(missing_ok=True)
        sys.exit('Nothing imported. Fix these:\n' + '\n'.join(errs))
    print(f'imported {len(written)}: {", ".join(written) or "none"}')
    if skipped: print(f'skipped (already exist, use --update): {", ".join(skipped)}')
main()
