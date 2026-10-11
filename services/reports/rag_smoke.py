"""Ground one answer in the guidance set, in stub mode. Run: python -m services.reports.rag_smoke"""
import json

from services.reports.rag import answer


def main() -> int:
    out = answer("Water is rising near our house by the river. Should we evacuate?", stub=True)
    print(json.dumps(out, indent=2))
    if not (out["grounded"] and out["citations"]):
        print("FAIL rag smoke: answer was not grounded")
        return 1
    print("rag smoke OK", out["citations"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
