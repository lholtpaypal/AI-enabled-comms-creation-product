# Campaign Response Field Map

Generated from `resources/campaigns-response.json`. This is an observed-data map, not a guaranteed service contract. Use it as the inventory for drafting a strict Structured Outputs JSON Schema and then tighten any field that product/API docs confirm as enum-bound.

## Dataset Snapshot

| Metric | Count |
| --- | --- |
| Campaign objects | 150 |
| Channel detail objects | 226 |
| Content objects | 282 |
| Top-level root keys | `campaigns` |

## High-Level Shape

```json
{
  "campaigns": [
    {
      "delivery_config": {},
      "channels": [1001, 1002],
      "channel_details": [
        {
          "channel_rules": {},
          "content": [
            {
              "content_payload": {
                "localizable_content": {},
                "non_localizable_content": {}
              },
              "content_rules": {}
            }
          ]
        }
      ]
    }
  ]
}
```

## Campaign Object

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `campaign_ref_id` | 150/150 | `string` (150) | 150 unique; examples: `"1684303559"` (1), `"4235959898"` (1), `"2999435171"` (1), `"5377083497"` (1), `"7545144522"` (1) | ID-like string; do not enum. |
| `campaign_id` | 150/150 | `string` (150) | 150 unique; examples: `"3436284626"` (1), `"3927014933"` (1), `"5008388238"` (1), `"5308612704"` (1), `"1937150588"` (1) | ID-like string; do not enum. |
| `version` | 150/150 | `integer` (150) | `1` (126), `2` (21), `3` (2), `4` (1) |  |
| `campaign_name` | 150/150 | `string` (150) | 150 unique; examples: `"NC_channgel"` (1), `"Bulk_4_publish"` (1), `"famglkmaklga"` (1), `"omni_ptt"` (1), `"Push_NC_Omni"` (1) | Free text. |
| `description` | 114/150 | `string` (114) | 88 unique; examples: `"This is a test cmapaign"` (6), `"mgaklnagklnagmkm"` (5), `"25May-NC25May-NC25May-NC25May-NC25May-NC"` (3), `"omni channel added Push + Non Transactional"` (3), `"Omni Testing 26th may ..akngjknagj"` (3) | Optional free text. |
| `tenant_id` | 150/150 | `integer` (150) | `101` (150) | Constant in this sample. |
| `tenant_name` | 150/150 | `string` (150) | `"PAYPAL"` (150) | Constant in this sample. |
| `status` | 150/150 | `string` (150) | `"DRAFT"` (72), `"SUBMITTED"` (35), `"PUBLISHED"` (33), `"APPROVED"` (7), `"ARCHIVED"` (2), `"APPROVAL_REQUESTED"` (1) |  |
| `owners` | 150/150 | `array` (150) | array lengths: `1` (92), `2` (40), `3` (17), `4` (1); values: `"praghuvanshi"` (108), `"hukaur"` (33), `"shivangsrivastav"` (22), `"samlnu"` (20), `"apasharma"` (9), `"nmalla"` (7), `"gsharma9"` (5), `"spratapsingh"` (4), `"mukapoor"` (3), `"pujatav"` (3), `"testuser"` (2), `"pperina"` (2), `"savutukuri"` (1), `"praghuvanhsi"` (1), `"agaag"` (1), `"gyejju"` (1), `"praghuavnshi"` (1), `"aashish"` (1), `"12334"` (1), `"gsharma"` (1), `"araykar"` (1) | Array of user IDs. |
| `team_dls` | 148/150 | `array` (148) | array lengths: `1` (140), `2` (8); 66 unique values; examples: `"test@paypal.com"` (14), `"sam@paypal.com"` (11), `"comms-decisioning-dev@paypal.com"` (8), `"marketing-team@paypal.com"` (8), `"communications-team@paypal.com"` (8), `"affa@paypal.com"` (7), `"comms@paypal.com"` (7), `"ffa@paypal.com"` (6) | Optional array of DL/email strings. |
| `campaign_product` | 148/150 | `string` (148) | `"Savings"` (56), `"Account"` (46), `"Buyer_Protection"` (25), `"Balance"` (9), `"PayPal_CBMC"` (4), `"Wallet"` (2), `"Subscriptions"` (2), `"Crypto"` (1), `"Offers"` (1), `"PayPal_DebitCard"` (1), `"Passkey"` (1) |  |
| `campaign_action` | 148/150 | `string` (148) | `"add_money"` (34), `"add_photo"` (31), `"awareness"` (26), `"confirmation"` (25), `"confirm_address"` (13), `"engage"` (10), `"fix_issue"` (3), `"add_debit_card"` (2), `"enroll"` (2), `"push_opt_in"` (1), `"confirm_email"` (1) |  |
| `countries` | 150/150 | `array` (150) | array lengths: `1` (102), `2` (17), `3` (19), `4` (1), `5` (6), `205` (5); 205 unique values; examples: `"US"` (133), `"CA"` (40), `"AS"` (31), `"AU"` (22), `"GB"` (17), `"BT"` (13), `"IN"` (6), `"PT"` (5) | ISO-like country/market codes; see full observed list below. |
| `delivery_type` | 150/150 | `string` (150) | `"API_BASED"` (126), `"SCHEDULED_BULK"` (22), `"NON_TRIGGERED"` (2) |  |
| `delivery_config` | 150/150 | `object` (150) | object / nested below | Nested object; shape varies by delivery_type/flow. |
| `channels` | 150/150 | `array` (150) | array lengths: `1` (68), `2` (82); values: `1002` (137), `1001` (95) |  |
| `channel_details` | 150/150 | `array` (150) | array lengths: `0` (4), `1` (66), `2` (80) | Array may be empty in draft/incomplete campaigns. |
| `approval_request_id` | 41/150 | `string` (41) | `"DIRECT_APPROVAL"` (10), `"RITM3548107"` (1), `"RITM3548235"` (1), `"RITM3548102"` (1), `"RITM3548132"` (1), `"RITM3548071"` (1), `"RITM3548125"` (1), `"RITM3548073"` (1), `"RITM3548253"` (1), `"RITM3548130"` (1), `"RITM3547994"` (1), `"RITM3548067"` (1), `"RITM3548136"` (1), `"RITM3548106"` (1), `"RITM3548254"` (1), `"RITM3548114"` (1), `"RITM3548149"` (1), `"RITM3548113"` (1), `"RITM3547995"` (1), `"RITM3548077"` (1), `"RITM3548255"` (1), `"RITM3548135"` (1), `"RITM3548025"` (1), `"RITM3548146"` (1), `"RITM3547993"` (1), `"RITM3548116"` (1), `"RITM3548103"` (1), `"RITM3548101"` (1), `"RITM3548072"` (1), `"RITM3548148"` (1), `"RITM3548251"` (1), `"RITM3548112"` (1) | RITM-like ID or DIRECT_APPROVAL. |
| `approval_request_status` | 41/150 | `string` (41) | `"CLOSED"` (30), `"DIRECT_APPROVAL"` (10), `"OPEN"` (1) |  |
| `approval_requested_by` | 41/150 | `string` (41) | `"praghuvanshi"` (19), `"shivangsrivastav"` (9), `"hukaur"` (5), `"spratapsingh"` (3), `"gsharma9"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"samlnu"` (1) |  |
| `approval_requested_time_ms` | 41/150 | `integer` (41) | 41 unique; examples: `1779703629390` (1), `1780298319124` (1), `1780982385180` (1), `1779700177893` (1), `1779787221761` (1) |  |
| `created_by` | 150/150 | `string` (150) | `"praghuvanshi"` (86), `"hukaur"` (16), `"samlnu"` (15), `"apasharma"` (9), `"shivangsrivastav"` (9), `"spratapsingh"` (4), `"gsharma9"` (4), `"testuser"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"pujatav"` (1), `"pperina"` (1), `"araykar"` (1) | Audit metadata; likely system-populated. |
| `time_created_ms` | 150/150 | `integer` (150) | 150 unique; examples: `1779441707756` (1), `1780550283629` (1), `1779084698314` (1), `1779451567425` (1), `1779428491880` (1) | Epoch milliseconds; likely system-populated. |
| `updated_by` | 150/150 | `string` (150) | `"praghuvanshi"` (84), `"samlnu"` (15), `"hukaur"` (14), `"apasharma"` (9), `"shivangsrivastav"` (9), `"spratapsingh"` (4), `"gsharma9"` (4), `"SCHEDULER"` (3), `"testuser"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"gyejju"` (1), `"nmalla3"` (1), `"pperina"` (1), `"araykar"` (1) | Audit metadata; likely system-populated. |
| `time_updated_ms` | 150/150 | `integer` (150) | 150 unique; examples: `1779441846767` (1), `1780912693983` (1), `1779167699660` (1), `1779451987965` (1), `1779431143256` (1) | Epoch milliseconds; likely system-populated. |

## Delivery Config

`delivery_config` exists on every campaign, but it can be an empty object. Observed optional children are below.

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `omni_type` | 50/150 | `string` (50) | `"TYPE_1"` (50) | Only observed for omni campaigns. |
| `schedule` | 26/150 | `object` (26) | object / nested below | Date/time window object. |
| `experiment_config` | 19/150 | `object` (19) | object / nested below | Experiment definition object; one sample is empty. |
| `target_type` | 39/150 | `string` (39) | `"DYNAMIC_SEGMENT"` (20), `"CUSTOM_TABLE"` (17), `"ALL_USERS"` (2) | Audience targeting mode. |
| `target_config` | 39/150 | `object` (39) | object / nested below | Shape depends on target_type. |
| `device_filter_rule` | 18/150 | `object` (18) | object / nested below | Optional device/app version targeting. |
| `client_service_name` | 8/150 | `string` (8) | `"testserv"` (2), `"Test"` (2), `"commsapigatewayserv"` (1), `"asdasdhj"` (1), `"njknjnjn"` (1), `"mjnjnknjknkjnjk"` (1) | Free text service/client identifier. |

### Delivery Schedule

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `start_date_time` | 26/26 | `string` (26) | `"2026-04-01T09:00"` (8), `"2026-05-15T10:47"` (3), `"2026-06-10T12:00"` (2), `"2026-05-18T10:57"` (2), `"2030-06-01T09:00"` (2), `"2026-05-18T11:46"` (1), `"2026-06-10T15:33"` (1), `"2026-05-20T10:18"` (1), `"2026-06-03T23:58"` (1), `"2026-05-15T15:00"` (1), `"2026-06-02T11:19"` (1), `"2030-04-01T09:00"` (1), `"2026-05-23T14:45"` (1), `"2026-05-22T15:56"` (1) | Local datetime string without seconds/timezone offset. |
| `end_date_time` | 26/26 | `string` (26) | `"2026-04-30T23:59"` (8), `"2026-05-26T10:47"` (3), `"2026-06-30T12:00"` (2), `"2026-05-31T10:58"` (2), `"2030-12-31T23:59"` (2), `"2026-07-03T11:41"` (1), `"2026-06-30T17:38"` (1), `"2026-05-28T10:18"` (1), `"2026-06-16T23:58"` (1), `"2026-05-16T14:14"` (1), `"2026-06-19T11:14"` (1), `"2030-04-30T23:59"` (1), `"2026-05-25T09:45"` (1), `"2026-05-28T15:45"` (1) | Local datetime string without seconds/timezone offset. |
| `timezone` | 26/26 | `string` (26) | `"America/Los_Angeles"` (12), `"Asia/Calcutta"` (7), `"Africa/Banjul"` (3), `"Africa/Abidjan"` (2), `"America/Anguilla"` (1), `"Africa/Addis_Ababa"` (1) | IANA timezone string. |

### Experiment Config

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `experiment_name` | 18/19 | `string` (18) | `"comms_hub_live_test"` (5), `"comms_config_store"` (5), `"spring_sale_exp_v1"` (3), `"money_received_test_sp"` (2), `"bulk_audit"` (2), `"abc1"` (1) | Free-form experiment key; empty object occurred once with no fields. |
| `eligible_treatments` | 18/19 | `array` (18) | array lengths: `1` (6), `2` (8), `3` (4); values: `"Control"` (9), `"Test"` (6), `"CommsTeam"` (5), `"treatment_control"` (3), `"treatment_variant_a"` (3), `"treatment_variant_b"` (3), `"Power Users"` (2), `"General Users"` (2), `""` (1) | Array of treatment names. |

### Device Filter Rule

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `device_os` | 18/18 | `string` (18) | `"ALL"` (14), `"ANDROID"` (4) | Observed device target options. |
| `android_app_version.operator` | 18/18 | `string` (18) | `"GREATER_THAN_OR_EQUAL"` (18) | Comparison operator for app version. |
| `android_app_version.app_version_value` | 18/18 | `string` (18) | `"9.0.0"` (10), `"8.65.0"` (5), `"9.0.1"` (2), `"9.0.8"` (1) |  |
| `ios_app_version.operator` | 14/18 | `string` (14) | `"GREATER_THAN_OR_EQUAL"` (13), `"EQUAL"` (1) | Comparison operator for app version. |
| `ios_app_version.app_version_value` | 14/18 | `string` (14) | `"9.0.0"` (9), `"8.65.0"` (5) |  |

### Target Config

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `bq_table_name` | 17/39 | `string` (17) | `"project.dataset.name"` (6), `"pypl-bods.prd_pzn_comms_common.generic_bulk_elmo_data"` (1), `"test.ts.f"` (1), `"tt.tt.ttnn"` (1), `"dev52-test-apps-bulk-comms.dev_pzn_comms_common.custom_bq_table_bulk_pn_qa"` (1), `"pypl-bods.prd_pzn_comms_common.comms_lta_prod_test_data"` (1), `"test.t.t"` (1), `"testproject.testdataset.testtable_name"` (1), `"true.ts.r"` (1), `"t.t.y"` (1), `"test.project.test"` (1), `"jkj.kj.jkl"` (1) | Required when target_type is CUSTOM_TABLE. |
| `dynamic_segment` | 20/39 | `object` (20) | object / nested below | Required when target_type is DYNAMIC_SEGMENT. |

### Dynamic Segment Targeting

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `between_groups_operator` | 20/20 | `string` (20) | `"OR"` (20) |  |
| `groups` | 20/20 | `array` (20) | array lengths: `1` (20) | Array of segment groups. |

| Segment sub-object | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `within_group_operator` | 20/20 | `string` (20) | `"AND"` (20) |  |
| `include_segments` | 20/20 | `array` (20) | array lengths: `1` (11), `2` (9) | Array of segment refs. |
| `exclude_segments` | 9/20 | `array` (9) | array lengths: `0` (2), `1` (7) | Optional array of segment refs; may be empty. |
| `include_segments[].segment_id` | 29/29 | `string` | `"seg_001"` (10), `"seg_002"` (6), `"DS-7532436059975491542"` (5), `"DS-7639808702465844574"` (3), `"DS-7639810314295137554"` (2), `"DS-7574376819299418380"` (2), `"DS-7306801429721457076"` (1) | ID-like string. |
| `include_segments[].segment_code` | 27/29 | `string` | `"HIGH_BALANCE_USERS"` (8), `"ACTIVE_USERS"` (6), `"hukaur_test_ds"` (5), `"br_cip_InReview_consumer"` (3), `"br_cip_hardDeclined_consumer"` (2), `"1099DA_2025_Biz"` (2), `"0.5Back_Debit_Card_Eligibility"` (1) | Optional in sample; missing on 2 include segment refs. |
| `exclude_segments[].segment_id` | 7/7 | `string` | `"seg_003"` (6), `"DS-7306801429721457076"` (1) | ID-like string. |
| `exclude_segments[].segment_code` | 7/7 | `string` | `"OPT_OUT_USERS"` (6), `"0.5Back_Debit_Card_Eligibility"` (1) | Segment code string. |

## Channel Detail Object

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `channel_id` | 226/226 | `integer` (226) | `1002` (133), `1001` (93) |  |
| `channel_name` | 226/226 | `string` (226) | `"PUSH"` (133), `"NOTIFICATION_CENTER"` (93) |  |
| `status` | 226/226 | `string` (226) | `"ACTIVE"` (226) | Constant in this sample. |
| `channel_rules` | 226/226 | `object` (226) | object / nested below | Nested object; differs by channel. |
| `content` | 226/226 | `array` (226) | array lengths: `0` (3), `1` (184), `2` (25), `3` (9), `4` (4), `5` (1) | Array may be empty in incomplete campaigns. |
| `created_by` | 226/226 | `string` (226) | `"praghuvanshi"` (139), `"hukaur"` (26), `"samlnu"` (15), `"shivangsrivastav"` (14), `"apasharma"` (11), `"spratapsingh"` (6), `"gsharma9"` (6), `"testuser"` (2), `"pperina"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"pujatav"` (1) |  |
| `time_created_ms` | 226/226 | `integer` (226) | 170 unique; examples: `1779451567425` (2), `1779428491880` (2), `1779865013447` (2), `1779450901031` (2), `1779703619843` (2) |  |
| `updated_by` | 226/226 | `string` (226) | `"praghuvanshi"` (138), `"hukaur"` (20), `"samlnu"` (16), `"shivangsrivastav"` (14), `"apasharma"` (11), `"spratapsingh"` (6), `"gsharma9"` (6), `"nmall6a"` (4), `"testuser"` (2), `"nmalla3"` (2), `"pperina"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"gyejju"` (1) |  |
| `time_updated_ms` | 226/226 | `integer` (226) | 147 unique; examples: `1779441846767` (2), `1779451987965` (2), `1779431143256` (2), `1780306873726` (2), `1779451328562` (2) |  |

## Channel Rules

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `type` | 128/226 | `string` (128) | `"TRANSACTIONAL"` (64), `"NON_TRANSACTIONAL"` (48), `"NA"` (16) | Push semantic type; mostly on PUSH channel. |
| `preference` | 130/226 | `string` (130) | `"CREDIT_PAYMENT_REMINDER"` (44), `"PURCHASE"` (37), `"CREDIT_AUTOPAY_FATAL"` (12), `"MESSAGE_RECEIVED"` (12), `"GENERAL_MARKETING"` (11), `"GENERIC_MARKETING"` (8), `"CREDIT_AUTOPAY_REMINDER"` (4), `"INVOICE_PAID"` (1), `"CREDIT_STATEMENT_AVAILABLE"` (1) | Push preference/category value. |
| `priority` | 133/226 | `string` (133) | `"Standard"` (133) | Only Standard observed. |
| `freq_control_config` | 121/226 | `object` (121) | object / nested below |  |
| `section` | 92/226 | `string` (92) | `"DEFAULT"` (87), `"URGENT"` (5) | Notification Center section. |
| `expiry_duration` | 93/226 | `object` (93) | object / nested below |  |
| `item_limit` | 88/226 | `integer` (88) | `2` (21), `3` (17), `5` (8), `10` (7), `1` (6), `-1` (6), `-2` (3), `20` (3), `4` (2), `23` (2), `15` (2), `11` (1), `-11` (1), `12` (1), `-10` (1), `-8` (1), `8` (1), `56` (1), `30` (1), `-14` (1), `-12` (1), `14` (1) | Integer; includes negative values in QA data. |
| `replicated_to_channels` | 52/226 | `array` (52) | array lengths: `0` (20), `1` (32); values: `1001` (32) | For omni push replication to NC. |
| `replicated_from_channel` | 32/226 | `integer` (32) | `1002` (32) | For NC replicated from push. |
| `contextual_rules` | 28/226 | `object` (28) | object / nested below | Rule object; same logical shape as content contextual rules. |

### Frequency Control

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `freq_enabled` | 94/121 | `boolean` (94) | `false` (94) | Optional; absent appears to imply enabled/default. |
| `base_attributes` | 121/121 | `array` (121) | array lengths: `1` (121) | Always one item in this sample. |

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `attribute` | 121/121 | `string` (121) | `"SENT"` (121) | Only SENT observed. |
| `freq_period` | 121/121 | `string` (121) | `"ONCE"` (117), `"ALWAYS"` (4) | Frequency period enum candidate. |

### Expiry Duration

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `value` | 93/93 | `string` (93) | `"2"` (31), `"3"` (18), `"10"` (11), `"7"` (7), `"90"` (6), `"30"` (4), `"20"` (3), `"12"` (2), `"5"` (2), `"1"` (2), `"32"` (2), `"4"` (1), `"15"` (1), `"34"` (1), `"21"` (1), `"120"` (1) | Stored as string, even when numeric. |
| `unit` | 93/93 | `string` (93) | `"DAYS"` (92), `"MINUTES"` (1) | DAYS except one MINUTES sample. |

## Content Object

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `content_id` | 282/282 | `string` (282) | 282 unique; examples: `"3757828121"` (1), `"2600214803"` (1), `"9038299381"` (1), `"9854050278"` (1), `"1464402037"` (1) | ID-like string; do not enum. |
| `content_name` | 282/282 | `string` (282) | `"Variant 1"` (200), `"Variant 2"` (34), `"Variant 3"` (10), `"Variant 4"` (4), `"Spring Sale Notification Center - 1"` (3), `"Spring Sale Push Notification - "` (3), `"push_omni"` (2), `"Spring Sale Push Notification-1"` (2), `"Spring Sale Notification Center"` (2), `"Cw"` (2), `"omni_test"` (2), `"Spring Sale Push Notification"` (2), `"bulk_no_exp_content"` (1), `"test"` (1), `"sat_wwoww"` (1), `"sat_wwoww_2"` (1), `"treatment_variant_a"` (1), `"Variant 5"` (1), `"testing"` (1), `"testing2"` (1), `"2 - Spring Sale Notification"` (1), `"1 - Spring Sale Notification"` (1), `"4 - Spring Sale Notification"` (1), `"3 - Spring Sale Notification"` (1), `"Bulk NC Test NC Alert"` (1), `"Test Content"` (1), `"Variant 7"` (1), `"contetn1"` (1) | Mostly variant labels, but free text. |
| `content_variant_code` | 282/282 | `integer` (282) | `1` (227), `2` (37), `3` (12), `4` (4), `5` (1), `7` (1) | Integer variant number. |
| `default_locale` | 282/282 | `string` (282) | `"en-US"` (265), `"en_US"` (17) | Two spellings observed: hyphen and underscore. |
| `content_payload` | 282/282 | `object` (282) | object / nested below | Nested object; title/body/deeplink live here. |
| `content_rules` | 76/282 | `object` (76) | object / nested below | Optional experiment/contextual rules. |
| `content_legal_review_id` | 17/282 | `string` (17) | `"LEGAL-2026-001"` (8), `"https://paypal-sandbox-694.atlassian.net/browse/DTLOCALZN-29934"` (6), `"hello there"` (2), `"https://home"` (1) | Optional ID/URL/free text in QA sample. |
| `content_legal_review_exception` | 211/282 | `boolean` (211) | `true` (193), `false` (18) | Boolean; if true, reason usually present. |
| `content_legal_review_exception_reason` | 193/282 | `string` (193) | 57 unique; examples: `"testing"` (29), `"test"` (25), `"Testing"` (22), `"NA"` (6), `"fafaaf"` (5) | Free text reason. |
| `status` | 282/282 | `string` (282) | `"ACTIVE"` (282) | Constant in this sample. |
| `created_by` | 282/282 | `string` (282) | `"praghuvanshi"` (166), `"hukaur"` (34), `"samlnu"` (24), `"shivangsrivastav"` (14), `"apasharma"` (13), `"spratapsingh"` (8), `"pperina"` (8), `"gsharma9"` (6), `"testuser"` (2), `"nmalla3"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"pujatav"` (1) |  |
| `time_created_ms` | 282/282 | `integer` (282) | 187 unique; examples: `1780461681422` (8), `1780642020192` (6), `1780029468814` (5), `1779082187056` (4), `1779083222230` (4) |  |
| `updated_by` | 282/282 | `string` (282) | `"praghuvanshi"` (166), `"hukaur"` (28), `"samlnu"` (25), `"shivangsrivastav"` (14), `"apasharma"` (13), `"spratapsingh"` (8), `"pperina"` (8), `"gsharma9"` (6), `"nmall6a"` (4), `"nmalla3"` (3), `"testuser"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"gyejju"` (1) |  |
| `time_updated_ms` | 282/282 | `integer` (282) | 148 unique; examples: `1780461949863` (8), `1779700094454` (6), `1780642024711` (6), `1780979343762` (5), `1780508911285` (5) |  |

## Content Payload

### Localizable Content

| Locale key | Observed payloads | Child fields |
| --- | --- | --- |
| `en-US` | 265 | `body` (265), `title` (265), `custom_view` (11) |
| `en_US` | 17 | `body` (17), `title` (17) |
| `es_ES` | 8 | `body` (8), `title` (8) |
| `es-US` | 3 | `body` (3), `title` (3) |
| `en-AU` | 1 | `body` (1), `title` (1) |
| `en-CA` | 1 | `body` (1), `title` (1) |
| `es-ES` | 1 | `body` (1), `title` (1) |

Common localizable fields:

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `localizable_content.{locale}.title` | 296/296 | `string` | 99+ unique strings across locales. | User-visible title copy. |
| `localizable_content.{locale}.body` | 296/296 | `string` | 101+ unique strings across locales. | User-visible body copy. |
| `localizable_content.{locale}.custom_view` | 11/296 | `object` | keys: `"title"` (4), `"type"` (3), `"key"` (1), `"message"` (1), `"template_id"` (1), `"ssb"` (1), `"afaf"` (1) | Optional localized custom view payload. |

### Non-Localizable Content

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `deep_link` | 280/280 | `string` (280) | `"paypal://home"` (219), `"https://deeplink"` (16), `"paypal://home?promo=spring_sale"` (8), `"https://test.com"` (6), `"https://paypal.com/checkout"` (4), `"paypal://home?${transactionId}"` (3), `"https://variant2.com"` (2), `"paypal://homes"` (2), `"https://deeplink3"` (2), `"https://deeplink2"` (2), `"https://example.com/icons/money.png"` (2), `"${WebsiteURL}"` (2), `"myapp://aaa"` (2), `"${wow}"` (1), `"htpps://deeplink"` (1), `"https://home"` (1), `"paypal://home?${somedph}"` (1), `"https://deeplink5"` (1), `"https://www"` (1), `"paypal://activity"` (1), `"https://www.paypal.com/mobile-app/myaccount/activity"` (1), `"paypal://"` (1), `"https://"` (1) | Usually paypal://home; allow URI/string. |
| `image_url` | 22/280 | `string` (22) | `"ImageURL"` (6), `"fafa"` (2), `"dmaknfadfamlkafmaklmgfamfam"` (2), `"fagklnmklag"` (2), `"famnafkjaf"` (2), `"amgklgmana"` (2), `"aggaag"` (1), `"RichPushImage"` (1), `"mgkamgk"` (1), `"fmamfa"` (1), `"https://media.giphy.com/media/NsTceS2EH3Mli/giphy.gif"` (1), `"444"` (1) | Optional rich push/image URL string; QA sample includes placeholders. |
| `icon_url` | 10/280 | `string` (10) | `"ImageURL"` (2), `"IconURL33"` (1), `"IconURL"` (1), `"fafafaaffafamdlkamd"` (1), `"IconURLType2144"` (1), `"fanlakfnfa"` (1), `"IconURLChangeeee"` (1), `"Icon"` (1), `"https://media.giphy.com/media/NsTceS2EH3Mli/giphy.gif"` (1) | Optional icon URL string; QA sample includes placeholders. |
| `custom_view` | 131/280 | `object` (131) | object / nested below | Optional object; mostly type/template_id placeholders. |

Observed `non_localizable_content.custom_view` keys:

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `alert_timestamp` | 1/131 | `string` (1) | `"February 9 at 2:45 PM (PST)"` (1) | Identity alert sample only. |
| `device_location` | 1/131 | `string` (1) | `"Near Rochester, NY, USA"` (1) | Identity alert sample only. |
| `device_name` | 1/131 | `string` (1) | `"MacBook Pro Chrome"` (1) | Identity alert sample only. |
| `local` | 1/131 | `string` (1) | `""` (1) |  |
| `template_id` | 8/131 | `string` (8) | `""` (5), `"12"` (2), `"1213"` (1) | Optional string; often empty. |
| `type` | 122/131 | `string` (122) | `""` (118), `"1313"` (1), `"nfakng"` (1), `"identity_unified_alerts"` (1), `"fafa"` (1) | Mostly empty string in QA data. |

## Content Rules

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `experiment_details` | 54/76 | `object` (54) | object / nested below | Experiment assignment per variant/content. |
| `contextual_rules` | 35/76 | `object` (35) | object / nested below | Variant-level rules. |

### Experiment Details

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `experiment_name` | 54/54 | `string` (54) | `""` (28), `"spring_sale_exp_v1"` (11), `"comms_hub_live_test"` (6), `"money_received_test_sp"` (6), `"comms_config_store"` (2), `"bulk_audit"` (1) | Can be empty string. |
| `treatment_name` | 54/54 | `string` (54) | `""` (31), `"treatment_variant_a"` (6), `"treatment_variant_b"` (5), `"General Users"` (4), `"Control"` (3), `"Power Users"` (2), `"CommsTeam"` (2), `"Test"` (1) | Can be empty string. |

## Contextual Rule Shape

`contextual_rules` appears in both `channel_rules` and `content_rules` with the same structure:

```json
{
  "between_groups_operator": "OR",
  "rule_groups": [
    {
      "within_group_operator": "AND",
      "conditions": [
        {
          "attribute": "...",
          "comparison_operator": "EQUAL",
          "value": "...",
          "data_type": "STRING"
        }
      ]
    }
  ]
}
```

| Rule source | Observed count | Variation |
| --- | --- | --- |
| Channel `contextual_rules` objects | 28 | rule_groups lengths: `1` (13), `2` (15) |
| Channel rule groups | 43 | conditions lengths: `1` (35), `2` (8) |
| Channel conditions | 51 |  |
| Content `contextual_rules` objects | 35 | rule_groups lengths: `1` (17), `2` (18) |
| Content rule groups | 53 | conditions lengths: `1` (51), `2` (2) |
| Content conditions | 55 |  |

Channel rule condition fields:

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `attribute` | 51/51 | `string` (51) | `"campaign_engagement_channel"` (7), `"is_first_time_channel"` (7), `"user_account_age"` (6), `"account_status"` (6), `"user_tier"` (6), `"faffa"` (2), `"fagag"` (2), `"pushCP1"` (2), `"PushCP2.1"` (2), `"PushRule2"` (2), `"fsfs"` (2), `"amount"` (1), `"ruleCP1"` (1), `"locale"` (1), `"trigger"` (1), `"this"` (1), `"string"` (1), `"dada"` (1) | Free-form profile/event attribute key. |
| `comparison_operator` | 51/51 | `string` (51) | `"EQUAL"` (26), `"GREATER_THAN"` (15), `"NOT_EQUAL"` (8), `"STARTS_WITH"` (2) | Enum candidate. |
| `value` | 51/51 | `string` (21), `integer` (20), `boolean` (10) | `true` (8), `55` (7), `30` (6), `"ACTIVE"` (6), `"PREMIUM"` (6), `"33"` (3), `2` (3), `"23"` (2), `23` (2), `"faaf"` (2), `false` (2), `122` (1), `"US"` (1), `9` (1), `"3"` (1) | Type depends on data_type. |
| `data_type` | 51/51 | `string` (51) | `"STRING"` (21), `"NUMBER"` (20), `"BOOLEAN"` (10) | Enum candidate. |

Content rule condition fields:

| Field | Observed | Type | Observed values / variation | Schema note |
| --- | --- | --- | --- | --- |
| `attribute` | 55/55 | `string` (55) | `"campaign_engagement_score"` (17), `"is_first_time_user"` (17), `"amount"` (6), `"faf"` (2), `"r"` (2), `"ffa"` (2), `"VCP1"` (2), `"type"` (2), `"VP1"` (1), `"true"` (1), `"af"` (1), `"kk"` (1), `"nmlml"` (1) | Free-form profile/event attribute key. |
| `comparison_operator` | 55/55 | `string` (55) | `"EQUAL"` (31), `"GREATER_THAN"` (14), `"NOT_EQUAL"` (9), `"STARTS_WITH"` (1) | Enum candidate. |
| `value` | 55/55 | `boolean` (19), `string` (5), `integer` (31) | `false` (19), `50` (17), `"2"` (4), `4` (2), `1000` (2), `10000` (2), `22` (2), `200` (2), `300` (2), `"9"` (1), `9` (1), `980` (1) | Type depends on data_type. |
| `data_type` | 55/55 | `string` (55) | `"NUMBER"` (31), `"BOOLEAN"` (19), `"STRING"` (5) | Enum candidate. |

## Observed Enum Candidates

| Path | Observed | Type | Values |
| --- | --- | --- | --- |
| `campaign.status` | 150/150 | `string` (150) | `"DRAFT"` (72), `"SUBMITTED"` (35), `"PUBLISHED"` (33), `"APPROVED"` (7), `"ARCHIVED"` (2), `"APPROVAL_REQUESTED"` (1) |
| `campaign.delivery_type` | 150/150 | `string` (150) | `"API_BASED"` (126), `"SCHEDULED_BULK"` (22), `"NON_TRIGGERED"` (2) |
| `campaign.campaign_product` | 148/150 | `string` (148) | `"Savings"` (56), `"Account"` (46), `"Buyer_Protection"` (25), `"Balance"` (9), `"PayPal_CBMC"` (4), `"Wallet"` (2), `"Subscriptions"` (2), `"Crypto"` (1), `"Offers"` (1), `"PayPal_DebitCard"` (1), `"Passkey"` (1) |
| `campaign.campaign_action` | 148/150 | `string` (148) | `"add_money"` (34), `"add_photo"` (31), `"awareness"` (26), `"confirmation"` (25), `"confirm_address"` (13), `"engage"` (10), `"fix_issue"` (3), `"add_debit_card"` (2), `"enroll"` (2), `"push_opt_in"` (1), `"confirm_email"` (1) |
| `channel_detail.channel_id` | 226/226 | `integer` (226) | `1002` (133), `1001` (93) |
| `channel.channel_name` | 226/226 | `string` (226) | `"PUSH"` (133), `"NOTIFICATION_CENTER"` (93) |
| `channel_rules.type` | 128/226 | `string` (128) | `"TRANSACTIONAL"` (64), `"NON_TRANSACTIONAL"` (48), `"NA"` (16) |
| `channel_rules.preference` | 130/226 | `string` (130) | `"CREDIT_PAYMENT_REMINDER"` (44), `"PURCHASE"` (37), `"CREDIT_AUTOPAY_FATAL"` (12), `"MESSAGE_RECEIVED"` (12), `"GENERAL_MARKETING"` (11), `"GENERIC_MARKETING"` (8), `"CREDIT_AUTOPAY_REMINDER"` (4), `"INVOICE_PAID"` (1), `"CREDIT_STATEMENT_AVAILABLE"` (1) |
| `channel_rules.priority` | 133/226 | `string` (133) | `"Standard"` (133) |
| `channel_rules.section` | 92/226 | `string` (92) | `"DEFAULT"` (87), `"URGENT"` (5) |
| `freq_period` | 121/121 | `string` (121) | `"ONCE"` (117), `"ALWAYS"` (4) |
| `expiry_duration.unit` | 93/93 | `string` (93) | `"DAYS"` (92), `"MINUTES"` (1) |
| `delivery_config.target_type` | 39/150 | `string` (39) | `"DYNAMIC_SEGMENT"` (20), `"CUSTOM_TABLE"` (17), `"ALL_USERS"` (2) |
| `delivery_config.omni_type` | 50/150 | `string` (50) | `"TYPE_1"` (50) |
| `device_filter_rule.device_os` | 18/18 | `string` (18) | `"ALL"` (14), `"ANDROID"` (4) |
| `android_app_version.operator` | 18/18 | `string` (18) | `"GREATER_THAN_OR_EQUAL"` (18) |
| `default_locale` | 282/282 | `string` (282) | `"en-US"` (265), `"en_US"` (17) |
| `content.status` | 282/282 | `string` (282) | `"ACTIVE"` (282) |
| `contextual_rules.comparison_operator` | 106/106 | `string` (106) | `"EQUAL"` (57), `"GREATER_THAN"` (29), `"NOT_EQUAL"` (17), `"STARTS_WITH"` (3) |
| `contextual_rules.data_type` | 106/106 | `string` (106) | `"NUMBER"` (51), `"BOOLEAN"` (29), `"STRING"` (26) |
| `content_rules.experiment_details.experiment_name` | 54/54 | `string` (54) | `""` (28), `"spring_sale_exp_v1"` (11), `"comms_hub_live_test"` (6), `"money_received_test_sp"` (6), `"comms_config_store"` (2), `"bulk_audit"` (1) |
| `content_rules.experiment_details.treatment_name` | 54/54 | `string` (54) | `""` (31), `"treatment_variant_a"` (6), `"treatment_variant_b"` (5), `"General Users"` (4), `"Control"` (3), `"Power Users"` (2), `"CommsTeam"` (2), `"Test"` (1) |

## Observed Country Codes

`countries[]` had 205 unique observed values across 150 campaign arrays. Full observed set:

`AD`, `AE`, `AG`, `AI`, `AL`, `AM`, `AN`, `AO`, `AR`, `AS`, `AT`, `AU`, `AW`, `AZ`, `BA`, `BB`, `BE`, `BF`, `BG`, `BH`, `BI`, `BJ`, `BM`, `BN`, `BO`, `BR`, `BS`, `BT`, `BW`, `BY`, `BZ`, `C2`, `CA`, `CD`, `CG`, `CH`, `CI`, `CK`, `CL`, `CM`, `CN`, `CO`, `CR`, `CV`, `CY`, `CZ`, `DE`, `DJ`, `DK`, `DM`, `DO`, `DZ`, `EC`, `EE`, `EG`, `ER`, `ES`, `ET`, `FI`, `FJ`, `FK`, `FM`, `FO`, `FR`, `GA`, `GB`, `GD`, `GE`, `GF`, `GI`, `GL`, `GM`, `GN`, `GP`, `GR`, `GT`, `GW`, `GY`, `HK`, `HN`, `HR`, `HU`, `ID`, `IE`, `IL`, `IN`, `IS`, `IT`, `JM`, `JO`, `JP`, `KE`, `KG`, `KH`, `KI`, `KM`, `KN`, `KR`, `KW`, `KY`, `KZ`, `LA`, `LC`, `LI`, `LK`, `LS`, `LT`, `LU`, `LV`, `MA`, `MC`, `MD`, `ME`, `MG`, `MH`, `MK`, `ML`, `MN`, `MQ`, `MR`, `MS`, `MT`, `MU`, `MV`, `MW`, `MX`, `MY`, `MZ`, `NA`, `NC`, `NE`, `NF`, `NG`, `NI`, `NL`, `NO`, `NP`, `NR`, `NU`, `NZ`, `OM`, `PA`, `PE`, `PF`, `PG`, `PH`, `PL`, `PM`, `PN`, `PT`, `PW`, `PY`, `QA`, `RE`, `RO`, `RS`, `RU`, `RW`, `SA`, `SB`, `SC`, `SE`, `SG`, `SH`, `SI`, `SJ`, `SK`, `SL`, `SM`, `SN`, `SO`, `SR`, `ST`, `SV`, `SZ`, `TC`, `TD`, `TG`, `TH`, `TJ`, `TM`, `TN`, `TO`, `TR`, `TT`, `TV`, `TW`, `TZ`, `UA`, `UG`, `US`, `UY`, `VA`, `VC`, `VE`, `VG`, `VN`, `VU`, `WF`, `WS`, `YE`, `YT`, `ZA`, `ZM`, `ZW`

## High-Cardinality / Free-Text Fields

| Field family | Observed | Type | Unique/shape | Examples | Schema note |
| --- | --- | --- | --- | --- | --- |
| `campaign_ref_id` | 150/150 | `string` (150) | 150 | `"1684303559"` (1), `"4235959898"` (1), `"2999435171"` (1), `"5377083497"` (1), `"7545144522"` (1), `"3149310764"` (1) | ID-like string. |
| `campaign_id` | 150/150 | `string` (150) | 150 | `"3436284626"` (1), `"3927014933"` (1), `"5008388238"` (1), `"5308612704"` (1), `"1937150588"` (1), `"2650433009"` (1) | ID-like string. |
| `campaign_name` | 150/150 | `string` (150) | 150 | `"NC_channgel"` (1), `"Bulk_4_publish"` (1), `"famglkmaklga"` (1), `"omni_ptt"` (1), `"Push_NC_Omni"` (1), `"csmpsihnPudhVustomView"` (1) | Human-entered free text. |
| `description` | 114/150 | `string` (114) | 88 | `"This is a test cmapaign"` (6), `"mgaklnagklnagmkm"` (5), `"25May-NC25May-NC25May-NC25May-NC25May-NC"` (3), `"omni channel added Push + Non Transactional"` (3), `"Omni Testing 26th may ..akngjknagj"` (3), `"This is a test campaign"` (3) | Optional human-entered free text. |
| `owners[]` | 150/150 | `array` | 21 | `"praghuvanshi"` (108), `"hukaur"` (33), `"shivangsrivastav"` (22), `"samlnu"` (20), `"apasharma"` (9), `"nmalla"` (7) | User IDs; array. |
| `team_dls[]` | 148/150 | `array` | 66 | `"test@paypal.com"` (14), `"sam@paypal.com"` (11), `"comms-decisioning-dev@paypal.com"` (8), `"marketing-team@paypal.com"` (8), `"communications-team@paypal.com"` (8), `"affa@paypal.com"` (7) | DL/email strings; optional array. |
| `created_by / updated_by` | 150/150 | `string` (150) | 13 | `"praghuvanshi"` (86), `"hukaur"` (16), `"samlnu"` (15), `"apasharma"` (9), `"shivangsrivastav"` (9), `"spratapsingh"` (4) | Audit metadata; same style appears at campaign, channel, and content levels. |
| `time_created_ms / time_updated_ms` | 150/150 | `integer` (150) | 150 | `1779441707756` (1), `1780550283629` (1), `1779084698314` (1), `1779451567425` (1), `1779428491880` (1), `1781075022673` (1) | Epoch milliseconds; system-populated. |
| `content_id` | 282/282 | `string` (282) | 282 | `"3757828121"` (1), `"2600214803"` (1), `"9038299381"` (1), `"9854050278"` (1), `"1464402037"` (1), `"8192023144"` (1) | ID-like string. |
| `content_name` | 282/282 | `string` (282) | 28 | `"Variant 1"` (200), `"Variant 2"` (34), `"Variant 3"` (10), `"Variant 4"` (4), `"Spring Sale Notification Center - 1"` (3), `"Spring Sale Push Notification - "` (3) | Mostly variant names, but free text. |
| `title/body copy` | 282/282 | `object` (282) | nested | nested object | Nested localized strings; should be free text. |
| `deep_link/image_url/icon_url` | 280/280 | `string` (280) | 23 | `"paypal://home"` (219), `"https://deeplink"` (16), `"paypal://home?promo=spring_sale"` (8), `"https://test.com"` (6), `"https://paypal.com/checkout"` (4), `"paypal://home?${transactionId}"` (3) | URI/placeholders in QA; validate as strings/URIs, not enums. |
| `rule condition attribute` | 106/106 | `string` (106) | 30 | `"campaign_engagement_score"` (17), `"is_first_time_user"` (17), `"amount"` (7), `"campaign_engagement_channel"` (7), `"is_first_time_channel"` (7), `"user_account_age"` (6) | Free-form attribute key; values vary by upstream profile/event contract. |
| `rule condition value` | 106/106 | `string` (26), `integer` (51), `boolean` (29) | 25 | `false` (21), `50` (17), `true` (8), `55` (7), `30` (6), `"ACTIVE"` (6) | Union of string/integer/boolean based on data_type. |

## Full Observed Field Path Inventory

This table is intentionally exhaustive at the field-path level. Array item paths use `[]`. For scalar paths with many unique values, only examples are shown.

| Path | Occurrences | Type | Observed variation |
| --- | --- | --- | --- |
| `campaigns` | 1 | `array` (1) | array lengths: `150` (1) |
| `campaigns.[]` | 150 | `object` (150) | object |
| `campaigns.[].approval_request_id` | 41 | `string` (41) | 32 unique; examples: `"DIRECT_APPROVAL"` (10), `"RITM3548107"` (1), `"RITM3548235"` (1), `"RITM3548102"` (1), `"RITM3548132"` (1) |
| `campaigns.[].approval_request_status` | 41 | `string` (41) | `"CLOSED"` (30), `"DIRECT_APPROVAL"` (10), `"OPEN"` (1) |
| `campaigns.[].approval_requested_by` | 41 | `string` (41) | `"praghuvanshi"` (19), `"shivangsrivastav"` (9), `"hukaur"` (5), `"spratapsingh"` (3), `"gsharma9"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"samlnu"` (1) |
| `campaigns.[].approval_requested_time_ms` | 41 | `integer` (41) | 41 unique; examples: `1779703629390` (1), `1780298319124` (1), `1780982385180` (1), `1779700177893` (1), `1779787221761` (1) |
| `campaigns.[].campaign_action` | 148 | `string` (148) | `"add_money"` (34), `"add_photo"` (31), `"awareness"` (26), `"confirmation"` (25), `"confirm_address"` (13), `"engage"` (10), `"fix_issue"` (3), `"add_debit_card"` (2), `"enroll"` (2), `"push_opt_in"` (1), `"confirm_email"` (1) |
| `campaigns.[].campaign_id` | 150 | `string` (150) | 150 unique; examples: `"3436284626"` (1), `"3927014933"` (1), `"5008388238"` (1), `"5308612704"` (1), `"1937150588"` (1) |
| `campaigns.[].campaign_name` | 150 | `string` (150) | 150 unique; examples: `"NC_channgel"` (1), `"Bulk_4_publish"` (1), `"famglkmaklga"` (1), `"omni_ptt"` (1), `"Push_NC_Omni"` (1) |
| `campaigns.[].campaign_product` | 148 | `string` (148) | `"Savings"` (56), `"Account"` (46), `"Buyer_Protection"` (25), `"Balance"` (9), `"PayPal_CBMC"` (4), `"Wallet"` (2), `"Subscriptions"` (2), `"Crypto"` (1), `"Offers"` (1), `"PayPal_DebitCard"` (1), `"Passkey"` (1) |
| `campaigns.[].campaign_ref_id` | 150 | `string` (150) | 150 unique; examples: `"1684303559"` (1), `"4235959898"` (1), `"2999435171"` (1), `"5377083497"` (1), `"7545144522"` (1) |
| `campaigns.[].channel_details` | 150 | `array` (150) | array lengths: `0` (4), `1` (66), `2` (80) |
| `campaigns.[].channel_details.[]` | 226 | `object` (226) | object |
| `campaigns.[].channel_details.[].channel_id` | 226 | `integer` (226) | `1002` (133), `1001` (93) |
| `campaigns.[].channel_details.[].channel_name` | 226 | `string` (226) | `"PUSH"` (133), `"NOTIFICATION_CENTER"` (93) |
| `campaigns.[].channel_details.[].channel_rules` | 226 | `object` (226) | object |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules` | 28 | `object` (28) | object |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.between_groups_operator` | 28 | `string` (28) | `"OR"` (28) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups` | 28 | `array` (28) | array lengths: `1` (13), `2` (15) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[]` | 43 | `object` (43) | object |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].conditions` | 43 | `array` (43) | array lengths: `1` (35), `2` (8) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].conditions.[]` | 51 | `object` (51) | object |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].conditions.[].attribute` | 51 | `string` (51) | `"campaign_engagement_channel"` (7), `"is_first_time_channel"` (7), `"user_account_age"` (6), `"account_status"` (6), `"user_tier"` (6), `"faffa"` (2), `"fagag"` (2), `"pushCP1"` (2), `"PushCP2.1"` (2), `"PushRule2"` (2), `"fsfs"` (2), `"amount"` (1), `"ruleCP1"` (1), `"locale"` (1), `"trigger"` (1), `"this"` (1), `"string"` (1), `"dada"` (1) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].conditions.[].comparison_operator` | 51 | `string` (51) | `"EQUAL"` (26), `"GREATER_THAN"` (15), `"NOT_EQUAL"` (8), `"STARTS_WITH"` (2) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].conditions.[].data_type` | 51 | `string` (51) | `"STRING"` (21), `"NUMBER"` (20), `"BOOLEAN"` (10) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].conditions.[].value` | 51 | `string` (21), `integer` (20), `boolean` (10) | `true` (8), `55` (7), `30` (6), `"ACTIVE"` (6), `"PREMIUM"` (6), `"33"` (3), `2` (3), `"23"` (2), `23` (2), `"faaf"` (2), `false` (2), `122` (1), `"US"` (1), `9` (1), `"3"` (1) |
| `campaigns.[].channel_details.[].channel_rules.contextual_rules.rule_groups.[].within_group_operator` | 43 | `string` (43) | `"AND"` (43) |
| `campaigns.[].channel_details.[].channel_rules.expiry_duration` | 93 | `object` (93) | object |
| `campaigns.[].channel_details.[].channel_rules.expiry_duration.unit` | 93 | `string` (93) | `"DAYS"` (92), `"MINUTES"` (1) |
| `campaigns.[].channel_details.[].channel_rules.expiry_duration.value` | 93 | `string` (93) | `"2"` (31), `"3"` (18), `"10"` (11), `"7"` (7), `"90"` (6), `"30"` (4), `"20"` (3), `"12"` (2), `"5"` (2), `"1"` (2), `"32"` (2), `"4"` (1), `"15"` (1), `"34"` (1), `"21"` (1), `"120"` (1) |
| `campaigns.[].channel_details.[].channel_rules.freq_control_config` | 121 | `object` (121) | object |
| `campaigns.[].channel_details.[].channel_rules.freq_control_config.base_attributes` | 121 | `array` (121) | array lengths: `1` (121) |
| `campaigns.[].channel_details.[].channel_rules.freq_control_config.base_attributes.[]` | 121 | `object` (121) | object |
| `campaigns.[].channel_details.[].channel_rules.freq_control_config.base_attributes.[].attribute` | 121 | `string` (121) | `"SENT"` (121) |
| `campaigns.[].channel_details.[].channel_rules.freq_control_config.base_attributes.[].freq_period` | 121 | `string` (121) | `"ONCE"` (117), `"ALWAYS"` (4) |
| `campaigns.[].channel_details.[].channel_rules.freq_control_config.freq_enabled` | 94 | `boolean` (94) | `false` (94) |
| `campaigns.[].channel_details.[].channel_rules.item_limit` | 88 | `integer` (88) | 22 unique; examples: `2` (21), `3` (17), `5` (8), `10` (7), `1` (6) |
| `campaigns.[].channel_details.[].channel_rules.preference` | 130 | `string` (130) | `"CREDIT_PAYMENT_REMINDER"` (44), `"PURCHASE"` (37), `"CREDIT_AUTOPAY_FATAL"` (12), `"MESSAGE_RECEIVED"` (12), `"GENERAL_MARKETING"` (11), `"GENERIC_MARKETING"` (8), `"CREDIT_AUTOPAY_REMINDER"` (4), `"INVOICE_PAID"` (1), `"CREDIT_STATEMENT_AVAILABLE"` (1) |
| `campaigns.[].channel_details.[].channel_rules.priority` | 133 | `string` (133) | `"Standard"` (133) |
| `campaigns.[].channel_details.[].channel_rules.replicated_from_channel` | 32 | `integer` (32) | `1002` (32) |
| `campaigns.[].channel_details.[].channel_rules.replicated_to_channels` | 52 | `array` (52) | array lengths: `0` (20), `1` (32) |
| `campaigns.[].channel_details.[].channel_rules.replicated_to_channels.[]` | 32 | `integer` (32) | `1001` (32) |
| `campaigns.[].channel_details.[].channel_rules.section` | 92 | `string` (92) | `"DEFAULT"` (87), `"URGENT"` (5) |
| `campaigns.[].channel_details.[].channel_rules.type` | 128 | `string` (128) | `"TRANSACTIONAL"` (64), `"NON_TRANSACTIONAL"` (48), `"NA"` (16) |
| `campaigns.[].channel_details.[].content` | 226 | `array` (226) | array lengths: `0` (3), `1` (184), `2` (25), `3` (9), `4` (4), `5` (1) |
| `campaigns.[].channel_details.[].content.[]` | 282 | `object` (282) | object |
| `campaigns.[].channel_details.[].content.[].content_id` | 282 | `string` (282) | 282 unique; examples: `"3757828121"` (1), `"2600214803"` (1), `"9038299381"` (1), `"9854050278"` (1), `"1464402037"` (1) |
| `campaigns.[].channel_details.[].content.[].content_legal_review_exception` | 211 | `boolean` (211) | `true` (193), `false` (18) |
| `campaigns.[].channel_details.[].content.[].content_legal_review_exception_reason` | 193 | `string` (193) | 57 unique; examples: `"testing"` (29), `"test"` (25), `"Testing"` (22), `"NA"` (6), `"fafaaf"` (5) |
| `campaigns.[].channel_details.[].content.[].content_legal_review_id` | 17 | `string` (17) | `"LEGAL-2026-001"` (8), `"https://paypal-sandbox-694.atlassian.net/browse/DTLOCALZN-29934"` (6), `"hello there"` (2), `"https://home"` (1) |
| `campaigns.[].channel_details.[].content.[].content_name` | 282 | `string` (282) | 28 unique; examples: `"Variant 1"` (200), `"Variant 2"` (34), `"Variant 3"` (10), `"Variant 4"` (4), `"Spring Sale Notification Center - 1"` (3) |
| `campaigns.[].channel_details.[].content.[].content_payload` | 282 | `object` (282) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content` | 282 | `object` (282) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-AU` | 1 | `object` (1) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-AU.body` | 1 | `string` (1) | `"body"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-AU.title` | 1 | `string` (1) | `"title"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-CA` | 1 | `object` (1) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-CA.body` | 1 | `string` (1) | `"encanadabody"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-CA.title` | 1 | `string` (1) | `"encandatitle"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US` | 265 | `object` (265) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.body` | 265 | `string` (265) | 101 unique; examples: `"Body"` (57), `"body"` (16), `"test campaign"` (12), `"Enter the dragon"` (8), `"Vody"` (7) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view` | 11 | `object` (11) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.afaf` | 1 | `string` (1) | `"afaf"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.key` | 1 | `string` (1) | `"test"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.message` | 1 | `string` (1) | `"Approve or deny this login attempt"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.ssb` | 1 | `string` (1) | `"bsbsbs"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.template_id` | 1 | `string` (1) | `"3"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.title` | 4 | `string` (4) | `"Title"` (1), `"priyanka"` (1), `"WOW"` (1), `"gamgm"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.custom_view.type` | 3 | `string` (3) | `"t"` (2), `"1213"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en-US.title` | 265 | `string` (265) | 99 unique; examples: `"Paypal"` (78), `"title"` (14), `"test campaign"` (12), `"Push"` (7), `"Paypal2"` (5) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en_US` | 17 | `object` (17) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en_US.body` | 17 | `string` (17) | `"Add money to your account and get 5% bonus"` (9), `"Limited time offer - spring sale ends soon!"` (6), `"This is a bulk notification without experiment config"` (1), `"This is treatment A"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.en_US.title` | 17 | `string` (17) | `"HEY THERE!"` (5), `"Spring Sale is Here!"` (4), `"Hey thereee"` (4), `"Exclusive: Add Money + Get 5% Bonus"` (2), `"Bulk No Exp Test"` (1), `"Statsig Test - Variant A"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es-ES` | 1 | `object` (1) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es-ES.body` | 1 | `string` (1) | `"Añade dinero a tu cuenta y obtén un 5% de bonificación"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es-ES.title` | 1 | `string` (1) | `"¡La Venta de Primavera Está Aquí!"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es-US` | 3 | `object` (3) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es-US.body` | 3 | `string` (3) | `"sgmlknsglkgn"` (1), `"ESAA"` (1), `"body 4"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es-US.title` | 3 | `string` (3) | `"klnglknga"` (1), `"ES "` (1), `"title4"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es_ES` | 8 | `object` (8) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es_ES.body` | 8 | `string` (8) | `"Añade dinero a tu cuenta y obtén un 5% de bonificación"` (8) |
| `campaigns.[].channel_details.[].content.[].content_payload.localizable_content.es_ES.title` | 8 | `string` (8) | `"¡La Venta de Primavera Está Aquí!"` (8) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content` | 280 | `object` (280) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view` | 131 | `object` (131) | object |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view.alert_timestamp` | 1 | `string` (1) | `"February 9 at 2:45 PM (PST)"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view.device_location` | 1 | `string` (1) | `"Near Rochester, NY, USA"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view.device_name` | 1 | `string` (1) | `"MacBook Pro Chrome"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view.local` | 1 | `string` (1) | `""` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view.template_id` | 8 | `string` (8) | `""` (5), `"12"` (2), `"1213"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.custom_view.type` | 122 | `string` (122) | `""` (118), `"1313"` (1), `"nfakng"` (1), `"identity_unified_alerts"` (1), `"fafa"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.deep_link` | 280 | `string` (280) | 23 unique; examples: `"paypal://home"` (219), `"https://deeplink"` (16), `"paypal://home?promo=spring_sale"` (8), `"https://test.com"` (6), `"https://paypal.com/checkout"` (4) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.icon_url` | 10 | `string` (10) | `"ImageURL"` (2), `"IconURL33"` (1), `"IconURL"` (1), `"fafafaaffafamdlkamd"` (1), `"IconURLType2144"` (1), `"fanlakfnfa"` (1), `"IconURLChangeeee"` (1), `"Icon"` (1), `"https://media.giphy.com/media/NsTceS2EH3Mli/giphy.gif"` (1) |
| `campaigns.[].channel_details.[].content.[].content_payload.non_localizable_content.image_url` | 22 | `string` (22) | `"ImageURL"` (6), `"fafa"` (2), `"dmaknfadfamlkafmaklmgfamfam"` (2), `"fagklnmklag"` (2), `"famnafkjaf"` (2), `"amgklgmana"` (2), `"aggaag"` (1), `"RichPushImage"` (1), `"mgkamgk"` (1), `"fmamfa"` (1), `"https://media.giphy.com/media/NsTceS2EH3Mli/giphy.gif"` (1), `"444"` (1) |
| `campaigns.[].channel_details.[].content.[].content_rules` | 76 | `object` (76) | object |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules` | 35 | `object` (35) | object |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.between_groups_operator` | 35 | `string` (35) | `"OR"` (35) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups` | 35 | `array` (35) | array lengths: `1` (17), `2` (18) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[]` | 53 | `object` (53) | object |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].conditions` | 53 | `array` (53) | array lengths: `1` (51), `2` (2) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].conditions.[]` | 55 | `object` (55) | object |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].conditions.[].attribute` | 55 | `string` (55) | `"campaign_engagement_score"` (17), `"is_first_time_user"` (17), `"amount"` (6), `"faf"` (2), `"r"` (2), `"ffa"` (2), `"VCP1"` (2), `"type"` (2), `"VP1"` (1), `"true"` (1), `"af"` (1), `"kk"` (1), `"nmlml"` (1) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].conditions.[].comparison_operator` | 55 | `string` (55) | `"EQUAL"` (31), `"GREATER_THAN"` (14), `"NOT_EQUAL"` (9), `"STARTS_WITH"` (1) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].conditions.[].data_type` | 55 | `string` (55) | `"NUMBER"` (31), `"BOOLEAN"` (19), `"STRING"` (5) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].conditions.[].value` | 55 | `boolean` (19), `string` (5), `integer` (31) | `false` (19), `50` (17), `"2"` (4), `4` (2), `1000` (2), `10000` (2), `22` (2), `200` (2), `300` (2), `"9"` (1), `9` (1), `980` (1) |
| `campaigns.[].channel_details.[].content.[].content_rules.contextual_rules.rule_groups.[].within_group_operator` | 53 | `string` (53) | `"AND"` (53) |
| `campaigns.[].channel_details.[].content.[].content_rules.experiment_details` | 54 | `object` (54) | object |
| `campaigns.[].channel_details.[].content.[].content_rules.experiment_details.experiment_name` | 54 | `string` (54) | `""` (28), `"spring_sale_exp_v1"` (11), `"comms_hub_live_test"` (6), `"money_received_test_sp"` (6), `"comms_config_store"` (2), `"bulk_audit"` (1) |
| `campaigns.[].channel_details.[].content.[].content_rules.experiment_details.treatment_name` | 54 | `string` (54) | `""` (31), `"treatment_variant_a"` (6), `"treatment_variant_b"` (5), `"General Users"` (4), `"Control"` (3), `"Power Users"` (2), `"CommsTeam"` (2), `"Test"` (1) |
| `campaigns.[].channel_details.[].content.[].content_variant_code` | 282 | `integer` (282) | `1` (227), `2` (37), `3` (12), `4` (4), `5` (1), `7` (1) |
| `campaigns.[].channel_details.[].content.[].created_by` | 282 | `string` (282) | `"praghuvanshi"` (166), `"hukaur"` (34), `"samlnu"` (24), `"shivangsrivastav"` (14), `"apasharma"` (13), `"spratapsingh"` (8), `"pperina"` (8), `"gsharma9"` (6), `"testuser"` (2), `"nmalla3"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"pujatav"` (1) |
| `campaigns.[].channel_details.[].content.[].default_locale` | 282 | `string` (282) | `"en-US"` (265), `"en_US"` (17) |
| `campaigns.[].channel_details.[].content.[].status` | 282 | `string` (282) | `"ACTIVE"` (282) |
| `campaigns.[].channel_details.[].content.[].time_created_ms` | 282 | `integer` (282) | 187 unique; examples: `1780461681422` (8), `1780642020192` (6), `1780029468814` (5), `1779082187056` (4), `1779083222230` (4) |
| `campaigns.[].channel_details.[].content.[].time_updated_ms` | 282 | `integer` (282) | 148 unique; examples: `1780461949863` (8), `1779700094454` (6), `1780642024711` (6), `1780979343762` (5), `1780508911285` (5) |
| `campaigns.[].channel_details.[].content.[].updated_by` | 282 | `string` (282) | `"praghuvanshi"` (166), `"hukaur"` (28), `"samlnu"` (25), `"shivangsrivastav"` (14), `"apasharma"` (13), `"spratapsingh"` (8), `"pperina"` (8), `"gsharma9"` (6), `"nmall6a"` (4), `"nmalla3"` (3), `"testuser"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"gyejju"` (1) |
| `campaigns.[].channel_details.[].created_by` | 226 | `string` (226) | `"praghuvanshi"` (139), `"hukaur"` (26), `"samlnu"` (15), `"shivangsrivastav"` (14), `"apasharma"` (11), `"spratapsingh"` (6), `"gsharma9"` (6), `"testuser"` (2), `"pperina"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"pujatav"` (1) |
| `campaigns.[].channel_details.[].status` | 226 | `string` (226) | `"ACTIVE"` (226) |
| `campaigns.[].channel_details.[].time_created_ms` | 226 | `integer` (226) | 170 unique; examples: `1779451567425` (2), `1779428491880` (2), `1779865013447` (2), `1779450901031` (2), `1779703619843` (2) |
| `campaigns.[].channel_details.[].time_updated_ms` | 226 | `integer` (226) | 147 unique; examples: `1779441846767` (2), `1779451987965` (2), `1779431143256` (2), `1780306873726` (2), `1779451328562` (2) |
| `campaigns.[].channel_details.[].updated_by` | 226 | `string` (226) | `"praghuvanshi"` (138), `"hukaur"` (20), `"samlnu"` (16), `"shivangsrivastav"` (14), `"apasharma"` (11), `"spratapsingh"` (6), `"gsharma9"` (6), `"nmall6a"` (4), `"testuser"` (2), `"nmalla3"` (2), `"pperina"` (2), `"araykar"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"gyejju"` (1) |
| `campaigns.[].channels` | 150 | `array` (150) | array lengths: `1` (68), `2` (82) |
| `campaigns.[].channels.[]` | 232 | `integer` (232) | `1002` (137), `1001` (95) |
| `campaigns.[].countries` | 150 | `array` (150) | array lengths: `1` (102), `2` (17), `3` (19), `4` (1), `5` (6), `205` (5) |
| `campaigns.[].countries.[]` | 1252 | `string` (1252) | 205 unique; examples: `"US"` (133), `"CA"` (40), `"AS"` (31), `"AU"` (22), `"GB"` (17) |
| `campaigns.[].created_by` | 150 | `string` (150) | `"praghuvanshi"` (86), `"hukaur"` (16), `"samlnu"` (15), `"apasharma"` (9), `"shivangsrivastav"` (9), `"spratapsingh"` (4), `"gsharma9"` (4), `"testuser"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"pujatav"` (1), `"pperina"` (1), `"araykar"` (1) |
| `campaigns.[].delivery_config` | 150 | `object` (150) | object |
| `campaigns.[].delivery_config.client_service_name` | 8 | `string` (8) | `"testserv"` (2), `"Test"` (2), `"commsapigatewayserv"` (1), `"asdasdhj"` (1), `"njknjnjn"` (1), `"mjnjnknjknkjnjk"` (1) |
| `campaigns.[].delivery_config.device_filter_rule` | 18 | `object` (18) | object |
| `campaigns.[].delivery_config.device_filter_rule.android_app_version` | 18 | `object` (18) | object |
| `campaigns.[].delivery_config.device_filter_rule.android_app_version.app_version_value` | 18 | `string` (18) | `"9.0.0"` (10), `"8.65.0"` (5), `"9.0.1"` (2), `"9.0.8"` (1) |
| `campaigns.[].delivery_config.device_filter_rule.android_app_version.operator` | 18 | `string` (18) | `"GREATER_THAN_OR_EQUAL"` (18) |
| `campaigns.[].delivery_config.device_filter_rule.device_os` | 18 | `string` (18) | `"ALL"` (14), `"ANDROID"` (4) |
| `campaigns.[].delivery_config.device_filter_rule.ios_app_version` | 14 | `object` (14) | object |
| `campaigns.[].delivery_config.device_filter_rule.ios_app_version.app_version_value` | 14 | `string` (14) | `"9.0.0"` (9), `"8.65.0"` (5) |
| `campaigns.[].delivery_config.device_filter_rule.ios_app_version.operator` | 14 | `string` (14) | `"GREATER_THAN_OR_EQUAL"` (13), `"EQUAL"` (1) |
| `campaigns.[].delivery_config.experiment_config` | 19 | `object` (19) | object |
| `campaigns.[].delivery_config.experiment_config.eligible_treatments` | 18 | `array` (18) | array lengths: `1` (6), `2` (8), `3` (4) |
| `campaigns.[].delivery_config.experiment_config.eligible_treatments.[]` | 34 | `string` (34) | `"Control"` (9), `"Test"` (6), `"CommsTeam"` (5), `"treatment_control"` (3), `"treatment_variant_a"` (3), `"treatment_variant_b"` (3), `"Power Users"` (2), `"General Users"` (2), `""` (1) |
| `campaigns.[].delivery_config.experiment_config.experiment_name` | 18 | `string` (18) | `"comms_hub_live_test"` (5), `"comms_config_store"` (5), `"spring_sale_exp_v1"` (3), `"money_received_test_sp"` (2), `"bulk_audit"` (2), `"abc1"` (1) |
| `campaigns.[].delivery_config.omni_type` | 50 | `string` (50) | `"TYPE_1"` (50) |
| `campaigns.[].delivery_config.schedule` | 26 | `object` (26) | object |
| `campaigns.[].delivery_config.schedule.end_date_time` | 26 | `string` (26) | `"2026-04-30T23:59"` (8), `"2026-05-26T10:47"` (3), `"2026-06-30T12:00"` (2), `"2026-05-31T10:58"` (2), `"2030-12-31T23:59"` (2), `"2026-07-03T11:41"` (1), `"2026-06-30T17:38"` (1), `"2026-05-28T10:18"` (1), `"2026-06-16T23:58"` (1), `"2026-05-16T14:14"` (1), `"2026-06-19T11:14"` (1), `"2030-04-30T23:59"` (1), `"2026-05-25T09:45"` (1), `"2026-05-28T15:45"` (1) |
| `campaigns.[].delivery_config.schedule.start_date_time` | 26 | `string` (26) | `"2026-04-01T09:00"` (8), `"2026-05-15T10:47"` (3), `"2026-06-10T12:00"` (2), `"2026-05-18T10:57"` (2), `"2030-06-01T09:00"` (2), `"2026-05-18T11:46"` (1), `"2026-06-10T15:33"` (1), `"2026-05-20T10:18"` (1), `"2026-06-03T23:58"` (1), `"2026-05-15T15:00"` (1), `"2026-06-02T11:19"` (1), `"2030-04-01T09:00"` (1), `"2026-05-23T14:45"` (1), `"2026-05-22T15:56"` (1) |
| `campaigns.[].delivery_config.schedule.timezone` | 26 | `string` (26) | `"America/Los_Angeles"` (12), `"Asia/Calcutta"` (7), `"Africa/Banjul"` (3), `"Africa/Abidjan"` (2), `"America/Anguilla"` (1), `"Africa/Addis_Ababa"` (1) |
| `campaigns.[].delivery_config.target_config` | 39 | `object` (39) | object |
| `campaigns.[].delivery_config.target_config.bq_table_name` | 17 | `string` (17) | `"project.dataset.name"` (6), `"pypl-bods.prd_pzn_comms_common.generic_bulk_elmo_data"` (1), `"test.ts.f"` (1), `"tt.tt.ttnn"` (1), `"dev52-test-apps-bulk-comms.dev_pzn_comms_common.custom_bq_table_bulk_pn_qa"` (1), `"pypl-bods.prd_pzn_comms_common.comms_lta_prod_test_data"` (1), `"test.t.t"` (1), `"testproject.testdataset.testtable_name"` (1), `"true.ts.r"` (1), `"t.t.y"` (1), `"test.project.test"` (1), `"jkj.kj.jkl"` (1) |
| `campaigns.[].delivery_config.target_config.dynamic_segment` | 20 | `object` (20) | object |
| `campaigns.[].delivery_config.target_config.dynamic_segment.between_groups_operator` | 20 | `string` (20) | `"OR"` (20) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups` | 20 | `array` (20) | array lengths: `1` (20) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[]` | 20 | `object` (20) | object |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].exclude_segments` | 9 | `array` (9) | array lengths: `0` (2), `1` (7) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].exclude_segments.[]` | 7 | `object` (7) | object |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].exclude_segments.[].segment_code` | 7 | `string` (7) | `"OPT_OUT_USERS"` (6), `"0.5Back_Debit_Card_Eligibility"` (1) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].exclude_segments.[].segment_id` | 7 | `string` (7) | `"seg_003"` (6), `"DS-7306801429721457076"` (1) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].include_segments` | 20 | `array` (20) | array lengths: `1` (11), `2` (9) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].include_segments.[]` | 29 | `object` (29) | object |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].include_segments.[].segment_code` | 27 | `string` (27) | `"HIGH_BALANCE_USERS"` (8), `"ACTIVE_USERS"` (6), `"hukaur_test_ds"` (5), `"br_cip_InReview_consumer"` (3), `"br_cip_hardDeclined_consumer"` (2), `"1099DA_2025_Biz"` (2), `"0.5Back_Debit_Card_Eligibility"` (1) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].include_segments.[].segment_id` | 29 | `string` (29) | `"seg_001"` (10), `"seg_002"` (6), `"DS-7532436059975491542"` (5), `"DS-7639808702465844574"` (3), `"DS-7639810314295137554"` (2), `"DS-7574376819299418380"` (2), `"DS-7306801429721457076"` (1) |
| `campaigns.[].delivery_config.target_config.dynamic_segment.groups.[].within_group_operator` | 20 | `string` (20) | `"AND"` (20) |
| `campaigns.[].delivery_config.target_type` | 39 | `string` (39) | `"DYNAMIC_SEGMENT"` (20), `"CUSTOM_TABLE"` (17), `"ALL_USERS"` (2) |
| `campaigns.[].delivery_type` | 150 | `string` (150) | `"API_BASED"` (126), `"SCHEDULED_BULK"` (22), `"NON_TRIGGERED"` (2) |
| `campaigns.[].description` | 114 | `string` (114) | 88 unique; examples: `"This is a test cmapaign"` (6), `"mgaklnagklnagmkm"` (5), `"25May-NC25May-NC25May-NC25May-NC25May-NC"` (3), `"omni channel added Push + Non Transactional"` (3), `"Omni Testing 26th may ..akngjknagj"` (3) |
| `campaigns.[].owners` | 150 | `array` (150) | array lengths: `1` (92), `2` (40), `3` (17), `4` (1) |
| `campaigns.[].owners.[]` | 227 | `string` (227) | 21 unique; examples: `"praghuvanshi"` (108), `"hukaur"` (33), `"shivangsrivastav"` (22), `"samlnu"` (20), `"apasharma"` (9) |
| `campaigns.[].status` | 150 | `string` (150) | `"DRAFT"` (72), `"SUBMITTED"` (35), `"PUBLISHED"` (33), `"APPROVED"` (7), `"ARCHIVED"` (2), `"APPROVAL_REQUESTED"` (1) |
| `campaigns.[].team_dls` | 148 | `array` (148) | array lengths: `1` (140), `2` (8) |
| `campaigns.[].team_dls.[]` | 156 | `string` (156) | 66 unique; examples: `"test@paypal.com"` (14), `"sam@paypal.com"` (11), `"comms-decisioning-dev@paypal.com"` (8), `"marketing-team@paypal.com"` (8), `"communications-team@paypal.com"` (8) |
| `campaigns.[].tenant_id` | 150 | `integer` (150) | `101` (150) |
| `campaigns.[].tenant_name` | 150 | `string` (150) | `"PAYPAL"` (150) |
| `campaigns.[].time_created_ms` | 150 | `integer` (150) | 150 unique; examples: `1779441707756` (1), `1780550283629` (1), `1779084698314` (1), `1779451567425` (1), `1779428491880` (1) |
| `campaigns.[].time_updated_ms` | 150 | `integer` (150) | 150 unique; examples: `1779441846767` (1), `1780912693983` (1), `1779167699660` (1), `1779451987965` (1), `1779431143256` (1) |
| `campaigns.[].updated_by` | 150 | `string` (150) | `"praghuvanshi"` (84), `"samlnu"` (15), `"hukaur"` (14), `"apasharma"` (9), `"shivangsrivastav"` (9), `"spratapsingh"` (4), `"gsharma9"` (4), `"SCHEDULER"` (3), `"testuser"` (2), `"savutukuri"` (1), `"mukapoor"` (1), `"gyejju"` (1), `"nmalla3"` (1), `"pperina"` (1), `"araykar"` (1) |
| `campaigns.[].version` | 150 | `integer` (150) | `1` (126), `2` (21), `3` (2), `4` (1) |

## Structured Outputs Drafting Notes

- Use `additionalProperties: false` at each object level only after deciding whether QA-only custom keys such as `custom_view.afaf`, `custom_view.ssb`, and placeholder URL fields should be excluded.
- Treat IDs, names, audit users, timestamps, legal review IDs, BQ table names, localized text, deep links, image URLs, and rule attributes as strings rather than enums.
- Good enum candidates from the sample: campaign `status`, `delivery_type`, `campaign_product`, `campaign_action`, channel `channel_id`/`channel_name`, channel rule `type`, `preference`, `priority`, `section`, `freq_period`, `expiry_duration.unit`, `target_type`, `device_os`, comparison operators, and rule `data_type`.
- Use conditional schema branches where possible: `delivery_config.target_type` controls `target_config`; `channel_id` controls whether push-only fields like `preference`/`type` or notification-center fields like `section`/`expiry_duration` are expected.
- For push notification configuration output, the minimal human-authored surface likely centers on `campaign_product`, `campaign_action`, `countries`, `delivery_type`, `delivery_config`, `channels`, `channel_rules`, `content_payload`, `content_rules`, and legal review fields. IDs and audit timestamps should generally be generated downstream, not by the model.
