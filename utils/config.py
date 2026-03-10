import json
from pathlib import Path


def _parse_scalar(raw: str):
    text = raw.strip()
    if not text:
        return ""
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _simple_yaml_load(content: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]

    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if value.strip() == "":
            node: dict = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            parent[key] = _parse_scalar(value)

    return root


def load_config(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except Exception:
        pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _simple_yaml_load(text)
