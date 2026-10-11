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
| `Dockerfile`, `Caddyfile` | Railway build and deploy. Runs `build.py`. |

## Working locally instead

```bash
cp ~/photos/* site/photos/
python3 build.py          # then open site/index.html
git add -A && git commit -m "photos" && git push
```

## Deploying

Live on Railway at https://site-production-ff11.up.railway.app — redeploys on
every push to `main`. The Docker build shrinks the photos and runs `build.py`,
so nothing needs running locally.

A free GitHub Pages mirror is also possible (Settings → Pages → Source: GitHub
Actions, plus a workflow file). Not set up.

## Custom domain

Pages: Settings → Pages → Custom domain. Railway: service → Settings →
Networking → Custom Domain. Point a CNAME at the host they give you.
