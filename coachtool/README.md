# Coach tool (prototype)

Brand-free records in, pages out.

- `data/activities/`: one file per activity. The library.
- `data/plans/`: one file per age and track. Weeks refer to activities by id.
- `data/blocks.yaml`: block names and group headings.
- `rules/ladder.yaml`: which blocks and levels each age and track uses.
- `theme/<brand>/`: name, logo and wording for one brand. Nothing else mentions a brand.
- `templates/`: page shells with `{{tokens}}`.
- `tools/check.py`: validates the records. `tools/build.py <plan> <brand>`: writes `build/<plan>.<brand>.html`.

Run: `python3 tools/check.py` then `python3 tools/build.py all (builds with the Coach Craft theme; pass a club id to use another, e.g. `all coach-craft`)`.

## Adding activities and diagrams
- Easiest: open `build/activity-builder.html` (made by `python3 tools/build.py author`), add activities or load one to edit, download the batch, then run `python3 tools/import_csv.py activity-batch.json`.
- Or fill in `data/templates/activities-template.csv` (one row per activity; lists use semicolons), then run `python3 tools/import_csv.py yourfile.csv`. It checks everything and keeps nothing if a row fails. Add `--update` to overwrite existing ids.
- Diagrams: export a PNG, JPG, WebP or SVG, put it in `data/diagrams/`, and put the file name in the `diagram` column (or the `diagram:` field of the record). Keep them brand-free. The app embeds them at up to 720px wide.

## Core and club layers
Core records (`data/`) are brand-free. Club-specific content lives in `theme/<club>/`: `club.yaml` for names, colors, logo, contact and feedback links, and `overlay/<age>.yaml` for things like game format, local rules and pathway text. Test: would another club change it? Yes means overlay. Delete the overlay folder and the app shows core content only.

## Adding a club
1. `python3 tools/new_club.py <id>` writes a labeled blank `theme/<id>/club.yaml`.
2. Fill it in and add the two logo files. Every field is described in `rules/club-fields.yaml`.
3. `python3 tools/club_check.py <id>` lists what is missing. Required fields stop the build. Recommended ones only warn, and the feature is hidden or generic.
4. Add `overlay/<age>.yaml` for any age where your game format, rules or pathway differ from the core.
