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
    data = {'area': area or 'all', 'help': {'email': (brand.get('help_email') or '').strip(), 'form': (brand.get('suggest_form_url') or '').strip(), 'feedback': (brand.get('feedback_url') or '').strip()}, 'activities': sorted(acts.values(), key=lambda a: a['order']), 'teams': teams, 'blocks': blocks, 'ladder': ladder, 'types': load(ROOT / 'data' / 'vocab' / 'activity-types.yaml')['types'], 'routines': [load(f) for f in sorted((ROOT / 'data' / 'routines').glob('*.yaml'))], 'routine_kinds': load(ROOT / 'data' / 'vocab' / 'routine-kinds.yaml')['kinds'], 'credit': load(ROOT / 'data' / 'credit.yaml'), 'updated': __import__('datetime').date.today().strftime('%b %-d, %Y')}
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
LANDING = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Coach Craft</title><script src="../../assets/gate-config.js"></script><script src="../../assets/gate.js" defer></script><style>
*{box-sizing:border-box}body{margin:0;font:17px/1.5 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#13202B;background:#F3F8FB}
.wrap{max-width:600px;margin:0 auto;padding:0 18px}
header{background:#E6F6FF;padding:14px 0}header .wrap{display:flex;align-items:center;gap:12px}header img{height:42px;border-radius:10px}header b{font-size:17px;font-weight:600;display:block;line-height:1.2}header small{display:block;color:#3A4D5C;font-size:13px}
.strip{display:flex;height:5px}.strip i{flex:1}
.hero{padding:34px 0 8px}.eyebrow{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#124A96;margin:0 0 8px}
h1{text-wrap:balance;font-size:32px;line-height:1.15;margin:0 0 12px;font-weight:700;letter-spacing:-.01em}.lead{color:#3A4D5C;margin:0 0 6px;font-size:18px}
.paths{display:grid;gap:12px;margin:22px 0 6px}
a.path{display:block;background:#fff;border:1px solid #D5DEE5;border-radius:14px;padding:18px 18px 16px;text-decoration:none;color:#13202B;box-shadow:0 1px 2px rgba(23,50,79,.06);border-left:6px solid {BLUE}}
a.path:active,a.path:hover{background:#F0F8FF}
a.path h2{margin:0 0 4px;font-size:21px;font-weight:700;display:flex;justify-content:space-between;align-items:center}a.path h2 span{color:{BLUE};font-size:24px;line-height:1}
a.path p{margin:0;color:#3A4D5C;font-size:16px}a.path em{display:inline-block;margin-top:10px;font-style:normal;font-size:13px;font-weight:600;color:#124A96;background:#D9F0FF;border-radius:6px;padding:3px 9px}
.tip{color:#5A6670;font-size:14px;margin:14px 0 0;text-align:center}
.how{margin:34px 0 0;padding-top:26px;border-top:1px solid #D5DEE5}.how h3{font-size:19px;margin:0 0 4px}.how>p{margin:0 0 14px;color:#3A4D5C;font-size:16px}
.how ul.bl{list-style:none;margin:0;padding:0;display:grid;gap:8px}.how .bl li{display:grid;grid-template-columns:auto 1fr;column-gap:12px;align-items:center;background:#fff;border:1px solid #D5DEE5;border-left:6px solid var(--c);border-radius:10px;padding:9px 14px}
.how .bl li b{grid-row:span 2;min-width:34px;text-align:center;background:var(--c);color:#13202B;border-radius:6px;padding:3px 8px;font-size:13px}.how .bl li span{font-weight:600;font-size:16px}.how .bl li small{color:#5A6670;font-size:13.5px;line-height:1.35}
.facts{display:flex;gap:8px;margin:18px 0 0;flex-wrap:wrap}.facts div{background:#E6F6FF;border-radius:10px;padding:8px 12px;font-size:14px;color:#3A4D5C}.facts b{display:block;font-size:20px;color:#13202B;line-height:1.1}
.steps{list-style:none;margin:0;padding:0;display:grid;gap:10px;counter-reset:s}.steps li{counter-increment:s;display:grid;grid-template-columns:34px 1fr;gap:12px;align-items:start;font-size:16px;color:#3A4D5C}.steps li::before{content:counter(s);width:34px;height:34px;border-radius:50%;background:{BLUE};color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}.steps b{color:#13202B;display:block}.start{margin:34px 0 0;padding-top:26px;border-top:1px solid #D5DEE5}.start h3{font-size:19px;margin:0 0 4px}.start>p{margin:0 0 12px;color:#3A4D5C;font-size:16px}.ages{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.ages a{background:#fff;border:1px solid #D5DEE5;border-radius:10px;padding:12px 0;text-align:center;text-decoration:none;color:#13202B;font-weight:700}.ages a:hover{background:#F0F8FF}footer .credit{margin:0 0 4px}
footer{margin:34px 0 0;padding:16px 0 30px;border-top:1px solid #D5DEE5;font-size:14px;color:#5A6670}footer a{color:#5A6670}
</style></head><body>
<header><div class="wrap"><img src="{LOGO}" alt=""><div><b>Coach Craft</b><small>Season planner</small></div></div></header>
<div class="strip"><i style="background:#BCA8F0"></i><i style="background:#66C4FF"></i><i style="background:#66F4FF"></i><i style="background:#ADEBB3"></i><i style="background:#FFC067"></i></div>
<main class="wrap">
<section class="hero"><p class="eyebrow">Youth soccer, coach to coach</p><h1>Ideas for your season, one week at a time</h1><p class="lead">Suggested sessions and how-tos for every activity, in one shared language.</p></section>
<div class="paths">
<a class="path" href="rec.html"><h2>Rec planner <span>&rsaquo;</span></h2><p>Pick your age group and get a season of sessions, week by week.</p><em>U6 to U14 rec</em></a>
<a class="path" href="comp.html"><h2>Comp planner <span>&rsaquo;</span></h2><p>Build a competitive season across all five blocks, with the activities to run it.</p><em>U14 comp</em></a>
</div>
<p class="tip">Tip: save this page to your phone's home screen so it opens like an app.</p>
<section class="how"><h3>How it works</h3><ol class="steps"><li><span><b>Pick your planner</b>Rec or comp, then your age group.</span></li><li><span><b>Open this week's session</b>Each week has a short plan and the activities to run.</span></li><li><span><b>Run it, then adjust</b>Every activity has setup, coaching points and how to make it easier or harder.</span></li></ol></section>
<section class="start"><h3>New to coaching? Start here</h3><p>Open the Coach Companion for your age group. It is a short guide with a season plan and sessions.</p><div class="ages"><a href="../../U6_Coach_Companion.html">U6</a><a href="../../U8_Coach_Companion.html">U8</a><a href="../../U10_Coach_Companion.html">U10</a><a href="../../U12_Coach_Companion.html">U12</a><a href="../../U14_Coach_Companion.html">U14</a></div></section>
<section class="how"><h3>Every session is built from five blocks</h3><p>Plan the season by block, so players build skills in an order that makes sense.</p><ul class="bl">{ROWS}</ul>
<div class="facts"><div><b>{N_ACT}</b>activities</div><div><b>{N_REC}</b>rec age plans</div><div><b>{N_COMP}</b>comp plan</div></div></section>
<footer><p class="credit">Designed by Coach Justin Whitaker. Grounded in US Soccer&rsquo;s Player Development Framework.</p><p class="credit">Last updated {UPDATED}</p><p class="credit"><a href="https://tally.so/r/5X9NVQ">Suggest an activity or report a problem</a></p>For authors: <a href="activity-builder.html">Activity Builder</a></footer>
</main></body></html>'''

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
    BC = {'B1': '#BCA8F0', 'B2': '#66C4FF', 'B3': '#66F4FF', 'B4': '#ADEBB3', 'B5': '#FFC067'}
    rows = ''.join(f'<li style="--c:{BC[k]}"><b>{k}</b><span>{data["blocks"][k]["name"]}</span><small>{data["blocks"][k]["group_label"]}</small></li>' for k in ['B1', 'B2', 'B3', 'B4', 'B5'])
    plans = sorted((ROOT / 'data' / 'plans').glob('*.yaml'))
    n_rec = sum(1 for f in plans if f.stem.endswith('-rec')); n_comp = len(plans) - n_rec
    n_act = len(data['activities'])
    root = LANDING.replace('{LOGO}', logo).replace('{ROWS}', rows).replace('{N_ACT}', str(n_act)).replace('{N_REC}', str(n_rec)).replace('{N_COMP}', str(n_comp)).replace('{BLUE}', brand['gold']).replace('{UPDATED}', __import__('datetime').date.today().strftime('%b %-d, %Y'))
    (ROOT / 'build' / 'index.html').write_text(root, encoding='utf-8')
    return out
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'all': print('wrote', *build_all(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BRAND)); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'author': print('wrote', build_author()); sys.exit()
    if len(sys.argv) > 3 and sys.argv[3] == 'app': print('wrote', build_app(sys.argv[1], sys.argv[2])); sys.exit()
    print('wrote', build(sys.argv[1], sys.argv[2]))
