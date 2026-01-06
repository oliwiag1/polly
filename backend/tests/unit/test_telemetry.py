"""Testy jednostkowe dla telemetrii (Application Insights)."""


def _reset_config_singleton() -> None:
    from app.config import ConfigMeta

    if hasattr(ConfigMeta, "_instances"):
        ConfigMeta._instances.clear()


def test_telemetry_disabled_without_connection_string(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
    _reset_config_singleton()

    from app.telemetry import get_telemetry

    telemetry = get_telemetry()
    stats = telemetry.get_stats()

    assert stats["enabled"] is False
    assert stats["connection_string_present"] is False


def test_telemetry_otel_enabled_with_connection_string(monkeypatch):
    monkeypatch.setenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://westeurope-0.in.applicationinsights.azure.com/",
    )
    _reset_config_singleton()

    import app.telemetry as telemetry_module

    called = {"value": False}

    def fake_configure_azure_monitor(*, connection_string: str):
        assert "InstrumentationKey=" in connection_string
        called["value"] = True

    # Patchujemy importowaną funkcję przez sys.modules lookup wewnątrz _setup
    import azure.monitor.opentelemetry

    monkeypatch.setattr(
        azure.monitor.opentelemetry,
        "configure_azure_monitor",
        fake_configure_azure_monitor,
        raising=True,
    )

    telemetry = telemetry_module.get_telemetry()
    stats = telemetry.get_stats()

    assert called["value"] is True
    assert stats["enabled"] is True
    assert stats["provider"] == "azure-monitor-opentelemetry"
    assert stats["connection_string_present"] is True

    # Dodatkowe pokrycie: śledzenie eventu i wyjątku nie powinno rzucać
    telemetry.track_event("test-event", {"k": "v"})
    telemetry.track_exception(ValueError("test-ex"))
