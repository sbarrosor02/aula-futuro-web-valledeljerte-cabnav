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


def svg(semilla, curso=None, ancho=1200, alto=240, capas=4, bancales=True, clase='paisaje'):
    est = ESTACIONES[estacion(curso)]
    r = _rng(semilla)
    uid = 'p' + hashlib.sha1(semilla.encode()).hexdigest()[:8]
    paso = max(14, ancho // 60)
    partes = [f'<svg class="{clase}" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">',
              f'<defs><linearGradient id="{uid}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{est["cielo"][0]}"/><stop offset="1" stop-color="{est["cielo"][1]}"/></linearGradient></defs>',
              f'<rect width="{ancho}" height="{alto}" fill="url(#{uid}c)"/>',
              f'<circle cx="{r.uniform(.15, .85) * ancho:.0f}" cy="{alto * .28:.0f}" r="{alto * .13:.0f}" fill="{est["sol"]}" opacity=".9"/>']
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
    partes.append('</svg>')
    return ''.join(partes)
