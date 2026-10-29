"""Genera el sitio estático del Aula del Futuro (un HTML por página).

Uso:  python3 generar.py datos_finales.json salida/

- datos_finales.json: contenido migrado del Google Site (cursos 22-23 a 25-26).
- nuevas/<curso>/*.json: situaciones de aprendizaje nuevas (este curso), con fotos en Drive.
"""
import json, re, sys, os, html, shutil, glob, unicodedata
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paisaje
import extras

SRC, OUT = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(SRC, encoding='utf-8'))
paginas = d['paginas']
esc = lambda s: html.escape(str(s or ''), quote=True)


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


# ---------- Fotos y documentos alojados en Drive ----------
def drive_img(fid, ancho=1280):
    return f'https://lh3.googleusercontent.com/d/{fid}=w{ancho}', f'https://drive.google.com/thumbnail?id={fid}&sz=w{ancho}'


def id_drive(v):
    m = re.search(r'/d/([\w-]{10,})', v) or re.search(r'[?&]id=([\w-]{10,})', v)
    return m.group(1) if m else v.strip()


# ---------- SdA nuevas (curso en marcha) desde nuevas/<curso>/*.json ----------
def carga_nuevas():
    por_id = {p['id']: p for p in paginas}
    for f in sorted(glob.glob(os.path.join(AQUI, 'nuevas', '*', '*.json'))):
        if os.path.basename(f).startswith('_'):
            continue  # plantillas y ejemplos
        s = json.load(open(f, encoding='utf-8'))
        curso = os.path.basename(os.path.dirname(f))           # p. ej. 26-27
        idx = f'curso-{curso}--situaciones-de-aprendizaje-{curso}'
        if idx not in por_id:
            idx = next((p['id'] for p in paginas if p['tipo'] == 'sda-index' and p['curso'] == curso), None)
        if not idx:
            print('AVISO: no hay índice de SdA para el curso', curso); continue
        pid = f'{idx.split("--")[0]}--{idx.split("--")[1]}--{slug(s["titulo"])}'
        partes = []
        if s.get('resumen'):
            partes.append(f'<p>{esc(s["resumen"])}</p>')
        for sec in s.get('secciones', []):
            partes.append(f'<h2>{esc(sec["titulo"])}</h2>')
            for par in str(sec.get('texto', '')).split('\n\n'):
                if par.strip():
                    partes.append(f'<p>{esc(par.strip())}</p>')
        fotos = [id_drive(x) for x in s.get('fotos', [])]
        if fotos:
            partes.append('<h2>Fotos</h2><div class="galeria">' + ''.join(
                f'<img src="drive:{fid}" alt="{esc(s["titulo"])}, foto {i + 1}" loading="lazy"/>' for i, fid in enumerate(fotos)) + '</div>')
        for doc in s.get('documentos', []):
            partes.append(f'<figure class="drive" data-id="{esc(id_drive(doc["enlace"]))}" data-nombre="{esc(doc["nombre"])}"></figure>')
        meta = {k: s[k] for k in ('autoria', 'etapa', 'areas') if s.get(k)}
        if s.get('resumen'):
            meta['resumen'] = s['resumen']
        if fotos:
            meta['portada'] = f'drive:{fotos[0]}'
        nueva = {'id': pid, 'titulo': s['titulo'], 'tipo': 'sda', 'padre': idx, 'curso': curso, 'meta': meta,
                 'html': '\n'.join(partes), 'texto': ' '.join([s.get('resumen', '')] + [x.get('texto', '') for x in s.get('secciones', [])])[:4000],
                 'url': None, 'docentes_texto': s.get('docentes', [])}
        paginas.append(nueva)
        por_id[pid] = nueva
        print('SdA nueva:', curso, s['titulo'])


carga_nuevas()

# Títulos que en el site estaban en MAYÚSCULAS, en tipo frase
TITULOS = {
    'ALIMENTACIÓN SALUDABLE': 'Alimentación saludable',
    'FIBONACCI EN LA NATURALEZA: DESCUBRIENDO EL SECRETO DE LAS PLANTAS': 'Fibonacci en la naturaleza: descubriendo el secreto de las plantas',
    'INTELIGENCIA ARTIFICIAL ¿BUENA O MALA?': 'Inteligencia artificial, ¿buena o mala?',
    'EL ARTE BARROCO: ARTE, PODER Y EMOCIÓN': 'El arte barroco: arte, poder y emoción',
    'EL DILEMA DEL DADO: ¿LA INTUICIÓN O LOS DATOS?': 'El dilema del dado: ¿la intuición o los datos?',
    'VIAJE A ROMA': 'Viaje a Roma',
    'BIO-CONSTRUCTORES 4.0: DISEÑANDO LA VIVIENDA SOSTENIBLE': 'Bio-constructores 4.0: diseñando la vivienda sostenible',
    'THINKING FRACCIONES': 'Thinking Fracciones',
    'TUK TUK VALLEY': 'Tuk Tuk Valley',
    'METAMORPHOSEON 2025-2026': 'Metamorphoseon 2025-2026',
    'PIANO INTERACTIVO DE CARTÓN CON MAKEY MAKEY Y SCRATCH': 'Piano interactivo de cartón con Makey Makey y Scratch',
    'NUTRI CHEF': 'Nutri Chef',
    'LO QUE SABEMOS, NOS AYUDA A CONSTRUIR LO QUE DESCONOCEMOS': 'Lo que sabemos nos ayuda a construir lo que desconocemos',
    'DIFUSIÓN DEL PROYECTO': 'Difusión del proyecto',
}
for p in paginas:
    p['titulo'] = TITULOS.get(p['titulo'].strip(), p['titulo'].strip())

P = {p['id']: p for p in paginas}
hijos = {}
for p in paginas:
    if p['padre']:
        hijos.setdefault(p['padre'], []).append(p)


def ruta(pid):
    return 'index.html' if pid == 'inicio' else pid.replace('--', '/') + '.html'


def rel(desde, pid):
    prof = ruta(desde).count('/')
    return '../' * prof + ruta(pid)


def raiz(desde):
    return '../' * ruta(desde).count('/')


CURSOS = sorted([p for p in paginas if p['tipo'] == 'curso'], key=lambda p: p['curso'], reverse=True)
OTRAS = [p for p in paginas if not p['padre'] and p['tipo'] == 'otra']
SDA_DE = {}
for s in paginas:
    for e in s.get('docentes', []):
        SDA_DE.setdefault(e['id'], []).append(s)

SIGLAS = {'eso': 'ESO', 'sda': 'SdA', 'adf': 'AdF', 'ods': 'ODS', 'cern': 'CERN', 'tic': 'TIC', 'ia': 'IA', 'stem': 'STEM', 'fp': 'FP',
          'cfgm': 'CFGM', 'ue': 'UE', 'lhc': 'LHC', 'dua': 'DUA', 'abp': 'ABP', '3d': '3D', 'ii': 'II', 'iii': 'III', 'iv': 'IV',
          'radioedu': 'RadioEdu', 'rebex': 'REBEX', 'educamatex': 'EDUCAMATEX', 'tedx': 'TEDx', 'jertedx': 'JerTEDx', 'smr': 'SMR',
          'garabato': 'Garabato', 'film': 'Film', 'fest': 'Fest', 'valle': 'Valle', 'jerte': 'Jerte', 'cabezuela': 'Cabezuela',
          'navaconcejo': 'Navaconcejo', 'extremadura': 'Extremadura', 'pikota': 'Pikota', 'radio': 'radio', 'aula': 'aula', 'futuro': 'futuro'}
NOMBRES_PROPIOS = {'Garabato', 'Film', 'Fest', 'Valle', 'Jerte', 'Cabezuela', 'Navaconcejo', 'Extremadura', 'Pikota'}


def frase(s):
    """Convierte un título en MAYÚSCULAS a tipo frase, respetando siglas y topónimos."""
    if s != s.upper() or not re.search(r'[A-ZÁÉÍÓÚÑ]{3}', s):
        return s
    palabras = re.split(r'(\s+)', s.lower())
    out, primera = [], True
    for w in palabras:
        if not w.strip():
            out.append(w); continue
        base = re.sub(r'[^\wáéíóúñü]', '', w)
        if base in SIGLAS:
            w = w.replace(base, SIGLAS[base])
        if primera:
            w = w[0].upper() + w[1:] if w and w[0].isalpha() else w
            primera = False
        elif base in SIGLAS and SIGLAS[base] in NOMBRES_PROPIOS:
            pass
        out.append(w)
    return ''.join(out)


def nombre_seccion(h):
    if h['tipo'] == 'sda-index':
        return 'Situaciones de aprendizaje'
    if h['tipo'] == 'part-index':
        return 'Participantes'
    if h['tipo'] == 'curso':
        return f'Curso {h["curso"]}'
    return frase(h['titulo'])


def ano(c):
    return f'20{c[:2]}-20{c[3:]}' if c else ''


# ---------- HTML del contenido migrado ----------
def prepara_html(desde, h, primera_img_prioritaria=False):
    antiguas = re.findall(r'<img[^>]*src="https://(?:sites\.google\.com|lh3\.googleusercontent\.com/docsubipk)[^"]*"[^>]*/?>', h)
    if antiguas:
        n = len(antiguas)
        url = P[desde].get('url')
        aviso = (f'<p class="fotos-site"><a href="{esc(url)}" target="_blank" rel="noopener">'
                 f'Ver {"la foto" if n == 1 else f"las {n} fotos"} de esta página en el Site del proyecto<span class="sr"> (se abre en otra pestaña)</span></a></p>') if url else ''
        primera = [True]
        def galeria(m):
            if 'drive:' in m.group(0):
                return m.group(0)
            if primera[0]:
                primera[0] = False
                return aviso
            return ''
        h = re.sub(r'<div class="galeria(?: sola)?">.*?</div>', galeria, h, flags=re.S)
        h = re.sub(r'<img[^>]*src="https://(?:sites\.google\.com|lh3\.googleusercontent\.com/docsubipk)[^"]*"[^>]*/?>', '', h)
        if primera[0] and aviso:
            h = aviso + h
    # enlaces internos
    h = re.sub(r'href="#([a-z0-9-]+)"', lambda m: f'href="{rel(desde, m.group(1))}"' if m.group(1) in P else m.group(0), h)
    # títulos en mayúsculas → tipo frase
    h = re.sub(r'<(h[23])>(.*?)</h[23]>', lambda m: f'<{m.group(1)}>' + (frase(m.group(2)) if '<' not in m.group(2) else m.group(2)) + f'</{m.group(1)}>', h)
    # fotos: cada una es un botón que abre el visor
    def foto(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        alt = re.search(r'alt="([^"]*)"', tag)
        alt = alt.group(1) if alt and alt.group(1) else ''
        alt_attr = alt or f'Foto de «{P[desde]["titulo"]}»'
        extra = ''
        if src.startswith('drive:'):
            src, alt_src = drive_img(src[6:])
            extra = f' data-alt="{esc(alt_src)}"'
        return (f'<button type="button" aria-label="Ampliar foto"><img src="{src}"{extra} alt="{esc(alt_attr)}" loading="lazy" decoding="async"></button>')
    h = re.sub(r'<img[^>]*/?>', foto, h)
    h = h.replace('<br/>', '<br>')
    h = re.sub(r'^\s*(<br>\s*)+', '', h)
    # Jerarquía de títulos: los h3 que aparecen antes del primer h2 pasan a h2
    i = h.find('<h2')
    cabeza, resto = (h, '') if i < 0 else (h[:i], h[i:])
    cabeza = re.sub(r'<h3>(.*?)</h3>', r'<h2>\1</h2>', cabeza)
    return cabeza + resto


def drive_cards(h):
    def card(m):
        fid, nombre = m.group(1), html.unescape(m.group(2))
        try:
            nombre = nombre.encode('latin-1').decode('utf-8')  # corrige nombres con acentos mal codificados
        except Exception:
            pass
        ext = (re.search(r'\.([A-Za-z0-9]{2,4})$', nombre) or [None, 'doc'])[1].upper()
        return (f'<figure class="drive" data-id="{esc(fid)}" data-nombre="{esc(nombre)}"><div class="fila">'
                f'<div class="ext" aria-hidden="true">{esc(ext)}</div><div class="nombre">{esc(nombre)}</div>'
                f'<div class="acciones"><a class="boton" href="https://drive.google.com/file/d/{esc(fid)}/view" target="_blank" rel="noopener">Abrir en Drive<span class="sr"> (se abre en otra pestaña)</span></a></div></div></figure>')
    return re.sub(r'<figure class="drive" data-id="([^"]*)" data-nombre="([^"]*)"></figure>', card, h)


def portada_src(src):
    if src and src.startswith('drive:'):
        a, b = drive_img(src[6:], 800)
        return a, b
    return src, None


# ---------- piezas comunes ----------
def nav(desde):
    actual = P[desde]
    activos = set()
    c = actual
    while c:
        activos.add(c['id']); c = P.get(c['padre'])
    def li(pid, texto, extra=''):
        cur = ' aria-current="page"' if pid == desde else (' aria-current="true"' if pid in activos and P[pid]['tipo'] != 'curso' else '')
        return f'<li><a href="{rel(desde, pid)}"{cur}>{texto}{extra}</a>'
    h = ['<ul>', li('inicio', 'Inicio') + '</li>', li('zonas', 'Zonas de aprendizaje') + '</li>', f'<li><a href="{rel(desde, "inicio")}#plano">Recorre el aula</a></li>', '<li class="sep" aria-hidden="true"></li>']
    for c in CURSOS:
        cur = ' aria-current="page"' if c['id'] == desde else ''
        h.append(f'<li class="grupo"><a href="{rel(desde, c["id"])}"{cur}><span>Curso {c["curso"]}</span><span class="ano">{ano(c["curso"])}</span></a><ul class="hijos">')
        for s in hijos.get(c['id'], []):
            n = len(hijos.get(s['id'], []))
            cur = ' aria-current="page"' if s['id'] == desde else (' aria-current="true"' if s['id'] in activos else '')
            num = f'<span class="n" aria-label="{n} páginas">{n}</span>' if n else ''
            h.append(f'<li><a href="{rel(desde, s["id"])}"{cur}><span>{esc(nombre_seccion(s))}</span>{num}</a></li>')
        h.append('</ul></li>')
    h.append('<li class="sep" aria-hidden="true"></li>')
    for o in OTRAS:
        cur = ' aria-current="page"' if o['id'] == desde else ''
        h.append(f'<li><a href="{rel(desde, o["id"])}"{cur}>{esc(o["titulo"])}</a></li>')
    h.append('</ul>')
    return ''.join(x for x in h if x)


def migas(p):
    if p['id'] == 'inicio':
        return ''
    cadena = []
    c = P.get(p['padre'])
    while c:
        cadena.insert(0, c); c = P.get(c['padre'])
    items = [f'<li><a href="{rel(p["id"], "inicio")}">Inicio</a></li>'] + \
            [f'<li><a href="{rel(p["id"], c["id"])}">{esc(nombre_seccion(c))}</a></li>' for c in cadena]
    return f'<nav class="migas" aria-label="Ruta de navegación"><ol>{"".join(items)}</ol></nav>'


ICONO_LUPA = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICONO_MENU = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
ICONO_X = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
FECHA = date.fromisoformat(d['extraido'][:10]).strftime('%d/%m/%Y')
import hashlib
VER = {f: hashlib.sha1(open(os.path.join(AQUI, 'sitio_src', f), 'rb').read()).hexdigest()[:8] for f in ('estilo.css', 'app.js')}


def pagina(p, cuerpo, descripcion='', imagen=None, titulo_doc=None):
    r = raiz(p['id'])
    titulo_doc = titulo_doc or (('' if p['id'] == 'inicio' else p['titulo'] + ' · ') + 'Aula del Futuro IES Valle del Jerte')
    descripcion = (descripcion or 'Aula del Futuro del IES Valle del Jerte (Cabezuela del Valle y Navaconcejo): situaciones de aprendizaje, docentes y transformación de los espacios.')[:300]
    og_img = f'<meta property="og:image" content="{esc(imagen)}">' if imagen and imagen.startswith('http') else ''
    return f'''<!doctype html>
<html lang="es" data-raiz="{r}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo_doc)}</title>
<meta name="description" content="{esc(descripcion)}">
<meta name="referrer" content="no-referrer">
<meta property="og:title" content="{esc(p['titulo'])}">
<meta property="og:description" content="{esc(descripcion)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
{og_img}
<link rel="icon" href="{r}assets/icono.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap">
<link rel="stylesheet" href="{r}assets/estilo.css?v={VER['estilo.css']}">
<script type="speculationrules">{{"prefetch":[{{"where":{{"and":[{{"href_matches":"*.html","relative_to":"document"}},{{"not":{{"selector_matches":"[target]"}}}}]}},"eagerness":"moderate"}}]}}</script>
<script src="{r}assets/app.js?v={VER['app.js']}" defer></script>
</head>
<body>
<a class="saltar" href="#contenido">Saltar al contenido</a>
<div class="app">
  <header class="cabecera-movil">
    <a class="marca" href="{rel(p['id'], 'inicio')}"><b>Aula del Futuro</b><small>IES Valle del Jerte</small></a>
    <button class="boton" id="drawer-open" type="button" aria-expanded="false" aria-controls="drawer">{ICONO_MENU}Menú</button>
  </header>
  <aside class="Drawer lateral-fija" id="drawer" popover="manual" aria-label="Menú del sitio">
    <div class="Drawer-scroller">
      <div class="Drawer-sheet" tabindex="-1">
        <div class="lateral-cab">
          <a class="marca" href="{rel(p['id'], 'inicio')}"><b>Aula del Futuro</b><small>IES Valle del Jerte · Cabezuela y Navaconcejo</small></a>
          <button class="boton cerrar-menu" type="button" aria-label="Cerrar menú">{ICONO_X}</button>
        </div>
        <form class="buscador" role="search" action="{r}buscar.html" method="get">
          {ICONO_LUPA}
          <input type="search" name="q" id="q-lateral" placeholder="Buscar en el sitio" aria-label="Buscar en el sitio" autocomplete="off">
        </form>
        <nav class="arbol" aria-label="Secciones del sitio">{nav(p['id'])}</nav>
        <p class="pie-lateral">Contenido migrado del Google Site del proyecto el {FECHA}.</p>
      </div>
    </div>
  </aside>
  <main id="contenido" tabindex="-1">
    <div class="columna">
{cuerpo}
    </div>
  </main>
</div>
<dialog class="visor" id="visor" closedby="any" aria-label="Foto ampliada">
  <form method="dialog"><button class="boton" aria-label="Cerrar foto">{ICONO_X}Cerrar</button></form>
  <img alt="">
</dialog>
</body>
</html>
'''


def pie_original(p):
    if not p.get('url'):
        return ''
    return (f'<footer class="original"><span>Página migrada desde el Google Site del proyecto.</span>'
            f'<a href="{esc(p["url"])}" target="_blank" rel="noopener">Ver la página original<span class="sr"> (se abre en otra pestaña)</span></a></footer>')


def tema_de(p):
    if p['tipo'] != 'sda':
        return None
    m = p.get('meta', {})
    return paisaje.tema(m.get('areas', ''), m.get('areas', ''), p['titulo'], p['titulo'], p['texto'][:1500])


# Zonas de aprendizaje: se buscan cerca de la palabra "zona(s)" y en sus distintas formas
# (Investiga / investigar / investigación, Presenta / presentación / exposición…)
RAICES_ZONA = {
    'Investiga': r'investig', 'Explora': r'explor', 'Interactúa': r'interact', 'Desarrolla': r'desarroll',
    'Crea': r'\bcrea(?:r|ción|cion|tiv)?\b|\bcreaci', 'Presenta': r'present|exposici|exponer', 'Intercambia': r'intercambi',
}


def zonas_de(p):
    t = p['texto']
    ventanas = [t[m.start():m.start() + 260] for m in re.finditer(r'(?i)\bzonas?\b', t)]
    if not ventanas:
        return []
    encontradas = []
    for z, raiz in RAICES_ZONA.items():
        if any(re.search(raiz, v, re.I) for v in ventanas):
            encontradas.append(z)
    # "Intercambia" es el nombre antiguo de "Explora": se agrupan
    if 'Intercambia' in encontradas:
        encontradas.remove('Intercambia')
        if 'Explora' not in encontradas:
            encontradas.insert(1, 'Explora')
    return [z for z in paisaje.ZONAS if z in encontradas]


def ancla_zona(z):
    return 'zona-' + slug(z)


def banda(p):
    est = paisaje.estacion(p.get('curso'))
    etiqueta = f'<span class="banda-etiqueta">Curso {p["curso"]} · {paisaje.NOMBRE[est]}</span>' if p.get('curso') else ''
    t = tema_de(p)
    if t:
        etiqueta = f'<span class="banda-etiqueta">{paisaje.NOMBRE_TEMA[t]} · curso {p["curso"]}</span>'
    return f'<div class="banda">{paisaje.svg(p["id"], p.get("curso"), 1200, 200, tema_sda=t)}{etiqueta}</div>'


def cabecera(p, sub=''):
    return f'{banda(p)}{migas(p)}<h1 class="titulo">{esc(nombre_seccion(p) if p["tipo"] in ("curso", "sda-index", "part-index") else frase(p["titulo"]))}</h1>' + (f'<p class="subtitulo">{sub}</p>' if sub else '')


def tarjeta(desde, s, nivel='h3'):
    m = s.get('meta', {})
    img = ''
    if str(m.get('portada', '')).startswith('drive:'):
        src, alt_src = portada_src(m['portada'])
        img = f'<img src="{esc(src)}" data-alt="{esc(alt_src)}" alt="" loading="lazy" decoding="async">'
    else:
        img = paisaje.svg(s['id'], s.get('curso'), 400, 230, capas=3, tema_sda=tema_de(s))
    area = re.split(r'\s*(?:·|,|;|/|\n| - |–)\s*', m.get('areas', ''))[0].strip(' .:')
    if area and len(area) <= 34:
        img += f'<span class="area">{esc(area)}</span>'
    texto = ' '.join([s['titulo'], m.get('autoria', ''), m.get('etapa', ''), m.get('areas', ''), s['texto'][:500]])
    return (f'<li data-texto="{esc(texto)}"><article class="tarjeta"><div class="img">{img}</div><div class="cuerpo">'
            f'<{nivel}><a href="{rel(desde, s["id"])}">{esc(s["titulo"])}</a></{nivel}>'
            + (f'<p class="etapa">{esc(m["etapa"])}</p>' if m.get('etapa') else '')
            + (f'<p class="resumen">{esc(m["resumen"])}</p>' if m.get('resumen') else '')
            + (f'<p class="autor">{esc(m["autoria"])}</p>' if m.get('autoria') else '')
            + '</div></article></li>')


# ---------- vistas ----------
def v_inicio(p):
    total = sum(1 for x in paginas if x['tipo'] == 'sda')
    docentes = len({' '.join(sorted(slug(x['titulo']).split('-'))) for x in paginas if x['tipo'] == 'part'})
    cuentas = {z: len(ZONA_SDA[z]) for z in paisaje.ZONAS}
    enlaces = {z: f'zonas.html#{ancla_zona(z)}' for z in paisaje.ZONAS}
    extra = paisaje.zonas(900, 620, enlaces, cuentas) + paisaje.petalos('portada', 900, 620)
    sedes = (f'<div class="panorama">{paisaje.svg("portada-valle", "22-23", 900, 620, extra=extra)}'
             f'<p class="sr">Las seis zonas de aprendizaje del Aula del Futuro.</p></div>')
    sedes += ('<nav class="zonas-portada" aria-label="Situaciones de aprendizaje por zona"><ul class="chips">'
              + ''.join(f'<li><a class="chip zona" href="zonas.html#{ancla_zona(z)}">{z} <span aria-hidden="true">·</span> {cuentas[z]}</a></li>' for z in paisaje.ZONAS) + '</ul></nav>')
    sedes = f'<div>{sedes}</div>'
    h = (f'<section class="portada" aria-labelledby="titulo-portada"><div>'
         f'<h1 id="titulo-portada">Dos sedes, dos aulas, un mismo proyecto</h1>'
         f'<p>El IES Valle del Jerte transforma sus espacios de Cabezuela del Valle y Navaconcejo para aprender investigando, creando y colaborando. Desde el curso 2022-2023 se han hecho {total} situaciones de aprendizaje con {docentes} docentes.</p>'
         f'</div>{sedes}</section>')
    h += '<h2 class="seccion-titulo" id="cursos">Cursos</h2><ul class="cursos" aria-labelledby="cursos">'
    for c in CURSOS:
        si = next((x for x in hijos.get(c['id'], []) if x['tipo'] == 'sda-index'), None)
        pi = next((x for x in hijos.get(c['id'], []) if x['tipo'] == 'part-index'), None)
        ns = len(hijos.get(si['id'], [])) if si else 0
        np_ = len(hijos.get(pi['id'], [])) if pi else 0
        det = (f'{ns} situaciones' + (f', {np_} docentes' if np_ else '')) if ns else 'En marcha'
        est = paisaje.estacion(c['curso'])
        h += (f'<li><a class="curso" href="{rel("inicio", c["id"])}">{paisaje.svg("curso-" + c["curso"], c["curso"], 320, 90, capas=3, clase="mini")}'
              f'<b>{c["curso"]}</b><span>{det}</span><span class="estacion">{paisaje.NOMBRE[est].capitalize()}</span></a></li>')
    h += '</ul>'
    cuentas_z = {z: len(ZONA_SDA[z]) for z in paisaje.ZONAS}
    h += extras.plano(DESCRIPCION_ZONA, cuentas_z, 'zonas.html#zona-')
    n_sda = {}
    for c in CURSOS:
        si = next((x for x in hijos.get(c['id'], []) if x['tipo'] == 'sda-index'), None)
        n_sda[c['curso']] = len(hijos.get(si['id'], [])) if si else 0
    h += extras.linea_tiempo(lambda pid: rel('inicio', pid), n_sda)
    cursos_asc = sorted(n_sda)
    doc_curso = []
    for c in cursos_asc:
        pi = next((x for x in hijos.get(f'curso-{c}', []) if x['tipo'] == 'part-index'), None)
        doc_curso.append((c, len(hijos.get(pi['id'], [])) if pi else 0))
    temas = {}
    for s in paginas:
        if s['tipo'] == 'sda':
            t = tema_de(s)
            k = paisaje.NOMBRE_TEMA[t] if t else 'Otros'
            temas[k] = temas.get(k, 0) + 1
    por_tema = sorted(temas.items(), key=lambda kv: (kv[0] == 'Otros', -kv[1]))
    con_z = len({s['id'] for v in ZONA_SDA.values() for s in v})
    h += extras.cifras(total, docentes, [(c, n_sda[c]) for c in cursos_asc], doc_curso, por_tema, con_z)
    h += '<h2 class="seccion-titulo">El proyecto</h2>'
    cuerpo = re.sub(r'^\s*<img[^>]*/?>', '', p['html'])  # la primera foto ya está en la portada
    h += f'<div class="contenido lectura">{drive_cards(prepara_html("inicio", cuerpo))}</div>'
    return pagina(p, h)


def v_curso(p):
    secs = hijos.get(p['id'], [])
    h = cabecera(p, f'Curso escolar {ano(p["curso"])}')
    if secs:
        h += '<ul class="accesos">'
        for s in secs:
            n = len(hijos.get(s['id'], []))
            sub = f'{n} situaciones' if s['tipo'] == 'sda-index' else f'{n} docentes' if s['tipo'] == 'part-index' else 'Ver apartado'
            if s['tipo'] == 'sda-index' and not n:
                sub = 'Aún sin publicar'
            h += f'<li><a class="acceso" href="{rel(p["id"], s["id"])}"><strong>{esc(nombre_seccion(s))}</strong><span>{sub}</span></a></li>'
        h += '</ul>'
    if p['html']:
        h += f'<div class="contenido" style="margin-top:32px">{drive_cards(prepara_html(p["id"], p["html"]))}</div>'
    return pagina(p, h + pie_original(p), descripcion=f'Aula del Futuro del IES Valle del Jerte en el curso {ano(p["curso"])}.')


def v_sda_index(p):
    lista = hijos.get(p['id'], [])
    h = cabecera(p, f'Curso {ano(p["curso"])}')
    if p['html']:
        h += f'<div class="contenido lectura">{drive_cards(prepara_html(p["id"], p["html"]))}</div>'
    if not lista:
        h += '<p class="vacio-aviso">Todavía no hay situaciones de aprendizaje publicadas en este curso.</p>'
    else:
        h += (f'<div class="filtro"><label for="filtro-sda">Filtrar por título, docente, curso o materia</label>'
              f'<input id="filtro-sda" type="search" autocomplete="off"><output id="filtro-n" for="filtro-sda" aria-live="polite">{len(lista)} situaciones</output></div>'
              f'<ul class="rejilla" id="rejilla">{"".join(tarjeta(p["id"], s, 'h2') for s in lista)}</ul>')
    return pagina(p, h + pie_original(p), descripcion=f'{len(lista)} situaciones de aprendizaje del Aula del Futuro del IES Valle del Jerte en el curso {ano(p["curso"])}.')


def v_part_index(p):
    lista = hijos.get(p['id'], [])
    h = cabecera(p, f'{len(lista)} docentes en el curso {ano(p["curso"])}')
    if p['html']:
        h += f'<div class="contenido lectura">{drive_cards(prepara_html(p["id"], p["html"]))}</div>'
    h += '<ul class="personas">'
    for x in lista:
        n = len(SDA_DE.get(x['id'], []))
        etiqueta = f'<span class="n">{n} {"situación" if n == 1 else "situaciones"}</span>' if n else ''
        h += f'<li><a class="persona" href="{rel(p["id"], x["id"])}">{extras.avatar(x["titulo"])}<span class="persona-nombre">{esc(x["titulo"])}</span>{etiqueta}</a></li>'
    h += '</ul>'
    return pagina(p, h + pie_original(p), descripcion=f'Docentes del Aula del Futuro del IES Valle del Jerte en el curso {ano(p["curso"])}.')


def v_sda(p):
    m = p.get('meta', {})
    h = cabecera(p, f'Situación de aprendizaje del curso {ano(p["curso"])}')
    filas = []
    if m.get('autoria'):
        nota = '<div class="nota">Según las fichas de participantes</div>' if m.get('autoria_origen') else ''
        filas.append(('Autoría', esc(m['autoria']) + nota))
    if m.get('etapa'):
        filas.append(('Curso y etapa', esc(m['etapa'])))
    if m.get('areas'):
        filas.append(('Áreas y materias', esc(m['areas'])))
    zs = zonas_de(p)
    if zs:
        filas.append(('Zonas del aula', '<ul class="chips">' + ''.join(f'<li><a class="chip zona" href="{raiz(p["id"])}zonas.html#{ancla_zona(z)}">{z}</a></li>' for z in zs) + '</ul>'))
    if p.get('docentes'):
        chips = ''.join(f'<li><a class="chip{" colabora" if e["rol"] == "colabora" else ""}" href="{rel(p["id"], e["id"])}">{esc(P[e["id"]]["titulo"])}'
                        + ('<span class="sr"> (colabora)</span>' if e['rol'] == 'colabora' else '') + '</a></li>' for e in p['docentes'])
        filas.append(('Docentes del proyecto', f'<ul class="chips">{chips}</ul>'))
    if filas:
        h += '<dl class="ficha">' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in filas) + '</dl>'
    cuerpo = drive_cards(prepara_html(p['id'], p['html'])) if p['html'] else '<p class="vacio-aviso">Esta página no tiene contenido en el site original.</p>'
    h += f'<div class="contenido lectura">{cuerpo}</div>'
    src, _ = portada_src(m.get('portada'))
    return pagina(p, h + pie_original(p), descripcion=m.get('resumen') or f'Situación de aprendizaje del Aula del Futuro, curso {ano(p["curso"])}.', imagen=src)


def v_part(p):
    lista = SDA_DE.get(p['id'], [])
    h = cabecera(p, f'Docente participante en el curso {ano(p["curso"])}').replace('<h1 class="titulo">', '<h1 class="titulo con-avatar">' + extras.avatar(p['titulo'], True), 1)
    if p['html']:
        h += f'<div class="contenido lectura">{drive_cards(prepara_html(p["id"], p["html"]))}</div>'
    if lista:
        h += f'<h2 class="seccion-titulo">Situaciones de aprendizaje <span class="n">{len(lista)}</span></h2><ul class="rejilla">{"".join(tarjeta(p["id"], s) for s in lista)}</ul>'
    return pagina(p, h + pie_original(p), descripcion=f'{p["titulo"]}, docente del Aula del Futuro del IES Valle del Jerte ({ano(p["curso"])}).')


def v_generica(p):
    h = cabecera(p, f'Curso {ano(p["curso"])}' if p.get('curso') else '')
    sub = hijos.get(p['id'], [])
    h += f'<div class="contenido lectura">{drive_cards(prepara_html(p["id"], p["html"]))}</div>' if p['html'] else ('' if sub else '<p class="vacio-aviso">Esta página no tiene contenido en el site original.</p>')
    return pagina(p, h + pie_original(p))


ZONA_SDA = {z: [] for z in paisaje.ZONAS}
for _s in paginas:
    if _s['tipo'] == 'sda':
        for _z in zonas_de(_s):
            ZONA_SDA[_z].append(_s)

DESCRIPCION_ZONA = {
    'Investiga': 'Buscar información, experimentar y analizar datos.',
    'Explora': 'Descubrir y manipular materiales, recursos y entornos.',
    'Interactúa': 'Debatir, colaborar y trabajar en equipo.',
    'Desarrolla': 'Trabajar de forma autónoma y reflexionar sobre lo aprendido.',
    'Crea': 'Diseñar y producir: vídeos, maquetas, programas, prototipos.',
    'Presenta': 'Exponer y compartir el trabajo con los demás.',
}


VISTAS = {'inicio': v_inicio, 'curso': v_curso, 'sda-index': v_sda_index, 'part-index': v_part_index, 'sda': v_sda, 'part': v_part}

# ---------- escritura ----------
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'assets'))
for f in ('estilo.css', 'app.js', 'icono.svg'):
    shutil.copy(os.path.join(AQUI, 'sitio_src', f), os.path.join(OUT, 'assets', f))
for p in paginas:
    destino = os.path.join(OUT, ruta(p['id']))
    os.makedirs(os.path.dirname(destino) or OUT, exist_ok=True)
    open(destino, 'w', encoding='utf-8').write(VISTAS.get(p['tipo'], v_generica)(p))

# Buscador: índice como script (funciona también abriendo los archivos en local)
def norm(s):
    return unicodedata.normalize('NFD', s.lower()).encode('utf-8').decode('utf-8')
indice = []
for p in paginas:
    if p['id'] == 'inicio':
        continue
    donde = {'sda': 'Situación de aprendizaje', 'part': 'Participante', 'sda-index': 'Situaciones de aprendizaje', 'part-index': 'Participantes', 'curso': 'Curso'}.get(p['tipo'], 'Página')
    if p.get('curso') and p['tipo'] != 'curso':
        donde += f', curso {p["curso"]}'
    t = p['texto']
    indice.append({'ti': p['titulo'], 'u': ruta(p['id']), 'd': donde, 't': t,
                   'n': re.sub(r'[̀-ͯ]', '', unicodedata.normalize('NFD', p['titulo'].lower())),
                   'x': re.sub(r'[̀-ͯ]', '', unicodedata.normalize('NFD', t.lower()))})
open(os.path.join(OUT, 'assets', 'indice.js'), 'w', encoding='utf-8').write('window.INDICE=' + json.dumps(indice, ensure_ascii=False, separators=(',', ':')) + ';')

zp = {'id': 'zonas', 'titulo': 'Zonas de aprendizaje', 'tipo': 'otra', 'padre': None, 'curso': None, 'html': '', 'texto': '', 'url': None}
P['zonas'] = zp
total_con = len({s['id'] for v in ZONA_SDA.values() for s in v})
cuerpo = (f'{migas(zp)}<h1 class="titulo">Zonas de aprendizaje</h1>'
          f'<p class="subtitulo">El Aula del Futuro se organiza en seis zonas. {total_con} situaciones de aprendizaje indican qué zonas usaron; '
          f'las de este curso las recogen todas.</p><ul class="chips indice-zonas">'
          + ''.join(f'<li><a class="chip zona" href="#{ancla_zona(z)}">{z} <span aria-hidden="true">·</span> {len(ZONA_SDA[z])}</a></li>' for z in paisaje.ZONAS) + '</ul>')
for z in paisaje.ZONAS:
    lista = sorted(ZONA_SDA[z], key=lambda s: s.get('curso') or '', reverse=True)
    cuerpo += (f'<section aria-labelledby="{ancla_zona(z)}"><h2 class="seccion-titulo" id="{ancla_zona(z)}">{z} <span class="n">{len(lista)} situaciones</span></h2>'
               f'<p class="desc-zona">{DESCRIPCION_ZONA[z]}</p><ul class="rejilla">{"".join(tarjeta("zonas", s) for s in lista)}</ul></section>')
open(os.path.join(OUT, 'zonas.html'), 'w', encoding='utf-8').write(pagina(zp, cuerpo, descripcion='Situaciones de aprendizaje del Aula del Futuro del IES Valle del Jerte agrupadas por zona de aprendizaje.'))

busq = {'id': 'buscar', 'titulo': 'Buscar', 'tipo': 'otra', 'padre': None, 'curso': None, 'html': '', 'texto': '', 'url': None}
P['buscar'] = busq
open(os.path.join(OUT, 'buscar.html'), 'w', encoding='utf-8').write(pagina(busq,
    f'{migas(busq)}<h1 class="titulo" id="titulo-busqueda" aria-live="polite">Buscar en el sitio</h1><ul class="resultados" id="resultados"></ul>',
    titulo_doc='Buscar · Aula del Futuro IES Valle del Jerte'))
no = {'id': '404', 'titulo': 'Página no encontrada', 'tipo': 'otra', 'padre': None, 'curso': None, 'html': '', 'texto': '', 'url': None}
P['404'] = no
open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(pagina(no,
    '<h1 class="titulo">No encontramos esta página</h1><p>Puede que la dirección haya cambiado. Usa el buscador o vuelve a la <a href="index.html">página de inicio</a>.</p>'))
print(f'{len(paginas)} páginas generadas en {OUT}')
