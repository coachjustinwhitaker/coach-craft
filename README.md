# Coach Craft

Reference and sessions for youth soccer coaches, built on the B1 to B5 block framework.

Live site: https://coachjustinwhitaker.github.io/coach-craft/

## What's here

- `U6` to `U12` Coach Companion pages
- `comp/`: competitive methodology for U11 to U14, plus a goalkeeper page
- `coachtool/`: the build tool and brand-free activity library that generate the planner pages

## Rebuild the planner pages

```
cd coachtool
python3 tools/check.py
python3 tools/build.py all
```

Themes live in `coachtool/theme/<id>/`. The default is `coach-craft`. See `coachtool/README.md` to add a club theme.

## Brand

Slate and soft blues on a cool off-white, Inter type, CC monogram logo. Logo files are in `assets/`.
