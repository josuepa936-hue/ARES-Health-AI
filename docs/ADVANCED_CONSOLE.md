# ARES Health AI v0.8 — Advanced Mission Control

## What changed

Version 0.8 redesigns the existing Streamlit presentation into a five-part mission-oriented interface:

1. **Mission Overview:** synthetic daily trends, quality findings and transparent review status.
2. **Signals Lab:** individually selected signal charts plus exploratory statistics from SciPy, NumPy and Pandas.
3. **Body Systems:** original stylized, **non-diagnostic** figure with selectable cardiovascular, sleep/recovery and musculoskeletal hotspots.
4. **Scientific Evidence:** curated NASA Human Research Program and Canadian Space Agency references, which motivate research context but provide **no astronaut observations to this prototype**.
5. **Mission Review:** traceable simulation review notes and JSON / CSV export.

No real-world medical risk scoring, diagnosis, sensor connection or NASA operational integration exists in this project.

## Exploratory statistics

The **first seven** fictional daily values are the reference and the **last four** are the recent comparison. The Signals Lab displays:
- The reference mean, recent mean and absolute difference.
- Full-series median.
- Robust dispersion: SciPy `median_abs_deviation(scale="normal")`.
- Descriptive slope in units/day: SciPy `theilslopes`.
- A three-point rolling median line, where there are enough observations.

**These statistics are descriptive only** and are **not** used to generate new alerts or clinical classifications. The existing review rules remain unchanged: 12 bpm or 1.5 hours mean difference, for demonstration only. The daily-activity signal has **no alert rule**.

Invalid or insufficient records withhold advanced statistics entirely. Missing datapoints are not bridged on plots.

## Body systems figure

The figure is a **stylized original UI schematic, not a medical anatomical illustration**. It contains three hotspots:
- Cardiovascular — simulated resting heart rate.
- Sleep & Recovery — simulated sleep duration.
- Musculoskeletal — simulated activity minutes.

A selector also provides keyboard-accessible navigation; where supported, selecting a Plotly hotspot changes the displayed content. The body map does **not** display disease risks, radiation dosimetry, bone density or mental health screening.

## Updated dependencies

`scipy>=1.14,<2` is added for robust statistics; `streamlit>=1.56,<3` ensures modern `st.plotly_chart(width="stretch")` and selection APIs. Existing SciPy-backed analyses do **not** require an LLM or network connection.

## Test and run

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Validate the four built-in scenarios and the CSV importer. Verify that both export buttons and the review-state selector work. The code is not flight-certified or clinically validated.

## Sources

- [SciPy median absolute deviation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_abs_deviation.html)
- [SciPy Theil–Sen slope](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html)
- [Streamlit Plotly chart selection](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)
- [Project NASA/CSA evidence](SCIENTIFIC_EVIDENCE.md)

## Demo narration note

Demo scripts written for earlier versions describe the same data-quality safeguards and core use cases, but the UI now uses tabs. Adjust click order before recording and do not describe the prototype as live astronaut telemetry.
