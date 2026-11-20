# Integración con CASTÚO-SYSTEM

e3bundle es la herramienta pública de verificación de evidencia para CASTÚO-SYSTEM.

## Relación
- CASTÚO-SYSTEM define el caso de uso, la hoja de ruta y las decisiones de promoción.
- e3bundle genera, firma y verifica paquetes de evidencia.
- La web castuo-system.es comunica el estado público y los límites del proyecto.

## Flujo
1. CASTÚO-SYSTEM registra resultados técnicos.
2. e3bundle crea un paquete de evidencia con manifiesto SHA-256.
3. e3bundle firma el paquete con Ed25519.
4. e3bundle verifica el paquete sin conexión.
5. CASTÚO-SYSTEM decide si la evidencia permite avanzar de fase.
6. castuo-system.es actualiza el estado público.

## Límites
La verificación no certifica calidad, conformidad regulatoria, exactitud del dato original ni validez de un piloto.
