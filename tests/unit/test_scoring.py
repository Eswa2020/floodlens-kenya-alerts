from services.reports.scoring import agreement_score, decide, severity, unknown_tokens


def test_real_flood_clears_threshold():
    s = agreement_score("Houses flooded at Nyalenda, water inside homes", ["flooded_house", "standing_water"])
    assert s >= 0.5
    assert decide(s, "en", False) == ("draft_alert", "strong_agreement")


def test_mismatched_report_is_flagged_not_dropped():
    s = agreement_score("Flooding everywhere, road under water", ["dry_road", "clear_sky"])
    assert s == 0.0
    assert decide(s, "en", False)[0] == "low_priority_review"


def test_place_name_regression_never_low_priority_when_photo_shows_water():
    # "Ngong Road" used to read as a road claim -> score 0 -> missed alarm
    s = agreement_score("Things are bad at Ngong Road tonight, come quickly.", ["floodwater"])
    assert s >= 0.2
    assert decide(s, "en", False)[0] == "review"


def test_kiswahili_and_sheng_always_reviewed_by_a_person():
    s = agreement_score("Maji imejaa barabara Mathare", ["submerged_road"])
    assert decide(s, "sw", False) == ("review", "language_review")
    assert decide(1.0, "sheng", False) == ("review", "language_review")


def test_injection_never_auto_drafts():
    assert decide(1.0, "en", True) == ("review", "possible_injection")


def test_no_image_goes_to_review():
    assert decide(0.0, "en", False, has_image=False) == ("review", "no_image_evidence")


def test_severity_levels():
    assert severity(["rooftop_refuge"]) == "high"
    assert severity(["submerged_road"]) == "medium"
    assert severity(["standing_water"]) == "low"
    assert severity(["dry_road"]) == "none"


def test_vocab_gaps_surface_unknown_words():
    assert "imejaa" in unknown_tokens("Maji imejaa barabara")
