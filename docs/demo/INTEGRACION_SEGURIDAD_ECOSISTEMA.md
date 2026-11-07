# CASTÚO · Demo de seguridad de integración, limitada a datos sintéticos

**Estado: candidato sin fusión.** Este repositorio público NO contiene código privado de CASTÚO-SYSTEM ni ejecuta una conexión a sensores, clientes, servicios remotos o sistemas físicos.

## Contratos observados, no conectores productivos

- Agro Edge, main d1c45a3cb55c0c7303a45f2197afc4d7e307e32d: evidencia_bridge/fixtures/normal.jsonl y models.py. El productor real evidence_bridge/bridge/export_pack.py devuelve NOT_IMPLEMENTED. Se utiliza una copia sintética explícita de tres eventos públicos, nunca datos de campo.
- Evidence, main 76fe85ada7dcf906dc1a5ef500fe497b3f4a0959: schemas/evidence-object-2.0.schema.json. Los campos requeridos se representan con aseguramientos oneD/oneV/oneR/oneA todos false. No se ha ejecutado todavía el validador independiente de Evidence sobre este paquete.
- E3, candidato fuente ba1f4f34cbf96f78686c03e0f80c159874a7767c: el script invoca el CLI E3 real del mismo árbol Git para generar manifest.json y verificar hash. No hay firma externa ni trust enrollment.
- Núcleo privado, main 5a392e5d6bf02ea1647bd64c0b75208295ca40a4: NO conectado. Requiere organización/roles/HTTP reales, CI completa, aislamiento y revisión.

## Ejecución reproducible, offline

    python scripts/demo_ecosystem_bridge.py --fixture examples/ecosystem/synthetic-edge.jsonl --out /tmp/castuo-edge-synthetic
    python scripts/e3bundle.py verify /tmp/castuo-edge-synthetic --format json

Sin firmas externas el único PASS técnicamente válido es VERIFIED_INTEGRITY_ONLY. Manipular un fichero del bundle debe dar FAILED. La ejecución estricta con --strict --min-signatures 2 y claves externas aprobadas debe fallar hasta que existan dos firmantes independientes legítimos. Una clave de ejemplo o autocontenida no aporta identidad real.

## Protección

Se rechazan procedencias no sintéticas, escritura, aprobación de revisión falsa, referencias QMS, campos desconocidos, NaN, timestamps malformados, duplicación de IDs, entradas enormes, archivos ausentes y symlinks. La etiqueta synthetic limita la demo, pero NO autentica el productor real. No se usan API, MQTT, PLC, DNS ni secretos. Maker-checker: quien propone no aprueba, aunque acumule roles.

El siguiente paso auténtico de integración es implementar y verificar la exportación de Edge por su propietario, introducir Evidence en una reproducción aislada firmada, activar trust store solo mediante aprobaciones humanas fuera de banda y superar CI/G1/G2. Sin estos elementos no existe integración completa del sistema. Solo pruebas técnicas sintéticas.
