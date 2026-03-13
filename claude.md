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
- `goodreads_url` - Direct Goodreads book page URL (if resolved)
- `cover_url` - Path to local cover image (e.g. `covers/pale-fire.jpg`)

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
- **Tag navigation**: Spacebar/right arrow advances through quotes with same tag, auto-drifts to related tags. Click/tap right 30% of quote area also advances, left 30% goes back.
- **Drift tags**: Arrow up goes to previous tag (shown above), arrow down goes to related tag (shown below). Click/tap on drift tag labels also works.
- **Edit modal**: Localhost-only editing (quote, author, book, tags, Goodreads URL, cover upload/remove/keep-web-cover, delete)
- **Add quote**: ADD link (top-right, next to EDIT) to add new quotes with all fields (localhost only). Auto-fills year and Goodreads URL when publication matches existing book.
- **Search**: Search quotes by text, author, or publication (top-left bar next to TOPICS link)
- **Goodreads links**: Click book block to open book's Goodreads page in new tab. URLs stored as `goodreads_url` field in quotes.json.
- **Tag index**: Pink "TOPICS" link (top-left) or press 'A' to view all topics alphabetically in a 3-column modal, click any tag to navigate to quotes with that tag

### Two Deployments
- `site/index.html` - Local development (has edit features via `isLocalhost` check)
- `docs/index.html` - GitHub Pages (same code, edit features hidden)
- `site/server.py` - Python server with API endpoints for editing

### Tag Data Model
- **`weighted_tags`** — The active tag field used by the site for all navigation, display, and editing. Each entry is `{ tag, weight }` (or `{ tag, weight, corpus_score, relevance }` for older quotes that went through `weight_tags.py`). This is the only tag field that matters.
- **`tags`** — Legacy field from the original GPT-4o extraction pipeline. Contains raw extracted terms (author names, publication keywords, etc.). **Not used by the site.** Many newer quotes (0551+) have this as an empty array, which is fine.
- **`primary_tags`** — Currently unused/empty on all quotes. Primary tag logic is handled by the `ALLOWED_PRIMARY_TAGS` allowlist in `build_tag_connections.py`.

### Important Files
- `site/quotes.json` and `docs/quotes.json` - Quote data (keep in sync)
- `site/tag_connections.json` and `docs/tag_connections.json` - Tag relationships
- `covers/` and `docs/covers/` - Book cover images (keep in sync)

---

## Current Issues (Updated: Mar 2026)

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

### Last Session (Mar 12 2026) - New Machine Migration & Cover Fixes

- **Migrated project from iCloud to local machine**:
  - Copied `site/` files (index.html, server.py, quotes.json, favicons, tag files)
  - Copied `docs/` files (index.html, quotes.json, CNAME, tag_connections.json, 565 covers)
  - Recreated `site/covers → ../docs/covers` symlink
  - Reinitialized git from GitHub remote (iCloud rsync of .git objects was too slow)

- **Fixed 4 missing covers on live site** (never committed):
  - `a-single-man.jpg`, `the-origin-of-species.jpg`, `doin-it-again.jpg`, `the-experience-of-pain.jpg`

- **Fixed duplicate Escape From Evil cover on landing canvas**:
  - Had both `escape-from-evil.png` (11KB, lower quality) and `escape-from-evil.jpg` (25KB, clearer)
  - Consolidated all 5 Escape From Evil quotes to use the `.jpg`, deleted the `.png`

- **Added correct cover for The Denial of Death**:
  - Was incorrectly using the Escape From Evil cover (same author, different book)
  - Downloaded proper cover from Open Library (ISBN 0684832402)
  - Updated 4 Denial of Death quotes to use `covers/the-denial-of-death.jpg`

- **Site now live at everyepigram.com** (GitHub Pages)
- **Total quotes**: ~875

### Previous Session (Mar 6 2026) - Favicon, New Quotes, Double Quotes Display

- **Added favicon** (quote mark logo):
  - SVG source from user's design: two stylized quote marks (pink `#FF0064` left, black right) — also read as mirrored "e" letters
  - Generated `favicon.svg`, `favicon.ico` (16/32/48px multi-size), `favicon-16x16.png`, `favicon-32x32.png`, `favicon-512.png`, `apple-touch-icon.png` (180px)
  - Added `<link>` tags to both `site/index.html` and `docs/index.html`
  - PNG generation via Python Pillow (rasterized SVG bezier paths manually)

- **Changed quote display to double curly quotes**:
  - `\u2018`/`\u2019` (single) → `\u201C`/`\u201D` (double) in `renderPanel()` line ~2706
  - Applied to both `site/index.html` and `docs/index.html`

- **Added 29 new quotes** (quote_0905–0933):
  - Paul Arden's *It's Not How Good You Are...* (Cleese, Ives, Camus, Andretti + others)
  - Foucault's *Discipline and Punish* (×2)
  - Neil Postman's *Building a Bridge to the 18th Century* (McLuhan, Postman ×2)
  - Hitchens' *Why Orwell Matters* (Hitchens, Orwell)
  - Oscar Wilde's *Shorter Prose Pieces* (×4)
  - Melville *Benito Cereno*, Mill *Principles of Political Economy*, Orwell *Down and Out*, Watson *Bendable Learnings* (Madoff), *The Second Machine Age*

- **10 new cover images**: bendable-learnings, benito-cereno, discipline-and-punish-the-birth-of-the-prison, its-not-how-good-you-are-its-how-good-you-want-to-, principles-of-political-economy, sand-talk, short-prose-pieces, the-road-to-serfdom, this-boys-life, why-orwell-matters

- **Tag cleanup** on existing quotes: removed low-relevance tags from Cioran (*A Short History of Decay*), Dostoevsky (*The Gambler*), Poundstone (*Fortune's Formula*). Added "speaking" tag to Dostoevsky.

- **Fixed stray opening `"` in Vonnegut quote** about museums (*If This Isn't Nice, What Is?*)

- **Total quotes**: ~875
- **Primary tags**: 209

### Previous Session (Mar 5 2026) - TOPICS Link, Tag Cleanup & New Quotes

- **Replaced counter with TOPICS link**:
  - Removed `001 / 846` counter from top-left
  - Added pink "TOPICS" link in its place, styled to match ADD/EDIT admin links (`#FF0064`, uppercase, `0.1em` letter-spacing, opacity hover)
  - Clicking TOPICS toggles the tag index overlay (same as pressing 'A')
  - Renamed tag index title from "All Tags" to "All Topics"

- **Tag cleanup — 11 tags merged/renamed** (219 → 209 primary tags):
  - Renamed: good → goodness
  - Merged into existing: stories → storytelling, narrative → storytelling, the end → death, doing → making, living → life, humans → humankind, end times → doom, eschatology → doom, speaking → talking, satisfaction → pleasure
  - Updated `ALLOWED_PRIMARY_TAGS` and `MANUAL_CONNECTIONS` in `build_tag_connections.py`
  - Rebuilt `tag_connections.json`

- **Added 25 new quotes** (quote_0880–0904):
  - Roling, Theroux, Balzac, Kahneman, Tolstoy, King, Alexievich ×3, Illich, Turgenev, Sartre, Mander ×2, Reagan, Berger ×3, Conrad, Huysmans ×2, Vonnegut ×3, Carroll
  - 8 new cover images: a-fortunate-man, against-nature, alice's-adventures, disabling-professions, on-writing, secondhand-time, sketches-from-a-hunters-album, the-kreutzer-sonata
  - 3 Vonnegut quotes have no covers

- **Fixed 3 typos**: "behinds" → "behind" (Roling), "vertiable" → "veritable" (Balzac), pipe char → "I" (Sartre)

- **Mobile spacing**: Bumped back-to-canvas icon down 10px (`top: 50px` → `60px`) for more room below TOPICS link

- **Fixed book author** for Vaneigem's Revolution of Everyday Life (added `book_author` field)

- **Total quotes**: 846
- **Primary tags**: 209

### Previous Session (Mar 5 2026) - Book Detail Modal, Book Bag Feature, Wikipedia Descriptions & Bug Fixes

- **Branch strategy**: Created `book-modal` branch from main, implemented all features, then fast-forward merged to main. Pre-book-bag rollback point: commit `fff8dcb` on main.

- **Added 17 new quotes** (quote_0863–0879) with 6 new cover images. Fixed 2 Goodreads URLs for Thinking Fast and Slow.

- **Book detail modal** (replaces direct Goodreads link):
  - Clicking book-block now opens a modal with: cover image, title, author, year, Wikipedia description, "Add to Book Bag" button, "View on Goodreads" link
  - Click handlers updated in TWO locations: `updateBookBlock()` (~line 2577) and `render()` (~line 2743)
  - Close via × button, Escape key, or backdrop click
  - Keyboard navigation (Space, arrows) blocked while modal is open

- **Wikipedia API integration** (`fetchWikiDescription`):
  - Uses Wikipedia REST API: `https://en.wikipedia.org/api/rest_v1/page/summary/{title}`
  - Tries `{title} (novel)`, `{title} (book)`, then `{title}` to find the right article
  - Skips disambiguation pages
  - Truncates to 2 sentences for brevity
  - **localStorage-backed cache** with versioning (`wikiDescriptions` key, `_v: 1`)
  - **Background prefetch**: `prefetchWikiDescriptions()` runs 5s after page load, iterates all unique books at 150ms intervals to warm the cache

- **Book bag feature** (session-based, no login):
  - `sessionStorage`-backed — persists within browser session, cleared on tab close
  - Functions: `getBookBag()`, `saveBookBag()`, `addToBookBag()`, `removeFromBookBag()`, `exportBookBag()`
  - Duplicate detection by title+author
  - Badge: fixed position bottom-right, SVG books icon (from noun-books-8291069.svg), count display, pop animation on add (`@keyframes badgePop`)
  - Badge z-index: 250 (above book modal's z-index 200 — fixed bug where badge was hidden behind modal)
  - SVG icon: 42px desktop, 33px mobile
  - Overlay: full list with remove × per item, "Copy List to Clipboard" export
  - Export format: `Title — Author (Year)` per line, copied via `navigator.clipboard.writeText()`

- **Design iterations**:
  - Moved badge from top-right to bottom-right (was conflicting with admin ADD/EDIT buttons)
  - Badge made ~3x bigger (padding 6→14px, font 0.8→1.1rem, border-radius 20→28px)
  - Replaced emoji 📖 with custom SVG icon for aesthetic consistency
  - SVG icon enlarged 50% (28→42px desktop, 22→33px mobile)
  - `.quote-panel-author` font changed from DM Mono to DM Sans
  - Book Bag overlay: DM Sans throughout (title, item-meta), title enlarged to 1.6rem with SVG icon
  - `.status-message` z-index bumped to 300 (was hidden behind overlays at 100)
  - `showStatus()` fixed with `void el.offsetWidth` reflow trick for reliable opacity transitions

- **Localhost cover images fix**:
  - Problem: server.py serves from `PROJECT_ROOT/covers/` but many covers only exist in `docs/covers/`
  - Added fallback path in `server.py._serve_cover()` but server didn't pick up code changes
  - **Final fix**: Created symlink `site/covers → ../docs/covers` so static file handler serves them directly

- **Key z-index layering**: status messages (300) > book bag badge (250) > modals/overlays (200)

- **Files modified**: `docs/index.html` (CSS + HTML + JS), `site/index.html` (mirror copy), `site/server.py` (covers fallback), `site/covers` (symlink)
- **Total quotes**: 846
- **Commits**: `2388979` (main feature), plus bug fix commit (pending)

### Previous Session (Mar 3 2026) - UI Overhaul, Goodreads Integration, Mona Matching & Goodreads URL Validation

- **Removed 4 duplicate quotes** (IDs 0059, 0765, 0839, 0818): 797→793 quotes

- **UI layout overhaul**:
  - Removed goto input box, Go button, and "+" button from top-left
  - Added ADD link next to EDIT (top-right, both pink `#FF0064`, 50px gap)
  - Merged count and search into one top-left bar (`#top-bar`) in DM Mono
  - DM Sans font for `.book-block`
  - DM Mono font for tags (`.drift-tag-above`, `.drift-tag`, `.quote-tag`), `.quote-panel-author`, count, search, edit/add links
  - Bumped all header text from 12px to 0.85rem
  - Bumped `.book-title` font from `clamp(9.4px, 1.1vw, 12.4px)` to `clamp(11px, 1.2vw, 14px)`
  - Zero-padded count display: `001 / 793` (prevents layout shift)
  - Google Fonts now loads DM Sans and DM Mono in addition to DM Serif Display/Text

- **Fixed tally bug**: Count was showing quote ID number instead of array position. Changed to `newIndex + 1` consistently.

- **Curly quotes fix**: Wrote Python script to fix all 6 quotes with straight double quotes → curly quotes across both JSON files.

- **Goodreads integration**:
  - Click book block → opens Goodreads page in new tab
  - `getGoodreadsUrl()` function: uses `goodreads_url` field first, falls back to ISBN search, then title+author search
  - Resolved actual Goodreads book page URLs for ~370 books (not search results)
  - Multi-pass process: automated scraping → manual lookups for 48 well-known books → fixed 32 study guide/summary links → synced inconsistent URLs across same-book quotes
  - Added `goodreads_url` field to edit modal (and add modal)
  - `autoFillBookInfo()` now also auto-fills Goodreads URL from existing books
  - `server.py` auto-links `goodreads_url` (along with year, isbn, cover_url) when publication matches
  - Fixed specific bad links: The Red Tenda of Bologna (was linking to Ways of Seeing), The Man Who Was Thursday (was linking to Gunman's Reckoning)

- **Goodreads URL validation & cleanup** (`validate_goodreads.py`, `fix_goodreads.py`):
  - Built validation script that fetches all 367 unique Goodreads URLs and compares page `<title>` against expected publication
  - Goodreads URL format: `book/show/{id}.{slug}` — slug is cosmetic, only numeric ID determines the page. Many wrong IDs had plausible slugs.
  - **~61 total URL fixes across 3 batches**:
    - Batch 1: 25 automated fixes from search script (filtered out study guides/analyses)
    - Batch 2: 14 manual lookups (10 where script found study guides + 4 not found)
    - Batch 3: 9 more wrong links found in full validation sweep (e.g. Conquest of Happiness → "Elfquest", The Light That Failed → "Overwatch Memes")
  - Replaced 15 foreign language edition URLs with English editions (Italian, Spanish, Turkish, Portuguese, French, Polish, Chinese, Catalan)
  - Fixed corrupted URL: Revolution of Everyday Life had `381erta` instead of `381416`
  - Fixed Distrust That Particular Flavor: all quotes → correct ID `11890817`
  - Scripts saved: `validate_goodreads.py`, `fix_goodreads.py`, `apply_goodreads_fixes.py` through `apply_goodreads_fixes4.py`
  - Validation results: `goodreads_validation.json`, fix proposals: `goodreads_fixes.json`

- **Mona API book matching** (`match_mona.py`, `filter_mona.py`):
  - Compared quotes collection (379 unique books) against Mona's Vernon O Content library (~30,000 books)
  - API: `pulse.mona.artpro.co/api/vernon-o-content/books/search?q=...` with `X-API-Key` header
  - Raw API matches: 170, but many false positives from loose text search
  - After rigorous filtering (require BOTH author surname AND title match): **73 confirmed matches (19%)**
  - Results saved in `mona_confirmed.json`
  - Notable overlaps: 6 Vonnegut titles, 3 Taleb, 2 Dostoyevsky, 2 David Walsh, classics (Moby Dick, Ulysses, Divine Comedy, etc.)

- **Fixed Pale Fire cover**: Shakespeare "moon's an arrant thief" quote changed from Timon of Athens to Pale Fire — updated `cover_url` and `book_title` to match.

- **Author name standardized**: "A.N. Whitehead" → "Alfred North Whitehead"

- **New quotes**: 2 William Gibson quotes added (quote_0861, 0862) from Distrust That Particular Flavor

- **New/updated covers**: 2 new (the-lyrics-1962-2012, twilight-of-idols-and-anti-christ), 2 updated higher-res (on-disobedience, the-life-and-masterworks-of-jmw-turner)

### Previous Session (Mar 2 2026) - Mobile Layout Overhaul, New Quotes & Serif Font

- **Added 19 new quotes** (quote_0817–0835) with 7 new covers and 1 updated cover (palm-sunday)

- **Mobile layout improvements** (`@media max-width: 768px`, at end of `<style>`):
  - Search input moved to top-right, tally stays top-left
  - Edit link and goto controls hidden on mobile
  - Back-to-canvas grid icon moved to top-left below tally
  - Primary tag lowered to clear top bar
  - Book block raised with `margin-bottom: 30px` for iOS Safari URL bar
  - Book block `height: auto` / `overflow: visible` to prevent cover clipping in column layout
  - Tag index overlay uses 2 columns (3 on desktop)
  - Search results dropdown anchored to right edge

- **Serif font for quote text**:
  - Loaded DM Serif Display + DM Serif Text from Google Fonts
  - `.quote-panel-text` base: `font-family: "DM Serif Display", serif; font-weight: 400`
  - JS in `renderPanel()`: quotes ≤64 chars use DM Serif Display, >64 chars use DM Serif Text
  - **Note**: The actual quote text class is `.quote-panel-text` (NOT `.quote-text` which is a dead/unused rule)

- **Added Tag Data Model section to claude.md**: documents `weighted_tags` (active) vs `tags` (legacy) vs `primary_tags` (unused)

- **Fix**: Edit modal backdrop close changed from `onclick` to `onmousedown`

- **Total quotes**: 782

### Previous Session (Feb 25 2026) - Tag Connection Overhaul & Force Graph Improvements

- **Connected 72 straggler tags** (had 0-2 connections, now all 219 tags have 3+):
  - Added `MANUAL_CONNECTIONS` dict (~85 entries) to `build_tag_connections.py`
  - Bidirectional expansion with varied scores (2.8-4.2 range)
  - Organized into sections: 0-connection, 1-connection, 2-connection tags, plus thematic bridges
  - Connections merge into organic PMI-based co-occurrence data during build

- **Force graph visualization improvements** (`site/tag_viz.html`, `docs/tag_viz.html`):
  - Increased bubble spacing by 40% (two rounds of 20%)
  - Changed bubble sizing from `sqrt` to `pow(0.6)` for more variance between hub and leaf tags
  - Bumped visible link count from 8 to 12 per tag
  - Fixed click highlight to include bidirectionally-connected tags (was only checking clicked node's own `related` list)

- **Reassigned 63 grey tags into themed color categories** (16 remain grey):
  - Philosophy/Mind: fear, love, happiness, sadness, pessimism, emotion, pain, suffering, desire, comfort, calmness, patience, gratitude, acceptance, pleasure, satisfaction, madness, hell, heaven, the devil, spirit, the unknown, individuality, purpose, expectations, experience, perspective, depth, why, views, opinion, attitude
  - Art/Creativity: looking, seeing, vision, wonder, eyes, the senses, perception, imagination, ideas, curiosity, process, collaboration, connections, doing, failure, perfection, problem solving, simplicity, simplification, the new
  - Moved perception tags (looking, seeing, vision, wonder, eyes, the senses, perception, imagination) from Philosophy to Art

- **Pushed to GitHub Pages**

### Previous Session (Feb 18 2026) - Click/Tap Navigation, Tag Fixes, New Quotes & Covers

- **Added click/tap navigation to quote view**:
  - Click/tap left 30% of quote area → previous quote (same as ArrowLeft)
  - Click/tap right 30% of quote area → next quote (same as ArrowRight)
  - Pointer cursor on hover over clickable zones
  - Drift tags above/below already had onclick handlers, no changes needed
  - Makes site fully navigable on mobile

- **Fixed corrupted tag_connections.json**:
  - All 215 tags had data replaced with `["related", "quote_count"]` instead of actual connection objects
  - This caused no drift tags (below) to appear on any quotes
  - Rebuilt with `build_tag_connections.py`

- **Retagged 37 quotes** with fewer than 3 primary tags:
  - Exported quotes with 0-1 primary tags to CSV for manual review
  - Applied updated tags from reviewed spreadsheet
  - Added books/writing tags to Melville quote_0378

- **Added 7 new primary tags to allowlist**: acceptance, ambition, authority, desire, humility, modernity, weakness
  - 2 active now (3+ quotes): acceptance (4), desire (5)
  - Others ready for when more quotes get tagged

- **Added 11 new quotes** (quote_0724–quote_0734):
  - Kurt Vonnegut Jr., Ernest Becker, F. Scott Fitzgerald, Franz Kafka
  - Gene Kranz, William Shakespeare, Kai Strittmatter, Haruki Murakami
  - Jeff Tweedy, Herbert Read, Michel Houellebecq, Wallace Stevens

- **Added 7 new cover images**:
  - after-dark, apollo-13, h-p-lovecraft-against-the-world-against-life
  - lyrics-vol-2, now, the-grass-roots-of-art, the-most-beautiful-woman-in-town

- **Updated 2 covers**: marcovaldo, mother-night

- **Added 4 missing covers to GitHub Pages**: apollos-arrow, complete-poems-19041962, making-museums-matter, notes-from-a-small-island

- **Standardized author name**: Kurt Vonnegut → Kurt Vonnegut Jr. (22 instances)

- **Primary tag count**: 216 (was 215)
- **Total quotes**: ~681

### Previous Session (Feb 11 2026) - New Quotes, Covers, Tag Cleanup & Pushes

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
