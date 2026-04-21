---
name: remotion-best-practices
description: Domain-specific knowledge base for building programmatic videos with Remotion and React
version: 1.0.0
source: https://skills.sh/remotion-dev/skills/remotion-best-practices
install: npx skills add https://github.com/remotion-dev/skills --skill remotion-best-practices
---

# Remotion Best Practices Skill

## Overview
Comprehensive guide for building programmatic videos using Remotion and React. Covers animations, audio, assets, 3D content, charts, text, transitions, and composition management.

## Installation (when npx available)
```bash
npx skills add https://github.com/remotion-dev/skills --skill remotion-best-practices
```

## Core Principles

### Project Setup
- Use `npx create-video@latest` to scaffold projects
- Configure `remotion.config.ts` for custom webpack/bundler settings
- Use `<Composition>` to register video components with metadata

### Animations & Timing
- Use `useCurrentFrame()` and `useVideoConfig()` hooks
- `interpolate()` for smooth value transitions between frames
- `spring()` for physics-based animations
- Always define `extrapolateLeft` and `extrapolateRight` to prevent value overflow

### Audio
- Use `<Audio>` component for background music and sound effects
- `useAudioData()` + `visualizeAudio()` for audio visualization
- Sync audio events to specific frames using `startFrom` prop

### Text & Captions
- Use `@remotion/google-fonts` for web fonts
- `measureText()` for dynamic text sizing
- `<CaptionedVideo>` for subtitle overlays

### Transitions
- `<TransitionSeries>` for sequencing scenes with transitions
- Built-in: fade, slide, wipe, clock wipe, flip
- Custom transitions via `presentationEffect()`

### 3D Content
- `@remotion/three` for Three.js integration
- Use `<ThreeCanvas>` as the 3D rendering surface
- Animate 3D objects using Remotion's frame-based system

### Performance
- Use `calculateMetadata()` for dynamic duration/fps
- `delayRender()` / `continueRender()` for async operations
- `prefetch()` for preloading assets

### Rendering
- CLI: `npx remotion render src/index.ts CompositionId out.mp4`
- Lambda: `@remotion/lambda` for serverless rendering
- Cloud Run: `@remotion/cloudrun` for Google Cloud

## When to Use
- Building programmatic video content with React
- Creating data-driven video animations
- Generating video templates with dynamic content
- Audio visualization projects
- Automated video production pipelines

## Key Dependencies
- remotion (core)
- @remotion/cli (rendering)
- @remotion/player (preview)
- @remotion/three (3D)
- @remotion/google-fonts
- @remotion/lambda / @remotion/cloudrun (cloud rendering)
