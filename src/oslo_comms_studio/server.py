from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
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

DEMO_SERVER_VERSION = "push-enrollment-paypal-logo-v5"
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

    label {
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
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

    <div class="demo-layout">
      <div class="workflow">
        <form id="intentForm" class="panel">
          <div class="panel-header">
            <h2 class="panel-title"><span class="step-number">1</span>Declared Intent</h2>
            <span class="badge" id="modelBadge">Localhost</span>
          </div>
          <div class="panel-body">
            <label for="intent">Intent</label>
            <textarea id="intent" name="intent" spellcheck="true">__DEFAULT_INTENT__</textarea>
            <div class="actions">
              <button id="submitButton" class="primary" type="submit">Generate workflow</button>
              <span id="workflowStatus" class="status">Ready</span>
            </div>
          </div>
        </form>

        <section class="panel">
          <div class="panel-header">
            <h2 class="panel-title"><span class="step-number">2</span>Editable Copy</h2>
            <span id="copyBadge" class="badge">Waiting</span>
          </div>
          <div class="panel-body">
            <div class="copy-fields">
              <div>
                <label for="copyTitle">Title</label>
                <input id="copyTitle" class="copy-title" type="text" spellcheck="true">
              </div>
              <div>
                <label for="copyBody">Body</label>
                <textarea id="copyBody" class="copy-body" spellcheck="true"></textarea>
              </div>
            </div>
            <div class="actions">
              <button id="regenButton" class="secondary" type="button" disabled>Regenerate copy text</button>
              <span id="copyStatus" class="status">Run the workflow to generate copy.</span>
            </div>
          </div>
        </section>

        <div class="support-grid">
          <section class="panel">
            <div class="panel-header">
              <h2 class="panel-title"><span class="step-number">3</span>Audience</h2>
              <span id="rpsBadge" class="badge">Waiting</span>
            </div>
            <div class="panel-body">
              <div class="split">
                <div>
                  <label for="segmentId">RPS Segment ID</label>
                  <input id="segmentId" type="text" autocomplete="off" placeholder="Dynamic Segment ID">
                  <div class="actions">
                    <span id="segmentStatus" class="status">Run the workflow to select a segment.</span>
                  </div>
                </div>
                <div>
                  <label>RPS Details</label>
                  <div id="segmentDetails" class="details-box">
                    <div class="empty">No segment selected.</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="panel">
            <div class="panel-header">
              <h2 class="panel-title"><span class="step-number">4</span>Suggested Audience Options</h2>
              <span id="suggestionsBadge" class="badge">Waiting</span>
            </div>
            <div class="panel-body">
              <div id="suggestions" class="suggestions">
                <div class="empty">Run the workflow to see suggested audiences.</div>
              </div>
            </div>
          </section>
        </div>
      </div>

      <aside class="phone-panel" aria-label="Push notification preview">
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
                <div id="previewTitle" class="notification-title">PayPal</div>
                <div id="previewBody" class="notification-body">You received $0.01 USD from Heidy Diana</div>
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
        <h2 class="panel-title"><span class="step-number">5</span>Generate Content Variants for A/B Experimentation</h2>
        <span id="variantsBadge" class="badge">Waiting</span>
      </div>
      <div class="panel-body">
        <div class="variant-question">
          <strong>Create content variations for A/B testing?</strong>
          <div class="button-row">
            <button id="variantsYes" class="choice-button yes" type="button" disabled>Yes</button>
            <button id="variantsNo" class="choice-button" type="button" disabled>No</button>
          </div>
        </div>
        <div class="actions">
          <span id="variantsStatus" class="status">Generate the workflow first.</span>
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
      workflowStatus.textContent = isLoading ? "Calling Cosmos and RPS" : "Ready";
    }

    function updatePreview() {
      previewTitle.textContent = copyTitle.value.trim() || "PayPal";
      previewBody.textContent = copyBody.value.trim() || "You received $0.01 USD from Heidy Diana";
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
        segmentDetails.innerHTML = '<div class="empty">No segment selected.</div>';
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
        segmentStatus.textContent = "No segment selected.";
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
        ? `Selected ${recommendation.segment_id}`
        : "Selected audience";
      setBadge(rpsBadge, "Selected", "ok");
      renderSegmentDetails(option);
    }

    function renderSuggestions(options) {
      activeSuggestions = options || [];
      if (!activeSuggestions.length) {
        suggestions.innerHTML = '<div class="empty">No alternate dynamic audiences returned.</div>';
        setBadge(suggestionsBadge, "No options", "warn");
        return;
      }

      suggestions.innerHTML = activeSuggestions.map((option, index) => {
        const recommendation = optionRecommendation(option);
        return `
          <button class="suggestion" type="button" data-index="${index}">
            <strong>${escapeHtml(recommendation.code || recommendation.segment_id)}</strong>
            <span>${escapeHtml(recommendation.description || "No description returned.")}</span>
            <span>${escapeHtml(recommendation.segment_id)} · ${escapeHtml(recommendation.audience_count || "Unavailable")}</span>
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
              <div class="notification-title">${escapeHtml(copy.title || "PayPal")}</div>
              <div class="notification-body">${escapeHtml(copy.body || "Notification body")}</div>
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
      copyStatus.textContent = "Generating copy.";
      segmentStatus.textContent = "Searching RPS.";
      segmentDetails.innerHTML = '<div class="empty">Searching RPS...</div>';
      suggestions.innerHTML = '<div class="empty">Waiting for RPS suggestions.</div>';

      try {
        const data = await postJson("/api/demo", { intent: value });
        applyCopy(data.copy);
        copyStatus.textContent = "Copy is editable.";
        setBadge(copyBadge, "Generated", "ok");
        setVariantControlsEnabled(true);
        clearVariants("Ready to create content variations.");
        setBadge(variantsBadge, "Ready");
        setSelectedAudience(data.selected_audience);
        renderSuggestions(data.suggested_audiences);
      } catch (error) {
        const payload = error.payload || { error: error.message };
        if (payload.step === "copy") {
          setBadge(copyBadge, "Error", "error");
          setBadge(rpsBadge, "Waiting");
          copyStatus.textContent = "Copy generation failed.";
          renderError(segmentDetails, payload);
        } else {
          if (payload.copy) {
            applyCopy(payload.copy);
            setBadge(copyBadge, "Generated", "ok");
            setVariantControlsEnabled(true);
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
      copyStatus.textContent = "Calling Cosmos again.";
      try {
        const data = await postJson("/api/copy", { intent: value });
        applyCopy(data.copy);
        copyStatus.textContent = "Copy regenerated.";
        setBadge(copyBadge, "Generated", "ok");
        clearVariants("Copy changed. Create content variations again when ready.");
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

        segmentStatus.textContent = "Looking up segment.";
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
      variantsStatus.textContent = "Generating two content variants.";
      setBadge(variantsBadge, "Generating", "warn");
      try {
        const data = await postJson("/api/variants", {
          intent: value,
          title: copy.title,
          body: copy.body
        });
        renderVariantRow(data.variants || []);
        variantsStatus.textContent = "Three push notification variants are ready.";
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
            self._send_json(HTTPStatus.BAD_GATEWAY, copy_error_payload(exc))
            return

        copy_payload = copy_response_payload(copy)
        try:
            audience_options = search_audience_options(intent, limit=3)
        except RpsApiError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "step": "rps",
                    "copy": copy_payload,
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
                "copy": copy_payload,
                "selected_audience": audience_option_payload(selected),
                "suggested_audiences": [audience_option_payload(option) for option in suggestions],
                "audience": asdict(selected.recommendation) if selected else None,
                "model": COSMOS_LLM_MODEL,
            },
        )

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
