# Brand discovery for the identity kit

The kit's colours and fonts must come from the customer, with a source for each. This page says where to look, how to read it and how to record it.

## 1. Sources, most trusted first

| Source | What it gives | How |
|---|---|---|
| Brand portal or brand guide | official colours, names, fonts, logo rules | ask the account team or the customer's communications contact; read the PDF |
| Customer-authored Office file (deck, template, .thmx) | theme colours (dark 1-2, light 1-2, accent 1-6) and theme fonts | attach it to the chat; `read_office_theme.py` |
| Customer website | interface colours (buttons, links, backgrounds) | browse the site with the user; note the hex values and the date |
| Blueprint colours | journey colours chosen during envisioning | fallback only; flagged in the seed report |

A deck the customer sent is good evidence of their theme; a Microsoft deck about the customer is not. If the theme and the website differ (common for orange and blue tones), prefer the shade that reaches 4.5:1 and note both.

## 2. Reading an Office theme

```bash
python scripts/read_office_theme.py "input/<Customer> template.potx" --out working/identity/<slug>/brand.json \
       --customer "<Customer legal name>" --short <Customer> --evidence-id E12
```
Presentations use the theme of the first slide master; documents and workbooks use their theme part. The script writes the twelve theme colours, the heading and body fonts, and named entries (`"<Customer> accent1"` …). Rename the colours to the customer's own names where the brand guide gives them ("Caldova Blue").

## 3. The brand file (`frontier-brand/1.0`)

```json
{
  "schema": "frontier-brand/1.0",
  "customer": "Caldova Industrial AG", "short": "Caldova",
  "status": "Derived from Caldova's Office theme and website; validate with the brand owner before production.",
  "sourceShort": "Caldova's Office theme 'Caldova Corporate' (E10) and caldova.example (E11)",
  "sources": {"theme": "...", "website": "..."},
  "theme": {"name": "Caldova Corporate", "dk1": "#1F2A33", "accent1": "#0F6CBD", "...": "...", "fonts": {"headings": "Aptos Display", "body": "Aptos"}},
  "named": [{"name": "Caldova Blue", "hex": "#0F6CBD", "slot": "accent1", "source": "theme accent 1 (E10)"}],
  "journeyColours": {"D2": "Caldova Violet"},
  "evidence": [{"id": "E10", "title": "Caldova Corporate Office theme", "date": "2026-10-30", "usedFor": "palette, fonts"}],
  "logo": null
}
```
`journeyColours` is optional and overrides the automatic mapping for a journey. `evidence` entries flow into the kit's `docs/evidence.md`.

## 4. Logos and fonts

- Logos are trademarks. Include one (`make_kit.py --logo`) only when the customer's brand rules allow it and the file comes from the customer; otherwise the cards show the customer's short name as a wordmark.
- Theme fonts are often not installed on client devices or build agents. The kit names the brand fonts and falls back to Arial for cards, pages and Adaptive Cards.

## 5. Recording and validating

- Every colour in `named` has a `source` with an evidence id; nothing is guessed.
- The seed report lists every journey colour, its contrast and any adjustment (dark glyph or accessible shade).
- Decision N-5 (colours confirmed by the brand owner) stays open until the customer confirms.
