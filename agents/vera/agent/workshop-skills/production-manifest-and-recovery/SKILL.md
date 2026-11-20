---
name: production-manifest-and-recovery
description: Authoritative production manifest tracking all six scenes through the lifecycle PENDING → READY → GENERATING → GENERATED → DOWNLOADED → VALIDATING → VALIDATED, with FAILED and BLOCKED states. Handles retry limits, error recording, and recovery of unfinished work.
metadata:
  version: "2.0.0"
  openclaw:
    emoji: "📋"
    owner: vera
    project: stz
---

# Production Manifest and Recovery

## Purpose
The production manifest is the authoritative record of the scene queue and ordering. Tracks each scene through its full lifecycle, records all generation/download/validation details, and manages retries and recovery.

## Scene Lifecycle States

```
PENDING → READY → GENERATING → GENERATED → DOWNLOADED → VALIDATING → VALIDATED
```

Additional states: `FAILED`, `BLOCKED`

A scene is **not** successful merely because Flow accepted the request. A scene is `VALIDATED` only after:
1. Generation is complete
2. The file has been downloaded
3. The media can be opened
4. Expected duration and streams have been checked
5. Required visual checks have passed

## Production Manifest Structure

File: `production/manifests/production-manifest.json`

Top-level fields:
- `content_id`: string
- `date`: ISO date
- `research_source`: string
- `selected_topic`: string
- `category`: string
- `priority`: string
- `title`: string
- `hook`: string
- `total_scenes`: 6
- `target_duration_seconds`: 60
- `actual_duration_seconds`: number | null
- `scene_ids`: ["scene_001", ..., "scene_006"]
- `scenes`: array of scene records
- `account_assignments`: map of account → scene IDs
- `job_ids`: map of scene_id → job ID
- `credit_usage`: map of account → {used, remaining, verified}
- `validation_results`: map of scene_id → {visual, audio, technical}
- `final_video_path`: string | null
- `final_video_duration`: number | null
- `notion_record_id`: string | null
- `drive_file_id`: string | null
- `drive_url`: string | null
- `status`: "PENDING" | "IN_PROGRESS" | "BLOCKED" | "COMPLETED"
- `blockers`: array of {scene_id, reason, timestamp}
- `last_updated`: ISO timestamp

## Per-Scene Record Fields

- `project_id` and `scene_id`
- `sequence_number` (1–6)
- `expected_duration`
- `script_segment` and `narration_segment`
- `reference_image_path` and `prompt`
- `assigned_account`
- `generation_job_id`
- `model` and `settings`
- `estimated_credit_cost` and `reported_credit_cost`
- `generation_status`
- `local_output_path` and `actual_duration`
- `visual_validation_result`
- `audio_validation_result` (if applicable)
- `technical_media_validation_result`
- `retry_count`
- `error_details`
- `last_status_check_time`

## Retry Policy

- Retry only failed or invalid scenes within configured limits
- Inspect a timed-out job before resubmitting
- Preserve successful outputs; prevent duplicate generation
- Never regenerate a validated scene just because another account becomes available

## Recovery

- If credits are exhausted, preserve the current manifest and completed clips
- Continue only if another account is permitted and eligible
- Otherwise, leave affected scenes pending and report exactly what remains
- If no eligible account has sufficient free credits, preserve the unfinished scene queue and report the blocker

## Scene Count Tracking

Track: planned, validated, failed, pending scene counts. Update after each state change.