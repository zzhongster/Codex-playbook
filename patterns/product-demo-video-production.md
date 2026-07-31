# Product Demo Video Production

## Context

When producing SaaS product operation videos, raw screen recordings alone often look unpolished, while screenshot-only videos fail to show real product behavior. A reliable workflow is to combine clean real recordings with a designed composition layer for layout, highlights, subtitles, voice, and timing control.

## Pattern

Use a two-layer production model:

1. Record clean product clips with Playwright/Chrome.
2. Keep login pages, loading waits, and debug overlays out of the usable clip range.
3. Record separate clips for action states and stable result states.
4. Build the final presentation in Remotion or an equivalent composition tool.
5. Add highlights, zooms, badges, captions, and timing adjustments in the composition layer, not in the raw recording.
6. Lock narration once the script is stable, then match visual pacing to the voice if the voice length is approved.
7. Extract keyframes at user-reported timestamps and inspect them before returning the revised video.

For designed explanation pages, use staged motion rather than static slides: reveal titles, cards, keyword chips, feature buttons, and process nodes in the order the narration introduces them. This makes the video feel closer to a polished product launch or Keynote presentation while preserving clarity.

## Why It Works

Clean recordings keep product evidence authentic and reusable. Composition-layer highlights make visual corrections cheap because bad highlight positions do not require re-recording. Stable-state clips prevent repeated operations and avoid flicker when the narration is explaining results rather than interactions.

## Quality Gates

- Copy should not be covered by video.
- Result-table proof should use stable table clips.
- Highlights should be overlaid after recording and checked by timestamped keyframes.
- Static design pages should have subtle staged reveals and follow the voiceover order.
- Voice scene changes should happen at or before the spoken topic shift.
- Subtitles should not obscure the UI being demonstrated.
- Credentials and TTS/API keys must stay local and never appear in outputs.

## Reusable Skill

The local Codex skill is available at:

```text
/Users/zhangzhong/.agents/skills/product-demo-video-production
```
