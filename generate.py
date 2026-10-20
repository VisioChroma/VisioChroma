#!/usr/bin/env python3
"""
Fox README v3 - quiet luxury edition.
  python generate.py --demo            sample data preview
  GITHUB_TOKEN=.. GH_USER=.. python generate.py
Writes dist/: hero.svg tile_about.svg tile_stack.svg tile_now.svg tile_stats.svg skyline.svg
"""
import base64, json, os, random, sys, datetime as dt, urllib.request
from pathlib import Path

# ───────────── EDIT ME ─────────────
USERNAME   = os.environ.get("GH_USER") or "VisioChroma"
NAME       = os.environ.get("GH_NAME") or "Sai Krishna Siddu"
KICKER     = "Computer Science · JNTUH"
TAGLINE    = "Ideas should be made visible."
META       = ["UI/UX", "AI applications", "Visual design"]
ABOUT_HEAD = ["Ideas into things", "people can use."]
ABOUT_SUB  = ["CS student at JNTUH. Software, AI apps,", "and the visual side: UI/UX, motion, comics."]
STACK      = ["Rust", "Python", "HTML", "AI apps", "UI/UX", "Motion"]
NOW_HEAD   = ["Working on", "Msword_opensource"]
NOW_SUB    = "Written in Rust."
SKY_WEEKS  = 18
# ───────────────────────────────────

# 70 / 20 / 10
STAGE, STAGE2 = "#101012", "#18181B"                 # 70%  graphite
CARD, STONE, LINE = "#1D1D21", "#2C2B2F", "#3A383B"  # 20%  stone neutrals
BONE, MUTED = "#EFE9DE", "#8F8B84"                   # 20%  type
COPPER, SAND = "#C9843F", "#DDB98C"                  # 10%  the fox + one accent
INK = "#101012"
FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI Variable Display','Segoe UI','Helvetica Neue',Arial,sans-serif"

A = Path(__file__).parent / "assets"
def uri(n): return "data:image/webp;base64," + base64.b64encode((A/f"{n}.webp").read_bytes()).decode()
def darken(h, f):
    h = h.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r*f), int(g*f), int(b*f))
LEVEL_SPRITE = ["s_0", "s_1", "s_2", "s_3", "s_4"]
LEVEL_BIG    = ["mR_sleep", "mR_neutral", "mR_laugh", "mR_heart", "mR_stars"]
LEVEL_NAME   = ["napping", "awake", "cheerful", "smitten", "starstruck"]
LEVEL_COL    = ["#2A2A2F", "#3E3D42", "#6A6056", "#A8693A", "#D6A267"]
def GRAD(i, c1=BONE, c2=SAND, c3=COPPER):
    return (f'<linearGradient id="{i}" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset=".6" stop-color="{c2}"/><stop offset="1" stop-color="{c3}"/></linearGradient>')

# ───────────── data ─────────────
def fetch():
    q = "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount contributionLevel}}}}}}"
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"u": USERNAME}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"})
    wk = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    lv = {"NONE":0,"FIRST_QUARTER":1,"SECOND_QUARTER":2,"THIRD_QUARTER":3,"FOURTH_QUARTER":4}
    return [[(d["date"], d["contributionCount"], lv[d["contributionLevel"]]) for d in w["contributionDays"]] for w in wk]
def demo():
    random.seed(11); end = dt.date.today(); d = end - dt.timedelta(days=(end.weekday()+1)%7 + 7*52); weeks = []
    while d <= end:
        w = []
        for _ in range(7):
            if d > end: break
            n = 0 if random.random() < .33 else int(random.expovariate(1/5))
            if d.weekday() >= 5 and random.random() < .5: n = 0
            w.append((d.isoformat(), n, 0 if n==0 else 1 if n<3 else 2 if n<6 else 3 if n<10 else 4)); d += dt.timedelta(days=1)
        weeks.append(w)
    return weeks
def stats(weeks):
    days = [x for w in weeks for x in w]
    total = sum(c for _,c,_ in days); best = max(days, key=lambda x: x[1]); streak = 0
    for k, (dte, c, _) in enumerate(reversed(days)):
        if c == 0 and k == 0: continue
        if c == 0: break
        streak += 1
    return dict(total=total, best=best[1], best_date=best[0], streak=streak, today=days[-1][2])

# ───────────── shared bits ─────────────
def noise(id_, w, h, op=.07):
    return (f'<filter id="{id_}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 .97  0 0 0 0 .92  0 0 0 {op} 0"/></filter>'), f'<rect width="{w}" height="{h}" filter="url(#{id_})"/>'
def gaze(frames, x, y, size, dur_each=.9, prefix="md_"):
    out = ""
    for i in range(9):
        vals = ";".join("1" if s == i else "0" for s in frames) + ";" + ("1" if frames[0]==i else "0")
        if "1" not in vals: continue
        out += (f'<image href="{uri(f"{prefix}{i}")}" x="{x}" y="{y}" width="{size}" height="{size}" opacity="0">'
                f'<animate attributeName="opacity" values="{vals}" dur="{dur_each*len(frames)}s" calcMode="discrete" repeatCount="indefinite"/></image>')
    return out
def reveal(begin, dur=.9, rise=26):
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{dur}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 {rise}" to="0 0" begin="{begin}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>')

# ───────────── HERO ─────────────
def hero(weeks):
    W, H = 830, 746
    size = min(108, int(770 / (len(NAME) * .55)))
    cx, cy, R0 = 415, 496, 142
    days = [x for w in weeks for x in w][-90:]
    LEN = [4, 11, 21, 33, 46]
    COL = ["#3B393C", "#5F5A52", "#8F7F6B", "#BE8A56", "#E4B27C"]
    bars = ""
    for k, (_, _, l) in enumerate(days):
        ang = k * 360 / len(days)
        last = k == len(days) - 1
        col = BONE if last else COL[l]
        bars += (f'<line x1="{cx}" y1="{cy-R0}" x2="{cx}" y2="{cy-R0}" transform="rotate({ang:.2f} {cx} {cy})" stroke="{col}" stroke-width="4.4" stroke-linecap="round">'
                 f'<animate attributeName="y2" from="{cy-R0}" to="{cy-R0-LEN[l]-(8 if last else 0)}" begin="{2.0+k*.022:.2f}s" dur=".55s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></line>')
    ticks = "".join(f'<line x1="{cx}" y1="{cy-R0+14}" x2="{cx}" y2="{cy-R0+(22 if k%6==0 else 18)}" transform="rotate({k*6} {cx} {cy})" stroke="{BONE}" stroke-opacity="{.28 if k%6==0 else .12}" stroke-width="1.2"/>' for k in range(60))
    nf, nrule = noise("n1", W, H, .05)
    parts = [m if k == 0 else f'<tspan fill="{COPPER}" dx="16">•</tspan><tspan dx="16">{m}</tspan>' for k, m in enumerate(META)]
    meta = f'<text x="{W/2}" y="274" text-anchor="middle" font-family="{FONT}" font-size="14" letter-spacing="1.3" fill="{MUTED}">' + "".join(parts) + "</text>"
    fox = gaze([4,4,5,4,2,4,3,4,8,4], cx-120, cy-104, 240, 1.0, "hd_")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{STAGE}"/><stop offset="1" stop-color="{STAGE2}"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BONE}" stop-opacity=".12"/><stop offset=".6" stop-color="{BONE}" stop-opacity=".03"/><stop offset="1" stop-color="{BONE}" stop-opacity="0"/></radialGradient>
<radialGradient id="warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{COPPER}" stop-opacity=".16"/><stop offset="1" stop-color="{COPPER}" stop-opacity="0"/></radialGradient>
<radialGradient id="disc" cx=".5" cy=".38" r=".7"><stop offset="0" stop-color="#3A383B"/><stop offset=".6" stop-color="#232225"/><stop offset="1" stop-color="#171718"/></radialGradient>
<linearGradient id="nm" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="{BONE}"/><stop offset="1" stop-color="#BDB5A6"/></linearGradient>
<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="240" y2="0" gradientTransform="translate(-300 0)">
  <stop offset="0" stop-color="{SAND}" stop-opacity="0"/><stop offset=".5" stop-color="{SAND}" stop-opacity=".9"/><stop offset="1" stop-color="{SAND}" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-300 0;{W+60} 0" dur="2.6s" begin="3.2s;shn.end+7s" id="shn"/></linearGradient>
<linearGradient id="hand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SAND}" stop-opacity=".0"/><stop offset="1" stop-color="{SAND}" stop-opacity=".55"/></linearGradient>
<filter id="bl" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="18"><animate attributeName="stdDeviation" from="18" to="0" begin=".5s" dur="1.6s" fill="freeze"/></feGaussianBlur></filter>
<clipPath id="nc"><text x="{W/2}" y="186" text-anchor="middle" font-family="{FONT}" font-size="{size}" font-weight="700" letter-spacing="-3">{NAME}</text></clipPath>
<clipPath id="dc"><circle cx="{cx}" cy="{cy}" r="129"/></clipPath>
{nf}
</defs>
<rect width="{W}" height="{H}" rx="30" fill="url(#bg)"/>
<ellipse cx="{cx}" cy="{cy}" rx="400" ry="300" fill="url(#glow)"/>
<ellipse cx="{cx}" cy="{cy+30}" rx="230" ry="200" fill="url(#warm)"><animate attributeName="opacity" values=".6;1;.6" dur="7s" repeatCount="indefinite"/></ellipse>
{nrule}
<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin=".9s" dur="1.2s" fill="freeze"/>{ticks}
  <circle cx="{cx}" cy="{cy}" r="{R0-4}" fill="none" stroke="{BONE}" stroke-opacity=".10"/></g>
<g opacity="0">{reveal(1.0, 1.4, 30)}
  <circle cx="{cx}" cy="{cy}" r="132" fill="url(#disc)" stroke="{BONE}" stroke-opacity=".16" stroke-width="1.2"/>
  <g clip-path="url(#dc)">{fox}</g>
  <circle cx="{cx}" cy="{cy}" r="129" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="6" style="mix-blend-mode:multiply"/>
</g>
{bars}
<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="3.4s" dur="1s" fill="freeze"/>
  <rect x="{cx-.75}" y="{cy-R0-58}" width="1.5" height="58" fill="url(#hand)"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="16s" repeatCount="indefinite"/></rect></g>
<g opacity="0"><text x="{cx}" y="{cy+R0+82}" text-anchor="middle" font-family="{FONT}" font-size="13" letter-spacing="1.4" fill="{MUTED}">THE LAST 90 DAYS, ONE LINE PER DAY</text><animate attributeName="opacity" from="0" to=".9" begin="3.6s" dur="1s" fill="freeze"/></g>
<g opacity="0"><text x="{W/2}" y="78" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="500" fill="{COPPER}" letter-spacing="2.5">{KICKER}</text>{reveal(.2,1,10)}</g>
<g opacity="0" filter="url(#bl)">
  <text x="{W/2}" y="186" text-anchor="middle" font-family="{FONT}" font-size="{size}" font-weight="700" letter-spacing="-3" fill="url(#nm)">{NAME}</text>
  <g clip-path="url(#nc)"><rect x="0" y="50" width="{W}" height="160" fill="url(#shine)"/></g>
  <animate attributeName="opacity" from="0" to="1" begin=".5s" dur="1.2s" fill="freeze"/></g>
<g opacity="0"><text x="{W/2}" y="232" text-anchor="middle" font-family="{FONT}" font-size="24" fill="{MUTED}">{TAGLINE}</text>{reveal(1.5,1,14)}</g>
<g opacity="0">{meta}<animate attributeName="opacity" from="0" to="1" begin="2s" dur="1s" fill="freeze"/></g>
</svg>'''

# ───────────── TILES ─────────────
def tile(w, h, inner, bg=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><linearGradient id="tb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#202024"/><stop offset="1" stop-color="#141416"/></linearGradient>
{GRAD("hg")}<linearGradient id="bn" x1="0" x2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C9C2B4"/></linearGradient>
<radialGradient id="rg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BONE}" stop-opacity=".10"/><stop offset="1" stop-color="{BONE}" stop-opacity="0"/></radialGradient>
<clipPath id="cp"><rect width="{w}" height="{h}" rx="28"/></clipPath></defs>
<g clip-path="url(#cp)"><rect width="{w}" height="{h}" fill="url(#tb)"/>{bg}{inner}</g>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="28" fill="none" stroke="#fff" stroke-opacity=".08"/></svg>'''
def kicker(t, x=38, y=56): return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="15" font-weight="600" letter-spacing=".6" fill="{COPPER}">{t}</text>'

def tile_about():
    head = "".join(f'<text x="38" y="{108+i*38}" font-family="{FONT}" font-size="29" font-weight="700" letter-spacing="-.6" fill="{"url(#hg)" if i else "url(#bn)"}">{t}</text>' for i, t in enumerate(ABOUT_HEAD))
    sub = "".join(f'<text x="38" y="{220+i*22}" font-family="{FONT}" font-size="15" fill="{MUTED}">{t}</text>' for i, t in enumerate(ABOUT_SUB))
    fox = (f'<circle cx="466" cy="250" r="130" fill="url(#rg)"/>'
           f'<image href="{uri("mR_laugh")}" x="372" y="126" width="190" height="190"><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="4s" repeatCount="indefinite"/></image>')
    return tile(540, 270, kicker("About") + head + sub + fox)
def tile_stack():
    chips, x, y = "", 38, 86
    for s in STACK:
        w = 34 + len(s) * 8.4
        if x + w > 250: x, y = 38, y + 44
        chips += (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="34" rx="17" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".14"/>'
                  f'<circle cx="{x+17}" cy="{y+17}" r="3" fill="{COPPER}"/><text x="{x+28}" y="{y+22}" font-family="{FONT}" font-size="14.5" font-weight="500" fill="{BONE}">{s}</text>')
        x += w + 8
    return tile(270, 270, kicker("Toolkit") + chips)
def tile_now():
    head = "".join(f'<text x="38" y="{100+i*30}" font-family="{FONT}" font-size="23" font-weight="700" fill="url(#bn)">{t}</text>' for i, t in enumerate(NOW_HEAD))
    sub = f'<text x="38" y="162" font-family="{FONT}" font-size="14" fill="{MUTED}">{NOW_SUB}</text>'
    fox = f'<circle cx="150" cy="270" r="110" fill="url(#rg)"/>' + gaze([3,3,0,3,4,4,3,1], 112, 178, 170, .9)
    return tile(270, 270, kicker("Right now") + head + sub + fox)
def tile_stats(S):
    big = lambda x, n, lab: (f'<text x="{x}" y="150" font-family="{FONT}" font-size="64" font-weight="700" letter-spacing="-2" fill="url(#bn)">{n}</text>'
                             f'<text x="{x+2}" y="178" font-family="{FONT}" font-size="14" fill="{MUTED}">{lab}</text>')
    nums = big(38, f"{S['total']:,}", "contributions") + big(238, S["streak"], "day streak")
    mood = (f'<circle cx="448" cy="250" r="140" fill="url(#rg)"/>'
            f'<image href="{uri(LEVEL_BIG[S["today"]])}" x="348" y="112" width="200" height="200"><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="3.4s" repeatCount="indefinite"/></image>')
    foot = f'<text x="38" y="236" font-family="{FONT}" font-size="15" fill="{BONE}">Today the fox is <tspan font-weight="700" fill="{COPPER}">{LEVEL_NAME[S["today"]]}</tspan>.</text>'
    return tile(540, 270, kicker("This season") + nums + foot + mood)

# ───────────── SKYLINE ─────────────
def hull(pts):
    pts = sorted(set(pts))
    def cross(o, p, q): return (p[0]-o[0])*(q[1]-o[1]) - (p[1]-o[1])*(q[0]-o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

def skyline(weeks, S):
    weeks = weeks[-SKY_WEEKS:]; n = len(weeks)
    a, b, W = 31, 14, 830
    ox = (W - (n + 8) * a) / 2 + 7.5 * a; oy = 292; H = 800
    HT = [4, 20, 42, 70, 104]
    ang = __import__("math").degrees(__import__("math").atan2(b, a))
    P = lambda u, v: (ox + (u - v) * a, oy + (u + v) * b)
    c = [P(-.75, -.75), P(n - .25, -.75), P(n - .25, 6.75), P(-.75, 6.75)]
    f = lambda pts: " ".join(f"{x:.1f},{y:.1f}" for x, y in pts); t = 20
    left = f([c[3], c[2], (c[2][0], c[2][1]+t), (c[3][0], c[3][1]+t)])
    right = f([c[2], c[1], (c[1][0], c[1][1]+t), (c[2][0], c[2][1]+t)])
    grid = "".join(f'<line x1="{P(i-.5,-.75)[0]:.1f}" y1="{P(i-.5,-.75)[1]:.1f}" x2="{P(i-.5,6.75)[0]:.1f}" y2="{P(i-.5,6.75)[1]:.1f}"/>' for i in range(0, n + 1)) + \
           "".join(f'<line x1="{P(-.75,j-.5)[0]:.1f}" y1="{P(-.75,j-.5)[1]:.1f}" x2="{P(n-.25,j-.5)[0]:.1f}" y2="{P(n-.25,j-.5)[1]:.1f}"/>' for j in range(0, 8))
    slab = (f'<polygon points="{left}" fill="#19191C"/><polygon points="{right}" fill="#131315"/>'
            f'<polygon points="{f(c)}" fill="url(#slab)" stroke="#fff" stroke-opacity=".10"/>'
            f'<g stroke="#fff" stroke-opacity=".035" stroke-width="1">{grid}</g>')
    # axis labels
    lab, last_m = "", None
    for i, w in enumerate(weeks):
        m = dt.date.fromisoformat(w[0][0]).strftime("%b")
        if m != last_m:
            x, y = P(i, 7.55); lab += f'<text x="{x:.1f}" y="{y:.1f}" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" font-family="{FONT}" font-size="12" letter-spacing=".6" fill="{MUTED}">{m}</text>'
        last_m = m
    for j, nme in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        x, y = P(n + .05, j); lab += f'<text x="{x:.1f}" y="{y:.1f}" transform="rotate({-ang:.1f} {x:.1f} {y:.1f})" font-family="{FONT}" font-size="12" letter-spacing=".6" fill="{MUTED}">{nme}</text>'
    items = sorted((i + j, i, j, lvl, cnt, date) for i, w in enumerate(weeks) for j, (date, cnt, lvl) in enumerate(w))
    today = (len(weeks) - 1, len(weeks[-1]) - 1); s_ = a * 1.5
    peak = max(items, key=lambda x: x[4])
    shadows, towers, callout = "", "", ""
    for k, i, j, lvl, cnt, date in items:
        cx, cy = P(i, j); h = HT[lvl]; aa, bb = a * .92, b * .92; col = LEVEL_COL[lvl]
        if lvl >= 2:
            base = [(cx-aa, cy), (cx, cy-bb), (cx+aa, cy), (cx, cy+bb)]
            off = [(x + h*.95, y + h*.42) for x, y in base]
            shadows += f'<polygon points="{f(hull(base+off))}"/>'
        faces = (f'<polygon points="{cx-aa:.1f},{cy:.1f} {cx:.1f},{cy+bb:.1f} {cx:.1f},{cy+bb-h:.1f} {cx-aa:.1f},{cy-h:.1f}" fill="{darken(col,.76)}"/>'
                 f'<polygon points="{cx+aa:.1f},{cy:.1f} {cx:.1f},{cy+bb:.1f} {cx:.1f},{cy+bb-h:.1f} {cx+aa:.1f},{cy-h:.1f}" fill="{darken(col,.5)}"/>'
                 f'<polygon points="{cx:.1f},{cy-bb-h:.1f} {cx+aa:.1f},{cy-h:.1f} {cx:.1f},{cy+bb-h:.1f} {cx-aa:.1f},{cy-h:.1f}" fill="{col}"/>'
                 f'<polyline points="{cx-aa:.1f},{cy-h:.1f} {cx:.1f},{cy+bb-h:.1f} {cx+aa:.1f},{cy-h:.1f}" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1"/>')
        ss = s_ * (.74 if lvl == 0 else 1)
        fox = f'<use href="#f{lvl}" x="{cx-ss/2:.1f}" y="{cy-h-ss+bb*.66:.1f}" width="{ss:.1f}" height="{ss:.1f}" opacity="{.5 if lvl==0 else 1}"/>'
        isT = (i, j) == today
        halo = f'<ellipse cx="{cx:.1f}" cy="{cy-h:.1f}" rx="{a*1.4:.0f}" ry="{b*1.6:.0f}" fill="{SAND}" opacity=".16"/>' if isT else ""
        tag = ""
        if isT:
            ty = cy - h - s_ - 2
            tag = (f'<g><rect x="{cx-28:.1f}" y="{ty-18:.1f}" width="56" height="23" rx="11.5" fill="{BONE}"/><text x="{cx:.1f}" y="{ty-2.5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12.5" font-weight="600" fill="{INK}">Today</text>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="2.2s" repeatCount="indefinite"/></g>')
        d = .3 + (i + j) * .05
        towers += (f'<g opacity="0">{halo}{faces}{fox}{tag}<animate attributeName="opacity" from="0" to="1" begin="{d:.2f}s" dur=".4s" fill="freeze"/>'
                   f'<animateTransform attributeName="transform" type="translate" from="0 50" to="0 0" begin="{d:.2f}s" dur=".75s" fill="freeze" calcMode="spline" keySplines=".2 .9 .25 1" keyTimes="0;1"/></g>')
        if (k, i, j) == (peak[0], peak[1], peak[2]) and cnt > 0:
            side = 1 if cx < W / 2 else -1
            x0, y0 = cx, cy - h - s_ * .95
            x1, y1 = cx + side * 44, y0 - 78
            nice = dt.date.fromisoformat(date).strftime("%b %-d")
            anc = "start" if side == 1 else "end"
            callout = (f'<g opacity="0"><polyline points="{x0:.1f},{y0:.1f} {x1:.1f},{y1:.1f} {x1+side*34:.1f},{y1:.1f}" fill="none" stroke="{BONE}" stroke-opacity=".5"/>'
                       f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="2.5" fill="{BONE}"/>'
                       f'<text x="{x1+side*42:.1f}" y="{y1+1:.1f}" text-anchor="{anc}" font-family="{FONT}" font-size="14" font-weight="600" fill="{BONE}">Peak day</text>'
                       f'<text x="{x1+side*42:.1f}" y="{y1+19:.1f}" text-anchor="{anc}" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{cnt} contributions, {nice}</text>'
                       f'<animate attributeName="opacity" from="0" to="1" begin="3.2s" dur=".8s" fill="freeze"/></g>')
    defs = "".join(f'<symbol id="f{l}" viewBox="0 0 96 96"><image href="{uri(LEVEL_SPRITE[l])}" width="96" height="96"/></symbol>' for l in range(5))
    # bottom: stats + legend
    sy = H - 84
    def stat(x, num, label): return (f'<text x="{x}" y="{sy}" font-family="{FONT}" font-size="34" font-weight="700" letter-spacing="-1" fill="url(#bn)">{num}</text>'
                                     f'<text x="{x}" y="{sy+24}" font-family="{FONT}" font-size="13" fill="{MUTED}">{label}</text>')
    stats_row = stat(48, f"{S['total']:,}", "contributions") + stat(214, S["streak"], "day streak") + stat(350, S["best"], "best single day")
    stats_row += f'<g stroke="#fff" stroke-opacity=".10"><line x1="190" y1="{sy-30}" x2="190" y2="{sy+26}"/><line x1="326" y1="{sy-30}" x2="326" y2="{sy+26}"/></g>'
    leg, lx = "", W - 48 - 5 * 56
    for l in range(5):
        leg += (f'<image href="{uri(LEVEL_SPRITE[l])}" x="{lx+8}" y="{sy-40}" width="40" height="40" opacity="{.75 if l==0 else 1}"/>'
                f'<text x="{lx+28}" y="{sy+24}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{MUTED}">{LEVEL_NAME[l]}</text>')
        lx += 56
    nf, nrule = noise("n2", W, H, .05)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{defs}{GRAD("hg")}{nf}
<linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{STAGE}"/><stop offset="1" stop-color="{STAGE2}"/></linearGradient>
<linearGradient id="slab" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#242428"/><stop offset="1" stop-color="#151517"/></linearGradient>
<linearGradient id="bn" x1="0" x2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C9C2B4"/></linearGradient>
<radialGradient id="g2" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BONE}" stop-opacity=".11"/><stop offset="1" stop-color="{BONE}" stop-opacity="0"/></radialGradient>
<radialGradient id="g3" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{COPPER}" stop-opacity=".12"/><stop offset="1" stop-color="{COPPER}" stop-opacity="0"/></radialGradient>
<filter id="sb" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3.5"/></filter></defs>
<rect width="{W}" height="{H}" rx="30" fill="url(#bg2)"/>
<ellipse cx="{W/2}" cy="{oy+210}" rx="470" ry="270" fill="url(#g2)"/><ellipse cx="{W/2+60}" cy="{oy+260}" rx="300" ry="150" fill="url(#g3)"/>{nrule}
<text x="48" y="84" font-family="{FONT}" font-size="44" font-weight="700" letter-spacing="-1.5" fill="url(#bn)">Every commit, a taller fox.</text>
<text x="48" y="118" font-family="{FONT}" font-size="18" fill="{MUTED}">Each day is a fox. Height and mood follow how much I shipped.</text>
{slab}{lab}<g fill="#000" fill-opacity=".34" filter="url(#sb)">{shadows}</g>{towers}{callout}
<line x1="48" y1="{sy-52}" x2="{W-48}" y2="{sy-52}" stroke="#fff" stroke-opacity=".08"/>
{stats_row}{leg}
</svg>'''

if __name__ == "__main__":
    out = Path(__file__).parent / "dist"; out.mkdir(exist_ok=True)
    weeks = demo() if "--demo" in sys.argv else fetch(); S = stats(weeks)
    for name, svg in [("hero", hero(weeks)), ("tile_about", tile_about()), ("tile_stack", tile_stack()),
                      ("tile_now", tile_now()), ("tile_stats", tile_stats(S)), ("skyline", skyline(weeks, S))]:
        (out / f"{name}.svg").write_text(svg)
    print("ok")
