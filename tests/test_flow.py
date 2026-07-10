from oslo_comms_studio.app import (
    CopyDraft,
    CosmosLlmError,
    build_paypal_value_prop_search_queries,
    build_search_terms,
    choose_top_dynamic_segment,
    copy_generation_messages,
    copy_variants_messages,
    extract_deeplink_catalog_data,
    find_dynamic_segment_record,
    generate_copy,
    generate_copy_variants,
    parse_copy_response,
    parse_copy_variants_response,
    parse_rps_search_plan,
    paypal_value_prop_context,
    rank_deeplink_options,
    rank_dynamic_segment_options,
    search_audience_options,
    search_deeplink_options,
)
from oslo_comms_studio.server import (
    build_demo_campaign_create_payload,
    build_demo_campaign_package,
    post_demo_campaign,
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
    monkeypatch.setattr("oslo_comms_studio.app.PAYPAL_VALUE_PROP_SEARCH_ENABLED", False)
    monkeypatch.setattr("oslo_comms_studio.app.requests.post", fake_post)

    draft = generate_copy("Create a push notification for PayPal One Card signups")

    assert draft.title == "Try PayPal One Card"
    assert calls["kwargs"]["json"]["model"] == "gpt-5-mini"
    assert calls["kwargs"]["json"]["response_format"] == {"type": "json_object"}
    assert calls["kwargs"]["json"]["max_completion_tokens"] == 1200
    assert "max_tokens" not in calls["kwargs"]["json"]
    assert "temperature" not in calls["kwargs"]["json"]
    assert calls["kwargs"]["headers"]["Authorization"] == "Bearer test-key"


def test_copy_generation_prompt_includes_push_writing_guidelines() -> None:
    control = CopyDraft(title="Save with PayPal", body="Open the app to get started.")
    system_prompts = [
        copy_generation_messages("Promote PayPal Savings")[0]["content"],
        copy_variants_messages("Promote PayPal Savings", control)[0]["content"],
    ]

    for system_prompt in system_prompts:
        assert "title must be 35 characters or fewer" in system_prompt
        assert "body must be 100 characters or fewer" in system_prompt
        assert "Avoid title punctuation" in system_prompt
        assert "encourage customer action" in system_prompt


def test_copy_prompt_includes_paypal_value_prop_context(monkeypatch) -> None:
    monkeypatch.setattr("oslo_comms_studio.app.PAYPAL_VALUE_PROP_SEARCH_ENABLED", False)
    intent = "Create a push notification for PayPal Debit Card enrollment"
    context = paypal_value_prop_context(intent)
    messages = copy_generation_messages(intent)

    assert "5% cash back" in context
    assert "PayPal.com product value-prop pass from web search agents" in messages[1]["content"]
    assert "5% cash back" in messages[1]["content"]


def test_paypal_value_prop_context_uses_live_paypal_sources(monkeypatch) -> None:
    class Response:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    search_html = """
    <a class="result__a" href="https://www.paypal.com/us/digital-wallet/manage-money/paypal-debit-card">
      PayPal Debit Card
    </a>
    <div class="result__snippet">
      Use the PayPal Debit Card anywhere Mastercard is accepted.
    </div>
    """
    page_html = """
    <html>
      <head>
        <title>PayPal Debit Card</title>
        <meta name="description" content="Earn cash back with the PayPal Debit Card.">
      </head>
      <body>
        <h1>Earn cash back with your PayPal Debit Card</h1>
        <p>Choose one monthly category and earn cash back on eligible purchases.</p>
      </body>
    </html>
    """
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        if url == "https://html.duckduckgo.com/html/":
            return Response(search_html)
        return Response(page_html)

    monkeypatch.setattr("oslo_comms_studio.app.requests.get", fake_get)

    context = paypal_value_prop_context("Create a push notification for PayPal Debit Card")

    assert "Live PayPal.com web-search-agent context" in context
    assert "https://www.paypal.com/us/digital-wallet/manage-money/paypal-debit-card" in context
    assert "monthly category" in context
    assert calls[0][1]["params"]["q"].startswith("site:paypal.com/us")


def test_build_paypal_value_prop_search_queries_uses_product_terms() -> None:
    queries = build_paypal_value_prop_search_queries(
        "Create a push notification for PayPal Pay Later"
    )

    assert any("PayPal Pay Later" in query for query in queries)
    assert all(query.startswith("site:paypal.com/us") for query in queries)


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
    monkeypatch.setattr("oslo_comms_studio.app.PAYPAL_VALUE_PROP_SEARCH_ENABLED", False)
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
    monkeypatch.setattr("oslo_comms_studio.app.PAYPAL_VALUE_PROP_SEARCH_ENABLED", False)
    monkeypatch.setattr("oslo_comms_studio.app.requests.post", fake_post)

    variants = generate_copy_variants(
        "Create a push notification for PayPal Debit Card enrollment",
        CopyDraft(title="You're eligible", body="Enroll in the app."),
    )

    assert len(variants) == 2
    assert variants[0].title == "Debit card perks"
    assert calls["kwargs"]["json"]["response_format"] == {"type": "json_object"}
    assert "variants" in calls["kwargs"]["json"]["messages"][0]["content"]


def test_build_demo_campaign_package_only_updates_content_fields() -> None:
    package = build_demo_campaign_package(
        title="Pay later today",
        body="Split eligible purchases at checkout.",
        deeplink="https://www.paypal.com/myaccount/paylater",
    )

    content = package["channel_details"][0]["content"][0]["content_payload"]
    assert content["localizable_content"]["en-US"]["title"] == "Pay later today"
    assert (
        content["localizable_content"]["en-US"]["body"] == "Split eligible purchases at checkout."
    )
    assert (
        content["non_localizable_content"]["deep_link"]
        == "https://www.paypal.com/myaccount/paylater"
    )
    assert (
        package["delivery_config"]["target_config"]["dynamic_segment"]["groups"][0][
            "include_segments"
        ][0]["segment_id"]
        == "DS-6892159868302557433"
    )


def test_build_demo_campaign_create_payload_creates_new_draft_campaign() -> None:
    campaign_name, payload = build_demo_campaign_create_payload(
        title="Yeah, it worked!",
        body="This came from the demo.",
        deeplink="https://www.paypal.com/mobile-app/paylater/pay-later-hub",
        segment_id="DS-123",
        segment_code="SEGMENT_CODE_123",
    )

    assert campaign_name.startswith("agentic_comms_post_")
    assert payload["campaign_name"] == campaign_name
    assert payload["status"] == "DRAFT"
    assert payload["owners"] == ["lholt"]
    assert payload["team_dls"] == ["lholt@paypal.com"]
    assert payload["delivery_type"] == "SCHEDULED_BULK"
    assert payload["channels"] == [1002]
    assert "campaign_id" not in payload
    assert "campaign_ref_id" not in payload
    assert "version" not in payload
    assert "created_by" not in payload
    assert "time_created_ms" not in payload
    assert payload["delivery_config"]["schedule"]["timezone"] == "America/Chicago"
    include_segment = payload["delivery_config"]["target_config"]["dynamic_segment"]["groups"][0][
        "include_segments"
    ][0]
    assert include_segment == {
        "segment_id": "DS-123",
        "segment_code": "SEGMENT_CODE_123",
    }

    content_payload = payload["channel_details"][0]["content"][0]["content_payload"]
    assert content_payload["localizable_content"]["en-US"] == {
        "body": "This came from the demo.",
        "title": "Yeah, it worked!",
    }
    assert (
        content_payload["non_localizable_content"]["deep_link"]
        == "https://www.paypal.com/mobile-app/paylater/pay-later-hub"
    )
    assert payload["channel_details"][0]["channel_rules"]["preference"] == "GENERAL_MARKETING"
    assert payload["channel_details"][0]["status"] == "ACTIVE"
    assert "created_by" not in payload["channel_details"][0]
    content = payload["channel_details"][0]["content"][0]
    assert content["status"] == "ACTIVE"
    assert content["content_legal_review_exception"] is True
    assert "content_id" not in content
    assert "created_by" not in content


def test_post_demo_campaign_calls_campaign_management(monkeypatch) -> None:
    class Response:
        text = '{"campaign_id":"4076525877"}'

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"campaign_id": "4076525877"}

    calls = {}

    def fake_post(url, **kwargs):
        calls["url"] = url
        calls["kwargs"] = kwargs
        return Response()

    monkeypatch.setattr("oslo_comms_studio.server.requests.post", fake_post)

    result = post_demo_campaign({"channel_details": []})

    assert result == {"campaign_id": "4076525877"}
    assert calls["url"].endswith("/v1/communications/campaign")
    assert calls["kwargs"]["json"] == {"channel_details": []}
    assert calls["kwargs"]["headers"]["Content-Type"] == "application/json"
    assert calls["kwargs"]["headers"]["USER_DETAILS"] == (
        '{"LOGGED_IN_USER":"lholt","USER_ROLES":["PP_SSO_COMMS_ADMIN"]}'
    )
    assert calls["kwargs"]["verify"] is False


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


def test_extract_deeplink_catalog_data_from_generated_js() -> None:
    catalog = extract_deeplink_catalog_data(
        """
        const _EXTERNAL_DATA = {
          "meta": {"totalPaths": 1},
          "modules": [
            {"module": "P2P", "links": [{"path": "/myaccount/transfer/homepage/pay"}]}
          ]
        };
        """
    )

    assert catalog["modules"][0]["module"] == "P2P"
    assert catalog["modules"][0]["links"][0]["path"] == "/myaccount/transfer/homepage/pay"


def test_rank_deeplink_options_prefers_p2p_pay_homepage() -> None:
    records = [
        {
            "module": "Home",
            "path": "/mobile-app/dashboard",
            "dest": "DashboardDestination",
            "fullClass": "com.paypal.home.DashboardDestination",
            "type": "Cross-Platform",
            "params": [],
            "adb": (
                "adb shell am start -W -a android.intent.action.VIEW -d "
                '"https://www.paypal.com/mobile-app/dashboard" com.paypal.android.p2pmobile'
            ),
        },
        {
            "module": "P2P",
            "path": "/myaccount/transfer/homepage/pay",
            "dest": "SendTransferDestination",
            "fullClass": "com.paypal.oslo.feature.p2p.api.navigation.SendTransferDestination",
            "type": "App-Only",
            "params": [],
            "adb": (
                "adb shell am start -W -a android.intent.action.VIEW -d "
                '"https://www.paypal.com/myaccount/transfer/homepage/pay" '
                "com.paypal.android.p2pmobile"
            ),
        },
    ]

    options = rank_deeplink_options(
        records,
        "Create a push notification nudging users to pay someone in the PayPal app.",
        limit=2,
    )

    assert options[0].recommendation.path == "/myaccount/transfer/homepage/pay"
    assert options[0].recommendation.url == "https://www.paypal.com/myaccount/transfer/homepage/pay"
    assert options[0].recommendation.required_params == []


def test_search_deeplink_options_uses_catalog_without_llm(monkeypatch) -> None:
    catalog = {
        "modules": [
            {
                "module": "Savings",
                "links": [
                    {
                        "path": "/myaccount/savings",
                        "dest": "SavingsDlHubDestination",
                        "fullClass": "com.paypal.oslo.feature.savings.api.navigation.SavingsDlHubDestination",
                        "type": "Cross-Platform",
                        "params": [],
                        "adb": (
                            "adb shell am start -W -a android.intent.action.VIEW -d "
                            '"https://www.paypal.com/myaccount/savings" '
                            "com.paypal.android.p2pmobile"
                        ),
                    },
                    {
                        "path": "/myaccount/savings/add-money",
                        "dest": "SavingsDlAddMoneyDestination",
                        "fullClass": "com.paypal.oslo.feature.savings.api.navigation.SavingsDlAddMoneyDestination",
                        "type": "Cross-Platform",
                        "params": [],
                        "adb": (
                            "adb shell am start -W -a android.intent.action.VIEW -d "
                            '"https://www.paypal.com/myaccount/savings/add-money" '
                            "com.paypal.android.p2pmobile"
                        ),
                    },
                ],
            }
        ]
    }

    monkeypatch.setenv("COSMOS_LLM_API_KEY", "")
    monkeypatch.setattr("oslo_comms_studio.app.fetch_deeplink_catalog", lambda: catalog)

    options = search_deeplink_options(
        "Create a push notification asking savings users to add money.",
        limit=2,
    )

    assert options[0].recommendation.path == "/myaccount/savings/add-money"
    assert len(options) == 2


def test_parse_rps_search_plan_accepts_safe_segment_search() -> None:
    plan = parse_rps_search_plan(
        """
        {
          "audience_summary": "Users not enrolled in PayPal Debit Card",
          "searches": [
            {
              "reason": "Search reusable debit-card eligibility segments",
              "method": "POST",
              "endpoint": "/segments/search",
              "payload": {
                "filters": {
                  "type": ["dynamic_segment"],
                  "codes": ["PayPal Debit Card", "PPDC", "not enrolled"]
                },
                "fields": ["id", "code", "description", "audience_count", "created_by", "type"],
                "sort_by": "code",
                "sort_order": "asc"
              }
            }
          ]
        }
        """
    )

    assert plan.searches[0].endpoint == "/segments/search"
    assert plan.searches[0].payload["filters"]["type"] == ["dynamic_segment"]
    assert "PayPal_Debit_Card" in plan.searches[0].payload["filters"]["codes"]
    assert plan.searches[0].payload["fields"][:2] == ["id", "code"]


def test_parse_rps_search_plan_rejects_unsafe_endpoint() -> None:
    try:
        parse_rps_search_plan(
            """
            {
              "audience_summary": "Bad plan",
              "searches": [
                {
                  "method": "POST",
                  "endpoint": "/rpsreadserv/v1/profile-attributes",
                  "payload": {
                    "filters": {"type": ["dynamic_segment"], "codes": ["PPDC"]},
                    "fields": ["id", "code"]
                  }
                }
              ]
            }
            """
        )
    except CosmosLlmError as exc:
        assert "usable RPS search plan" in str(exc)
    else:
        raise AssertionError("Unsafe RPS search plan should be rejected.")


def test_search_audience_options_executes_validated_segment_search(monkeypatch) -> None:
    responses = [
        {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"audience_summary":"Debit card holdouts","searches":[{'
                            '"method":"POST","endpoint":"/segments/search",'
                            '"payload":{"filters":{"type":["dynamic_segment"],'
                            '"codes":["PPDC","not enrolled"]},'
                            '"fields":["id","code","description","audience_count","created_by","type"]}}]}'
                        )
                    }
                }
            ]
        },
        {
            "choices": [
                {
                    "message": {
                        "content": '{"segment_ids":["DS-2","DS-3","DS-1"]}',
                    }
                }
            ]
        },
    ]
    requests = []

    def fake_post_cosmos_chat_completion(payload, api_key):
        return responses.pop(0)

    def fake_request_json(method, path, **kwargs):
        requests.append((method, path, kwargs["json"]))
        return {
            "dynamic_segments": [
                {
                    "code": "PPDC_ACTIVE_CARDHOLDERS",
                    "id": "DS-1",
                    "description": "Users who have PPDC",
                    "audience_count": 100,
                    "created_by": "team-a",
                    "type": "BATCH",
                },
                {
                    "code": "NON_PPDC_ELIGIBLE_USERS",
                    "id": "DS-2",
                    "description": "Eligible users not enrolled in PayPal debit card",
                    "audience_count": 250,
                    "created_by": "team-b",
                    "type": "BATCH",
                },
                {
                    "code": "CONSUMER_WITH_NO_ACTIVE_DEBIT_CARDS",
                    "id": "DS-3",
                    "description": "Consumers with no active debit card",
                    "audience_count": 200,
                    "created_by": "team-c",
                    "type": "BATCH",
                },
            ]
        }

    monkeypatch.setenv("COSMOS_LLM_API_KEY", "test-key")
    monkeypatch.setattr(
        "oslo_comms_studio.app.post_cosmos_chat_completion",
        fake_post_cosmos_chat_completion,
    )
    monkeypatch.setattr("oslo_comms_studio.app.request_json", fake_request_json)

    options = search_audience_options(
        "Create a push notification for users not enrolled in PayPal Debit Card",
        limit=3,
    )

    assert requests[0][0] == "POST"
    assert requests[0][1] == "/segments/search"
    assert requests[0][2]["filters"]["type"] == ["dynamic_segment"]
    search_requests = [request for request in requests if request[1] == "/segments/search"]
    enrich_requests = [request for request in requests if request[1] == "/segments"]
    assert len(search_requests) >= 2
    assert enrich_requests
    assert enrich_requests[0][2]["segment_codes"]
    assert all("get_all_segments" not in payload for _, _, payload in requests)
    assert [option.recommendation.segment_id for option in options] == ["DS-2", "DS-3", "DS-1"]


def test_search_audience_options_falls_back_to_targeted_segment_search(monkeypatch) -> None:
    requests = []

    def fake_post_cosmos_chat_completion(payload, api_key):
        raise CosmosLlmError("planner unavailable")

    def fake_request_json(method, path, **kwargs):
        requests.append((method, path, kwargs["json"]))
        return {
            "dynamic_segments": [
                {
                    "code": "NON_PPDC_ELIGIBLE_USERS",
                    "id": "DS-2",
                    "description": "Eligible users not enrolled in PayPal debit card",
                    "audience_count": 250,
                    "created_by": "team-b",
                    "type": "BATCH",
                }
            ]
        }

    monkeypatch.setenv("COSMOS_LLM_API_KEY", "test-key")
    monkeypatch.setattr(
        "oslo_comms_studio.app.post_cosmos_chat_completion",
        fake_post_cosmos_chat_completion,
    )
    monkeypatch.setattr("oslo_comms_studio.app.request_json", fake_request_json)

    options = search_audience_options(
        "Create a push notification for users not enrolled in PayPal Debit Card",
        limit=3,
    )

    assert requests
    assert requests[0][1] == "/segments/search"
    assert any(path == "/segments" and "segment_codes" in payload for _, path, payload in requests)
    assert all("get_all_segments" not in payload for _, _, payload in requests)
    assert options[0].recommendation.segment_id == "DS-2"
