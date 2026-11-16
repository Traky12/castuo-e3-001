# PROPOSED: castuo-e3-001 → Castuo-system handoff governance (E3-001 side)

Status: DRAFT — READY FOR REVIEW
Authority: NONE
Production readiness: NOT ASSESSED
Deployment authorization: NONE
Human independent review: PENDING
Operational state: BLOCKED
As-of: 2026-11-16
Revision: 2

"READY FOR REVIEW" significa únicamente que el texto está completo para que una
persona lo revise (ver §10). No significa aprobado, ni listo para implementar, ni
GO. Este documento no autoriza staging, producción, despliegue ni promoción, y no
declara que ningún sistema esté en GO.

Convención de etiquetas:

- **[V]** verificado en archivos del repositorio o en la salida de un comando
  fechado en el Anexo A.
- **[I]** inferido de lo verificado.
- **[S]** suposición o propuesta, sin evidencia.
- **[CTX]** contexto del proyecto, no verificado desde este repositorio.

No se ha accedido a `Castuo-system` ni a ningún otro repositorio remoto para
redactar este documento: todo lo que se dice de él es **[CTX]**. Los datos que
caducan están fechados en el Anexo A y no forman parte del cuerpo normativo. El
documento no contiene secretos, claves, tokens, correos, cuentas, rutas locales ni
datos personales.

## 1. Propósito, alcance y no-goals

**Propósito.** Proponer cómo gobernaría `castuo-e3-001` la entrega de evidencia a
`Castuo-system`: qué entrega, qué espera del receptor, quién decide cada paso y qué
debe cumplirse antes de escribir código o esquemas.

**Alcance.** Es la perspectiva del emisor. Describe expectativas y recomendaciones
de `castuo-e3-001`; no son normas para `Castuo-system`.

**No-goals.**

- Implementar nada: ni esquemas, ni código, ni workflows, ni automatizaciones.
- Renombrar artefactos, código o workflows existentes.
- Un orquestador, cola o servicio de handoff.
- Que `castuo-e3-001` escriba o ejecute algo en `Castuo-system`.
- Afirmar producción, certificación, validación de campo, cumplimiento o
  independencia real de personas.
- Autorizar staging, despliegue o promoción.

**Documentos relacionados** (se referencian, no se redefinen aquí):

- `docs/KEY-LIFECYCLE.es.md`: modelo de confianza, alta, separación de funciones,
  rotación, revocación y custodia de claves.
- `docs/LEGAL-CLAIM-BOUNDARY.es.md`: límites de alegación, datos personales,
  cadena de custodia y tiempo, condiciones antes de piloto o promoción.
- `docs/OPERATING_RUNBOOK.es.md`: procedimiento operativo E3-001, incluida la
  gestión segura del secreto de publicación.
- `PROTOCOL.md`, `STATUS.md`, `GOVERNANCE.md`, `docs/E3-001.md`.
- `docs/architecture/PROPOSED-HANDOFF-CONTRACT.md`: borrador de arquitectura.

Este documento no establece jerarquía ni precedencia respecto a ninguno de ellos.
Si detecta una discrepancia, la señala como pregunta abierta (§14) para decisión
humana; no la resuelve por sí mismo.

## 2. Posición en la cadena y límites de autoridad

- `castuo-e3-001` **emite evidencia**. No decide ni promociona [V `GOVERNANCE.md`,
  `docs/E3-001.md`].
- `Castuo-system` es la autoridad canónica del estado técnico, de `staging-rls` y de
  la decisión de promoción [V como texto declarado en `docs/E3-001.md`; su
  funcionamiento real es **[CTX]**].
- `Castuo-system` conserva la autoridad sobre sus propios registros, controles y
  decisiones. Todo lo que este documento le atribuye es una expectativa o una
  recomendación del emisor.
- El flujo es **unidireccional y fail-closed**: del emisor hacia el receptor, sin
  escritura del emisor en el receptor [S].
- La evidencia puede **informar** una decisión; nunca la sustituye. Un resultado
  automático, una CI en verde o un PASS no son aprobación [V `GOVERNANCE.md`].
- Un handoff **no** transfiere autoridad ni reduce los controles propios del
  receptor.

## 3. Actores y separación de funciones

Los roles son **propuestos [S] y no tienen titular asignado**. Los controles sobre
claves (alta, revisión distinta del proponente, rotación y revocación) se rigen por
`docs/KEY-LIFECYCLE.es.md` y no se repiten aquí.

Leyenda: **E** ejecuta · **D** decide · **C** consultado · **I** informado ·
**✗** no debe participar.

| Actividad | Emisor | Runner externo | Revisor humano | Aceptante | Operador de staging | Promotor |
|---|---|---|---|---|---|---|
| Congelar el paquete y emitir el handoff | E, D | C | I | I | I | I |
| Ejecutar el replay y firmar la atestación | C | E, D | ✗ | I | I | I |
| Revisión humana y firma | C | ✗ | E, D | I | I | I |
| Revisar el informe de validación automática | C | I | C | E | I | I |
| Aceptar o rechazar el handoff | I | I | I | D | I | I |
| Solicitar y operar staging | I | I | I | C | E | I |
| Aceptar el resultado de staging | I | I | I | D | C | C |
| Decidir la promoción | I | I | I | C | I | D |
| Revocar un handoff emitido | E, D | I | I | I | I | I |

**Incompatibilidades [S]** (una misma persona no debe ocupar ambos roles):
emisor y runner; emisor y revisor; runner y revisor; emisor y aceptante; aceptante
y operador de staging; operador de staging y promotor; emisor y promotor. La
exigencia de que el runner no sea autor de la implementación ni del paquete ya
figura en `PROTOCOL.md` [V].

**Independencia.** `GOVERNANCE.md` describe un único mantenedor y `CODEOWNERS`
lista un único propietario [V]. **Con un único mantenedor, la independencia no puede
afirmarse.** Mientras una misma persona ocupe más de un rol incompatible, ni la
revisión independiente ni la separación de funciones están acreditadas. Una clave
inscrita acredita control de la clave, no independencia social
(`docs/KEY-LIFECYCLE.es.md`, "Límites de la afirmación") [V].

## 4. Ciclo de vida del handoff

Estados [S]: **EMITIDO → RECIBIDO → VALIDADO → ACEPTADO | RECHAZADO → CADUCADO |
REVOCADO**.

| Transición | La registra | Condición |
|---|---|---|
| (nada) → EMITIDO | Emisor | Handoff completo, con hash y `expires_at_utc` |
| EMITIDO → RECIBIDO | Receptor | Extraído por el receptor; registra el hash recibido |
| RECIBIDO → VALIDADO | Persona del receptor | Ha revisado el informe de validación automática y lo confirma |
| RECIBIDO → RECHAZADO | Persona del receptor | El informe es negativo o la persona no lo confirma |
| VALIDADO → ACEPTADO | Aceptante | Decisión humana explícita |
| VALIDADO → RECHAZADO | Aceptante | Decisión humana explícita |
| EMITIDO, RECIBIDO, VALIDADO → CADUCADO | Receptor | Supera `expires_at_utc` según su fuente de tiempo de confianza |
| ACEPTADO → CADUCADO | Receptor | Supera `expires_at_utc` |
| Cualquier estado no terminal → REVOCADO | Emisor (revoca) y receptor (registra) | Existe un registro de revocación que referencia `handoff_id` |

RECHAZADO, CADUCADO y REVOCADO son terminales. **Cada transición registra: rol, hora
UTC (según una fuente de tiempo de confianza) y los hashes de lo evaluado**
(`handoff_id`, hash del handoff y hash del informe de validación). **Una validación
automática propone; no decide.** Su salida se etiqueta `non-decisional`.

**Controles contra la reutilización [S].**

1. **`handoff_id` único.** Un `handoff_id` ya usado se rechaza.
2. **Registro de `handoff_id` usados.** Lo mantiene el receptor. Es estado
   persistente y hoy no tiene propietario (§14).
3. **`audience`.** Cada handoff nombra a su receptor destinatario; el receptor
   rechaza los que no le corresponden.
4. **Caducidad.** `expires_at_utc` está en el handoff; el receptor la evalúa con su
   propia fuente de tiempo de confianza, no con la hora que declara el payload.
5. **Revocación.** Un registro separado, con su propia integridad, referencia
   `handoff_id`. El receptor lo consulta antes de aceptar. Qué rol firma ese
   registro no está decidido (§14).
6. **Fuente de tiempo de confianza.** Una hora autodeclarada no equivale a un sello
   de tiempo de confianza (`docs/LEGAL-CLAIM-BOUNDARY.es.md` §1 y §5;
   `docs/KEY-LIFECYCLE.es.md`, "Rotación y revocación") [V]. Cuál es esa fuente
   está sin decidir (§14).

## 5. Contenido mínimo del handoff

El nombre, identificador y versión del esquema **no están asignados**: se usa
`<SCHEMA-NAME-TBD>`. Los nombres de campo son indicativos y no vinculantes. Los
marcados con **[V]** reflejan salidas ya emitidas por el validador de evidencia
externa o por el evaluador de E3-001; el resto es propuesta **[S]**.

**El handoff es inmutable.** Solo contiene hechos conocidos en el momento de emitirlo.
La aceptación, el staging y la promoción se registran en el receptor, referenciando
`handoff_id` (§4).

| Grupo | Campos obligatorios propuestos |
|---|---|
| Identidad y uso [S] | `handoff_id`, `schema_version`, `issued_at_utc`, `expires_at_utc`, `audience`, `scenario_id`, `protocol_id` |
| Origen y hashes [V parcial] | `source_commit` (40 hex), `rollback_ref`, `fixture_hash`, `result_hash`, `evidence_hash` |
| Emisor [S] | `emitter_repo`, `emitter_commit`, `validator_script_sha256`, `trust_store_sha256` |
| Validación [V parcial] | `validation.status`, `validation.mode`, `claim_boundary`, `findings[]`, `validation_report_sha256` |
| Gate de evidencia E3-EG [V parcial] | `evidence_gate.status`, `evidence_gate.staging_handoff_eligible` (solo dato de entrada), `oneR`, `oneV`, `oneA`, `promotion` |
| CI referenciada [S] | `ci.commit`, `ci.event`, `ci.runs[{run_id, workflow, conclusion}]`, `ci.queried_at_utc`, `ci.logs_reviewed` |
| Revisión humana [S] | `review.quorum`, `review.reviews_sha256`, `review.reviewer_refs[]` (opacas), `review.independence_attestation_sha256` |
| Límites [S] | `can_certify[]`, `cannot_certify[]` |
| Promoción [V] | `promotion` = `BLOCKED`, siempre |

**`staging_handoff_eligible`** es únicamente el dato que produce el evaluador E3 [V
`scripts/evaluate_g2.py`]. No es un estado de staging ni una solicitud.

**Excluido del handoff, de forma expresa:** `staging.state`, `staging.run_ref`,
cualquier estado de aceptación o de promoción, nombres, correos o cuentas de
personas, y secretos o claves privadas.

**Qué puede certificar la evidencia [I, a partir de `PROTOCOL.md`].** Dentro del
alcance declarado de S-001A, que un paquete congelado con `source_commit` y hashes
concretos fue reproducido por un runner con clave inscrita y revisado por dos
firmantes con clave inscrita.

**Qué no puede certificar [V `PROTOCOL.md`, `STATUS.md`,
`docs/LEGAL-CLAIM-BOUNDARY.es.md`].** Producción, operación en campo,
certificación, cumplimiento legal, ausencia de vulnerabilidades, ni autorización de
promoción. **[I]** Tampoco la independencia real de las personas: solo que sus
claves están inscritas. Una CI en `success` no sustituye nada de lo anterior.

## 6. Expectativas del emisor sobre el receptor (fail-closed)

`Castuo-system` decide sus propios controles. Lo que sigue es lo que
`castuo-e3-001` **espera y recomienda**, y **no es normativa para `Castuo-system`**
[S]. El emisor espera que un receptor prudente:

1. Rechace el handoff si falta un campo obligatorio, hay un campo desconocido,
   `promotion` no es `BLOCKED`, `oneA` no es `false`, `audience` no le
   corresponde o `expires_at_utc` ha pasado.
2. No dé crédito a `ci` ni al gate E3-EG copiados en el payload: reconsulte la CI y
   revalide los hashes contra el repositorio emisor.
3. Compruebe `trust_store_sha256` contra el trust store versionado y que las claves
   implicadas están vigentes y no revocadas, conforme a
   `docs/KEY-LIFECYCLE.es.md`.
4. Rechace un `handoff_id` ya usado o revocado.
5. Trate todo valor desconocido, ausente o no verificable como `BLOCKED` o
   `NO_CLAIM`, nunca como éxito.
6. Tome la decisión de aceptación con una persona, no con un resultado automático.

Quién implementa estas expectativas, y dónde viven, lo decide `Castuo-system`. Hoy
no existen implementadas en este repositorio [V].

## 7. Nomenclatura y mapeo hipotético

**Nomenclatura propuesta [S]** para evitar colisiones, solo en documentación; **no se
renombra ningún artefacto, código ni workflow existente**:

- **E3-EG**: el gate de evidencia del protocolo E3-001. En `evaluate_g2.py`,
  `STATUS.md` y `PROTOCOL.md` se llama "G2" [V].
- **CS-G1 … CS-G4**: los gates G1-G4 de Castuo-system (definiciones no reproducidas
  aquí).
- Los resultados automáticos se describen como `EVIDENCE_PASS` o `EVIDENCE_BLOCKED`,
  nunca como "aprobado".

**Mapeo hipotético [S].** No se ha leído `Castuo-system`. No se reproducen sus
definiciones de gate. Todo lo siguiente es hipótesis hasta que `Castuo-system` lo
confirme.

| Evidencia que E3-EG puede aportar [V] | Puede servir como entrada a | No puede cerrar |
|---|---|---|
| Procedencia: `source_commit`, hashes, firmas | Un gate de `Castuo-system` por determinar (CS-Gx) | La identidad real de las personas |
| Integridad: manifiesto y verificación Ed25519 | Un CS-Gx por determinar | La seguridad del sistema operativo |
| Replay sobre un fixture sintético | Ninguno por sí solo | Cualquier gate que exija dato real |
| Revisión humana del bundle | Un CS-Gx por determinar | Cualquier gate de cumplimiento u operación |

La evidencia puede aportar entrada a un gate; **nunca lo cierra por sí sola**
[S]. Cerrar un gate de `Castuo-system` es una decisión humana de `Castuo-system`.

## 8. Claves, privacidad y seguridad

**Claves.** Alta, separación de funciones, rotación, revocación y custodia se rigen
por `docs/KEY-LIFECYCLE.es.md`. Este documento no los redefine. Las claves privadas
nunca se guardan en Git, paquetes, informes ni logs [V `KEY-LIFECYCLE`].

**Credenciales entre repositorios [S].**

- Prohibida cualquier credencial de **escritura cruzada**: ni `castuo-e3-001` hacia
  `Castuo-system`, ni un repositorio público con credencial de escritura hacia uno
  privado.
- La **extracción la hace el receptor** con una credencial de **solo lectura**. El
  repositorio emisor es público [V `.castuo/repository-profile.yaml`], así que quizá
  ni siquiera necesite credencial; el mecanismo exacto está por decidir (§14).
- Los secretos de publicación se gestionan según `docs/OPERATING_RUNBOOK.es.md` (§8)
  y no se pegan en chats, issues, logs ni archivos versionados.

**Privacidad [S].**

- **El handoff público se limita a hashes y referencias.** No contiene datos de
  personas.
- El **roster de revisores** (quién es cada referencia) permanece en el **lado
  privado**.
- Una referencia opaca puede seguir siendo dato personal si es enlazable. Hay que
  evaluar la base jurídica, la minimización y la necesidad de una evaluación de
  impacto conforme a `docs/LEGAL-CLAIM-BOUNDARY.es.md` §3.
- **[V]** El modelo del trust store (`docs/KEY-LIFECYCLE.es.md`) registra
  `subject_id` y `approved_by` en un archivo que vive en un repositorio público.
  Si esos valores identifican a personas es una pregunta abierta (§14); este
  documento no la resuelve.

**Fugas por logs, artefactos y metadatos [S].** Antes de publicar cualquier handoff,
informe, log de CI o artefacto, una persona revisa que no revele: datos personales,
credenciales, nombres de repositorios privados, identificadores de ejecución que
permitan correlacionar actividad, ni tiempos que identifiquen a personas.
`docs/LEGAL-CLAIM-BOUNDARY.es.md` §3 prohíbe subir a repositorios públicos o logs de
CI datos identificables y credenciales [V].

**Retención [S].** El handoff, el registro de IDs usados, el informe de validación y
el registro de revocación deben tener una retención definida. Los plazos **no
están decididos** (§14).

## 9. Automatización

**Puede automatizarse [S]:** calcular y comparar hashes, validar estructura y
firmas, reconsultar la CI, generar informes etiquetados `non-decisional` y notificar
a una persona.

**No puede automatizarse [S]:** aceptar o rechazar un handoff, inscribir claves,
confirmar independencia, solicitar o aceptar staging, decidir la promoción,
conceder excepciones, publicar ramas o lanzar workflows de publicación.

**Prohibiciones.**

- Un PASS automático (E3-EG, CI o validador) **no** abre staging, no actualiza
  registros ni despliega sin una persona autorizada.
- `castuo-e3-001` no escribe directamente en `Castuo-system`.
- No se confía en un payload autodeclarado sin revalidación independiente.
- No se reutilizan handoffs antiguos.
- No se rellena el trust store con claves candidatas para que un gate pase
  (`docs/KEY-LIFECYCLE.es.md`, "Estado conservador") [V].
- **Ninguna IA aprueba, fusiona ni promociona** [V `GOVERNANCE.md`]. Un agente no
  revisa ni aprueba su propio cambio, y una cuenta de automatización no puede ser
  aprobadora requerida [S].
- Un snapshot que muestre "G2 PASS" no se presenta como aprobación.

**Trazabilidad [S].** Todo registro de decisión incluye rol, hora UTC, hashes de lo
evaluado y si fue una decisión humana o una salida automática. Las salidas
automáticas se marcan `non-decisional` y nunca figuran como la decisión.

## 10. Estados y definiciones

Este repositorio **no puede declarar GO**. GO es una decisión humana de la autoridad
canónica.

| Estado | Significa | Evidencia mínima | Decisión humana requerida | Quién lo declara | No autoriza |
|---|---|---|---|---|---|
| **BLOCKED** | Algún predicado incumplido o desconocido. Valor por defecto | — | Para salir de BLOCKED, una decisión registrada | Automático (fail-closed) o una persona | Nada |
| **READY FOR REVIEW** | Texto completo y autoconsistente para revisión humana | Criterios del §10.1 cumplidos | Ninguna todavía | El autor | Aprobación, implementación, staging |
| **READY FOR IMPLEMENTATION** | Se pueden escribir esquemas y código en ramas propias | Requisitos del §12 resueltos con evidencia; bloqueantes del §14 respondidos; revisión independiente de este documento registrada | Registro de decisiones firmado por una persona autorizada | Propietario del repositorio y un revisor independiente | Staging, producción, escritura en `Castuo-system` |
| **READY FOR STAGING** | Se puede solicitar `staging-rls` | Implementación revisada; pruebas fail-closed pasadas; handoff ACEPTADO; evidencia con claves inscritas; entorno de staging definido por `Castuo-system` | Aceptación del handoff y aprobación de la solicitud de staging | Autoridad de `Castuo-system` **[CTX]** | Producción; cada ejecución de staging necesita su propia autorización |
| **GO** | Decisión de pasar a una etapa operativa concreta y nombrada | Los gates aplicables de `Castuo-system` cerrados por esa autoridad; resultado de staging aceptado; reversión; revisión legal donde proceda | Decisión humana explícita y trazable, separada de cualquier PASS | **Solo la autoridad canónica [CTX].** Este repositorio no puede declararlo | — |

`PROTOCOL.md` establece que la promoción es una decisión separada que requiere un
objeto de autoridad y una decisión propios, y que staging no concede autorización
de producción [V].

**Estado actual de este documento y del sistema:** BLOCKED. No se cumplen READY FOR
IMPLEMENTATION, READY FOR STAGING ni GO [V Anexo A].

### 10.1 Criterios para declarar READY FOR REVIEW este documento

1. Cabecera íntegra, con `As-of` y `Revision`.
2. Toda afirmación no trivial lleva etiqueta; toda [V] indica archivo o comando y,
   si caduca, está fechada en el Anexo A.
3. Sin rutas locales, cuentas, correos, tokens, claves ni datos personales.
4. Sin lenguaje de aprobación afirmativa (GO, listo para producción, autorizado)
   salvo negado o dentro de las definiciones.
5. Todo el mapeo de gates marcado como hipótesis y sin reproducir definiciones de
   `Castuo-system`.
6. Referencias cruzadas a documentos existentes que resuelven.
7. Definidos los cinco estados del §10.
8. Coherente con `GOVERNANCE.md` y `docs/E3-001.md`.
9. El verificador del manifiesto pasa tras regenerarlo.
10. El cambio que lo incorpore no incluye código, esquemas ni workflows.
11. Cada pregunta abierta con propietario, qué desbloquea y evidencia necesaria.
12. Revisado por una persona distinta del autor antes de declararlo READY FOR
    REVIEW.

## 11. Integración con el PR #122

Todo lo siguiente es una propuesta **[S]**; el orden lo decide el propietario.

**Contexto [V a la fecha del Anexo A].** El PR #122 y la rama de este trabajo
modifican ambos el manifiesto raíz `SHA256SUMS.json`. No hay en el repositorio un
generador oficial del manifiesto. `main` usa finales de línea LF y la rama del PR
#122 lo reescribió en CRLF.

1. **Política LF** para el manifiesto raíz, coherente con `main`. Pendiente de
   confirmación del propietario.
2. **Integrar primero el PR #122.**
3. **Rebase posterior** de la rama de esta propuesta sobre el `main` resultante.
   Cualquier commit de esta rama que solo reparase el manifiesto puede quedar
   redundante tras integrar #122 [I]: comprobarlo antes de descartarlo.
4. **No resolver conflictos del manifiesto a mano.** Se toma el manifiesto de la
   base y se regenera.
5. **Regenerar en un commit exclusivo de manifiesto**, al final de la rama, tras el
   último cambio de contenido, con el algoritmo declarado en el propio manifiesto.
6. **Verificar tras cada rebase** con el verificador del workflow
   `source-cli-browser-parity`. Si falla, se regenera y se vuelve a verificar.
7. **Lo regenera una persona**, el integrador, y se revisa como cualquier cambio.
   **Ningún workflow con permisos de escritura regenera el manifiesto.**

## 12. Requisitos previos antes de implementar

| # | Requisito | Estado | Evidencia para cerrarlo |
|---|---|---|---|
| a | Acceso de solo lectura a `Castuo-system`, o exportación verificable de sus registros, esquemas y definiciones de gates | No resuelto | Exportación con hash o acceso confirmado |
| b | Runner externo real | No resuelto | Identidad verificada fuera de banda e inscripción de clave |
| c | Dos revisores humanos independientes | No resuelto | Identificación y confirmación de independencia |
| d | Protecciones reales de `main` y del entorno `public-snapshot` | No verificadas | Captura de la configuración real, con fecha |
| e | Consumidor real del snapshot firmado | No confirmado | Confirmación del propietario del consumidor |
| f | Estado actual de PyPI, Pages, GHCR y la Advisory API | No reverificado | Consultas fechadas |
| g | Mecanismo de transporte del handoff | Sin decidir | Decisión registrada |
| h | Firma del handoff y roles del trust store | Sin decidir | Decisión registrada; el modelo actual admite `runner`, `reviewer`, `publisher` [V] |
| i | Caducidad y fuente de tiempo de confianza | Sin decidir | Decisión registrada |
| j | Requisitos de privacidad para las referencias de revisores | Sin revisar | Revisión de protección de datos |
| k | Política LF y orden de integración con el PR #122 | Sin decidir | Decisión registrada |
| l | Propietario del registro de `handoff_id` usados y de la revocación | Sin decidir | Decisión registrada |

## 13. Entregables propuestos y orden de trabajo

Cada entregable va en una rama propia, con commits pequeños y manifiesto regenerado
y verificado, y es **revisable sin despliegue**. Cada paso de publicación (push, PR)
necesita autorización explícita aparte.

| # | Entregable | Criterios de aceptación |
|---|---|---|
| 1 | Registro de decisiones humanas | Plantilla con rol, hora UTC, evidencia y decisión; sin datos personales; primeras decisiones: política LF, nomenclatura E3-EG / CS-Gx, orden de integración |
| 2 | Informe de requisitos previos | Cada fila del §12 con su evidencia o con "sin evidencia" explícito |
| 3 | Documento de arquitectura revisado | Alineado con este documento, sin duplicar `KEY-LIFECYCLE` ni `LEGAL-CLAIM-BOUNDARY` |
| 4 | Límites y no-goals | Lista cerrada de lo que el handoff no certifica |
| 5 | Esquema versionado del handoff | **Solo tras responder los bloqueantes del §14.** Sin `staging.*`; con `audience` |
| 6 | Pruebas fail-closed | Un caso negativo por cada expectativa del §6 |
| 7 | Plan de verificación sin despliegue | Pasos reproducibles sin staging, producción ni credenciales de escritura |

## 14. Preguntas abiertas

La columna **Bloquea** indica si impide escribir esquemas o código.

| ID | Pregunta | Propietario | Desbloquea | Evidencia necesaria | Bloquea |
|---|---|---|---|---|---|
| Q1 | ¿Qué gates, registros y esquemas de evidencia existen realmente en `Castuo-system`? | Autoridad de `Castuo-system` | §7, §5, entregable 5 | Exportación verificable o acceso de lectura | Sí |
| Q2 | ¿Existe allí un esquema equivalente, para no crear arquitectura paralela? | Autoridad de `Castuo-system` | Entregable 5 | Inventario de esquemas | Sí |
| Q3 | ¿Se pueden publicar las definiciones de los gates CS-G1…CS-G4? | Propietario del repositorio | §7 | Decisión registrada | No |
| Q4 | ¿Quiénes son el runner externo y los dos revisores, y cómo se verifican independencia y posesión de claves? | Propietario y revisores | READY FOR IMPLEMENTATION | Identificación y verificación fuera de banda | Sí |
| Q5 | ¿Cómo se transporta el handoff y quién lo extrae? | Propietario y autoridad de `Castuo-system` | §8 y entregable 5 | Decisión registrada | Sí |
| Q6 | ¿Se firma el handoff? ¿Con qué rol del trust store y quién custodia la clave? ¿Qué rol firma la revocación? | Propietario | Entregable 5 | Decisión registrada | Sí |
| Q7 | ¿Nombre, identificador y versión del esquema? | Propietario | Entregable 5 | Decisión registrada | Sí |
| Q8 | ¿Se aprueba la nomenclatura E3-EG / CS-Gx? | Propietario | §7 | Decisión registrada | No |
| Q9 | ¿Qué referencia no personal identifica a los revisores, y cumple la normativa de protección de datos? ¿`subject_id` y `approved_by` del trust store identifican a personas? | Responsable de protección de datos (**sin titular asignado**) | §8 y entregable 5 | Revisión de protección de datos | Sí |
| Q10 | ¿Qué caducidad tiene el handoff y cuál es la fuente de tiempo de confianza? | Propietario y autoridad de `Castuo-system` | §4 | Decisión registrada | Sí |
| Q11 | ¿Quién mantiene el registro de `handoff_id` usados y el de revocaciones? | Autoridad de `Castuo-system` | §4 | Decisión registrada | Sí |
| Q12 | ¿Qué retención tienen handoff, informes, registro de usados y revocaciones? | Propietario y protección de datos | §8 | Decisión registrada | Sí |
| Q13 | ¿Cuáles son las protecciones reales de `main` y del entorno `public-snapshot`? | Propietario | §12 d | Captura fechada de la configuración | Sí |
| Q14 | ¿Quién consume el snapshot firmado y cómo valida la firma? | Propietario del consumidor | §12 e | Confirmación del consumidor | No |
| Q15 | ¿Estado actual de PyPI, Pages, GHCR y la Advisory API? | Propietario | §12 f | Consultas fechadas | No |
| Q16 | ¿Política LF, orden de integración con el PR #122 y quién regenera el manifiesto? ¿Se registra el procedimiento de regeneración como entregable? | Propietario | §11 | Decisión registrada | No |
| Q17 | ¿Se amplía el alcance del control de claims a estos documentos (cambio de código, futuro) o se usa una lista de verificación manual? | Propietario | §10.1 | Decisión registrada | No |

## Anexo A. Estado verificado a 2026-11-16 (no normativo)

Estos datos caducan. Hay que reverificarlos antes de actuar sobre ellos. Procedencia
de cada dato: archivos del repositorio y consultas de solo lectura a la API de CI
hechas el 2026-11-16.

- **[V]** `trust/e3-001-trust-store.json` está vacío (`keys: []`). Mientras siga así,
  ninguna evidencia externa real puede alcanzar `VERIFIED_FOR_G2`.
- **[V]** `STATUS.md` declara: replay independiente PENDING, atestación del runner
  PENDING, revisión humana firmada con quórum 0/2, E3-EG (en el archivo, "G2")
  REVIEW_REQUIRED, handoff a `staging-rls` BLOCKED, promoción BLOCKED.
- **[V]** `PROTOCOL.md` indica que el arnés de replay (`run_s001a_foreign_replay.py`)
  no está publicado en este repositorio.
- **[V]** `main` estaba en el commit `1cf8970`. El manifiesto raíz tenía 118
  entradas y no coincidía con `.github/workflows/publish-pypi.yml`; el workflow de
  paridad había fallado sobre `main` en un push del 2026-11-09.
- **[I]** Causa probable del desajuste: un bump de dependencias que cambió el
  workflow sin regenerar el manifiesto. No se ha verificado que sea la única causa.
- **[V]** El manifiesto raíz usa finales de línea LF en `main` y CRLF en la cabeza
  del PR #122. No hay en el repositorio un generador oficial del manifiesto: el
  algoritmo está declarado en el propio manifiesto y lo verifica el workflow de
  paridad.
- **[V]** La cabeza del PR #122 estaba en el commit `dd1abe1`; sus 8 workflows del
  evento `pull_request` terminaron en `success`. No se revisaron los logs de cada
  job. Ese resultado corresponde a ese commit, no a ninguna otra rama.
- **[V]** Ni la rama de este trabajo ni este documento estaban publicados en el
  remoto, por lo que no tienen CI.
- **No verificado:** todo lo relativo a `Castuo-system`, al runner y a los revisores
  reales, a las protecciones reales de `main` y de los entornos, al consumidor del
  snapshot y al estado actual de PyPI, Pages, GHCR y la Advisory API.

## Anexo B. Revisión

| Revisión | Estado |
|---|---|
| Revisión humana independiente de este documento | PENDIENTE |
| Decisiones registradas sobre las preguntas del §14 | NINGUNA |
