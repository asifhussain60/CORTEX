# Chapter Images

Place one image per chapter in this folder using the naming convention:

```
ch-01-prologue.png
ch-02-hotel-receptionist.png
ch-03-sacred-rules.png
ch-04-conductors-baton.png
ch-05-opening-doors.png
ch-06-four-walls.png
ch-07-crystal-ball.png
ch-08-battle-for-truth.png
ch-09-everything-broke.png
ch-10-reckoning.png
ch-11-great-pruning.png
ch-12-pylance-epiphany.png
ch-13-3am-healer.png
```

## Specs
- **Formats:** `.png`, `.jpg`, or `.webp`
- **Recommended size:** 1200×630px (2:1 ratio, social-media friendly)
- **Max file size:** ~500KB (optimize for web)
- **Displayed at:** full-width hero banner at the top of each chapter, max-height 400px, object-fit cover, with 16px border-radius and a subtle glow matching the chapter's wave color.

## Wave Color Map
| Wave | Color | Chapters |
|------|-------|----------|
| Origin (0) | `#a78bfa` purple | 01, 02, 03, 04 |
| Structure (1) | `#67e8f9` cyan | 05, 06, 07, 08 |
| Resilience (2) | `#fbbf24` amber | 09, 10 |
| Autonomy (3) | `#34d399` emerald | 11 |
| Vision (4) | `#8b5cf6` violet | 12 |

Images are loaded by `index.html` via the `image` field in the CHAPTERS array.
If no image file exists for a chapter, the hero banner is simply hidden.
