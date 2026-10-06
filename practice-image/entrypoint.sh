#!/usr/bin/env bash
# Starts PostgreSQL and JupyterLab together, then hands the terminal to
# Jupyter so the container's lifetime follows it.
set -euo pipefail

PGDATA="${PGDATA:-/var/lib/pgsql/data}"
PRACTICE_DIR="${PRACTICE_DIR:-/practice}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
JUPYTER_TOKEN="${JUPYTER_TOKEN:-}"

echo "-------------------------------------------------------------"
echo " PostgreSQL: 1,000 Examples -- practice environment"
echo "-------------------------------------------------------------"

# Seed /practice on first run. A mounted volume starts empty, so this is what
# puts the notebooks in front of the reader; on later runs their edited copies
# are left exactly as they were.
if [ -z "$(ls -A "$PRACTICE_DIR" 2>/dev/null || true)" ]; then
  echo ">> first run: copying notebooks into $PRACTICE_DIR"
  cp -r /opt/book-notebooks/. "$PRACTICE_DIR"/
else
  echo ">> $PRACTICE_DIR already has content; leaving your work untouched"
fi
chown -R postgres:postgres "$PRACTICE_DIR" 2>/dev/null || true

echo ">> starting PostgreSQL ..."
su postgres -s /bin/bash -c "pg_ctl -D '$PGDATA' \
  -o '-c config_file=/etc/postgresql/postgresql.conf -c listen_addresses=*' \
  -w -t 60 start" >/dev/null

until pg_isready -U book -d pg1000 -q; do sleep 1; done

ORDERS=$(psql -U book -d pg1000 -tAX -c \
  'SELECT count(*) FROM ecommerce.order_items' 2>/dev/null || echo '?')
STAFF=$(psql -U book -d pg1000 -tAX -c \
  'SELECT count(*) FROM hr.employees' 2>/dev/null || echo '?')
COLL=$(psql -U book -d pg1000 -tAX -c \
  "SELECT datcollate FROM pg_database WHERE datname='pg1000'" 2>/dev/null || echo '?')

echo ">> PostgreSQL ready"
echo "   ecommerce.order_items  $ORDERS rows"
echo "   hr.employees           $STAFF rows"
echo "   collation              $COLL"

if [ "$COLL" != "C" ]; then
  echo "   WARNING: collation is not C. Text sort order will differ from the"
  echo "            book, and ordered results will not match."
fi

# No token by default: this is a local practice container and a token in the
# URL is friction. Set JUPYTER_TOKEN to turn it back on.
echo ""
echo "   Open:  http://localhost:${JUPYTER_PORT}/lab"
echo "   psql:  docker exec -it \$(hostname) psql -U book -d pg1000"
echo "   DSN:   postgresql://book:book@localhost:5432/pg1000"
echo ""
echo "   Part VIII needs the large dataset:"
echo "          docker exec -it \$(hostname) load-large-dataset"
echo ""
echo "   Start with START-HERE.md, then open any chapter notebook."
echo "-------------------------------------------------------------"

exec su postgres -s /bin/bash -c "cd '$PRACTICE_DIR' && \
  jupyter lab \
    --ip=0.0.0.0 \
    --port='$JUPYTER_PORT' \
    --no-browser \
    --ServerApp.root_dir='$PRACTICE_DIR' \
    --IdentityProvider.token='$JUPYTER_TOKEN'"
