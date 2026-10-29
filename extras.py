"""Piezas de la portada: plano del aula, línea del tiempo, cifras y avatares de docentes.

Los datos del plano y de la línea del tiempo salen de las páginas «Diseño del aula»,
«Transformación del espacio», «Difusión del proyecto» y «Garabato Film Fest» del Site.
"""
import html, json, hashlib

esc = lambda s: html.escape(str(s or ''), quote=True)

# ---------- Plano del aula ----------
ZONAS_PLANO = ['Investiga', 'Explora', 'Interactúa', 'Desarrolla', 'Crea', 'Presenta', 'RadioEdu']
EQUIPAMIENTO = {
    'navaconcejo': {
        'Investiga': ['Mesas con sillas', 'Ordenadores con conexión a internet', 'Armario con llave para los aparatos más delicados'],
        'Explora': ['Mesa alta y taburetes', 'Jardín vertical en el pasillo de entrada, con luz natural, para cultivos, germinación y estudio de condiciones ambientales'],
        'Interactúa': ['Rincones para intercambiar información y debatir', 'Mesa con puestos movibles para combinar grupos de trabajo', 'Pufs, mesa baja y pizarra'],
        'Desarrolla': [],
        'Crea': ['Croma de cuatro colores (verde, negro, azul y blanco)', 'Kit de iluminación, trípode y aro de luz', 'Cámara de vídeo 4K', 'Montada sobre el antiguo escenario del aula', 'Impresora 3D con revólver de colores (curso 24-25)'],
        'Presenta': ['Gradas con ruedas y almacenaje, fabricadas con el alumnado a partir de cajoneras recicladas', 'Pizarra digital', 'Ordenador con altavoces'],
        'RadioEdu': ['Radio Pikota, la emisora del centro, integrada como una zona más', 'Cerramiento de aluminio y cristal de seguridad', 'Puerta interior al aula y puerta propia al pasillo'],
    },
    'cabezuela': {
        'Investiga': [], 'Explora': [], 'Interactúa': [], 'Desarrolla': [],
        'Crea': ['Croma construido en el curso 22-23', 'Impresora 3D'],
        'Presenta': ['Gradas fabricadas con las cajoneras de las mesas del alumnado: el modelo que luego copió Navaconcejo'],
        'RadioEdu': ['Sala de Radio Pikota cerrada dentro del aula en el curso 24-25'],
    },
}
OTROS_CABEZUELA = ['Dos mesas de robótica con ruedas y frenos, que se unen en una grande', 'Mesa redonda modular de ocho puestos para el trabajo colaborativo',
                   'Señalización de las zonas de aprendizaje (curso 24-25)', 'Vinilos en puerta y ventanas diseñados con el alumnado']


def plano(descripciones, cuentas, enlace_zonas):
    datos = {'equipamiento': EQUIPAMIENTO, 'otros': {'cabezuela': OTROS_CABEZUELA, 'navaconcejo': []},
             'descripcion': {**descripciones, 'RadioEdu': 'Emisora escolar para producir programas, entrevistas y podcasts dentro de las SdA.'},
             'cuentas': cuentas, 'enlace': enlace_zonas}
    botones = ''.join(
        f'<button type="button" class="zona-plano zp-{z.lower().replace("ú", "u")}" data-zona="{esc(z)}" aria-pressed="{"true" if z == "Presenta" else "false"}">'
        f'<span class="zp-nombre">{esc(z)}</span>' + (f'<span class="zp-n">{cuentas[z]} SdA</span>' if cuentas.get(z) else '') + '</button>'
        for z in ZONAS_PLANO)
    return f'''<section class="bloque" id="plano" aria-labelledby="t-plano">
<h2 class="seccion-titulo" id="t-plano">Recorre el aula</h2>
<p class="subtitulo">Pulsa una zona para ver qué hay en ella y qué situaciones de aprendizaje la usan. Es un esquema de zonas, no un plano a escala.</p>
<div class="sede-selector" role="group" aria-label="Sede">
  <button type="button" data-sede="navaconcejo" aria-pressed="true">Navaconcejo</button>
  <button type="button" data-sede="cabezuela" aria-pressed="false">Cabezuela del Valle</button>
</div>
<div class="plano-wrap">
  <div class="plano" role="group" aria-label="Zonas del aula">{botones}<span class="puerta" aria-hidden="true"></span></div>
  <div class="plano-panel" id="plano-panel" aria-live="polite"></div>
</div>
<script type="application/json" id="datos-plano">{json.dumps(datos, ensure_ascii=False)}</script>
</section>'''


# ---------- Línea del tiempo ----------
def linea_tiempo(rel, n_sda):
    hitos = [
        ('22-23', 'Nace el aula de Cabezuela del Valle',
         'El alumnado participa en el diseño con una lluvia de ideas y la app HomeByMe. Se fabrican gradas con cajoneras recicladas, mesas de robótica con ruedas y un croma.',
         'curso-22-23--transformacion-del-espacio'),
        ('23-24', 'Segunda aula en Navaconcejo',
         'Con la experiencia de Cabezuela se monta «en tiempo récord». RadioEdu se integra como una zona más y se construye un jardín vertical. Se celebra el I Garabato Film Fest.',
         'curso-23-24--transformacion-del-espacio'),
        ('24-25', 'Mejoras y difusión',
         'Cabezuela cierra su sala de Radio Pikota y señaliza las zonas; Navaconcejo estrena impresora 3D. Se graban vídeos para que los docentes nuevos conozcan el aula.',
         'curso-24-25--transformacion-del-espacio'),
        ('25-26', 'El curso con más situaciones de aprendizaje',
         'Las dos aulas acogen proyectos de casi todas las materias, de la ESO al Bachillerato y la FP.',
         'curso-25-26--situaciones-de-aprendizaje'),
        ('26-27', 'Nueva etapa',
         'Nueva plantilla de situaciones de aprendizaje y nueva web del proyecto.',
         'curso-26-27'),
    ]
    items = ''
    for curso, titulo, texto, destino in hitos:
        n = n_sda.get(curso)
        cifra = f'<span class="hito-n">{n} SdA</span>' if n else ''
        items += (f'<li class="hito"><div class="hito-curso">{curso}</div><div class="hito-cuerpo"><h3>{esc(titulo)}</h3>'
                  f'<p>{esc(texto)}</p><p class="hito-pie">{cifra}<a href="{rel(destino)}">Ver el curso {curso}</a></p></div></li>')
    return (f'<section class="bloque" aria-labelledby="t-linea"><h2 class="seccion-titulo" id="t-linea">Cómo ha crecido el proyecto</h2>'
            f'<ol class="linea">{items}</ol></section>')


# ---------- Cifras ----------
def barras(titulo, filas, nota='', horizontal=False, sufijo=''):
    """Gráfico de barras de una sola serie, con valores escritos y vista de tabla."""
    maximo = max(v for _, v in filas) or 1
    if horizontal:
        alto_f, ancho, eti = 34, 560, 170
        alto = alto_f * len(filas) + 8
        partes = []
        for i, (k, v) in enumerate(filas):
            y = i * alto_f + 6
            w = max(4, (ancho - eti - 50) * v / maximo)
            partes.append(f'<g><title>{esc(k)}: {v}{sufijo}</title>'
                          f'<text x="{eti - 10}" y="{y + 15}" text-anchor="end" class="g-eti">{esc(k)}</text>'
                          f'<rect x="{eti}" y="{y + 2}" width="{w:.1f}" height="20" rx="4" class="g-barra"/>'
                          f'<text x="{eti + w + 8:.1f}" y="{y + 17}" class="g-valor">{v}</text></g>')
        svg = f'<svg viewBox="0 0 {ancho} {alto}" class="grafico" role="img" aria-label="{esc(titulo)}">{"".join(partes)}</svg>'
    else:
        ancho, alto, base, top = 420, 230, 196, 24
        paso = ancho / len(filas)
        bw = min(56, paso * .55)
        partes = [f'<line x1="0" y1="{base}" x2="{ancho}" y2="{base}" class="g-eje"/>']
        for i, (k, v) in enumerate(filas):
            h = max(3 if v else 0, (base - top) * v / maximo)
            x = i * paso + (paso - bw) / 2
            partes.append(f'<g><title>Curso {esc(k)}: {v}{sufijo}</title>'
                          + (f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" class="g-barra"/>' if v else '')
                          + f'<text x="{x + bw / 2:.1f}" y="{base - h - 8:.1f}" text-anchor="middle" class="g-valor">{v if v else "—"}</text>'
                          f'<text x="{x + bw / 2:.1f}" y="{base + 22}" text-anchor="middle" class="g-eti">{esc(k)}</text></g>')
        svg = f'<svg viewBox="0 0 {ancho} {alto + 6}" class="grafico" role="img" aria-label="{esc(titulo)}">{"".join(partes)}</svg>'
    tabla = ('<details class="tabla-datos"><summary>Ver los datos en tabla</summary><table><tbody>'
             + ''.join(f'<tr><th scope="row">{esc(k)}</th><td>{v}</td></tr>' for k, v in filas) + '</tbody></table></details>')
    return f'<figure class="cifra"><figcaption>{esc(titulo)}</figcaption>{svg}{tabla}' + (f'<p class="nota-grafico">{esc(nota)}</p>' if nota else '') + '</figure>'


def cifras(total_sda, total_docentes, por_curso, docentes_curso, por_tema, con_zonas):
    tiles = (f'<dl class="totales"><div><dt>Situaciones de aprendizaje</dt><dd>{total_sda}</dd></div>'
             f'<div><dt>Docentes participantes</dt><dd>{total_docentes}</dd></div>'
             f'<div><dt>Aulas del Futuro</dt><dd>2</dd></div>'
             f'<div><dt>SdA con zonas registradas</dt><dd>{con_zonas}</dd></div></dl>')
    return (f'<section class="bloque" aria-labelledby="t-cifras"><h2 class="seccion-titulo" id="t-cifras">El proyecto en cifras</h2>{tiles}'
            f'<div class="graficos">{barras("Situaciones de aprendizaje por curso", por_curso, sufijo=" situaciones")}'
            f'{barras("Docentes participantes por curso", docentes_curso, sufijo=" docentes")}</div>'
            f'{barras("Situaciones de aprendizaje por ámbito", por_tema, nota="Ámbito asignado automáticamente según las materias y el texto de cada SdA.", horizontal=True, sufijo=" situaciones")}'
            '</section>')


# ---------- Avatares ----------
TONOS = [('#f7e4e9', '#7d0e2c'), ('#e2eee2', '#24552f'), ('#e3ecf5', '#24476b'), ('#f6ecd9', '#6e4a12'), ('#ece5f4', '#4d2f72'), ('#e0f0ee', '#1f5550')]


def avatar(nombre, grande=False):
    partes = [p for p in nombre.replace(',', ' ').split() if p[0].isupper()]
    ini = (partes[0][0] + (partes[1][0] if len(partes) > 1 else '')).upper() if partes else '?'
    fondo, tinta = TONOS[int(hashlib.sha1(nombre.encode()).hexdigest(), 16) % len(TONOS)]
    return f'<span class="avatar{" grande" if grande else ""}" style="background:{fondo};color:{tinta}" aria-hidden="true">{esc(ini)}</span>'
