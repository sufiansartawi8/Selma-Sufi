# Build stage: normalise iPhone HEIC, shrink everything, regenerate the page.
# This is what makes "upload photos on github.com" enough on its own.
FROM python:3.12-alpine AS build
RUN apk add --no-cache imagemagick imagemagick-heic imagemagick-jpeg \
                       imagemagick-png imagemagick-webp
WORKDIR /app
COPY . .
RUN set -e; \
    # iPhone shoots HEIC; browsers don't render it. Convert, then drop the original.
    find site/photos -type f \( -iname '*.heic' -o -iname '*.heif' \) -print0 \
      | xargs -0 -r -I{} sh -c 'magick "$1" "${1%.*}.jpg" && rm -f "$1"' _ {}; \
    find site/photos -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -print0 \
      | xargs -0 -r magick mogrify -auto-orient -strip -resize '2000x2000>' -quality 82; \
    python3 build.py

FROM caddy:2.8-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/site /srv
