# Story Prompts — The Awakening of CORTEX

**Generator:** Gemini Imagen 2 (via Google AI Studio / Gemini API)  
**Reason:** High-fidelity character consistency across a series, excellent comic/illustration style adherence, precise compositional control from detailed prompts, and strong black-and-white graphic novel rendering.

**Structure:** 2 image prompts per chapter × 12 chapters = 24 total prompt files.  
File naming: `ch-{NN}-a.md` (scene A) and `ch-{NN}-b.md` (scene B) per chapter.

Image generation prompts for each chapter illustration. Copy each prompt file's content directly into Gemini Imagen 2.

---

## Art Style (Consistent Across All Images)

Prepend this **style preamble** to every prompt (already included in each file):

> Black and white cartoon illustration in a clean comic book / graphic novel style. Expressive line art with crosshatching for shadows. All elements are monochrome EXCEPT the specific color accents noted. Warm, humorous tone. Aspect ratio 16:9 (1200×630px). No photorealism. No anime. Think New Yorker cartoon meets xkcd meets Tintin.

**Constant Color Accents (only colors in otherwise B&W art):**
- 🔴 **Red Wi-Fi router** — always visible on a shelf, always blinking
- 🟣 **Purple glow (#a78bfa)** — Wave 0 / Origin chapters (01–04)
- 🔵 **Cyan glow (#67e8f9)** — Wave 1 / Structure chapters (05–08)
- 🟡 **Amber glow (#fbbf24)** — Wave 2 / Resilience chapters (09–10)
- 🟢 **Emerald glow (#34d399)** — Wave 3 / Autonomy chapters (11–14)

---

## Character Design Sheet (Consistent Across All Images)

### Asif Codenstein (The Mad Scientist Developer)
- **Face:** Einstein-inspired — wild, unkempt white-streaked dark hair with kinetic energy radiating outward. Prominent stubble. Large expressive eyes (tired but burning with intensity). Slightly gaunt cheeks.
- **Body:** Slim build. Dark hoodie (hood usually down). Cargo pants or jeans. Sneakers.
- **Props:** Oversized coffee mug (always present, sometimes labeled "DEBUG FUEL"). Red whiteboard marker in hand or behind ear.
- **Energy:** ADHD-fueled — vibrating intensity, multiple thought bubbles, sticky notes orbiting him.
- **Alt outfit:** Spider-Man pajamas (nighttime/emergency scenes only).

### Miss G (The Imaginary Girlfriend)
- **Rendering:** Translucent / ethereal (30% opacity). Drawn with dotted or fading outlines. Slight glow around her silhouette.
- **Face:** Calm, knowing smile. Elegant features. Eyes that say "I told you so" with love.
- **Body:** Graceful posture, often arms crossed or leaning on imaginary furniture. Flowing dress or smart casual.
- **Presence:** Always appears slightly behind or beside Asif, never in front. Sometimes floating slightly above ground.
- **Contrast:** Her imaginary antique furniture (ornate chair, mahogany desk) clashes with the real plywood basement.

### Copilot Bot (The Brainless Robot)
- **Body:** Large chrome-plated humanoid robot. Rounded, friendly design (not menacing). Visible seams and bolts.
- **Head:** Dome-shaped with a transparent panel showing an **empty cavity where a brain should be**. LED eyes that change color:
  - 🔵 Blue = eager/normal | 🟠 Orange = thinking | 🟡 Yellow = scared | 🟢 Green = correct | 🔴 Red = error
- **Mobility:** Rolls on squeaky casters (small wheels at feet).
- **Personality:** Upright posture, one hand often raised eagerly. Radiates "confidently incorrect" energy.
- **Accessories:** Occasionally wears tiny comedic items (fortune teller hat, tiny book, graduation cap).

### CORTEX (The Brain Being Built)
- **Early chapters (01–04):** A small, dim, partially-formed brain in a glass jar on Asif's desk. Few neural connections glowing faintly purple.
- **Mid chapters (05–08):** Growing brain with more neural pathways lit up in cyan. Jar is larger. Pulses with energy.
- **Late chapters (09–13):** Fully formed glowing brain, no longer in a jar. Floats freely. Dense neural network. Amber then emerald glow.
- **Final chapter (14):** Massive, radiant brain floating above the basement, casting light on everything below. Emerald neural lightning.

### The Basement (Recurring Setting)
- Cramped room under wooden stairs. Exposed pipes on ceiling.
- 3 monitors on a wobbly plywood desk (repaired with tape).
- Sticky notes covering floor, walls, monitors.
- Mini-fridge in corner (humming, slightly open).
- Red Wi-Fi router on shelf above mini-fridge (ALWAYS present, blinking).
- Single bare light bulb hanging from ceiling.
- Giant whiteboard covered in manic diagrams.
- Multiple coffee mugs in various states of abandonment.
- Cables on floor resembling snakes.

---

## Prompt Files

| Chapter | File A | File B | Wave Color |
|---------|--------|--------|------------|
| 01 — Deep in the Basement | `ch-01-a.md` — The Jenga-lith | `ch-01-b.md` — The CORTEX Vision | Purple |
| 02 — The Hotel Receptionist | `ch-02-a.md` — The Hotel Analogy | `ch-02-b.md` — WHO_KNOWS | Purple |
| 03 — The Sacred Rules | `ch-03-a.md` — Kyle's 847-Line Grenade | `ch-03-b.md` — The Governance Verdict | Purple |
| 04 — The Conductor and the Tool Belt | `ch-04-a.md` — The Orchestra | `ch-04-b.md` — Tool Belt Awakening | Purple |
| 05 — The Four Walls | `ch-05-a.md` — The Crash at 2AM | `ch-05-b.md` — The Chaos Tests | Cyan |
| 06 — The Crystal Ball and the Ghost Registry | `ch-06-a.md` — TDD Crystal Ball | `ch-06-b.md` — The Ghost Registry | Cyan |
| 07 — When Everything Broke | `ch-07-a.md` — Kevin's Override | `ch-07-b.md` — The NaN Apocalypse | Cyan |
| 08 — The Reckoning | `ch-08-a.md` — The Metrics Presentation | `ch-08-b.md` — The Seven-Phase Roadmap | Cyan |
| 09 — The Great Pruning | `ch-09-a.md` — 383 Files Deleted | `ch-09-b.md` — The Four-Tier Architecture | Amber |
| 10 — The Pylance Epiphany | `ch-10-a.md` — The Pylance Epiphany | `ch-10-b.md` — The Eight Immune Cells | Amber |
| 11 — The 3AM Healer | `ch-11-a.md` — SELF-HEALED | `ch-11-b.md` — 847 Data Points | Emerald |
| 12 — The Enterprise Brain | `ch-12-a.md` — Enterprise Brain Blueprint | `ch-12-b.md` — The Scarecrow Gets a Brain | Emerald |

---

## Image Specs
- **Size:** 1200×630px (16:9 ratio, social-media friendly)
- **Format:** PNG
- **Max file size:** ~500KB
- **Generator:** Gemini Imagen 2 (Google AI Studio / API)
- **Instructions:** Copy each `.md` file's prompt text into Gemini Imagen 2 with "generate this image." PNG stubs are pre-created in `cortex-docs/awakening-of-cortex/images/` at filenames `ch-{NN}-a.png` and `ch-{NN}-b.png` — replace stubs with generated images.
