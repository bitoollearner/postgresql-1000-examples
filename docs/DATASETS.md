# The datasets

Three schemas, each produced by a seeded generator. Running a generator on any
machine at any time produces byte-identical output, which is what makes the
figures in the book reproducible rather than approximate.

| Schema | Scale | In the image | Used by |
|---|---|---|---|
| `ecommerce` | 5,000 orders, 14,998 lines | yes | most of the book |
| `hr` | 1,200 employees | yes | Chapter 49 |
| `ecommerce_lg` | 2,000,000 orders, 6,001,586 lines | on demand | Part VIII |

## `ecommerce`

| Table | Rows | Notes |
|---|---:|---|
| `categories` | 16 | hierarchical, `parent_id` self-reference |
| `customers` | 804 | 763 have ordered, 41 never have |
| `products` | 200 | 16 have never been ordered |
| `orders` | 5,000 | `status`, `channel`, `order_ts` as `timestamptz` |
| `order_items` | 14,998 | grain: one row per order line |
| `payments` | varies | 358 orders are unpaid |
| `returns` | varies | a subset of delivered orders |

`order_items` holds 14,998 rows rather than a round 15,000. The generator
reserves sixteen products that are never ordered, and that reservation shifts
the seeded sequence. The figure is stable across every run.

### Deliberate defects

The data contains problems on purpose, because the examples about data quality
need data with something wrong in it:

- 70 customers with a `NULL` email
- 41 customers who have never placed an order
- 16 products that have never been ordered
- 358 orders with no matching payment
- near-duplicate customers differing only by whitespace or letter case
- order timestamps spanning several UTC offsets

## `hr`

| Table | Rows | Grain |
|---|---:|---|
| `departments` | 26 | one row per department |
| `salary_bands` | 8 | one row per pay grade |
| `employees` | 1,200 | one row per person, ever employed |
| `compensation` | ~5,300 | one row per person per salary held (Type 2) |
| `performance_reviews` | ~2,100 | one row per person per review year |
| `requisitions` | 180 | one row per open position |
| `applications` | ~4,000 | one row per candidate per requisition |
| `absences` | ~7,200 | one row per person per absent day |

Every figure in Chapter 49 is taken as of **1 January 2026**, fixed in the
generator rather than read from the clock. A workforce report whose answer
changes overnight cannot be printed in a book.

### Deliberate defects

- about 6% of employees have a `NULL` work email
- two departments have never had an employee
- around 200 active employees report to a manager who has since left, which
  disconnects them from the org chart
- five current employees have no open compensation row
- contractors are never reviewed, so an inner join to `performance_reviews`
  silently loses them
- near-duplicate names, including one differing only by whitespace

### No protected attributes

There is no race, ethnicity, gender, age, date of birth, religion, disability,
marital status or health column anywhere in the `hr` schema, and no example in
the book derives one. Workforce analytics that segments people on those
attributes is a legal and ethical question before it is a SQL one. Everything
in Chapter 49 cuts by department, job family, level, location, tenure and
performance.

## `ecommerce_lg`

Same shape as `ecommerce`, four hundred times the size. Part VIII uses it
because index selection, partition pruning and BRIN cannot be demonstrated on
five thousand rows — at that size the planner correctly prefers a sequential
scan and every lesson inverts.

```bash
docker exec -it pg1000-practice load-large-dataset
```

About three minutes and 850 MB. It is not baked into the image because that
cost would be paid by every reader for the one part that needs it.

## Regenerating by hand

```bash
python datasets/ecommerce/generate.py --size sm --out datasets/ecommerce/data
python datasets/ecommerce/generate.py --size lg --out datasets/ecommerce/data_lg
python datasets/hr/generate.py --out datasets/hr/data
```

The schema name is supplied to `psql`, so one DDL file builds either size:

```bash
psql -v schema=ecommerce -f datasets/ecommerce/ddl.sql
```
