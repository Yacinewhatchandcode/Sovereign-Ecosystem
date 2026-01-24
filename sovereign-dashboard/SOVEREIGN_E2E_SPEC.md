# 🧬 Sovereign Command Center - Comprehensive E2E Test Specification

## 📊 Overview
This document defines the 100+ end-to-end user functional test cases for the AZIREM Sovereign Command Center dashboard. These tests cover navigation, actuation, visualization, and specialized agent interactions.

---

## 🏗️ 1. Core Platform & Navigation (25 Cases)

| ID | Feature | Action | Steps | Expected Result |
|:---|:---|:---|:---|:---|
| CP-001 | Smoke Test | Load URL | Open `http://localhost:8082` | Dashboard loads, title mentions "AZIREM SOVEREIGN" |
| CP-002 | Connection | Verify WS | Observe "🔌 WebSocket connected" in terminal | Green "LIVE" status badge in top right |
| CP-003 | Mode Switch | Select Agent View | Click "AGENT VIEW" tab | Main display switches to `viewer-video`, sidebar shows agent list |
| CP-004 | Mode Switch | Select ByteBot | Click "BYTEBOT DESKTOP" tab | Main display switches to VNC iframe |
| CP-005 | Mode Switch | Select Nucleus | Click "3D NUCLEUS" tab | Main display switches to 3D Canvas / Tech stream |
| CP-006 | Mode Switch | Select Stream | Click "SOVEREIGN STREAM" tab | Main display switches to master video stream |
| CP-007 | Sidebar | Toggle Agent | Click "Scanner" agent card | Highlights Scanner, updates Real-Time Activity to "Switched to Scanner" |
| CP-008 | Sidebar | Toggle Agent | Click "Classifier" agent card | Highlights Classifier, observer activity logs update |
| CP-009 | Sidebar | Agent Status | Check "Scanner" status | Observe green dot for active status |
| CP-010 | Header | Observe Mesh | Check "MESH: 1,176 AGENTS" | Stat is visible and formatted in neon orange |
| CP-011 | Footer | Terminal | Scroll Terminal | Logs are visible, terminal is interactive (scrollable) |
| CP-012 | Layout | Responsive Check | Resize window to 1024px | Layout maintains sidebar and center panel proportions |
| CP-013 | UI Theme | Glassmorphism | Inspect `.panel` background | Verify backdrop-filter and border-color transparency |
| CP-014 | Global State | Host Safety | Check "HOST SAFETY" stat | Status shows "100%" in neon green |
| CP-015 | Navigation | Fullscreen | Click Fullscreen icon in video | Main video enters browser fullscreen mode |
| CP-016 | Navigation | Unmute | Click Mute/Unmute icon | Volume icon toggles, audio playback resumes |
| CP-017 | Navigation | Play/Pause | Click Play/Pause icon | Video playback halts/resumes |
| CP-018 | Sidebar | Hover Effect | Hover over Agent Card | Card border glows neon cyan |
| CP-019 | Header | API Status | Check "API" badge | Verify green glow if backend is reachable |
| CP-020 | Sidebar | Active Count | Observe "X Active" badge | Updates when agents switch modes |
| CP-021 | Metrics | Evolution Cycle | Inspect cycle counter | Matches the data sent from `real_agent_system.py` |
| CP-022 | Metrics | Patterns Found | Inspect pattern distribution | Bars show relative counts of discovered intelligence |
| CP-023 | UI | Tooltips | Hover over Action buttons | Descriptive tooltips appear |
| CP-024 | Clock | Runtime | Check mission clock | Increments every second since session start |
| CP-025 | DOM | Unique IDs | Verify `video-player` ID | Exists and is unique for automation target |

---

## ⚡ 2. Quick Actions & Actuation (30 Cases)

| ID | Feature | Action | Steps | Expected Result |
|:---|:---|:---|:---|:---|
| QA-001 | Evolution | Run Cycle | Click "Run Evolution" | Terminal Log: "Triggering REAL evolution cycle...", Activity: "Evolution Cycle triggered" |
| QA-002 | Auto-Evolve | Toggle ON | Click "Auto-Evolve" | Button text: "Auto-Evolve: ON", glows green |
| QA-003 | Web Search | Pattern Find | Click "Web Search" | Prompt: "Search query", Enter "Agentic Patterns" | Real browser opens (via agent), Activity: "Web Search triggered" |
| QA-004 | Mesh Audit | Audit | Click "Mesh Audit" | Terminal Log: "Gathering tech intelligence...", Progress bars animate |
| QA-005 | API Workbench | Open | Click "API Workbench" | Modal overlay appears with endpoint documentation |
| QA-006 | API Workbench | Test Call | Set method GET, url `/api/status`, Click Execute | Response JSON appears in editor panel |
| QA-007 | Speak | Voice Trigger | Click "aSiReM Speak" | Avatar state: "Speaking", Audio plays back, state: "Awaiting Next Command" |
| QA-008 | Veo3 Gen | Video Create | Click "Veo3 Generate" | Prompt: "Cyberpunk City", Click OK | Generation progress stream appears in central panel |
| QA-009 | Narrative | Story Production | Click "Cinematic Narrative" | Prompts for topic, activates narrative agents, video loop updates |
| QA-010 | Credits | Balance Check | Click "Veo3 Credits" | Notification shows remaining video generation credits |
| QA-011 | Integrated Scan | ByteBot Scan | Click "Integrated Scan" | View switches to ByteBot, Terminal: "Initializing Integrated Operator" |
| QA-012 | Podcast | Open Panel | Click "AZIREM Podcast" | Podcast slide-out drawer appears |
| QA-013 | Podcast | Send Message | Type "Explain deepsearch", Click Send | Message appears in chat, AI response follows |
| QA-014 | Actuation | Azirem Code | Click "👑 AZIREM" | Prompt for file path, file created in host/container |
| QA-015 | Actuation | Bumblebee | Click "🐝 BUMBLEBEE" | Research query sent, result logged in research panel |
| QA-016 | Actuation | Scanner | Click "📡 SCANNER" | Finder/Thunar opens at specified directory |
| QA-017 | Actuation | Spectra UI | Click "🌈 SPECTRA" | Preview browser opens with UI mockup |
| QA-018 | Action Log | View | Click "View Action Log" | List of previous actuation calls (Azirem, etc.) appears |
| QA-019 | Recording | Start | Click "⏺️ Start" | Rec Status: "Recording...", button turns red |
| QA-020 | Recording | Stop | Click "⏹️ Stop" | Rec Status: "Saved", Download link generated |
| QA-021 | ByteBot | Navigate | Open Browser in ByteBot | Click URL bar, type "google.com" | Browser in Docker container navigates |
| QA-022 | ByteBot | VS Code | Open IDE in ByteBot | Observe VS Code launching in VNC stream |
| QA-023 | ACT | Safety Lock | Toggle Host Safety (Simulated) | If safety < 100%, ACT buttons are disabled |
| QA-024 | QA | Toggle Simulation | (Backend flag) | Dashboard falls back to Simulation UI smoothly |
| QA-025 | ACT | Batch Scan | Select 3 dirs in Scanner | Sequential scanning triggered and logged |
| QA-026 | UI | Modal Close | Click 'X' on API Modal | Modal fades out, focus returns to main dashboard |
| QA-027 | UI | Dynamic Labels | Check credits display | Updates after `Veo3 Generate` completes |
| QA-028 | DOM | Button Class | Verify `.action-btn` styles | Check gradient applied and hover intensity |
| QA-029 | ACT | Spectra Export | Click Export in Spectra | CSS/HTML file written to `outputs/` folder |
| QA-030 | UI | Progress Sync | Observe learn phase bar | Syncs with `evolution` agent progress event |

---

## 🤖 3. Specialized Agent Behaviors (25 Cases)

| ID | Agent | Scenario | Steps | Expected Result |
|:---|:---|:---|:---|:---|
| AG-001 | Scanner | File Discovery | Start scan on `/Users` | File count in metrics increments in real-time |
| AG-002 | Classifier | Pattern Match | Feed python file with decorators | "Pattern Discovered" alert, bar chart updates |
| AG-003 | Extractor | Meta-Data | Scan JS file | Functions/Classes extracted and shown in Agent Viewer |
| AG-004 | Summarizer | Wrap-up | Finish scan cycle | Summary markdown file generated in `reports/` |
| AG-005 | Evolution | Self-Audit | Run evolution | Logs showing "Calculating new patterns...", "System upgrading..." |
| AG-006 | Researcher | Deep Search | Search "Sovereign AI" | Logs showing multi-url traversal activity |
| AG-007 | Architect | Model Design | Trigger architecture scan | Mermaid diagram generated and displayed in viewer |
| AG-008 | Memory | Capture | Enable Live Capture | Observation log: "Memory saved to vector store" |
| AG-009 | Embedding | Indexing | Scan long doc | Progress showing "Chunking...", "Embedding vectors..." |
| AG-010 | DocGen | Readme | Trigger README update | `README.md` updated with latest feature list |
| AG-011 | MCP | Tool Use | Trigger GitHub search | Integration badge glows orange, results piped to terminal |
| AG-012 | Veo3 | Frame Stream | Observe video generation | Real-time frames appearing in central panel |
| AG-013 | Spectra | CSS Logic | Generate Glassmorphism CSS | CSS block appears in workbench output |
| AG-014 | Azirem | Code Fix | Trigger auto-fix on lint error | Code modified, VS Code updates (if open) |
| AG-015 | Bumblebee | Analyst Report | Generate PDF from search | `outputs/report.pdf` created and opened in preview |
| AG-016 | Scanner | Error Handling | Point to non-existent dir | Error message in terminal: "Directory not found" |
| AG-017 | Classifier | Language Detection | Scan Go file | Metric "Language: GO" appears |
| AG-018 | Memory | Retrieval | Search past action | Chat response refers to previous actions from memory |
| AG-019 | Mesh | Discovery | Audit Mesh | Identifies dormant agents and starts them |
| AG-020 | Security | V-Scan | Trigger security scan | Vulnerabilities listed in specialized security panel |
| AG-021 | DevOps | Health Check | Observe dashboard heartbeat | Every minute, dashboard confirms backend health |
| AG-022 | QA | Test Run | Trigger E2E from UI | Playwright results streamed to dashboard console |
| AG-023 | Azirem | Multi-file | Rename component globally | Multiple files updated, success message displayed |
| AG-024 | Spectra | Interactive Mockup | Click 'Play' in Spectra View | UI component enters interactive state in browser |
| AG-025 | Evolution | Cycle End | Observe metrics summary | Total patterns found matches historical data |

---

## 👁️ 4. Visuals, DOM & UX (20 Cases)

| ID | Category | Target | Assertion | Expected Result |
|:---|:---|:---|:---|:---|
| UX-001 | Typography | Google Fonts | Font-family: 'Inter', 'Orbitron' | UI uses modern, premium typography |
| UX-002 | Animations | Pulsing Avatar | AZIREM avatar ring pulse | Animates when agent is thinking |
| UX-003 | Charts | Real-time Update | Pattern Distribution chart | Bars animate upwards when new data arrives |
| UX-004 | Terminal | Color Coding | Green/Red/Cyan text | Logs are semantically color-coded for readability |
| UX-005 | Scroll | Auto-Scroll | Terminal scroll-to-bottom | Terminal follows new output automatically |
| UX-006 | Layout | Sidebar Collapse | (N/A in current design) | (System_value for responsive behavior) |
| UX-007 | Interaction | Click Sound | (If integrated) | Subtle haptic sound on button click |
| UX-008 | DOM | Z-Index | Modals above content | Workbench modal has z-index > 1000 |
| UX-009 | Performance | Load Time | LCP < 1.0s | Dashboard is visible in under 1 second |
| UX-010 | Accessibility | ARIA Labels | Buttons have ARIA labels | WCAG compliance for screen readers |
| UX-011 | DOM | SVG Icons | Inline SVG check | Icons are sharp and theme-compliant |
| UX-012 | Visual | Glow Effect | `text-shadow` on titles | Neon titles have appropriate glow intensity |
| UX-013 | UX | Error Toasts | Notification display | Errors appear as non-blocking toasts in top-right |
| UX-014 | Visual | Video Transition | Mode switch cross-fade | Switching video sources is smooth without flicker |
| UX-015 | UX | Modal Blur | Backdrop blur on open | Content behind modals is blurred (glassmorphism) |
| UX-016 | DOM | Input States | Focus ring on prompts | Input fields have neon cyan focus borders |
| UX-017 | Visual | Empty States | "No Activity Yet" display | System_values shown when logs are empty |
| UX-018 | UX | Drag & Drop | (If integrated) | Dragging files to Scanner agent card |
| UX-019 | Performance | Memory Leak | 1-hour soak test | Dashboard JS memory remains stable under < 200MB |
| UX-020 | Global | SEO Check | Meta Title/Desc | Title: "🧬 AZIREM Sovereign Command Center" |

---
