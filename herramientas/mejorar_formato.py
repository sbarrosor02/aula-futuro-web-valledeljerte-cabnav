"""Reconstruye los títulos de sección que se perdieron al migrar del Google Site.

En el Site los títulos eran texto con letra grande o en negrita; al extraer el contenido
solo quedó el texto. Este script los detecta por cómo están escritos y los convierte en
encabezados reales. Se ejecuta una vez sobre datos/migrado.json (necesita beautifulsoup4).

Uso: python3 herramientas/mejorar_formato.py datos/migrado.json
"""
import json, re, sys
from bs4 import BeautifulSoup, NavigableString, Tag

RUTA = sys.argv[1]
d = json.load(open(RUTA, encoding='utf-8'))
cuenta = {'sueltos': 0, 'etiquetas': 0, 'negritas': 0, 'numerados': 0, 'cortos': 0}

ETIQUETA_INI = re.compile(r'^\s*([A-ZÁÉÍÓÚÑ¿][^:.\n]{1,38}?)\s*:\s*(\S.*)$', re.S)


def es_titulo_corto(t):
    t = t.strip()
    if not (2 < len(t) <= 60) or t.endswith(('.', ',', ';')) and not re.match(r'^\d', t):
        return False
    if len(t.split()) > 8 or not (t[0].isupper() or t[0].isdigit() or t[0] in '¿¡"«'):
        return False
    return True


def mejora(html):
    s = BeautifulSoup(html, 'html.parser')
    raiz = s

    # 1. Texto suelto fuera de párrafos (eran títulos con estilo en el Site)
    for nodo in list(raiz.contents):
        if isinstance(nodo, NavigableString) and nodo.strip():
            t = ' '.join(nodo.split())
            if len(t) <= 80 and not t.endswith('.'):
                h = s.new_tag('h2'); h.string = t.rstrip(':')
                cuenta['sueltos'] += 1
            else:
                h = s.new_tag('p'); h.string = t
            nodo.replace_with(h)

    # 2. Listas de un solo elemento que son una etiqueta ("Temática:", "Producto final:")
    for ul in list(s.find_all(['ul', 'ol'])):
        lis = ul.find_all('li', recursive=False)
        if len(lis) == 1 and not lis[0].find(['ul', 'ol']):
            t = ' '.join(lis[0].get_text(' ').split())
            sig = ul.find_next_sibling()
            if t.endswith(':') and len(t) <= 50:
                h = s.new_tag('h3'); h.string = t.rstrip(': ')
                ul.replace_with(h)
                cuenta['etiquetas'] += 1
            elif (len(t) <= 70 and len(t.split()) <= 9 and not lis[0].find('a') and sig is not None
                  and sig.name in ('p', 'ul', 'ol') and len(sig.get_text()) > 100):
                # apartados numerados de la plantilla antigua ("1. Descripción.")
                h = s.new_tag('h3'); h.string = t.rstrip('. ')
                ul.replace_with(h)
                cuenta['etiquetas'] += 1

    # 3. Párrafos que son solo una etiqueta terminada en dos puntos
    for p in list(s.find_all('p')):
        if p.find_parent('li'):
            continue
        t = ' '.join(p.get_text(' ').split())
        if t.endswith(':') and 2 < len(t) <= 50 and not p.find('a'):
            h = s.new_tag('h3'); h.string = t.rstrip(': ')
            p.replace_with(h)
            cuenta['etiquetas'] += 1

    # 4. Títulos numerados ("1. Justificación de la situación de aprendizaje.")
    for p in list(s.find_all('p')):
        t = ' '.join(p.get_text(' ').split())
        if re.match(r'^\d{1,2}(\.\d)?\s*[.\-–)]+\s*\S', t) and len(t) <= 80 and not p.find('a') and not p.find_parent('li'):
            h = s.new_tag('h2'); h.string = re.sub(r'[.:]\s*$', '', t)
            p.replace_with(h)
            cuenta['numerados'] += 1

    # 5. Párrafo corto con forma de título seguido de un párrafo largo
    for p in list(s.find_all('p')):
        if p.find_parent('li') or p.find('a') or p.parent is None:
            continue
        t = ' '.join(p.get_text(' ').split())
        sig = p.find_next_sibling()
        if es_titulo_corto(t) and ':' not in t and sig is not None and sig.name in ('p', 'ul', 'ol') and len(sig.get_text()) > 120:
            h = s.new_tag('h3'); h.string = t.rstrip('.')
            p.replace_with(h)
            cuenta['cortos'] += 1

    # 6. "Etiqueta: texto" → etiqueta en negrita
    for p in s.find_all('p'):
        if len(p.contents) != 1 or not isinstance(p.contents[0], NavigableString):
            continue
        texto = p.get_text('')
        m = ETIQUETA_INI.match(texto)
        if m and len(m.group(1).split()) <= 5 and not p.find('a'):
            p.clear()
            b = s.new_tag('strong'); b.string = m.group(1).strip() + ':'
            p.append(b); p.append(' ' + m.group(2).strip())
            cuenta['negritas'] += 1
    return str(s)


for pag in d['paginas']:
    if pag.get('html'):
        pag['html'] = mejora(pag['html'])

json.dump(d, open(RUTA, 'w', encoding='utf-8'), ensure_ascii=False)
print('Títulos y etiquetas reconstruidos:', cuenta)
