"""Tests for the Week 5 pipeline."""

from pathlib import Path
import pytest

from src.ingest_files import read_csv_records
from src.pipeline import get_config


class TestGetConfig:
    def test_returns_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-key-123")
        monkeypatch.delenv("OUTPUT_DIR", raising=False)
        config = get_config()
        assert config["api_key"] == "test-key-123"

    def test_uses_default_output_dir(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-key-123")
        monkeypatch.delenv("OUTPUT_DIR", raising=False)
        config = get_config()
        assert config["output_dir"] == "output"

    def test_reads_custom_output_dir(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-key-123")
        monkeypatch.setenv("OUTPUT_DIR", "/tmp/myout")
        config = get_config()
        assert config["output_dir"] == "/tmp/myout"

    def test_raises_when_api_key_missing(self, monkeypatch):
        monkeypatch.delenv("API_KEY", raising=False)
        with pytest.raises((RuntimeError, KeyError, SystemExit)):
            get_config()


class TestReadCsvRecords:
    def test_returns_records(self, tmp_path):
        csv_file = tmp_path / "weather.csv"
        csv_file.write_text(
            "station,timestamp,temperature_c,humidity_pct\n"
            "amsterdam,2026-01-01T10:00:00,12.5,80\n",
            encoding="utf-8",
        )

        records = read_csv_records(Path(csv_file))

        assert len(records) == 1
