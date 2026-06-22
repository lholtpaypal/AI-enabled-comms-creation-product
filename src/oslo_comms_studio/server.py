from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import UTC, datetime
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import quote, urlparse

import requests
import urllib3

from oslo_comms_studio.app import (
    COSMOS_LLM_API_KEY_ENV,
    COSMOS_LLM_BASE_URL,
    COSMOS_LLM_MAX_TOKENS,
    COSMOS_LLM_MODEL,
    DEEPLINK_CATALOG_DATA_URL,
    DEEPLINK_CATALOG_URL,
    DEFAULT_INTENT,
    DYNSEG_BASE_URL,
    PROJECT_ROOT,
    AudienceOption,
    CopyDraft,
    CosmosLlmError,
    DeeplinkCatalogError,
    DeeplinkOption,
    RpsApiError,
    cosmos_api_key,
    generate_copy,
    generate_copy_variants,
    get_dynamic_segment,
    search_audience_options,
    search_deeplink_options,
)

DEMO_SERVER_VERSION = "transcript-demo-v18"
AGENTIC_CAMPAIGN_PATH = PROJECT_ROOT / "resources" / "agentic_comms_test.json"
REFERENCE_CAMPAIGN_PATH = AGENTIC_CAMPAIGN_PATH
CAMPAIGN_MANAGEMENT_BASE_URL = os.getenv(
    "CAMPAIGN_MANAGEMENT_BASE_URL",
    "https://te-campaign-management-3.qa.paypal.com:16223/v1/communications/campaign",
).rstrip("/")
CAMPAIGN_MANAGEMENT_TIMEOUT_SECONDS = float(
    os.getenv("CAMPAIGN_MANAGEMENT_TIMEOUT_SECONDS", "45")
)
CAMPAIGN_MANAGEMENT_USER_DETAILS = os.getenv(
    "CAMPAIGN_MANAGEMENT_USER_DETAILS",
    json.dumps(
        {"LOGGED_IN_USER": "lholt", "USER_ROLES": ["PP_SSO_COMMS_ADMIN"]},
        separators=(",", ":"),
    ),
)
LAST_WORKFLOW_RESPONSE: dict[str, Any] | None = None
PAYPAL_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 72">
  <rect width="64" height="72" rx="4" fill="#17214a"/>
  <path d="M18 8h22c9.8 0 16.2 5.6 14.5 15.1-1.7 9.9-8.8 15-19.6 15H25.8l-4 21.9H8.2L18 8Z" fill="#f3f6fb"/>
  <path d="M25.3 26.1h19.5c8.5 0 13.3 5.2 11.8 13.4-1.6 9.3-8.5 14.6-18.5 14.6H30l-2.5 13.8H14.4l6.3-35.1c.6-3.3 2.2-6.7 4.6-6.7Z" fill="#8fb8e8"/>
  <path d="M27.4 26.1h15.9c4.9 0 8 2.1 9.4 5.6-2.8 4-7.7 6.3-14.6 6.3h-9.3L25.3 57h-9.4l4.8-26.6c.6-3.2 2.1-4.3 6.7-4.3Z" fill="#2f77c8"/>
</svg>
"""
PAYPAL_LOGO_DATA_URI = f"data:image/svg+xml,{quote(PAYPAL_LOGO_SVG)}"

INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Oslo Comms Studio</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f6f8;
      --panel: #ffffff;
      --ink: #111318;
      --muted: #5f6875;
      --line: #d8dee7;
      --soft: #f8fafc;
      --accent: #0070e0;
      --accent-dark: #003087;
      --success: #0a7a4b;
      --warning: #996000;
      --danger: #b42318;
      --shadow: 0 12px 36px rgba(22, 30, 46, 0.07);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button,
    input,
    textarea {
      font: inherit;
    }

    .shell {
      width: min(1340px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 44px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .mark {
      width: 30px;
      height: 30px;
      border-radius: 8px;
      background: var(--ink);
      position: relative;
      flex: 0 0 auto;
    }

    .mark::after {
      content: "";
      position: absolute;
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #5fd3f3;
      top: 10px;
      left: 10px;
    }

    h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.1;
      letter-spacing: 0;
      white-space: nowrap;
    }

    .health {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--panel);
      padding: 6px 11px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--warning);
    }

    .dot.ready {
      background: var(--success);
    }

    .demo-layout {
      display: grid;
      grid-template-columns: minmax(620px, 1fr) 382px;
      gap: 18px;
      align-items: start;
    }

    .intro-strip {
      display: grid;
      gap: 10px;
      margin-bottom: 18px;
      border: 1px solid #b9d8ff;
      border-radius: 8px;
      background: #eef6ff;
      padding: 16px;
    }

    .intro-strip h2 {
      margin: 0;
      font-size: 18px;
      line-height: 1.25;
      letter-spacing: 0;
    }

    .intro-strip p {
      max-width: 980px;
      margin: 0;
      color: #344054;
      font-size: 14px;
      line-height: 1.5;
    }

    .intro-strip ol {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin: 2px 0 0;
      padding: 0;
      list-style: none;
      color: #344054;
      font-size: 13px;
      line-height: 1.4;
    }

    .intro-strip li {
      border: 1px solid #c8ddf8;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.56);
      padding: 9px 10px;
    }

    .intro-strip li strong {
      display: block;
      margin-bottom: 2px;
      color: var(--ink);
      font-size: 13px;
    }

    .workflow {
      display: grid;
      gap: 14px;
      min-width: 0;
    }

    .demo-layout.guided-start {
      grid-template-columns: minmax(0, 820px);
      justify-content: center;
    }

    .guide-card {
      display: grid;
      gap: 6px;
      border: 1px solid #b9d8ff;
      border-radius: 8px;
      background: #eef6ff;
      padding: 14px 16px;
      color: #344054;
      font-size: 14px;
      line-height: 1.45;
    }

    .guide-card strong {
      color: var(--ink);
      font-size: 16px;
      line-height: 1.25;
    }

    .guide-step {
      color: var(--accent-dark);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .support-grid,
    .audience-stack {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      align-items: start;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid var(--line);
      padding: 14px 16px;
    }

    .panel-title {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 0;
      font-size: 15px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .step-number {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 999px;
      background: var(--ink);
      color: #fff;
      font-size: 12px;
      font-weight: 800;
    }

    .panel-body {
      padding: 16px;
    }

    .section-help {
      margin: 0 0 10px;
      color: #344054;
      font-size: 13px;
      line-height: 1.4;
    }

    .section-help strong {
      color: var(--ink);
    }

    .field-help,
    .small-note {
      margin: -2px 0 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .example-list {
      margin: 10px 0 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--soft);
      color: #344054;
      font-size: 12px;
      line-height: 1.45;
    }

    .example-list summary {
      color: var(--ink);
      cursor: pointer;
      font-weight: 750;
    }

    .example-list summary:focus-visible {
      border-radius: 4px;
      outline: 3px solid rgba(0, 112, 224, 0.16);
    }

    .example-list strong {
      color: var(--ink);
    }

    .example-list ul {
      margin: 8px 0 0;
      padding-left: 18px;
    }

    .example-list li + li {
      margin-top: 4px;
    }

    label {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
    }

    .field-tag {
      border-radius: 999px;
      background: #eef1f4;
      color: #596373;
      padding: 2px 6px;
      font-size: 10px;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .help-tip {
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex: 0 0 auto;
      width: 18px;
      height: 18px;
      border: 1px solid #aeb8c5;
      border-radius: 999px;
      background: #fff;
      color: #475467;
      cursor: help;
      font-size: 11px;
      font-weight: 800;
      line-height: 1;
    }

    .help-tip::after {
      content: attr(data-tooltip);
      position: absolute;
      left: 50%;
      bottom: calc(100% + 9px);
      z-index: 20;
      width: max-content;
      max-width: min(320px, calc(100vw - 40px));
      border-radius: 8px;
      background: #101828;
      color: #fff;
      padding: 9px 10px;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.22);
      font-size: 12px;
      font-weight: 500;
      line-height: 1.4;
      opacity: 0;
      pointer-events: none;
      transform: translate(-50%, 4px);
      transition: opacity 0.12s ease, transform 0.12s ease;
      white-space: normal;
    }

    .help-tip::before {
      content: "";
      position: absolute;
      left: 50%;
      bottom: calc(100% + 3px);
      z-index: 21;
      border: 6px solid transparent;
      border-top-color: #101828;
      opacity: 0;
      pointer-events: none;
      transform: translate(-50%, 4px);
      transition: opacity 0.12s ease, transform 0.12s ease;
    }

    .help-tip:hover::after,
    .help-tip:hover::before,
    .help-tip:focus-visible::after,
    .help-tip:focus-visible::before {
      opacity: 1;
      transform: translate(-50%, 0);
    }

    .help-tip:focus-visible {
      outline: 3px solid rgba(0, 112, 224, 0.16);
      outline-offset: 2px;
    }

    textarea,
    input {
      width: 100%;
      border: 1px solid #c8d0da;
      border-radius: 8px;
      color: var(--ink);
      background: #fbfcfd;
    }

    textarea {
      min-height: 142px;
      resize: vertical;
      padding: 12px;
      line-height: 1.45;
    }

    .json-output {
      min-height: 300px;
      margin-top: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      line-height: 1.45;
      white-space: pre;
    }

    input {
      min-height: 42px;
      padding: 0 12px;
    }

    textarea:focus,
    input:focus {
      border-color: var(--accent);
      outline: 3px solid rgba(0, 112, 224, 0.16);
    }

    .copy-fields {
      display: grid;
      gap: 12px;
    }

    .copy-title {
      font-weight: 750;
    }

    .copy-body {
      min-height: 112px;
    }

    .actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 12px;
      flex-wrap: wrap;
    }

    .button-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .package-actions {
      justify-content: flex-start;
    }

    .primary,
    .secondary,
    .suggestion {
      border-radius: 8px;
      cursor: pointer;
      font-weight: 750;
    }

    .primary,
    .secondary {
      min-height: 40px;
      padding: 0 15px;
    }

    .primary,
    .secondary,
    .choice-button.yes {
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
    }

    .primary:hover:not(:disabled),
    .secondary:hover:not(:disabled),
    .choice-button.yes:hover:not(:disabled) {
      border-color: var(--accent-dark);
      background: var(--accent-dark);
    }

    .choice-button {
      border: 1px solid #b9c3d0;
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      min-height: 36px;
      padding: 0 14px;
      cursor: pointer;
      font-weight: 750;
    }

    .primary:disabled,
    .secondary:disabled,
    .suggestion:disabled,
    .choice-button:disabled {
      cursor: not-allowed;
      opacity: 0.62;
    }

    .status {
      min-height: 20px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
      flex: 1 1 260px;
    }

    .badge {
      border-radius: 999px;
      background: #eef1f4;
      color: #4c5562;
      padding: 4px 8px;
      font-size: 12px;
      white-space: nowrap;
    }

    .badge.ok {
      background: #e6f4ee;
      color: var(--success);
    }

    .badge.error {
      background: #fdeceb;
      color: var(--danger);
    }

    .badge.warn {
      background: #fff3d6;
      color: var(--warning);
    }

    .split {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      align-items: start;
    }

    .details-box {
      min-height: 190px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--soft);
      padding: 12px;
    }

    .details-title {
      margin: 0 0 8px;
      font-size: 16px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .details-description {
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .fields {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
    }

    .field {
      border-top: 1px solid var(--line);
      padding-top: 8px;
      min-width: 0;
    }

    .field label {
      margin: 0 0 4px;
      color: #697383;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .field div {
      color: var(--ink);
      font-size: 13px;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
    }

    .suggestions {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .suggestion {
      display: grid;
      gap: 7px;
      width: 100%;
      min-height: 136px;
      border: 1px solid #cdd5df;
      background: #fff;
      color: var(--ink);
      padding: 12px;
      text-align: left;
    }

    .suggestion:hover {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(0, 112, 224, 0.12);
    }

    .suggestion.selected {
      border-color: var(--accent);
      background: #eef6ff;
      box-shadow: 0 0 0 3px rgba(0, 112, 224, 0.1);
    }

    .suggestion strong {
      font-size: 14px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .suggestion span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .suggestion code {
      color: #1d2939;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      overflow-wrap: anywhere;
      white-space: normal;
    }

    .deeplink-choice {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .empty,
    .error-box {
      border-radius: 8px;
      padding: 14px;
      font-size: 14px;
      line-height: 1.45;
    }

    .empty {
      border: 1px dashed #c5ccd6;
      color: var(--muted);
      text-align: center;
    }

    .error-box {
      border: 1px solid #f2bbb6;
      background: #fff7f6;
      color: var(--danger);
    }

    .phone-panel {
      position: sticky;
      top: 18px;
      display: grid;
      gap: 10px;
      justify-items: center;
    }

    .preview-note {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 12px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .preview-note strong {
      display: block;
      margin-bottom: 3px;
      color: var(--ink);
      font-size: 13px;
    }

    .phone-shell {
      width: 376px;
      height: 812px;
      border-radius: 40px;
      background: #000;
      padding: 8px;
      box-shadow: 0 20px 60px rgba(15, 23, 42, 0.24);
    }

    .phone-screen {
      position: relative;
      width: 100%;
      height: 100%;
      overflow: hidden;
      border-radius: 34px;
      background:
        radial-gradient(circle at 50% 58%, rgba(30, 148, 217, 0.46) 0 18%, transparent 33%),
        radial-gradient(circle at 48% 58%, rgba(33, 94, 141, 0.92) 0 26%, rgba(13, 36, 65, 0.95) 35%, transparent 36%),
        #000;
      color: #f7f7f7;
      isolation: isolate;
    }

    .phone-screen::before {
      content: "";
      position: absolute;
      left: 22px;
      right: 22px;
      top: 284px;
      height: 360px;
      border-radius: 50%;
      background:
        radial-gradient(circle at 56% 34%, rgba(255, 255, 255, 0.72), transparent 9%),
        radial-gradient(circle at 54% 42%, rgba(227, 213, 138, 0.85), transparent 16%),
        radial-gradient(circle at 61% 46%, rgba(53, 143, 83, 0.9), transparent 18%),
        radial-gradient(circle at 37% 42%, rgba(223, 230, 230, 0.56), transparent 20%),
        radial-gradient(circle at 45% 55%, rgba(48, 126, 189, 0.95), rgba(22, 87, 150, 0.88) 42%, rgba(7, 35, 82, 0.92) 68%, rgba(6, 20, 44, 0.1) 70%);
      filter: saturate(1.1);
      box-shadow: 0 0 32px rgba(82, 185, 255, 0.65);
      z-index: 0;
    }

    .phone-screen::after {
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 12% 37%, rgba(255, 255, 255, 0.22), transparent 1px),
        radial-gradient(circle at 93% 72%, rgba(255, 255, 255, 0.24), transparent 1px),
        radial-gradient(circle at 78% 31%, rgba(255, 255, 255, 0.16), transparent 1px);
      pointer-events: none;
    }

    .phone-status {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 18px 0;
      color: #f8f8f8;
      font-size: 13px;
      letter-spacing: 0;
    }

    .phone-indicators {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: #fff;
    }

    .signal {
      display: inline-flex;
      align-items: end;
      gap: 2px;
      height: 12px;
    }

    .signal span {
      display: block;
      width: 3px;
      border-radius: 2px;
      background: #fff;
    }

    .signal span:nth-child(1) { height: 4px; }
    .signal span:nth-child(2) { height: 7px; }
    .signal span:nth-child(3) { height: 10px; }

    .battery {
      width: 24px;
      height: 12px;
      border: 1.5px solid #fff;
      border-radius: 4px;
      position: relative;
    }

    .battery::before {
      content: "";
      position: absolute;
      top: 2px;
      left: 2px;
      width: 16px;
      height: 6px;
      border-radius: 2px;
      background: #fff;
    }

    .battery::after {
      content: "";
      position: absolute;
      top: 3px;
      right: -4px;
      width: 2px;
      height: 5px;
      border-radius: 0 2px 2px 0;
      background: #fff;
    }

    .lock-date {
      margin-top: 52px;
      text-align: center;
      font-size: 21px;
      font-weight: 650;
    }

    .lock-time {
      text-align: center;
      font-size: 94px;
      line-height: 0.98;
      font-weight: 780;
      letter-spacing: 0;
      color: rgba(255, 255, 255, 0.92);
    }

    .lock-widgets {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 28px;
      padding: 18px 28px 0;
      font-size: 14px;
      line-height: 1.25;
    }

    .lock-widgets strong {
      display: block;
      font-size: 15px;
      line-height: 1.2;
    }

    .lock-widgets span {
      color: rgba(255, 255, 255, 0.86);
    }

    .notification {
      position: absolute;
      left: 10px;
      right: 10px;
      bottom: 106px;
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
      min-height: 64px;
      border-radius: 18px;
      background: rgba(218, 218, 218, 0.84);
      color: #0b0b0c;
      padding: 10px 12px;
      backdrop-filter: blur(16px);
    }

    .paypal-app-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: #17214a url("__PAYPAL_LOGO_URI__") center / cover no-repeat;
      box-shadow: 0 1px 1px rgba(0, 0, 0, 0.18);
      font-size: 0;
      overflow: hidden;
    }

    .notification-title {
      font-size: 14px;
      font-weight: 700;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }

    .notification-body {
      margin-top: 3px;
      font-size: 13px;
      line-height: 1.25;
      color: rgba(0, 0, 0, 0.84);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .notification-now {
      color: rgba(0, 0, 0, 0.54);
      font-size: 12px;
      white-space: nowrap;
    }

    .phone-bottom {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 16px;
      display: grid;
      justify-items: center;
      gap: 10px;
      color: rgba(255, 255, 255, 0.62);
      font-size: 14px;
    }

    .phone-actions {
      width: 100%;
      display: flex;
      justify-content: space-between;
      padding: 0 58px;
    }

    .phone-action {
      width: 46px;
      height: 46px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.12);
      display: grid;
      place-items: center;
      color: #fff;
      font-size: 18px;
      font-weight: 800;
    }

    .home-indicator {
      width: 134px;
      height: 5px;
      border-radius: 999px;
      background: #fff;
    }

    .variant-panel {
      margin-top: 14px;
    }

    .variant-question {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }

    .variant-question strong {
      font-size: 15px;
      line-height: 1.3;
    }

    .variant-question p {
      max-width: 780px;
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .variant-row {
      display: flex;
      justify-content: center;
      gap: 14px;
      margin-top: 16px;
      flex-wrap: nowrap;
      overflow-x: auto;
      padding-bottom: 2px;
    }

    .variant-card {
      flex: 0 0 300px;
    }

    .standalone-notification {
      display: grid;
      grid-template-columns: 38px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
      min-height: 72px;
      border: 1px solid rgba(15, 23, 42, 0.12);
      border-radius: 18px;
      background: rgba(235, 236, 239, 0.92);
      color: #0b0b0c;
      padding: 10px 12px;
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    }

    .variant-label {
      margin: 0 0 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 750;
      text-align: center;
    }

    @media (max-width: 1080px) {
      .demo-layout {
        grid-template-columns: 1fr;
      }

      .phone-panel {
        position: static;
      }
    }

    @media (max-width: 820px) {
      .support-grid {
        grid-template-columns: 1fr;
      }

      .intro-strip ol {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 560px) {
      .shell {
        width: min(100vw - 20px, 980px);
        padding-top: 16px;
      }

      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }

      h1 {
        white-space: normal;
      }

      .fields {
        grid-template-columns: 1fr;
      }

      .phone-shell {
        width: min(376px, calc(100vw - 20px));
        height: 760px;
      }

      .lock-time {
        font-size: 82px;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div class="brand">
        <span class="mark" aria-hidden="true"></span>
        <h1>Oslo Comms Studio</h1>
      </div>
      <div class="health"><span id="healthDot" class="dot"></span><span id="healthText">Checking local config</span></div>
    </header>

    <section class="intro-strip" aria-label="How to use this page">
      <h2>
        Create a push notification
        <span class="help-tip" tabindex="0" aria-label="Page overview help" data-tooltip="The page reveals each next action after you complete each step. Start with campaign context, then move through copy, variants, audience, deeplink, and the upload JSON package.">?</span>
      </h2>
      <p>Start with one plain-English request. The rest of the demo stays hidden until the first copy draft is ready.</p>
    </section>

    <div id="demoLayout" class="demo-layout guided-start">
      <div class="workflow">
        <section class="guide-card" aria-live="polite">
          <span id="guideStep" class="guide-step">Step 1 of 4</span>
          <strong id="guideTitle">Provide the context</strong>
          <span id="guideBody">Tell us who you want to reach, which PayPal product matters, and what you want the customer to do.</span>
        </section>

        <form id="intentForm" class="panel">
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">1</span>
              Context
              <span class="help-tip" tabindex="0" aria-label="Context help" data-tooltip="Describe your campaign in plain English. Include message type, audience, product or feature, and what you want the customer to do. You do not need final copy or an RPS segment ID yet.">?</span>
            </h2>
            <span class="badge" id="modelBadge">Localhost</span>
          </div>
          <div class="panel-body">
            <p class="section-help">Give the content writer enough context to draft the push.</p>
            <label for="intent">
              Campaign context
              <span class="field-tag">Required</span>
              <span class="help-tip" tabindex="0" aria-label="Campaign context field help" data-tooltip="This is the main input. More specific context gives the tool better copy, audience search, deeplink assumptions, and variants.">?</span>
            </label>
            <textarea id="intent" name="intent" spellcheck="true" placeholder="Example: I want to encourage eligible US customers to use PayPal's Buy Now, Pay Later for the first time.">__DEFAULT_INTENT__</textarea>
            <details class="example-list" aria-label="Campaign intent examples">
              <summary>Need examples? Open this.</summary>
              <ul>
                <li>I want to encourage eligible US customers to use PayPal's Buy Now, Pay Later for the first time.</li>
                <li>Create a push notification for eligible US customers who have not enrolled in PayPal Debit Card. Goal: get them to start enrollment.</li>
                <li>Create a push notification nudging users to pay someone from the PayPal app.</li>
              </ul>
            </details>
            <div class="actions">
              <button id="submitButton" class="primary" type="submit">Generate copy</button>
              <span id="workflowStatus" class="status">Waiting for your campaign intent.</span>
            </div>
          </div>
        </form>

        <section id="copyPanel" class="panel" hidden>
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">2</span>
              Copy
              <span class="help-tip" tabindex="0" aria-label="Copy help" data-tooltip="Cosmos drafts the title and body from your intent. Treat your generated text as a starting point. Both fields are editable, and the phone preview updates as you type.">?</span>
            </h2>
            <span id="copyBadge" class="badge">Waiting</span>
          </div>
          <div class="panel-body">
            <p class="section-help">Edit your generated message.</p>
            <div class="copy-fields">
              <div>
                <label for="copyTitle">
                  Push title
                  <span class="field-tag">Editable</span>
                  <span class="help-tip" tabindex="0" aria-label="Push title help" data-tooltip="This is the bold first line customers see. Keep it short, concrete, and easy to understand at a glance.">?</span>
                </label>
                <input id="copyTitle" class="copy-title" type="text" spellcheck="true" placeholder="Generated title appears here. You can type your own.">
              </div>
              <div>
                <label for="copyBody">
                  Push body
                  <span class="field-tag">Editable</span>
                  <span class="help-tip" tabindex="0" aria-label="Push body help" data-tooltip="This is the supporting sentence. Say the customer benefit or next step clearly. Avoid cramming in details that belong in the landing experience.">?</span>
                </label>
                <textarea id="copyBody" class="copy-body" spellcheck="true" placeholder="Generated body copy appears here. You can rewrite it."></textarea>
              </div>
            </div>
            <div class="actions">
              <button id="regenButton" class="secondary" type="button" disabled>Regenerate copy text</button>
              <span id="copyStatus" class="status">Generate copy first, then edit it here.</span>
            </div>
            <div id="variantPanel" class="variant-panel" hidden>
              <div class="variant-question">
                <div>
                  <strong>
                    Add copy variations?
                    <span class="help-tip" tabindex="0" aria-label="Create variants help" data-tooltip="Choose Yes to generate Variant A and Variant B from the current editable title and body. Choose No to keep the current copy as the only version.">?</span>
                  </strong>
                  <p>Variants stay tied to the message copy, so experimentation is handled before audience and deeplink setup.</p>
                </div>
                <div class="button-row">
                  <button id="variantsYes" class="choice-button yes" type="button" disabled>Yes</button>
                  <button id="variantsNo" class="choice-button" type="button" disabled>No</button>
                  <button id="continueAudienceButton" class="secondary" type="button" disabled>Continue to audience</button>
                </div>
              </div>
              <div class="actions">
                <span id="variantsStatus" class="status">Generate copy first. Variants use your editable title and body.</span>
                <span id="variantsBadge" class="badge">Waiting</span>
              </div>
              <div id="variantRow" class="variant-row" hidden></div>
            </div>
          </div>
        </section>

        <div id="audienceStep" class="audience-stack" hidden>
          <section class="panel">
            <div class="panel-header">
              <h2 class="panel-title">
                <span class="step-number">3</span>
                Find audience
                <span class="help-tip" tabindex="0" aria-label="Audience help" data-tooltip="Your audience controls who receives the message. We search RPS Dynamic Segments from your context, then show one suggested segment so you can inspect it.">?</span>
              </h2>
              <span id="rpsBadge" class="badge">Waiting</span>
            </div>
            <div class="panel-body">
              <p class="section-help">Find one RPS Dynamic Segment for the demo, or paste the segment you already want to use.</p>
              <div class="split">
                <div>
                  <label for="segmentId">
                    RPS Segment ID
                    <span class="field-tag">Editable</span>
                    <span class="help-tip" tabindex="0" aria-label="RPS segment ID help" data-tooltip="The recommended segment ID appears here. Paste a different Dynamic Segment ID or code to replace it and refresh the details below.">?</span>
                  </label>
                  <input id="segmentId" type="text" autocomplete="off" placeholder="Paste a Dynamic Segment ID or code">
                  <div class="actions">
                    <button id="findRpsButton" class="secondary" type="button">Find RPS segment</button>
                    <span id="segmentStatus" class="status">Click Find RPS segment to search, or paste a segment ID yourself.</span>
                  </div>
                </div>
                <div>
                  <label>
                    RPS details
                    <span class="field-tag">Read-only</span>
                    <span class="help-tip" tabindex="0" aria-label="RPS details help" data-tooltip="These are facts returned by RPS. Check the code, description, count, status, country, owner, and refresh timing before trusting the audience.">?</span>
                  </label>
                  <div id="segmentDetails" class="details-box">
                    <div class="empty">No segment selected yet. After you run RPS search, this box will explain exactly which RPS segment was found.</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </div>

        <section id="deeplinkPanel" class="panel" hidden>
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">3</span>
              Deeplink
              <span class="help-tip" tabindex="0" aria-label="Deeplink help" data-tooltip="Use your existing deeplink if you already have one. Otherwise we fetch the Oslo deeplink catalog, rank registered app pages against your intent, and return the two most likely destinations.">?</span>
            </h2>
            <span id="deeplinkBadge" class="badge">Waiting</span>
          </div>
          <div class="panel-body">
            <p class="section-help">Choose where your push should send people.</p>
            <div class="deeplink-choice" aria-label="Deeplink source choice">
              <button id="manualDeeplinkButton" class="choice-button" type="button">I have a deeplink</button>
              <button id="searchDeeplinkButton" class="choice-button yes" type="button">Find deeplink</button>
            </div>
            <label for="deeplinkUrl">
              Deeplink URL
              <span class="field-tag">Editable</span>
              <span class="help-tip" tabindex="0" aria-label="Deeplink URL help" data-tooltip="The recommended URL appears here. You can paste your own deeplink or click a catalog candidate to replace it.">?</span>
            </label>
            <input id="deeplinkUrl" type="url" autocomplete="off" placeholder="Catalog recommendation or pasted deeplink appears here">
            <div class="actions">
              <span id="deeplinkStatus" class="status">Paste your own deeplink, or click Find deeplink to search the Oslo catalog.</span>
            </div>
            <div id="deeplinkCandidates" class="suggestions">
              <div class="empty">No deeplink selected yet.</div>
            </div>
          </div>
        </section>

        <section id="packagePanel" class="panel" hidden>
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">4</span>
              Upload JSON
              <span class="help-tip" tabindex="0" aria-label="Upload JSON help" data-tooltip="This builds a demo upload package from the agentic campaign template. The target audience and other campaign settings stay hard-coded; only the push copy and deeplink are replaced.">?</span>
            </h2>
            <span id="packageBadge" class="badge">Waiting</span>
          </div>
          <div class="panel-body">
            <p class="section-help">Build the demo JSON package for PStudio upload.</p>
            <div class="actions">
              <button id="buildPackageButton" class="primary" type="button">Build upload JSON</button>
              <span id="packageStatus" class="status">Waiting for title, body, and deeplink.</span>
            </div>
            <textarea id="packageJson" class="json-output" readonly spellcheck="false" placeholder="The generated campaign JSON appears here."></textarea>
            <div class="actions package-actions">
              <button id="copyPackageButton" class="secondary" type="button" disabled>Copy JSON</button>
              <button id="downloadPackageButton" class="secondary" type="button" disabled>Download JSON</button>
            </div>
          </div>
        </section>

        <section id="createCampaignPanel" class="panel" hidden>
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">4</span>
              Create Campaign
              <span class="help-tip" tabindex="0" aria-label="Create campaign help" data-tooltip="This PATCHes the QA campaign using the agentic_comms_test template. Only the push title, push body, deeplink, and selected RPS segment ID/code are replaced in the request body.">?</span>
            </h2>
            <span id="createCampaignBadge" class="badge">Waiting</span>
          </div>
          <div class="panel-body">
            <p class="section-help">PATCH campaign 9855711573 in QA with the reviewed copy, deeplink, and selected RPS segment.</p>
            <div class="actions">
              <button id="createCampaignButton" class="primary" type="button">Create Campaign</button>
              <span id="createCampaignStatus" class="status">Waiting for generated title, body, deeplink, and selected RPS segment.</span>
            </div>
            <textarea id="createCampaignResult" class="json-output" readonly spellcheck="false" hidden placeholder="The API response appears here."></textarea>
          </div>
        </section>
      </div>

      <aside id="previewPanel" class="phone-panel" aria-label="Push notification preview" hidden>
        <div class="preview-note">
          <strong>
            Live preview
            <span class="help-tip" tabindex="0" aria-label="Live preview help" data-tooltip="This mock phone shows how your current title and body read on a lock screen. It updates immediately when you edit copy.">?</span>
          </strong>
        </div>
        <div class="phone-shell">
          <div class="phone-screen">
            <div class="phone-status">
              <span>r&amp;T Wi‑Fi</span>
              <span class="phone-indicators">
                <span class="signal"><span></span><span></span><span></span></span>
                <span>⌁</span>
                <span class="battery"></span>
              </span>
            </div>
            <div class="lock-date">Thursday, April 11</div>
            <div class="lock-time">9:41</div>
            <div class="lock-widgets">
              <div><strong>☼ 56°</strong><span>Mostly Sunny<br>H:65° L:51°</span></div>
              <div><strong>Thu, Apr 11</strong><span>No events today<br>Your day is clear</span></div>
            </div>
            <div class="notification">
              <div class="paypal-app-icon" aria-hidden="true"></div>
              <div>
                <div id="previewTitle" class="notification-title"></div>
                <div id="previewBody" class="notification-body"></div>
              </div>
              <div class="notification-now">now</div>
            </div>
            <div class="phone-bottom">
              <div class="phone-actions"><span class="phone-action">▾</span><span class="phone-action">⌾</span></div>
              <div>Swipe up to open</div>
              <div class="home-indicator"></div>
            </div>
          </div>
        </div>
      </aside>
    </div>

  </main>

  <script>
    const form = document.querySelector("#intentForm");
    const intent = document.querySelector("#intent");
    const submitButton = document.querySelector("#submitButton");
    const regenButton = document.querySelector("#regenButton");
    const copyTitle = document.querySelector("#copyTitle");
    const copyBody = document.querySelector("#copyBody");
    const demoLayout = document.querySelector("#demoLayout");
    const copyPanel = document.querySelector("#copyPanel");
    const audienceStep = document.querySelector("#audienceStep");
    const deeplinkPanel = document.querySelector("#deeplinkPanel");
    const packagePanel = document.querySelector("#packagePanel");
    const variantPanel = document.querySelector("#variantPanel");
    const previewPanel = document.querySelector("#previewPanel");
    const guideStep = document.querySelector("#guideStep");
    const guideTitle = document.querySelector("#guideTitle");
    const guideBody = document.querySelector("#guideBody");
    const previewTitle = document.querySelector("#previewTitle");
    const previewBody = document.querySelector("#previewBody");
    const segmentId = document.querySelector("#segmentId");
    const segmentDetails = document.querySelector("#segmentDetails");
    const findRpsButton = document.querySelector("#findRpsButton");
    const deeplinkUrl = document.querySelector("#deeplinkUrl");
    const manualDeeplinkButton = document.querySelector("#manualDeeplinkButton");
    const searchDeeplinkButton = document.querySelector("#searchDeeplinkButton");
    const deeplinkCandidates = document.querySelector("#deeplinkCandidates");
    const buildPackageButton = document.querySelector("#buildPackageButton");
    const packageJson = document.querySelector("#packageJson");
    const packageStatus = document.querySelector("#packageStatus");
    const packageBadge = document.querySelector("#packageBadge");
    const copyPackageButton = document.querySelector("#copyPackageButton");
    const downloadPackageButton = document.querySelector("#downloadPackageButton");
    const createCampaignPanel = document.querySelector("#createCampaignPanel");
    const createCampaignButton = document.querySelector("#createCampaignButton");
    const createCampaignStatus = document.querySelector("#createCampaignStatus");
    const createCampaignBadge = document.querySelector("#createCampaignBadge");
    const createCampaignResult = document.querySelector("#createCampaignResult");
    const workflowStatus = document.querySelector("#workflowStatus");
    const copyStatus = document.querySelector("#copyStatus");
    const segmentStatus = document.querySelector("#segmentStatus");
    const deeplinkStatus = document.querySelector("#deeplinkStatus");
    const copyBadge = document.querySelector("#copyBadge");
    const rpsBadge = document.querySelector("#rpsBadge");
    const deeplinkBadge = document.querySelector("#deeplinkBadge");
    const healthDot = document.querySelector("#healthDot");
    const healthText = document.querySelector("#healthText");
    const modelBadge = document.querySelector("#modelBadge");
    const variantsYes = document.querySelector("#variantsYes");
    const variantsNo = document.querySelector("#variantsNo");
    const continueAudienceButton = document.querySelector("#continueAudienceButton");
    const variantsBadge = document.querySelector("#variantsBadge");
    const variantsStatus = document.querySelector("#variantsStatus");
    const variantRow = document.querySelector("#variantRow");

    let activeDeeplinkOptions = [];
    let currentPackage = null;
    let selectedAudienceOption = null;
    let segmentLookupTimer = null;
    let suppressSegmentLookup = false;

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function setBadge(element, text, state = "") {
      element.textContent = text;
      element.className = `badge ${state}`.trim();
    }

    function reveal(element) {
      if (element) element.hidden = false;
    }

    function conceal(element) {
      if (element) element.hidden = true;
    }

    function setGuide(step, title, body) {
      guideStep.textContent = step;
      guideTitle.textContent = title;
      guideBody.textContent = body;
    }

    function focusStep(element) {
      if (!element || element.hidden) return;
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function setWorkflowLoading(isLoading) {
      submitButton.disabled = isLoading;
      regenButton.disabled = isLoading || !intent.value.trim();
      findRpsButton.disabled = isLoading;
      searchDeeplinkButton.disabled = isLoading;
      manualDeeplinkButton.disabled = isLoading;
      workflowStatus.textContent = isLoading
        ? "Working: asking Cosmos to draft the push title and body."
        : "Ready for edits or the next agent step.";
    }

    function updatePreview() {
      previewTitle.textContent = copyTitle.value.trim();
      previewBody.textContent = copyBody.value.trim();
    }

    function applyCopy(copy) {
      copyTitle.value = copy?.title || "";
      copyBody.value = copy?.body || "";
      updatePreview();
    }

    function currentCopy() {
      return {
        title: copyTitle.value.trim(),
        body: copyBody.value.trim()
      };
    }

    function setVariantControlsEnabled(isEnabled) {
      variantsYes.disabled = !isEnabled;
      variantsNo.disabled = !isEnabled;
      continueAudienceButton.disabled = !isEnabled;
    }

    function showAudienceStep() {
      reveal(audienceStep);
      setGuide("Step 3 of 4", "Find audience and deeplink", "Find one RPS segment for the demo, then choose or paste the landing page.");
      focusStep(audienceStep);
    }

    function resetPackage(shouldHide = true) {
      currentPackage = null;
      packageJson.value = "";
      packageStatus.textContent = "Waiting for title, body, and deeplink.";
      setBadge(packageBadge, "Waiting");
      copyPackageButton.disabled = true;
      downloadPackageButton.disabled = true;
      if (shouldHide) {
        conceal(packagePanel);
      }
    }

    function resetCreateCampaign(shouldHide = true) {
      createCampaignResult.value = "";
      createCampaignResult.hidden = true;
      createCampaignStatus.textContent = "Waiting for generated title, body, deeplink, and selected RPS segment.";
      setBadge(createCampaignBadge, "Waiting");
      if (shouldHide) {
        conceal(createCampaignPanel);
      }
    }

    function formatValue(value) {
      if (value === null || value === undefined || value === "") return "Not listed";
      if (Array.isArray(value)) return value.length ? value.join(", ") : "None";
      if (typeof value === "object") return JSON.stringify(value, null, 2);
      return String(value);
    }

    function labelFor(key) {
      return key.replaceAll("_", " ").replace(/\\b\\w/g, (character) => character.toUpperCase());
    }

    function optionRecommendation(option) {
      return option?.recommendation || option || null;
    }

    function selectedSegmentPayload() {
      const recommendation = optionRecommendation(selectedAudienceOption);
      const details = selectedAudienceOption?.details || {};
      const typedValue = segmentId.value.trim();
      const typedLooksLikeId = typedValue.toUpperCase().startsWith("DS-");
      return {
        segment_id: String(recommendation?.segment_id || details.id || (typedLooksLikeId ? typedValue : "")).trim(),
        segment_code: String(recommendation?.code || details.code || (!typedLooksLikeId ? typedValue : "")).trim()
      };
    }

    function renderSegmentDetails(option) {
      const recommendation = optionRecommendation(option);
      if (!recommendation) {
        segmentDetails.innerHTML = '<div class="empty">No segment selected yet. After you run RPS search, this box will explain exactly which RPS segment was found.</div>';
        return;
      }

      const details = option.details || {};
      const priorityKeys = [
        "id",
        "code",
        "description",
        "lifecycle_status",
        "audience_count",
        "country_codes",
        "regions",
        "created_by",
        "co_owners",
        "type",
        "refresh_frequency",
        "last_refresh_time",
        "created_time",
        "updated_time"
      ];
      const keys = [
        ...priorityKeys.filter((key) => Object.prototype.hasOwnProperty.call(details, key)),
        ...Object.keys(details)
          .filter((key) => !priorityKeys.includes(key))
          .sort()
      ];
      const fields = keys.length
        ? keys.map((key) => `
            <div class="field">
              <label>${escapeHtml(labelFor(key))}</label>
              <div>${escapeHtml(formatValue(details[key]))}</div>
            </div>
          `).join("")
        : `
            <div class="field"><label>Segment ID</label><div>${escapeHtml(recommendation.segment_id)}</div></div>
            <div class="field"><label>Status</label><div>${escapeHtml(recommendation.status)}</div></div>
          `;

      segmentDetails.innerHTML = `
        <h3 class="details-title">${escapeHtml(recommendation.code || recommendation.segment_id)}</h3>
        <p class="details-description">${escapeHtml(recommendation.description || "No description returned.")}</p>
        <div class="fields">${fields}</div>
      `;
    }

    function setSelectedAudience(option, shouldUpdateInput = true) {
      const recommendation = optionRecommendation(option);
      if (!recommendation) {
        selectedAudienceOption = null;
        segmentStatus.textContent = "No segment selected. Paste a Dynamic Segment ID or run RPS search.";
        setBadge(rpsBadge, "No match", "warn");
        renderSegmentDetails(null);
        conceal(deeplinkPanel);
        resetPackage();
        resetCreateCampaign();
        return;
      }

      selectedAudienceOption = option;
      if (shouldUpdateInput) {
        suppressSegmentLookup = true;
        segmentId.value = recommendation.segment_id || "";
        queueMicrotask(() => {
          suppressSegmentLookup = false;
        });
      }
      segmentStatus.textContent = recommendation.segment_id
        ? `Done: selected ${recommendation.segment_id}. This field is editable if you want to replace it.`
        : "Done: selected an audience. This field is editable if you want to replace it.";
      setBadge(rpsBadge, "Selected", "ok");
      renderSegmentDetails(option);
      reveal(deeplinkPanel);
      if (deeplinkUrl.value.trim()) {
        reveal(createCampaignPanel);
        resetCreateCampaign(false);
      }
      setGuide("Step 3 of 4", "Choose your landing page", "Paste a deeplink if you already have one, or run the Oslo catalog search to find the best registered app page.");
      focusStep(deeplinkPanel);
    }

    function resetAudienceSearch() {
      selectedAudienceOption = null;
      segmentId.value = "";
      segmentStatus.textContent = "Click Find RPS segment to search, or paste a segment ID yourself.";
      setBadge(rpsBadge, "Waiting");
      renderSegmentDetails(null);
      conceal(deeplinkPanel);
      resetPackage();
      resetCreateCampaign();
    }

    function deeplinkRecommendation(option) {
      return option?.recommendation || option || null;
    }

    function deeplinkOptionList(data) {
      if (Array.isArray(data?.deeplink_options)) return data.deeplink_options;
      return [data?.selected_deeplink, ...(data?.suggested_deeplinks || [])].filter(Boolean);
    }

    function formatDeeplinkParams(params) {
      if (!Array.isArray(params) || !params.length) return "Required params: none";
      return `Required params: ${params.map((param) => param.url_param || param.property || "unnamed").join(", ")}`;
    }

    function setSelectedDeeplink(option, shouldUpdateInput = true) {
      const recommendation = deeplinkRecommendation(option);
      if (!recommendation) {
        deeplinkStatus.textContent = "No deeplink selected. Paste your own URL or search the Oslo catalog.";
        setBadge(deeplinkBadge, "No match", "warn");
        if (shouldUpdateInput) deeplinkUrl.value = "";
        return;
      }

      if (shouldUpdateInput) {
        deeplinkUrl.value = recommendation.url || "";
      }
      deeplinkStatus.textContent = recommendation.url
        ? `Done: selected ${recommendation.path || recommendation.url}. You can edit your URL before handoff.`
        : "Done: selected a catalog destination. Confirm your URL before handoff.";
      setBadge(deeplinkBadge, recommendation.confidence || "Selected", "ok");
      renderDeeplinkOptions(activeDeeplinkOptions, recommendation.path);
      reveal(createCampaignPanel);
      resetCreateCampaign(false);
      reveal(packagePanel);
      resetPackage(false);
      setGuide("Step 4 of 4", "Create the campaign", "PATCH the QA campaign with your reviewed copy, deeplink, and selected RPS segment.");
      focusStep(createCampaignPanel);
    }

    function renderDeeplinkOptions(options, selectedPath = "") {
      activeDeeplinkOptions = options || [];
      if (!activeDeeplinkOptions.length) {
        deeplinkCandidates.innerHTML = '<div class="empty">No catalog candidates yet. Choose Find deeplink when your intent and copy are ready.</div>';
        setBadge(deeplinkBadge, "Waiting");
        return;
      }

      deeplinkCandidates.innerHTML = activeDeeplinkOptions.map((option, index) => {
        const recommendation = deeplinkRecommendation(option);
        const label = index === 0 ? "Recommended destination" : "Alternative destination";
        const selectedClass = recommendation.path === selectedPath ? " selected" : "";
        return `
          <button class="suggestion${selectedClass}" type="button" data-deeplink-index="${index}">
            <strong>${escapeHtml(label)} · ${escapeHtml(recommendation.confidence || "Medium")} confidence</strong>
            <code>${escapeHtml(recommendation.url || "")}</code>
            <span>${escapeHtml(recommendation.path || "No path")} · ${escapeHtml(recommendation.destination || "No destination")} · ${escapeHtml(recommendation.link_type || "Unknown type")}</span>
            <span>${escapeHtml(formatDeeplinkParams(recommendation.required_params))}</span>
            <span>${escapeHtml(recommendation.rationale || "Catalog-backed candidate.")}</span>
          </button>
        `;
      }).join("");
      setBadge(deeplinkBadge, `${activeDeeplinkOptions.length} options`, "ok");
    }

    function resetDeeplinkSearch() {
      activeDeeplinkOptions = [];
      deeplinkUrl.value = "";
      deeplinkStatus.textContent = "Paste your own deeplink, or click Find deeplink to search the Oslo catalog.";
      setBadge(deeplinkBadge, "Waiting");
      deeplinkCandidates.innerHTML = '<div class="empty">No deeplink selected yet.</div>';
      resetPackage();
      resetCreateCampaign();
    }

    function renderError(target, data) {
      const hint = data.hint ? `<br>${escapeHtml(data.hint)}` : "";
      target.innerHTML = `<div class="error-box">${escapeHtml(data.error || "Request failed.")}${hint}</div>`;
    }

    function notificationMarkup(copy, label) {
      return `
        <div class="variant-card">
          <div class="variant-label">${escapeHtml(label)}</div>
          <div class="standalone-notification">
            <div class="paypal-app-icon" aria-hidden="true"></div>
            <div>
              <div class="notification-title">${escapeHtml(copy.title || "")}</div>
              <div class="notification-body">${escapeHtml(copy.body || "")}</div>
            </div>
            <div class="notification-now">now</div>
          </div>
        </div>
      `;
    }

    function renderVariantRow(generatedVariants) {
      const variants = [currentCopy(), ...(generatedVariants || [])];
      const labels = ["Control", "Variant A", "Variant B"];
      variantRow.innerHTML = variants
        .slice(0, 3)
        .map((copy, index) => notificationMarkup(copy, labels[index] || `Variant ${index + 1}`))
        .join("");
      variantRow.hidden = false;
    }

    function clearVariants(message = "No content variations selected.") {
      variantRow.hidden = true;
      variantRow.innerHTML = "";
      variantsStatus.textContent = message;
      setBadge(variantsBadge, "Skipped");
    }

    async function postJson(path, payload) {
      const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) {
        const error = new Error(data.error || "Request failed.");
        error.payload = data;
        throw error;
      }
      return data;
    }

    async function loadHealth() {
      try {
        const response = await fetch("/api/health");
        const data = await response.json();
        modelBadge.textContent = `${data.model || "Localhost"} · ${data.max_tokens || "?"} tokens`;
        if (data.has_api_key) {
          healthDot.classList.add("ready");
          healthText.textContent = data.server_version
            ? `Local config ready · ${data.server_version}`
            : "Local config ready";
        } else {
          healthDot.classList.remove("ready");
          healthText.textContent = "Missing Cosmos key";
        }
      } catch {
        healthText.textContent = "Health check failed";
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const value = intent.value.trim();
      if (!value) {
        workflowStatus.textContent = "Enter your intent first.";
        return;
      }

      setWorkflowLoading(true);
      setBadge(copyBadge, "Calling", "warn");
      copyStatus.textContent = "Working: Cosmos is drafting a title and body from your intent.";

      try {
        const data = await postJson("/api/copy", { intent: value });
        applyCopy(data.copy);
        reveal(copyPanel);
        reveal(variantPanel);
        reveal(previewPanel);
        demoLayout.classList.remove("guided-start");
        workflowStatus.textContent = "Copy generated. Review it, then decide whether to add variants.";
        copyStatus.textContent = "Done: copy generated. Title and body are editable, and the phone preview updates as you type.";
        setBadge(copyBadge, "Generated", "ok");
        setVariantControlsEnabled(true);
        clearVariants("Ready: choose Yes to create variants from your current editable copy.");
        setBadge(variantsBadge, "Ready");
        conceal(audienceStep);
        resetAudienceSearch();
        resetDeeplinkSearch();
        setGuide("Step 2 of 4", "Select your copy", "Edit the title and body, then add variants or continue to audience.");
        focusStep(copyPanel);
      } catch (error) {
        const payload = error.payload || { error: error.message };
        workflowStatus.textContent = payload.error || "Copy generation failed.";
        copyStatus.textContent = payload.error || "Copy generation failed.";
        setBadge(copyBadge, "Error", "error");
      } finally {
        setWorkflowLoading(false);
      }
    });

    regenButton.addEventListener("click", async () => {
      const value = intent.value.trim();
      if (!value) {
        copyStatus.textContent = "Enter your intent first.";
        return;
      }

      regenButton.disabled = true;
      setBadge(copyBadge, "Regenerating", "warn");
      copyStatus.textContent = "Working: asking Cosmos for a fresh title and body using the same intent.";
      try {
        const data = await postJson("/api/copy", { intent: value });
        applyCopy(data.copy);
        reveal(copyPanel);
        reveal(variantPanel);
        reveal(previewPanel);
        demoLayout.classList.remove("guided-start");
        copyStatus.textContent = "Done: copy regenerated. You can still edit the title and body directly.";
        setBadge(copyBadge, "Generated", "ok");
        clearVariants("Copy changed. Choose Yes again when you want variants based on the new copy.");
        setBadge(variantsBadge, "Ready");
        conceal(audienceStep);
        resetAudienceSearch();
        resetDeeplinkSearch();
        setGuide("Step 2 of 4", "Review your revised copy", "Because your copy changed, continue through audience and deeplink again when you are ready.");
        focusStep(copyPanel);
      } catch (error) {
        const payload = error.payload || { error: error.message };
        copyStatus.textContent = payload.error || "Copy regeneration failed.";
        setBadge(copyBadge, "Error", "error");
      } finally {
        regenButton.disabled = false;
      }
    });

    findRpsButton.addEventListener("click", async () => {
      const value = intent.value.trim();
      if (!value) {
        segmentStatus.textContent = "Enter your intent first so RPS has audience context.";
        setBadge(rpsBadge, "Waiting", "warn");
        return;
      }

      findRpsButton.disabled = true;
      segmentStatus.textContent = "Working: RPS is searching Dynamic Segments that match your intended audience.";
      segmentDetails.innerHTML = '<div class="empty">Searching RPS. Details will appear here so you can inspect your selected segment.</div>';
      setBadge(rpsBadge, "Searching", "warn");
      try {
        const data = await postJson("/api/audience", { intent: value });
        setSelectedAudience(data.selected_audience);
      } catch (error) {
        const payload = error.payload || { error: error.message };
        segmentStatus.textContent = payload.error || "RPS search failed.";
        setBadge(rpsBadge, "Error", "error");
        renderError(segmentDetails, payload);
      } finally {
        findRpsButton.disabled = false;
      }
    });

    segmentId.addEventListener("input", () => {
      if (suppressSegmentLookup) return;
      selectedAudienceOption = null;
      resetCreateCampaign(false);
      clearTimeout(segmentLookupTimer);
      segmentLookupTimer = setTimeout(async () => {
        const value = segmentId.value.trim();
        if (!value) {
          setSelectedAudience(null, false);
          return;
        }

        segmentStatus.textContent = "Working: looking up the segment you typed.";
        setBadge(rpsBadge, "Looking up", "warn");
        try {
          const data = await postJson("/api/segment", { segment_id: value });
          setSelectedAudience(data.selected_audience, false);
        } catch (error) {
          const payload = error.payload || { error: error.message };
          segmentStatus.textContent = payload.error || "Segment lookup failed.";
          setBadge(rpsBadge, "Not found", "error");
          renderError(segmentDetails, payload);
        }
      }, 450);
    });

    deeplinkCandidates.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-deeplink-index]");
      if (!button) return;
      const option = activeDeeplinkOptions[Number(button.dataset.deeplinkIndex)];
      setSelectedDeeplink(option);
    });

    manualDeeplinkButton.addEventListener("click", () => {
      deeplinkStatus.textContent = "Paste the deeplink you already have. The field is editable and will be used as entered.";
      setBadge(deeplinkBadge, "Manual");
      setGuide("Step 3 of 4", "Paste your deeplink", "Paste your destination URL. Once the field has a value, the create step will unlock.");
      deeplinkUrl.focus();
    });

    deeplinkUrl.addEventListener("input", () => {
      if (!deeplinkUrl.value.trim()) {
        resetPackage();
        resetCreateCampaign();
        return;
      }
      reveal(createCampaignPanel);
      resetCreateCampaign(false);
      reveal(packagePanel);
      resetPackage(false);
      setBadge(deeplinkBadge, "Manual");
      deeplinkStatus.textContent = "Manual deeplink entered. You can still edit it before handoff.";
      setGuide("Step 4 of 4", "Create the campaign", "PATCH the QA campaign with your reviewed copy, deeplink, and selected RPS segment.");
    });

    searchDeeplinkButton.addEventListener("click", async () => {
      const value = intent.value.trim();
      if (!value) {
        deeplinkStatus.textContent = "Enter your intent first so the catalog search has context.";
        setBadge(deeplinkBadge, "Waiting", "warn");
        return;
      }

      searchDeeplinkButton.disabled = true;
      manualDeeplinkButton.disabled = true;
      deeplinkStatus.textContent = "Working: searching the Oslo deeplink catalog using your current intent and editable copy.";
      deeplinkCandidates.innerHTML = '<div class="empty">Searching the Oslo catalog. The top two landing pages will appear here.</div>';
      setBadge(deeplinkBadge, "Searching", "warn");
      try {
        const data = await postJson("/api/deeplinks", {
          intent: value,
          title: copyTitle.value.trim(),
          body: copyBody.value.trim()
        });
        const deeplinkOptions = deeplinkOptionList(data);
        renderDeeplinkOptions(deeplinkOptions, data.selected_deeplink?.recommendation?.path || "");
        setSelectedDeeplink(data.selected_deeplink);
      } catch (error) {
        const payload = error.payload || { error: error.message };
        deeplinkStatus.textContent = payload.error || "Deeplink catalog search failed.";
        setBadge(deeplinkBadge, "Error", "error");
        renderError(deeplinkCandidates, payload);
      } finally {
        searchDeeplinkButton.disabled = false;
        manualDeeplinkButton.disabled = false;
      }
    });

    variantsYes.addEventListener("click", async () => {
      const value = intent.value.trim();
      const copy = currentCopy();
      if (!value || !copy.title || !copy.body) {
        variantsStatus.textContent = "Generate or enter title and body copy first.";
        setBadge(variantsBadge, "Waiting", "warn");
        return;
      }

      variantsYes.disabled = true;
      variantsNo.disabled = true;
      variantsStatus.textContent = "Working: generating two variants from your current editable title and body.";
      setBadge(variantsBadge, "Generating", "warn");
      try {
        const data = await postJson("/api/variants", {
          intent: value,
          title: copy.title,
          body: copy.body
        });
        renderVariantRow(data.variants || []);
        variantsStatus.textContent = "Done: control copy plus Variant A and Variant B are ready for review.";
        setBadge(variantsBadge, "Generated", "ok");
        showAudienceStep();
      } catch (error) {
        const payload = error.payload || { error: error.message };
        variantsStatus.textContent = payload.error || "Variant generation failed.";
        setBadge(variantsBadge, "Error", "error");
      } finally {
        setVariantControlsEnabled(true);
      }
    });

    variantsNo.addEventListener("click", () => {
      clearVariants();
      showAudienceStep();
    });

    continueAudienceButton.addEventListener("click", () => {
      showAudienceStep();
    });

    buildPackageButton.addEventListener("click", async () => {
      const copy = currentCopy();
      const deeplink = deeplinkUrl.value.trim();
      if (!copy.title || !copy.body || !deeplink) {
        packageStatus.textContent = "Enter title, body, and deeplink before building the JSON package.";
        setBadge(packageBadge, "Waiting", "warn");
        return;
      }

      buildPackageButton.disabled = true;
      packageStatus.textContent = "Working: building the demo upload package from the agentic campaign template.";
      setBadge(packageBadge, "Building", "warn");
      try {
        const data = await postJson("/api/package", {
          intent: intent.value.trim(),
          title: copy.title,
          body: copy.body,
          deeplink: deeplink
        });
        currentPackage = data;
        packageJson.value = JSON.stringify(data.package, null, 2);
        packageStatus.textContent = "Done: title, body, and deeplink were inserted; the rest of the campaign stayed hard-coded for the demo send.";
        setBadge(packageBadge, "Ready", "ok");
        copyPackageButton.disabled = false;
        downloadPackageButton.disabled = false;
      } catch (error) {
        const payload = error.payload || { error: error.message };
        packageStatus.textContent = payload.error || "Package generation failed.";
        setBadge(packageBadge, "Error", "error");
      } finally {
        buildPackageButton.disabled = false;
      }
    });

    createCampaignButton.addEventListener("click", async () => {
      const copy = currentCopy();
      const segment = selectedSegmentPayload();
      const deeplink = deeplinkUrl.value.trim();
      if (!copy.title || !copy.body) {
        createCampaignStatus.textContent = "Enter title and body copy before creating the campaign.";
        setBadge(createCampaignBadge, "Waiting", "warn");
        return;
      }
      if (!deeplink) {
        createCampaignStatus.textContent = "Enter or select a deeplink before creating the campaign.";
        setBadge(createCampaignBadge, "Waiting", "warn");
        return;
      }
      if (!segment.segment_id || !segment.segment_code) {
        createCampaignStatus.textContent = "Select an RPS segment with both segment ID and segment code before creating the campaign.";
        setBadge(createCampaignBadge, "Waiting", "warn");
        return;
      }

      createCampaignButton.disabled = true;
      createCampaignStatus.textContent = "Working: PATCHing campaign 9855711573 in QA.";
      setBadge(createCampaignBadge, "PATCHing", "warn");
      createCampaignResult.hidden = true;
      createCampaignResult.value = "";
      try {
        const data = await postJson("/api/create-campaign", {
          title: copy.title,
          body: copy.body,
          deeplink: deeplink,
          segment_id: segment.segment_id,
          segment_code: segment.segment_code
        });
        createCampaignStatus.textContent = `Done: campaign ${data.campaign_id || "9855711573"} was updated in QA.`;
        setBadge(createCampaignBadge, "Created", "ok");
        createCampaignResult.value = JSON.stringify(data.response || data, null, 2);
        createCampaignResult.hidden = false;
      } catch (error) {
        const payload = error.payload || { error: error.message };
        createCampaignStatus.textContent = payload.error || "Campaign PATCH failed.";
        setBadge(createCampaignBadge, "Error", "error");
        createCampaignResult.value = JSON.stringify(payload, null, 2);
        createCampaignResult.hidden = false;
      } finally {
        createCampaignButton.disabled = false;
      }
    });

    copyPackageButton.addEventListener("click", async () => {
      if (!packageJson.value.trim()) return;
      try {
        await navigator.clipboard.writeText(packageJson.value);
        packageStatus.textContent = "Copied JSON to clipboard.";
      } catch {
        packageStatus.textContent = "Copy failed. Select the JSON text and copy it manually.";
      }
    });

    downloadPackageButton.addEventListener("click", () => {
      if (!packageJson.value.trim()) return;
      const blob = new Blob([packageJson.value], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = currentPackage?.download_filename || "oslo-demo-campaign.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    });

    function handleCopyInput() {
      updatePreview();
      if (!packagePanel.hidden) {
        resetPackage(false);
      }
      if (!createCampaignPanel.hidden) {
        resetCreateCampaign(false);
      }
    }

    copyTitle.addEventListener("input", handleCopyInput);
    copyBody.addEventListener("input", handleCopyInput);

    updatePreview();
    loadHealth();
  </script>
</body>
</html>
"""


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class LocalDemoHandler(BaseHTTPRequestHandler):
    server_version = "OsloCommsStudio/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._send_html(
                INDEX_HTML.replace("__DEFAULT_INTENT__", escape(DEFAULT_INTENT)).replace(
                    "__PAYPAL_LOGO_URI__", PAYPAL_LOGO_DATA_URI
                )
            )
            return
        if path == "/api/health":
            self._send_json(HTTPStatus.OK, health_payload())
            return
        if path == "/api/last-workflow":
            self._send_json(HTTPStatus.OK, last_workflow_payload())
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        if path == "/api/demo":
            self._handle_demo(payload)
            return
        if path == "/api/copy":
            self._handle_copy(payload)
            return
        if path == "/api/audience":
            self._handle_audience(payload)
            return
        if path == "/api/segment":
            self._handle_segment(payload)
            return
        if path == "/api/deeplinks":
            self._handle_deeplinks(payload)
            return
        if path == "/api/variants":
            self._handle_variants(payload)
            return
        if path == "/api/package":
            self._handle_package(payload)
            return
        if path == "/api/create-campaign":
            self._handle_create_campaign(payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def _handle_demo(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        if not intent:
            self._send_json(
                HTTPStatus.BAD_REQUEST, {"error": "Enter your intent before generating copy."}
            )
            return

        try:
            copy = generate_copy(intent)
        except CosmosLlmError as exc:
            error_payload = copy_error_payload(exc)
            record_last_workflow(HTTPStatus.BAD_GATEWAY, intent, error_payload)
            self._send_json(HTTPStatus.BAD_GATEWAY, error_payload)
            return

        copy_payload = copy_response_payload(copy)
        try:
            audience_options = search_audience_options(intent, limit=3)
        except RpsApiError as exc:
            error_payload = {
                "step": "rps",
                "copy": copy_payload,
                "error": str(exc),
                "hint": "Confirm VPN/network access to the QA RPS host, then retry.",
            }
            record_last_workflow(HTTPStatus.BAD_GATEWAY, intent, error_payload)
            self._send_json(HTTPStatus.BAD_GATEWAY, error_payload)
            return

        selected = audience_options[0] if audience_options else None
        suggestions = audience_options[1:]
        selected_payload = audience_option_payload(selected)
        suggestions_payload = [audience_option_payload(option) for option in suggestions]
        try:
            deeplink_options = search_deeplink_options(intent, copy=copy, limit=2)
        except DeeplinkCatalogError as exc:
            error_payload = {
                "step": "deeplink",
                "copy": copy_payload,
                "selected_audience": selected_payload,
                "suggested_audiences": suggestions_payload,
                "error": str(exc),
                "hint": "Confirm VPN/network access to the Oslo hub catalog, then retry the deeplink search.",
            }
            record_last_workflow(HTTPStatus.BAD_GATEWAY, intent, error_payload)
            self._send_json(HTTPStatus.BAD_GATEWAY, error_payload)
            return

        selected_deeplink = deeplink_options[0] if deeplink_options else None
        suggested_deeplinks = deeplink_options[1:]
        response_payload = {
            "intent": intent,
            "copy": copy_payload,
            "selected_audience": selected_payload,
            "suggested_audiences": suggestions_payload,
            "selected_deeplink": deeplink_option_payload(selected_deeplink),
            "suggested_deeplinks": [
                deeplink_option_payload(option) for option in suggested_deeplinks
            ],
            "deeplink_options": [deeplink_option_payload(option) for option in deeplink_options],
            "audience": asdict(selected.recommendation) if selected else None,
            "model": COSMOS_LLM_MODEL,
        }
        record_last_workflow(HTTPStatus.OK, intent, response_payload)
        self._send_json(HTTPStatus.OK, response_payload)

    def _handle_copy(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        if not intent:
            self._send_json(
                HTTPStatus.BAD_REQUEST, {"error": "Enter your intent before generating copy."}
            )
            return

        try:
            copy = generate_copy(intent)
        except CosmosLlmError as exc:
            self._send_json(HTTPStatus.BAD_GATEWAY, copy_error_payload(exc))
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "intent": intent,
                "copy": copy_response_payload(copy),
                "model": COSMOS_LLM_MODEL,
            },
        )

    def _handle_audience(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        if not intent:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Enter your intent before searching for an RPS segment."},
            )
            return

        try:
            audience_options = search_audience_options(intent, limit=3)
        except RpsApiError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "step": "rps",
                    "error": str(exc),
                    "hint": "Confirm VPN/network access to the QA RPS host, then retry.",
                },
            )
            return

        selected = audience_options[0] if audience_options else None
        suggestions = audience_options[1:]
        self._send_json(
            HTTPStatus.OK,
            {
                "intent": intent,
                "selected_audience": audience_option_payload(selected),
                "suggested_audiences": [audience_option_payload(option) for option in suggestions],
                "model": COSMOS_LLM_MODEL,
            },
        )

    def _handle_segment(self, payload: dict[str, Any]) -> None:
        segment_id = str(payload.get("segment_id", "")).strip()
        if not segment_id:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Enter an RPS Dynamic Segment ID."})
            return

        try:
            option = get_dynamic_segment(segment_id)
        except RpsApiError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "step": "rps",
                    "error": str(exc),
                    "hint": "Confirm VPN/network access to the QA RPS host, then retry.",
                },
            )
            return

        if option is None:
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {
                    "step": "rps",
                    "error": f"No Dynamic Segment found for {segment_id}.",
                },
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "selected_audience": audience_option_payload(option),
            },
        )

    def _handle_deeplinks(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).strip()
        if not intent:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Enter your intent first."})
            return

        copy = CopyDraft(title=title, body=body) if title and body else None
        try:
            deeplink_options = search_deeplink_options(intent, copy=copy, limit=2)
        except DeeplinkCatalogError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "step": "deeplink",
                    "error": str(exc),
                    "hint": "Confirm VPN/network access to the Oslo hub catalog, then retry.",
                },
            )
            return

        selected = deeplink_options[0] if deeplink_options else None
        suggestions = deeplink_options[1:]
        self._send_json(
            HTTPStatus.OK,
            {
                "intent": intent,
                "selected_deeplink": deeplink_option_payload(selected),
                "suggested_deeplinks": [deeplink_option_payload(option) for option in suggestions],
                "deeplink_options": [
                    deeplink_option_payload(option) for option in deeplink_options
                ],
                "model": COSMOS_LLM_MODEL,
            },
        )

    def _handle_variants(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).strip()
        if not intent:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Enter your intent first."})
            return
        if not title or not body:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Generate or enter title and body copy before creating variants."},
            )
            return

        try:
            variants = generate_copy_variants(
                intent,
                CopyDraft(title=title, body=body),
                count=2,
            )
        except CosmosLlmError as exc:
            self._send_json(HTTPStatus.BAD_GATEWAY, copy_error_payload(exc))
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "variants": [copy_response_payload(variant) for variant in variants],
                "model": COSMOS_LLM_MODEL,
            },
        )

    def _handle_package(self, payload: dict[str, Any]) -> None:
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).strip()
        deeplink = str(payload.get("deeplink", "")).strip()
        if not title or not body:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Enter title and body copy before building the upload JSON."},
            )
            return
        if not deeplink:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Enter or select a deeplink before building the upload JSON."},
            )
            return

        try:
            package = build_demo_campaign_package(title=title, body=body, deeplink=deeplink)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {
                    "error": f"Could not build the demo campaign package: {exc}",
                    "hint": "Confirm resources/agentic_comms_test.json is present and still has PUSH content.",
                },
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "package": package,
                "download_filename": "oslo-demo-campaign-upload.json",
                "updated_fields": {
                    "title": title,
                    "body": body,
                    "deep_link": deeplink,
                },
                "hard_coded_from": str(REFERENCE_CAMPAIGN_PATH.relative_to(PROJECT_ROOT)),
            },
        )

    def _handle_create_campaign(self, payload: dict[str, Any]) -> None:
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).strip()
        deeplink = str(payload.get("deeplink", "")).strip()
        segment_id = str(payload.get("segment_id", "")).strip()
        segment_code = str(payload.get("segment_code", "")).strip()
        if not title or not body:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Enter title and body copy before creating the campaign."},
            )
            return
        if not deeplink:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Enter or select a deeplink before creating the campaign."},
            )
            return
        if not segment_id or not segment_code:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": "Select an RPS segment with both segment ID and segment code before creating the campaign."
                },
            )
            return

        try:
            campaign_id, patch_payload = build_demo_campaign_patch_payload(
                title=title,
                body=body,
                deeplink=deeplink,
                segment_id=segment_id,
                segment_code=segment_code,
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {
                    "error": f"Could not build the campaign PATCH payload: {exc}",
                    "hint": "Confirm resources/agentic_comms_test.json is present and still has PUSH content plus a Dynamic Segment target.",
                },
            )
            return

        try:
            response_payload = patch_demo_campaign(campaign_id, patch_payload)
        except RuntimeError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "error": str(exc),
                    "hint": "Confirm VPN/network access to the QA campaign-management host, then retry.",
                    "campaign_id": campaign_id,
                    "patch_payload": patch_payload,
                },
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "campaign_id": campaign_id,
                "source_template": str(AGENTIC_CAMPAIGN_PATH.relative_to(PROJECT_ROOT)),
                "updated_fields": {
                    "title": title,
                    "body": body,
                    "deep_link": deeplink,
                    "segment_id": segment_id,
                    "segment_code": segment_code,
                },
                "patch_payload": patch_payload,
                "response": response_payload,
            },
        )

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        if content_length > 1_000_000:
            raise ValueError("Request body is too large.")

        raw_body = self.rfile.read(content_length)
        try:
            decoded = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must be valid JSON.") from exc
        if not isinstance(decoded, dict):
            raise ValueError("Request body must be a JSON object.")
        return decoded

    def _send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[local-demo] {self.address_string()} - {format % args}")


def health_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "server_version": DEMO_SERVER_VERSION,
        "process_id": os.getpid(),
        "has_api_key": bool(cosmos_api_key()),
        "model": COSMOS_LLM_MODEL,
        "max_tokens": COSMOS_LLM_MAX_TOKENS,
        "cosmos_base_url": COSMOS_LLM_BASE_URL,
        "rps_base_url": DYNSEG_BASE_URL,
        "deeplink_catalog_url": DEEPLINK_CATALOG_URL,
        "deeplink_catalog_data_url": DEEPLINK_CATALOG_DATA_URL,
    }


def copy_response_payload(copy: CopyDraft) -> dict[str, str]:
    return asdict(copy)


def audience_option_payload(option: AudienceOption | None) -> dict[str, Any] | None:
    if option is None:
        return None
    return {
        "recommendation": asdict(option.recommendation),
        "details": option.details,
    }


def deeplink_option_payload(option: DeeplinkOption | None) -> dict[str, Any] | None:
    if option is None:
        return None
    return {
        "recommendation": asdict(option.recommendation),
        "details": option.details,
    }


def build_demo_campaign_package(title: str, body: str, deeplink: str) -> dict[str, Any]:
    package = json.loads(REFERENCE_CAMPAIGN_PATH.read_text())
    push_channel = next(
        (
            channel
            for channel in package.get("channel_details", [])
            if channel.get("channel_name") == "PUSH" or channel.get("channel_id") == 1002
        ),
        None,
    )
    if not isinstance(push_channel, dict):
        raise ValueError("reference campaign does not include a PUSH channel")

    content_items = push_channel.get("content")
    if not isinstance(content_items, list) or not content_items:
        raise ValueError("reference PUSH channel does not include content")

    content = content_items[0]
    content_payload = content.setdefault("content_payload", {})
    locale = str(content.get("default_locale") or "en-US")
    localized = content_payload.setdefault("localizable_content", {}).setdefault(locale, {})
    localized["title"] = title
    localized["body"] = body
    content_payload.setdefault("non_localizable_content", {})["deep_link"] = deeplink
    return package


def build_demo_campaign_patch_payload(
    title: str,
    body: str,
    deeplink: str,
    segment_id: str,
    segment_code: str,
) -> tuple[str, dict[str, Any]]:
    campaign = json.loads(AGENTIC_CAMPAIGN_PATH.read_text())
    campaign_id = str(campaign.get("campaign_id") or "").strip()
    if not campaign_id:
        raise ValueError("agentic campaign template is missing campaign_id")

    delivery_type = str(campaign.get("delivery_type") or "").strip()
    if not delivery_type:
        raise ValueError("agentic campaign template is missing delivery_type")

    delivery_config = campaign.get("delivery_config")
    if not isinstance(delivery_config, dict):
        raise ValueError("agentic campaign template is missing delivery_config")

    dynamic_segment = (
        delivery_config.get("target_config", {})
        .get("dynamic_segment", {})
    )
    groups = dynamic_segment.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("delivery_config does not include Dynamic Segment groups")

    include_segments = groups[0].get("include_segments")
    if not isinstance(include_segments, list) or not include_segments:
        raise ValueError("delivery_config does not include include_segments")

    include_segments[0]["segment_id"] = segment_id
    include_segments[0]["segment_code"] = segment_code

    push_channel = next(
        (
            channel
            for channel in campaign.get("channel_details", [])
            if channel.get("channel_name") == "PUSH" or channel.get("channel_id") == 1002
        ),
        None,
    )
    if not isinstance(push_channel, dict):
        raise ValueError("agentic campaign template does not include a PUSH channel")

    content_items = push_channel.get("content")
    if not isinstance(content_items, list) or not content_items:
        raise ValueError("agentic PUSH channel does not include content")

    content = content_items[0]
    if not isinstance(content, dict):
        raise ValueError("agentic PUSH content is invalid")

    content_payload = content.get("content_payload")
    if not isinstance(content_payload, dict):
        raise ValueError("agentic PUSH content is missing content_payload")

    localized = content_payload.get("localizable_content", {}).get("en-US")
    if not isinstance(localized, dict):
        raise ValueError("agentic PUSH content is missing localizable_content.en-US")

    localized["title"] = title
    localized["body"] = body
    non_localized = content_payload.get("non_localizable_content")
    if not isinstance(non_localized, dict):
        raise ValueError("agentic PUSH content is missing non_localizable_content")
    non_localized["deep_link"] = deeplink

    patch_content = {
        key: content[key]
        for key in (
            "content_id",
            "content_name",
            "content_variant_code",
            "default_locale",
            "content_legal_review_exception",
            "content_legal_review_exception_reason",
        )
        if key in content
    }
    patch_content["content_payload"] = content_payload

    patch_channel = {
        key: push_channel[key]
        for key in ("channel_id", "channel_name", "channel_rules")
        if key in push_channel
    }
    patch_channel["content"] = [patch_content]

    return campaign_id, {
        "delivery_type": delivery_type,
        "delivery_config": delivery_config,
        "channel_details": [patch_channel],
    }


def patch_demo_campaign(campaign_id: str, patch_payload: dict[str, Any]) -> dict[str, Any]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f"{CAMPAIGN_MANAGEMENT_BASE_URL}/{campaign_id}"
    try:
        response = requests.patch(
            url,
            headers={
                "Content-Type": "application/json",
                "USER_DETAILS": CAMPAIGN_MANAGEMENT_USER_DETAILS,
            },
            json=patch_payload,
            timeout=CAMPAIGN_MANAGEMENT_TIMEOUT_SECONDS,
            verify=False,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"PATCH {url} failed: {exc}") from exc

    detail = response.text.strip()
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        message = f"PATCH {url} failed: {exc}"
        if detail:
            message = f"{message} - {detail[:500]}"
        raise RuntimeError(message) from exc

    try:
        parsed = response.json()
    except ValueError:
        return {"raw_response": detail}
    if not isinstance(parsed, dict):
        return {"response": parsed}
    return parsed


def last_workflow_payload() -> dict[str, Any]:
    if LAST_WORKFLOW_RESPONSE is None:
        return {
            "captured": False,
            "message": "No workflow has been generated since the server started.",
        }
    return {
        "captured": True,
        "workflow": LAST_WORKFLOW_RESPONSE,
    }


def record_last_workflow(status: HTTPStatus, intent: str, response_payload: dict[str, Any]) -> None:
    global LAST_WORKFLOW_RESPONSE

    captured = {
        "captured_at": datetime.now(UTC).isoformat(),
        "status": int(status),
        "status_text": status.phrase,
        "intent": intent,
        "response": response_payload,
    }
    LAST_WORKFLOW_RESPONSE = json.loads(json.dumps(captured, ensure_ascii=True))
    print(workflow_log_line(LAST_WORKFLOW_RESPONSE), flush=True)


def workflow_log_line(workflow: dict[str, Any]) -> str:
    response = workflow.get("response") if isinstance(workflow.get("response"), dict) else {}
    selected = response.get("selected_audience") if isinstance(response, dict) else None
    selected_rec = selected.get("recommendation") if isinstance(selected, dict) else None
    selected_deeplink = response.get("selected_deeplink") if isinstance(response, dict) else None
    selected_deeplink_rec = (
        selected_deeplink.get("recommendation") if isinstance(selected_deeplink, dict) else None
    )
    suggestions = response.get("suggested_audiences") if isinstance(response, dict) else []
    suggestion_codes = []
    if isinstance(suggestions, list):
        for option in suggestions:
            rec = option.get("recommendation") if isinstance(option, dict) else None
            if isinstance(rec, dict):
                suggestion_codes.append(str(rec.get("code") or rec.get("segment_id") or ""))

    selected_code = ""
    selected_id = ""
    selected_deeplink_path = ""
    if isinstance(selected_rec, dict):
        selected_code = str(selected_rec.get("code") or "")
        selected_id = str(selected_rec.get("segment_id") or "")
    if isinstance(selected_deeplink_rec, dict):
        selected_deeplink_path = str(
            selected_deeplink_rec.get("path") or selected_deeplink_rec.get("url") or ""
        )

    if response.get("error"):
        outcome = f"error={response.get('error')}"
    else:
        outcome = f"selected={selected_code or selected_id or 'none'}"
        if selected_id:
            outcome = f"{outcome} ({selected_id})"

    return (
        "[workflow] "
        f"status={workflow.get('status')} "
        f"intent={workflow.get('intent')!r} "
        f"{outcome} "
        f"deeplink={selected_deeplink_path or 'none'} "
        f"suggestions={', '.join(filter(None, suggestion_codes)) or 'none'}"
    )


def copy_error_payload(exc: CosmosLlmError) -> dict[str, Any]:
    error = str(exc)
    if error.startswith(f"Missing {COSMOS_LLM_API_KEY_ENV}"):
        hint = f"Check {COSMOS_LLM_API_KEY_ENV} in .env, then restart the local demo."
    elif "empty copy output" in error:
        hint = (
            "The Cosmos request succeeded, but the model returned no visible copy. "
            "The server retried with a larger token budget; try again or increase "
            "COSMOS_LLM_MAX_TOKENS in .env."
        )
    else:
        hint = "The Cosmos request reached the API but returned an unusable copy response."

    return {
        "step": "copy",
        "error": error,
        "hint": hint,
    }


def build_server(host: str, port: int) -> ReusableThreadingHTTPServer:
    last_error: OSError | None = None
    candidate_ports = [0] if port == 0 else list(range(port, port + 21))
    for candidate_port in candidate_ports:
        try:
            return ReusableThreadingHTTPServer((host, candidate_port), LocalDemoHandler)
        except OSError as exc:
            last_error = exc
            if port == 0 or exc.errno not in {48, 98}:
                raise
    raise OSError(f"Could not bind localhost demo on ports {port}-{port + 20}.") from last_error


def serve(host: str, port: int) -> None:
    server = build_server(host, port)
    actual_host, actual_port = server.server_address
    display_host = "127.0.0.1" if actual_host in {"", "0.0.0.0"} else actual_host
    print(f"Local demo running at http://{display_host}:{actual_port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local demo.")
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Oslo Comms Studio localhost demo.")
    parser.add_argument("--host", default=os.getenv("OSLO_DEMO_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("OSLO_DEMO_PORT", "8000")))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
