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
    ("Company", "UZUM Technologies × Kapitalbank"),
    ("Team", "Core Banking (ABS)"),
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
    "dark_mode.svg": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", dots="#616e7f", accent="#7ee787"),
    "light_mode.svg": dict(bg="#f6f8fa", fg="#24292f", key="#953800", dots="#c2cfde", accent="#116329"),
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


def build(theme, art):
    t = THEMES[theme]
    art_lines = art.strip("\n").split("\n")
    art_w = max(len(l) for l in art_lines)
    ch, lh = 9.6, 20  # char width / line height for 16px monospace
    x_info = 25 + (art_w + 4) * ch

    out = []
    y = 30
    pad = "—" * (WIDTH_CH - len(TITLE) - 1)
    out.append(f'<tspan x="{x_info}" y="{y}" class="acc">{escape(TITLE)}</tspan> <tspan class="dots">{pad}</tspan>')
    for k, v in INFO:
        y += lh
        if k is None:
            out.append(f'<tspan x="{x_info}" y="{y}" class="dots">.</tspan>')
            continue
        if k == "—":
            line = "— " + v + " "
            out.append(f'<tspan x="{x_info}" y="{y}" class="acc">{escape(line)}</tspan>'
                       f'<tspan class="dots">{"—" * (WIDTH_CH - len(line))}</tspan>')
            continue
        dots = "." * max(2, WIDTH_CH - len(k) - len(v) - 5)
        out.append(f'<tspan x="{x_info}" y="{y}">. </tspan><tspan class="key">{escape(k)}</tspan>:'
                   f'<tspan class="dots"> {dots} </tspan><tspan class="val">{escape(v)}</tspan>')
    height = max(y, 30 + lh * len(art_lines)) + 30
    width = x_info + WIDTH_CH * ch + 25

    art_y0 = (height - lh * len(art_lines)) / 2 + 14
    art_svg = "".join(
        f'<tspan x="25" y="{art_y0 + i * lh:.0f}">{escape(l)}</tspan>' for i, l in enumerate(art_lines)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width:.0f}px" height="{height:.0f}px" font-size="16px">
<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
.key {{fill: {t["key"]};}} .val {{fill: {t["fg"]};}} .dots {{fill: {t["dots"]};}} .acc {{fill: {t["accent"]};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{width:.0f}px" height="{height:.0f}px" fill="{t["bg"]}" rx="15"/>
<text fill="{t["fg"]}" class="ascii">{art_svg}</text>
<text fill="{t["fg"]}">{"".join(out)}</text>
</svg>
'''


if __name__ == "__main__":
    art = photo_to_ascii(sys.argv[1]) if len(sys.argv) > 1 else ART
    for name in THEMES:
        with open(name, "w", encoding="utf-8") as f:
            f.write(build(name, art))
        print("wrote", name)
