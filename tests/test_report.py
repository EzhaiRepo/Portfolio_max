import json
from html.parser import HTMLParser
from portfoliolens.cli import main


def test_offline_cli_report(tmp_path):
    main(["review", "--demo", "--output", str(tmp_path)])
    report = (tmp_path / "review.html").read_text()
    assert "SYNTHETIC DEMO" in report
    assert "<svg" in report
    class ResourceParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key in {"src", "href", "xlink:href"}:
                    assert not (value or "").startswith(("http://", "https://", "//"))
    ResourceParser().feed(report)
    data = json.loads((tmp_path / "run.json").read_text())
    assert data["observations"] == 756
    assert data["metrics"]["SPY"]["Information ratio"] is None
    assert (tmp_path / "trades_capped_min_variance.csv").exists()
