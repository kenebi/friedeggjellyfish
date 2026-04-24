# Fried Egg Jellyfish (FEJ) — Brand Guide
*Created: April 24, 2026*
*Agent: Claude (CLD)*
*Version: 1.0*

---

## Logo

The FEJ logo is a stylized fried egg jellyfish — the bell of the jellyfish
is rendered as a sunny-side-up fried egg, with the yolk as the focal point
and tentacles flowing below. The teal drop-shadow offset-right gives it
depth and reinforces the underwater jellyfish metaphor.

**Logo files:**
- `AVILANE_FEJ_LOGO_20260423_CLD_v1.svg` — canonical vector source
- `AVILANE_FEJ_LOGO_20260423_CLD_v1.png` — raster export (725×812 px)

**Canvas:** 725 × 812 px (SVG viewBox)
**Orientation:** Portrait
**Background:** Transparent (works on any light background)

---

## Color Palette — 4 Colors

These are the **canonical hex values pulled directly from the SVG source**.
All FEJ assets — dashboard UI, README, PyPI page, GitHub social card,
docs site — must use these exact values.

| # | Name | Role | Hex | RGB |
|---|------|------|-----|-----|
| 1 | **Yolk Gold** | Primary — focal point, running state | `#F9AA10` | `249, 170, 16` |
| 2 | **Jellyfish Navy** | Outlines, primary text, success state | `#1B3C5A` | `27, 60, 90` |
| 3 | **Tentacle Teal** | Drop-shadow, accent, links | `#22A3A4` | `34, 163, 164` |
| 4 | **Egg White** | Body fill, dashboard background | `#FDFEFE` | `253, 254, 254` |

### Why these 4 colors work

- Navy and teal share a low red channel and similar blue — the shadow
  feels like it *belongs* to the outline rather than being a random
  accent
- Yolk gold is the only warm color — it commands all the attention,
  which is correct since the yolk is the brand's focal point
- Egg white is near-pure white with a 2-unit offset — prevents harsh
  contrast on real displays but reads as white

---

## Dashboard Color Mapping

The 4-color palette maps cleanly to the dashboard's node states:

| State | Color | Hex | Meaning |
|-------|-------|-----|---------|
| Pending | Egg White (or 20% Navy) | `#FDFEFE` / `#1B3C5A33` | Step hasn't started yet |
| Running | Yolk Gold | `#F9AA10` | Currently executing — animated pulse |
| Success | Navy | `#1B3C5A` | Done, succeeded |
| Error | — | `#D64545` (added) | Failed — this is the only color outside the palette, added because none of the 4 read as "error" |
| Accent | Tentacle Teal | `#22A3A4` | Links, hover states, edge lines between nodes |
| Text | Navy | `#1B3C5A` | All body text |
| Background | Egg White | `#FDFEFE` | Dashboard canvas |

**Note on error red (`#D64545`):** The 4-color palette has no "warning"
signal, so a red is added *only* for error states. This is the one
allowed exception to the palette rule. Do not use red anywhere else.

### CSS variables (for dashboard)

```css
:root {
  /* Brand palette */
  --fej-gold:  #F9AA10;
  --fej-navy:  #1B3C5A;
  --fej-teal:  #22A3A4;
  --fej-white: #FDFEFE;

  /* State tokens (derived) */
  --fej-state-pending: rgba(27, 60, 90, 0.2);
  --fej-state-running: var(--fej-gold);
  --fej-state-success: var(--fej-navy);
  --fej-state-error:   #D64545;

  /* Semantic */
  --fej-bg:     var(--fej-white);
  --fej-text:   var(--fej-navy);
  --fej-accent: var(--fej-teal);
}
```

---

## Typography

**Not yet finalized.** For Phase 1, the dashboard will use a safe
system-font stack so there are no font-loading dependencies on users'
machines:

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif;
```

**Phase 2 decision:** Pick one open-source font for the README/docs/PyPI
page that reinforces the playful-but-technical feel. Candidates to
evaluate: Inter, DM Sans, Work Sans, Manrope.

*Note: FEJ is a separate brand from AVI Lane, so it does NOT inherit
AVI Lane's Inter + DM Sans pairing. Decide fresh.*

---

## Relationship to AVI Lane

FEJ is an **open-source project owned by Kenneth Ebilane** and credited
to AVI Lane Digital for attribution/reputation-building purposes.
It is **not** an AVI Lane sub-brand.

- FEJ has its own palette (above) — do NOT use AVI Lane's Dark & Bold
  palette (`#2C2C2A`, `#EF9F27`, `#FAC775`) in FEJ assets
- FEJ's `#F9AA10` gold and AVI Lane's `#EF9F27` amber are close but
  distinct. Keep them separate.
- FEJ's GitHub README may reference "Built by Kenneth Ebilane /
  AVI Lane Digital" in a footer, but not co-brand visually

---

## Asset Checklist (Phase 1)

- [x] Primary logo (PNG + SVG) — `AVILANE_FEJ_LOGO_20260423_CLD_v1.*`
- [ ] Favicon (ICO or PNG, 32×32 and 16×16) — derive from yolk alone
- [ ] GitHub social card (1280×640) — logo + tagline on Egg White
- [ ] PyPI project icon (square, recommended 200×200)
- [ ] Dashboard logo variant (simplified, smaller — for header)
- [ ] Monochrome variant (navy-only, for print/one-color use)
- [ ] Dark-background variant (if dark mode dashboard is shipped)

---

## Usage Rules

**Do:**
- Use the SVG wherever possible (infinitely scalable, smallest file)
- Preserve the teal drop-shadow — it's part of the identity, not
  optional decoration
- Give the logo breathing room equal to at least the width of the yolk
- Use on light backgrounds in Phase 1

**Don't:**
- Recolor the logo outside the 4-color palette
- Remove the drop-shadow "just to clean it up"
- Squash or stretch — lock aspect ratio
- Place on busy photographic backgrounds
- Use at sizes below 48 px wide (yolk detail disappears)

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-04-24 | [CLD] Initial brand guide. Logo palette extracted from SVG source. Dashboard color mapping defined. Error red (`#D64545`) added as single palette exception. |
