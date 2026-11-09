# E3 — Candidato integral de reconciliación de fuentes (sin promoción)

Estado: PLAN / CANDIDATE. Esta rama sintetiza los cambios con un padre main, NO fusiona las PR originales.

- main padre literal: 4e41c5c58e2e02361a2118768df9ee83a78038c9
- #85 (claves/alias): 16bfe53cfcb1f916b29800e81a725071f0d79851
- #91 (trust store/CSP/snapshot): fc6886057bbe68a7095eaa4b3e19839dab071056
- #109 (incluye #108): 02d8dba32b2e67355eec1f11b67d609f79a1dd8c

Se han incorporado los cambios de #85 y #91 sobre el árbol de main. Tres solapamientos resueltos explícitamente:
1. README: conserva el diagnóstico actual de PyPI con causa NO CONFIRMADA y agrega cláusulas de identidad de clave (#85) y confianza externa denegada por defecto (#91).
2. Pages: conserva las acciones fijadas v7.1.0 del main y añade las pruebas de alias de #85; NO altera la puerta de publicación.
3. Snapshot: conserva el setup-python v7.1.0 de main y la separación de permisos del candidato #91. El publisher conserva aprobación humana y confianza externa requerida.

#108 añade paridad CLI/JS sobre HEAD literal; #109 añade el control de afirmaciones; ambos se incluyen sin alterar sus reglas.

Se requiere validación exact HEAD de todos los flujos, cobertura Windows/macOS/Playwright, revisión humana independiente, inscripción externa con custodia de claves públicas, y reproducción fuera del equipo autor. Claves del trust store sin alta autorizada: NO G2. No se hace publicación, despliegue, merge main ni certificación. G1/G2=BLOCKED.
