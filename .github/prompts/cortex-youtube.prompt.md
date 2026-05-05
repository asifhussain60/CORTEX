---
mode: agent
description: "Process downloaded YouTube files into a clean flat folder with Copilot-curated song titles. Usage: /cortex-youtube [source folder] [target folder]"
---

# CORTEX YouTube Processor

**You are the LLM.** No API key or external service needed -- Copilot reads filenames and curates clean song titles directly.

---

## Invocation

```
/cortex-youtube [source] [target]
```

| Argument | Default | Example |
|----------|---------|---------|
| `source` | `Z:/MUSIC/YouTube` | `Z:/MUSIC/Downloads` or any folder with YouTube files |
| `target` | `Z:/MUSIC/Flattened files` | `Z:/MUSIC/Clean` |

If the user provides arguments, substitute them into every command below.
If arguments are omitted, use the defaults.

---

## Pipeline (run all steps automatically, pausing only for curation and final confirm)

### Step 1 -- Scan

```powershell
python scripts/process_media.py --profile youtube scan --src "<source>" --titles scripts/_titles_youtube.json
```

- Read the output. It prints every file stem that is **not yet curated**.
- If it says "All files are already curated", skip straight to Step 3.
- Otherwise: the staging file `scripts/_titles_youtube_staging.json` is created -- proceed to Step 2.

---

### Step 2 -- Curate titles (you do this, no API needed)

Open `scripts/_titles_youtube_staging.json`. For each entry with `"title": ""`:

**Title curation rules:**
- Keep the **song name only** -- strip everything else
- Remove: artist/channel names, featured artists, collab markers (ft, feat, x, prod, w/),
  movie names, album names, release year, video quality tags (4K, HD, HQ, Official Video,
  Full Song, Audio, Lyrics, Music Video), platform noise (YouTube, VEVO, T-Series, Sony Music),
  parenthetical labels `(...)` and bracket labels `[...]` unless they are part of the actual title
- Title Case every word
- Maximum **25 characters** -- truncate at the last full word boundary within 25 chars
- If the filename is truly just an artist name with no identifiable song title, keep it as-is

After curating, **merge** all new entries into `scripts/_titles_youtube.json`:
- Read the existing JSON array (or start with `[]` if the file does not exist)
- Append the new `{"stem": "...", "title": "..."}` entries
- Write the merged array back to `scripts/_titles_youtube.json`

Show the user a compact inline table of the curations you made (original stem -> clean title).

---

### Step 3 -- Preview

```powershell
python scripts/process_media.py --profile youtube preview --src "<source>" --dest "<target>" --titles scripts/_titles_youtube.json
```

- Print the 50-sample table to the user
- Call out any titles that are over 25 chars or look wrong
- The full plan is saved to `scripts/_media_plan.json`

---

### Step 4 -- Confirm and execute

Ask the user: **"Ready to move [N] files to `<target>`? Type `yes` to proceed."**

On confirmation:

```powershell
python scripts/process_media.py execute --live
```

Report the final summary: files moved, duplicates dropped, already-existing, any errors.

---

## Rules

- **Never skip the preview** -- always show it before executing
- **Never overwrite** a file that already exists in the target -- report it as EXISTS
- **Largest file wins** when two files share the same curated title (smaller copy is SKIP, not deleted)
- **Originals are never deleted** for skipped duplicates -- only the moved winner is touched
- All output is inline -- no markdown report files created

---

## Example session

```
User: /cortex-youtube "Z:/Downloads/Music" "Z:/MUSIC/Flat"

Agent: [runs scan] -> 12 uncurated files found
       [curates titles inline]
       Abd Ali - Teri Mitti        -> Teri Mitti
       Arijit Singh Kesariya       -> Kesariya
       ...
       [runs preview] -> 47 move, 3 skip (dupes)
       "Ready to move 47 files to Z:/MUSIC/Flat? Type yes to proceed."

User: yes

Agent: [runs execute --live] -> 47 moved, 3 skipped, 0 errors
```
