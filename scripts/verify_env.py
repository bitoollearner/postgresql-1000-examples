#!/usr/bin/env python3
"""
Report whether this environment matches the one the book was verified against.

Paste the output into any errata report. Most reports that turn out not to be
errata come from a cluster whose collation or planner settings differ, and
those are exactly what this prints.

    python scripts/verify_env.py
    docker exec -it pg1000-practice python3 /opt/verify_env.py
"""
import os
import subprocess
import sys

DSN = os.environ.get("BOOK_DSN", "postgresql://book:book@localhost:5432/pg1000")

# setting -> what the book needs it to be
EXPECTED = {
    "max_parallel_workers_per_gather": "0",
    "max_parallel_workers": "0",
    "jit": "off",
    "work_mem": "4096",                 # kB
    "default_statistics_target": "1000",
    "DateStyle": "ISO, YMD",
    "TimeZone": "UTC",
}

COUNTS = {
    "ecommerce.order_items": 14998,
    "ecommerce.orders": 5000,
    "hr.employees": 1200,
}


def q(sql):
    r = subprocess.run(["psql", DSN, "-tAX", "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def main():
    if q("SELECT 1") is None:
        print(f"Cannot connect to {DSN}")
        print("Is the container running?  docker ps")
        return 2

    ok = True
    print("=" * 60)
    print("PostgreSQL: 1,000 Examples -- environment check")
    print("=" * 60)
    print(f"server      {q('SHOW server_version')}")

    coll = q("SELECT datcollate FROM pg_database "
             "WHERE datname = current_database()")
    enc = q("SELECT pg_encoding_to_char(encoding) FROM pg_database "
            "WHERE datname = current_database()")
    mark = "ok " if coll == "C" else "BAD"
    print(f"[{mark}] collation   {coll}   (must be C)")
    print(f"      encoding    {enc}")
    if coll != "C":
        ok = False
        print("      -> Text sorts differently from the book. The cluster must")
        print("         be recreated with: initdb --locale=C")

    print("-" * 60)
    for name, want in EXPECTED.items():
        got = q(f"SELECT setting FROM pg_settings WHERE name = '{name}'")
        good = (got or "").lower() == want.lower()
        ok = ok and good
        print(f"[{'ok ' if good else 'BAD'}] {name:<34} {got}"
              f"{'' if good else f'   (expected {want})'}")

    print("-" * 60)
    for rel, want in COUNTS.items():
        got = q(f"SELECT count(*) FROM {rel}")
        if got is None:
            print(f"[   ] {rel:<34} not loaded")
            continue
        good = int(got) == want
        ok = ok and good
        print(f"[{'ok ' if good else 'BAD'}] {rel:<34} {got}"
              f"{'' if good else f'   (expected {want})'}")

    lg = q("SELECT count(*) FROM ecommerce_lg.orders")
    print(f"[   ] ecommerce_lg.orders              "
          f"{lg if lg else 'not loaded (Part VIII needs it)'}")

    ext = q("SELECT string_agg(extname, ', " "' ORDER BY extname) "
            "FROM pg_extension")
    print("-" * 60)
    print(f"extensions  {ext}")
    print("=" * 60)
    print("PASS -- this environment matches the book" if ok else
          "MISMATCH -- see the BAD lines above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
