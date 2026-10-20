#!/usr/bin/env python3
"""Profile card: neofetch-style info on the right, an animated ASCII Earth with an orbiting Moon on the left.

Run:  python3 generate.py   ->  dark_mode.svg, light_mode.svg
Stats come from the GitHub GraphQL API when GITHUB_TOKEN is set (GitHub Actions), otherwise from stats.json.
"""
import math
from html import escape

TITLE = "javhar@bokhodirov"
WIDTH_CH = 58  # width of the info column, in characters

# (key, value) ; key None = blank line ; ("—", "Section") = section header
INFO = [
    ("OS", "macOS, Linux, Windows"),
    ("Host", "Tashkent, Uzbekistan"),
    ("Kernel", "QA Engineer · Business Systems Analyst"),
    ("Company", "UZUM Tech × Kapitalbank · ABS"),
    ("Domain", "Payments, SWIFT, Scrum"),
    (None, None),
    ("Languages.Code", "SQL, PL/SQL, Python"),
    ("Languages.Modeling", "BPMN 2.0, UML, DFD, ER"),
    ("Languages.Real", "English C1, Russian, Uzbek"),
    ("Tools", "Postman, Swagger, Jira, DataGrip"),
    (None, None),
    ("Education.Uni", "Webster Univ. · MIS · GPA 3.9/4.0"),
    ("Education.School21", "Business Systems Analyst"),
    ("Hobbies.Hardware", "Drones, Satellites, Arduino"),
    ("—", "Awards"),
    ("Intl STEM, Ankara '23", "1st / 150+ teams"),
    ("MoD STEM Festival '24", "1st / 50+ teams"),
    ("Code for Change '25", "Best Implementation"),
    ("—", "Contact"),
    ("Email", "bohodirovjavhar@gmail.com"),
    ("Telegram", "@javxarr"),
    ("LinkedIn", "javhar-bokhodirov"),
]

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", dots="#616e7f", accent="#7ee787", add="#3fb950", rm="#f85149",
                          o0="#1b2b45", o1="#1f4f99", o2="#2f72d6", o3="#58a6ff", l0="#173a22", l1="#238636", l2="#2ea043", l3="#56d364",
                          m0="#3d444d", m1="#6e7681", m2="#9da7b3", m3="#e6edf3", orb="#3d444d", st="#8b949e", tk="#ffa657"),
    "light_mode.svg": dict(bg="#f6f8fa", fg="#24292f", key="#953800", dots="#c2cfde", accent="#116329", add="#1a7f37", rm="#cf222e",
                           o0="#d8e0ea", o1="#9ec5fe", o2="#4493f8", o3="#0969da", l0="#c6e6cf", l1="#6fdd8b", l2="#2da44e", l3="#116329",
                           m0="#d0d7de", m1="#afb8c1", m2="#6e7781", m3="#24292f", orb="#d0d7de", st="#afb8c1", tk="#bc4c00"),
}

FRAMES, SECONDS = 90, 18          # one earth spin and one moon orbit per loop
STILL = 0.85                       # frame shown when the viewer prefers reduced motion
CAPTION = "~ hello from 41.3°N ~"
TASHKENT = (69.24, 41.31)

import math

LAND = {
 "north_america": [(-168,66),(-162,70),(-156,71),(-140,70),(-128,70),(-115,68),(-100,68),(-95,72),(-85,70),(-80,63),(-90,58),(-94,59),(-82,52),(-78,55),(-77,62),(-70,60),(-64,60),(-56,52),(-60,47),(-66,44),(-70,42),(-76,38),(-76,35),(-81,31),(-80,25),(-82,27),(-84,30),(-90,29),(-97,27),(-97,22),(-92,18),(-87,21),(-88,16),(-84,11),(-80,8),(-78,8),(-83,8),(-86,12),(-92,14),(-96,16),(-105,20),(-106,23),(-110,24),(-112,29),(-114,31),(-117,32),(-121,35),(-124,40),(-124,46),(-123,49),(-130,54),(-135,58),(-142,60),(-150,60),(-155,57),(-163,55),(-158,58),(-165,60),(-166,63)],
 "greenland": [(-73,78),(-60,82),(-30,83),(-20,80),(-18,75),(-22,70),(-32,68),(-42,60),(-50,62),(-54,67),(-58,75),(-68,77)],
 "south_america": [(-80,9),(-75,11),(-72,12),(-62,11),(-52,5),(-50,0),(-44,-2),(-35,-5),(-35,-9),(-39,-15),(-40,-22),(-48,-26),(-53,-34),(-58,-38),(-62,-39),(-65,-45),(-68,-50),(-69,-55),(-74,-52),(-75,-45),(-73,-37),(-71,-30),(-70,-18),(-76,-14),(-81,-6),(-80,-1),(-78,2),(-77,7)],
 "eurasia": [(-10,36),(-9,43),(-2,44),(-5,48),(2,51),(8,54),(9,57),(5,62),(14,67),(20,70),(28,71),(40,67),(45,68),(55,69),(60,70),(70,73),(80,73),(95,76),(105,78),(115,74),(130,72),(140,72),(150,71),(160,70),(170,69),(180,68),(180,65),(178,64),(170,60),(163,58),(160,54),(156,51),(156,57),(150,59),(142,59),(137,54),(141,52),(140,48),(135,43),(130,42),(129,35),(126,35),(126,38),(122,40),(122,37),(119,35),(121,31),(122,30),(119,25),(115,22),(110,21),(108,18),(106,11),(105,9),(103,10),(100,13),(100,8),(103,1),(101,3),(98,8),(98,16),(94,17),(92,22),(90,22),(86,20),(80,16),(80,10),(77,8),(73,16),(72,21),(68,24),(62,25),(57,26),(56,24),(59,22),(52,17),(44,12),(43,15),(39,21),(35,28),(34,31),(35,36),(30,36),(27,37),(26,40),(23,40),(22,37),(19,40),(18,42),(13,45),(12,44),(15,40),(16,38),(12,38),(10,44),(3,43),(0,39),(-2,37),(-6,36)],
 "africa": [(-17,21),(-17,15),(-15,11),(-13,8),(-8,4),(-3,5),(5,6),(9,4),(10,1),(9,-2),(12,-6),(13,-12),(12,-17),(15,-27),(18,-34),(20,-35),(26,-34),(31,-29),(33,-25),(35,-22),(40,-15),(40,-10),(39,-5),(42,0),(46,3),(51,11),(44,11),(43,13),(39,16),(35,23),(33,28),(32,31),(25,32),(20,31),(15,32),(11,33),(10,37),(3,37),(-2,35),(-6,36),(-10,30),(-13,27)],
 "madagascar": [(44,-25),(47,-25),(50,-15),(49,-12),(44,-16)],
 "australia": [(114,-22),(114,-26),(115,-34),(118,-35),(124,-34),(131,-31),(135,-35),(138,-35),(140,-38),(146,-39),(150,-37),(153,-30),(153,-25),(146,-19),(145,-15),(142,-11),(141,-17),(136,-15),(137,-12),(131,-11),(126,-14),(122,-17)],
 "uk": [(-5,50),(1,51),(2,53),(-2,56),(-2,58),(-6,58),(-5,55),(-3,54),(-5,52)],
 "japan": [(130,31),(132,34),(136,34),(140,35),(141,38),(142,43),(145,44),(141,45),(140,41),(139,38),(136,36),(132,35)],
 "sumatra": [(95,5),(98,4),(104,-2),(106,-6),(102,-4),(97,1)],
 "borneo": [(109,1),(111,-3),(116,-4),(118,1),(119,6),(116,7),(113,3)],
 "new_guinea": [(131,-1),(138,-2),(145,-5),(150,-10),(141,-9),(138,-8),(132,-4)],
 "java": [(105,-6),(114,-7),(114,-8.5),(106,-7.5)],
 "iceland": [(-24,64),(-14,64),(-14,66.5),(-22,66.5)],
 "new_zealand": [(172,-34),(178,-38),(175,-41),(171,-46),(167,-46),(172,-40)],
}

def _inside(lon, lat, poly):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c

# 2° land grid, computed once
GRID = [[lat < -66 or any(_inside(lon, lat, p) for p in LAND.values())
         for lon in range(-180, 180, 2)] for lat in range(90, -90, -2)]

def is_land(lon, lat):
    r = min(89, max(0, int((90 - lat) / 2)))
    c = int(((lon + 180) % 360) / 2) % 180
    return GRID[r][c]

# ── earth & moon ─────────────────────────────────────────────────────────
W, H = 50, 21            # canvas, chars
CX, CY = 25, 10.5        # earth centre (cols, rows)
R = 7.4                  # earth radius in rows (cols = 2*R)
MR = 1.75                # moon radius in rows
ORBIT_A, ORBIT_B = 22.0, 3.4   # orbit semi-axes (cols, rows)
TILT = math.radians(23.4)
LIGHT = (-0.62, -0.35, 0.70)   # sun: left, slightly above, towards viewer
_n = math.sqrt(sum(v * v for v in LIGHT)); LIGHT = tuple(v / _n for v in LIGHT)
STARS = [(2, 1, "."), (10, 0, "+"), (44, 1, "."), (48, 7, "*"), (1, 13, "+"), (6, 19, "."),
         (42, 19, "."), (48, 15, "+"), (16, 20, "."), (33, 0, "."), (3, 7, ".")]

def _shade(b):
    return 0 if b <= 0.04 else 1 if b < 0.35 else 2 if b < 0.65 else 3

def frame(t):
    """t in [0,1): one earth spin and one moon orbit per loop. Returns grid of (char, cls)."""
    grid = [[(" ", "") for _ in range(W)] for _ in range(H)]
    earth = [[False] * W for _ in range(H)]
    for x, y, ch in STARS:
        grid[y][x] = (ch, "st")
    spin = -t * 2 * math.pi
    th = t * 2 * math.pi
    # orbit path, far half only (near half is drawn after the earth)
    path = []
    for k in range(0, 360, 4):
        a = math.radians(k)
        x = int(round(CX + ORBIT_A * math.cos(a))); y = int(round(CY - ORBIT_B * math.sin(a)))
        if 0 <= x < W and 0 <= y < H:
            path.append((x, y, math.sin(a) > 0))
    for x, y, far in path:
        if far: grid[y][x] = ("·", "or")
    # earth
    for row in range(H):
        for col in range(W):
            nx = (col + 0.5 - CX) / (2 * R); ny = (row + 0.5 - CY) / R
            d = nx * nx + ny * ny
            if d > 1: continue
            nz = math.sqrt(1 - d)
            x1 = nx * math.cos(TILT) - ny * math.sin(TILT)
            y1 = nx * math.sin(TILT) + ny * math.cos(TILT)
            lat = math.degrees(math.asin(max(-1.0, min(1.0, -y1))))
            lon = (math.degrees(math.atan2(x1, nz) + spin) + 180) % 360 - 180
            b = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            s = _shade(b)
            if is_land(lon, lat):
                grid[row][col] = ("#" if s else ".", f"l{s}")
            else:
                grid[row][col] = (":" if s else ".", f"o{s}")
            earth[row][col] = True
    # Tashkent: nearest visible cell on the day or night side
    best = None
    for row in range(H):
        for col in range(W):
            if not earth[row][col]: continue
            nx = (col + 0.5 - CX) / (2 * R); ny = (row + 0.5 - CY) / R
            nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            x1 = nx * math.cos(TILT) - ny * math.sin(TILT); y1 = nx * math.sin(TILT) + ny * math.cos(TILT)
            lat = math.degrees(math.asin(max(-1.0, min(1.0, -y1))))
            lon = (math.degrees(math.atan2(x1, nz) + spin) + 180) % 360 - 180
            dl = (lon - TASHKENT[0] + 180) % 360 - 180
            dist = math.hypot(dl * math.cos(math.radians(lat)), lat - TASHKENT[1])
            if nz > 0.25 and dist < 6 and (best is None or dist < best[0]): best = (dist, row, col)
    if best: grid[best[1]][best[2]] = ("*", "tk")
    for x, y, far in path:
        if not far and not earth[y][x]: grid[y][x] = ("·", "or")
    # moon: hidden where it is behind the earth
    mx = CX + ORBIT_A * math.cos(th); my = CY - ORBIT_B * math.sin(th)
    behind = math.sin(th) > 0
    for row in range(H):
        for col in range(W):
            nx = (col + 0.5 - mx) / (2 * MR); ny = (row + 0.5 - my) / MR
            d = nx * nx + ny * ny
            if d > 1 or (behind and earth[row][col]): continue
            nz = math.sqrt(1 - d)
            b = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            s = _shade(b)
            grid[row][col] = ("@" if s == 3 else "%" if s == 2 else "o" if s == 1 else ".", f"m{s}")
    return grid



def fetch_stats(user="Javharr"):
    """Live numbers from the GitHub GraphQL API (needs GITHUB_TOKEN). Returns None offline."""
    import os, json, urllib.request, datetime
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return None

    def gql(query, **variables):
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query, "variables": variables}).encode(),
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
        )
        data = json.load(urllib.request.urlopen(req))
        if "errors" in data:
            raise RuntimeError(data["errors"])
        return data["data"]

    u = gql("""query($login:String!){ user(login:$login){
        id createdAt followers{totalCount}
        repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100, isFork:false){
          totalCount nodes{ name stargazerCount defaultBranchRef{name} } }
        repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY], first:1){totalCount}
        contributionsCollection{ contributionYears } } }""", login=user)["user"]

    commits = contributions = 0
    for y in u["contributionsCollection"]["contributionYears"]:
        c = gql("""query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
            contributionsCollection(from:$from,to:$to){ totalCommitContributions restrictedContributionsCount
              contributionCalendar{totalContributions} } } }""",
                login=user, **{"from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"})
        cc = c["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"]
        contributions += cc["contributionCalendar"]["totalContributions"]

    add = rem = 0
    for r in u["repositories"]["nodes"]:
        if not r["defaultBranchRef"]:
            continue
        cursor = None
        while True:
            h = gql("""query($owner:String!,$name:String!,$id:ID!,$after:String){ repository(owner:$owner,name:$name){
                defaultBranchRef{ target{ ... on Commit { history(first:100, after:$after, author:{id:$id}){
                  pageInfo{hasNextPage endCursor} nodes{additions deletions} } } } } } }""",
                    owner=user, name=r["name"], id=u["id"], after=cursor)
            hist = h["repository"]["defaultBranchRef"]["target"]["history"]
            for n in hist["nodes"]:
                add += n["additions"]; rem += n["deletions"]
            if not hist["pageInfo"]["hasNextPage"]:
                break
            cursor = hist["pageInfo"]["endCursor"]

    since = datetime.date.fromisoformat(u["createdAt"][:10])
    today = datetime.date.today()
    months = (today.year - since.year) * 12 + today.month - since.month - (today.day < since.day)
    return dict(
        repos=u["repositories"]["totalCount"],
        contributed=u["repositoriesContributedTo"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        followers=u["followers"]["totalCount"],
        commits=commits, contributions=contributions,
        loc=add - rem, add=add, rem=rem,
        uptime=", ".join(p for p in (
            f"{months // 12} year{'s' * (months // 12 != 1)}" if months >= 12 else "",
            f"{months % 12} month{'s' * (months % 12 != 1)}" if months % 12 or months < 12 else "",
        ) if p),
        updated=today.isoformat(),
    )


def load_stats():
    import json, os
    cache = "stats.json"
    try:
        s = fetch_stats()
    except Exception as e:  # network / rate limit: keep last good numbers
        print("stats fetch failed:", e); s = None
    if s:
        json.dump(s, open(cache, "w"), indent=2)
        return s
    if os.path.exists(cache):
        return json.load(open(cache))
    return dict(repos="—", contributed="—", stars="—", followers="—", commits="—",
                contributions="—", loc="—", add="—", rem="—", uptime="—", updated="—")


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)




def render_frame(grid, y0, x0):
    """One <text> per frame; colour runs become <tspan class>."""
    rows = []
    for i, r in enumerate(grid):
        cells = [(c, k) for c, k in r]
        while cells and cells[-1][0] == " ": cells.pop()
        parts, cur, buf = [], None, ""
        for c, k in cells:
            k = k or "sp"
            if c == " ": k = cur or "sp"
            if k != cur and buf:
                parts.append(f'<tspan class="{cur}">{escape(buf)}</tspan>' if cur != "sp" else escape(buf)); buf = ""
            cur = k; buf += c
        if buf: parts.append(f'<tspan class="{cur}">{escape(buf)}</tspan>' if cur != "sp" else escape(buf))
        if parts: rows.append(f'<tspan x="{x0}" y="{y0 + i * LH:.0f}">{"".join(parts)}</tspan>')
    return "".join(rows)


CH, LH = 9.6, 20


def build(theme, stats, frames):
    t = THEMES[theme]
    W_INFO = WIDTH_CH
    x_info = 25 + (W + 2) * CH

    def kv(k, v, width):
        dots = "." * max(2, width - len(k) - len(v) - 3)
        return (f'<tspan class="key">{escape(k)}</tspan>:<tspan class="dots"> {dots} </tspan>'
                f'<tspan class="val">{escape(v)}</tspan>')

    rows = list(INFO)
    i = rows.index(("—", "Contact"))
    rows[i:i] = [
        ("—", "GitHub Stats"),
        ("PAIR", (("Repos", f'{fmt(stats["repos"])} {{Contributed: {fmt(stats["contributed"])}}}'), ("Stars", fmt(stats["stars"])))),
        ("PAIR", (("Commits", fmt(stats["commits"])), ("Followers", fmt(stats["followers"])))),
        ("LOC", None),
    ]
    rows.insert(1, ("Uptime", f'{stats["uptime"]} on GitHub'))

    out = []
    y = 30
    out.append(f'<tspan x="{x_info}" y="{y}" class="acc">{escape(TITLE)}</tspan> <tspan class="dots">{"—" * (W_INFO - len(TITLE) - 1)}</tspan>')
    for k, v in rows:
        y += LH
        if k is None:
            out.append(f'<tspan x="{x_info}" y="{y}" class="dots">.</tspan>')
        elif k == "—":
            line = "— " + v + " "
            out.append(f'<tspan x="{x_info}" y="{y}" class="acc">{escape(line)}</tspan><tspan class="dots">{"—" * (W_INFO - len(line))}</tspan>')
        elif k == "PAIR":
            (k1, v1), (k2, v2) = v
            rw = len(k2) + len(v2) + 8
            out.append(f'<tspan x="{x_info}" y="{y}">. </tspan>{kv(k1, v1, W_INFO - 5 - rw)}<tspan class="dots"> | </tspan>{kv(k2, v2, rw)}')
        elif k == "LOC":
            k1, v1 = "Lines of Code", fmt(stats["loc"])
            tail = f'( +{fmt(stats["add"])}, -{fmt(stats["rem"])} )'
            dots = "." * max(2, W_INFO - 2 - len(k1) - 3 - len(v1) - 1 - len(tail))
            out.append(f'<tspan x="{x_info}" y="{y}">. </tspan><tspan class="key">{k1}</tspan>:<tspan class="dots"> {dots} </tspan>'
                       f'<tspan class="val">{v1} ( </tspan><tspan class="add">+{fmt(stats["add"])}</tspan><tspan class="val">, </tspan>'
                       f'<tspan class="rm">-{fmt(stats["rem"])}</tspan><tspan class="val"> )</tspan>')
        else:
            out.append(f'<tspan x="{x_info}" y="{y}">. </tspan>{kv(k, v, W_INFO - 2)}')
    height = y + 34
    width = x_info + W_INFO * CH + 25

    art_h = (H + 2) * LH
    y0 = (height - art_h) / 2 + 14
    step = SECONDS / FRAMES
    still = int(STILL * FRAMES) % FRAMES
    groups = []
    for n, grid in enumerate(frames):
        delay = n * step - SECONDS
        groups.append(f'<text class="f{" s" if n == still else ""}" style="animation-delay:{delay:.2f}s">{render_frame(grid, y0, 25)}</text>')
    cap_x = 25 + (W * CH - len(CAPTION) * CH) / 2
    caption = f'<text x="{cap_x:.0f}" y="{y0 + (H + 1) * LH:.0f}" class="dots">{escape(CAPTION)}</text>'
    upd = (f'<text x="{width - 25:.0f}" y="{height - 10:.0f}" text-anchor="end" font-size="11px" class="dots">'
           f'updated {escape(str(stats["updated"]))} · auto-refreshed by GitHub Actions</text>')
    colors = " ".join(f'.{k}{{fill:{t[k]}}}' for k in ("o0", "o1", "o2", "o3", "l0", "l1", "l2", "l3", "m0", "m1", "m2", "m3", "tk"))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width:.0f}px" height="{height:.0f}px" font-size="16px">
<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
.key {{fill: {t["key"]};}} .val {{fill: {t["fg"]};}} .dots {{fill: {t["dots"]};}} .acc {{fill: {t["accent"]};}} .add {{fill: {t["add"]};}} .rm {{fill: {t["rm"]};}}
.or {{fill: {t["orb"]};}} .st {{fill: {t["st"]};}} {colors}
text, tspan {{white-space: pre;}}
.f {{visibility: hidden; animation: spin {SECONDS}s step-end infinite;}}
@keyframes spin {{ 0% {{visibility: visible;}} {100 / FRAMES:.4f}% {{visibility: hidden;}} 100% {{visibility: hidden;}} }}
@media (prefers-reduced-motion: reduce) {{ .f {{animation: none;}} .s {{visibility: visible;}} }}
</style>
<rect width="{width:.0f}px" height="{height:.0f}px" fill="{t["bg"]}" rx="15"/>
{"".join(groups)}
{caption}
<text fill="{t["fg"]}">{"".join(out)}</text>
{upd}
</svg>
'''


if __name__ == "__main__":
    stats = load_stats()
    frames = [frame(n / FRAMES) for n in range(FRAMES)]
    for name in THEMES:
        with open(name, "w", encoding="utf-8") as f:
            f.write(build(name, stats, frames))
        print("wrote", name)
