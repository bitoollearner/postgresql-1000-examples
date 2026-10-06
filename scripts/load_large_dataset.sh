#!/usr/bin/env bash
# Generate and load ecommerce_lg, the 2,000,000-order dataset Part VIII needs.
#
#   docker exec -it pg1000-practice load-large-dataset
#
# About three minutes and 850 MB. It is not baked into the image because that
# cost would be paid by every reader for the one part that uses it.
set -euo pipefail

DATA=/tmp/ecommerce_lg
DB=${PGDATABASE:-pg1000}
USER=${PGUSER:-book}
GEN=/opt/book-datasets/ecommerce/generate.py
DDL=/opt/book-datasets/ecommerce/ddl.sql

if [ ! -f "$GEN" ]; then
  GEN="$(dirname "$0")/../datasets/ecommerce/generate.py"
  DDL="$(dirname "$0")/../datasets/ecommerce/ddl.sql"
fi

echo ">> generating (about two minutes, no output until it finishes) ..."
mkdir -p "$DATA"
python3 "$GEN" --size lg --out "$DATA"

echo ">> creating schema ecommerce_lg ..."
psql -U "$USER" -d "$DB" -v ON_ERROR_STOP=1 -v schema=ecommerce_lg -f "$DDL"

echo ">> loading ..."
for t in categories customers products orders order_items payments returns; do
  printf '   %-14s' "$t"
  psql -U "$USER" -d "$DB" -v ON_ERROR_STOP=1 \
       -c "\copy ecommerce_lg.$t FROM $DATA/$t.tsv"
done

echo ">> ANALYZE ..."
psql -U "$USER" -d "$DB" -q -c "VACUUM ANALYZE ecommerce_lg.orders, \
  ecommerce_lg.order_items, ecommerce_lg.customers, ecommerce_lg.products, \
  ecommerce_lg.categories, ecommerce_lg.payments, ecommerce_lg.returns;"

rm -rf "$DATA"

N=$(psql -U "$USER" -d "$DB" -tAX -c "SELECT count(*) FROM ecommerce_lg.order_items")
echo ""
echo ">> ecommerce_lg ready -- $N order lines"
echo "   Part VIII examples query ecommerce_lg.* by name; nothing else changes."
