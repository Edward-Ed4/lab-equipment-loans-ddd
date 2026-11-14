from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "src" / "domain"
APPLICATION = ROOT / "src" / "application"


def _scan(path):
    return [p for p in path.rglob("*.py") if p.is_file()]


def test_architecture_dependencies():
    # Architecture: domain code cannot import application, infrastructure, or interface.
    bad = []
    for file in _scan(DOMAIN):
        content = file.read_text(encoding="utf-8")
        if "application" in content or "infrastructure" in content or "interface" in content:
            bad.append(str(file.relative_to(ROOT)))
    assert not bad, f"Domain imports violate layering: {bad}"

    bad_app = []
    for file in _scan(APPLICATION):
        content = file.read_text(encoding="utf-8")
        if "infrastructure" in content or "interface" in content:
            bad_app.append(str(file.relative_to(ROOT)))
    assert not bad_app, f"Application imports violate layering: {bad_app}"
