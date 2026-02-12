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
- **Edit modal**: Localhost-only editing (quote, author, book, tags, cover upload/remove/keep-web-cover, delete)
- **Add quote**: "+" button to add new quotes with all fields (localhost only)
- **Go-to input**: Jump to specific quote by number (localhost only)
- **Search**: Search quotes by text, author, or publication (press 'S' to toggle)
- **Tag index**: Press 'A' to view all tags alphabetically in a 3-column modal, click any tag to navigate to quotes with that tag

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

### Last Session (Feb 11 2026) - New Quotes, Covers, Tag Cleanup & Pushes

- **Added 40 new quotes** (quote_0656–quote_0699, minus quote_0688 Simonides which has no cover):
  - Bill Callahan: *I Drive a Valence*
  - David Hockney: *Hockney on Photography*
  - Ralph Waldo Emerson: *Essays: First and Second Series*
  - Guy Debord: *Society of the Spectacle* (×2)
  - David Hume, Friedrich Nietzsche, Harold Innis: *The Bias of Communication*
  - Herman Melville (via Philip Hoare): *The Whale*
  - H.P. Lovecraft (via James Bridle): *The New Dark Age* (×2)
  - Graham Greene: *Our Man in Havana* (×2)
  - Jacques Ellul: *Propaganda*
  - Jane Jacobs: *The Death and Life of Great American Cities*
  - John Berryman: *The Dream Songs*
  - Carl Jung: *Memories, Dreams, Reflections*
  - Kurt Vonnegut Jr.: *If This Isn't Nice, What Is?* (×3)
  - Lewis Mumford: *The Story of Utopias*
  - Louis-Ferdinand Celine: *Journey to the End of the Night* (×4)
  - Nassim Nicholas Taleb: *Fooled By Randomness*
  - Neil Postman: *The Disappearance of Childhood* (×2)
  - Nikolai Gogol: *Dead Souls*
  - Paul M. Schwartz (via Zuboff): *The Age of Surveillance Capitalism*
  - Daniel Defoe: *Robinson Crusoe*
  - Shoshana Zuboff: *The Age of Surveillance Capitalism*
  - Simonides of Ceos (via Taleb): *Antifragile*
  - Alva Noe, James Baldwin: *Strange Tools*
  - The Invisible Committee: *To Our Friends*
  - Henry David Thoreau (via Hoare): *The Whale*
  - T.S. Eliot: *Collected Poems 1909-1962*
  - W.H. Auden: *Another Time*
  - Wendell Berry: *The Peace of Wild Things* (×2)
  - William Durant (via Winchester): *Krakatoa*
  - William Blake: *The Complete Poetry and Prose*
  - William Carlos Williams: *Paterson*

- **Added 14 new cover images**:
  - another-time, collected-poems-1909-1962, essays-first-and-second-series
  - hockney-on-photography, i-drive-a-valence, krakatoa-the-day-the-world-exploded
  - memories-dreams-reflections, our-man-in-havana, robinson-crusoe
  - society-of-the-spectacle, strange-tools, the-dream-songs, the-new-dark-age, the-whale

- **Updated cover**: the-story-of-utopias (higher resolution)

- **Fixed misspelled tags** (10): creativty→creativity, doube→doubt, exceptance→acceptance, existience→existence, goverment→government, openess→openness, temperment→temperament, univeralism→universalism, wiscom→wisdom, upheavel→upheaval

- **Fixed corrupted tag**: `capitalism\` → `capitalism` (trailing backslash)

- **Standardized spelling variants**: aging→ageing, labor→labour, dostoyevsky→dostoevsky, michel du montaigne→michel de montaigne, problem-solving→problem solving, red tends→red tenda of bologna

- **Removed 22 junk tags**: year numbers (1862, 1866, 1868, etc.), name fragments (nicholas, friedrich, nnt), nonsense (vx, state again, take it, thank you, what, do, up, done, here, akzidenz, fedra)

- **Updated 4 Taleb quotes**: publication renamed to *Antifragile: Things That Gain from Disorder*

- **Added tags** to Blake quote_0537: honesty, truth

- **Total quotes**: 653 (was 609 at start of session)

### Previous Session (Feb 9 2026) - Tag Index Modal, Weak Tag Fixes, New Quotes & Rebellion Tag

- **Added tag index modal** (press 'A'):
  - 3-column alphabetical list of all primary tags with quote counts
  - Works as overlay from both landing canvas and quote view
  - Click any tag to navigate to quotes with that tag
  - Close with Escape, click outside, or press 'A' again
  - Deployed to both localhost and GitHub Pages

- **Fixed 20 weakest tag connections**:
  - Replaced poor/irrelevant connections (e.g. architecture→humour, doom→songs, clarity→banality)
  - Added 55 reciprocal connections for bidirectional navigation
  - Examples: architecture now connects to cities/civilisation/art/design

- **Removed 9 primary tags**: birth, error, eschatology, expression, jobs, humour, humankind, humans, speaking
- **Renamed 2 tags**: definition→definitions, good→goodness
- **Primary tag count**: 228→220

- **Added 'rebellion' as primary tag**:
  - Connected to revolution, power, disobedience, defiance, change
  - Tagged 12 quotes (Fromm ×3, Cioran, Vaneigem ×3, Joyce, Camus, Twain, Saint-Just, Russell)

- **Added 21 new quotes** (quote_0635–quote_0655):
  - Balzac, Thoreau, Poincaré, Harlan Ellison, Paul Theroux
  - Borges, Bohr, Bryson ×2, Russell ×3, Kahneman, Orwell, Alva Noë ×3, Camus ×3, Burgess
  - 6 new covers: a-clockwork-orange, a-short-history-of-nearly-everything, down-and-out-in-paris-and-london, other-inquisitions, the-impact-of-science-on-society, the-happy-isles-of-oceania-paddling-the-pacific
  - Updated cover: correspondence-between-schiller-and-goethe

- **Cleaned up tags across 55 quotes**:
  - Removed 288 low-value tags (author names, publication titles, "humour" over-tagging, generic filler)
  - Added 40 meaningful replacements

- **Minor fixes**:
  - Fixed Shitao quote: publication "Shape of a Pocket" → "The Shape of a Pocket", added cover
  - Fixed Goethe year: 2012 → 1898
  - Fixed Mencken author: "HL Mencken" → "H.L. Mencken"
  - Fixed Nabokov line break in waxwing quote

### Previous Session (Feb 8 2026) - New Quotes, Search on GitHub Pages & Tag Connections

- **Added 14 new quotes** (quote_0621–quote_0634):
  - Gibson, Gottlieb, Becker, Thompson, Giraudoux, Cage, Basso, Vonnegut, Proust, Mallarmé, Kant, Eco, Stevens
  - 6 new cover images: anthropology-history-and-education, collected-poems, for-the-birds, selected-poetry-and-prose, walsh-street, within-a-budding-grove
  - Fixed quote_0632 attribution: was Gravity's Rainbow, corrected to V. (Pynchon)
  - Removed duplicate Pynchon quotes (quote_0496, quote_0632), kept quote_0553

- **Added search to GitHub Pages**:
  - Search container moved out of localhost-only goto-container
  - Hidden by default, press 'S' to toggle open, Escape to close
  - Same search functionality: text, author, publication matching

- **Added 'randomness' tag**:
  - Tagged 8 quotes (Taleb, Pynchon, Keith Richards, Kubler, Dufrêne, Stoppard, Poundstone ×2)
  - Connected to luck, chance, gambling, serendipity

- **Connected 'luck' tag** to chance, gambling, uncertainty, failure, serendipity

- **Connected 'simplification' tag** to complexity, design

- **Connected all orphan tags** (zero remaining):
  - First batch (11): freedom, curiosity, collaboration, ethics, play, travel, mathematics, psychology, success, logic, prediction
  - Second batch (13): uniqueness, attitude, calmness, danger, depth, error, fire, gratitude, improvement, laws, ownership, property, spirit

- **Minor fixes**:
  - Added book_author "Jens Ludwig" to quote_0600 (Unforgiving Places)
  - Updated citadelle.jpg cover image

### Previous Session (Feb 5 2026) - Keep Web Cover Feature & Cover Sync Fix

- **Added "Keep Web Cover" button**:
  - When editing a quote that has a web cover (from bookcover.longitood.com) but no local cover, a green "Keep Web Cover" button appears
  - Clicking it downloads the image and saves it to both `covers/` and `docs/covers/`
  - Updates the quote's `cover_url` to use the local path
  - New `/api/download-cover` endpoint in server.py handles the download

- **Fixed cover sync issue**:
  - `citadelle.jpg` and `the-ashtray.jpg` were in `docs/covers/` but not `covers/`
  - Copied missing covers to `covers/` folder
  - Updated `cover_url` for quote_0616 (The Ashtray) and quote_0618 (Citadelle)

- **Cover workflow clarified**:
  - Web covers: fetched from `https://bookcover.longitood.com/bookcover` API
  - Local covers: stored in `covers/` (localhost) and `docs/covers/` (GitHub Pages)
  - Both folders must stay in sync for consistent behavior

### Previous Session (Jan 30 2026) - New Quotes & Landing Canvas Fix

- **Added 23 new quotes** from various authors:
  - Einstein, Herzen, Sagan, Harris, Wallace, Pollan, Mamet (x2), Dostoevsky, Camus, Calvino
  - Nina Simone, Will Rogers, William Blake, Walter Benjamin, T. S. Eliot, Kahneman, Toffler
  - David Brower, Folk saying (via Solzhenitsyn), Balzac

- **Added 10 new cover images**:
  - albert-einstein-the-human-side, both-flesh-and-not, conclave, very-best-of-nina-simone-vol-2
  - berlin-childhood-around-1900, the-perfect-critic, the-third-wave, thinking-fast-and-slow
  - pere-goriot, bills-secrets-class-war-and-ambition

- **Updated covers**: timon-of-athens, the-life-of-reason, whats-wrong-with-the-world

- **Fixed landing canvas cover repetition bug**:
  - Problem: Covers repeated in a pattern every 2 rows due to chunk recycling
  - Solution: Implemented seeded PRNG based on chunk coordinates
  - Each chunk (x,y) now gets deterministic but unique covers
  - Added `seededRandom()` and `getChunkCovers()` functions
  - Backup saved at `docs/index.html.backup`

### Previous Session (Jan 23 2026) - Tag Revisions & New Quotes

- **Revised tags on multiple quotes**:
  - Cleaned up weighted_tags by removing less relevant tags
  - Improved tag accuracy across several quotes (Bertrand Russell, Dostoevsky, etc.)

- **Added 7 new quotes with cover images**:
  - Goethe: "Correspondence Between Schiller and Goethe" (books, understanding, discovery)
  - Hilary Mantel: "Wolf Hall" (the past, sins)
  - Shoshana Zuboff: "The Age of Surveillance Capitalism" - 2 quotes (surveillance, technology, uncertainty, chaos)
  - David Walsh: "A Bone of Fact" (iteration, prototyping, design)
  - Antonio Gramsci: "Selections from the Prison Notebooks" (history, teaching, learning)
  - Albert Camus: "The Plague" (words, language, clarity)

- **Added 5 new cover images**:
  - correspondence-between-schiller-and-goethe.jpg
  - selections-from-the-prison-notebooks.jpg
  - the-age-of-surveillance-capitalism.jpg
  - the-plague.jpg
  - wolf-hall.jpg

### Previous Session (Jan 22 2026) - URL Parameters, Quote IDs & New Quotes

- **Added URL parameter for direct quote access**:
  - Use `?q=484` to jump directly to quote_0484
  - Skips landing canvas, goes straight to quote view
  - Works on both localhost and GitHub Pages

- **Fixed quote numbering to use quote ID**:
  - Display now shows quote ID (484) instead of array index (425)
  - Go-to input accepts quote IDs, matching the URL parameter
  - Makes `?q=484` and displayed "484 / 561" consistent

- **Auto-convert straight apostrophes to curly**:
  - Fixed 3 existing quotes with straight apostrophes
  - Editor auto-converts `'` to `'` as you type
  - Uses Unicode escape `\u2019` for safe encoding

- **Added new quotes and covers**:
  - Virginia Woolf: Mrs Dalloway, Orlando, The Waves, Between the Acts, Three Guineas
  - Emily Dickinson Letters
  - When Things Fall Apart (Pema Chödrön)

### Previous Session (Jan 22 2026) - Primary Tag Allowlist & Pipeline Fixes

- **Added ALLOWED_PRIMARY_TAGS allowlist** to `build_tag_connections.py`:
  - 230 curated tags that can appear as navigable primary themes
  - Only these tags show in drift navigation (tag above/below)
  - Quotes can still have other tags in `weighted_tags`, they just won't be primary
  - Result: 227 primary tags (3 from the list don't have enough quotes)

- **Fixed drift navigation for renamed tags**:
  - `build_tag_connections.py` now reads from `weighted_tags` (curated) instead of `tags` (original)
  - This fixes navigation for renamed tags like "the end" (was "end")
  - Without this fix, renamed tags wouldn't appear as drift suggestions

- **Investigated lost quote edit**:
  - Steinbeck "advice" quote tags weren't saved from a previous session
  - Examined server.py save mechanism - works correctly
  - Likely cause: file operations (cp commands) during session overwrote the edit
  - User re-edited, confirmed save now works (both site/ and docs/ updated)

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
