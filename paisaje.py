"""Ilustraciones del Valle del Jerte generadas por código (SVG).

Cada curso tiene su estación del valle: cerezo en flor, picota, Otoñada e invierno.
Las laderas llevan bancales de cerezos dibujados como hileras de puntos que siguen
la curva del terreno. Son decorativas: llevan aria-hidden y no necesitan texto alternativo.
"""
import math, random, hashlib

ESTACIONES = {
    'primavera': {'cielo': ('#dce8f2', '#f7f1f3'), 'capas': ('#b4c2d1', '#8aa596', '#62865f', '#3f6646'),
                  'puntos': ('#ffffff', '#f6c9d6', '#f0b3c5'), 'nieve': False, 'sol': '#fff6df'},
    'verano':    {'cielo': ('#cfe2f0', '#f6f1e3'), 'capas': ('#a8b9c9', '#759775', '#4e7652', '#2f5a37'),
                  'puntos': ('#b3123c', '#8c0d2c', '#d22a52'), 'nieve': False, 'sol': '#ffe9b0'},
    'otono':     {'cielo': ('#efdfca', '#f8f0e4'), 'capas': ('#bcae9f', '#c58f4e', '#a95c31', '#6e3b22'),
                  'puntos': ('#e9a83a', '#d06a2c', '#f2c66b'), 'nieve': False, 'sol': '#fde3b8'},
    'invierno':  {'cielo': ('#d9e1ea', '#f1f4f7'), 'capas': ('#c3ccd6', '#8a99a8', '#61717f', '#3e4b56'),
                  'puntos': ('#ffffff', '#e9eef3', '#dfe6ec'), 'nieve': True, 'sol': '#f4f6f8'},
}
POR_CURSO = {'22-23': 'primavera', '23-24': 'verano', '24-25': 'otono', '25-26': 'invierno', '26-27': 'primavera'}
NOMBRE = {'primavera': 'cerezo en flor', 'verano': 'picota', 'otono': 'Otoñada', 'invierno': 'invierno'}


def estacion(curso):
    return POR_CURSO.get(curso or '', 'primavera')


def _rng(semilla):
    return random.Random(int(hashlib.sha1(semilla.encode()).hexdigest()[:12], 16))


def _cresta(r, ancho, base, amp, paso):
    ondas = [(r.uniform(.6, 1.6) / ancho * 2 * math.pi * k, r.uniform(0, 6.28), amp / k) for k in (1, 2.3, 4.7)]
    return [(x, base - sum(a * math.sin(f * x + fase) for f, fase, a in ondas)) for x in range(0, ancho + paso, paso)]


def svg(semilla, curso=None, ancho=1200, alto=240, capas=4, bancales=True, clase='paisaje', tema_sda=None, extra=''):
    est = ESTACIONES[estacion(curso)]
    r = _rng(semilla)
    uid = 'p' + hashlib.sha1(semilla.encode()).hexdigest()[:8]
    paso = max(14, ancho // 60)
    partes = [f'<svg class="{clase}" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">',
              f'<defs><linearGradient id="{uid}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{est["cielo"][0]}"/><stop offset="1" stop-color="{est["cielo"][1]}"/></linearGradient></defs>',
              f'<rect width="{ancho}" height="{alto}" fill="url(#{uid}c)"/>',
              f'<circle cx="{r.uniform(.15, .85) * ancho:.0f}" cy="{alto * .28:.0f}" r="{alto * .13:.0f}" fill="{est["sol"]}" opacity=".9"/>']
    partes.append(motivo(tema_sda, semilla, ancho, alto))
    colores = est['capas'][-capas:]
    for i, color in enumerate(colores):
        base = alto * (.42 + .16 * i)
        amp = alto * (.16 - .025 * i)
        pts = _cresta(r, ancho, base, amp, paso)
        d = 'M0,' + f'{alto} ' + ' '.join(f'L{x},{y:.0f}' for x, y in pts) + f' L{ancho},{alto} Z'
        partes.append(f'<path d="{d}" fill="{color}"/>')
        if bancales and i >= len(colores) - 2:
            # bancales de cerezos: hileras de puntos que siguen la ladera
            sep = max(7, alto // 26)
            filas = 5 if ancho >= 800 else 3
            for fila in range(1, filas + 1):
                desfase = r.uniform(0, sep)
                for x, y in pts:
                    if r.random() < (.5 if ancho >= 800 else .4):
                        cx = x + desfase + r.uniform(-2, 2)
                        cy = y + fila * sep + r.uniform(-1.5, 1.5)
                        if cy < alto - 2:
                            partes.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r.uniform(1.6, 3.2) * max(1, ancho / 900):.1f}" fill="{r.choice(est["puntos"])}"/>')
    partes.append(extra)
    partes.append('</svg>')
    return ''.join(partes)


# ---------- Motivos según el contenido de la SdA ----------
TEMAS = [
    ('tecnologia', r'tecnolog|digitaliz|rob[oó]t|arduino|programaci|scratch|makey|3d|impresora|inteligencia artificial|\bia\b|redes|packet|inform[aá]tic|c[oó]digo|simulaci|sm[r]\b'),
    ('ciencias', r'f[ií]sica|qu[ií]mica|[aá]tomo|at[oó]mic|mol[eé]cul|laboratorio|cern|coloide|corrosi|energ[ií]a|reacci|sustancia'),
    ('matematicas', r'matem[aá]t|geometr|fracci|estad[ií]st|ecuaci|n[uú]mero|fibonacci|funcion|educamatex|probabil|porcentaje|pajitas'),
    ('biologia', r'biolog|bot[aá]nic|planta|huerto|hoja|nutrici|alimentac|saludable|ser vivo|c[eé]lula|mitosis|ecolog|medioambient|natural|jard[ií]n|cajas nido|suplement'),
    ('economia', r'econom|emprend|mercado|empresa|negocio|financ|bolsa|consum|monedas|marketing|retail'),
    ('idiomas', r'ingl[eé]s|english|franc[eé]s|fran[cç]ais|lengua extranjera|celebrit|admire|travelling|cr[eê]pes|atelier|cin[eé]ma|francophon'),
    ('historia', r'historia|roma|romana|grieg|polis|barroco|arte\b|art[ií]stic|lat[ií]n|cl[aá]sic|mitolog|reinos|imperialismo|patrimonio|revoluci|goya|prado|andalus|filosof'),
    ('lengua', r'lengua castellana|literatura|literari|escritura|periodis|informativo|radio|corto|booktrailer|lectura|palabras|autor'),
]
NOMBRE_TEMA = {'tecnologia': 'Tecnología', 'ciencias': 'Ciencias', 'matematicas': 'Matemáticas', 'biologia': 'Biología',
               'economia': 'Economía', 'idiomas': 'Idiomas', 'historia': 'Humanidades', 'lengua': 'Lengua y comunicación'}


def tema(*textos):
    import re
    t = ' '.join(x for x in textos if x).lower()
    mejor, puntos = None, 0
    for nombre, patron in TEMAS:
        n = len(re.findall(patron, t))
        if n > puntos:
            mejor, puntos = nombre, n
    return mejor


def motivo(nombre, semilla, ancho, alto):
    """Dibujo lineal blanco en el cielo del paisaje, según la materia."""
    if not nombre:
        return ''
    r = _rng('m' + semilla)
    alto_cielo = alto * .52
    piezas = []
    n = 4 if ancho >= 800 else 2
    xs = sorted(r.uniform(.08, .92) * ancho for _ in range(n))
    for k, x in enumerate(xs):
        y = r.uniform(.6, .92) * alto_cielo
        s = r.uniform(.9, 1.3) * (alto / 200) * (1.0 if ancho >= 800 else 1.1)
        g = []
        if nombre == 'ciencias':
            g.append(f'<circle r="{5*s:.1f}" fill="#fff"/>')
            for ang in (0, 60, 120):
                g.append(f'<ellipse rx="{26*s:.1f}" ry="{9*s:.1f}" transform="rotate({ang + r.randint(-8, 8)})"/>')
        elif nombre == 'matematicas':
            fig = r.choice(['tri', 'cuad', 'hex', 'pi'])
            if fig == 'tri':
                g.append(f'<path d="M0,{-22*s:.1f} L{19*s:.1f},{11*s:.1f} L{-19*s:.1f},{11*s:.1f} Z"/>')
            elif fig == 'cuad':
                g.append(f'<rect x="{-15*s:.1f}" y="{-15*s:.1f}" width="{30*s:.1f}" height="{30*s:.1f}" transform="rotate({r.randint(0, 40)})"/><circle r="{21*s:.1f}"/>')
            elif fig == 'hex':
                pts = ' '.join(f'{20*s*math.cos(math.pi/3*i):.1f},{20*s*math.sin(math.pi/3*i):.1f}' for i in range(6))
                g.append(f'<polygon points="{pts}"/><path d="M{-20*s:.1f},0 H{20*s:.1f}"/>')
            else:
                g.append(f'<text font-size="{38*s:.0f}" text-anchor="middle" dy=".35em" fill="#fff" stroke="none" font-family="Georgia, serif">π</text>')
        elif nombre == 'tecnologia':
            pasos = [(0, 0), (22, 0), (22, -16), (44, -16)] if r.random() < .5 else [(0, 0), (0, 18), (26, 18), (26, 4)]
            d = 'M' + ' L'.join(f'{a*s:.1f},{b*s:.1f}' for a, b in pasos)
            g.append(f'<path d="{d}"/>')
            for a, b in (pasos[0], pasos[-1]):
                g.append(f'<circle cx="{a*s:.1f}" cy="{b*s:.1f}" r="{4*s:.1f}" fill="#fff"/>')
            g.append(f'<rect x="{8*s:.1f}" y="{-6*s:.1f}" width="{10*s:.1f}" height="{8*s:.1f}" rx="1.5"/>')
        elif nombre == 'biologia':
            g.append(f'<path d="M0,{-20*s:.1f} C{16*s:.1f},{-10*s:.1f} {16*s:.1f},{12*s:.1f} 0,{22*s:.1f} C{-16*s:.1f},{12*s:.1f} {-16*s:.1f},{-10*s:.1f} 0,{-20*s:.1f} Z" transform="rotate({r.randint(-40, 40)})"/>')
            g.append(f'<path d="M0,{-16*s:.1f} V{20*s:.1f}" transform="rotate({r.randint(-40, 40)})"/>')
        elif nombre == 'economia':
            barras = [r.uniform(.3, 1) for _ in range(4)]
            for i, b in enumerate(sorted(barras)):
                g.append(f'<rect x="{(i*10-20)*s:.1f}" y="{-28*b*s:.1f}" width="{7*s:.1f}" height="{28*b*s:.1f}" rx="1"/>')
            g.append(f'<path d="M{-22*s:.1f},{6*s:.1f} L{-6*s:.1f},{-8*s:.1f} L{6*s:.1f},{-2*s:.1f} L{22*s:.1f},{-24*s:.1f}"/>')
        elif nombre == 'idiomas':
            g.append(f'<path d="M{-22*s:.1f},{-14*s:.1f} h{44*s:.1f} v{24*s:.1f} h{-28*s:.1f} l{-10*s:.1f},{9*s:.1f} v{-9*s:.1f} h{-6*s:.1f} Z" stroke-linejoin="round"/>')
            for i in (-1, 0, 1):
                g.append(f'<circle cx="{i*10*s:.1f}" cy="{-2*s:.1f}" r="{2.2*s:.1f}" fill="#fff"/>')
        elif nombre == 'historia':
            g.append(f'<path d="M{-20*s:.1f},{-14*s:.1f} L0,{-24*s:.1f} L{20*s:.1f},{-14*s:.1f} Z M{-22*s:.1f},{18*s:.1f} H{22*s:.1f}"/>')
            for i in (-12, 0, 12):
                g.append(f'<path d="M{i*s:.1f},{-12*s:.1f} V{16*s:.1f}"/>')
        elif nombre == 'lengua':
            g.append(f'<path d="M0,{-12*s:.1f} C{-9*s:.1f},{-18*s:.1f} {-20*s:.1f},{-17*s:.1f} {-25*s:.1f},{-13*s:.1f} V{14*s:.1f} C{-20*s:.1f},{10*s:.1f} {-9*s:.1f},{9*s:.1f} 0,{15*s:.1f} '
                     f'C{9*s:.1f},{9*s:.1f} {20*s:.1f},{10*s:.1f} {25*s:.1f},{14*s:.1f} V{-13*s:.1f} C{20*s:.1f},{-17*s:.1f} {9*s:.1f},{-18*s:.1f} 0,{-12*s:.1f} Z M0,{-12*s:.1f} V{15*s:.1f}" stroke-linejoin="round"/>')
        piezas.append(f'<g transform="translate({x:.0f},{y:.0f})" style="--retraso:{-k*2.3:.1f}s">{"".join(g)}</g>')
    return (f'<g class="motivo" fill="none" stroke="#fff" stroke-width="{2.2 if ancho >= 800 else 2.6}" stroke-linecap="round" opacity=".85">'
            + ''.join(piezas) + '</g>')


# ---------- Portada: las 6 zonas del Aula del Futuro y pétalos de cerezo ----------
ZONAS = ['Investiga', 'Explora', 'Interactúa', 'Desarrolla', 'Crea', 'Presenta']


def zonas(ancho, alto):
    cx, cy, rx, ry = ancho * .5, alto * .3, ancho * .33, alto * .2
    nodos = [(cx + rx * math.cos(math.pi * (-.5 + i / 3)), cy + ry * math.sin(math.pi * (-.5 + i / 3))) for i in range(6)]
    lineas = []
    for i in range(6):
        for j in (i + 1, i + 2):
            a, b = nodos[i], nodos[j % 6]
            largo = math.dist(a, b)
            lineas.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" style="--largo:{largo:.0f};--i:{len(lineas)}"/>')
    puntos = []
    for i, ((x, y), nombre) in enumerate(zip(nodos, ZONAS)):
        w = 14 * len(nombre) + 62
        puntos.append(f'<g class="nodo" style="--i:{i}" transform="translate({x:.0f},{y:.0f})">'
                      f'<rect x="{-w/2:.0f}" y="-22" width="{w:.0f}" height="44" rx="22" fill="#ffffff" stroke="#9e1238" stroke-width="2"/>'
                      f'<circle cx="{-w/2 + 22:.0f}" cy="0" r="7" fill="#9e1238"/>'
                      f'<text x="{-w/2 + 38:.0f}" y="8" font-size="23" font-weight="700" fill="#1b201c" font-family="Bricolage Grotesque, system-ui, sans-serif">{nombre}</text></g>')
    return (f'<g class="zonas"><g class="lineas" stroke="#ffffff" stroke-width="2.5" opacity=".9">{"".join(lineas)}</g>{"".join(puntos)}</g>')


def petalos(semilla, ancho, alto, n=16):
    r = _rng('petalos' + semilla)
    out = []
    for i in range(n):
        x = r.uniform(0, ancho)
        out.append(f'<ellipse class="petalo" cx="{x:.0f}" cy="-12" rx="{r.uniform(4, 7):.1f}" ry="{r.uniform(2.5, 4):.1f}" '
                   f'fill="{r.choice(["#ffffff", "#f6c9d6", "#f0b3c5"])}" '
                   f'style="--dur:{r.uniform(9, 17):.1f}s;--delay:{-r.uniform(0, 17):.1f}s;--dx:{r.uniform(-120, 120):.0f}px;--alto:{alto + 24}px"/>')
    return f'<g class="petalos">{"".join(out)}</g>'
