# Changelog

## 1.1

- Notebooks reorganised into one folder per chapter, so each chapter has
  somewhere for your own scratch queries and notes.
- Part VIII notebooks now check for the large dataset themselves and say
  whether you are ready, instead of relying on a note you have to remember.
- Docker Desktop install links in the README and setup guide.
- `scripts/test_image.ps1` - an acceptance test you can run against the
  published image.
- Fixed: the published port refused external connections. `initdb --auth=trust`
  writes rules for the Unix socket and 127.0.0.1 only, so pgAdmin, DBeaver and
  every other client arriving from the Docker bridge was rejected with
  "no pg_hba.conf entry for host". The image now adds a `scram-sha-256` rule
  for external addresses, so the documented password is actually required and
  actually works.
- Removed `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` from the image:
  the official entrypoint reads them and this image replaces that entrypoint,
  so they only baked a credential into the image metadata.

## 1.0

First public release.

- Practice image `bilearner/postgres1000-practice:1.1` — PostgreSQL 16.15 with the
  `ecommerce` and `hr` schemas preloaded, JupyterLab, and all 53 chapter
  notebooks.
- 1000 examples indexed across 53 chapters.
- `ecommerce_lg` loadable on demand for Part VIII.
- Server configuration copied verbatim from the book's own build, so plans and
  printed output reproduce.
