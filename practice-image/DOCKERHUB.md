# PostgreSQL: 1,000 Examples — Practice Environment

The complete practice environment for the book
**[PostgreSQL: 1,000 Examples](https://www.amazon.com/dp/YOUR-REAL-ASIN)**: PostgreSQL 16.15 with the book's seeded
datasets already loaded, JupyterLab, and all 53 chapter notebooks.

```bash
docker run -d --name pg1000-practice \
  -p 8888:8888 -p 5432:5432 \
  bilearner/postgres1000-practice:1.0
```

Open <http://localhost:8888/lab>.

Nothing to generate, nothing to load, nothing to configure.

## Also connects to any SQL client

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `pg1000` |
| Username | `book` |
| Password | `book` |

pgAdmin, DBeaver, DataGrip, PyCharm and the VS Code SQL extensions all work.

## What is inside

- **PostgreSQL 16.15**, configured exactly as the book's 1000 examples
  were verified against — parallelism and JIT off, `work_mem` at 4 MB,
  `default_statistics_target` at 1000, and the cluster locale pinned to `C`.
  Printed row counts and execution plans reproduce because of these.
- **`ecommerce`** — 5,000 orders, 14,998 order lines. Most of the book.
- **`hr`** — 1,200 employees. Chapter 49.
- **`ecommerce_lg`** — 2,000,000 orders, loadable on demand for Part VIII:
  `docker exec -it pg1000-practice load-large-dataset`
- **JupyterLab** with `ipython-sql`, pandas and matplotlib.
- **53 chapter notebooks** — every example as a problem with an empty cell.

## The notebooks are problems, not answers

Each notebook gives you the question and somewhere to write your SQL. The
verified solutions, explanations, common mistakes and pattern insights are in
the book. Work the problem, then check yourself.

## Tags

| Tag | What it is |
|---|---|
| `1.0` | pinned release — use this one |
| `latest` | most recent release |

`linux/amd64` and `linux/arm64`, so Apple Silicon runs natively.

## Persisting your work

```bash
docker run -d --name pg1000-practice \
  -p 8888:8888 -p 5432:5432 \
  -v pg1000-work:/practice \
  bilearner/postgres1000-practice:1.0
```

Your notebook edits live in `/practice` and survive restarts.

## Source

[https://github.com/bitoollearner/postgresql-1000-examples](https://github.com/bitoollearner/postgresql-1000-examples) · MIT licensed.
The book's text and solutions are © Bi Learner.
