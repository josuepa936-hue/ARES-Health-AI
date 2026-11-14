# Guía rápida — ARES Health AI v0.5

Prototipo local con cuatro escenarios sintéticos, gráficos, controles de calidad, explicaciones de cambios y Mission Review Center con exportación JSON y CSV.

## Linux / entorno en la nube

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run app.py
```

Para Windows/PowerShell consulta `README.md`. No se requieren claves API ni servicios externos.

Selecciona **Stable observations**, **Resting heart rate shift**, **Shortened sleep** o **Incomplete records**. Los fallos de calidad bloquean la interpretación de tendencias. Los cambios se calculan con siete días iniciales y cuatro recientes, sin modificar los umbrales ilustrativos de 12 bpm y 1.5 horas. Puedes registrar una revisión ficticia y descargar el informe JSON o las observaciones CSV.

No uses información personal o médica real. El prototipo no diagnostica ni cuenta con validación médica o aprobación de NASA. La arquitectura y los límites implementados se documentan en inglés en `docs/ARCHITECTURE.md`.
