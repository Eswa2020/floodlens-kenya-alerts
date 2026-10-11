from agents.router import route


def test_route_flood_report_is_default():
    assert route("Water has covered the road at Kibera") == "flood_report"


def test_route_guidance():
    assert route("What should we do if water enters the house?") == "guidance_lookup"


def test_route_guidance_kiswahili():
    assert route("Nifanye nini maji yakiingia nyumbani?") == "guidance_lookup"


def test_route_review_queue():
    assert route("Show queue for Kisumu") == "review_queue"


def test_route_empty_text_falls_back_to_default():
    assert route("") == "flood_report"
