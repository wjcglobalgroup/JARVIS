---
name: google-flow-video-generation
description: Generate STZ short-form video scenes using Google Flow. Handles scene prompt construction, reference-image conditioning, job submission, model/duration selection, and per-scene job tracking. References the account manager for account selection and the production manifest for scene state tracking.
metadata:
  version: "2.0.0"
  openclaw:
    emoji: "🎬"
    owner: vera
    project: stz
---

# Google Flow Video Generation

## Purpose
Generate the six STZ short-form video scenes using Google Flow. Handles scene prompts, reference-image conditioning for the official presenter avatar, job submission, model/duration selection, and per-scene job tracking.

Account selection and credit checks are delegated to the Google Flow Account Manager. Scene state tracking and per-scene records are maintained in the Production Manifest.

## Target Production Standard

- 6 scenes × 10 seconds = approximately 60 seconds total
- Scene IDs: scene_001 through scene_006
- Vertical 9:16 portrait (1080×1920 where supported)
- MP4/H.264, 30 fps target
- Consistent seated PC podcast/vlogging presenter setup

## Scene Prompt Template

Each scene prompt must include:

1. **Scene number** and **target duration**
2. **Presenter identity**: same man, seated at computer workstation, podcast/vlogging setup
3. **Appearance**: black STZ hoodie with cyan accents (lining and drawstrings), glasses, consistent hairstyle and skin tone
4. **Environment**: professional crypto-education studio, cyan accent lighting, STZ branding
5. **Camera**: stable front-facing medium close-up or medium shot
6. **Action**: natural blinking, subtle head movement, restrained speaking gestures
7. **On-screen text**: concise, accurate, placed in safe areas
8. **Transition/pacing**: when useful

Do not:
- Replace the presenter
- Change clothing or hairstyle
- Remove glasses
- Move to unrelated location
- Turn into animated character

## Reference Image

Path: `assets/vera/avatar_reference.png`

## Reference Image Verification

Before using `assets/vera/avatar_reference.png` for reference-image conditioning:
1. Open or inspect the image to confirm it shows the correct STZ presenter (same man, glasses, consistent hairstyle and skin tone).
2. Confirm it is a presenter photo, not a logo badge, placeholder, or different person.
3. If the image is inaccessible, incorrect, or a logo badge, request the correct presenter photo from the user rather than substituting another person.

If the reference image is inaccessible, request it from the user rather than substituting another person.

## Model/Duration Verification

Before generating, verify:
- Whether the selected model supports 8-second clips
- The model's actual duration limits
- Adapt scene plan without falsely claiming each clip is 8 seconds

Report actual duration limits if the model doesn't support 8 seconds.

## Job Submission Workflow

1. Read the script and divide into 6 logical scenes
2. Create stable scene IDs (scene_001–scene_006)
3. For each scene:
   a. Select the assigned account using the Google Flow Account Manager (priority order; fall back only when the primary account cannot lawfully continue)
   b. Check the selected account's credit balance and eligibility via the account manager
   c. Verify model supports the target duration
   d. Perform dry-run cost check (must not submit a generation request)
   e. Submit generation job with reference image conditioning
   f. Record job ID, model, settings, estimated cost
   g. Record the job in the production manifest (scene state advances through the manifest lifecycle)
   h. Prevent duplicate submissions when an existing job is still active
   i. On failure, record error details and retry within configured limits

Per-scene records are maintained in the production manifest (`production-manifest-and-recovery` skill). Video generation references the manifest for scene state and field definitions rather than duplicating them.