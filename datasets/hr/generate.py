#!/usr/bin/env python3
"""
Generate the hr dataset as COPY-ready TSV.

Deterministic: fixed seed, no wall-clock dependence, no Faker. Running this
on any machine at any time produces byte-identical output, which is what
makes every expected_output.csv in Chapter 49 reproducible.

NO PROTECTED ATTRIBUTES are generated. See the header of ddl.sql.

Imperfections are INTENTIONAL, as in the ecommerce dataset -- the chapter's
data quality and NULL-handling material needs something to find:

  * ~6% of employees have a NULL work_email
  * two departments have never had an employee
  * some employees report to a manager who has since left
  * a few employees have a gap in compensation history (no current row)
  * contractors have no performance review
  * a handful of requisitions have been open for over a year
  * near-duplicate names (two "Priya Nair", one "Priya  Nair" with a double
    space) for the deduplication material

The reference date is fixed at REPORT_DATE rather than taken from the clock.
Tenure, attrition and headcount all depend on "today", and a dataset whose
answers change overnight cannot be printed in a book.

Usage:
    python generate.py --out ./data
"""
import argparse
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260101
# Every "as of" figure in Chapter 49 is relative to this date, never to now().
REPORT_DATE = date(2026, 1, 1)
FOUNDED = date(2016, 1, 4)

N_EMPLOYEES = 1200

# (dept_id, name, cost_centre, parent_dept_id, location)
DEPARTMENTS = [
    (1,  "Executive",            "CC-1000", None, "Bengaluru"),
    (2,  "Engineering",          "CC-2000", 1,    "Bengaluru"),
    (3,  "Platform",             "CC-2100", 2,    "Bengaluru"),
    (4,  "Data",                 "CC-2200", 2,    "Pune"),
    (5,  "Product Engineering",  "CC-2300", 2,    "Bengaluru"),
    (6,  "Quality Engineering",  "CC-2400", 2,    "Chennai"),
    (7,  "Site Reliability",     "CC-2500", 2,    "Bengaluru"),
    (8,  "Product",              "CC-3000", 1,    "Bengaluru"),
    (9,  "Design",               "CC-3100", 8,    "Bengaluru"),
    (10, "Product Management",   "CC-3200", 8,    "Pune"),
    (11, "Sales",                "CC-4000", 1,    "Mumbai"),
    (12, "Enterprise Sales",     "CC-4100", 11,   "Mumbai"),
    (13, "Inside Sales",         "CC-4200", 11,   "Pune"),
    (14, "Sales Engineering",    "CC-4300", 11,   "Bengaluru"),
    (15, "Marketing",            "CC-5000", 1,    "Mumbai"),
    (16, "Demand Generation",    "CC-5100", 15,   "Mumbai"),
    (17, "Product Marketing",    "CC-5200", 15,   "Bengaluru"),
    (18, "Customer Success",     "CC-6000", 1,    "Chennai"),
    (19, "Support",              "CC-6100", 18,   "Chennai"),
    (20, "Professional Services","CC-6200", 18,   "Pune"),
    (21, "Finance",              "CC-7000", 1,    "Mumbai"),
    (22, "People",               "CC-8000", 1,    "Bengaluru"),
    (23, "Talent Acquisition",   "CC-8100", 22,   "Bengaluru"),
    (24, "Legal",                "CC-9000", 1,    "Mumbai"),
    # Two departments that have never had an employee. Anti-join material,
    # and the reason a headcount report must decide between 0 and NULL.
    (25, "Internal Audit",       "CC-9100", 21,   "Mumbai"),
    (26, "Corporate Development","CC-9200", 1,    "Mumbai"),
]
STAFFED = [d[0] for d in DEPARTMENTS if d[0] not in (25, 26)]

# dept_id -> job family. Keeps the family consistent with the department so
# "engineers in Sales" never appears and confuses a grouping example.
FAMILY = {
    1: "Executive", 2: "Engineering", 3: "Engineering", 4: "Data",
    5: "Engineering", 6: "Quality", 7: "Engineering", 8: "Product",
    9: "Design", 10: "Product", 11: "Sales", 12: "Sales", 13: "Sales",
    14: "Sales Engineering", 15: "Marketing", 16: "Marketing",
    17: "Marketing", 18: "Customer Success", 19: "Support",
    20: "Professional Services", 21: "Finance", 22: "People",
    23: "People", 24: "Legal",
}

# Rough relative size of each department, so headcount by department is
# uneven in the way a real org is.
WEIGHT = {1: 1, 2: 3, 3: 14, 4: 10, 5: 16, 6: 8, 7: 6, 8: 2, 9: 5, 10: 6,
          11: 2, 12: 11, 13: 9, 14: 5, 15: 2, 16: 6, 17: 4, 18: 2, 19: 12,
          20: 7, 21: 6, 22: 3, 23: 4, 24: 3}

# (pay_grade, job_level, min, mid, max) -- annual base, INR thousands scale
# kept as plain numeric so the arithmetic examples stay readable.
BANDS = [
    ("G1", 1,  400000,  500000,  600000),
    ("G2", 2,  600000,  760000,  920000),
    ("G3", 3,  900000, 1150000, 1400000),
    ("G4", 4, 1350000, 1700000, 2050000),
    ("G5", 5, 2000000, 2500000, 3000000),
    ("G6", 6, 2900000, 3600000, 4300000),
    ("G7", 7, 4200000, 5200000, 6200000),
    ("G8", 8, 6000000, 7500000, 9000000),
]
BAND_BY_LEVEL = {b[1]: b for b in BANDS}

# Level mix. Most people are levels 2-4; the pyramid narrows above that.
LEVEL_WEIGHTS = [(1, 12), (2, 26), (3, 25), (4, 18), (5, 10), (6, 6),
                 (7, 2), (8, 1)]

FIRST = ["Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Meera", "Arjun",
         "Divya", "Karthik", "Sneha", "Rahul", "Nisha", "Aditya", "Kavya",
         "Siddharth", "Pooja", "Nikhil", "Ishita", "Varun", "Tanvi",
         "Manish", "Shreya", "Akash", "Riya", "Harsh", "Lakshmi", "Dev",
         "Anjali", "Gaurav", "Swati", "Rajesh", "Neha", "Suresh", "Deepa",
         "Amit", "Preeti", "Vivek", "Sunita", "Kiran", "Rekha"]
LAST = ["Sharma", "Nair", "Patel", "Reddy", "Iyer", "Gupta", "Singh",
        "Rao", "Mehta", "Chopra", "Desai", "Banerjee", "Kulkarni", "Joshi",
        "Verma", "Menon", "Pillai", "Shetty", "Bhat", "Agarwal", "Kapoor",
        "Malhotra", "Sinha", "Das", "Mishra"]

LOCATIONS = ["Bengaluru", "Pune", "Mumbai", "Chennai", "Remote"]
STAGES = ["applied", "screened", "interviewed", "offered", "hired"]


def weighted(rng, pairs):
    total = sum(w for _, w in pairs)
    r = rng.uniform(0, total)
    acc = 0
    for v, w in pairs:
        acc += w
        if r <= acc:
            return v
    return pairs[-1][0]


def between(rng, start, end):
    if end <= start:
        return start
    return start + timedelta(days=rng.randint(0, (end - start).days))


def write(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join("\\N" if v is None else str(v) for v in r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./data")
    args = ap.parse_args()
    rng = random.Random(SEED)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    write(out / "departments.tsv", DEPARTMENTS)
    write(out / "salary_bands.tsv", BANDS)

    # ---- employees --------------------------------------------------
    dept_pairs = [(d, WEIGHT[d]) for d in STAFFED]
    employees = []
    for eid in range(1, N_EMPLOYEES + 1):
        dept = 1 if eid == 1 else weighted(rng, dept_pairs)
        level = 8 if eid == 1 else weighted(rng, LEVEL_WEIGHTS)
        first, last = rng.choice(FIRST), rng.choice(LAST)

        hire = between(rng, FOUNDED, REPORT_DATE - timedelta(days=1))

        # Leavers. Probability rises with how long ago someone joined, which
        # is what makes the tenure-band attrition example show a gradient
        # rather than a flat line.
        term, leaver = None, None

        # Two separate mechanisms, because they are two different phenomena
        # and the chapter's attrition example exists to separate them.
        #
        # Early attrition is a property of the hire: the role was
        # misdescribed, or the person was wrong for it, and that chance does
        # not depend on how long ago they joined. Modelled as tenure-driven
        # it vanishes from recent cohorts, which is precisely the cohort
        # anyone measuring it cares about.
        if rng.random() < 0.06:
            cand = hire + timedelta(days=rng.randint(14, 86))
            if cand < REPORT_DATE:
                term = cand
        else:
            # Ordinary attrition, rising with how long ago someone joined,
            # so the tenure-band example shows a gradient rather than a
            # flat line.
            years_here = (REPORT_DATE - hire).days / 365.25
            if rng.random() < min(0.46, 0.055 * years_here):
                earliest = hire + timedelta(days=rng.randint(95, 400))
                if earliest < REPORT_DATE:
                    term = between(rng, earliest,
                                   REPORT_DATE - timedelta(days=1))
        if term is not None:
            leaver = "voluntary" if rng.random() < 0.74 else "involuntary"

        etype = weighted(rng, [("full_time", 86), ("part_time", 6),
                               ("contract", 8)])
        fte = {"full_time": "1.00", "part_time": rng.choice(["0.60", "0.80"]),
               "contract": "1.00"}[etype]

        email = None if rng.random() < 0.06 else \
            f"{first.lower()}.{last.lower()}{eid}@example.com"

        loc = next(d[4] for d in DEPARTMENTS if d[0] == dept)
        if rng.random() < 0.14:
            loc = rng.choice(LOCATIONS)

        employees.append([eid, first, last, email, dept, None, FAMILY[dept],
                          level, etype, fte, hire, term, leaver, loc])

    # Near-duplicate names, for the deduplication material. Fixed positions
    # so they are stable across runs.
    employees[203][1], employees[203][2] = "Priya", "Nair"
    employees[561][1], employees[561][2] = "Priya", "Nair"
    employees[804][1], employees[804][2] = "Priya ", " Nair"   # whitespace

    # ---- management chain -------------------------------------------
    # Assign each person a manager in the same department at a higher level,
    # falling back to the department's own head and then to the CEO. Built
    # from a sorted pool so the result does not depend on dict ordering.
    by_dept = {}
    for e in employees:
        by_dept.setdefault(e[4], []).append(e)
    dept_heads = {}
    for dept, members in sorted(by_dept.items()):
        members.sort(key=lambda e: (-e[7], e[0]))
        dept_heads[dept] = members[0][0]
    # Designate a limited number of managers per department and spread
    # reports evenly across them. Assigning each person a random senior
    # colleague instead produces an org where half the company manages one
    # person, which makes the span-of-control example meaningless.
    TARGET_SPAN = 7
    parent_of = {d[0]: d[3] for d in DEPARTMENTS}
    reports = {e[0]: 0 for e in employees}
    for dept, members in sorted(by_dept.items()):
        head = members[0]
        n_mgr = max(1, round(len(members) / TARGET_SPAN))
        managers = members[:n_mgr]
        mgr_ids = {m[0] for m in managers}
        for e in members:
            if e[0] == 1:
                continue
            if e[0] in mgr_ids:
                # Managers report to the department head; the head reports
                # up to the parent department's head.
                if e[0] == head[0]:
                    p = parent_of[dept]
                    e[5] = dept_heads.get(p, 1) if p else 1
                else:
                    e[5] = head[0]
            else:
                cand = [m for m in managers if m[7] > e[7]] or [head]
                pick = min(cand, key=lambda m: (reports[m[0]], m[0]))
                e[5] = pick[0]
            if e[5] == e[0]:
                e[5] = 1
            reports[e[5]] += 1
    write(out / "employees.tsv", employees)

    # ---- compensation (Type 2) --------------------------------------
    # The history is built so that the LAST row's grade matches the person's
    # current job_level. Promotions walk the grade up through the history,
    # which is what makes an as-of grade lookup a real question rather than a
    # constant. Salary is not clamped to the band: a few long-tenured people
    # end up above band_max (red-circled) and a few sit below band_min, and
    # finding them is the point of the compa-ratio example.
    comp = []
    for e in employees:
        eid, level, hire, term = e[0], e[7], e[10], e[11]
        last_day = term or REPORT_DATE
        tenure_days = max((last_day - hire).days, 1)

        # When each salary change happened, and which of them were promotions.
        change_dates = []
        cursor = hire
        while True:
            cursor = cursor + timedelta(days=rng.randint(330, 460))
            if cursor >= last_day:
                break
            change_dates.append(cursor)
        n_promos = min(level - 1, len(change_dates),
                       int(tenure_days / rng.randint(900, 1500)))
        promo_at = set(rng.sample(range(len(change_dates)), n_promos)) \
            if n_promos else set()

        cur_level = level - n_promos
        band = BAND_BY_LEVEL[cur_level]
        salary = round(band[2] + (band[4] - band[2]) * rng.betavariate(2, 3.4))
        rows = [[eid, hire, None, f"{salary}.00", band[0], "hire"]]
        for i, when in enumerate(change_dates):
            if i in promo_at:
                cur_level += 1
                band = BAND_BY_LEVEL[cur_level]
                # A promotion lands low in the new band far more often than
                # it lands at the midpoint.
                salary = max(round(salary * rng.uniform(1.10, 1.22)),
                             round(band[2] * rng.uniform(1.00, 1.06)))
                reason = "promotion"
            else:
                salary = round(salary * rng.uniform(1.025, 1.075))
                # Merit does not push someone out of their band, except for
                # the small number of long-tenured people who are
                # red-circled and paid above the maximum deliberately.
                if salary > band[4]:
                    salary = (round(band[4] * rng.uniform(1.00, 1.07))
                              if rng.random() < 0.08 else band[4])
                reason = "adjustment" if rng.random() < 0.14 else "merit"
            rows.append([eid, when, None, f"{salary}.00", band[0], reason])
        for i in range(len(rows) - 1):
            rows[i][2] = rows[i + 1][1]
        # A current row ends open. A leaver's last row closes on their last
        # day, so "current salary" is unambiguous for both.
        if term is not None:
            rows[-1][2] = term
        comp.extend(rows)

    # A band refresh that some salaries have not caught up with. Twelve
    # current rows are pushed below their band minimum, which is the
    # condition a compa-ratio review exists to surface.
    current_idx = [i for i, c in enumerate(comp) if c[2] is None]
    for i in sorted(rng.sample(current_idx, 12)):
        lo = BAND_BY_LEVEL[next(b[1] for b in BANDS if b[0] == comp[i][4])][2]
        comp[i][3] = f"{round(lo * rng.uniform(0.88, 0.97))}.00"

    # Gaps: five employees lose their most recent compensation row, so the
    # reconciliation example has something to report.
    still_here = [e[0] for e in employees if e[11] is None]
    for eid in sorted(rng.sample(still_here, 5)):
        idx = [i for i, c in enumerate(comp) if c[0] == eid]
        if len(idx) > 1:
            comp.pop(idx[-1])
            comp[idx[-2]][2] = REPORT_DATE - timedelta(days=30)
    write(out / "compensation.tsv", comp)

    # ---- performance reviews ----------------------------------------
    # Contractors are not reviewed, which is why a naive join loses them.
    reviews, rid = [], 1
    for e in employees:
        eid, etype, hire, term = e[0], e[8], e[10], e[11]
        if etype == "contract":
            continue
        for year in (2023, 2024, 2025):
            cutoff = date(year, 12, 31)
            if hire > date(year, 7, 1):
                continue
            if term is not None and term < cutoff:
                continue
            rating = weighted(rng, [(1, 2), (2, 9), (3, 52), (4, 28), (5, 9)])
            reviews.append([rid, eid, year, rating, e[5]])
            rid += 1
    write(out / "performance_reviews.tsv", reviews)

    # ---- requisitions and applications ------------------------------
    reqs, apps, aid = [], [], 1
    hired_pool = sorted(e[0] for e in employees
                        if e[10] >= date(2024, 1, 1))
    hp = 0
    for req_id in range(1, 181):
        dept = weighted(rng, dept_pairs)
        level = weighted(rng, LEVEL_WEIGHTS[:6])
        opened = between(rng, date(2024, 1, 1), REPORT_DATE - timedelta(days=5))
        roll = rng.random()
        if roll < 0.66:
            outcome, closed = "filled", opened + timedelta(days=rng.randint(18, 150))
        elif roll < 0.80:
            outcome, closed = "cancelled", opened + timedelta(days=rng.randint(10, 120))
        else:
            outcome, closed = None, None          # still open
        if closed is not None and closed >= REPORT_DATE:
            outcome, closed = None, None
        reqs.append([req_id, dept, FAMILY[dept], level, opened, closed, outcome])

        # The funnel: everyone applies, fewer reach each later stage.
        n_apps = rng.randint(6, 40)
        for _ in range(n_apps):
            applied = between(rng, opened, closed or REPORT_DATE - timedelta(days=1))
            r = rng.random()
            if r < 0.42:
                furthest = 0
            elif r < 0.70:
                furthest = 1
            elif r < 0.90:
                furthest = 2
            else:
                furthest = 3
            stage_date = applied + timedelta(days=rng.randint(1, 10) * (furthest + 1))
            if stage_date >= REPORT_DATE:
                stage_date = REPORT_DATE - timedelta(days=1)
            apps.append([aid, req_id, applied, STAGES[furthest], stage_date, None])
            aid += 1
        # Exactly one hire per filled requisition, tied to a real employee.
        if outcome == "filled" and hp < len(hired_pool):
            applied = between(rng, opened, closed)
            apps.append([aid, req_id, applied, "hired", closed, hired_pool[hp]])
            aid += 1
            hp += 1
    write(out / "requisitions.tsv", reqs)
    write(out / "applications.tsv", apps)

    # ---- absences ----------------------------------------------------
    absences = []
    for e in employees:
        eid, hire, term = e[0], e[10], e[11]
        lo = max(hire, date(2025, 1, 1))
        hi = min(term or REPORT_DATE, REPORT_DATE) - timedelta(days=1)
        if hi <= lo:
            continue
        seen = set()
        for _ in range(rng.randint(0, 22)):
            d = between(rng, lo, hi)
            if d.weekday() >= 5 or d in seen:
                continue
            seen.add(d)
            cat = weighted(rng, [("annual_leave", 70), ("sick", 22),
                                 ("other", 8)])
            hours = "8.00" if rng.random() < 0.85 else "4.00"
            absences.append([eid, d, hours, cat])
    absences.sort(key=lambda r: (r[0], r[1]))
    write(out / "absences.tsv", absences)

    active = sum(1 for e in employees if e[11] is None)
    print(f"hr: employees={len(employees)} active_at_{REPORT_DATE}={active} "
          f"compensation={len(comp)} reviews={len(reviews)} "
          f"requisitions={len(reqs)} applications={len(apps)} "
          f"absences={len(absences)}")


if __name__ == "__main__":
    main()
