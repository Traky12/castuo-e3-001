# Revisión del recorrido e3bundle

Alcance: index.html, crear.html, paquete.html y estilos. No modifica el verificador ni publica Pages.

Cambios: tres recorridos por objetivo; claves contrastadas fuera del paquete; separación VERIFIED/GO; entorno CLI aislado; salto al contenido; rejillas sin mínimo fijo superior al ancho disponible. Conserva referencias históricas de versión: no afirma equivalencia entre main y Pages.

Comprobación estática: IDs únicos, destinos internos existentes y salto al contenido en tres páginas. Revisión Chromium bloqueada por restricción de sockets; no se ha acreditado comportamiento a 360/768/1280, lector de pantalla ni conformidad CLI.

Aceptación pendiente: revisar claro/oscuro, 360 px/tablet/escritorio, teclado, lector de pantalla, carga/error/sin conexión y ocho escenarios criptográficos sobre SHA candidato. Autor de propuesta: asistente; revisor humano sin asignar. Sin aceptación independiente: NO_GO.


## Reparación autorizada · 2026-11-16
Se conserva el historial del intento local. La CI posterior del PR inicial registró UI/build sobre merge de prueba 2259ab32de1c177c06094d6205912aa03e64f23d (run 43752941253); no acredita este nuevo contenido.

Se reconstruyó el árbol de partida e1913eeeb9c2196c4dd998c36808bec2bcbc4e9c y se cotejaron sus blobs Git. El validador original del workflow source-cli-browser-parity reprodujo FAIL en .github/workflows/publish-pypi.yml antes de reparar el manifiesto. No se modifica ese workflow ni sus controles para ocultar el fallo.

Se separan instrucciones POSIX y PowerShell y se identifica su CLI histórico. Reproducción de los comandos en sistemas limpios PENDING. Regenerados manifiesto parcial y global. Pruebas del validador: candidato PASS; mutación, omisión y archivo añadido al índice se rechazan; restauración PASS. Esta evidencia solo cubre integridad del árbol. CI nueva, conformidad sobre SHA final y revisión humana PENDING. Sin merge ni despliegue.
