# Guía rápida — ARES Health AI v1.5

El flujo principal es la consola React + FastAPI en un solo servidor local.
Consulta [README](README.md) para instalación limpia en Windows o Linux: Python
3.12+, Node >=22.12 (24 verificado), entorno virtual, `pip install -r requirements.txt`,
`npm ci` y compilación. En Windows ejecuta `.\start-ares.cmd` desde la raíz;
si PowerShell bloquea `.ps1`, usa `.cmd` sin cambiar la política de ejecución.
La consola está en `http://127.0.0.1:8000/`. Streamlit sigue disponible como alternativa.

Las pruebas HTTP requieren FastAPI en 8000 **y** Vite en 5173. Las de navegador
usan la aplicación compilada en 8014 por defecto, o `ARES_E2E_ORIGIN` explícito.
Consulta [validación](docs/VALIDATION_PLAN.md) antes de ejecutarlas.

Solo datos ficticios: las fechas son simuladas y los umbrales de 12 bpm / 1.5
horas son ejemplos de ingeniería, no criterios clínicos. Copilot es determinista,
local y no usa un LLM. Las vistas opcionales MIT/NASA son investigación separada;
no proporcionan telemetría de astronautas ni validan el motor.

El [guion oficial](docs/DEMO_SCRIPT.md) prepara un video inferior a 30 segundos.
La [lista de entrega](docs/SUBMISSION_CHECKLIST.md) requiere revisión humana.
No se afirma envío a NASA Space Apps, validación médica ni aprobación de NASA.
