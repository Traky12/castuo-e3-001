# Reconciliación de seguridad E3 — expediente de candidato

Estado: DOCUMENTED / PLAN, NO FUSIONADO. No autoriza publicar ni levantar G1/G2.

Referencias exactas comprobadas (01-11-2026):

- main: 4e41c5c58e2e02361a2118768df9ee83a78038c9
- PR #85: 16bfe53cfcb1f916b29800e81a725071f0d79851
- PR #91: fc6886057bbe68a7095eaa4b3e19839dab071056
- PR #108: f91359451db2af2b93820d60b1a6453f1628a3c5

La comparación GitHub #85→#91 indica ramas divergentes: #91 está 49 commits por delante y 8 por detrás de #85. En la lista de archivos modificados por cada PR frente a su base histórica, el solapamiento directo es README.md. Esto NO demuestra que un merge real sea automático, seguro o semánticamente compatible.

El README de #85 y #91 conserva una hipótesis histórica sobre la causa PyPI invalid-publisher basada en el sub OIDC. El README actual de main ya delimita el hecho como causa NO CONFIRMADA y advierte que Warehouse dejó de comprobar sub para publishers GitHub. El candidato actualiza el párrafo heredado de #85 conservando sus cambios de identidad de claves, y añade un gate contra la reintroducción de afirmaciones no justificadas. La rama #91 requiere reconciliación documental separada.

Próximos gates en orden, todos pendientes: revisión humana independiente de #85; conciliación no destructiva de #91 con CLI y fuente principal; ejecución de tests Pytest, Ruff, Gitleaks, pip-audit y HTTP aplicables, Action y tres navegadores en SHA literal resultante; verificación trust store externamente y maker-checker distinto para altas y decisiones; regeneración manifiesto completo, E2E Edge→Evidence→E3 y replay externo.

Las claves públicas de una firma no constituyen por sí solas autorización ni custodia externa. PR #91 contiene un trust store con keys: [], por lo que publicación y evidencia G2 externa deben seguir BLOQUEADAS.

El presente expediente no reemplaza el estado maestro Castuo-system #709. No merge, release, Pages, PyPI, producción ni G1/G2.
