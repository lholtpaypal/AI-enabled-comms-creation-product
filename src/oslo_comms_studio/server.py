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

from oslo_comms_studio.app import (
    COSMOS_LLM_API_KEY_ENV,
    COSMOS_LLM_BASE_URL,
    COSMOS_LLM_MAX_TOKENS,
    COSMOS_LLM_MODEL,
    DEFAULT_INTENT,
    DYNSEG_BASE_URL,
    AudienceOption,
    CopyDraft,
    CosmosLlmError,
    RpsApiError,
    cosmos_api_key,
    generate_copy,
    generate_copy_variants,
    get_dynamic_segment,
    search_audience_options,
)

DEMO_SERVER_VERSION = "blank-startup-preview-v9"
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

    .support-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.08fr) minmax(300px, 0.92fr);
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

    .primary {
      border: 0;
      background: var(--accent);
      color: #fff;
    }

    .primary:hover {
      background: var(--accent-dark);
    }

    .secondary {
      border: 1px solid #b9c3d0;
      background: #fff;
      color: var(--ink);
    }

    .choice-button {
      min-height: 36px;
      border: 1px solid #b9c3d0;
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      padding: 0 14px;
      cursor: pointer;
      font-weight: 750;
    }

    .choice-button.yes {
      border-color: var(--accent);
      background: var(--accent);
      color: #fff;
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
        Create from intent
        <span class="help-tip" tabindex="0" aria-label="Page overview help" data-tooltip="Start at step 1 and work down the page. Every generated output is visible, and editable fields are marked.">?</span>
      </h2>
      <p>Start with a plain-English campaign request. The tool uses that intent to assemble the first pass, but it does not hide the work: you can see and edit the copy, inspect the audience, compare alternatives, and decide whether variants are needed.</p>
      <ol aria-label="Workflow summary">
        <li><strong>1. Write the intent</strong> Say what you want to create, who it is for, and what the customer should do.</li>
        <li><strong>2. Generate the workflow</strong> Cosmos drafts copy while RPS searches for matching Dynamic Segments.</li>
        <li><strong>3. Edit the copy</strong> Title and body are editable, and the phone preview updates immediately.</li>
        <li><strong>4. Inspect the audience</strong> The selected RPS segment ID and read-only RPS details are shown before you trust it.</li>
        <li><strong>5. Compare alternatives</strong> Suggested audience options are clickable if another segment fits better.</li>
        <li><strong>6. Create variants</strong> Choose whether to generate A/B copy variants from the current edited copy.</li>
      </ol>
    </section>

    <div class="demo-layout">
      <div class="workflow">
        <form id="intentForm" class="panel">
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">1</span>
              Intent
              <span class="help-tip" tabindex="0" aria-label="Intent help" data-tooltip="Describe the campaign in plain English. Include message type, audience, product or feature, and what the customer should do. You do not need final copy or an RPS segment ID yet.">?</span>
            </h2>
            <span class="badge" id="modelBadge">Localhost</span>
          </div>
          <div class="panel-body">
            <p class="section-help">Describe the campaign.</p>
            <label for="intent">
              Campaign intent
              <span class="field-tag">Editable</span>
              <span class="help-tip" tabindex="0" aria-label="Campaign intent field help" data-tooltip="This is the main input. More specific intent gives the tool better context for copy, audience search, deeplink assumptions, and variants.">?</span>
            </label>
            <textarea id="intent" name="intent" spellcheck="true" placeholder="Example: Create a push notification for eligible US customers who have not enrolled in the PayPal Debit Card. Goal: get them to start enrollment. Tone: clear and helpful.">__DEFAULT_INTENT__</textarea>
            <details class="example-list" aria-label="Campaign intent examples">
              <summary>Need examples? Open this.</summary>
              <ul>
                <li>Create a push notification for eligible US customers who have not enrolled in PayPal Debit Card. Goal: get them to start enrollment.</li>
                <li>Create an app tile for customers who used Pay Later last month. Goal: remind them that a new promo is available.</li>
                <li>Create an email for small business sellers with high checkout volume. Goal: introduce a working-capital offer. Keep the tone practical.</li>
              </ul>
            </details>
            <div class="actions">
              <button id="submitButton" class="primary" type="submit">Generate workflow</button>
              <span id="workflowStatus" class="status">Waiting for your campaign intent.</span>
            </div>
          </div>
        </form>

        <section class="panel">
          <div class="panel-header">
            <h2 class="panel-title">
              <span class="step-number">2</span>
              Copy
              <span class="help-tip" tabindex="0" aria-label="Copy help" data-tooltip="Cosmos drafts the title and body from your intent. Treat the generated text as a starting point. Both fields are editable, and the phone preview updates as you type.">?</span>
            </h2>
            <span id="copyBadge" class="badge">Waiting</span>
          </div>
          <div class="panel-body">
            <p class="section-help">Edit the generated message.</p>
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
              <span id="copyStatus" class="status">Run step 1 to generate editable copy.</span>
            </div>
          </div>
        </section>

        <div class="support-grid">
          <section class="panel">
            <div class="panel-header">
              <h2 class="panel-title">
                <span class="step-number">3</span>
                Audience
                <span class="help-tip" tabindex="0" aria-label="Audience help" data-tooltip="The audience controls who receives the message. The tool searches RPS Dynamic Segments from your intent, then shows the selected segment so you can inspect it.">?</span>
              </h2>
              <span id="rpsBadge" class="badge">Waiting</span>
            </div>
            <div class="panel-body">
              <p class="section-help">Review the selected segment.</p>
              <div class="split">
                <div>
                  <label for="segmentId">
                    RPS Segment ID
                    <span class="field-tag">Editable</span>
                    <span class="help-tip" tabindex="0" aria-label="RPS segment ID help" data-tooltip="The recommended segment ID appears here. Paste a different Dynamic Segment ID or code to replace it and refresh the details below.">?</span>
                  </label>
                  <input id="segmentId" type="text" autocomplete="off" placeholder="Paste a Dynamic Segment ID or code">
                  <div class="actions">
                    <span id="segmentStatus" class="status">Run step 1 to let RPS choose a segment, or paste a segment ID yourself.</span>
                  </div>
                </div>
                <div>
                  <label>
                    RPS details
                    <span class="field-tag">Read-only</span>
                    <span class="help-tip" tabindex="0" aria-label="RPS details help" data-tooltip="These are facts returned by RPS. Check the code, description, count, status, country, owner, and refresh timing before trusting the audience.">?</span>
                  </label>
                  <div id="segmentDetails" class="details-box">
                    <div class="empty">No segment selected yet. After the workflow runs, this box will explain exactly which RPS segment was found.</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="panel">
            <div class="panel-header">
              <h2 class="panel-title">
                <span class="step-number">4</span>
                Alternatives
                <span class="help-tip" tabindex="0" aria-label="Alternative audiences help" data-tooltip="These are other RPS segments that looked relevant. Click one if its description fits the campaign better than the current selection.">?</span>
              </h2>
              <span id="suggestionsBadge" class="badge">Waiting</span>
            </div>
            <div class="panel-body">
              <p class="section-help">Optional audience swaps.</p>
              <div id="suggestions" class="suggestions">
                <div class="empty">Run step 1 to see suggested audiences.</div>
              </div>
            </div>
          </section>
        </div>
      </div>

      <aside class="phone-panel" aria-label="Push notification preview">
        <div class="preview-note">
          <strong>
            Live preview
            <span class="help-tip" tabindex="0" aria-label="Live preview help" data-tooltip="This mock phone shows how the current title and body read on a lock screen. It updates immediately when you edit copy.">?</span>
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

    <section class="panel variant-panel">
      <div class="panel-header">
        <h2 class="panel-title">
          <span class="step-number">5</span>
          Variants
          <span class="help-tip" tabindex="0" aria-label="Variants help" data-tooltip="Variants test different ways to say the same thing. The current title and body, including edits you made, become the control copy.">?</span>
        </h2>
        <span id="variantsBadge" class="badge">Waiting</span>
      </div>
      <div class="panel-body">
        <p class="section-help">Create A/B copy options.</p>
        <div class="variant-question">
          <div>
            <strong>
              Create two variants?
              <span class="help-tip" tabindex="0" aria-label="Create variants help" data-tooltip="Choose Yes to generate Variant A and Variant B. Choose No if the current copy should remain the only version.">?</span>
            </strong>
          </div>
          <div class="button-row">
            <button id="variantsYes" class="choice-button yes" type="button" disabled>Yes</button>
            <button id="variantsNo" class="choice-button" type="button" disabled>No</button>
          </div>
        </div>
        <div class="actions">
          <span id="variantsStatus" class="status">Run step 1 first. Variants use the editable copy from step 2.</span>
        </div>
        <div id="variantRow" class="variant-row" hidden></div>
      </div>
    </section>
  </main>

  <script>
    const form = document.querySelector("#intentForm");
    const intent = document.querySelector("#intent");
    const submitButton = document.querySelector("#submitButton");
    const regenButton = document.querySelector("#regenButton");
    const copyTitle = document.querySelector("#copyTitle");
    const copyBody = document.querySelector("#copyBody");
    const previewTitle = document.querySelector("#previewTitle");
    const previewBody = document.querySelector("#previewBody");
    const segmentId = document.querySelector("#segmentId");
    const segmentDetails = document.querySelector("#segmentDetails");
    const suggestions = document.querySelector("#suggestions");
    const workflowStatus = document.querySelector("#workflowStatus");
    const copyStatus = document.querySelector("#copyStatus");
    const segmentStatus = document.querySelector("#segmentStatus");
    const copyBadge = document.querySelector("#copyBadge");
    const rpsBadge = document.querySelector("#rpsBadge");
    const suggestionsBadge = document.querySelector("#suggestionsBadge");
    const healthDot = document.querySelector("#healthDot");
    const healthText = document.querySelector("#healthText");
    const modelBadge = document.querySelector("#modelBadge");
    const variantsYes = document.querySelector("#variantsYes");
    const variantsNo = document.querySelector("#variantsNo");
    const variantsBadge = document.querySelector("#variantsBadge");
    const variantsStatus = document.querySelector("#variantsStatus");
    const variantRow = document.querySelector("#variantRow");

    let activeSuggestions = [];
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

    function setWorkflowLoading(isLoading) {
      submitButton.disabled = isLoading;
      regenButton.disabled = isLoading || !intent.value.trim();
      workflowStatus.textContent = isLoading
        ? "Working: using your intent to ask Cosmos for copy and RPS for audience matches."
        : "Ready for edits or another workflow run.";
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

    function renderSegmentDetails(option) {
      const recommendation = optionRecommendation(option);
      if (!recommendation) {
        segmentDetails.innerHTML = '<div class="empty">No segment selected yet. After the workflow runs, this box will explain exactly which RPS segment was found.</div>';
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
        segmentStatus.textContent = "No segment selected. Paste a Dynamic Segment ID or choose a suggestion when one is available.";
        setBadge(rpsBadge, "No match", "warn");
        renderSegmentDetails(null);
        return;
      }

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
    }

    function renderSuggestions(options) {
      activeSuggestions = options || [];
      if (!activeSuggestions.length) {
        suggestions.innerHTML = '<div class="empty">No alternate dynamic audiences returned. The selected segment in step 3 is the only match the search returned.</div>';
        setBadge(suggestionsBadge, "No options", "warn");
        return;
      }

      suggestions.innerHTML = activeSuggestions.map((option, index) => {
        const recommendation = optionRecommendation(option);
        return `
          <button class="suggestion" type="button" data-index="${index}">
            <strong>${escapeHtml(recommendation.code || recommendation.segment_id)}</strong>
            <span>${escapeHtml(recommendation.description || "No description returned.")}</span>
            <span>Click to use this segment. ${escapeHtml(recommendation.segment_id)} · ${escapeHtml(recommendation.audience_count || "Unavailable")}</span>
          </button>
        `;
      }).join("");
      setBadge(suggestionsBadge, `${activeSuggestions.length} options`, "ok");
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
        workflowStatus.textContent = "Enter an intent first.";
        return;
      }

      setWorkflowLoading(true);
      setBadge(copyBadge, "Calling", "warn");
      setBadge(rpsBadge, "Searching", "warn");
      setBadge(suggestionsBadge, "Waiting");
      copyStatus.textContent = "Working: Cosmos is drafting a title and body from your intent.";
      segmentStatus.textContent = "Working: RPS is searching Dynamic Segments that match your intended audience.";
      segmentDetails.innerHTML = '<div class="empty">Searching RPS. Details will appear here so you can inspect the selected segment.</div>';
      suggestions.innerHTML = '<div class="empty">Waiting for alternate RPS audience options.</div>';

      try {
        const data = await postJson("/api/demo", { intent: value });
        applyCopy(data.copy);
        copyStatus.textContent = "Done: copy generated. Title and body are editable, and the phone preview updates as you type.";
        setBadge(copyBadge, "Generated", "ok");
        setVariantControlsEnabled(true);
        clearVariants("Ready: choose Yes to create variants from the current editable copy.");
        setBadge(variantsBadge, "Ready");
        setSelectedAudience(data.selected_audience);
        renderSuggestions(data.suggested_audiences);
      } catch (error) {
        const payload = error.payload || { error: error.message };
        if (payload.step === "copy") {
          setBadge(copyBadge, "Error", "error");
          setBadge(rpsBadge, "Waiting");
          copyStatus.textContent = "Copy generation failed before RPS search could run.";
          renderError(segmentDetails, payload);
        } else {
          if (payload.copy) {
            applyCopy(payload.copy);
            setBadge(copyBadge, "Generated", "ok");
            setVariantControlsEnabled(true);
            copyStatus.textContent = "Copy generated, but the audience step needs attention.";
          }
          setBadge(rpsBadge, "Error", "error");
          renderError(segmentDetails, payload);
        }
      } finally {
        setWorkflowLoading(false);
      }
    });

    regenButton.addEventListener("click", async () => {
      const value = intent.value.trim();
      if (!value) {
        copyStatus.textContent = "Enter an intent first.";
        return;
      }

      regenButton.disabled = true;
      setBadge(copyBadge, "Regenerating", "warn");
      copyStatus.textContent = "Working: asking Cosmos for a fresh title and body using the same intent.";
      try {
        const data = await postJson("/api/copy", { intent: value });
        applyCopy(data.copy);
        copyStatus.textContent = "Done: copy regenerated. You can still edit the title and body directly.";
        setBadge(copyBadge, "Generated", "ok");
        clearVariants("Copy changed. Choose Yes again when you want variants based on the new copy.");
        setBadge(variantsBadge, "Ready");
      } catch (error) {
        const payload = error.payload || { error: error.message };
        copyStatus.textContent = payload.error || "Copy regeneration failed.";
        setBadge(copyBadge, "Error", "error");
      } finally {
        regenButton.disabled = false;
      }
    });

    segmentId.addEventListener("input", () => {
      if (suppressSegmentLookup) return;
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

    suggestions.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-index]");
      if (!button) return;
      const option = activeSuggestions[Number(button.dataset.index)];
      setSelectedAudience(option);
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
    });

    copyTitle.addEventListener("input", updatePreview);
    copyBody.addEventListener("input", updatePreview);

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
        if path == "/api/segment":
            self._handle_segment(payload)
            return
        if path == "/api/variants":
            self._handle_variants(payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def _handle_demo(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        if not intent:
            self._send_json(
                HTTPStatus.BAD_REQUEST, {"error": "Enter an intent before generating copy."}
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
        response_payload = {
            "intent": intent,
            "copy": copy_payload,
            "selected_audience": audience_option_payload(selected),
            "suggested_audiences": [audience_option_payload(option) for option in suggestions],
            "audience": asdict(selected.recommendation) if selected else None,
            "model": COSMOS_LLM_MODEL,
        }
        record_last_workflow(HTTPStatus.OK, intent, response_payload)
        self._send_json(HTTPStatus.OK, response_payload)

    def _handle_copy(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        if not intent:
            self._send_json(
                HTTPStatus.BAD_REQUEST, {"error": "Enter an intent before generating copy."}
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

    def _handle_variants(self, payload: dict[str, Any]) -> None:
        intent = str(payload.get("intent", "")).strip()
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).strip()
        if not intent:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Enter an intent first."})
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
    suggestions = response.get("suggested_audiences") if isinstance(response, dict) else []
    suggestion_codes = []
    if isinstance(suggestions, list):
        for option in suggestions:
            rec = option.get("recommendation") if isinstance(option, dict) else None
            if isinstance(rec, dict):
                suggestion_codes.append(str(rec.get("code") or rec.get("segment_id") or ""))

    selected_code = ""
    selected_id = ""
    if isinstance(selected_rec, dict):
        selected_code = str(selected_rec.get("code") or "")
        selected_id = str(selected_rec.get("segment_id") or "")

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
