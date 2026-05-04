from pathlib import Path
from scripts.report import render_html


def test_render_html_contains_cluster_names_and_chart_libs(tmp_path):
    out = tmp_path / "out.html"
    render_html(
        log_path=Path("tests/fixtures/sample_commute_log.csv"),
        apartments_path=Path("tests/fixtures/sample_apartments.json"),
        template_path=Path("templates/report.html.j2"),
        output_path=out,
    )
    html = out.read_text(encoding="utf-8")
    assert "Test Cluster A" in html
    assert "Test Cluster B" in html
    assert "chart.js" in html.lower()  # CDN script tag
    assert "07:00" in html
    assert "07:30" in html
