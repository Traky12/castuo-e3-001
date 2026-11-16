# PROPOSED: castuo-e3-001 → Castuo-system handoff governance

Status: DRAFT — READY FOR REVIEW
Authority: NONE
Production readiness: NOT ASSESSED
Deployment authorization: NONE
Human independent review: PENDING
Operational state: BLOCKED

"READY FOR REVIEW" significa únicamente que el texto está completo para que una
persona lo revise. No significa aprobado, ni listo para implementar, ni GO (ver
§11). Este documento no autoriza staging, producción, despliegue ni promoción, y
no declara que ningún sistema esté en GO.

Convención de etiquetas:

- **[V]** verificado en archivos o salidas de comandos del repositorio.
- **[I]** inferido de lo verificado.
- **[S]** suposición o propuesta, sin evidencia.
- **[CTX]** contexto del proyecto, no verificado desde este repositorio.

Los datos de estado son de 2026-11-16 y caducan. Hay que reverificarlos antes de
actuar sobre ellos. No se ha accedido a `Castuo-system` ni a ningún repositorio
remoto para redactar este documento: todo lo que se dice de él es **[CTX]**. El
documento no contiene secretos, claves, tokens ni datos personales.

Complementa a `docs/architecture/PROPOSED-HANDOFF-CONTRACT.md` (propuesta de
arquitectura). Si ambos difieren, prevalece el que lleve una decisión humana
registrada; hoy ninguno la tiene.

## 1. Objetivo y no-goals

**Objetivo.** Definir cómo se gobernaría un handoff de evidencia desde
`castuo-e3-001` hacia `Castuo-system`: qué se entrega, qué comprueba el receptor,
quién decide cada paso y qué debe cumplirse antes de escribir código o esquemas.

**No-goals.**

- Implementar nada: ni esquemas, ni código, ni workflows, ni automatizaciones.
- Un orquestador, cola o servicio de handoff.
- Que `castuo-e3-001` escriba o ejecute algo en `Castuo-system`.
- Cambiar el validador, el trust store, los workflows o los nombres de gates sin
  decisión humana registrada.
- Afirmar producción, certificación, validación de campo, cumplimiento o
  independencia real de personas.
- Autorizar staging, despliegue o promoción.

## 2. Estado actual

### Verificado [V]

- Rama de trabajo `docs/handoff-contract-proposal`, con 2 commits sobre
  `origin/main` (`1cf8970`), sin publicar en el remoto.
  - `35eacd7`: corrige en `SHA256SUMS.json` el hash de
    `.github/workflows/publish-pypi.yml` (118 entradas).
  - `76a3bff`: añade `docs/architecture/PROPOSED-HANDOFF-CONTRACT.md` y lleva el
    manifiesto a 119 entradas.
  - El verificador del manifiesto pasa con 118 tras el primero y con 119 tras el
    segundo.
- `trust/e3-001-trust-store.json` está vacío (`keys: []`). Mientras siga así,
  ninguna evidencia externa real puede alcanzar `VERIFIED_FOR_G2`.
- `STATUS.md` declara: replay independiente PENDING, atestación del runner
  PENDING, revisión humana firmada con quórum 0/2, G2 REVIEW_REQUIRED, handoff a
  `staging-rls` BLOCKED, promoción BLOCKED.
- `PROTOCOL.md` indica que el arnés de replay (`run_s001a_foreign_replay.py`) no
  está publicado en este repositorio.
- El workflow de paridad (`source-cli-browser-parity`) falló sobre `main` en el
  push `1cf8970` (2026-11-09).
- Los 8 workflows del evento `pull_request` terminaron en `success` sobre
  `dd1abe1`, la cabeza del PR #122 (consulta del 2026-11-16). No se revisaron los
  logs de cada job.

### Inferido [I]

- El fallo de paridad sobre `main` se debe probablemente al desajuste de hash de
  `publish-pypi.yml` tras un bump de Dependabot. No se ha verificado que sea la
  única causa.
- La rama de la corrección de trazabilidad del PR #122 y esta rama modifican
  ambas `SHA256SUMS.json`. Quien se integre en segundo lugar tendrá que
  regenerarlo.
- La CI de la rama `docs/handoff-contract-proposal` no existe todavía; solo
  existirá si se publica la rama.

### Pendiente o bloqueado

- La corrección de trazabilidad del PR #122 está preparada en un worktree local y
  sin commit.
- No verificado: todo lo relativo a `Castuo-system`, al runner y a los
  revisores reales, a las protecciones reales de `main` y del entorno
  `public-snapshot`, al consumidor real del snapshot firmado y al estado actual
  de PyPI, Pages, GHCR y la Advisory API.

## 3. Contrato mínimo de handoff

El nombre, identificador y versión del esquema **no están asignados**. Se usa el
marcador `<SCHEMA-NAME-TBD>`. Los campos se apoyan en artefactos existentes [V]
(`validate_external_evidence_bundle.py`, `evaluate_g2.py`,
`schemas/e3-manifest.schema.json`, `publish_public_snapshot.py`). Se propone
reutilizar el JSON canónico existente y el formato `sha256:<64 hex>` [S].

| Grupo | Campos obligatorios propuestos [S] |
|---|---|
| Identidad | `handoff_id`, `schema_version`, `issued_at_utc`, `expires_at_utc`, `scenario_id`, `protocol_id` |
| Origen y hashes | `source_commit` (40 hex), `rollback_ref`, `fixture_hash`, `result_hash`, `evidence_hash` |
| Evidencia del emisor | `emitter_repo`, `emitter_commit`, `validator_script_sha256`, `trust_store_sha256` |
| Validador | `validation.status`, `mode`, `g2_eligible`, `claim_boundary`, `findings[]`, `validation_report_sha256` |
| Evaluador G2 | `g2.status`, `staging_handoff_eligible`, `oneR`, `oneV`, `oneA`, `promotion` |
| CI oficial | `ci.commit`, `ci.event`, `ci.runs[{run_id, workflow, conclusion}]`, `ci.queried_at_utc`, `ci.logs_reviewed` |
| Revisión humana | `review.quorum`, `review.reviews_sha256`, `review.reviewer_refs[]` (opacas), `review.independence_attested_by` |
| Staging | `staging.state` ∈ {`NOT_REQUESTED`, `REQUESTED`, `BLOCKED`, `PASSED_WITHIN_SCOPE`, `FAILED`}, `staging.run_ref` |
| Promoción | `promotion`, obligatoriamente `BLOCKED` en el handoff |
| Límites | `can_certify[]`, `cannot_certify[]`, `claim_boundary` |

**Datos personales.** El contrato no incluye nombres, correos ni cuentas de
personas. Las referencias de revisores son opacas. Si una referencia opaca puede
considerarse dato personal es una pregunta abierta (§10).

**Qué puede certificar la evidencia [V PROTOCOL.md].** Dentro del alcance
declarado de S-001A, que un paquete congelado con `source_commit` y hashes
concretos fue reproducido por un runner con clave inscrita y revisado por dos
firmantes con clave inscrita.

**Qué no puede certificar.** Producción, operación en campo, certificación,
cumplimiento legal, la independencia real de las personas (solo que sus claves
están inscritas), ausencia de vulnerabilidades ni autorización de promoción. Una
CI en `success` no sustituye nada de lo anterior.

## 4. Reglas fail-closed del receptor [S]

1. Rechazar si falta un campo obligatorio, hay un campo desconocido,
   `promotion` no es `BLOCKED`, `oneA` no es `false` o `expires_at_utc` ha pasado.
2. No fiarse de `ci` ni de `g2` copiados en el payload: reconsultar la CI y
   revalidar los hashes contra el repositorio emisor.
3. Comprobar que `trust_store_sha256` coincide con el trust store versionado y que
   las claves referidas están activas y no revocadas.
4. Rechazar un `handoff_id` ya usado.
5. Todo valor desconocido, ausente o no verificable se trata como `BLOCKED` o
   `NO_CLAIM`, nunca como éxito.

Quién implementa estas reglas y dónde viven es una decisión abierta (§10). Estas
reglas se describen aquí; no existen implementadas [V].

## 5. Mapeo hipotético entre el G2 de E3-001 y los gates de Castuo-system

**Toda esta sección es hipótesis [S].** No se ha leído `Castuo-system`. Las
definiciones de G1–G4 son **[CTX]**: G1 Procedencia · G2 Integridad y seguridad ·
G3 Dato real E2E · G4 Cumplimiento y operación. Pueden estar desactualizadas.

En este repositorio, "G2" es el gate de evidencia del protocolo E3-001
(`evaluate_g2.py`), que mantiene siempre `oneA: false` y `promotion: BLOCKED`
[V]. Un PASS no es promoción.

| Evidencia de E3-001 [V] | Gate al que *podría* aportar (hipótesis) | Puede aportar | No puede cerrar |
|---|---|---|---|
| `source_commit`, hashes, firmas | G1 Procedencia | Cadena de hash y firma sobre el paquete | La identidad real de las personas |
| Verificación Ed25519, manifiesto de árbol, claim firewall | G2 Integridad y seguridad | Integridad del bundle | La seguridad del sistema |
| Replay sobre fixture sintético | G3 Dato real E2E | Nada | El gate (el fixture no es dato real) |
| Revisión humana del bundle | G4 Cumplimiento y operación | Nada | El gate (no hay revisión legal ni operativa) |

Ninguna evidencia de E3-001 cierra un gate de `Castuo-system`: aporta entrada.
Cerrar un gate es una decisión humana propia de `Castuo-system`. Si "G2" resulta
tener un significado distinto allí, cómo distinguirlos está sin decidir (§10).

## 6. Puntos de decisión humana obligatoria [S]

| # | Decisión | Rol |
|---|---|---|
| 1 | Inscribir claves de runner, revisores y publicador en el trust store, mediante un cambio revisado aparte | Propietario, con verificación fuera de banda |
| 2 | Confirmar la independencia del runner y de los revisores | Revisor independiente |
| 3 | Revisión humana sustantiva y firma de dos revisiones | Revisores externos |
| 4 | Aceptar o rechazar el handoff en `Castuo-system` | Responsable de gobernanza |
| 5 | Solicitar `staging-rls` y aceptar su resultado | Operador autorizado y responsable de staging |
| 6 | Decidir la promoción, decisión separada y no derivada del handoff | Propietario |
| 7 | Cambiar el contrato, los nombres de gates o conceder excepciones | Propietario, mediante PR |
| 8 | Publicar ramas, abrir PR, crear releases o lanzar workflows | Propietario |

## 7. Prohibiciones de automatización excesiva

- Un PASS automático (G2, CI o validador) no abre staging, no actualiza registros
  y no despliega sin una persona autorizada.
- `castuo-e3-001` no escribe directamente en `Castuo-system`, ni con credenciales
  cruzadas de un repositorio público a uno privado.
- No se confía en un payload autodeclarado sin revalidación independiente.
- No se reutilizan handoffs antiguos.
- No se rellena el trust store con claves candidatas para que un gate pase.
- Ninguna IA aprueba, fusiona ni promociona, y ningún agente se autoaprueba.
- Un snapshot que muestre "G2 PASS" no se presenta como aprobación.

## 8. Requisitos previos antes de implementar

| # | Requisito | Estado |
|---|---|---|
| a | Acceso de solo lectura a `Castuo-system`, o exportación verificable (con hash) de sus registros, esquemas y definiciones de gates | No resuelto |
| b | Runner externo real definido | No resuelto |
| c | Dos revisores humanos independientes identificados | No resuelto |
| d | Protecciones reales de `main` y del entorno `public-snapshot` | No verificadas (el perfil del repo las declara, sin comprobación) |
| e | Consumidor real del snapshot firmado | No confirmado |
| f | Estado actual de PyPI, Pages, GHCR y Advisory API | No reverificado |
| g | Mecanismo de transporte del handoff (¿extracción por `Castuo-system`? es hipótesis [S]) | Sin decidir |
| h | Firma del handoff y roles del trust store (hoy solo `runner`, `reviewer`, `publisher` [V]) | Sin decidir |
| i | Caducidad del handoff | Sin decidir |
| j | Requisitos de privacidad y protección de datos para las referencias de revisores | Sin revisar |
| k | Orden de integración con el PR #122 y quién regenera `SHA256SUMS.json` | Sin decidir |

## 9. Entregables propuestos y orden de trabajo

Cada entregable va en una rama propia, con commits pequeños, manifiesto
regenerado y verificado, CI revisada y revisión humana antes del siguiente. Cada
paso de publicación (push, PR) necesita autorización explícita aparte.

1. Registro de decisiones humanas.
2. Documento de arquitectura (evolución de `PROPOSED-HANDOFF-CONTRACT.md`).
3. Documentación de límites y no-goals.
4. Esquema versionado del handoff. **Solo tras responder §10.**
5. Pruebas de validación fail-closed, un caso negativo por regla de §4.
6. Plan de verificación sin despliegue.

## 10. Preguntas abiertas

1. ¿Qué gates, registros y esquemas de evidencia existen realmente en
   `Castuo-system`?
2. ¿Existe ya allí un esquema equivalente, para no crear arquitectura paralela?
3. ¿Quiénes son el runner externo y los dos revisores, y cómo se verifican su
   independencia y la posesión de sus claves?
4. ¿Cómo se transporta el handoff y quién lo extrae?
5. ¿Se firma? ¿Con qué rol del trust store y quién custodia la clave?
6. ¿Cuál es el nombre, identificador y versión del esquema?
7. ¿Cómo se distingue el G2 de E3-001 de cualquier gate homónimo?
8. ¿Qué referencia no personal identifica a los revisores y qué exige la
   normativa de protección de datos aplicable?
9. ¿Qué caducidad tiene el handoff?
10. ¿Cuáles son las protecciones reales de `main` y del entorno `public-snapshot`?
11. ¿Quién consume el snapshot firmado y cómo valida la firma?
12. ¿Cuál es el estado actual de PyPI, Pages, GHCR y la Advisory API?
13. ¿En qué orden se integra con el PR #122 y quién regenera `SHA256SUMS.json`?
14. ¿Se publica la rama `docs/handoff-contract-proposal` y se abre PR? Decisión
    aparte, con la CI revisada.

## 11. Definiciones: READY FOR IMPLEMENTATION y GO

### READY FOR IMPLEMENTATION (propuesta [S])

Significaría que una persona autorizada ha registrado, por escrito y con
evidencia, que se cumplen **todas** estas condiciones:

1. Los requisitos a–k de §8 están resueltos y cada uno tiene su evidencia.
2. Las preguntas de §10 están respondidas con una decisión humana registrada.
3. El nombre, identificador y versión del esquema están decididos.
4. Este documento y el de arquitectura tienen revisión humana independiente
   registrada.
5. El registro de decisiones humanas (§9, entregable 1) existe.

READY FOR IMPLEMENTATION autoriza únicamente a escribir esquemas y código en
ramas propias, sujetos a revisión. **No** autoriza staging, producción,
despliegue, promoción ni escritura en `Castuo-system`.

**Estado actual: NO se cumple.** Los requisitos a–k siguen sin resolver [V].

### GO (propuesta [S])

GO sería una decisión humana tomada por la autoridad canónica
(`Castuo-system`, según [CTX]), registrada allí, que acepta pasar a una etapa
operativa concreta y nombrada. Este repositorio no define ni puede declarar GO.
Según el propio protocolo, la promoción es una decisión separada que requiere un
objeto de autoridad y una decisión propios [V PROTOCOL.md].

GO presupondría, como mínimo y sin limitarse a ello:

1. Los gates aplicables de `Castuo-system` cerrados por esa autoridad.
2. Revisión humana independiente real, con claves inscritas y verificadas.
3. Resultado de staging aceptado, con evidencia de reversión y revisión legal
   donde corresponda.
4. Una decisión humana explícita y trazable, separada de cualquier PASS
   automático.

**Estado actual: NO hay GO.** El estado operativo es BLOCKED y la promoción está
BLOCKED [V]. Ningún documento de este repositorio, ni una CI en verde, ni este
borrador lo cambian.

## 12. Revisión

| Revisión | Estado |
|---|---|
| Revisión humana independiente de este documento | PENDIENTE |
| Decisiones registradas sobre las preguntas de §10 | NINGUNA |
