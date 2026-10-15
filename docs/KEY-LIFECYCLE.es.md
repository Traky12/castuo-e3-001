# Ciclo de vida de claves E3-001

## Estado actual

El archivo `trust/e3-001-trust-store.json` empieza deliberadamente con `keys: []`. Por tanto, las firmas Ed25519 autocontenidas dentro de un paquete **no autentican por sí solas** a un runner ni a un revisor, y la validación de evidencia externa debe detenerse en `BLOCKED` hasta que existan identidades aprobadas y verificadas fuera del paquete.

Esta política no altera la demo sintética: puede devolver `DEMO_VALIDATED`, pero nunca `VERIFIED_FOR_G2`, `oneV=true` ni autorización de promoción.

## Modelo de confianza

Cada entrada aprobada registra:

- `key_id`: identificador único e inmutable de esa versión de clave.
- `subject_id`: identidad exacta del runner o revisor.
- `role`: `runner`, `reviewer` o `publisher`; la clave de publicación debe ser distinta de las claves de runner y revisor.
- `public_key_b64`: clave pública Ed25519 en Base64 canónico; nunca una clave privada.
- `status`: `trusted` o `revoked`.
- `approved_by` y `approval_ref`: responsable y referencia de revisión que autorizó el alta.
- Si se revoca: `revocation_ref` y `revocation_reason`.

Los validadores rechazan identidades no inscritas, claves que no coinciden, claves revocadas, duplicados y más de una clave activa por identidad y rol. El cortafuegos del snapshot exige que `public_verification.key_id` y su clave pública coincidan con una entrada activa `role: publisher`; una clave incluida por el propio snapshot no crea confianza. Las claves públicas no se deben copiar del paquete candidato para incorporarlas al trust store: deben comprobarse mediante un canal externo y un procedimiento de prueba de posesión.

## Alta y separación de funciones

1. Verificar la identidad y el control de la clave por un canal independiente del paquete que se evaluará.
2. Crear una propuesta de cambio limitada al trust store con huella, identidad, rol, propósito, responsable y evidencia de aprobación.
3. Exigir una revisión distinta del proponente; el autor no puede autoaprobar el alta ni aprobar la publicación que depende de ella.
4. Comprobar que una misma clave no se comparte entre runner y revisores y que los revisores no reutilizan claves entre identidades.
5. Fusionar sólo después de que las revisiones requeridas y las comprobaciones del repositorio hayan pasado.

La entrada en el trust store es una decisión de confianza, no un resultado de CI. El commit que la incorpora y su revisión constituyen parte de la procedencia de esa decisión.

## Rotación y revocación

- **Rotación normal:** generar una clave nueva fuera del repositorio; verificar su titularidad; añadir una entrada nueva con nuevo `key_id`; aprobarla mediante revisión; y marcar como `revoked` la anterior en un cambio auditado. No se reutilizan IDs ni se reescribe el historial.
- **Compromiso o sospecha:** revocar inmediatamente la clave afectada mediante un cambio de emergencia revisado por una segunda persona, registrar motivo y referencia del incidente y volver a evaluar los paquetes firmados con esa clave.
- **Regla de evaluación:** las claves revocadas no satisfacen el umbral de confianza. No se confía en `signed_at` autocertificado para demostrar que una firma se creó antes de la revocación; sin una marca temporal de confianza, el tiempo declarado no resuelve esa duda.
- **Custodia:** las claves privadas permanecen en el dispositivo del titular o en un gestor de secretos aprobado. Nunca se guardan en Git, paquetes de evidencia, páginas web, informes de verificación ni logs.

La clave privada de publicación del snapshot tiene un uso y un límite distintos: debe permanecer únicamente en el environment protegido `public-snapshot`, disponible sólo para el job publicador aprobado. La clave pública correspondiente se inscribe como `role: publisher` tras verificar la huella por un canal externo y revisar la propuesta. No se introduce una clave real ni se desbloquea la publicación de forma automática.

## Límites de la afirmación

El trust store enlaza las claves autorizadas con identidades/roles aceptados por el proceso de gobernanza. No demuestra por sí solo independencia social, ausencia de conflicto de interés, calidad de la revisión, veracidad de los datos, validación de campo, seguridad completa o preparación para producción. Esos aspectos requieren evidencia separada.

**Estado conservador:** mientras el registro esté vacío o no haya claves verificadas, la validación externa y la publicación de snapshots permanecen bloqueadas. No se añadirán claves ficticias para conseguir un resultado verde.
