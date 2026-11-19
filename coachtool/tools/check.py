"""Checks the records. Exit code 1 if anything is wrong."""
import sys, pathlib, yaml, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCKS = set(yaml.safe_load((ROOT / 'data' / 'blocks.yaml').read_text(encoding='utf-8')))
def load(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def check(root=ROOT):
    errs = []
    ladder = load(root / 'rules' / 'ladder.yaml')
    acts = {}
    for f in sorted((root / 'data' / 'activities').glob('*.yaml')):
        a = load(f)
        _types = {t['id'] for t in load(root / 'data' / 'vocab' / 'activity-types.yaml')['types']} if (root / 'data' / 'vocab' / 'activity-types.yaml').exists() else set()
        if a.get('type') not in _types: errs.append(f"{f.name}: type must be one of {sorted(_types)}")
        def _txt(v): return (isinstance(v, str) and v.strip()) or (isinstance(v, list) and v and all(isinstance(x, str) and x.strip() for x in v))
        for _k in ('setup', 'scoring', 'rules', 'coach_note'):
            if _k in a and not _txt(a[_k]): errs.append(f'{f.name}: {_k} must be text or a list of lines')
        if 'objective' in a and not (isinstance(a['objective'], str) and a['objective'].strip()): errs.append(f'{f.name}: objective must be a non-empty string')
        if 'diagram_caption' in a and not _txt(a['diagram_caption']): errs.append(f'{f.name}: diagram_caption must be text or a list of captions')
        def _coach(c): return isinstance(c, list) and c and all(isinstance(x, dict) and (x.get('cue') or '').strip() and (x.get('ask') or '').strip() for x in c)
        if not _coach(a.get('coach')): errs.append(f'{f.name}: coach must be a list of cue and ask pairs')
        for ag, o in (a.get('for_age') or {}).items():
            if 'coach' in o and not _coach(o['coach']): errs.append(f'{f.name}: for_age {ag} coach must be a list of cue and ask pairs')
        if 'progression' in a:
            p = a['progression']
            if not (isinstance(p, list) and p and all(isinstance(x, dict) and (x.get('title') or '').strip() and (x.get('text') or '').strip() and (x.get('minutes') is None or isinstance(x['minutes'], int)) for x in p)):
                errs.append(f'{f.name}: progression must be a list of steps with a title and text (minutes optional)')
        if 'source' in a and not (isinstance(a['source'], str) and a['source'].strip()): errs.append(f'{f.name}: source must be a non-empty string')
        for k in ['id', 'name', 'block', 'skills', 'ages', 'tracks', 'levels', 'players', 'space', 'setup', 'coach', 'equipment', 'objective']:
            if a.get(k) in (None, '', []): errs.append(f'{f.name}: missing {k}')
        if a.get('id') != f.stem: errs.append(f'{f.name}: id {a.get("id")} does not match file name')
        if a.get('space') not in ('quarter', 'half', 'full'): errs.append(f'{f.name}: space must be quarter, half or full, not {a.get("space")}')
        if a.get('block') not in BLOCKS: errs.append(f'{f.name}: bad block {a.get("block")}')
        ds = a.get('diagram'); ds = [ds] if isinstance(ds, str) else (ds or [])
        cs = a.get('diagram_caption'); cs = [cs] if isinstance(cs, str) else (cs or [])
        if len(cs) > len(ds) or (len(ds) > 1 and cs and len(cs) != len(ds)): errs.append(f'{f.name}: give one diagram caption per diagram, or none')
        for d in ds:
            if not (root / 'data' / 'diagrams' / d).is_file(): errs.append(f'{f.name}: diagram file {d} not found in data/diagrams')
            if d.rsplit('.', 1)[-1].lower() not in ('png', 'jpg', 'jpeg', 'webp', 'svg'): errs.append(f'{f.name}: diagram must be png, jpg, webp or svg')
        v = a.get('video')
        if v and not (isinstance(v, str) and v.startswith(('http://', 'https://'))): errs.append(f'{f.name}: video must be a web link starting with http')
        tags = load(root / 'data' / 'vocab' / 'activity-tags.yaml'); okt = set(tags['actions'] + tags['concepts'])
        for t in a.get('skills', []):
            if t not in okt: errs.append(f'{f.name}: skill tag "{t}" is not in data/vocab/activity-tags.yaml')
        acts[a['id']] = a
        for age in a.get('ages', []):
            for tr in a.get('tracks', []):
                if age in ladder[tr] and a['block'] not in ladder[tr][age]:
                    errs.append(f'{a["id"]}: block {a["block"]} is not part of {tr} {age}')
                for lv in a.get('levels', []):
                    if lv not in ladder['levels'][tr]: errs.append(f'{a["id"]}: level {lv} is not used in {tr}')
    for a in acts.values():
        for ag, o in (a.get('for_age') or {}).items():
            if ag not in a['ages']: errs.append(f'{a["id"]}: for_age {ag} is not one of its ages')
    kinds = {k['id'] for k in load(root / 'data' / 'vocab' / 'routine-kinds.yaml')['kinds']} if (root / 'data' / 'vocab' / 'routine-kinds.yaml').exists() else set()
    for f in sorted((root / 'data' / 'routines').glob('*.yaml')) if (root / 'data' / 'routines').exists() else []:
        r = load(f)
        for k in ['id', 'name', 'kind', 'objective', 'ages', 'tracks', 'steps', 'equipment']:
            if r.get(k) in (None, '', []): errs.append(f'routine {f.name}: missing {k}')
        if r.get('id') != f.stem: errs.append(f'routine {f.name}: id does not match file name')
        if r.get('kind') not in kinds: errs.append(f'routine {f.name}: kind {r.get("kind")} is not in data/vocab/routine-kinds.yaml')
        for i, st in enumerate(r.get('steps') or []):
            if not (isinstance(st, dict) and (st.get('name') or '').strip() and (st.get('how') or '').strip()): errs.append(f'routine {f.name}: step {i+1} needs a name and how')
        for tr in r.get('tracks') or []:
            for ag in r.get('ages') or []:
                if ag not in ladder.get(tr, {}): errs.append(f'routine {f.name}: {ag} is not an age in {tr}')
        v = r.get('video')
        if v and not (isinstance(v, str) and v.startswith(('http://', 'https://'))): errs.append(f'routine {f.name}: video must be a web link starting with http')
    rids = {f.stem for f in (root / 'data' / 'routines').glob('*.yaml')} if (root / 'data' / 'routines').exists() else set()
    for pf in sorted((root / 'data' / 'plans').glob('*.yaml')):
        for w in load(pf).get('weeks', []):
            if w.get('routine') and w['routine'] not in rids: errs.append(f'plan {pf.name} week {w.get("week")}: routine {w["routine"]} does not exist')
    for pf in sorted((root / 'data' / 'plans').glob('*.yaml')):
        pl = load(pf)
        for w in pl.get('weeks', []):
            o = w.get('opening')
            if o:
                oa = acts.get(o.get('activity'))
                if not oa: errs.append(f'plan {pf.name} week {w.get("week")}: opening activity {o.get("activity")} does not exist')
                else:
                    if oa['type'] != 'opening-play': errs.append(f'plan {pf.name} week {w.get("week")}: opening {oa["id"]} is not an opening-play activity')
                    if pl['age'] not in oa['ages'] or pl['track'] not in oa['tracks']: errs.append(f'plan {pf.name} week {w.get("week")}: opening {oa["id"]} is not for {pl["track"]} {pl["age"]}')
            for ses in w.get('sessions', []):
                b, lv = ses.get('block'), ses.get('level')
                if b and b not in ladder[pl['track']].get(pl['age'], []): errs.append(f'plan {pf.name} week {w.get("week")}: block {b} is not part of {pl["track"]} {pl["age"]}')
                if lv and lv not in ladder['levels'][pl['track']]: errs.append(f'plan {pf.name} week {w.get("week")}: level {lv} is not used in {pl["track"]}')
    seen = {}
    for a in acts.values():
        _flat = lambda v: ' '.join(v) if isinstance(v, list) else str(v)
        for k, val in (('setup', _flat(a['setup'])),) + tuple((f'coach {i+1} cue', c['cue']) for i, c in enumerate(a['coach'])) + tuple((f'coach {i+1} ask', c['ask']) for i, c in enumerate(a['coach'])):
            key = re.sub(r'\W+', ' ', val.lower()).strip()
            if key in seen: errs.append(f'{a["id"]}: {k} repeats {seen[key]}')
            seen[key] = f'{a["id"]}.{k}'
    def ref_ok(r):
        base, _, var = r.partition('#')
        if base not in acts: return False
        return not var or var in [v['id'] for v in acts[base].get('variants', [])]
    for a in acts.values():
        for r in a.get('pairs_with', []):
            if not ref_ok(r): errs.append(f'{a["id"]}: pairs_with {r} does not exist')
            if r == a['id']: errs.append(f'{a["id"]}: pairs with itself')
    for f in sorted((root / 'data' / 'plans').glob('*.yaml')):
        p = load(f); allowed = ladder[p['track']].get(p['age'], [])
        nums = [w['week'] for w in p['weeks']]
        if nums != list(range(1, len(nums) + 1)): errs.append(f'{f.name}: weeks are not numbered 1 to {len(nums)}')
        for w in p['weeks']:
            if w.get('coach_choice'): continue
            if w['block'] not in allowed: errs.append(f'{f.name} wk{w["week"]}: block {w["block"]} not allowed for {p["track"]} {p["age"]}')
            if w['level'] not in ladder['levels'][p['track']]: errs.append(f'{f.name} wk{w["week"]}: level {w["level"]} not used in {p["track"]}')
            for i, ses in enumerate(w['sessions'], 1):
                ids = []; full = []
                for slot in [k for k in ('a', 'b') if k in ses]:
                    r = ses[slot].get('activity')
                    if not r: continue
                    if not ref_ok(r): errs.append(f'{f.name} wk{w["week"]} session {i} {slot}: unknown activity {r}'); continue
                    ids.append(r.split('#')[0]); full.append(r)
                    if p['age'] not in acts[r.split('#')[0]]['ages']: errs.append(f'{f.name} wk{w["week"]}: {r} is not an {p["age"]} activity')
                if len(full) == 2 and full[0] == full[1]: errs.append(f'{f.name} wk{w["week"]} session {i}: A and B are the same activity')
                if ids and not any(acts[x]['block'] in [ses.get('block', w['block'])] + w.get('also_blocks', []) for x in ids):
                    errs.append(f'{f.name} wk{w["week"]} session {i}: neither activity is a {ses.get("block", w["block"])} activity')

    # skills, goals and age configs
    for f in sorted((root / 'data' / 'rules').glob('*.yaml')) if (root / 'data' / 'rules').exists() else []:
        rd = load(f); seen = set()
        for r in rd.get('rules', []):
            if not r.get('label') or not r.get('text'): errs.append(f'{f.name}: every rule needs a label and text')
            elif (r['label'].lower(), tuple(r.get('tracks', []))) in seen: errs.append(f'{f.name}: duplicate rule label {r["label"]}')
            else: seen.add((r['label'].lower(), tuple(r.get('tracks', []))))
        if rd.get('age') != f.stem: errs.append(f'{f.name}: age does not match file name')
    vocab = load(root / 'data' / 'vocab' / 'skills.yaml')
    seen_b = {}
    for f in sorted((root / 'data' / 'skills').glob('*.yaml')):
        recs = load(f)['skills']; areas = {}; rec_areas = set()
        for r in recs:
            if r['block'] not in BLOCKS: errs.append(f'{r["id"]}: bad block {r["block"]}')
            if not r.get('bullets'): errs.append(f'{r["id"]}: no bullets')
            for tr in r['tracks']:
                if r['level'] not in ladder['levels'][tr]: errs.append(f'{r["id"]}: level {r["level"]} not used in {tr}')
                if r['age'] in ladder[tr] and r['block'] not in ladder[tr][r['age']]: errs.append(f'{r["id"]}: block {r["block"]} not part of {tr} {r["age"]}')
            areas.setdefault((r['block'], r['area']), set()).add(r['level'])
            if 'rec' in r['tracks']: rec_areas.add((r['block'], r['area']))
            for b in r['bullets']:
                for tr in r['tracks']:
                    key = (r['age'], tr, re.sub(r'\W+', ' ', b.lower()).strip())
                    if key in seen_b: errs.append(f'{r["id"]}: bullet repeats {seen_b[key]}: "{b[:50]}"')
                    seen_b[key] = r['id']
        for (b, a), lv in areas.items():
            if 'intro' not in lv and (b, a) in rec_areas: errs.append(f'{f.name}: {b} {a} has no intro level')
    for f in sorted((root / 'data' / 'goals').glob('*.yaml')):
        g = load(f)
        for x in g['goals']:
            for b in x['blocks']:
                if b not in BLOCKS: errs.append(f'goal {x["id"]}: bad block {b}')
    for f in sorted((root / 'data' / 'ages').glob('*.yaml')):
        a = load(f)
        for pid in a['pills']:
            if pid not in vocab: errs.append(f'{f.name}: pill {pid} is not in the skill vocabulary')
        for k, d in (('goals', 'goals'), ('players', 'players'), ('framework', 'framework')):
            if a.get(k) and not (root / 'data' / d / (a[k] + '.yaml')).exists(): errs.append(f'{f.name}: {k} file {a[k]} missing')
    return errs, acts
if __name__ == '__main__':
    errs, acts = check()
    for e in errs: print('ERROR', e)
    print(f'{len(acts)} activities checked, {len(errs)} problems')
    sys.exit(1 if errs else 0)
