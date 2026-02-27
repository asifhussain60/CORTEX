# Story Prompts — The Awakening of CORTEX

**Generator:** DALL·E 3 (via ChatGPT / GPT-4o)  
**Reason:** Superior character consistency across a series, better comic/illustration style adherence, reliable text-on-object rendering, and precise compositional control from detailed prompts.

Image generation prompts for each chapter illustration. Copy each prompt file's content directly into DALL·E 3.

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

| Chapter | File | Wave Color |
|---------|------|------------|
| 01 — Deep in the Basement | `ch-01-prologue.md` | Purple |
| 02 — The Hotel Receptionist | `ch-02-hotel-receptionist.md` | Purple |
| 03 — The Sacred Rules | `ch-03-sacred-rules.md` | Purple |
| 04 — The Conductor's Baton | `ch-04-conductors-baton.md` | Purple |
| 05 — Opening the Doors | `ch-05-opening-doors.md` | Cyan |
| 06 — The Four Walls | `ch-06-four-walls.md` | Cyan |
| 07 — The Crystal Ball | `ch-07-crystal-ball.md` | Cyan |
| 08 — The Battle for Truth | `ch-08-battle-for-truth.md` | Cyan |
| 09 — When Everything Broke | `ch-09-everything-broke.md` | Amber |
| 10 — The Reckoning | `ch-10-reckoning.md` | Amber |
| 11 — The Great Pruning | `ch-11-great-pruning.md` | Emerald |
| 12 — The Pylance Epiphany | `ch-12-pylance-epiphany.md` | Emerald |
| 13 — The 3 AM Healer | `ch-13-3am-healer.md` | Emerald |
| 14 — The Enterprise Brain | `ch-14-enterprise-brain.md` | Emerald |

---

## Image Specs
- **Size:** 1200×630px (16:9 ratio, social-media friendly)
- **Format:** PNG
- **Max file size:** ~500KB
- **Generator:** DALL·E 3 (ChatGPT Plus / API)
- **Instructions:** Copy each `.md` file's DALL·E 3 prompt text into ChatGPT with "generate this image" or use the API with `model: "dall-e-3"`, `size: "1792x1024"` (closest 16:9 option), `quality: "hd"`.
