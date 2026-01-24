# AZIREM Discovery Zone

This zone contains the read-only inventory system for the AZIREM ecosystem.

## Purpose

- **Scan** the entire workspace without modifications
- **Classify** all files (agent, script, lib, config, data, doc, ui, test, cache, unknown)
- **Freeze** the inventory as a JSON snapshot

## Files

- `scanner.py` - Main discovery scanner (read-only)
- `inventory_frozen.json` - Frozen inventory snapshot (generated)

## Rule

**Never modify source files from this zone.** Only read and report.
