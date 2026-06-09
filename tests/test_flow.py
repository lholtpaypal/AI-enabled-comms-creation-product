from oslo_comms_studio.app import (
    CopyDraft,
    build_search_terms,
    choose_top_dynamic_segment,
    find_dynamic_segment_record,
    generate_copy,
    generate_copy_variants,
    parse_copy_response,
    parse_copy_variants_response,
    rank_dynamic_segment_options,
)


def test_parse_copy_response_handles_json() -> None:
    draft = parse_copy_response(
        '{"title":"Your PayPal debit card is waiting","body":"Apply in the app."}'
    )

    assert draft.title == "Your PayPal debit card is waiting"
    assert draft.body == "Apply in the app."


def test_parse_copy_response_handles_wrapped_json() -> None:
    draft = parse_copy_response(
        'Here is the copy: {"title":"Card ready","body":"Apply in the app."}'
    )

    assert draft.title == "Card ready"
    assert draft.body == "Apply in the app."


def test_generate_copy_calls_cosmos(monkeypatch) -> None:
    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"title":"Try PayPal One Card",'
                                '"body":"Apply for the debit card in your app."}'
                            )
                        }
                    }
                ]
            }

    calls = {}

    def fake_post(url, **kwargs):
        calls["url"] = url
        calls["kwargs"] = kwargs
        return Response()

    monkeypatch.setenv("COSMOS_LLM_API_KEY", "test-key")
    monkeypatch.setattr("oslo_comms_studio.app.requests.post", fake_post)

    draft = generate_copy("Create a push notification for PayPal One Card signups")

    assert draft.title == "Try PayPal One Card"
    assert calls["kwargs"]["json"]["model"] == "gpt-5-mini"
    assert calls["kwargs"]["json"]["response_format"] == {"type": "json_object"}
    assert calls["kwargs"]["json"]["max_completion_tokens"] == 1200
    assert "max_tokens" not in calls["kwargs"]["json"]
    assert "temperature" not in calls["kwargs"]["json"]
    assert calls["kwargs"]["headers"]["Authorization"] == "Bearer test-key"


def test_generate_copy_retries_empty_cosmos_content(monkeypatch) -> None:
    class Response:
        def __init__(self, content: str) -> None:
            self.content = content

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"finish_reason": "length", "message": {"content": self.content}}]}

    payloads = []
    responses = [
        Response(""),
        Response('{"title":"Try PayPal One Card","body":"Apply in the app."}'),
    ]

    def fake_post(url, **kwargs):
        payloads.append(kwargs["json"])
        return responses.pop(0)

    monkeypatch.setenv("COSMOS_LLM_API_KEY", "test-key")
    monkeypatch.setattr("oslo_comms_studio.app.requests.post", fake_post)

    draft = generate_copy("Create a push notification for PayPal One Card signups")

    assert draft.title == "Try PayPal One Card"
    assert payloads[0]["max_completion_tokens"] == 1200
    assert payloads[1]["max_completion_tokens"] == 2400


def test_parse_copy_variants_response_handles_two_variants() -> None:
    variants = parse_copy_variants_response(
        '{"variants":['
        '{"title":"Variant A","body":"First body."},'
        '{"title":"Variant B","body":"Second body."}'
        "]}"
    )

    assert [variant.title for variant in variants] == ["Variant A", "Variant B"]
    assert [variant.body for variant in variants] == ["First body.", "Second body."]


def test_generate_copy_variants_calls_cosmos(monkeypatch) -> None:
    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"variants":['
                                '{"title":"Debit card perks","body":"Enroll today."},'
                                '{"title":"Use your PayPal balance","body":"Get your card now."}'
                                "]}"
                            )
                        }
                    }
                ]
            }

    calls = {}

    def fake_post(url, **kwargs):
        calls["url"] = url
        calls["kwargs"] = kwargs
        return Response()

    monkeypatch.setenv("COSMOS_LLM_API_KEY", "test-key")
    monkeypatch.setattr("oslo_comms_studio.app.requests.post", fake_post)

    variants = generate_copy_variants(
        "Create a push notification for PayPal Debit Card enrollment",
        CopyDraft(title="You're eligible", body="Enroll in the app."),
    )

    assert len(variants) == 2
    assert variants[0].title == "Debit card perks"
    assert calls["kwargs"]["json"]["response_format"] == {"type": "json_object"}
    assert "variants" in calls["kwargs"]["json"]["messages"][0]["content"]


def test_build_search_terms_expands_debit_card_synonyms() -> None:
    terms = build_search_terms("Users not enrolled in PayPal One Card")

    assert "paypal one card" in terms
    assert "ppdc" in terms
    assert "not enrolled" in terms


def test_choose_top_dynamic_segment_prefers_negative_match() -> None:
    segments = [
        {
            "code": "PPDC_ACTIVE_CARDHOLDERS",
            "id": "DS-1",
            "description": "Users who have PPDC",
            "lifecycle_status": "ACTIVE",
            "audience_count": 100,
        },
        {
            "code": "NON_PPDC_ELIGIBLE_USERS",
            "id": "DS-2",
            "description": "Eligible users not enrolled in PayPal debit card",
            "lifecycle_status": "ACTIVE",
            "audience_count": 250,
        },
    ]

    recommendation = choose_top_dynamic_segment(
        segments,
        "I need a push notification for users not enrolled in PayPal One Card",
    )

    assert recommendation is not None
    assert recommendation.code == "NON_PPDC_ELIGIBLE_USERS"
    assert recommendation.segment_id == "DS-2"


def test_rank_dynamic_segment_options_returns_next_suggestions() -> None:
    segments = [
        {
            "code": "LOW_MATCH",
            "id": "DS-1",
            "description": "Debit card",
            "lifecycle_status": "ACTIVE",
        },
        {
            "code": "NON_PPDC_ELIGIBLE_USERS",
            "id": "DS-2",
            "description": "Eligible users not enrolled in PayPal debit card",
            "lifecycle_status": "ACTIVE",
        },
        {
            "code": "CONSUMER_WITH_NO_ACTIVE_DEBIT_CARDS",
            "id": "DS-3",
            "description": "Consumers with no active debit card",
            "lifecycle_status": "ACTIVE",
        },
    ]

    options = rank_dynamic_segment_options(
        segments,
        "Create a push notification for users not enrolled in PayPal Debit Card",
        limit=3,
    )

    assert [option.recommendation.segment_id for option in options] == ["DS-2", "DS-3", "DS-1"]
    assert options[0].details["code"] == "NON_PPDC_ELIGIBLE_USERS"


def test_find_dynamic_segment_record_accepts_id_or_code() -> None:
    segments = [
        {"code": "CONSUMER_WITH_NO_ACTIVE_DEBIT_CARDS", "id": "DS-3"},
    ]

    by_id = find_dynamic_segment_record(segments, "DS-3")
    by_code = find_dynamic_segment_record(segments, "consumer_with_no_active_debit_cards")

    assert by_id == segments[0]
    assert by_code == segments[0]
