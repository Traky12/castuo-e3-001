# Runbook de publicación de e3bundle en PyPI

**Estado operativo a 2026-10-11: BLOQUEADO en Trusted Publishing.**  
Fuente de estado: [run 38088766020](https://github.com/Traky12/castuo-e3-001/actions/runs/38088766020), release GitHub [v0.1.3 alpha](https://github.com/Traky12/castuo-e3-001/releases/tag/v0.1.3).

## 1. Objetivo y límites

Publicar `e3bundle` en PyPI mediante GitHub Actions Trusted Publishing (OIDC), sin guardar una API token de larga duración. Mantener separadas estas afirmaciones:

`BUILD_PASS ≠ OIDC_AUTHORIZED ≠ PYPI_PUBLISHED ≠ CLEAN_INSTALL_PASS ≠ DEPLOYMENT_PASS ≠ INDEPENDENT_VALIDATION`.

Ningún release se considera distribuido por PyPI hasta que exista una versión consultable en el índice público y supere la verificación de instalación y comportamiento.

## 2. Secuencia de estados y cierre

| Estado | Evidencia mínima | Transición permitida |
|---|---|---|
| `PREPARED` | Tag inmutable y versión de `pyproject.toml` coincidente | Ejecutar build/test |
| `BUILD_PASS` | Tests, build de sdist/wheel y smoke test en venv limpio en verde | Intentar Trusted Publishing solo si no hay un fallo conocido pendiente de diagnóstico |
| `OIDC_MATCH` | Job `publish` completa sin `invalid-publisher` y PyPI acepta la identidad | Verificar proyecto/versión públicos |
| `PYPI_PUBLISHED` | PyPI muestra exactamente la versión de la release y artefactos esperados | Instalar en entorno limpio |
| `CLEAN_INSTALL_PASS` | Instalación limpia más caso válido y manipulado con salidas/exit codes previstos | Validar gates posteriores |
| `POST_RELEASE_GATES` | Aviso de seguridad, demo Pages y metadatos legales verificados para el mismo commit/version | Considerar captación de testers |
| `RELEASE_UNBLOCKED` | Todos los anteriores con URLs, SHA/commit y resultados registrados | Cierre del proceso de publicación |

Un estado fallido no se salta por estar en verde otro job. No se declara cerrado un gate usando capturas antiguas, estados inferidos o la salida de un paso anterior.

## 3. Configuración del Trusted Publisher

En [PyPI → Manage account → Publishing](https://pypi.org/manage/account/publishing/), los valores esperados del pending publisher para la primera publicación son:

| Campo | Valor exacto |
|---|---|
| PyPI Project Name | `e3bundle` |
| Owner | `Traky12` |
| Repository name | `castuo-e3-001` |
| Workflow name | `publish-pypi.yml` |
| Environment name | `pypi` |

El workflow vigente es `.github/workflows/publish-pypi.yml`, el job publica con `environment: pypi` y `permissions: id-token: write`. No usar el path completo del workflow en el campo que pide solo el nombre del fichero; no incluir `Traky12/` en Repository name; no sustituir el environment por `p`.

El mensaje de alta confirma que se envió el formulario, pero no sustituye la inspección de la fila persistida bajo **Pending publishers**. Guardar esa fila como evidencia no secreta en el registro del incidente (no necesita incluir datos de autenticación).

## 4. Caso actual: `invalid-publisher`

Evidencia de [run 38088766020](https://github.com/Traky12/castuo-e3-001/actions/runs/38088766020):

- `build`: `success`. Pasaron comprobación versión/tag, tests, sdist/wheel y smoke test en venv limpio.
- `publish`: `failure` al intercambiar la identidad con PyPI.
- Error devuelto: `invalid-publisher: valid token, but no corresponding publisher (Publisher with matching claims was not found)`.
- Claims observados: `repository=Traky12/castuo-e3-001`, `repository_owner=Traky12`, `repository_owner_id=202805065`, `workflow_ref=Traky12/castuo-e3-001/.github/workflows/publish-pypi.yml@refs/tags/v0.1.3`, `ref=refs/tags/v0.1.3`, `environment=pypi`.
- El claim `sub` observado es `repo:Traky12@202805065/castuo-e3-001@1341612953:environment:pypi`.

### Señal adicional que debe comprobarse

GitHub informa que los repositorios creados después del 15 de julio de 2026 reciben por defecto un `sub` OIDC inmutable con IDs de propietario y repositorio. Este repositorio fue creado el 21 de agosto de 2026, y el claim observado coincide con ese formato. Véase [GitHub: Immutable subject claims](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims) y el [anuncio oficial](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/).

Esto es una **pista de compatibilidad que se debe investigar, no una causa raíz confirmada**. PyPI define `invalid-publisher` como un token válido que no coincide con ningún publisher configurado; su [guía de diagnóstico](https://docs.pypi.org/trusted-publishers/troubleshooting/) recomienda comparar claims y configuración. PyPI mantiene abierta la solicitud [warehouse #19347 — Generic OIDC support](https://github.com/pypi/warehouse/issues/19347), que describe problemas potenciales cuando el `sub` se personaliza. Esa solicitud no prueba por sí sola que el formato actual sea la causa de este fallo.

## 5. Procedimiento frente a un fallo de identidad

1. Abrir el log del job fallido y conservar el enlace del run, intento, fecha y texto exacto del error.
2. Verificar la fila guardada en la página **Publishing**. Comparar, carácter por carácter, project, owner, repository, workflow filename y environment con la tabla anterior.
3. Comparar los claims no secretos del log con los campos del publisher. No copiar ni solicitar tokens OIDC, API tokens, códigos de recuperación, cookies o valores de secretos.
4. Si hay una diferencia, corregir únicamente ese campo en PyPI y registrar la evidencia antes de reintentar.
5. Si la fila ya coincide exactamente y reaparece `invalid-publisher`, **detener reintentos**. Abrir una consulta de soporte PyPI/reproducible con el run URL, workflow name, repository IDs y claims no secretos; señalar el formato inmutable de `sub`. No afirmar que el publisher está mal configurado hasta descartar la incompatibilidad.
6. No migrar a una API token `twine`, no guardar una credencial larga en GitHub y no desactivar salvaguardas de identidad como solución automática. Cualquier excepción de publicación manual requiere revisión explícita, alcance mínimo, almacenamiento en un secret manager y revocación documentada al terminar.

**Regla de reintento:** máximo un reintento después de una corrección identificada y registrada. Un nuevo fallo debe producir diagnóstico/escalado, no más repeticiones.

## 6. Verificación posterior a la primera publicación

Cuando `publish` finalice correctamente:

1. Confirmar [PyPI project e3bundle](https://pypi.org/project/e3bundle/) y que `0.1.3` está publicado. Una release de GitHub, el contenedor GHCR o un build verde no cuentan como publicación PyPI.
2. Instalar `e3bundle==0.1.3` en un virtualenv recién creado desde PyPI (no desde Git y no desde caché) y guardar versiones/comandos/resultados.
3. Ejecutar el bundle válido: debe dar `VERIFIED` y exit code `0`; el bundle manipulado: `FAILED` y exit code `1`.
4. Confirmar el estado público y la versión corregida del aviso `GHSA-55pc-7v4h-jf7c`.
5. Confirmar el despliegue de Pages con `deploy=success`; verificar la demo pública y `legal.html` frente a la misma versión/commit, y comprobar la existencia de los GitHub Actions secrets `DEMO_LEGAL_NIF`, `DEMO_LEGAL_ADDRESS` y `DEMO_LEGAL_EMAIL` sin mostrar sus valores.
6. Solo entonces actualizar el README y la issue de testers a la versión realmente publicada, y reanudar la captación de testers independientes.

## 7. Registro mínimo de cada intento

Registrar en la issue de seguimiento existente:

- URL y run ID + attempt.
- SHA del tag/release y resultado de cada job.
- Error literal y claims OIDC no secretos relevantes.
- Resultado de inspección de la fila PyPI: coincide / no coincide; no guardar secretos.
- Cambio correctivo o razón del escalado.
- Resultado de publicación, instalación limpia, casos válido/manipulado, advisory y Pages cuando existan.

No crear issues duplicadas para cada repetición; añadir cada transición a [issue #30](https://github.com/Traky12/castuo-e3-001/issues/30).

## Referencias operativas

- [PyPI Trusted Publishers — troubleshooting](https://docs.pypi.org/trusted-publishers/troubleshooting/)
- [PyPI — creating a project through OIDC](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
- [PyPI Warehouse #19347 — Generic OIDC support](https://github.com/pypi/warehouse/issues/19347)
- [GitHub OIDC immutable subject claims](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims)
