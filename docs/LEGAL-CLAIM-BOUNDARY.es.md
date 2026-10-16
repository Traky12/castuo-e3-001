# e3bundle — límites legales y criterios de alegación

**Revisado:** 14 de octubre de 2026  
**Estado:** guía de control documental; no es dictamen jurídico ni acredita conformidad.

## 1. Regla de interpretación

e3bundle es una herramienta local de integridad de ficheros y verificación de firmas criptográficas. Su resultado describe únicamente la entrada, las claves de confianza y la política usadas. No valida por sí mismo la verdad del contenido, la forma en que se capturó, la identidad civil del firmante, la independencia entre firmantes ni una cadena de custodia externa al paquete.

- **Integridad:** los ficheros declarados coinciden con el manifiesto según la verificación ejecutada.
- **Firma criptográfica:** la firma corresponde a los bytes firmados y a la clave pública comprobada.
- **Identidad:** la asociación entre una clave y una persona requiere un proceso separado.
- **Fecha fiable:** una fecha autodeclarada no es un sello de tiempo de confianza.
- **Verdad y calidad:** hash y firma no demuestran que la observación original sea cierta o correctamente capturada.
- **Custodia:** requiere controles de captura, transferencia, almacenamiento, acceso, retención y revisión.

## 2. Frontera eIDAS

La firma Ed25519 local de e3bundle no convierte automáticamente el resultado en firma electrónica avanzada o cualificada, sello electrónico cualificado, servicio cualificado de validación o sello de tiempo cualificado. Fijar claves expresa una política criptográfica local; no demuestra por sí solo identidad verificada, control exclusivo de los datos de creación de firma, revocación ni condición de prestador cualificado.

Antes de anunciar un caso como firma avanzada/cualificada o evidencia con valor probatorio específico, revisar el flujo completo frente al Reglamento (UE) n.º 910/2014 (eIDAS), sus modificaciones aplicables —incluido el Reglamento (UE) 2024/1183— y la normativa nacional relevante. Si el uso lo exige, seleccionar un prestador adecuado y verificar su condición en fuentes oficiales. No afirmar que e3bundle presta por sí mismo esos servicios.

## 3. Datos personales y RGPD

La demo está diseñada para verificar en el navegador; los ficheros y resultados no deben enviarse a los mantenedores ni publicarse como material de reproducción. La página legal distingue esta ejecución local de los metadatos técnicos que el proveedor de alojamiento puede registrar. No resumirlo como “no se trata ningún dato personal” sin considerar el alojamiento y los canales de colaboración.

Antes de un piloto con datos reales, documentar según corresponda:

1. finalidad y base jurídica de cada operación;
2. categorías de datos y personas afectadas, incluidas ubicaciones precisas, vídeo, imágenes, matrículas, operadores y terceros incidentales;
3. minimización, transparencia, permisos y controles de acceso;
4. retención, borrado, copias, seguridad y gestión de incidentes;
5. roles de responsable/encargado, acuerdos RGPD cuando procedan y transferencias internacionales;
6. cribado de necesidad de una evaluación de impacto (EIPD/DPIA), y su realización antes del tratamiento cuando sea exigible;
7. atención de derechos y solicitudes de supresión cuando proceda.

No subir a repositorios públicos, issues, logs de CI ni ejemplos compartidos imágenes identificables, coordenadas precisas, credenciales, claves privadas, dumps de bases de datos ni paquetes reales de campo. Usar fixtures sintéticos y evidencia redactada.

## 4. Reglamento de IA

e3bundle no es por sí mismo un sistema de decisión mediante IA. Si CASTÚO conecta modelos para detección, recomendaciones agronómicas o decisiones operativas, evaluar el sistema concreto, su finalidad prevista, contexto de uso y papel del proveedor/desplegador. No asignar categoría únicamente por usar IA ni presumir que un uso agronómico es o no de alto riesgo sin análisis.

Antes de habilitar una salida de IA en operación real: registrar clasificación y fundamento; comprobar el texto consolidado y calendario vigentes; documentar datos, límites, precisión y riesgos; exigir supervisión humana proporcional, trazas, capacidad de ignorar/revertir la salida y abstención segura. La IA operativa permanece fuera de alcance mientras esos controles y validaciones no estén demostrados. Las obligaciones específicas —incluidas las del artículo 14 para sistemas de alto riesgo cuando sean aplicables— dependen de la clasificación y del régimen vigente.

## 5. Cadena de custodia y tiempo

Para un uso probatorio, documentar captura y responsable, dispositivo/fuente, contexto temporal, manifiesto, firma, transferencias, almacenamiento, acceso, verificación, retención, rotación/revocación de claves e incidencias. Una verificación correcta solo cubre los controles ejecutados sobre el paquete recibido.

El sellado de tiempo RFC 3161 o un servicio cualificado no forman parte de una garantía implícita de e3bundle. Cualquier integración futura debe identificarse como componente separado y probar proveedor, política, verificación y tratamiento de fallos antes de promocionarla.

## 6. Redacción segura

**Permitido:**

> e3bundle permite crear, firmar y verificar paquetes de evidencia offline mediante manifiestos SHA-256 y firmas Ed25519. La verificación informa si los ficheros declarados coinciden con el manifiesto y si se cumple la política de firmas configurada. No certifica la verdad del contenido ni acredita por sí sola la identidad real de los firmantes.

**No afirmar sin evidencia específica:**

- que e3bundle certifica evidencia, es notario digital o garantiza la verdad del contenido;
- que una firma Ed25519 local equivale a firma avanzada o cualificada eIDAS;
- que existe sello de tiempo fiable/cualificado, identidad fuerte o revocación de claves si no se ha implementado y verificado;
- que el sistema cumple íntegramente RGPD, eIDAS o Reglamento de IA;
- que un paquete verificado valida una captura UAV/GIS, un piloto de campo o una decisión agronómica;
- que la herramienta está certificada, validada de forma independiente o autorizada para producción.

## 7. Condiciones antes de piloto o promoción

| Gate | Evidencia necesaria | Estado documentado disponible a 14/10/2026 |
|---|---|---|
| Publicación Python | Recuperación e instalación limpia desde el índice público | **BLOCKED / no confirmar** |
| Aviso de seguridad | Metadatos públicos que confirmen la versión corregida | **PENDING / no confirmar** |
| Demo Pages | URL pública alineada con el mismo candidato CLI y conformance | **PENDING**; README diferencia la demo sintética v0.1.1 del CLI alfa v0.1.3 |
| Reproducción independiente | Dos revisiones externas sustantivas, firmadas y ligadas a SHA/hashes | **0/2; PENDING** |
| Datos reales | Piloto autorizado, preflight de privacidad y protocolo de captura/custodia | **NOT DEMONSTRATED** |
| Producción/certificación | Evidencia operativa, revisión pertinente y autorización explícita | **NOT CLAIMED / BLOCKED** |

Este snapshot no afirma que se haya ejecutado un workflow nuevo el 14 de octubre. Verificar los registros enlazados antes de cambiar cualquier estado.

## 8. Fuentes oficiales de partida

- [Reglamento eIDAS (UE) n.º 910/2014](https://eur-lex.europa.eu/eli/reg/2014/910/oj)
- [Reglamento (UE) 2024/1183](https://eur-lex.europa.eu/eli/reg/2024/1183/oj)
- [Reglamento general de protección de datos (UE) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [Reglamento de IA: artículo 14 y supervisión humana](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14)
- [Calendario oficial de aplicación del Reglamento de IA](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [Aviso legal y privacidad de la demo](demo/legal.html)
- [Política de seguridad](../SECURITY.md)

Revalidar texto normativo, modificaciones, guías y fechas antes de cada piloto, oferta comercial o alegación de conformidad.
