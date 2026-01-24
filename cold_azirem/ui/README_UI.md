# ASIREM UI CENTRAL COMMAND

## Status: ✅ CENTRALIZED
**Date**: 2026-01-18
**Standard**: Antigravity UI v1

The UI ecosystem has been merged and centralize into this directory (`cold_azirem/ui`).
All disparate interfaces (`flux`, `landing`, `deployment`) have been gathered here and upgraded to use a unified design system.

## 📂 Structure
- `index.html`: **CENTRAL PORTAL** (New Entry Point) - Links to all interfaces.
- `asirem_flux_ui.html`: The Protocol dashboard (formerly `asirem_flux_ui.html` / `deployment`).
- `asirem_landing.html`: The Origin narrative page (formerly `asirem_landing.html`).
- `asirem_theme.css`: **The Single Source of Truth** for styles (Colors, Fonts, Glassmorphism).
- `asirem_ui.js`: Centralized logic (Cursors, Animations).

## 🚀 How to Run
We recommend serving this directory directly:
```bash
cd cold_azirem/ui
python3 -m http.server 8888
```

## 🎨 Design System
- **Fonts**: 'Outfit' (Body), 'Space Grotesk' (Headers/Tech)
- **Colors**:
  - `var(--bg-deep)`: Cosmic Background
  - `var(--neon-asirem)`: Cyan Accent (#00f0ff)
- **Components**:
  - `btn-flux`: Main interaction button
  - `card`: Glassmorphism panels

## ⚠️ Migration Notes
- Original files in `aSiReM/` root have been moved here.
- `deployment/` folder is now considered legacy/downstream. This directory is the new master.
