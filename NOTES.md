# Notes — news-image v6

## The v5 flaws (verified by viewing v5's entry.png before coding)
1. **Trailing gap right of #16**: the mid grid's last row held only 3 cards (#14 Iowa, #15 Kathmandu, #16 Antalya) at 1/5 width each, so the row ended at 3/5 of the page width and the right 2/5 was blank paper. The user spotted it: "Itu sebelah gambar 16 masih ad ruang kosong".
2. **Short third list column**: the 17–50 list used 12/12/10 columns, so the bottom-right of the list had 2 empty rows.

## v6 fixes
- Last mid row: #14/#15/#16 are each **1/3 wide** (332px), stretched across the full page width — row ends flush at the right edge. Headlines/body wrap at the wider width, so text is shorter and the art panel gets more room.
- List columns rebalanced to **12/11/11** (17–28 / 29–39 / 40–50) — no column ends visibly shorter.
- General rule enforced in the fit pass: art heights are derived from the remaining page budget after all text is measured, so the page ends flush (final y within a few px of 1024).

## Kept from v5 (user accepted)
- y-cursor layout engine: every text block wrapped and measured with font ascent+descent (getmetrics) before drawing; art and text in separate stacked boxes — no text can ever sit under a picture (v5 fixed 16 overlaps this way; v6 keeps the engine).
- Giant serif masthead "Wednesday 25 November 2026", top strip, number strip (1ST / 4TH / 50,000 / 11 / 5-1 / 116), 3 hero cards with full edge-to-edge scenes, 13 numbered illustrated mids, filled-land map with numbered pins, thumbnail glyph on every 17–50 row, DATE CHECK box with dated exclusions, sources line.
- Exactly 50 stories, all Nov 25 2026 only (same verified list as v5 — see STORIES.md).

## Render passes
- Pass 1 (06:14): full page rendered, final y=1024, 216,461 bytes. Viewed full + zoomed bands. Found: (a) 5 list rows ran past the column's right edge (22: 292px, 29: 305px, 34: 289px, 44: 309px, 50: 303px vs 290px available) — text clipped by the page edge; (b) map pins 9/12/13 overlapped each other in Western Europe.
- Pass 2 (06:16): shortened the 5 list items, spread pins 9 (472,30) / 12 (498,14) / 13 (500,52), added a trim guard in the list draw loop (any row over the column width is cut to fit). Re-rendered, final y=1024, 215,439 bytes. Viewed full + zoomed list/map/row-3 bands + 300px downscale: row 3 flush right, list 12/11/11 balanced with all rows inside their columns, pins separated, zero overlaps, dense newspaper at 300px.
- Determinism: main.ts copies entry.png byte-for-byte (verified via out/ run).
