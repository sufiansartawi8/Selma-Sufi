# Build stage: shrink the photos, regenerate the page.
# This is what makes "upload photos on github.com" enough on its own.
FROM python:3.12-alpine AS build
RUN apk add --no-cache imagemagick
WORKDIR /app
COPY . .
RUN set -e; \
    find site/photos -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -print0 \
      | xargs -0 -r magick mogrify -auto-orient -strip -resize '2000x2000>' -quality 82; \
    python3 build.py

FROM caddy:2.8-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/site /srv
