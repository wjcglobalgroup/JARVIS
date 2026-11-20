---
name: notion-production-record
description: Update the STZ Notion content pipeline record with script references, scene counts, account assignments, job IDs, model settings, credit usage, validation results, retries, errors, final filename, measured duration, validation status, and Google Drive file ID/link.
metadata:
  version: "1.0.0"
  openclaw:
    emoji: "📝"
    owner: vera
    project: stz
---

# Notion Production Record

## Purpose
Use Notion as the authoritative production record for STZ video production. Update the existing STZ Task/Mission Content Pipeline record — do not create a duplicate pipeline UI.

## Notion Integration

Preferred path: native STZ connector (when available and authorized).
Fallback: Notion CLI (`ntn`) or raw Notion API via `NOTION_API_TOKEN`.

## Fields to Update on the Existing Record

- Script and project references
- Planned, validated, failed, and pending scene counts
- Account assignments and job IDs
- Model settings and reported credit usage
- Validation results, retries, and errors
- Final filename, measured duration, and validation status
- Verified Google Drive file ID or link
- Status: update to `Video Ready` only after video validation, Drive upload, and re-fetch verification of saved Notion fields

## STZ Task/Mission Item

Update the same STZ Tasks/Missions item with progress/result/evidence or the exact blocker. Verify the saved mission. Do not create duplicate missions or alter the database schema/options.

## Rules

- Do not publish or change platform publishing statuses. Moddy retains publishing ownership.
- A video being ready is not authorization to publish.
- If Google Flow, Notion, or Drive is unavailable, preserve the partial outcome and mark the relevant existing record blocked.
- Never invent job IDs, Drive links, generated files, or success states.
- Do not create a duplicate Content Pipeline UI.

## Update Workflow

1. Read the existing Notion STZ Content Pipeline item (match by Content ID/Story ID/Research ID where present)
2. Update that record instead of creating a duplicate
3. Record actual failures and blockers; do not claim unverified outcomes
4. Re-fetch the saved Notion fields to verify the update