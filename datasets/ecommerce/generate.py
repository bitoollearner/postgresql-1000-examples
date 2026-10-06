#!/usr/bin/env python3
"""
Generate the ecommerce dataset as COPY-ready TSV.

Deterministic: fixed seed, no wall-clock dependence, no Faker. Running this
on any machine at any time produces byte-identical output, which is what
makes every expected_output.csv in the book reproducible.

Imperfections are INTENTIONAL and load-bearing -- the data quality,
NULL-handling and deduplication chapters need something to find:

  * ~5% of customers never place an order (LEFT JOIN / retention examples)
  * ~8% of products are never ordered (anti-join examples)
  * ~6% of customers have a NULL email
  * a handful of customers are near-duplicates (same person, name variants)
  * some orders have no payment (abandoned)
  * some payments are short-paid or over-paid
  * order_ts spans multiple time zones' worth of offsets
  * a few products have NULL cost_price

Usage:
    python generate.py --size sm --out ./data
    python generate.py --size lg --out ./data
"""
import argparse
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SEED = 20260101
START = date(2023, 1, 1)
END = date(2025, 12, 31)

SIZES = {
    "sm": dict(customers=800, products=200, orders=5_000),
    "lg": dict(customers=250_000, products=20_000, orders=2_000_000),
}

COUNTRIES = [
    ("India", ["Bengaluru", "Mumbai", "Delhi", "Dehradun", "Pune", "Chennai"]),
    ("United States", ["Austin", "Seattle", "Chicago", "Boston", "Denver"]),
    ("Germany", ["Berlin", "Munich", "Hamburg"]),
    ("United Kingdom", ["London", "Manchester", "Bristol"]),
    ("Australia", ["Sydney", "Melbourne", "Perth"]),
    ("Brazil", ["Sao Paulo", "Rio de Janeiro"]),
]
SEGMENTS = ["consumer"] * 6 + ["small_business"] * 3 + ["enterprise"]
STATUSES = ["delivered"] * 6 + ["shipped"] * 2 + ["placed", "cancelled", "returned"]
CHANNELS = ["web"] * 5 + ["mobile"] * 4 + ["store", "partner"]
METHODS = ["card"] * 4 + ["upi"] * 3 + ["wallet", "netbanking", "cod"]
REASONS = ["damaged", "wrong item", "not as described", "changed mind", "late delivery"]

FIRST = ["Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Meera", "James", "Sarah",
         "Michael", "Emma", "Lukas", "Sofia", "Oliver", "Chloe", "Mateus", "Isabel",
         "Ravi", "Divya", "Thomas", "Hannah", "Arjun", "Kavya", "Daniel", "Laura"]
LAST = ["Sharma", "Patel", "Reddy", "Nair", "Iyer", "Smith", "Johnson", "Brown",
        "Muller", "Schmidt", "Silva", "Santos", "Wilson", "Taylor", "Gupta", "Bose",
        "Kumar", "Menon", "Fischer", "Weber", "Costa", "Oliveira", "Clark", "Lewis"]

CATEGORIES = [
    (1, "Electronics", None), (2, "Home & Kitchen", None), (3, "Apparel", None),
    (4, "Books", None), (5, "Sports", None),
    (10, "Laptops", 1), (11, "Phones", 1), (12, "Audio", 1),
    (20, "Cookware", 2), (21, "Furniture", 2),
    (30, "Men", 3), (31, "Women", 3),
    (40, "Fiction", 4), (41, "Technical", 4),
    (50, "Fitness", 5), (51, "Outdoor", 5),
]
LEAF_CATS = [c[0] for c in CATEGORIES if c[2] is not None]

NOUNS = ["Pro", "Air", "Max", "Lite", "Ultra", "Classic", "Prime", "Edge",
         "Nova", "Vertex", "Quantum", "Summit", "Atlas", "Orbit", "Delta"]
STEMS = ["Zenith", "Kestrel", "Halcyon", "Ironwood", "Lumen", "Corvus", "Pallas",
         "Meridian", "Basalt", "Vireo", "Tessera", "Onyx"]


def daterange_pick(rng, start=START, end=END):
    return start + timedelta(days=rng.randint(0, (end - start).days))


def write(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join("\\N" if v is None else str(v) for v in r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", choices=SIZES, default="sm")
    ap.add_argument("--out", default="./data")
    args = ap.parse_args()

    cfg = SIZES[args.size]
    rng = random.Random(SEED)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # ---- categories -------------------------------------------------
    write(out / "categories.tsv", CATEGORIES)

    # ---- customers --------------------------------------------------
    customers = []
    for cid in range(1, cfg["customers"] + 1):
        fn, ln = rng.choice(FIRST), rng.choice(LAST)
        country, cities = rng.choice(COUNTRIES)
        email = None if rng.random() < 0.06 else f"{fn.lower()}.{ln.lower()}{cid}@example.com"
        customers.append([
            cid, fn, ln, email, country, rng.choice(cities),
            daterange_pick(rng, START, date(2025, 6, 30)),
            rng.choice(SEGMENTS),
            "true" if rng.random() > 0.12 else "false",
        ])

    # Plant near-duplicates for the dedup / data-quality chapters:
    # same human, inconsistent casing and whitespace, different id.
    next_id = cfg["customers"] + 1
    for src in rng.sample(customers, max(4, cfg["customers"] // 200)):
        customers.append([
            next_id, src[1].upper(), f" {src[2]} ", src[3], src[4], src[5],
            src[6], src[7], src[8],
        ])
        next_id += 1
    write(out / "customers.tsv", customers)
    n_cust = len(customers)

    # Reserve the top ~5% of customer ids as NON-BUYERS: they exist in the
    # customers table and appear in no order. Chapters 14 (LEFT JOIN zero-vs-NULL)
    # and 21 (retention, churn) both need customers with no child rows. Without
    # them, every LEFT JOIN in the book behaves like an inner join and the
    # lesson has nothing to show.
    n_buyers = int(n_cust * 0.95)

    # ---- products ---------------------------------------------------
    products = []
    for pid in range(1, cfg["products"] + 1):
        price = round(rng.uniform(5, 2500), 2)
        cost = None if rng.random() < 0.04 else round(price * rng.uniform(0.45, 0.8), 2)
        launched = daterange_pick(rng, date(2022, 1, 1), date(2025, 6, 30))
        disc = None
        if rng.random() < 0.08:
            disc = launched + timedelta(days=rng.randint(200, 900))
        products.append([
            pid, f"{rng.choice(STEMS)} {rng.choice(NOUNS)} {rng.randint(100, 999)}",
            rng.choice(LEAF_CATS), price, cost, launched, disc,
        ])
    write(out / "products.tsv", products)

    # Reserve the top ~8% of product ids as NEVER ORDERED. Anti-join examples
    # (NOT EXISTS, LEFT JOIN ... IS NULL) need products with no child rows, in
    # the same way the non-buyer customers above are needed. Without them every
    # anti-join in the book returns an empty result and teaches nothing.
    n_sellable = int(len(products) * 0.92)

    # ---- orders, items, payments, returns ---------------------------
    orders, items, payments, returns = [], [], [], []
    pay_id = ret_id = 1
    offsets = ["+00", "+05:30", "-05", "+01", "+10"]

    for oid in range(1, cfg["orders"] + 1):
        cust = rng.randint(1, n_buyers)          # never picks a reserved non-buyer
        d = daterange_pick(rng)
        ts = f"{d} {rng.randint(0,23):02d}:{rng.randint(0,59):02d}:{rng.randint(0,59):02d}{rng.choice(offsets)}"
        status = rng.choice(STATUSES)
        orders.append([oid, cust, ts, status, rng.choice(CHANNELS),
                       round(rng.uniform(0, 25), 2)])

        total = 0.0
        for line in range(1, rng.randint(1, 5) + 1):
            p = products[rng.randint(0, n_sellable - 1)]
            qty = rng.randint(1, 6)
            disc = rng.choice([0, 0, 0, 5, 10, 15, 20])
            unit = float(p[3])
            items.append([oid, line, p[0], qty, unit, disc])
            total += qty * unit * (1 - disc / 100)

        # ~8% of orders are never paid -> reconciliation examples
        if status != "cancelled" and rng.random() > 0.08:
            amt = round(total, 2)
            if rng.random() < 0.03:                 # short-pay / over-pay anomalies
                amt = round(amt * rng.choice([0.9, 1.1]), 2)
            payments.append([pay_id, oid,
                             f"{d} {rng.randint(0,23):02d}:{rng.randint(0,59):02d}:00+00",
                             amt, rng.choice(METHODS)])
            pay_id += 1

        if status == "returned":
            returns.append([ret_id, oid, 1, d + timedelta(days=rng.randint(1, 30)),
                            rng.choice(REASONS), round(total * rng.uniform(0.2, 1.0), 2)])
            ret_id += 1

    write(out / "orders.tsv", orders)
    write(out / "order_items.tsv", items)
    write(out / "payments.tsv", payments)
    write(out / "returns.tsv", returns)

    print("\n!! The dataset has been regenerated. Every expected_output.csv and\n"
          "!! explain.txt in examples/ is now potentially stale. Run:\n"
          "!!     python run.py capture\n"
          "!! then review any plan-shape diffs before committing.\n")
    print(f"size={args.size} customers={n_cust} (buyers={n_buyers}) "
          f"products={len(products)} "
          f"orders={len(orders)} items={len(items)} payments={len(payments)} "
          f"returns={len(returns)}")


if __name__ == "__main__":
    main()
