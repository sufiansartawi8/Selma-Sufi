# 100 Reasons

A single static page. Photo on top with a shuffle button, one reason that
changes daily, then all one hundred.

## Adding photos

Go to `site/photos/` on github.com → **Add file** → **Upload files** → drag
them in → **Commit changes**.

That's the whole job. Every push triggers a build that shrinks the photos,
regenerates the page, and redeploys. Any filename works, any number of photos,
no list to update, nothing to run. Deleting a photo works the same way.

Full-size phone photos are fine to upload — the build resizes the deployed
copies to 2000px and strips metadata. The originals stay in the repo as you
uploaded them.

## Changing the list

Edit `reasons.md` on github.com and commit. The page rebuilds.

## Files

| Path | What it is |
|---|---|
| `reasons.md` | The list. Source of truth. |
| `site/photos/` | The photos. Everything in here gets picked up. |
| `build.py` | Generates `site/index.html` from those two. CI runs it. |
| `site/index.html` | Generated. Don't edit; it gets overwritten each build. |
| `.github/workflows/pages.yml` | Build and deploy to GitHub Pages. |
| `Dockerfile`, `Caddyfile` | Railway deployment, if you ever want it. |

## Working locally instead

```bash
cp ~/photos/* site/photos/
python3 build.py          # then open site/index.html
git add -A && git commit -m "photos" && git push
```

## Deploying

**GitHub Pages** — Settings → Pages → Source: **GitHub Actions**. Free. Needs
a public repo unless the account is on GitHub Pro.

**Railway** — New Project → Deploy from GitHub repo. Reads the `Dockerfile`,
serves `site/` with Caddy on `$PORT`. Works with private repos. Costs money
after the trial credit.

## Custom domain

Pages: Settings → Pages → Custom domain. Railway: service → Settings →
Networking → Custom Domain. Point a CNAME at the host they give you.
