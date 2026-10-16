# Tutorial: detectar manipulaciones en un conjunto de datos

Esta guía crea un pequeño conjunto CSV sintético, firma su manifiesto con dos claves Ed25519, lo verifica usando claves públicas fijadas y prueba tres modificaciones independientes: cambiar un valor, añadir un archivo y eliminar un archivo.

**Alcance:** este ejemplo demuestra comprobación de integridad de archivos y verificación criptográfica según una política de firmas configurada. Los datos son sintéticos. Un resultado correcto no demuestra que los datos sean ciertos, que se hayan recogido bien, que las personas firmantes sean independientes ni que su identidad real esté acreditada.

## 1. Requisitos y preparación

- Python 3.11 o posterior.
- Git.
- Un entorno en el que puedas instalar el proyecto y sus dependencias. La preparación puede necesitar acceso a la red; una vez instalado, el comando de verificación de e3bundle no realiza conexiones de red.
- Usa un directorio de trabajo desechable. Las claves privadas y el conjunto de datos se crearán fuera del clon del repositorio para no añadirlos por accidente a Git.

La distribución pública de PyPI y la demo web tienen controles de publicación separados. Este tutorial instala el código desde el repositorio; no afirma que PyPI o GitHub Pages estén desbloqueados.

~~~bash
git clone https://github.com/Traky12/castuo-e3-001.git
cd castuo-e3-001
git rev-parse HEAD
python -m venv .venv
~~~

Activa el entorno virtual e instala el proyecto localmente.

**Bash / Zsh**

~~~bash
source .venv/bin/activate
python -m pip install .
~~~

**PowerShell**

~~~powershell
.\.venv\Scripts\Activate.ps1
python -m pip install .
~~~

Crea un directorio hermano y cambia a él. Ejecuta allí el resto de los comandos, no dentro del checkout de Git.

**Bash / Zsh**

~~~bash
mkdir -p ../e3bundle-tutorial-workspace
cd ../e3bundle-tutorial-workspace
~~~

**PowerShell**

~~~powershell
New-Item -ItemType Directory -Force ..\e3bundle-tutorial-workspace | Out-Null
Set-Location ..\e3bundle-tutorial-workspace
~~~

## 2. Crear datos sintéticos y dos claves de firma

Este comando crea dos archivos dentro del paquete de datos y un directorio separado para las claves públicas y privadas. Puedes pegarlo en Bash/Zsh o PowerShell.

~~~bash
python -c 'from pathlib import Path; root=Path("dataset-bundle"); (root/"data").mkdir(parents=True, exist_ok=True); (root/"data/readings.csv").write_text("timestamp,temperature_c,plot\n2026-10-15T08:00:00Z,21.4,GH-01\n2026-10-15T09:00:00Z,21.7,GH-01\n", encoding="utf-8"); (root/"report.md").write_text("Datos sintéticos de tutorial; no son evidencia de campo.\n", encoding="utf-8"); Path("keys").mkdir(exist_ok=True)'
~~~

Genera dos claves diferentes. Mantén los archivos .key en secreto y fuera del paquete. Los archivos .pub.json contienen claves públicas.

~~~bash
e3bundle keygen --private-key keys/operator.key --signer-id operator
e3bundle keygen --private-key keys/reviewer.key --signer-id reviewer
~~~

Ambas claves se generan localmente para este tutorial. Tener dos claves no demuestra que existan dos personas independientes. En un proceso real de aprobación también hay que gobernar la custodia de claves, la independencia de revisores y la fijación de claves públicas.

## 3. Fijar las claves públicas y firmar el manifiesto

Crea un archivo de confianza a partir de las claves públicas generadas. No incluye ninguna clave privada.

~~~bash
python -c 'import json; from pathlib import Path; ids=["operator","reviewer"]; data={i:json.loads((Path("keys")/f"{i}.pub.json").read_text(encoding="utf-8"))["public_key_b64"] for i in ids}; Path("trusted-keys.json").write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")'
~~~

Crea el manifiesto después de añadir todos los archivos de datos y, después, añade las dos firmas sobre ese mismo manifiesto.

~~~bash
e3bundle manifest dataset-bundle --bundle-id tutorial-dataset-001
e3bundle sign dataset-bundle --private-key keys/operator.key --signer-id operator --role operator
e3bundle sign dataset-bundle --private-key keys/reviewer.key --signer-id reviewer --role reviewer
~~~

Resultado esperado: el manifiesto declara dos archivos y signatures.json contiene una firma de operator y otra de reviewer. No modifiques los datos y vuelvas a generar el manifiesto durante las pruebas de manipulación: eso describiría otro paquete en lugar de detectar el cambio.

## 4. Verificar el paquete original

~~~bash
e3bundle verify dataset-bundle --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Estado y código de salida esperados:

~~~text
VERIFIED  tutorial-dataset-001  files 2/2  signatures 2 trusted / 2 valid
código de salida: 0
~~~

El archivo de claves de confianza fija las claves públicas que cuentan para alcanzar el umbral. El campo role de la firma es descriptivo; por sí solo no acredita identidad, independencia ni autoridad.

## 5. Crear tres copias para pruebas negativas

Cada modificación parte de la misma copia firmada para que los resultados no interfieran entre sí. Este comando funciona en Bash/Zsh y PowerShell.

~~~bash
python -c 'import shutil; [shutil.copytree("dataset-bundle", name) for name in ("scenario-edit", "scenario-add", "scenario-delete")]'
~~~

### Caso A — Cambiar un valor

Modifica una temperatura en la copia.

~~~bash
python -c 'from pathlib import Path; p=Path("scenario-edit/data/readings.csv"); s=p.read_text(encoding="utf-8"); assert s.count("21.4")==1; p.write_text(s.replace("21.4","21.9"), encoding="utf-8")'
e3bundle verify scenario-edit --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Hallazgo esperado: **hash mismatch: data/readings.csv**. Código de salida esperado: **1**.

### Caso B — Añadir un archivo

Añade un archivo que no estaba en el manifiesto original.

~~~bash
python -c 'from pathlib import Path; Path("scenario-add/data/extra.txt").write_text("Añadido después de firmar.\n", encoding="utf-8")'
e3bundle verify scenario-add --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Hallazgo esperado: **undeclared file: data/extra.txt**. Código de salida esperado: **1**.

### Caso C — Eliminar un archivo

Elimina un archivo declarado en el manifiesto original.

~~~bash
python -c 'from pathlib import Path; Path("scenario-delete/report.md").unlink()'
e3bundle verify scenario-delete --min-signatures 2 --trusted-keys trusted-keys.json --strict --format text
~~~

Hallazgo esperado: **missing file: report.md**. Código de salida esperado: **1**.

Comprueba el código de salida antes de ejecutar otro comando:

- Bash / Zsh: **echo $?**
- PowerShell: **$LASTEXITCODE**

El resultado debe ser **1** cuando la verificación devuelve FAILED. El código **2** significa que la entrada no se pudo leer o que los argumentos son inválidos; no es el resultado esperado de estas tres manipulaciones.

## 6. Interpretar el resultado

| Resultado | Significado |
|---|---|
| VERIFIED, salida 0 | Los archivos declarados coinciden con el manifiesto y las claves públicas fijadas satisfacen el umbral de firmas distintas. |
| FAILED, salida 1 | Un archivo declarado cambió, falta un archivo, existe un archivo no declarado u otra condición de verificación ha fallado. |
| ERROR, salida 2 | El paquete, el manifiesto, el archivo de claves de confianza o los argumentos no se pudieron utilizar. |

VERIFIED no demuestra que las temperaturas sean exactas, que los datos procedan de una explotación real, que las personas firmantes sean independientes ni que una organización haya aprobado legalmente los datos. e3bundle comprueba la integridad y la política criptográfica configurada. No proporciona una autoridad de sellado de tiempo ni un servicio de revocación de claves.

## Notas de reproducibilidad

- Registra el commit que muestra git rev-parse HEAD, la versión de Python, el sistema operativo, los comandos exactos, los hallazgos y los códigos de salida.
- No incluyas claves privadas en el paquete, en un pull request, en una incidencia, en una captura ni en un artefacto público.
- La prueba automatizada del repositorio ejecuta los casos de este tutorial. Es evidencia reproducible de CI, no una validación humana independiente.
- Informa de los problemas en el [rastreador de incidencias](https://github.com/Traky12/castuo-e3-001/issues). No intercambies ni solicites estrellas a cambio de informes o ayuda.
