# Quotes Vision Pipeline

A Python project for extracting and structuring quotes from images using GPT-4o vision.

## Project Structure

```
quotes/
├── input/              # Source images of quotes (PNG/JPG)
│   └── rd2/            # Current batch of quote images
├── output/             # Processed output files
│   ├── quotes.json     # Extracted quotes (main output)
│   └── quotes.csv      # CSV format output
├── site/               # Web display utilities
│   ├── csv_to_json.py  # Convert CSV to JSON for web
│   └── quotes.json     # Final quotes for display
├── source images/      # Original source images
├── z_old/              # Archived/old data and legacy scripts
└── extract_quotes.py   # Main extraction script (GPT-4o vision)
```

## Pipeline Workflow

Single-step extraction using GPT-4o vision:

```bash
python extract_quotes.py
```

Images are sent directly to GPT-4o which extracts and structures the quote data in one pass. No intermediate OCR step required.

## Dependencies

- Python 3
- OpenAI Python SDK

```bash
pip install openai
```

## Environment Variables

- `OPENAI_API_KEY` - Required

## Usage

```bash
# Extract quotes from images in input/ directory
python extract_quotes.py

# Custom input/output paths
python extract_quotes.py --input path/to/images --output output/quotes.json

# Convert to site JSON (if needed)
cd site && python csv_to_json.py
```

## Output Schema

Each processed quote contains:
- `id` - Unique identifier
- `source_image` - Original filename
- `quote` - The quote text (sentence case, single paragraph)
- `author` - Attribution
- `year` - Publication year (if found, else null)
- `publication` - Source work (if found, else null)
- `notes` - Extraction observations
- `confidence` - Extraction confidence score (0.0-1.0)
- `needs_review` - Flag for manual review

## Legacy Scripts

The old Tesseract-based pipeline is preserved in `z_old/`:
- `ocr_dump.py` - Tesseract OCR extraction
- `ocr_v2.py` - Alternative OCR with parsing heuristics
- `llm_parse.py` - LLM cleanup of OCR output

---

## Quote Viewer Site (site/index.html)

Interactive quote browser with tag-based navigation, book covers, and flying cover animations.

### Key Features
- **Landing canvas**: Grid of book covers that users click to enter quote view
- **Tag navigation**: Spacebar/right arrow advances through quotes with same tag, auto-drifts to related tags
- **Drift tags**: Arrow up goes to previous tag (shown above), arrow down goes to related tag (shown below)
- **Edit modal**: Localhost-only editing (quote, author, book, tags, cover upload/remove, delete)
- **Add quote**: "+" button to add new quotes with all fields (localhost only)
- **Go-to input**: Jump to specific quote by number (localhost only)
- **Search**: Search quotes by text, author, or publication (localhost only)

### Two Deployments
- `site/index.html` - Local development (has edit features via `isLocalhost` check)
- `docs/index.html` - GitHub Pages (same code, edit features hidden)
- `site/server.py` - Python server with API endpoints for editing

### Important Files
- `site/quotes.json` and `docs/quotes.json` - Quote data (keep in sync)
- `site/tag_connections.json` and `docs/tag_connections.json` - Tag relationships
- `covers/` and `docs/covers/` - Book cover images (keep in sync)

---

## Current Issues (Updated: Jan 2026)

### Arrow Up (driftUp) Intermittent Bug
- **Problem**: Pressing arrow up to navigate to the tag shown above works sometimes but not always
- **Example**: Tag "devil" shows above the active tag, but arrow up does nothing
- **Arrow down works fine**
- **Debug logging added**: Check browser console for:
  - "ArrowUp pressed, calling driftUp"
  - "driftUp called" with `transitionActive`, `driftTags`, `tagHistory` values
  - "renderRelatedTags called, tagHistory:"
- **Suspect**: Timing issue with `tagHistory` or `driftTags` array population
- **Key functions**: `driftUp()`, `renderRelatedTags()`, `switchToTag()`
- **Key variables**: `driftTags[]` (index 0 = tag above from history), `tagHistory[]`

### Recent Fixes Applied
- Added `document.activeElement.blur()` in `closeEditModal()` to restore keyboard nav after editing
- Added input field check in keyboard handler to prevent spacebar changing quotes while typing

---

## Session Notes

*Ask me to update this section at the end of each session!*

### Last Session (Jan 22 2026) - Search, Tag Weighting & Pipeline Fixes

- **Fixed duplicate covers across chunk boundaries**:
  - `pickUniqueCover()` now checks edge covers of neighboring chunks
  - Prevents same book appearing side-by-side when chunks are adjacent

- **Added search feature** (localhost only):
  - Search input next to go-to and "+" buttons
  - Searches quote text, author, and publication
  - Keyboard navigation (arrows, Enter, Escape)
  - Shows up to 10 results with truncated quote preview

- **Improved tag weight distribution**:
  - Changed weight formula from `corpus_score × relevance` to `sqrt(corpus_score) × relevance`
  - This reduces dominance of high-frequency tags (humanity, life, society)
  - Lower-frequency but highly relevant tags now rank higher
  - `getTopWeightedTag()` now randomly picks from tags within 50% of max weight

- **Fixed weight_tags.py pipeline**:
  - Now reads from `weighted_tags` (curated) instead of `tags` (original)
  - Preserves manual tag edits (additions/removals) made through the editor
  - Only recalculates weights, doesn't replace tag lists

- **Tag weighting formula**:
  - `weight = sqrt(corpus_score) × relevance`
  - `corpus_score`: log-scaled frequency across all quotes (0-1)
  - `relevance`: how well tag fits quote (0.5 base + bonuses for appearing in text)

- **Pipeline to update tags after editing**:
  ```bash
  python weight_tags.py           # Recalculate weights (preserves curated tags)
  python build_tag_connections.py # Rebuild tag relationships
  cp site/quotes.json docs/quotes.json
  cp site/tag_connections.json docs/tag_connections.json
  ```

### Previous Session (Jan 20 2026) - Add Quote Feature & Cover Updates
- **Added "Add Quote" feature** (localhost only):
  - "+" button next to go-to input
  - Reuses edit modal with "Add Quote" title, hides delete button
  - New `/api/add-quote` endpoint in server.py generates next quote ID
  - Auto-links book info (cover, year, ISBN) if publication matches existing quote
  - Validates required fields (quote text, author)
- **Updated book block width**: 400px → 320px
- **Hid ISBN field** from quote display (still editable in modal)
- **Synced 46 cover images** to docs/covers/ (16 updated, 4 new from previous commit, 23 more today)
- **Pushed cover updates to GitHub** for GitHub Pages

### Previous Session (Jan 2026) - Tag System Overhaul
- **Revised popular tags list**: Reduced from 263 to 228 displayed tags
- **Renamed 23 tags** for clarity:
  - Singular → plural: artist→artists, king→kings, poem→poems, song→songs, path→paths
  - Added "the" prefix: mind→the mind, world→the world, future→the future, past→the past, present→the present, end→the end, self→the self, senses→the senses, unknown→the unknown, new→the new, brain→the brain, devil→the devil
  - Other: calm→calmness, banal→banality, unique→uniqueness, value→values, view/viewpoint→views
- **Applied 161 tag renames** across all quotes in weighted_tags
- **Deleted quote_0424** (Ozzy Osbourne on wine - "it's all bullshit with wine")
- **Fixed 6 orphaned quotes** that had no popular tags:
  - quote_0142 (Erich Fromm): added revolution, humankind, change
  - quote_0164 (Nietzsche): added learning, knowledge
  - quote_0172 (Nietzsche): added humanity, society
  - quote_0212 (Flaubert): added design, spirit
  - quote_0272 (James Joyce): added media, vision, the senses
  - quote_0305 (John Muir): added nature, complexity
- **Fixed Saint-Exupéry quote** (quote_0001): was incorrectly tagged as "technology", changed to simplicity, design, perfection, creativity
- **Rebuilt tag_connections.json** with new popular tags
- **Fixed cover URLs**: removed leading slash (`/covers/` → `covers/`) for GitHub Pages compatibility
- **Fixed adjacent duplicate covers** in infinite canvas: updated `pickUniqueCover()` to check left/above neighbors
- **Updated server.py** to auto-sync edits to docs/:
  - Cover uploads now save to both `covers/` and `docs/covers/`
  - All quote saves/deletes now write to both `site/quotes.json` and `docs/quotes.json`
  - Cover URLs use relative path (`covers/filename`) for GitHub Pages
- **Pushed 6 new/updated cover images**: don-juan, mark-twains-notebook, intentions, as-i-walked-out-one-evening, distrust-that-particular-flavour, the-collected-poems-of-bertolt-brecht

### Older Session
- Rebuilt edit modal from scratch (was lost/overwritten)
- Added go-to input box
- Fixed spacebar-in-input-field bug
- Synced site/ to docs/ (quotes.json, tag_connections.json, 380 cover images)
- Started debugging intermittent driftUp issue - not yet resolved
