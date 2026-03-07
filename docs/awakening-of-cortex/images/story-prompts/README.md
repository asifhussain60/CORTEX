# Story Prompts — The Awakening of CORTEX

**Generator:** Gemini Imagen 2 (via Google AI Studio / Gemini API)  
**Reason:** High-fidelity character consistency across a series, excellent comic/illustration style adherence, precise compositional control from detailed prompts, and strong black-and-white graphic novel rendering.

**Structure:** 2–3 image prompts per chapter × 12 chapters = 28 total prompt files.  
File naming: `ch-{NN}-a.md` (scene A), `ch-{NN}-b.md` (scene B), `ch-{NN}-c.md` (scene C — stability-anchored supplementary scene, chapters 09–12 only).

**Stability policy:** `-c` prompts are written to survive CORTEX evolution — they anchor to character comedy moments and permanent metaphors, never to capability counts or numbers that will grow.

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
- **Age & build:** 54 years old — youthful-looking and enthusiastic, a bit on the plump side. Round full cheeks, a soft belly just visible under the hoodie, the lovably round silhouette of a man who eats takeaway at 2AM and calls it field research. Not fat — plump, cherub-round, cartoon-endearing.
- **Face:** Einstein-meets-Chaplin inspired — wild, explosively unkempt white-streaked dark hair radiating in every direction as if each strand has its own opinion. Huge round thick-rimmed glasses (always slightly askew). Prominent stubble. Eyes comically large — perpetually wide, ranging from manic terror to unhinged glee. A slightly too-wide grin that appears in moments of eureka. Round, full cheeks — the face of someone well-fed on enthusiasm and instant noodles.
- **Body:** Plump but not fat — soft round belly, full cheeks, slightly chubby hands. The body of someone whose entire exercise regime is sprinting to the whiteboard. Arms seem marginally too short for the enthusiasm he puts into gestures. Perpetually wrinkled, slightly mismatched clothing.
- **Comedy physics:** Asif obeys exaggerated cartoon physics. His hair responds to emotional state — frizzier when panicked, slightly more organized when focused. Multiple thought bubbles orbit him at once. Sticky notes spontaneously appear on his clothing. His coffee mug is always in a precarious state (tipping, empty, growing mold, shattering, being used as a hat). He regularly drops things at the wrong moment.
- **Specific comedic markers:** (a) his glasses are ALWAYS slightly crooked; (b) there is ALWAYS at least one sticky note attached to him that he doesn't know about; (c) his chair is visibly held together with duct tape and optimism; (d) his shoe is sometimes untied; (e) his hoodie often has a badge, sticker, or previous coffee spill on it.
- **Props:** Oversized "DEBUG FUEL" mug (chipped, labeled in Sharpie). Red whiteboard marker perpetually behind his ear or gripped like a weapon. Stack of sticky notes always losing battle with gravity.
- **Energy:** ADHD-fueled chaos incarnate — vibrating intensity, multiple thought bubbles colliding with each other, sticky notes orbiting him, at least one leg bouncing even when seated.
- **Alt outfit:** Spider-Man pajamas (nighttime/emergency scenes only) — these should have an obvious small tear at the knee and be visibly too short at the ankles.

### Miss G (The Imaginary Girlfriend)
- **Rendering:** Semi-translucent like frosted starlight — fully readable and visually prominent despite her translucency; features and form are crisp and clear, not faded. Drawn with a **solid, bold outline** in the wave's accent color (purple `#a78bfa` in the Origin wave; shifts to cyan, amber, emerald, violet in later waves), same line weight as other characters. A visible glow-halo in the matching accent color emanates from within her silhouette to signal "imaginary." She floats very slightly above the floor.
- **Face (CANONICAL — IDENTICAL ACROSS ALL PROMPTS):** Indian-Asian beauty — warm honey-brown skin, wide luminous dark eyes with a natural double lid, softly arched expressive brows, a delicately rounded nose with a slight upturn, full defined lips with a cupid's bow, a gentle heart-shaped face with soft cheekbones. Expression is kind, gentle, and loving — the face of someone who has infinite patience and infinite warmth. This face NEVER changes across any chapter.
- **Hair (CANONICAL):** Naturally curly, voluminous, thick black hair falling to just below shoulder length — the curls are lush, defined ringlets with body and bounce. Never straight, never in a high ponytail. Loose strands and curls frame her face softly. Hair may be styled differently per image (see per-chapter costume notes) but the curl texture and below-shoulder length NEVER change.
- **Figure:** Petite height (notably shorter than Asif), curvy and feminine — soft curves, a defined waist, a graceful silhouette. Her posture is always upright and confident despite her small stature.
- **Costume:** VARIES PER IMAGE — each image she wears a modestly styled, fashion-forward outfit inspired by a different country's traditional or contemporary dress. Always elegant, always stylishly modest (no bare midriff, no revealing cuts), always rendered in the wave's accent-color glow with the semi-translucent frosted-starlight quality. See per-chapter costume specifications below.
- **Body:** Graceful, confident posture — arms crossed, or one hand on hip, or leaning elegantly on imaginary antique furniture. Never hunched.
- **Presence:** Placed as a **named mid-frame or second-tier character** — prominent enough to register immediately. Never cropped, never tucked into far corners at near-invisible levels.
- **Contrast:** Her imaginary antique furniture (ornate chair, mahogany desk) clashes beautifully with the real plywood basement. She is always the most visually elegant element in the frame.

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

| Chapter | File A | File B | File C (Stable) | Wave Color |
|---------|--------|--------|-----------------|------------|
| 01 — Deep in the Basement | `ch-01-a.md` — The Jenga-lith | `ch-01-b.md` — The CORTEX Vision | — | Purple |
| 02 — The Hotel Receptionist | `ch-02-a.md` — The Hotel Analogy | `ch-02-b.md` — WHO_KNOWS | — | Purple |
| 03 — The Sacred Rules | `ch-03-a.md` — Kyle's 847-Line Grenade | `ch-03-b.md` — The Governance Verdict | — | Purple |
| 04 — The Conductor and the Tool Belt | `ch-04-a.md` — The Orchestra | `ch-04-b.md` — Tool Belt Awakening | — | Purple |
| 05 — The Four Walls | `ch-05-a.md` — The Crash at 2AM | `ch-05-b.md` — The Chaos Tests | — | Cyan |
| 06 — The Crystal Ball and the Ghost Registry | `ch-06-a.md` — TDD Crystal Ball | `ch-06-b.md` — The Ghost Registry | — | Cyan |
| 07 — When Everything Broke | `ch-07-a.md` — Kevin's Override | `ch-07-b.md` — The NaN Apocalypse | — | Cyan |
| 08 — The Reckoning | `ch-08-a.md` — The Metrics Presentation | `ch-08-b.md` — The Seven-Phase Roadmap | — | Cyan |
| 09 — The Great Pruning | `ch-09-a.md` — 383 Files Deleted | `ch-09-b.md` — The Four-Tier Architecture | `ch-09-c.md` — The Janitor Volunteers ✅ | Amber |
| 10 — The Pylance Epiphany | `ch-10-a.md` — The Pylance Epiphany | `ch-10-b.md` — The Eight Immune Cells | `ch-10-c.md` — The Race Condition ✅ | Amber |
| 11 — The 3AM Healer | `ch-11-a.md` — SELF-HEALED | `ch-11-b.md` — 847 Data Points | `ch-11-c.md` — Gold Stars and Quarantine ✅ | Emerald |
| 12 — The Enterprise Brain | `ch-12-a.md` — Enterprise Brain Blueprint | `ch-12-b.md` — The Scarecrow Gets a Brain | `ch-12-c.md` — Receptionists All the Way Down ✅ | Violet |

---

## Miss G — Per-Chapter Costume & Hair Reference

| File | Country Inspiration | Outfit | Hair Style |
|------|--------------------|---------|----|
| `ch-01-a.md` | 🇮🇳 India | Anarkali suit with dupatta | Loose free ringlets |
| `ch-01-b.md` | 🇯🇵 Japan | Kimono-cut coat-dress with obi sash | Loose curly half-updo with purple ribbon |
| `ch-02-a.md` | 🇬🇭 West Africa (Kente) | Kente-inspired wrap dress with headband | Side-swept cascade of ringlets |
| `ch-02-b.md` | 🇲🇦 Morocco | Embroidered kaftan with passementerie trim | Double low buns with curly wisps |
| `ch-03-a.md` | 🇰🇷 South Korea | Modern Hanbok jeogori + chima | Crown braid halo with free ringlets |
| `ch-03-b.md` | 🇹🇷 Turkey | Ottoman-style entari coat-dress with sash | Loose romantic chignon with tendrils |
| `ch-04-a.md` | 🇪🇹 Ethiopia | Habesha kemis with embroidered netela wrap | High curly puff with ribbon |
| `ch-04-b.md` | 🇵🇪 Peru | Embroidered huipil blouse + tiered pollera skirt + manta | Deep side-part all-one-side waterfall |
| `ch-05-a.md` | 🇳🇬 Nigeria | Aso-oke buba + gele + iro | Floating overhead halo of ringlets |
| `ch-05-b.md` | 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | Tartan pinafore dress over fitted top | Windswept alarm ringlets |
| `ch-06-a.md` | 🇮🇳 India (Mysore silk saree) | Nivi-style saree with fitted blouse | Starburst pins with free ringlets below |
| `ch-06-b.md` | 🇨🇳 China | Classic fitted qipao (cheongsam) | Structured twisted updo with decorative clip |
| `ch-07-a.md` | 🇮🇩 Indonesia | Batik kebaya blouse + sarong batik skirt | Low side-swept ringlet cluster |
| `ch-07-b.md` | 🇮🇷 Iran | Long tunic-coat with geometric embroidery + wide trousers | Braided half-back with free ringlets |
| `ch-08-a.md` | 🇪🇸 Spain | Flamenco-inspired fitted bodice with ruffled hem | Loose gathered cascade with face-framing ringlets |
| `ch-08-b.md` | 🇬🇷 Greece | Modernised Grecian single-shoulder draped dress | Completely free loose natural ringlets |
| `ch-09-a.md` | 🇲🇽 Mexico | Tehuana huipil + enagua skirt + woven sash | Low ponytail of curly mass with tendrils |
| `ch-09-b.md` | 🇧🇷 Brazil | Festa Junina floral midi dress with eyelet trim | French braids merging into ringlet cascade |
| `ch-09-c.md` | 🇲🇦 Morocco | Embroidered mid-length caftan with woven sash | Side-swept ringlets gathered loosely to one side |
| `ch-10-a.md` | 🇸🇪 Sweden | Modernised folk dress with embroidered apron panel | High pompadour roll with loose ringlets below |
| `ch-10-b.md` | 🇮🇳 India (Lucknow chikankari) | Chikankari Anarkali with stole | Full loose twist-out wide halo |
| `ch-10-c.md` | 🇯🇵 Japan | Modernised kimono silhouette with obi sash | Sleek low bun with face-framing escaped ringlets |
| `ch-11-a.md` | 🇵🇰 Pakistan | Phulkari kameez shalwar with dupatta | Completely free nocturnal ringlets |
| `ch-11-b.md` | 🇵🇹 Portugal | Viana embroidered skirt + blouse + velvet jacket + apron | Big bouncy exuberant free ringlets with flower pin |
| `ch-11-c.md` | 🇳🇬 Nigeria | Ankara print midi skirt + peplum top + head wrap | Relaxed two-strand twist-out loose spirals |
| `ch-12-a.md` | 🇮🇳 India (Rajasthani lehenga) | Full zardozi lehenga choli with dupatta | Grand Frohawk curly updo |
| `ch-12-b.md` | 🇱🇧 Lebanon | Floor-length jewel-tone kaftan with bell sleeves | Maximum-volume free halo ringlets |
| `ch-12-c.md` | 🇹🇷 Turkey | Long Ottoman-style embroidered tunic dress with woven belt | Stacked half-up voluminous curls with free ringlets below |

---

## Generator Note — Gemini Pro Upgrade

**Recommended generator:** Gemini Imagen 3 (Gemini Pro / Google AI Studio Pro tier) for enhanced:
- **Character consistency** — seed-based character anchoring for Miss G's face across all 24 prompts
- **Fine detail rendering** — embroidery patterns, ringlet curl texture, translucency effects
- **Cinematic composition** — improved crosshatching and tonal range in the B&W/accent-color style
- **Prompt fidelity** — longer prompt adherence for complex multi-character scenes

**Workflow:** Use Google AI Studio Pro → Imagen 3 → paste each prompt file's `## Prompt` section verbatim. For cross-image character consistency, use the "Reference image" feature with a seed character sheet generated from `ch-01-a.md` as the canonical Miss G reference.

---

## Image Specs
- **Size:** 1200×630px (16:9 ratio, social-media friendly)
- **Format:** PNG
- **Max file size:** ~500KB
- **Generator:** Gemini Imagen 2 (Google AI Studio / API)
- **Instructions:** Copy each `.md` file's prompt text into Gemini Imagen 2 with "generate this image." PNG stubs are pre-created in `cortex-docs/awakening-of-cortex/images/` at filenames `ch-{NN}-a.png` and `ch-{NN}-b.png` — replace stubs with generated images.
