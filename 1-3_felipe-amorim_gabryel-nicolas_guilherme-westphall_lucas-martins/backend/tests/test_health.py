from app.health import health


def test_health_reports_ok():
    assert health()["status"] == "ok"


def test_health_identifies_service():
    assert health()["service"] == "olist-delay-agent"
