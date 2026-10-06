# PostgreSQL: 1,000 Examples — Companion

The practice environment for **[PostgreSQL: 1,000 Examples](https://www.amazon.com/dp/YOUR-REAL-ASIN)** by Bi Learner.

[![Practice image](https://img.shields.io/docker/v/bilearner/postgres1000-practice?label=docker&logo=docker)](https://hub.docker.com/r/bilearner/postgres1000-practice)
[![Image size](https://img.shields.io/docker/image-size/bilearner/postgres1000-practice/latest?label=size)](https://hub.docker.com/r/bilearner/postgres1000-practice)
[![Build](https://github.com/bitoollearner/postgresql-1000-examples/actions/workflows/docker-image.yml/badge.svg)](https://github.com/bitoollearner/postgresql-1000-examples/actions/workflows/docker-image.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## Start practising in one command

```bash
docker run -d --name pg1000-practice \
  -p 8888:8888 -p 5432:5432 \
  bilearner/postgres1000-practice:1.0
```

Then open **<http://localhost:8888/lab>**.

PostgreSQL 16.15 is already running with the book's datasets loaded and
all 53 chapter notebooks waiting. There is nothing to generate, nothing to
load, and nothing to configure. First start is a few seconds.

To connect your own client instead — pgAdmin, DBeaver, DataGrip, PyCharm:

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `pg1000` |
| Username | `book` |
| Password | `book` |

---

## What this repository is

The book is 1000 worked PostgreSQL examples across 53 chapters. Every one
was executed against PostgreSQL 16.15 and its output captured — the
printed row counts, sums and execution plans are real, not illustrative.

This repository is the **environment those examples run in**, so you can work
through them on your own machine and get the same answers the book prints.

### What you get here

- **The practice image** — PostgreSQL 16.15, configured exactly as the
  book was verified against, with the datasets preloaded and JupyterLab on top.
- **53 chapter notebooks** — every example as a problem to solve, with an
  empty cell under it waiting for your SQL.
- **The datasets** — the seeded generators, so the figures are reproducible
  rather than approximate.
- **The exact server configuration** — `conf/postgresql.conf`, copied from the
  book's own build. Plans depend on these settings; a different `work_mem` or
  `default_statistics_target` produces a different plan.
- **A chapter index** — all 1000 example titles, so you can find the one you
  need.

### What is in the book, not here

The **solutions, explanations, common mistakes, recommendations and pattern
insights**. Each example in the book carries all of them in a fixed
seven-section format, plus a captured execution plan for the advanced tier.

That is the deal: the environment and the problems are free and open, and the
answers are what you buy. The notebooks here give you the question and a blank
cell — work it out, then check yourself against the book.

**[Get the book on Amazon Kindle](https://www.amazon.com/dp/YOUR-REAL-ASIN)**

---

## The datasets

Three schemas, each from a seeded generator, so your numbers match the printed
ones exactly.

| Schema | Scale | In the image? | Used by |
|---|---|---|---|
| `ecommerce` | 5,000 orders, 14,998 lines | preloaded | most of the book |
| `hr` | 1,200 employees | preloaded | Chapter 49 |
| `ecommerce_lg` | 2,000,000 orders, 6M lines | load on demand | Part VIII |

`ecommerce_lg` is not baked in because it would add roughly 850 MB to the
image for the one part that needs it. Load it when you reach Part VIII:

```bash
docker exec -it pg1000-practice load-large-dataset
```

Index selection, partition pruning and BRIN cannot be demonstrated on five
thousand rows — at that size the planner correctly prefers a sequential scan
and every lesson inverts. See [docs/DATASETS.md](docs/DATASETS.md), including
the defects the data contains **on purpose**.

---

## Contents

```
conf/            the server configuration the book was verified against
datasets/        seeded generators and DDL for all three schemas
docs/            setup, datasets, troubleshooting, and the chapter index
notebooks/       53 chapter notebooks -- problems, not answers
practice-image/  the Dockerfile and entrypoint for the image above
scripts/         environment verification and dataset loading
```

---

## Chapters


**Part I — Getting Started**

- 1. [PostgreSQL in Context](docs/chapters/01-postgresql-in-context.md) · 5 examples
- 2. [Your Environment: Docker, psql, PyCharm](docs/chapters/02-your-environment-docker-psql-pycharm.md) · 8 examples
- 3. [The Architecture You Actually Need](docs/chapters/03-the-architecture-you-actually-need.md) · 7 examples

**Part II — Data Definition and Types**

- 4. [Databases, Schemas and Tables](docs/chapters/04-databases-schemas-and-tables.md) · 14 examples
- 5. [The Type System: Numbers, Text, Booleans](docs/chapters/05-the-type-system-numbers-text-booleans.md) · 20 examples
- 6. [Dates, Times and Time Zones as Types](docs/chapters/06-dates-times-and-time-zones-as-types.md) · 12 examples
- 7. [Constraints and Data Integrity](docs/chapters/07-constraints-and-data-integrity.md) · 22 examples
- 8. [Writing Data: INSERT, UPDATE, DELETE, UPSERT](docs/chapters/08-writing-data-insert-update-delete-upsert.md) · 24 examples

**Part III — Querying**

- 9. [SELECT Fundamentals](docs/chapters/09-select-fundamentals.md) · 22 examples
- 10. [Filtering and Conditional Logic](docs/chapters/10-filtering-and-conditional-logic.md) · 26 examples
- 11. [String Functions](docs/chapters/11-string-functions.md) · 28 examples
- 12. [Numeric and Mathematical Functions](docs/chapters/12-numeric-and-mathematical-functions.md) · 16 examples
- 13. [Date and Time Functions](docs/chapters/13-date-and-time-functions.md) · 36 examples
- 14. [Aggregation and GROUP BY](docs/chapters/14-aggregation-and-group-by.md) · 38 examples
- 15. [Advanced Grouping: ROLLUP, CUBE, GROUPING SETS](docs/chapters/15-advanced-grouping-rollup-cube-grouping-sets.md) · 12 examples
- 16. [Joins](docs/chapters/16-joins.md) · 45 examples

**Part IV — Composition and Analytics**

- 17. [Subqueries](docs/chapters/17-subqueries.md) · 18 examples
- 18. [Common Table Expressions](docs/chapters/18-common-table-expressions.md) · 20 examples
- 19. [Recursive CTEs](docs/chapters/19-recursive-ctes.md) · 12 examples
- 20. [Window Functions](docs/chapters/20-window-functions.md) · 60 examples
- 21. [Analytical Patterns](docs/chapters/21-analytical-patterns.md) · 28 examples

**Part V — Data Modeling**

- 22. [Relational Modeling](docs/chapters/22-relational-modeling.md) · 20 examples
- 23. [Normalization and Denormalization](docs/chapters/23-normalization-and-denormalization.md) · 16 examples
- 24. [Dimensional Modeling](docs/chapters/24-dimensional-modeling.md) · 26 examples
- 25. [Slowly Changing Dimensions](docs/chapters/25-slowly-changing-dimensions.md) · 20 examples
- 26. [Designing Production Schemas](docs/chapters/26-designing-production-schemas.md) · 15 examples

**Part VI — PostgreSQL's Distinctive Types**

- 27. [Arrays](docs/chapters/27-arrays.md) · 25 examples
- 28. [JSON and JSONB](docs/chapters/28-json-and-jsonb.md) · 19 examples
- 29. [UUID, ENUM, Ranges and Custom Types](docs/chapters/29-uuid-enum-ranges-and-custom-types.md) · 15 examples

**Part VII — Objects, Transactions and Programming**

- 30. [Views and Materialized Views](docs/chapters/30-views-and-materialized-views.md) · 20 examples
- 31. [Transactions and Savepoints](docs/chapters/31-transactions-and-savepoints.md) · 13 examples
- 32. [MVCC, Isolation and Locking](docs/chapters/32-mvcc-isolation-and-locking.md) · 14 examples
- 33. [Functions and Procedures](docs/chapters/33-functions-and-procedures.md) · 22 examples
- 34. [Triggers and Change Tracking](docs/chapters/34-triggers-and-change-tracking.md) · 13 examples

**Part VIII — Performance**

- 35. [Index Fundamentals](docs/chapters/35-index-fundamentals.md) · 17 examples
- 36. [Specialized Indexes](docs/chapters/36-specialized-indexes.md) · 16 examples
- 37. [Reading Execution Plans](docs/chapters/37-reading-execution-plans.md) · 17 examples
- 38. [Query Optimization](docs/chapters/38-query-optimization.md) · 16 examples
- 39. [Partitioning, VACUUM and Maintenance](docs/chapters/39-partitioning-vacuum-and-maintenance.md) · 20 examples

**Part IX — Data Engineering**

- 40. [Loading Data](docs/chapters/40-loading-data.md) · 17 examples
- 41. [Incremental Processing and CDC](docs/chapters/41-incremental-processing-and-cdc.md) · 18 examples
- 42. [Dimension and Fact Pipelines](docs/chapters/42-dimension-and-fact-pipelines.md) · 16 examples
- 43. [Data Quality and Reconciliation](docs/chapters/43-data-quality-and-reconciliation.md) · 14 examples
- 44. [Orchestration with Python](docs/chapters/44-orchestration-with-python.md) · 14 examples

**Part X — Production Operations**

- 45. [Roles, Security and RLS](docs/chapters/45-roles-security-and-rls.md) · 13 examples
- 46. [Backup, Recovery and PITR](docs/chapters/46-backup-recovery-and-pitr.md) · 11 examples
- 47. [Monitoring and System Catalogs](docs/chapters/47-monitoring-and-system-catalogs.md) · 12 examples
- 48. [Beyond the Core](docs/chapters/48-beyond-the-core.md) · 4 examples

**Part XI — Capstone Projects**

- 49. [HR and Workforce Analytics](docs/chapters/49-hr-and-workforce-analytics.md) · 10 examples
- 50. [Capstone I - E-Commerce Warehouse](docs/chapters/50-capstone-i-e-commerce-warehouse.md) · 22 examples
- 51. [Capstone II - Enterprise ELT](docs/chapters/51-capstone-ii-enterprise-elt.md) · 20 examples
- 52. [Capstone III - Banking and Fraud](docs/chapters/52-capstone-iii-banking-and-fraud.md) · 16 examples
- 53. [Capstone IV - Event Analytics](docs/chapters/53-capstone-iv-event-analytics.md) · 16 examples

---

## Difficulty mix

| Level | Examples | What it means |
|---|---:|---|
| Beginner | 142 | establishes a mechanism; usually one reasonable way to write it |
| Intermediate | 729 | applying it correctly, which is where most real difficulty lives |
| Advanced | 129 | carries a captured `EXPLAIN` plan and a performance discussion |

---

## Running without Docker

You can use any PostgreSQL 13 or later, but the book assumes the container's
configuration and some output will differ. See
[docs/SETUP.md](docs/SETUP.md#running-without-docker). The settings that matter
are in `conf/postgresql.conf`, and the cluster locale must be `C` — text sort
order depends on it, and every example that orders mixed-case text will differ
otherwise.

---

## Errata and questions

Found a mistake in the book, or an example that does not reproduce?
[Open an issue](https://github.com/bitoollearner/postgresql-1000-examples/issues/new/choose). Errata reports are especially
welcome and are credited in the next revision.

---

## Licence

The code, notebooks, configuration and dataset generators in this repository
are MIT licensed — see [LICENSE](LICENSE).

The book's text, example solutions and explanations are © Bi Learner and are
not covered by that licence.
