# Aula del Futuro · IES Valle del Jerte

Web del proyecto Aula del Futuro del IES Valle del Jerte (Cabezuela del Valle y Navaconcejo). Recoge todo lo publicado en el Google Site desde el curso 2022-2023: 159 situaciones de aprendizaje, las fichas de los docentes y la transformación de los espacios.

Es un sitio estático: un archivo HTML por página, sin base de datos ni servidor. GitHub Pages lo publica solo cada vez que se sube un cambio.

## Cómo está organizado

| Ruta | Qué es |
| --- | --- |
| `datos/migrado.json` | Todo el contenido migrado del Google Site (cursos 22-23 a 25-26) |
| `nuevas/26-27/` | Situaciones de aprendizaje nuevas de este curso, una por archivo `.json` |
| `sitio_src/` | Estilos, JavaScript e icono de la web |
| `generar.py` | Crea la web a partir de los datos |
| `.github/workflows/publicar.yml` | Publica la web en GitHub Pages en cada cambio |

## Añadir una situación de aprendizaje de este curso

1. Sube las fotos a la carpeta de Drive de la SdA y compártelas como **"Cualquier persona con el enlace"**.
2. Copia `nuevas/26-27/_ejemplo.json` con un nombre nuevo, por ejemplo `nuevas/26-27/mision-cern.json`.
3. Rellena los campos y pega en `fotos` los enlaces de cada foto (Compartir › Copiar enlace).
4. Sube el archivo al repositorio. En un par de minutos aparece en la web, con su ficha, su tarjeta y en el buscador.

Las fotos no se suben a GitHub: se muestran directamente desde Drive. Así el repositorio no crece aunque se añadan cientos de fotos.

Los archivos que empiezan por `_` no se publican.

## Fotos de los cursos anteriores

Se muestran desde el Google Site original. Si algún día se borra el Site, habría que pasarlas a Drive antes.

## Probarla en tu ordenador

```sh
python3 generar.py datos/migrado.json sitio
python3 -m http.server -d sitio 8000
```

Y abre http://localhost:8000.

## Accesibilidad

La web se ha revisado con axe-core (WCAG 2.1 AA) en escritorio, móvil, modo claro y modo oscuro, sin errores. Se puede navegar con teclado, tiene enlace para saltar al contenido y el menú del móvil gestiona el foco.
