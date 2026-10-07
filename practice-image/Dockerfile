# ---------------------------------------------------------------------------
# bilearner/postgres1000-practice
#
# One image, everything ready: PostgreSQL 16.15 with the book's seeded
# datasets already loaded, JupyterLab, and all 53 chapter notebooks. Run it
# and start practising -- no dataset generation, no loading, no configuration.
#
#   docker run -d -p 8888:8888 -p 5432:5432 bilearner/postgres1000-practice:1.1
# ---------------------------------------------------------------------------
FROM postgres:16.15-bookworm

LABEL org.opencontainers.image.title="PostgreSQL: 1,000 Examples -- Practice Environment" \
      org.opencontainers.image.description="PostgreSQL 16.15 with the book's seeded datasets preloaded, JupyterLab, and all 53 chapter notebooks." \
      org.opencontainers.image.authors="Bi Learner" \
      org.opencontainers.image.source="https://github.com/bitoollearner/postgresql-1000-examples" \
      org.opencontainers.image.licenses="MIT"

# The cluster locale is pinned to C, and this is not a detail.
#
# Text sort order depends on collation. Under C, ORDER BY on text is plain
# byte order and uppercase sorts before lowercase; under en_US.utf8 or
# C.UTF-8 it does not. Every captured output in the book that sorts mixed-case
# text depends on this. initdb takes its locale from the environment and the
# base image's default has changed between releases, so it is set explicitly
# rather than inherited.
#
# POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB are deliberately NOT set.
# The official image's entrypoint reads them, and this image replaces that
# entrypoint entirely -- so they did nothing here except bake a credential
# into the image metadata and trip BuildKit's SecretsUsedInArgOrEnv lint. The
# role, database and password are created explicitly in the build below.
ENV LANG=C \
    LC_ALL=C \
    PGDATA=/var/lib/pgsql/data \
    PRACTICE_DIR=/practice \
    JUPYTER_PORT=8888 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

# PYTHONUTF8 is set because LC_ALL=C is set. Current Pythons coerce a C locale
# to C.UTF-8 (PEP 538) and are fine either way, but that behaviour belongs to
# the base image rather than to us -- and the notebooks are full of en dashes,
# so losing it would surface as a UnicodeDecodeError opening a notebook, which
# is a baffling thing to debug from a locale setting three layers away.

# PGDATA is deliberately NOT /var/lib/postgresql/data. The official image
# declares that path as a VOLUME, so anything written there during the build
# is discarded -- the seeded cluster would vanish from the image.

USER root

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        python3 python3-venv curl tini; \
    rm -rf /var/lib/apt/lists/*

# A venv keeps pip off the system Python, which Debian protects (PEP 668).
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY practice-image/requirements-practice.txt /tmp/requirements-practice.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements-practice.txt

COPY conf/postgresql.conf /etc/postgresql/postgresql.conf
COPY conf/initdb/        /opt/book-initdb/
COPY conf/psqlrc         /etc/psqlrc
COPY datasets/           /opt/book-datasets/

# ---- Build the seeded cluster into the image ------------------------------
# initdb, start, create the extensions and schemas, generate and load the
# data, then shut down cleanly. Doing all of this at build time is what makes
# the image start in seconds with nothing to load.
#
# The appended pg_hba.conf line is what makes the published port usable at
# all. `initdb --auth=trust` writes rules for the Unix socket and for
# 127.0.0.1 only; a connection from the host through `-p 5432:5432` reaches
# PostgreSQL from the Docker bridge address instead, matches no rule, and is
# refused with "no pg_hba.conf entry for host". The official image's
# entrypoint adds this line itself, which is why bypassing that entrypoint
# means adding it here. scram-sha-256 rather than trust, so the port that is
# exposed to the network actually asks for the password the docs give.
#
# ANALYZE, not VACUUM ANALYZE, because that is what the book's loader runs.
# VACUUM creates the free space and visibility map forks, which
# pg_total_relation_size counts -- so a vacuumed cluster reports every table
# as larger and example 909, which prints those sizes, no longer matches.
RUN set -eux; \
    mkdir -p "$PGDATA"; \
    chown -R postgres:postgres "$PGDATA" /opt/book-datasets /etc/postgresql \
                               /opt/book-initdb; \
    su postgres -s /bin/bash -c 'set -eux; \
      initdb -D "$PGDATA" --username=book --auth=trust \
             --encoding=UTF8 --locale=C >/dev/null; \
      export PGUSER=book; \
      printf "host all all all scram-sha-256\n" >> "$PGDATA/pg_hba.conf"; \
      pg_ctl -D "$PGDATA" -w -t 60 \
        -o "-c config_file=/etc/postgresql/postgresql.conf -c listen_addresses=" \
        start; \
      psql -v ON_ERROR_STOP=1 -d postgres \
           -c "CREATE DATABASE pg1000 OWNER book;"; \
      psql -v ON_ERROR_STOP=1 -d pg1000 \
           -c "ALTER USER book WITH PASSWORD '"'"'book'"'"';"; \
      for f in /opt/book-initdb/*.sql; do \
        psql -v ON_ERROR_STOP=1 -d pg1000 -f "$f"; \
      done; \
      python3 /opt/book-datasets/ecommerce/generate.py --size sm \
              --out /opt/book-datasets/ecommerce/data; \
      psql -v ON_ERROR_STOP=1 -d pg1000 -v schema=ecommerce \
           -f /opt/book-datasets/ecommerce/ddl.sql; \
      for t in categories customers products orders order_items payments returns; do \
        psql -v ON_ERROR_STOP=1 -d pg1000 \
             -c "\copy ecommerce.$t FROM /opt/book-datasets/ecommerce/data/$t.tsv"; \
      done; \
      python3 /opt/book-datasets/hr/generate.py \
              --out /opt/book-datasets/hr/data; \
      psql -v ON_ERROR_STOP=1 -d pg1000 -v schema=hr \
           -f /opt/book-datasets/hr/ddl.sql; \
      for t in departments salary_bands employees compensation \
               performance_reviews requisitions applications absences; do \
        psql -v ON_ERROR_STOP=1 -d pg1000 \
             -c "\copy hr.$t FROM /opt/book-datasets/hr/data/$t.tsv"; \
      done; \
      psql -v ON_ERROR_STOP=1 -d pg1000 -c "ANALYZE;"; \
      python3 /opt/book-datasets/stamp_fingerprint.py; \
      pg_ctl -D "$PGDATA" -w -m fast stop'; \
    rm -rf /opt/book-datasets/ecommerce/data /opt/book-datasets/hr/data

# ---- Notebooks ------------------------------------------------------------
# Copied to a pristine location. The entrypoint seeds /practice from it on
# first run, so a mounted volume gets the notebooks and the reader's edits
# survive restarts.
COPY notebooks            /opt/book-notebooks
COPY docs/chapters        /opt/book-notebooks/_chapter-index
COPY practice-image/WELCOME.md /opt/book-notebooks/START-HERE.md
COPY practice-image/entrypoint.sh      /usr/local/bin/practice-entrypoint
COPY scripts/load_large_dataset.sh     /usr/local/bin/load-large-dataset
COPY scripts/verify_env.py             /opt/verify_env.py

RUN chmod +x /usr/local/bin/practice-entrypoint \
             /usr/local/bin/load-large-dataset && \
    mkdir -p "$PRACTICE_DIR" && \
    chown -R postgres:postgres /opt/book-notebooks "$PRACTICE_DIR" "$PGDATA"

EXPOSE 5432 8888
VOLUME ["/practice"]

HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=5 \
  CMD pg_isready -U book -d pg1000 -q && \
      curl -sf "http://localhost:${JUPYTER_PORT}/api" >/dev/null || exit 1

# tini reaps the two long-running processes, so Ctrl-C actually stops the
# container instead of leaving orphans behind.
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/practice-entrypoint"]
