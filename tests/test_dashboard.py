"""Exercise the preserved dashboard and export controls without a browser."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_scenarios_and_review_controls():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py', default_timeout=30).run()
    for scenario, quality, flags in [
        ('Stable observations', '0', '0'),
        ('Resting heart rate shift', '0', '1'),
        ('Shortened sleep', '0', '1'),
        ('Incomplete records', '2', '0'),
    ]:
        app.sidebar.selectbox[0].select(scenario).run()
        assert not app.exception
        assert app.metric[2].value == quality
        assert app.metric[3].value == flags
        assert len(app.get('download_button')) == 2
        assert any('Mission review center' in item.value for item in app.subheader)
    next(widget for widget in app.selectbox if widget.label == 'Review log state').select('Reviewed in demo')
    app.text_area[0].input('Synthetic review completed.').run()
    assert not app.exception
