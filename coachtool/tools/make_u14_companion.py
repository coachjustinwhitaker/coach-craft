#!/usr/bin/env python3
"""Build U14_Coach_Companion.html from the U12 page shell + coachtool U14 rec data."""
import re, html, yaml, pathlib

ROOT = pathlib.Path('/home/claude/coach-craft-repo')
D = ROOT / 'coachtool' / 'data'
y = lambda p: yaml.safe_load((D / p).read_text())

age = y('ages/u14-rec.yaml')
plan = y('plans/u14-rec.yaml')
fw = y('framework/u14.yaml')
pl = y('players/u14.yaml')
goals = y('goals/u14.yaml')
acts = {p.stem: yaml.safe_load(p.read_text()) for p in (D / 'activities').glob('*.yaml')}

def e(t):
    return html.escape(str(t).strip(), quote=False).replace('"', '&quot;') if False else html.escape(str(t).strip(), quote=False)

def txt(t):
    """escape + curly quotes + no em dashes"""
    t = str(t).strip().replace('—', ':').replace(' -- ', ': ')
    t = html.escape(t, quote=False)
    t = re.sub(r'"([^"]*)"', r'&ldquo;\1&rdquo;', t)
    t = t.replace("'", '&rsquo;')
    return t

def flat(v):
    if isinstance(v, list): v = ' '.join(str(x).strip() for x in v)
    v = re.sub(r'a field about 25 by 20 yards at U8, 30 by 25 at U10, and 35 by 30 at U12 and U14', 'a field about 35 by 30 yards', str(v))
    return v

def A(aid):
    a = dict(acts[aid])
    over = (a.get('for_age') or {}).get('u14') or {}
    a.update(over)
    return a

BLOCK_NAME = {'B1': 'Me & the Ball', 'B2': 'Me & My Teammates', 'B3': 'Me & My Team Defending',
              'B4': 'Me & the Game', 'B5': 'Me & the Moment'}

# ---- shell from U12 ----
u12 = (ROOT / 'U12_Coach_Companion.html').read_text()
head = u12[:u12.index('<div class="header-content">')].replace('U12 Coach Companion', 'U14 Coach Companion')
tail_i = u12.index('<div class="section gold-tint">\n  <div class="eyebrow">Questions?')
tail = u12[tail_i:]
tail = tail.replace('U12 Coach Companion &nbsp;&middot;&nbsp; All four focuses', 'U14 Coach Companion &nbsp;&middot;&nbsp; All five focuses')
tail = tail.replace('Next: U14 &nbsp;&middot;&nbsp; + Me &amp; the Moment &nbsp;&middot;&nbsp; 11v11', 'Next: the next level')

# extra css for the fifth block
extra_css = """<style>
/* U14 additions */
.bt-moment{background:#B36B00;}
.skill-group-bar.moment{background:#FFE9C2!important;border-left-color:var(--b5)!important}
.block-band-grid{grid-template-columns:repeat(auto-fit,minmax(135px,1fr))}
.four-grid{grid-template-columns:repeat(2,1fr)}
@media(max-width:560px){.four-grid{grid-template-columns:1fr}}
</style>
"""
head = head.replace('</head>', extra_css + '</head>', 1)

out = []
w = out.append

# ---- header ----
w('''<div class="header-content">
    <div class="club-label">Coach Craft &nbsp;|&nbsp; Player Development Methodology</div>
    <h1>U14 Coach Companion
      <span class="blocks">Me &amp; the Ball &nbsp;&middot;&nbsp; Me &amp; My Teammates &nbsp;&middot;&nbsp; Me &amp; My Team Defending &nbsp;&middot;&nbsp; Me &amp; the Game &nbsp;&middot;&nbsp; Me &amp; the Moment</span>
    </h1>
    <div class="header-meta">Progression Phase I &nbsp;&middot;&nbsp; 11v11 &nbsp;&middot;&nbsp; 2 Practices Per Week &nbsp;&middot;&nbsp; Recreational</div>
    <div class="header-duration">
      <strong>Session Length:</strong><span>Up to 90 minutes total &nbsp;&middot;&nbsp; Arrive 15 minutes early</span>
    </div>
  </div>
</div>
<div class="philosophy">
  <p>The field got big. <em>Eleven against eleven means shape matters as much as skill.</em> The players in front of you can reason now, they care what their teammates think, and they want a say. Your job this season is to give them real problems to solve in games they enjoy, then step back when they solve them. Enjoy watching them take ownership.</p>
</div>''')

# ---- what each focus means ----
cells = [
    ('B1', 'Growth Phase', 'Scanning, first touch, body shape and playing forward. Players know these habits and now use them at full-game speed with a defender closing fast. Every player does this, in every position.'),
    ('B2', 'Growth Phase', 'Support angles, wall passes and moving after the pass. New this season is timing: a run that arrives when the ball does, not early and not late.'),
    ('B3', 'Reinforced', 'Pressure, cover and balance with eleven. The nearest player pressures, a teammate covers behind, and the team stays close enough to stay connected. Forwards defend too.'),
    ('B4', 'Reinforced', 'The first second after the ball changes hands. Press or recover when you lose it. Play forward or keep it when you win it.'),
    ('B5', 'Introduced', 'Finishing: separating to receive, a final pass, and a composed shot with few touches. New at U14 and the focus of weeks 4 to 6.'),
]
w('<div class="block-band">\n  <div class="eyebrow" style="color:var(--gold);">What Each Focus Means at U14</div>\n  <div class="block-band-grid">')
for b, st, d in cells:
    w(f'    <div class="block-cell">\n      <div class="block-cell-name">{e(BLOCK_NAME[b]).replace("&amp;","&amp;")}</div>\n      <div class="block-cell-status">{st}</div>\n      <div class="block-cell-desc">{txt(d)}</div>\n    </div>')
w('  </div>\n</div>')

# ---- US soccer alignment ----
w('''<div class="section tinted">
  <div class="eyebrow navy">US Soccer Alignment</div>
  <div class="section-heading">Progression Phase I &nbsp;&middot;&nbsp; 11v11 Format</div>
  <p style="font-size:12.5px;margin-top:8px;max-width:780px;">At U14, US Soccer&rsquo;s Progression Phase I expects players to play within a formation with defined roles, and adds new objectives like midfield interchange and quick combination play in tight spaces under high pressure. For a recreational team, take the spirit and keep it light. Teach the shape of the team and the habits that go with it, and let players try different spots across the season. Finishing joins the first four focuses as a fifth. All five run at the Introduction level.</p>
  <div class="two-col" style="margin-top:14px;">
    <div class="info-box navy-left"><h4>What This Season Keeps Simple</h4>Introduction level in all five focuses. The habits every player needs in every position. No fixed roles. Players rotate through lines and positions, because identity at this age is still forming.</div>
    <div class="info-box gold-left"><h4>What a Competitive Program Adds</h4>Development and Application levels, where the same ideas run at full game speed and then by function: who combines together, who presses together, who finishes. Press triggers, center backs stepping into midfield and role-specific work all live there.</div>
  </div>
</div>''')

# ---- who is in front of you ----
who = {x['label']: x['text'] for x in pl['who']}
cards = [
    ('Growth Is Uneven', who['Growth is uneven'] + ' Sore knees or heels are worth a word with the parent. Rest beats extra reps.'),
    ('The Field Got Big', who['The field got big']),
    ('Peers Matter More Than You', who['Peers matter more than you'] + ' Pushing back is part of building an identity, not disrespect. Give them a say: let players pick a warm-up game or lead one.'),
    ('They Can Think It Through', 'U14 players can reason about why, not just what. Ask &ldquo;what was open?&rdquo; or &ldquo;why did we lose our shape there?&rdquo; and let them answer before you do. A solution they work out themselves sticks.'),
]
w('<div class="section">\n  <div class="eyebrow">Who Is In Front of You</div>\n  <div class="section-heading">Understanding Your U14 Players</div>\n  <div class="four-grid">')
for h, t in cards:
    body = t if '&ldquo;' in t else txt(t)
    w(f'    <div class="info-card"><h4>{h}</h4><p>{body}</p></div>')
w('  </div>\n</div>')

# ---- great session ----
w('<div class="section navy">\n  <div class="eyebrow white">What a Great U14 Session Looks Like</div>\n  <div class="six-grid">')
for g in pl['great_session']:
    w(f'    <div class="success-item"><strong>{txt(g["title"])}</strong><p>{txt(g["text"])}</p></div>')
w('  </div>\n</div>')

# ---- pills ----
perc = {'scanning', 'supporting', 'body-shape', 'covering', 'marking', 'timing-runs'}
w('<div class="section tinted">\n  <div class="eyebrow navy">Teaching Points for This Age Group</div>\n  <div class="section-heading">What You Are Developing</div>\n  <div class="pills">')
pills = []
for p in age['pills']:
    nm = p.replace('-', ' ').title()
    cls = 'perc' if p in perc else 'tech'
    pills.append(f'<span class="pill {cls}">{nm}</span>')
for k in range(0, len(pills), 3):
    w('    ' + ''.join(pills[k:k+3]))
note = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', txt(age['pills_note']))
w(f'  </div>\n  <p class="pills-note">{note}</p>\n</div>')

# ---- before you arrive ----
par = pl['parents']
w(f'''<div class="section">
  <div class="eyebrow">Before You Arrive</div>
  <div class="section-heading">What Prepared Looks Like</div>
  <div class="arrive-box">{txt(pl['prepared'])}</div>
  <div class="sideline-box">
    <div class="eyebrow">The Parents on the Sideline</div>
    <p>{txt(par['intro'])}</p>
    <span class="script">&ldquo;{txt(par['script'])}&rdquo;</span>
    <p style="margin-top:8px;">{txt(par['outro'])}</p>
  </div>
</div>''')

# ---- structure strip ----
sh = pl['shape']
w('''<div class="structure-strip">
  <span class="s-block s-play">Opening Play</span><span class="s-time">12 min</span>
  <span class="s-arrow">&#8594;</span>
  <span class="s-block s-practice">Activity A</span><span class="s-time">15 min</span>
  <span class="s-arrow">&#8594;</span>
  <span class="s-block s-practice">Activity B</span><span class="s-time">15 min</span>
  <span class="s-arrow">&#8594;</span>
  <span class="s-block s-play">Closing Play</span><span class="s-time">25 min</span>
  <span class="pairing-note">A = anchor (familiar) &nbsp;&middot;&nbsp; B = concept focus for the week</span>
</div>''')

# ---- opening play ----
op = sh['opening']
w(f'''<div class="play-section">
  <div class="phase-header">
    <span class="phase-pill play">Opening Play</span>
    <div><div class="phase-title">6v6 or 7v7 &ndash; Free Small-Sided Game</div>
    <div class="phase-sub">Same setup every session. Smaller than the closing game. More touches, more shots and cleaner decisions.</div></div>
  </div>
  <div class="two-col">
    <div class="info-box navy-left"><h4>The Setup</h4>{txt(op['setup'])}</div>
    <div class="info-box gold-left"><h4>Your Job</h4>{txt(op['job'])}</div>
  </div>
  <div class="question-box">
    <span class="q-label">One Question &mdash; Ask it after the opening game</span>
    <span class="q-text">&ldquo;{txt(op['question'])}&rdquo;</span>
  </div>
  <div class="e-tags"><span class="e-tag">{txt(op['kit'])}</span></div>
</div>''')

# ---- activity toolkit ----
opening_ids = []
ab_ids = []
for wk in plan['weeks']:
    if 'opening' in wk:
        opening_ids.append(wk['opening']['activity'])
    for s in wk.get('sessions', []):
        ab_ids += [s['a']['activity'], s['b']['activity']]
def uniq(seq):
    seen = []
    for x in seq:
        if x not in seen: seen.append(x)
    return seen
opening_ids = uniq(opening_ids)
ab_ids = [x for x in uniq(ab_ids) if x not in opening_ids]

TOOLKIT = set(opening_ids) | set(ab_ids)
counter = [0]
def card(aid):
    a = A(aid)
    counter[0] += 1
    coach = a.get('coach') or [{}]
    look = ' '.join(flat(c['cue']) for c in coach if c.get('cue'))
    ask = flat(next((c['ask'] for c in coach if c.get('ask')), ''))
    focus = ' · '.join((a.get('skills') or [])[:3]) + ' · ' + BLOCK_NAME[a['block']]
    pairs = [acts[p]['name'] for p in (a.get('pairs_with') or []) if p in acts and p in TOOLKIT]
    pair_html = f'\n        <span class="pairs-tag">&#8594; Pairs well with: {" or ".join(txt(x) for x in pairs)}</span>' if pairs else ''
    return f'''    <div class="act-card">
      <div class="act-header">
        <div class="act-num">Activity {counter[0]:02d}</div>
        <div class="act-name">{txt(a['name'])}</div>
        <div class="act-focus">{txt(focus)}</div>
      </div>
      <div class="act-body">
        <div class="a-label">Setup</div><div class="a-text">{txt(flat(a.get('setup','')))}</div>
        <div class="a-label">What to Look For</div><div class="a-text">{txt(look)}</div>
        <div class="a-question">&ldquo;{txt(ask)}&rdquo;</div>{pair_html}
        <div class="e-tags" style="margin-top:10px;"><span class="e-tag">{txt(a.get('equipment',''))}</span></div>
      </div>
    </div>'''

w(f'''<div class="practice-section">
  <div class="phase-header">
    <span class="phase-pill practice">Practice</span>
    <div><div class="phase-title">Activity Toolkit &ndash; Pick Two Per Session</div></div>
  </div>
  <p class="practice-intro">Run Activity A for 15 minutes, then Activity B for 15 minutes. A brief transition or water break (&ldquo;good work, new game&rdquo;) resets attention and energy. Follow the season plan for which focus to prioritize each week. The five opening games at the top of the toolkit replace the free small-sided game when a week calls for a challenge built into the play.</p>
  <div class="pairing-rule">
    <strong>The Pairing Rule</strong>
    Try to avoid pairing two new concepts in the same session. Activity A works best as something players already know well enough to run without much explanation. Activity B is where the new concept lives. If the group is flat after Activity A, shorten Activity B or swap it for something more physical.
  </div>''')

w('  <div class="skill-group-bar integration"><span class="skill-group-label">OPENING PLAY &nbsp;&mdash;&nbsp; One added rule sets the challenge before the practice starts</span></div>')
w('  <div class="activity-grid" style="margin-top:14px;">')
for aid in opening_ids: w(card(aid))
w('  </div>')

groups = {}
for aid in ab_ids:
    groups.setdefault(A(aid)['block'], []).append(aid)
bar = {'B1': ('', 'ME &amp; THE BALL'), 'B2': ('', 'ME &amp; MY TEAMMATES'), 'B3': ('defending', 'ME &amp; MY TEAM DEFENDING'),
       'B4': ('game', 'ME &amp; THE GAME'), 'B5': ('moment', 'ME &amp; THE MOMENT')}
sub = {'B1': 'Ball skills at game speed', 'B2': 'Combination play, switching, patience', 'B3': 'Compact shape, first and second defender',
       'B4': 'Both transitions, relentless reaction', 'B5': 'Finishing, final pass, timing the run'}
for b in ['B1', 'B2', 'B3', 'B4', 'B5']:
    if b not in groups: continue
    cls, nm = bar[b]
    w(f'  <div class="skill-group-bar {cls}"><span class="skill-group-label">{nm} &nbsp;&mdash;&nbsp; {sub[b]}</span></div>')
    w('  <div class="activity-grid" style="margin-top:14px;">')
    for aid in groups[b]: w(card(aid))
    w('  </div>')

# closing play
cl = sh['closing']
setup_txt, _, notice = cl['setup'].partition('Watch for the focus')
notice = 'Watch for the focus' + notice
w(f'''  <div class="play-section">
    <div class="phase-header">
      <span class="phase-pill play">Closing Play</span>
      <div><div class="phase-title">11v11 &ndash; Full Game</div>
      <div class="phase-sub">The biggest game of the session. 25 minutes. This is where everything comes together.</div></div>
    </div>
    <div class="two-col">
      <div class="info-box navy-left"><h4>The Setup</h4>{txt(setup_txt)}</div>
      <div class="info-box gold-left"><h4>What to Notice</h4>{txt(notice)}</div>
    </div>
    <div class="question-box">
      <span class="q-label">Closing Question</span>
      <span class="q-text">&ldquo;{txt(cl['question'])}&rdquo;</span>
    </div>
    <div class="e-tags"><span class="e-tag">{txt(cl['kit'])}</span></div>
  </div>
  <div class="gk-note"><strong style="font-family:Inter,Arial,sans-serif;color:var(--navy);font-size:11px;">Goalkeeper:</strong>&nbsp; Every player should experience goalkeeper at some point, and at U14 finishing practice is also goalkeeper practice. Rotate the position so nobody misses a turn. If a player shows genuine enthusiasm for the role, encourage that.</div>
</div>''')

# ---- season plan ----
tag = {'B2': ('bt-establishing', 'Teammates'), 'B3': ('bt-defending', 'Defending'), 'B4': ('bt-game', 'Transitions'),
       'B5': ('bt-moment', 'Finishing')}
w('''<div class="section">
  <div class="eyebrow navy">Season Plan</div>
  <div class="section-heading">Sample Rotation &nbsp;&middot;&nbsp; Two Practices Per Week</div>
  <p style="font-size:12.5px;margin-top:6px;margin-bottom:14px;max-width:780px;">Weeks 1&ndash;2 bring combination play and team defending into the 11v11 environment. Week 3 revisits both transition moments. Weeks 4&ndash;6 introduce and deepen finishing, the new focus at U14. Week 7 integrates all five. Week 8 belongs to you. Each week starts with a small opening game that builds the week&rsquo;s challenge into the play.</p>
  <table class="rotation-table">
    <thead><tr>
      <th style="width:5%">Week</th>
      <th style="width:20%">Focus</th>
      <th style="width:37%">Activity A &mdash; Anchor</th>
      <th>Activity B &mdash; Concept Focus</th>
    </tr></thead>
    <tbody>''')
def cell(s, first=False):
    nm = acts[s['activity']]['name']
    lab = '<span class="prac-label prac-%s">Practice %s</span><br>'
    return nm, s['note']
for wk in plan['weeks']:
    n = wk['week']
    if wk.get('coach_choice'):
        w(f'''      <tr>
        <td class="week-num" style="border-right:2px solid #e0e5f0;">{n}</td>
        <td style="font-style:italic;color:var(--gray-mid);font-size:11.5px;border-right:1px solid #eee;">Coach&rsquo;s choice both days</td>
        <td colspan="2" style="font-style:italic;color:var(--gray-mid);">{txt(wk['note'])}</td>
      </tr>''')
        continue
    if n == 7:
        cls, lab = 'bt-int', 'Integration'
    else:
        cls, lab = tag[wk['block']]
    openline = ''
    if 'opening' in wk:
        o = wk['opening']
        openline = f'<div class="pair-tag" style="margin-top:4px;"><strong>Opening:</strong> {txt(acts[o["activity"]]["name"])}. {txt(o["note"])}</div>'
    for k, s in enumerate(wk['sessions']):
        pa, pb = s['a'], s['b']
        row = 'week-a' if k == 0 else 'week-b'
        w(f'      <tr class="{row}">')
        if k == 0:
            w(f'''        <td rowspan="2" class="week-num" style="vertical-align:middle;border-right:2px solid #e0e5f0;">{n}</td>
        <td rowspan="2" style="vertical-align:middle;border-right:1px solid #eee;"><span class="block-tag-cell {cls}">{lab}</span><div class="pair-tag" style="margin-top:4px;">{txt(wk['focus'])}</div>{openline}</td>''')
        lab_p = 'Practice A' if k == 0 else 'Practice B'
        pc = 'prac-a' if k == 0 else 'prac-b'
        w(f'        <td><span class="prac-label {pc}">{lab_p}</span><br>{txt(acts[pa["activity"]]["name"])}<div class="pair-tag">{txt(pa["note"])}</div></td>')
        w(f'        <td>{txt(acts[pb["activity"]]["name"])}<div class="pair-tag">{txt(pb["note"])}</div></td>')
        w('      </tr>')
w('    </tbody>\n  </table>\n</div>')

# ---- session setup ----
w('''<div class="section gold-tint">
  <div class="eyebrow">Session Setup</div>
  <div class="section-heading">What You'll Need Each Session</div>
  <div class="equip-grid">
    <div class="equip-item"><strong>Balls &mdash; 1 per player (Size 5)</strong><span>Practice activities require one ball per pair minimum.</span></div>
    <div class="equip-item"><strong>Cones &mdash; 60+ per team</strong><span>Half-field marking, practice grids and the box for shooting games. Several grids may run at once.</span></div>
    <div class="equip-item"><strong>Full-size goals &mdash; 2</strong><span>Finishing is the new focus, so players need to shoot at a proper goal with a keeper in it as often as you can manage.</span></div>
    <div class="equip-item"><strong>Pinnies &mdash; Full squad, 3 colors</strong><span>Three colors are useful when more than two teams play at once, and for marking the floater in numbers-up games.</span></div>
    <div class="equip-item"><strong>Small goals &mdash; 4&ndash;6</strong><span>Still needed for several activities even though the closing game uses full-size goals.</span></div>
    <div class="equip-item"><strong>Timer</strong><span>Timed rounds are essential. Competition drives intensity and mirrors the real game.</span></div>
  </div>
</div>''')

# ---- cues ----
w('<div class="section">\n  <div class="eyebrow navy">Coaching Cues</div>\n  <div class="section-heading">What to Watch For and How to Respond</div>\n  <div class="cues-grid">')
for c in pl['cues']:
    say = txt(c['say'])
    w(f'    <div class="cue-card"><strong>{txt(c["when"])}</strong><p>{say}</p></div>')
w('  </div>\n</div>')

# ---- player development ----
w('''<div class="section tinted">
  <div class="eyebrow navy">Player Development</div>
  <div class="section-heading">Where Your Players Will Be</div>
  <p style="font-size:12.5px; color:var(--gray-dark); margin-top:6px; margin-bottom:14px; max-width:780px;">These are the skills we hope to see developing by the end of the season. All players develop at different rates and not every player will show all of these. That is completely normal.</p>
  <p style="font-size:12.5px; color:var(--gray-dark); margin-bottom:14px; max-width:780px;">Finishing is the new piece this season. Let it show up in games, ask about it, and celebrate the brave shot as much as the goal.</p>
  <div class="profile-grid">
    <div class="profile-card primary">
      <h4>Moving on to the Next Level</h4>''')
for g in goals['goals']:
    w(f'      <div class="profile-item">{txt(g["text"])}</div>')
w('''    </div>
    <div class="profile-card comp">
      <h4>A Player Ready for More</h4>
      <div class="profile-item">A few players in your group may be curious about a more competitive pathway</div>
      <div class="profile-item">A competitive program exists to open more doors for those players when they are ready</div>
      <div class="profile-item">Notice them, encourage them, and talk to your club director about what that pathway looks like. Do not promise anything. Just open the door.</div>
    </div>
  </div>
</div>''')

body = '\n'.join(out) + '\n' + tail
page = head + body
(ROOT / 'U14_Coach_Companion.html').write_text(page)
print('wrote', len(page), 'cards', counter[0], 'opening', opening_ids, 'ab', ab_ids)
