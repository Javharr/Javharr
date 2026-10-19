#!/usr/bin/env python3
"""Generates dark_mode.svg and light_mode.svg — a neofetch-style profile card.

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
    ("Education.Uni", "Webster Univ. · MIS · GPA 3.9"),
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
    "dark_mode.svg": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", dots="#616e7f", accent="#7ee787", add="#3fb950", rm="#f85149"),
    "light_mode.svg": dict(bg="#f6f8fa", fg="#24292f", key="#953800", dots="#c2cfde", accent="#116329", add="#1a7f37", rm="#cf222e"),
}


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
        uptime=f"{months // 12} years, {months % 12} months",
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


def build(theme, art, stats):
    t = THEMES[theme]
    art_lines = art.strip("\n").split("\n")
    art_w = max(len(l) for l in art_lines)
    ch, lh = 9.6, 20  # char width / line height for 16px monospace
    x_info = 25 + (art_w + 4) * ch
    W = WIDTH_CH

    def kv(k, v, width):
        dots = "." * max(2, width - len(k) - len(v) - 3)
        return (f'<tspan class="key">{escape(k)}</tspan>:<tspan class="dots"> {dots} </tspan>'
                f'<tspan class="val">{escape(v)}</tspan>')

    rows = list(INFO)
    rows[rows.index(("—", "Contact")):rows.index(("—", "Contact"))] = [
        ("—", "GitHub Stats"),
        ("PAIR", (("Repos", f'{fmt(stats["repos"])} {{Contributed: {fmt(stats["contributed"])}}}'),
                  ("Stars", fmt(stats["stars"])))),
        ("PAIR", (("Commits", fmt(stats["commits"])), ("Followers", fmt(stats["followers"])))),
        ("LOC", None),
    ]
    rows.insert(1, ("Uptime", f'{stats["uptime"]} on GitHub'))

    out = []
    y = 30
    out.append(f'<tspan x="{x_info}" y="{y}" class="acc">{escape(TITLE)}</tspan> '
               f'<tspan class="dots">{"—" * (W - len(TITLE) - 1)}</tspan>')
    for k, v in rows:
        y += lh
        if k is None:
            out.append(f'<tspan x="{x_info}" y="{y}" class="dots">.</tspan>')
        elif k == "—":
            line = "— " + v + " "
            out.append(f'<tspan x="{x_info}" y="{y}" class="acc">{escape(line)}</tspan>'
                       f'<tspan class="dots">{"—" * (W - len(line))}</tspan>')
        elif k == "PAIR":
            (k1, v1), (k2, v2) = v
            left = W - 2 - 3 - (len(k2) + len(v2) + 8)
            out.append(f'<tspan x="{x_info}" y="{y}">. </tspan>{kv(k1, v1, left)}'
                       f'<tspan class="dots"> | </tspan>{kv(k2, v2, len(k2) + len(v2) + 8)}')
        elif k == "LOC":
            tail = f'( +{fmt(stats["add"])}, -{fmt(stats["rem"])} )'
            v1 = fmt(stats["loc"])
            k1 = "Lines of Code"
            dots = "." * max(2, W - 2 - len(k1) - 3 - len(v1) - 1 - len(tail))
            out.append(f'<tspan x="{x_info}" y="{y}">. </tspan><tspan class="key">{k1}</tspan>:'
                       f'<tspan class="dots"> {dots} </tspan><tspan class="val">{v1}</tspan> '
                       f'<tspan class="val">( </tspan><tspan class="add">+{fmt(stats["add"])}</tspan>'
                       f'<tspan class="val">, </tspan><tspan class="del">-{fmt(stats["rem"])}</tspan>'
                       f'<tspan class="val"> )</tspan>')
        else:
            out.append(f'<tspan x="{x_info}" y="{y}">. </tspan>{kv(k, v, W - 2)}')
    height = max(y, 30 + lh * len(art_lines)) + 30
    width = x_info + W * ch + 25

    art_y0 = (height - lh * len(art_lines)) / 2 + 14
    art_svg = "".join(
        f'<tspan x="25" y="{art_y0 + i * lh:.0f}">{escape(l)}</tspan>' for i, l in enumerate(art_lines)
    )
    upd = (f'<text x="{width - 25:.0f}" y="{height - 10:.0f}" text-anchor="end" font-size="11px" '
           f'class="dots">updated {escape(stats["updated"])} · auto-refreshed by GitHub Actions</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width:.0f}px" height="{height:.0f}px" font-size="16px">
<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
.key {{fill: {t["key"]};}} .val {{fill: {t["fg"]};}} .dots {{fill: {t["dots"]};}} .acc {{fill: {t["accent"]};}}
.add {{fill: {t["add"]};}} .del {{fill: {t["rm"]};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{width:.0f}px" height="{height:.0f}px" fill="{t["bg"]}" rx="15"/>
<text fill="{t["fg"]}" class="ascii">{art_svg}</text>
<text fill="{t["fg"]}">{"".join(out)}</text>
{upd}
</svg>
'''


if __name__ == "__main__":
    art = photo_to_ascii(sys.argv[1]) if len(sys.argv) > 1 else ART
    stats = load_stats()
    for name in THEMES:
        with open(name, "w", encoding="utf-8") as f:
            f.write(build(name, art, stats))
        print("wrote", name)
