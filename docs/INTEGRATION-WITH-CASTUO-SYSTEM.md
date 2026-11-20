# Integración con CASTÚO-SYSTEM

`e3bundle` es la herramienta pública de verificación de integridad y autoría de paquetes de evidencia utilizada por CASTÚO-SYSTEM.

## Propósito

CASTÚO-SYSTEM requiere poder registrar, conservar y verificar evidencias de operaciones de campo, incluso en entornos con conectividad irregular. `e3bundle` proporciona un mecanismo reproducible para empaquetar, firmar y verificar dichas evidencias sin depender de un servicio centralizado durante la verificación.

## Responsabilidades

| Componente | Responsabilidad |
|---|---|
| `CASTÚO-SYSTEM` | Define el caso de uso, la hoja de ruta, los criterios de aceptación, las decisiones de promoción y el estado del proyecto |
| `e3bundle` | Genera manifiestos, calcula hashes SHA-256, valida firmas Ed25519 y permite verificar paquetes sin conexión |
| `castuo-system.es` | Comunica el estado público, los límites del proyecto y los enlaces a evidencia verificable |

## Flujo de evidencia

1. CASTÚO-SYSTEM registra un resultado técnico, una decisión de gobernanza, una prueba o un resultado de piloto.
2. Se seleccionan únicamente los ficheros no sensibles que deben formar parte del paquete de evidencia.
3. `e3bundle` genera un manifiesto con hashes SHA-256 de los ficheros incluidos.
4. El manifiesto se firma mediante Ed25519 conforme a la política de claves configurada.
5. Cualquier verificador puede comprobar el paquete sin conexión mediante `e3bundle`.
6. CASTÚO-SYSTEM evalúa si la evidencia es suficiente para avanzar de fase.
7. `castuo-system.es` actualiza el estado público únicamente cuando existe evidencia verificable y una decisión de gobernanza registrada.

## Criterios de evidencia

Una evidencia solo puede utilizarse para actualizar el estado público o promover una fase si cumple, como mínimo, los siguientes requisitos:

- Incluye un manifiesto con hashes SHA-256.
- Incluye una firma Ed25519 válida.
- Puede verificarse sin conexión mediante `e3bundle`.
- Identifica la versión de `e3bundle`, la fecha de generación y el responsable de la evidencia.
- No incluye secretos, credenciales, datos personales, claves privadas ni información confidencial.
- Indica claramente qué afirma y qué no afirma la evidencia.

## Límites de la verificación

La verificación correcta de un paquete mediante `e3bundle` demuestra que:

- Los ficheros incluidos coinciden con el manifiesto.
- Las firmas cumplen la política de claves configurada por quien verifica.
- El paquete no ha sido alterado después de su firma, siempre que las claves y la política de verificación sean fiables.

La verificación **no** demuestra por sí sola que:

- El dato original sea exacto, completo o de alta calidad.
- El origen del dato sea auténtico.
- El producto cumpla una norma, reglamento o certificación.
- Un piloto haya sido validado.
- El sistema esté listo para producción.

## Estado de integración

| Elemento | Estado |
|---|---|
| Verificación offline de integridad y firmas | Disponible en e3bundle alpha |
| Captura offline | En desarrollo |
| Sincronización | En desarrollo |
| Piloto validado en campo | Pendiente |
| Revisión independiente | Pendiente |
| Promoción E3-001 | Bloqueada hasta disponer de evidencia suficiente |
