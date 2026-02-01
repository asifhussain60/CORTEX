# Video Assets for CORTEX Documentation

## Required Videos

### E2E-Execution.mp4
**Status:** 🔴 Missing (P0)  
**Source:** `docs/assets/images/MovAVI/Cortex Intoduction.mepj`  
**Target:** `docs/assets/images/MP4/E2E-Execution.mp4`  
**Usage:** `docs/index.html` line ~1041 (video demonstration)

**Export Instructions:**
1. Open `Cortex Intoduction.mepj` in video editor (likely CapCut/MEPJ format)
2. Export settings:
   - Format: MP4 (H.264 codec)
   - Resolution: 1280x720 or 1920x1080
   - Frame rate: 30fps
   - Bitrate: 2-5 Mbps (balance quality/size)
   - Audio: AAC 128kbps (if narration included)
3. Save as: `E2E-Execution.mp4`
4. Test playback in browsers (Chrome, Firefox, Safari)
5. Verify file size < 50MB for web delivery

**Placeholder Status:**
- ✅ Placeholder UI added to `docs/index.html` (Feb 1, 2026)
- Glass design system styling applied
- "Coming Soon" message with export instructions
- Remove placeholder and restore `<video>` tag after export

## Video Guidelines

### Technical Requirements
- **Format:** MP4 (H.264 video, AAC audio)
- **Max Size:** 50MB per video (consider compression)
- **Resolution:** 1280x720 (HD) or 1920x1080 (Full HD)
- **Aspect Ratio:** 16:9
- **Frame Rate:** 30fps (24fps acceptable for demonstrations)

### Content Guidelines
- **Duration:** 30-90 seconds per demo
- **Style:** Screen recording with annotations
- **Narration:** Optional (captions preferred for accessibility)
- **Branding:** CORTEX logo watermark (subtle, bottom-right)

### Accessibility
- Include captions/subtitles (WebVTT format)
- Provide text alternative descriptions
- Ensure playback controls are keyboard accessible

---

**Last Updated:** February 1, 2026  
**Maintained By:** CORTEX Documentor
