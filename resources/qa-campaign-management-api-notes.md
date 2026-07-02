# QA Campaign Management API Notes

Date: 2026-07-01

## What Worked

I adapted the existing PATCH flow in `src/oslo_comms_studio/server.py` into a POST create flow against QA campaign-management.

Base URL:

```text
https://te-campaign-management-3.qa.paypal.com:16223/v1/communications/campaign
```

Original PATCH helper at the time of discovery:

```text
patch_demo_campaign(campaign_id, patch_payload)
```

Current app helpers after the POST implementation:

```text
build_demo_campaign_create_payload(...)
post_demo_campaign(create_payload)
```

Existing template:

```text
resources/agentic_comms_test.json
```

## Headers

The successful calls used these headers:

```text
Content-Type: application/json
USER_DETAILS: {"LOGGED_IN_USER":"lholt","USER_ROLES":["PP_SSO_COMMS_ADMIN"]}
```

## POST Create Command

```bash
curl -k -sS -X POST 'https://te-campaign-management-3.qa.paypal.com:16223/v1/communications/campaign' \
  -H 'Content-Type: application/json' \
  -H 'USER_DETAILS: {"LOGGED_IN_USER":"lholt","USER_ROLES":["PP_SSO_COMMS_ADMIN"]}' \
  --data-binary @/private/tmp/oslo-post-campaign.json \
  -o /private/tmp/oslo-post-campaign-response.json \
  -w '\nHTTP_STATUS:%{http_code}\n'
```

Result:

```text
HTTP_STATUS:201
```

## GET Verification Command

```bash
curl -k -sS 'https://te-campaign-management-3.qa.paypal.com:16223/v1/communications/campaign/4076525877' \
  -H 'Content-Type: application/json' \
  -H 'USER_DETAILS: {"LOGGED_IN_USER":"lholt","USER_ROLES":["PP_SSO_COMMS_ADMIN"]}' \
  -o /private/tmp/oslo-get-created-campaign-response.json \
  -w '\nHTTP_STATUS:%{http_code}\n'
```

Result:

```text
HTTP_STATUS:200
```

## Created Campaign

```json
{
  "campaign_ref_id": "8148646118",
  "campaign_id": "4076525877",
  "version": 1,
  "campaign_name": "agentic_comms_post_test_20260701_135602",
  "status": "DRAFT",
  "created_by": "lholt",
  "delivery_type": "SCHEDULED_BULK",
  "channels": [1002],
  "content_id": "9047732449"
}
```

## Payload Construction Notes

The POST payload was derived from `resources/agentic_comms_test.json`.

I removed server-generated fields before POSTing:

- Campaign-level: `campaign_ref_id`, `campaign_id`, `version`, `created_by`, `updated_by`, `time_created_ms`, `time_updated_ms`
- Channel-level: `created_by`, `updated_by`, `time_created_ms`, `time_updated_ms`
- Content-level: `content_id`, `created_by`, `updated_by`, `time_created_ms`, `time_updated_ms`

I set:

- `campaign_name`: `agentic_comms_post_test_20260701_135602`
- `description`: `QA API POST smoke test from Codex`
- `status`: `DRAFT`
- `owners`: `["lholt"]`
- `team_dls`: `["lholt@paypal.com"]`
- Push title: `Codex POST smoke test`
- Push body: `Created by API POST smoke test.`
- Deep link: `paypal://home`
- Content legal review exception: `true`
- Content legal review exception reason: `QA API smoke test`

Because the template uses `delivery_type: SCHEDULED_BULK`, I added a future schedule:

```json
{
  "start_date_time": "2026-07-02T09:00",
  "end_date_time": "2026-12-01T23:59",
  "timezone": "America/Chicago"
}
```

The dynamic segment was kept from the template:

```json
{
  "segment_id": "DS-6892159868302557433",
  "segment_code": "NA_20201106_ALL_USERS"
}
```

## Useful Local Commands

Find the current create helper and template:

```bash
rg -n "CAMPAIGN_MANAGEMENT|post_demo_campaign|build_demo_campaign_create_payload|agentic_comms_test|campaign-management" src resources tests
```

Preview a staged payload:

```bash
jq '{campaign_name,status,owners,delivery_type,delivery_config,channels,channel_details}' /private/tmp/oslo-post-campaign.json
```

Summarize the created campaign:

```bash
jq '{campaign_ref_id,campaign_id,version,campaign_name,status,created_by,time_created_ms,delivery_type,channels,content_id:.channel_details[0].content[0].content_id}' /private/tmp/oslo-get-created-campaign-response.json
```
