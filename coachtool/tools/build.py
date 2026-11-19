"""Builds pages from the records. Usage: python3 tools/build.py <plan id> <brand id>"""
import sys, re, html, base64, pathlib, yaml
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check import check, load, ROOT
from club_check import club_report
def esc(t):
    t = html.escape(t, quote=False)
    for ch, ent in {'’': '&rsquo;', '‘': '&lsquo;', '“': '&ldquo;', '”': '&rdquo;', '—': '&mdash;', '–': '&ndash;'}.items():
        t = t.replace(ch, ent)
    return t
def names_list(refs, acts):
    ns = []
    for r in refs:
        base, _, var = r.partition('#')
        ns.append(next(v['name'] for v in acts[base].get('variants', []) if v['id'] == var) if var else acts[base]['name'])
    return ns[0] if len(ns) == 1 else ' or '.join(ns) if len(ns) == 2 else ', '.join(ns[:-1]) + ', or ' + ns[-1]
def txt(v):
    return '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in v) + '</ul>' if isinstance(v, list) else esc(v)
def opt(label, v):
    return f'<div class="a-label">{label}</div><div class="a-text">{txt(v)}</div>' if v else ''
def progression_html(a):
    if not a.get('progression'): return ''
    return '<div class="a-label">Progressions</div><div class="a-text"><ol>' + ''.join(f'<li><b>{esc(p["title"])}</b>{(" (" + str(p["minutes"]) + " min)") if p.get("minutes") else ""} {esc(p["text"])}</li>' for p in a['progression']) + '</ol></div>'
def card(a, acts):
    equip = esc(a['equipment'])
    src = f'<div class="act-source">Source: {esc(a["source"])}</div>' if a.get('source') else ''
    return f'''    <div class="act-card">
      <div class="act-header">
        <div class="act-num">Activity {a["order"]:02d}</div>
        <div class="act-name">{esc(a["name"])}</div>
        <div class="act-focus">{esc(" · ".join(a["skills"]))}</div>
      </div>
      <div class="act-body">
        {opt('What it is for', a.get('objective'))}<div class="a-label">Setup</div><div class="a-text">{txt(a["setup"])}</div>
        {opt('Rules', a.get('rules'))}{opt('Scoring', a.get('scoring'))}{opt('Coach note', a.get('coach_note'))}
        {progression_html(a)}<div class="a-label">What to Look For</div><div class="a-text">{" ".join(esc(c["cue"]) for c in a["coach"])}</div>
        {"".join(f'<div class="a-question">&ldquo;{esc(c["ask"])}&rdquo;</div>' for c in a["coach"])}
        <span class="pairs-tag">&#8594; Pairs well with: {esc(names_list(a["pairs_with"], acts))}</span>
        <div class="e-tags" style="margin-top:10px;"><span class="e-tag">{equip}</span></div>
        {src}
      </div></div>
'''
def activities_html(plan, acts, blocks):
    out = ''
    for b in ['B1', 'B2', 'B3', 'B4', 'B5']:
        group = sorted([a for a in acts.values() if a['block'] == b and plan['age'] in a['ages'] and plan['track'] in a['tracks']], key=lambda a: a['order'])
        if not group: continue
        bl = blocks[b]
        out += f'''  <div class="skill-group-bar {bl["css"]}"><span class="skill-group-label">{esc(bl["name"].upper())} &nbsp;&mdash;&nbsp; {esc(bl["group_label"])}</span></div>
  <div class="activity-grid" style="margin-top:14px;">
''' + ''.join(card(a, acts) for a in group) + '  </div>\n\n'
    return out.rstrip('\n') + '\n'
def rotation_html(plan, acts):
    cell = 'style="vertical-align:middle;border-right:2px solid #e0e5f0;"'
    out = ''
    def nm(r):
        base, _, var = r.partition('#')
        return next(v['name'] for v in acts[base]['variants'] if v['id'] == var) if var else acts[base]['name']
    for w in plan['weeks']:
        if w.get('coach_choice'):
            out += f'''      <tr>
        <td class="week-num" style="border-right:2px solid #e0e5f0;">{w["week"]}</td>
        <td style="font-style:italic;color:var(--gray-mid);font-size:11.5px;border-right:1px solid #eee;">{esc(w["focus"])}</td>
        <td colspan="2" style="font-style:italic;color:var(--gray-mid);">{esc(w["note"])}</td>
      </tr>
'''
            continue
        s1, s2 = w['sessions']
        out += f'''
      <tr class="week-a">
        <td rowspan="2" class="week-num" {cell}>{w["week"]}</td>
        <td rowspan="2" style="vertical-align:middle;border-right:1px solid #eee;font-size:11.5px;font-style:italic;color:var(--gray-mid);">{esc(w["focus"])}</td>
        <td><span class="prac-label prac-a">Practice A</span><br>{esc(nm(s1["a"]["activity"]))}<div class="pair-tag">{esc(s1["a"]["note"])}</div></td>
        <td>{esc(nm(s1["b"]["activity"]))}<div class="pair-tag">{esc(s1["b"]["note"])}</div></td>
      </tr>
      <tr class="week-b">
        <td><span class="prac-label prac-b">Practice B</span><br>{esc(nm(s2["a"]["activity"]))}<div class="pair-tag">{esc(s2["a"]["note"])}</div></td>
        <td>{esc(nm(s2["b"]["activity"]))}<div class="pair-tag">{esc(s2["b"]["note"])}</div></td>
      </tr>'''
    return out
def build(plan_id, brand_id, out=None):
    errs, acts = check()
    if errs: sys.exit('Fix these first:\n' + '\n'.join(errs))
    plan = load(ROOT / 'data' / 'plans' / f'{plan_id}.yaml'); blocks = load(ROOT / 'data' / 'blocks.yaml')
    brand = load(ROOT / 'theme' / brand_id / 'club.yaml')
    logo = 'data:image/png;base64,' + base64.b64encode((ROOT / 'theme' / brand_id / brand['logo_file']).read_bytes()).decode()
    age = load(ROOT / 'data' / 'ages' / f'{plan_id}.yaml'); vocab = load(ROOT / 'data' / 'vocab' / 'skills.yaml')
    goals = load(ROOT / 'data' / 'goals' / f"{age['goals']}.yaml")['goals']
    pills = '\n    '.join(f'<span class="pill {vocab[p]["kind"]}">{esc(vocab[p]["label"])}</span>' for p in age['pills'])
    note = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc(age['pills_note']))
    gl = '\n'.join(f'      <div class="profile-item">{esc(g["text"])}</div>' for g in goals)
    page = (ROOT / 'templates' / 'companion-rec.html').read_text(encoding='utf-8')
    page = page.replace('{{PILLS}}', pills).replace('{{PILLS_NOTE}}', note).replace('{{NEXT_AGE}}', age['next_age']).replace('{{GOALS}}', gl)
    page = page.replace('{{ACTIVITIES}}', activities_html(plan, acts, blocks)).replace('{{ROTATION}}', rotation_html(plan, acts))
    for k, v in brand.items(): page = page.replace('{{brand.%s}}' % k, v)
    page = page.replace('{{brand.logo_src}}', logo)
    left = [t for t in re.findall(r'\{\{[^}]+\}\}', page)]
    if left: sys.exit(f'Unfilled tokens: {left}')
    out = pathlib.Path(out or ROOT / 'build' / f'{plan_id}.{brand_id}.html'); out.write_text(page, encoding='utf-8'); return out
def merge_rules(age, club, track):
    """Core rules for the age, then the club's. Same label: the club's replaces the core one in place. New label: appended."""
    cp = ROOT / 'data' / 'rules' / f'{age}.yaml'
    out = [dict(r, origin='core') for r in (load(cp).get('rules', []) if cp.exists() else []) if track in r.get('tracks', [track])]
    for r in club.get('rules', []):
        if track not in r.get('tracks', [track]): continue
        r = dict(r, origin='club'); at = next((i for i, x in enumerate(out) if x['label'].lower() == r['label'].lower()), None)
        if at is None: out.append(r)
        else: out[at] = r
    return out
def attach_figs(acts):
    import io
    from PIL import Image
    for a in acts:
        ds = a.get('diagram'); ds = [ds] if isinstance(ds, str) else (ds or [])
        cs = a.get('diagram_caption'); cs = [cs] if isinstance(cs, str) else (cs or [])
        figs = []
        for n, d in enumerate(ds):
            f = ROOT / 'data' / 'diagrams' / d
            if f.suffix.lower() == '.svg': raw, mime = f.read_bytes(), 'image/svg+xml'
            else:
                im = Image.open(f); im.thumbnail((720, 720)); buf = io.BytesIO()
                if im.mode in ('RGBA', 'LA', 'P'): im.save(buf, 'PNG', optimize=True); mime = 'image/png'
                else: im.convert('RGB').save(buf, 'JPEG', quality=82, optimize=True); mime = 'image/jpeg'
                raw = buf.getvalue()
            figs.append({'src': f'data:{mime};base64,' + base64.b64encode(raw).decode(), 'caption': cs[n] if n < len(cs) else ''})
        if figs: a['figs'] = figs

def build_app(plan_id, brand_id, area=None):
    cerrs, cwarns = club_report(brand_id)
    if cerrs: sys.exit('Fix the club file first:\n' + '\n'.join('  ' + e for e in cerrs))
    for w in cwarns: print('club setup, blank:', w)
    import json
    errs, acts = check()
    if errs: sys.exit('Fix these first:\n' + '\n'.join(errs))
    attach_figs(acts.values())
    blocks = load(ROOT / 'data' / 'blocks.yaml'); brand = load(ROOT / 'theme' / brand_id / 'club.yaml'); ladder = load(ROOT / 'rules' / 'ladder.yaml')
    teams = []
    for pf in sorted((ROOT / 'data' / 'plans').glob('*.yaml'), key=lambda f: int(re.sub(r'\D', '', load(f)['age']))):
        plan = load(pf); age = load(ROOT / 'data' / 'ages' / f"{plan['id']}.yaml"); fid = age['goals']
        skills = [r for f in (ROOT / 'data' / 'skills').glob(f"{plan['age']}.yaml") for r in load(f)['skills'] if plan['track'] in r['tracks']]
        ov = ROOT / 'theme' / brand_id / 'overlay' / f"{plan['age']}.yaml"
        club = load(ov) if ov.exists() else {}
        teams.append({'id': plan['id'], 'age': plan['age'], 'track': plan['track'], 'label': age.get('label', plan['age'].upper()), 'plan': plan,
                      'goals': load(ROOT / 'data' / 'goals' / f"{fid}.yaml")['goals'], 'players': load(ROOT / 'data' / 'players' / f"{age['players']}.yaml"),
                      'framework': load(ROOT / 'data' / 'framework' / f"{age['framework']}.yaml"), 'skills': skills, 'club': club, 'rules': merge_rules(plan['age'], club, plan['track']), 'ladder': ladder[plan['track']][plan['age']]})
    if area: teams = [t for t in teams if t['track'] == area]
    if not teams: sys.exit(f'No {area} teams yet')
    data = {'area': area or 'all', 'help': {'email': (brand.get('help_email') or '').strip(), 'form': (brand.get('suggest_form_url') or '').strip(), 'support': (brand.get('support_line') or '').strip()}, 'activities': sorted(acts.values(), key=lambda a: a['order']), 'teams': teams, 'blocks': blocks, 'ladder': ladder, 'types': load(ROOT / 'data' / 'vocab' / 'activity-types.yaml')['types'], 'routines': [load(f) for f in sorted((ROOT / 'data' / 'routines').glob('*.yaml'))], 'routine_kinds': load(ROOT / 'data' / 'vocab' / 'routine-kinds.yaml')['kinds'], 'credit': load(ROOT / 'data' / 'credit.yaml'), 'updated': __import__('datetime').date.today().strftime('%b %-d, %Y')}
    if not area: (ROOT / 'build' / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    logo = 'data:image/png;base64,' + base64.b64encode((ROOT / 'theme' / brand_id / brand.get('logo_small_file', brand['logo_file'])).read_bytes()).decode()
    page = (ROOT / 'app' / 'index.html').read_text(encoding='utf-8').replace('/*DATA*/', json.dumps(data, ensure_ascii=False))
    for k, v in brand.items(): page = page.replace('{{brand.%s}}' % k, v)
    page = page.replace('{{brand.logo_src}}', logo).replace('{{area}}', {'rec': 'Rec', 'comp': 'Comp'}.get(area, 'Rec and comp'))
    left = re.findall(r'\{\{[^}]+\}\}', page)
    if left: sys.exit(f'Unfilled tokens: {left}')
    out = ROOT / 'build' / (f'{area}.html' if area else f'planner.{brand_id}.html'); out.write_text(page, encoding='utf-8'); return out
DEFAULT_BRAND = 'coach-craft'  # the club theme used when none is named
def build_all(brand_id=DEFAULT_BRAND):
    build_app('u10-rec', brand_id)  # full data.json
    outs = [build_app('u10-rec', brand_id, a) for a in ('rec', 'comp')]
    (ROOT / 'build' / f'planner.{brand_id}.html').write_text('<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=rec.html"><title>Coach Companion</title><a href="rec.html">Open the rec planner</a>', encoding='utf-8')
    return outs
def build_author():
    import json
    errs, acts = check()
    if errs: sys.exit('Fix these first:\n' + '\n'.join(errs))
    attach_figs(acts.values())
    data = {'activities': sorted(acts.values(), key=lambda a: a['order']), 'blocks': load(ROOT / 'data' / 'blocks.yaml'),
            'tags': load(ROOT / 'data' / 'vocab' / 'activity-tags.yaml'), 'types': load(ROOT / 'data' / 'vocab' / 'activity-types.yaml')['types'], 'ladder': load(ROOT / 'rules' / 'ladder.yaml')}
    page = (ROOT / 'app' / 'author.html').read_text(encoding='utf-8').replace('/*DATA*/', json.dumps(data, ensure_ascii=False))
    out = ROOT / 'build' / 'activity-builder.html'; out.write_text(page, encoding='utf-8')
    (ROOT / 'build' / 'all-activities.html').write_text((ROOT / 'app' / 'all.html').read_text(encoding='utf-8').replace('/*DATA*/', json.dumps(data, ensure_ascii=False)), encoding='utf-8')
    skills = [r for f in sorted((ROOT / 'data' / 'skills').glob('*.yaml')) for r in load(f)['skills']]
    (ROOT / 'build' / 'skills-matrix.html').write_text((ROOT / 'app' / 'matrix.html').read_text(encoding='utf-8').replace('/*DATA*/', json.dumps({'skills': skills, 'blocks': data['blocks']}, ensure_ascii=False)), encoding='utf-8')
    brand = load(ROOT / 'theme' / DEFAULT_BRAND / 'club.yaml')
    logo = 'data:image/png;base64,' + base64.b64encode((ROOT / 'theme' / DEFAULT_BRAND / brand['logo_file']).read_bytes()).decode()
    root = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Coach Companion</title><style>
body{{margin:0;font:18px/1.5 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#222;background:#f6f7fa}}header{{background:{brand['navy_dark']};border-bottom:3px solid {brand['gold']};padding:14px 16px;color:#fff;display:flex;align-items:center;gap:12px}}header img{{height:44px}}header b{{font-size:17px}}header small{{display:block;opacity:.75;font-size:13px}}
main{{max-width:560px;margin:0 auto;padding:28px 16px}}h1{{font-size:28px;margin:0 0 8px}}p.lead{{color:#555;margin:0 0 22px}}a.go{{display:block;background:{brand['navy']};color:#fff;text-align:center;text-decoration:none;font-weight:700;border-radius:12px;padding:16px;font-size:19px}}.tip{{color:#6b7280;font-size:15px;margin:14px 0 0;text-align:center}}footer{{max-width:560px;margin:30px auto 0;padding:16px;border-top:1px solid #e3e7ee;font-size:14px;color:#6b7280}}footer a{{color:#6b7280}}</style></head><body>
<header><img src="{logo}" alt=""><div><b>Coach Companion</b><small>{'' if brand['short_name'] == 'Coach Companion' else brand['short_name']}</small></div></header>
<main><h1>Ideas for your season, one week at a time</h1><p class="lead">Suggested sessions and how-tos for every activity, in one shared language across the club.</p><a class="go" href="rec.html">Open the rec planner</a><a class="go" href="comp.html" style="margin-top:10px">Open the comp planner</a><p class="tip">Tip: save this page to your phone's home screen so it opens like an app.</p></main>
<footer>For authors: <a href="activity-builder.html">Activity Builder</a></footer></body></html>'''
    (ROOT / 'build' / 'index.html').write_text(root, encoding='utf-8')
    return out
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'all': print('wrote', *build_all(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BRAND)); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'author': print('wrote', build_author()); sys.exit()
    if len(sys.argv) > 3 and sys.argv[3] == 'app': print('wrote', build_app(sys.argv[1], sys.argv[2])); sys.exit()
    print('wrote', build(sys.argv[1], sys.argv[2]))
