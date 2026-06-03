# Allegory — A Tapestry of Guru Nanak's Travels

A single-page **study companion** to the work of **Amardeep Singh** and **Vininder Kaur**
(Lost Heritage Productions): the major themes, the body of work, an interactive journey map,
and the **complete verbatim text of all 24 episodes** of the *Allegory* docuseries — each with
a timestamped transcript that links straight into the films, and a live full-text search across
everything.

**▶ Live site:** https://komnieve.github.io/allegory-guru-nanak/

---

## A note on attribution

All words here are Amardeep Singh and Vininder Kaur's. This is an **unofficial, freely-offered
companion** for study and reflection — assembled with gratitude and admiration, in the spirit of
the open transmission they themselves practice (the scripts are published as free PDFs and the
films stream free on YouTube). Nothing here is sold or claimed.

Sources — the official *“Script & Discussion Pointers”* PDFs and the (English) *Allegory* YouTube
playlist — live at **[TheGuruNanak.com](https://thegurunanak.com/)** (channel
**[@OnenessInDiversity](https://www.youtube.com/@OnenessInDiversity)**). The films are best watched
there and on YouTube; this page links out to both throughout.

If anything here should be corrected, attributed differently, or removed, please
[open an issue](https://github.com/komnieve/allegory-guru-nanak/issues) — it will be honoured.

## What's inside

- **The throughline** — six ideas that carry the whole body of work
- **The man** — a life timeline, from Muzaffarabad to Singapore to the udasis
- **Body of work** — the four projects as one (the books, *Allegory*, *Oneness in Diversity*, LearnWithNanak)
- **In his own words** — sourced quotations
- **The journey** — an interactive map of the travels across nine countries, a pin per episode
- **All 24 episodes, in full** — verbatim scripts (speaker labels, scripture verses, discussion
  pointers) with a Script ⇄ timestamped-transcript toggle, plus deep links to each film
- **Search** — full-text across all 24 scripts at once
- **Questions the work raises** — eight threads for study, teaching, or conversation

## Build it yourself

The page is generated from the source markdown in `data/` by one script (Python 3 only — no
dependencies):

```bash
ALLEGORY_PUBLIC=1 ALLEGORY_DATA=./data ALLEGORY_OUT=. ALLEGORY_GEO=./data/countries.geo.json \
  python3 build.py
```

That rewrites `index.html`. Source data in `data/`:

| File | What it is |
|------|------------|
| `allegory-english-scripts.md` | the 24 verbatim episode scripts |
| `allegory-english-youtube-transcripts.md` | timestamped YouTube captions |
| `countries.geo.json` | country outlines for the journey map |

The map is rendered to inline SVG at build time, so the page is fully self-contained (the only
runtime dependency is Google Fonts).

## Credits

Content © Amardeep Singh & Vininder Kaur / Lost Heritage Productions. Country geometry from
[`world.geo.json`](https://github.com/johan/world.geo.json). The page markup and build script in
this repo are free to reuse.
