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

### Corrección del diagnóstico OIDC — revisión del 14/10/2026

El claim observado `sub=repo:Traky12@202805065/castuo-e3-001@1341612953:environment:pypi` contiene IDs inmutables, pero **eso no debe tratarse como la causa principal**. Warehouse fusionó [PR #19422 el 29/01/2026](https://github.com/pypi/warehouse/pull/19422), que elimina la comprobación de `sub` para Trusted Publishers de GitHub porque los claims estructurados correspondientes se validan por separado. El [issue #19347](https://github.com/pypi/warehouse/issues/19347) sigue abierto para soporte OIDC genérico/personalizado; no prueba que el flujo GitHub→PyPI aquí sea incompatible.

`invalid-publisher` solo permite concluir que no se encontró un publisher que coincidiera con las reclamaciones recibidas. La causa concreta sigue **UNCONFIRMED**. Por prioridad:

1. Confirmar en el ámbito/cuenta de PyPI correcto que el Pending Publisher de `e3bundle` realmente aparece guardado y no solo que el formulario se envió.
2. Comparar los campos guardados, carácter por carácter, con los claims no secretos de la ejecución: nombre de proyecto, owner/cuenta, repositorio, nombre de fichero del workflow y environment. Revisar espacios al inicio/final, selector de cuenta/proyecto y nombre exacto del workflow.
3. Si la interfaz indica que existe y todo parece coincidir, no inferir que los datos persistidos son idénticos a lo que evalúa Warehouse. Registrar la discrepancia y pedir a soporte que confirme el registro persistido usando el run URL y los valores no secretos. Un reporte similar, [Warehouse #20504](https://github.com/pypi/warehouse/issues/20504), recibió respuesta del mantenedor indicando que no había fila pendiente para el proyecto del reportante; ese caso solo ilustra la necesidad de confirmar persistencia, no establece la causa de e3bundle.
4. No publicar JWT OIDC, API tokens, cookies, credenciales ni valores de secretos. No comentar repetidamente en issues de terceros; usar el canal oficial de soporte y el seguimiento propio existente.

## 5. Procedimiento frente a un fallo de identidad

1. Abrir el log del job fallido y conservar el enlace del run, intento, fecha y texto exacto del error.
2. Verificar la fila guardada en la página **Publishing**. Comparar, carácter por carácter, project, owner, repository, workflow filename y environment con la tabla anterior.
3. Comparar los claims no secretos del log con los campos del publisher. No copiar ni solicitar tokens OIDC, API tokens, códigos de recuperación, cookies o valores de secretos.
4. Si hay una diferencia, corregir únicamente ese campo en PyPI y registrar la evidencia antes de reintentar.
5. Si los campos visibles coinciden y la existencia/alcance del registro está confirmada, **detener los reintentos OIDC** y escalar por soporte con el run URL, nombre/ID del workflow, referencia/tag, IDs del repo/owner, claims no secretos y resultado de la comparación. Solicitar confirmación del registro persistido; no enviar JWT OIDC, API tokens, códigos de recuperación ni otros secretos.
6. Solo si la primera publicación es urgente y el titular acepta expresamente el riesgo, puede evaluarse la contingencia de subida manual controlada con Twine. No usarla para fingir que Trusted Publishing quedó resuelto. Para un proyecto aún no creado, el token puede requerir un alcance amplio; debe crearlo el titular, usarlo únicamente en su terminal y revocarlo inmediatamente tras comprobar la subida. Nunca compartirlo en chat, guardarlo en GitHub ni añadirlo como secreto permanente.
7. No cambiar el `sub` de GitHub ni reducir la protección OIDC automáticamente. Cualquier ajuste de seguridad debe pasar por una evaluación de compatibilidad y por la evidencia de la configuración real.

**Regla de reintento:** máximo un reintento después de una corrección identificada y registrada. Un nuevo fallo debe producir diagnóstico/escalado, no más repeticiones.

### Contingencia Twine: subida manual única (solo con autorización consciente del titular)

El build ya produjo artefactos para el tag `v0.1.3` en [run 38088766020](https://github.com/Traky12/castuo-e3-001/actions/runs/38088766020). El artefacto `dist` contiene estos dos ficheros y hashes, calculados sobre los bytes descargados en esta sesión:

| Fichero | SHA-256 |
|---|---|
| `e3bundle-0.1.3-py3-none-any.whl` | `6b15d476480104d9448e6b9601ca14f4f346ebe70a40dfec5c2f9b1fc24450a6` |
| `e3bundle-0.1.3.tar.gz` | `e41fac7ab62ffb527cdf25818d5e5e3329cf3736f74eddd0bc30a880b57eea91` |

1. Descarga el artefacto `dist` del run anterior y comprueba ambos SHA-256 antes de subir.
2. En la cuenta PyPI, crea una API token con alcance de cuenta únicamente para esta subida inicial. No copies el valor a Issues, chat, Git o logs. Introduce el token de forma interactiva en una terminal local.
3. En PowerShell, desde la carpeta que contiene los dos artefactos:

```powershell
py -m venv .venv-pypi-upload
.\.venv-pypi-upload\Scripts\python.exe -m pip install --upgrade pip twine
.\.venv-pypi-upload\Scripts\python.exe -m twine check .\e3bundle-0.1.3.tar.gz .\e3bundle-0.1.3-py3-none-any.whl
.\.venv-pypi-upload\Scripts\python.exe -m twine upload .\e3bundle-0.1.3.tar.gz .\e3bundle-0.1.3-py3-none-any.whl
```

Cuando Twine lo solicite, usa el usuario `__token__` y pega la API token en el prompt de contraseña. No actives `--verbose` para evitar trazas innecesarias. Después de una subida con éxito, revoca la token de cuenta inmediatamente en PyPI. Esto publica los artefactos pero **no arregla el Trusted Publisher** ni permite declarar resueltas futuras publicaciones automáticas. Si `twine check`, la comparación de hashes o el upload falla, detente y registra el error saneado; no repitas subidas a ciegas.

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
- [PyPI Warehouse PR #19422 — disregard GitHub `sub` claim (merged 2026-01-29)](https://github.com/pypi/warehouse/pull/19422)
- [PyPI Warehouse #19347 — generic OIDC support (context, not confirmed cause)](https://github.com/pypi/warehouse/issues/19347)
- [PyPI Warehouse #20504 — example of invalid-publisher with no persisted pending row](https://github.com/pypi/warehouse/issues/20504)
- [GitHub OIDC immutable subject claims](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims)
