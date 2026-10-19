#!/usr/bin/env python3
"""Generates the space-themed profile: card (dark_mode.svg / light_mode.svg),
mission brief panel and project cards in assets/.

Edit INFO / ART below and run:  python3 generate.py
Optional: python3 generate.py photo.jpg  -> replaces the satellite with an ASCII portrait.
"""
import sys
from html import escape

ART = r"""
              .-.
             ( * )
        ______`-'______
       /      /|\      \
      /______/ | \______\
     |  ||  |  |  |  ||  |
     |  ||  |=[#]=|  ||  |
     |__||__|  |  |__||__|
            \  |  /
         .---\_|_/---.
        /  .-------.  \
       |  /  _____  \  |
       | |  |SAT-1|  | |
       | |  |_____|  | |
       |  \  .---.  /  |
        \  '-'   '-'  /
         '-----------'
          |    |    |
         /|\  /|\  /|\
        ' ' '' ' '' ' '

     ~ 45 km to stratosphere ~
"""

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


def photo_to_ascii(path, cols=40, rows=24):
    from PIL import Image, ImageOps
    ramp = " .:-=+*#%@"
    img = ImageOps.grayscale(Image.open(path))
    img = ImageOps.autocontrast(img).resize((cols, rows))
    px = img.load()
    return "\n".join(
        "".join(ramp[(255 - px[x, y]) * (len(ramp) - 1) // 255] for x in range(cols))
        for y in range(rows)
    )


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



# ── space palette ────────────────────────────────────────────────────────────
P = dict(
    bg0="#04060f", bg1="#0b1030", border="#26305e",
    fg="#e6e9f5", muted="#8f99c2", dots="#4a5585",
    key="#8ab4ff", title="#c4b5fd", section="#ffcf70",
    add="#5eead4", rm="#fb7185",
)
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CH, LH = 9.6, 20  # 16px monospace advance / line height


def defs(uid, w, h):
    return f"""<defs>
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{P['bg0']}"/><stop offset="1" stop-color="{P['bg1']}"/>
  </linearGradient>
  <radialGradient id="neb1{uid}" cx="0.85" cy="0.1" r="0.6">
    <stop offset="0" stop-color="#7c3aed" stop-opacity="0.28"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="neb2{uid}" cx="0.05" cy="0.95" r="0.55">
    <stop offset="0" stop-color="#0ea5e9" stop-opacity="0.18"/><stop offset="1" stop-color="#0ea5e9" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="clip{uid}"><rect width="{w}" height="{h}" rx="16"/></clipPath>
</defs>"""


def starfield(w, h, seed, density=1.0):
    import random
    rnd = random.Random(seed)
    out = []
    for _ in range(int(w * h / 2600 * density)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([0.5, 0.6, 0.7, 0.8, 1.0, 1.2]) if rnd.random() > 0.05 else 1.6
        o = rnd.uniform(0.25, 0.9)
        c = rnd.choice(["#ffffff", "#ffffff", "#ffffff", "#cdd6ff", "#ffe9c4"])
        if rnd.random() < 0.18:  # twinkle
            d = rnd.uniform(2.5, 6.5)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" opacity="{o:.2f}">'
                       f'<animate attributeName="opacity" values="{o:.2f};0.1;{o:.2f}" dur="{d:.1f}s" '
                       f'begin="{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" opacity="{o:.2f}"/>')
    return "".join(out)


def frame(uid, w, h, body, seed, density=1.0):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" font-family="{MONO}">
{defs(uid, w, h)}
<style>text,tspan{{white-space:pre}} .k{{fill:{P['key']}}} .v{{fill:{P['fg']}}} .d{{fill:{P['dots']}}} .t{{fill:{P['title']}}} .s{{fill:{P['section']}}} .a{{fill:{P['add']}}} .r{{fill:{P['rm']}}} .m{{fill:{P['muted']}}}</style>
<g clip-path="url(#clip{uid})">
  <rect width="{w}" height="{h}" fill="url(#bg{uid})"/>
  <rect width="{w}" height="{h}" fill="url(#neb1{uid})"/>
  <rect width="{w}" height="{h}" fill="url(#neb2{uid})"/>
  {starfield(w, h, seed, density)}
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{P['border']}"/>
{body}
</svg>
"""


def card_width(art):
    art_w = max(len(l) for l in art.strip("\n").split("\n"))
    return 25 + (art_w + 4) * CH + WIDTH_CH * CH + 25


def build_card(art, stats):
    art_lines = art.strip("\n").split("\n")
    art_w = max(len(l) for l in art_lines)
    x_info = 25 + (art_w + 4) * CH
    W = WIDTH_CH

    def kv(k, v, width):
        dots = "." * max(2, width - len(k) - len(v) - 3)
        return f'<tspan class="k">{escape(k)}</tspan><tspan class="d">: {dots} </tspan><tspan class="v">{escape(v)}</tspan>'

    rows = list(INFO)
    i = rows.index(("—", "Contact"))
    rows[i:i] = [
        ("—", "GitHub Stats"),
        ("PAIR", (("Repos", f'{fmt(stats["repos"])} {{Contributed: {fmt(stats["contributed"])}}}'),
                  ("Stars", fmt(stats["stars"])))),
        ("PAIR", (("Commits", fmt(stats["commits"])), ("Followers", fmt(stats["followers"])))),
        ("LOC", None),
    ]
    rows.insert(1, ("Uptime", f'{stats["uptime"]} on GitHub'))

    y = 36
    out = [f'<tspan x="{x_info}" y="{y}" class="t" font-weight="bold">{escape(TITLE)}</tspan>'
           f'<tspan class="d"> {"—" * (W - len(TITLE) - 1)}</tspan>']
    for k, v in rows:
        y += LH
        if k is None:
            out.append(f'<tspan x="{x_info}" y="{y}" class="d">.</tspan>')
        elif k == "—":
            line = "— " + v + " "
            out.append(f'<tspan x="{x_info}" y="{y}" class="s">{escape(line)}</tspan>'
                       f'<tspan class="d">{"—" * (W - len(line))}</tspan>')
        elif k == "PAIR":
            (k1, v1), (k2, v2) = v
            rw = len(k2) + len(v2) + 8
            out.append(f'<tspan x="{x_info}" y="{y}" class="d">. </tspan>{kv(k1, v1, W - 5 - rw)}'
                       f'<tspan class="d"> | </tspan>{kv(k2, v2, rw)}')
        elif k == "LOC":
            k1, v1 = "Lines of Code", fmt(stats["loc"])
            tail = f'( +{fmt(stats["add"])}, -{fmt(stats["rem"])} )'
            dots = "." * max(2, W - 2 - len(k1) - 3 - len(v1) - 1 - len(tail))
            out.append(f'<tspan x="{x_info}" y="{y}" class="d">. </tspan><tspan class="k">{k1}</tspan>'
                       f'<tspan class="d">: {dots} </tspan><tspan class="v">{v1} ( </tspan>'
                       f'<tspan class="a">+{fmt(stats["add"])}</tspan><tspan class="v">, </tspan>'
                       f'<tspan class="r">-{fmt(stats["rem"])}</tspan><tspan class="v"> )</tspan>')
        else:
            out.append(f'<tspan x="{x_info}" y="{y}" class="d">. </tspan>{kv(k, v, W - 2)}')
    h = max(y, 36 + LH * len(art_lines)) + 38
    w = card_width(art)
    art_y0 = (h - LH * len(art_lines)) / 2 + 12
    art_svg = "".join(f'<tspan x="25" y="{art_y0 + i * LH:.0f}">{escape(l)}</tspan>'
                      for i, l in enumerate(art_lines))
    body = (f'<text font-size="16" fill="{P["title"]}" opacity="0.92">{art_svg}</text>'
            f'<text font-size="16">{"".join(out)}</text>'
            f'<text x="{w - 25:.0f}" y="{h - 12:.0f}" text-anchor="end" font-size="11" class="m" opacity="0.7">'
            f'last sync {escape(stats["updated"])} · auto-updated every 6h</text>')
    return frame("c", w, h, body, seed=7)


# ── mission brief + onboard systems ──────────────────────────────────────────
BRIEF = ("QA Engineer in the core banking (ABS) team at UZUM Technologies x Kapitalbank: "
         "payment flows, SWIFT messaging, backend checks in SQL / PL/SQL, API testing in Postman. "
         "School 21 graduate (Business Systems Analyst), MIS at Webster University, GPA 3.9/4.0. "
         "Before software I built drones and a student satellite that reached 45 km.")

SYSTEMS = [
    ("Testing", ["Web", "API", "Backend / DB", "Regression", "Test design", "Bug reports"]),
    ("Analysis", ["Requirements", "BPMN 2.0", "UML", "DFD", "ER models", "REST / SOAP specs"]),
    ("Code & Data", ["SQL", "PL/SQL", "Python", "pytest", "requests"]),
    ("Tools", ["Postman", "Swagger", "Jira", "Confluence", "DataGrip", "Git"]),
    ("Hardware", ["Arduino", "Sensors", "Drones", "LiDAR"]),
]


def wrap(text, n):
    import textwrap
    return textwrap.wrap(text, n)


def build_brief(w):
    pad = 32
    cw = 8.4  # 14px mono advance
    y = 44
    parts = [f'<text x="{pad}" y="{y}" font-size="13" class="s" letter-spacing="2">MISSION BRIEF</text>']
    y += 28
    for line in wrap(BRIEF, int((w - 2 * pad) / cw)):
        parts.append(f'<text x="{pad}" y="{y}" font-size="14" class="v">{escape(line)}</text>')
        y += 22
    y += 22
    parts.append(f'<text x="{pad}" y="{y}" font-size="13" class="s" letter-spacing="2">ONBOARD SYSTEMS</text>')
    y += 18
    label_w = 120
    for label, items in SYSTEMS:
        y += 34
        parts.append(f'<text x="{pad}" y="{y}" font-size="13" class="k">{escape(label)}</text>')
        x = pad + label_w
        for it in items:
            tw = len(it) * 7.8 + 22
            if x + tw > w - pad:
                y += 32; x = pad + label_w
            parts.append(f'<rect x="{x:.1f}" y="{y - 17}" width="{tw:.1f}" height="25" rx="12.5" '
                         f'fill="#ffffff" fill-opacity="0.03" stroke="{P["border"]}"/>'
                         f'<text x="{x + tw / 2:.1f}" y="{y}" font-size="13" text-anchor="middle" class="v">{escape(it)}</text>')
            x += tw + 8
    h = y + 34
    return frame("b", w, h, "".join(parts), seed=21, density=0.8)


# ── mission cards (projects) ─────────────────────────────────────────────────
MISSIONS = [
    ("meet-meme-cam", "Google Meet extension that turns faces, gestures and claps into memes the whole call sees.",
     "JavaScript · MediaPipe · WebRTC", "https://github.com/Javharr/meet-meme-cam"),
    ("oracle-sql-reports", "Oracle SQL / PL/SQL reporting queries: the kind of backend checks I run in core banking QA.",
     "PL/SQL · Oracle", "https://github.com/Javharr/oracle-sql-reports"),
    ("Barbershop & Delivery", "End-to-end system analysis across 16 School 21 projects: stakeholders, BPMN, ER, REST/SOAP specs.",
     "BPMN 2.0 · UML · draw.io", "https://github.com/Javharr/javhar-portfolio"),
    ("MockMate", "AI mock interview platform for practising technical and behavioural interviews.",
     "Next.js · AI", "https://mockmate-swart.vercel.app/"),
    ("Résumé site", "Personal résumé and portfolio: experience, awards, robotics and satellite projects.",
     "React · Vite · Railway", "https://github.com/Javharr/javhar-portfolio"),
    ("Web testing artifacts", "Test cases, checklists, an ISO 29119 test plan and boundary test data for real websites.",
     "Web testing · DevTools", "https://github.com/Javharr/javhar-portfolio"),
]


def build_mission(i, name, desc, stack, w):
    pad, h = 24, 150
    parts = [
        f'<text x="{pad}" y="34" font-size="11" class="s" letter-spacing="2">MISSION {i:02d}</text>',
        f'<circle cx="{w - pad - 4}" cy="30" r="3.5" fill="{P["add"]}"><animate attributeName="opacity" values="1;0.3;1" dur="2.4s" repeatCount="indefinite"/></circle>',
        f'<text x="{pad}" y="62" font-size="18" font-weight="bold" class="v">{escape(name)}</text>',
    ]
    y = 88
    for line in wrap(desc, int((w - 2 * pad) / 7.8))[:2]:
        parts.append(f'<text x="{pad}" y="{y}" font-size="13" class="m">{escape(line)}</text>')
        y += 19
    parts.append(f'<text x="{pad}" y="{h - 18}" font-size="12" class="k">{escape(stack)}</text>')
    return frame(f"m{i}", w, h, "".join(parts), seed=100 + i, density=0.7)


if __name__ == "__main__":
    import os
    art = photo_to_ascii(sys.argv[1]) if len(sys.argv) > 1 else ART
    stats = load_stats()
    card = build_card(art, stats)
    for name in ("dark_mode.svg", "light_mode.svg"):
        open(name, "w", encoding="utf-8").write(card)
    w = card_width(art)
    os.makedirs("assets", exist_ok=True)
    open("assets/brief.svg", "w", encoding="utf-8").write(build_brief(w))
    mw = (w - 16) / 2
    for i, (n, d, s, _) in enumerate(MISSIONS, 1):
        open(f"assets/mission-{i}.svg", "w", encoding="utf-8").write(build_mission(i, n, d, s, mw))
    print("ok")
