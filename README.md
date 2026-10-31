# گرامر آلمانی به فارسی — German Grammar for Persian Speakers

A self-contained, offline single-page web app that teaches German grammar from **A1.1 to B2.2** in Persian, lesson by lesson, following the order of common textbooks (Menschen, Momente, Linie 1).

**Read the lessons online:** https://lingoping.com/fa/german-grammar/

**Offline:** download [`dist/german-grammar-fa.html`](dist/german-grammar-fa.html) and open it in any browser. No internet connection or installation needed.

## Features

- 99 grammar lessons across 8 sub-levels, plus 4 reference appendices (tenses, declension tables, irregular verbs, verbs/adjectives with prepositions)
- Every lesson compares the German structure with Persian grammar
- Cross-links back to earlier lessons, with a "back to where you were" button
- Tables, audio examples (browser text-to-speech), self-check quizzes
- Full-text search in Persian and German (tolerates `ae/oe/ue/ss` spellings)
- Gender colour-coding (der / die / das / plural), progress tracking, dark mode, adjustable text size
- Material Design 3, RTL, mobile-friendly

## Project layout

| Path | Contents |
|---|---|
| `content/*.txt` | Lesson sources in a small Markdown-like format (see below) |
| `template.html` | App shell: styles and JavaScript |
| `build.py` | Builds `dist/german-grammar-fa.html` from the content and template |
| `vendor/` | Vazirmatn font (SIL Open Font License) |
| `tests/` | Playwright checks and screenshot scripts |

## Building

```bash
python3 build.py
```

The build fails (exit code 1) if any cross-link points to a lesson or section that doesn't exist.

## Content format

Each lesson starts with `@@ lesson-id`, a header (`level`, `title`, `de`, `tags`, `summary`), then `---` and the body:

- `## Heading {#anchor}` — section (linkable)
- `` `German text` `` — German span (LTR); `**bold**`, `~~wrong form~~`
- `{m|der Tisch}` / `{f|…}` / `{n|…}` / `{p|…}` — gender colouring
- `[[lesson-id]]` or `[[lesson-id#anchor|label]]` — cross-link
- `> German sentence = Persian translation` — example with audio button
- `:::tip|fa|warn|note|rule|remember Title` … `:::` — callout boxes
- `?? question => answer` — quiz item
- Markdown tables (`| a | b |`) and lists
