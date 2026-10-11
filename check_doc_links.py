"""Starter-pack checker (reproduced from the course page): README mentions all five docs."""
from pathlib import Path

REQUIRED = ['architecture', 'deployment', 'cost', 'user', 'build_checkpoint']


def main() -> int:
    text = Path('README.md').read_text(encoding='utf-8').lower()
    missing = [s for s in REQUIRED if s not in text]
    if missing:
        print('FAIL missing doc mentions', missing)
        return 1
    print('doc links OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
