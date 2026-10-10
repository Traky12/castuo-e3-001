# Publicación de los datos legales de la demo

El archivo versionado `docs/demo/legal.html` es una plantilla. No añadas un NIF, domicilio particular o correo personal real al HTML, a un commit, a una issue o a un comentario.

## Configuración necesaria

En GitHub, abre **Settings → Secrets and variables → Actions → New repository secret** y configura, solo si autorizas su publicación en la página legal pública:

- `DEMO_LEGAL_NIF`
- `DEMO_LEGAL_ADDRESS`
- `DEMO_LEGAL_EMAIL`
- `DEMO_LEGAL_COURT_CITY`

Los valores no se imprimen en logs y no se guardan en el repositorio. El workflow los inyecta en el artefacto de GitHub Pages únicamente durante una compilación que no sea de pull request. **El resultado publicado es una web pública** y mostrará esos datos; los secretos evitan que queden en el historial de Git, no que puedan verse o copiarse desde la página publicada.

Si falta alguno, la puerta de publicación queda cerrada. No se debe rellenar un dato por inferencia ni activar Pages para saltarse el control.

## Estado de release

La configuración de secretos no crea una release ni resuelve el aviso de seguridad. La publicación sigue condicionada a la revisión/fusión del arreglo de seguridad, la versión corregida aprobada, la release GitHub, el paquete PyPI y la imagen GHCR, además de los controles de conformance y UI. No se debe etiquetar ni publicar una versión hasta cumplir esos requisitos.
