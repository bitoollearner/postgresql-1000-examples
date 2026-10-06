# The practice image

Published as [`bilearner/postgres1000-practice`](https://hub.docker.com/r/bilearner/postgres1000-practice).

## Using it

See the [repository README](https://github.com/bitoollearner/postgresql-1000-examples#start-practising-in-one-command).

## Building it yourself

From the repository root — note the context is the root, not this folder,
because the build needs `conf/`, `datasets/`, `notebooks/` and `docs/`:

```bash
docker build -f practice-image/Dockerfile -t bilearner/postgres1000-practice:dev .
```

Roughly five minutes, most of it generating and loading the datasets.

```bash
docker run -d --name pg1000-dev -p 8888:8888 -p 5432:5432 bilearner/postgres1000-practice:dev
docker logs -f pg1000-dev
```

## What the build does

1. Starts from `postgres:16.15-bookworm`.
2. Installs Python, JupyterLab and the SQL tooling into a venv.
3. Runs `initdb` **with `--locale=C`** into `/var/lib/pgsql/data`.
4. Installs the book's extensions from `conf/initdb/`.
5. Generates and loads `ecommerce` and `hr` from the seeded generators.
6. `VACUUM ANALYZE`, then a clean shutdown.
7. Copies the notebooks to `/opt/book-notebooks`.

Two details matter more than they look:

**`PGDATA` is `/var/lib/pgsql/data`, not `/var/lib/postgresql/data`.** The
official image declares the latter as a `VOLUME`, and anything written to a
declared volume during a build is discarded. Seeding the cluster there would
produce an image that appears to build correctly and starts up empty.

**`initdb --locale=C`.** Text sort order depends on collation. Under `C` it is
byte order and uppercase sorts before lowercase; under `C.UTF-8` or
`en_US.utf8` it does not. Every ordered result in the book that contains
mixed-case text depends on this, and getting it wrong breaks a large number of
examples in a way that looks like broken SQL rather than a locale setting.

## Publishing

`.github/workflows/docker-image.yml` builds and pushes on a version tag:

```bash
git tag v1.0 && git push origin v1.0
```

It builds `linux/amd64` and `linux/arm64`, pushes `:1.0` and `:latest`, and
updates the Docker Hub description from `DOCKERHUB.md`.

Requires two repository secrets: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`
(a Docker Hub access token with Read/Write, not your password).
