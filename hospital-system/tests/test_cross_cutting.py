from pathlib import Path


def test_compose_file_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "docker-compose.yml").is_file()
    assert (root / "prometheus.yml").is_file()
    assert (root / ".env.example").is_file()
