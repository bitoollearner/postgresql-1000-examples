#!/usr/bin/env python3
"""Record the dataset fingerprint, as `run.py load-sm` does in the book repo.

Hashes the generator and DDL that produced the loaded data and stores the
result, so the book's validator can confirm this database matches the dataset
its expected outputs were captured against.
"""
import hashlib
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
SOURCES = [HERE / "ecommerce" / "generate.py", HERE / "ecommerce" / "ddl.sql"]
USER = os.environ.get("PGUSER", "book")
DB = os.environ.get("PGDATABASE", "pg1000")


def main():
    h = hashlib.sha256()
    for f in SOURCES:
        h.update(f.read_bytes())
    fp = h.hexdigest()[:16]

    for sql in (
        "CREATE SCHEMA IF NOT EXISTS book_meta;",
        "CREATE TABLE IF NOT EXISTS book_meta.dataset_fingerprint "
        "(id int PRIMARY KEY DEFAULT 1, fingerprint text NOT NULL, "
        "loaded_at timestamptz NOT NULL DEFAULT now(), CHECK (id = 1));",
        f"INSERT INTO book_meta.dataset_fingerprint (id, fingerprint) "
        f"VALUES (1, '{fp}') ON CONFLICT (id) DO UPDATE "
        f"SET fingerprint = EXCLUDED.fingerprint, loaded_at = now();",
    ):
        subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
                        "-U", USER, "-d", DB, "-c", sql], check=True)
    print(f"dataset fingerprint {fp} stamped")


if __name__ == "__main__":
    main()
