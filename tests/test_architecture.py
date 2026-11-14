import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_DIR = ROOT / "src" / "domain"
APPLICATION_DIR = ROOT / "src" / "application"


def _iter_imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module


def _is_forbidden(module_name, forbidden_roots):
    module_name = module_name.lower()
    for root in forbidden_roots:
        root = root.lower()
        if (
            module_name == root
            or module_name == f"src.{root}"
            or module_name.startswith(f"{root}.")
            or module_name.startswith(f"src.{root}.")
        ):
            return True
    return False


def _scan(folder, forbidden_roots):
    violations = []
    for path in sorted(folder.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for imported in _iter_imports(tree):
            if _is_forbidden(imported, forbidden_roots):
                violations.append(f"{path.relative_to(ROOT)} imports forbidden module: {imported}")
    return violations


def test_domain_imports_are_not_cross_layer():
    violations = _scan(DOMAIN_DIR, ["application", "infrastructure", "interface"])
    assert not violations, "\n".join(violations)


def test_application_imports_do_not_cross_layer():
    violations = _scan(APPLICATION_DIR, ["infrastructure", "interface"])
    assert not violations, "\n".join(violations)
