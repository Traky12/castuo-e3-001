# Cierre técnico y preparación de staging

Estado: PLAN, salvo resultados locales expresamente registrados.

## Alcance y límites

Candidato: PR #122 de Traky12/castuo-e3-001.
SHA validado: 8589e7b57cb2df2e8180f313668570530aefa87e.

Este documento no autoriza escrituras remotas, gasto, merge, cambios de
permisos ni despliegues. No implementa por sí mismo controles técnicos.
Producción y CORE-008 permanecen fuera del alcance de modificación.

La validación local no equivale a CI oficial, revisión independiente,
aceptación visual, aprobación de staging ni autorización GO.

## Responsabilidades

Antes de ejecutar, designar:
- Responsable del proyecto.
- Ejecutor técnico.
- Revisor humano independiente.
- Responsable de aceptación visual.
- Administrador de facturación.
- Responsable de staging.

No presentar autorrevisión como revisión independiente.

## Fase A: evidencias y seguimiento

1. Conservar resultados originales, incluidos intentos fallidos.
2. Revisar logs antes de compartirlos.
3. Retirar de las copias publicables secretos, datos personales,
   credenciales, rutas privadas y datos reales no autorizados.
4. Conservar los originales privados y registrar las redacciones.
5. Inventariar SHA, entorno, comandos, versiones, fechas, códigos,
   resultados, limitaciones y responsables.
6. Generar hashes de los archivos de evidencia que se compartan.
7. Confirmar los destinos: PR #122, issue #123 y GOVERNANCE-001,
   identificado previamente como issue #18 del dashboard de progreso.
8. Mostrar al propietario el contenido, adjuntos y destinos exactos.
9. Publicar exclusivamente tras aprobación específica.
10. Enlazar los registros sin duplicar el seguimiento.

Los hashes detectan modificaciones; no acreditan por sí solos autoría
ni veracidad de una ejecución.

Cierre: evidencias revisadas, publicación autorizada y referencias
trazables al SHA. No se considera cerrado por crear este documento.

## Fase B: revisión humana independiente y aceptación visual

1. Confirmar HEAD y base del PR.
2. Revisar el diff, manifiestos, instrucciones Windows/POSIX,
   corrección móvil, workflows, permisos y límites declarados.
3. Explicar con inventario real la diferencia entre 122 archivos
   del manifiesto y 123 blobs cotejados; no suponer la causa.
4. Reproducir los controles acordados en una copia limpia.
5. Registrar identidad del revisor, entorno, comandos y resultados.
6. Evaluar móvil y escritorio, ajuste del SHA, copia exacta del SHA,
   navegación por teclado, zoom y claridad de estados.
7. Verificar que la demo no implica autorización de producción.
8. Usar vista previa local o entorno ya autorizado.
9. Registrar cambios solicitados, aprobación o bloqueo.

Si cambia el HEAD, evaluar el impacto y repetir los controles afectados.
No trasladar automáticamente la aprobación a otro commit.

Cierre: revisión independiente y aceptación visual registradas,
sin observaciones bloqueantes pendientes.

## Fase C: Actions y facturación

1. Consultar de nuevo el estado de cada repositorio.
2. Registrar propietario, SHA, workflow, run ID, fecha,
   mensaje exacto, runner, pasos y enlaces.
3. No atribuir facturación solo por runner_id=0 y ausencia de pasos:
   conservar el mensaje explícito que identifica la causa.
4. El administrador revisa pagos, método de pago, consumo,
   presupuestos, límites y alertas.
5. No autorizar gasto ilimitado ni modificar presupuestos
   sin aprobación de importe y responsable.
6. Inspeccionar un workflow existente, sin publicación ni despliegue.
7. Solicitar autorización y ejecutar una comprobación de bajo coste.
8. Registrar si arranca y produce un resultado diagnosticable.

Cierre: capacidad de ejecución recuperada y verificada.
El arranque del runner no demuestra que el código pase.

## Fase D: controles oficiales y reparación por causa demostrada

Repositorios por confirmar:
- Castuo-system.
- goldfish.
- castuo-evolution.
- castuo-live-status-dashboard.
- castuo-progress-dashboard.
- castuo-e3-001.

1. Inventariar dependencias y priorizar por riesgo.
2. Elegir SHA y controles apropiados por repositorio.
3. Inspeccionar efectos secundarios antes de ejecutar workflows.
4. Autorizar ejecuciones y registrar el SHA realmente probado.
5. Clasificar bloqueo externo, entorno, código, omisión o falta de CI.
6. Abrir reparación solo cuando exista una causa demostrada.
7. Trabajar en ramas candidatas autorizadas, con cambios mínimos.
8. Añadir regresión cuando corresponda.
9. No desactivar checks, ignorar vulnerabilidades ni forzar resultados.
10. Revisar el PR y ejecutar de nuevo los controles afectados.

Para el dashboard sin workflow, confirmar primero que no exista
validación equivalente. Proponer un workflow adecuado a su tecnología.
Una candidata validada no valida retrospectivamente main.

Cierre: controles adecuados, resultados por SHA y excepciones explicadas.

## Fase E: definición y aprobación de staging

1. Clasificar qué componentes necesitan despliegue.
2. Para CLI y bibliotecas, considerar pruebas de instalación.
3. Para documentación, validar build y contenido.
4. Excluir archivados salvo reactivación expresa.
5. Definir proveedor, región, finalidad, coste máximo, duración,
   propietario, dominio y acceso.
6. Usar datos sintéticos y credenciales exclusivas de staging.
7. No conectar actuadores reales ni secretos de producción.
8. Definir logs, retención, alertas, borrado y reversión.
9. Verificar las protecciones disponibles en el plan de GitHub.
10. Documentar revisores, separación de funciones y excepciones.
11. Aprobar destino y artefacto antes de desplegar.
12. Registrar SHA de origen y digest del artefacto cuando corresponda.
13. Ejecutar humo, integración, aceptación visual y reversión acordada.
14. Registrar aceptación o rechazo.

El nombre de un entorno no demuestra residencia europea de datos.
Staging no concede autorización de producción.

Cierre: entorno aprobado y validado, o no aplicable con justificación.

## Decisiones separadas

- Publicar evidencias.
- Modificar ramas candidatas.
- Cambiar permisos o configuración.
- Autorizar gasto y ejecuciones.
- Hacer merge.
- Desplegar a staging.
- Desplegar a producción: fuera de este procedimiento.

Ninguna de estas decisiones queda concedida por este documento.
