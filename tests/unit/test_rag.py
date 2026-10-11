from services.reports.rag import answer, load_docs, retrieve


def test_document_set_is_small_and_loaded():
    assert 5 <= len(load_docs()) <= 20


def test_retrieval_finds_evacuation_guidance():
    assert retrieve("when should we evacuate")[0]["id"] == "G02"


def test_answer_is_grounded_and_cites():
    out = answer("Is it safe to drive through a flooded road?", stub=True)
    assert out["grounded"] and "G01" in out["citations"]
    assert out["mode"] == "stub"


def test_uncovered_question_is_not_grounded():
    out = answer("xyzzy qwerty", stub=True)
    assert out["grounded"] is False and out["citations"] == []
