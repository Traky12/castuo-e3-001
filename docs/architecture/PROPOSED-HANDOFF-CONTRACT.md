# PROPOSED: castuo-e3-001 → Castuo-system handoff contract

Status: DRAFT — NOT APPROVED
Scope: architecture and governance proposal only
Authority: none
Production readiness: NOT ASSESSED
Deployment authorization: NONE
Human independent review: PENDING

Este documento es un borrador de trabajo. No es una aprobación, no es un GO,
no declara producción lista y no autoriza ningún despliegue. No añade
código, esquemas, workflows, manifiestos, claves ni dependencias.

Convención de etiquetas:

- **[V]** verificado en archivos de este repositorio.
- **[I]** inferido de lo verificado.
- **[S]** suposición o propuesta, sin evidencia.
- **[CTX]** dato de contexto del proyecto, no verificado desde este repositorio.

No se ha accedido a `Castuo-system` ni a ningún repositorio remoto para
redactar este documento. Todo lo que se dice de `Castuo-system` es **[CTX]**.

## 1. Mapa de componentes y responsabilidades

| Componente | Responsabilidad | Papel en el handoff |
|---|---|---|
| `castuo-evidence` | Fixture congelado y artefactos de replay [V, solo descrito en `docs/E3-001.md`] | Entrada |
| Runner externo y revisores humanos | Replay, atestación y firmas; fuera de ambos repositorios [V] | Entrada |
| `castuo-e3-001` | Protocolo, validador, evaluador G2 de solo lectura y contratos del paquete [V] | Emisor |
| `Castuo-system` | Autoridad canónica del estado técnico, gates, registros, `staging-rls` y decisión de promoción [CTX] | Receptor y decisor |
| Dashboards | Superficie de lectura del snapshot firmado; su consumo no está demostrado [V] | Fuera del handoff |

Regla de dirección **[S]**: el flujo es de un solo sentido. `castuo-e3-001`
emite evidencia y `Castuo-system` decide. El repositorio emisor no escribe ni
ejecuta nada en el receptor, y no actúa como gate. Es coherente con
`GOVERNANCE.md` y `docs/E3-001.md` [V], pero la regla concreta es una propuesta.

## 2. Contrato mínimo de handoff (nombre del esquema: por decidir)

El nombre, el identificador y la versión del esquema **no están asignados**.
En este documento se usa el marcador `<SCHEMA-NAME-TBD>`. Elegirlo es una
decisión abierta (ver §6).

Los campos se apoyan en artefactos que ya existen [V]:
`scripts/validate_external_evidence_bundle.py`, `scripts/evaluate_g2.py`,
`schemas/e3-manifest.schema.json` y `scripts/publish_public_snapshot.py`.
Se propone reutilizar el JSON canónico existente (`sort_keys`, separadores
compactos, `ensure_ascii`) y el formato de hash `sha256:<64 hex>` [S].

| Grupo | Campos obligatorios propuestos | Origen |
|---|---|---|
| Identidad | `handoff_id`, `schema_version`, `issued_at_utc`, `expires_at_utc`, `scenario_id`, `protocol_id` | manifiesto [V] y campos nuevos [S] |
| Hashes y origen | `source_commit` (40 hex), `rollback_ref`, `fixture_hash`, `result_hash`, `evidence_hash` | manifiesto [V] |
| Commit de evidencia | `emitter_repo`, `emitter_commit`, `validator_script_sha256`, `trust_store_sha256` | campos nuevos [S] |
| Decisión del validador | `validation.status`, `mode`, `g2_eligible`, `claim_boundary`, `findings[]`, `validation_report_sha256` | salida del validador [V] |
| Decisión del evaluador G2 | `g2.status`, `staging_handoff_eligible`, `oneR`, `oneV`, `oneA`, `promotion` | `evaluate_g2.py` [V] |
| CI oficial | `ci.commit`, `ci.event`, `ci.runs[{run_id, workflow, conclusion}]`, `ci.queried_at_utc`, `ci.logs_reviewed` | propuesto [S]; precedente local en la corrección de trazabilidad del PR #122, no disponible en main |
| Revisión humana | `review.quorum`, `review.reviews_sha256`, `review.reviewer_refs[]`, `review.independence_attested_by` | `reviewers.json` [V] y campos nuevos [S] |
| Staging | `staging.state`, `staging.run_ref` | snapshot [V] y campo nuevo [S] |
| Promoción | `promotion`, obligatoriamente `BLOCKED` en el handoff | [V] |
| Límites | `can_certify[]`, `cannot_certify[]`, `claim_boundary` | [S] |

Valores propuestos para `staging.state`: `NOT_REQUESTED`, `REQUESTED`, `BLOCKED`,
`PASSED_WITHIN_SCOPE`, `FAILED` [S].

**Datos personales.** El contrato no debe incluir identificadores personales de
revisores ni del runner (nombres, correos, cuentas de usuario). `reviewer_refs[]`
sería una referencia opaca, no personal. Si una referencia opaca (por ejemplo,
un identificador de clave) puede considerarse dato personal, y qué alternativa
usar, es una pregunta abierta (ver §6).

### Qué puede y no puede certificar la evidencia

- **Puede** acreditar, dentro del alcance declarado de S-001A, que un paquete
  congelado con `source_commit` y hashes concretos fue reproducido por un runner
  con clave inscrita y revisado por dos firmantes con clave inscrita [V
  `PROTOCOL.md`].
- **No puede** acreditar producción, operación en campo, certificación,
  cumplimiento legal, la independencia real de las personas (solo que sus claves
  están inscritas), ausencia de vulnerabilidades ni autorización de promoción
  [V `PROTOCOL.md`, `STATUS.md`].
- Una CI en `success` no sustituye ninguna de las anteriores.

### Reglas fail-closed propuestas para el receptor **[S]**

1. Rechazar si falta un campo obligatorio o hay uno desconocido, si
   `promotion` no es `BLOCKED`, si `oneA` no es `false` o si `expires_at_utc`
   ha pasado.
2. No fiarse de `ci` ni de `g2` copiados en el payload: reconsultar la CI y
   revalidar los hashes contra el repositorio emisor.
3. Comprobar que `trust_store_sha256` coincide con el trust store versionado y
   que las claves referidas están activas y no revocadas.
4. Rechazar un `handoff_id` ya usado.

### Transporte: propuesta, no decisión **[S]**

Se propone, como hipótesis a validar, que sea `Castuo-system` quien **extraiga**
el handoff (modelo pull) y no `castuo-e3-001` quien lo empuje. La razón
**inferida** [I] es evitar una credencial de escritura de un repositorio
público hacia uno privado. **No es un hecho**: no se ha comprobado cómo
`Castuo-system` obtendría el handoff, ni si puede hacerlo. Alternativas por
evaluar: PR abierto por una persona, activo adjunto a una release, o archivo en
un repositorio de evidencia. Cada una tiene un modelo de confianza distinto. La
elección es una decisión humana pendiente.

## 3. Mapeo G2 de E3-001 ↔ gates G1–G4 de Castuo-system — HIPÓTESIS

**Toda esta sección es hipótesis [S].** No se ha leído `Castuo-system`. Las
definiciones de G1–G4 provienen de contexto del proyecto **[CTX]** y pueden
estar desactualizadas o ser incorrectas. Ningún elemento de esta tabla es un
mapeo acordado, verificado ni aprobado.

Definiciones **[CTX]**, sin verificar: G1 Procedencia · G2 Integridad y
seguridad · G3 Dato real E2E · G4 Cumplimiento y operación.

| Predicado de E3-001 [V] | Gate de Castuo-system al que *podría* aportar (hipótesis) | Cobertura hipotética |
|---|---|---|
| `source_commit`, hashes, `evidence_hash`, firmas | G1 Procedencia | Parcial |
| Verificación Ed25519, manifiesto de árbol, claim firewall | G2 Integridad y seguridad | Parcial |
| Replay sobre fixture sintético | G3 Dato real E2E | Ninguna hipotética: el fixture no es dato real |
| Revisión humana | G4 Cumplimiento y operación | Ninguna hipotética: no hay revisión legal ni operativa |

Observación **[I]** apoyada solo en que ambos usan el nombre "G2": existe riesgo
de confusión terminológica entre el G2 de E3-001 (gate de evidencia del
protocolo [V]) y un posible G2 de `Castuo-system` [CTX]. Si se confirma que
son conceptos distintos, habrá que decidir cómo distinguirlos. Esa decisión, y
cualquier nombre alternativo, **no está tomada** (ver §6).

Cerrar un gate de `Castuo-system` sería siempre una decisión humana propia de
`Castuo-system`. Este documento no la anticipa.

## 4. Puntos de decisión humana obligatoria **[S]**

| # | Decisión | Rol |
|---|---|---|
| 1 | Inscribir claves de runner, revisores y publicador en el trust store, mediante un cambio revisado aparte | Propietario, con verificación fuera de banda |
| 2 | Confirmar la independencia del runner y de los revisores | Revisor independiente |
| 3 | Firmar dos revisiones sustantivas | Revisores externos |
| 4 | Aceptar o rechazar el handoff en `Castuo-system` | Responsable de gobernanza |
| 5 | Solicitar `staging-rls` | Operador autorizado, con revisores del entorno |
| 6 | Aceptar el resultado de staging | Responsable de staging |
| 7 | Decidir la promoción, decisión separada y no derivada del handoff | Propietario |
| 8 | Cambiar la versión del contrato o conceder excepciones | Propietario, mediante PR |

## 5. Riesgos de automatización excesiva

- **Disparo automático por G2 en PASS.** Que `staging_handoff_eligible=true`
  abra PRs, lance `staging-rls` o actualice registros sin intervención humana.
  Debe quedar prohibido [S].
- **Credencial entre repositorios.** Un workflow de un repositorio público con
  escritura a uno privado ampliaría la superficie de ataque [I].
- **Confianza en el payload.** Si el receptor no revalida, el emisor certifica
  lo que declare [I].
- **Reutilización de handoffs antiguos.** Sin `handoff_id`, caducidad y hashes,
  uno viejo valdría para un commit nuevo [I].
- **Claves añadidas para que el gate pase.** El trust store está vacío en este
  repositorio y `PROTOCOL.md` lo exige así hasta verificar identidades [V].
- **Decisión por un modelo de IA.** Ningún modelo debe aprobar, fusionar o
  promocionar. Lo declara `GOVERNANCE.md` [V] y es un principio del proyecto
  [CTX].
- **Lectura equivocada del snapshot.** Un dashboard que muestre "G2 PASS" como
  "aprobado". El snapshot mantiene `promotion: BLOCKED`, pero su consumo no
  está demostrado [V].

## 6. Preguntas abiertas antes de implementar nada

1. ¿Cuál es el contenido real de los gates y registros de `Castuo-system`? Sin
   verlo, el §3 sigue siendo una hipótesis.
2. ¿`Castuo-system` ya tiene un esquema de evidencia con el que este contrato
   debería alinearse, para no crear arquitectura paralela?
3. ¿Quiénes serán el runner externo y los revisores? Sin personas reales, el
   contrato no se puede ejercitar.
4. ¿Cómo se transporta el handoff y quién lo extrae? El §2 solo plantea una
   hipótesis.
5. ¿Se firma el handoff? El validador actual solo admite los roles `runner`,
   `reviewer` y `publisher` [V], de modo que otro rol exigiría cambiar código.
6. ¿Cuál es el nombre, identificador y versión del esquema? **No asignado.**
7. ¿Cómo se distingue el G2 de E3-001 de cualquier gate homónimo de
   `Castuo-system`? **No decidido.**
8. ¿Qué referencia no personal se usa para los revisores, y cumple los
   requisitos de protección de datos aplicables?
9. ¿Qué caducidad (`expires_at_utc`) es razonable?

## 7. Ubicación del contrato — propuesta

Tres opciones, sin decisión tomada:

| Opción | Ventajas | Inconvenientes |
|---|---|---|
| Solo en `castuo-e3-001/schemas/` | Público, versionado, junto al validador | El receptor decide sin ser dueño del contrato |
| Solo en `Castuo-system` | El receptor es dueño | Privado: los revisores externos no verían el contrato que firman [I] |
| En ambos, con fuente única | Cada lado ve su parte | Riesgo de duplicado y deriva si no hay una sola fuente de verdad |

Propuesta provisional **[S]**: esquema del payload con fuente única en
`castuo-e3-001/schemas/`, referenciado (no copiado) desde `Castuo-system` por
repositorio, etiqueta y SHA-256. Registro de decisiones (aceptación, resultado
de staging, promoción) solo en `Castuo-system`. Depende de confirmar antes que
`Castuo-system` no tenga ya un esquema equivalente (pregunta 2).

## 8. Qué no se propone

- Un orquestador, cola o servicio de handoff.
- Que `castuo-e3-001` escriba en `Castuo-system`.
- Cambiar el validador, los gates o sus nombres sin decisión del propietario.
- Poner este contrato en uso antes de resolver las preguntas 1, 2 y 3.

## 9. Evidencia pendiente

Todo lo relativo a `Castuo-system`, a los revisores y al runner reales, a la
protección de ramas y entornos en GitHub y a si algún dashboard consume el
snapshot. Este documento no puede afirmar nada sobre ello.
