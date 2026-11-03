# nairaexchangerate

Daily Naira exchange rates website (nairaexchangerate.com), hosted on Netlify.

## How it works
- `index.html` is the whole site. Netlify publishes it on every push to `main`.
- Mid-market rates for 15 currencies load live in the visitor's browser each day.
- The editable data (official CBN rates, UK dealer rate, news, partner links) lives in the
  `<script id="site-data">` block inside `index.html`.

## Updating the data
Write a small JSON patch and run:

    python3 scripts/update_site.py patch.json

Keys: `cbn`, `parallel`, `news`, `partners`, `whatsappChannel` (see the script for formats).

## Daily update
- CBN rates: published each business day around 18:00 Lagos time.
- UK dealer rate: from the daily "NAIRA RATE" email in Gmail.
- News: the 6 latest Nigerian economy and money headlines, summarised in our own words and linked to the source.
