# 📊 Sovereign E2E Automation Summary

- **Date**: 2026-01-21 23:28
- **Total Tests**: 26
- **Passed**: ✅ 0
- **Failed**: ❌ 26

| ID | Test Name | Result | Details |
|---|---|---|---|
| CP-001 | Smoke Test - Page Load | ❌ | Page.goto: Timeout 30000ms exceeded.
Call log:
  - navigating to "http://localhost:8082/", waiting until "load"
 |
| CP-LAYOUT | Panel Visibility: Header | ❌ | Locator expected to be visible
Actual value: None 
Call log:
  - Expect "to_be_visible" with timeout 5000ms
  - waiting for locator(".header")
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-LAYOUT | Panel Visibility: Left Sidebar | ❌ | Locator expected to be visible
Actual value: None 
Call log:
  - Expect "to_be_visible" with timeout 5000ms
  - waiting for locator(".sidebar-left")
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-LAYOUT | Panel Visibility: Main Content Area | ❌ | Locator expected to be visible
Actual value: None 
Call log:
  - Expect "to_be_visible" with timeout 5000ms
  - waiting for locator(".center-content")
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-LAYOUT | Panel Visibility: Right Sidebar | ❌ | Locator expected to be visible
Actual value: None 
Call log:
  - Expect "to_be_visible" with timeout 5000ms
  - waiting for locator(".sidebar-right")
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-LAYOUT | Panel Visibility: Terminal Panel | ❌ | Locator expected to be visible
Actual value: None 
Call log:
  - Expect "to_be_visible" with timeout 5000ms
  - waiting for locator(".terminal-panel")
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-NAV | Switch to AGENT VIEW | ❌ | Page.wait_for_selector: Timeout 10000ms exceeded.
Call log:
  - waiting for locator("#tab-agent") to be visible
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-NAV | Switch to BYTEBOT DESKTOP | ❌ | Page.wait_for_selector: Timeout 10000ms exceeded.
Call log:
  - waiting for locator("#tab-bytebot") to be visible
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| CP-NAV | Switch to 3D NUCLEUS | ❌ | Page.wait_for_selector: Timeout 10000ms exceeded.
Call log:
  - waiting for locator("#tab-nucleus") to be visible
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| QA-ACTION | Trigger Run Evolution | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card").filter(has_text="Run Evolution").first
    - waiting for" http://localhost:8082/" navigation to finish...
 |
| QA-ACTION | Trigger Mesh Audit | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card").filter(has_text="Mesh Audit").first
 |
| QA-ACTION | Trigger API Workbench | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card").filter(has_text="API Workbench").first
 |
| QA-ACTION | Trigger Web Search | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card").filter(has_text="Web Search").first
 |
| QA-ACTION | Trigger aSiReM Speak | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card").filter(has_text="aSiReM Speak").first
 |
| QA-ACTION | Trigger Veo3 Credits | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card").filter(has_text="Veo3 Credits").first
 |
| AG-FLEET | Select Scanner | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Scanner')").first
 |
| AG-FLEET | Select Classifier | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Classifier')").first
 |
| AG-FLEET | Select Extractor | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Extractor')").first
 |
| AG-FLEET | Select Summarizer | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Summarizer')").first
 |
| AG-FLEET | Select Evolution | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Evolution')").first
 |
| AG-FLEET | Select Researcher | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Researcher')").first
 |
| AG-FLEET | Select Architect | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Architect')").first
 |
| AG-FLEET | Select Memory | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Memory')").first
 |
| AG-FLEET | Select Embedding | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('Embedding')").first
 |
| AG-FLEET | Select DocGen | ❌ | Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".agent-card:has-text('DocGen')").first
 |
| BB-001 | ByteBot Check Failed | ❌ | Page.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("text=BYTEBOT DESKTOP")
 |
