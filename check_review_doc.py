"""Starter-pack checker (reproduced from the course page): peer review checklist has 6+ items."""
from pathlib import Path


def main() -> int:
    text = Path('docs/peer_review_checklist.md').read_text(encoding='utf-8')
    n = text.count('- [ ]')
    if n < 6:
        print('FAIL need 6 checkboxes, got', n)
        return 1
    print('review checklist OK', n)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
