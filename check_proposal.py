"""Starter-pack checker (reproduced from the course page): proposal.md headings and no scale overclaim."""
import re
from pathlib import Path

HEADS = ['Path', 'Dataset', 'Milestones']


def claims_million_rows(text: str) -> bool:
    """Fail only on real overclaims. Allow 'Do not use millions of rows'."""
    low = text.lower()
    cleaned = re.sub(
        r"(do\s+not|don't|does\s+not|never|no)\s+[^.!\n]{0,60}?millions?\b",
        ' ',
        low,
    )
    if re.search(r'\bmillions?\s+(of\s+)?rows?\b', cleaned):
        return True
    if re.search(r'\b1[\s,]*000[\s,]*000\b', cleaned):
        return True
    return False


def main() -> int:
    text = Path('proposal.md').read_text(encoding='utf-8')
    low = text.lower()
    if claims_million_rows(text):
        print('FAIL dataset scale overclaim')
        return 1
    missing = [h for h in HEADS if h.lower() not in low]
    if missing:
        print('FAIL missing', missing)
        return 1
    print('proposal headings OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
