# PostgreSQL: 1,000 Examples - Practice Environment

A ready-to-practice PostgreSQL + Jupyter environment for the book
**PostgreSQL: 1,000 Examples** on Amazon Kindle.

## Quick start

Needs [Docker Desktop](https://docs.docker.com/get-started/get-docker/) - free
for personal use, and the only thing to install.

Mac / Linux:
```bash
mkdir -p practice
docker run --rm \
  -p 8888:8888 -p 5432:5432 \
  -v $(pwd)/practice:/practice \
  bilearner/postgres1000-practice:1.1
```

Windows PowerShell:
```powershell
mkdir practice -Force
docker run --rm `
  -p 8888:8888 -p 5432:5432 `
  -v ${PWD}/practice:/practice `
  bilearner/postgres1000-practice:1.1
```

Open http://localhost:8888 in your browser. JupyterLab opens with 53 chapter
folders, each holding that chapter's notebook and room for your own files.

Also on GitHub Container Registry, if Docker Hub's anonymous pull limit gets in
your way: `ghcr.io/bitoollearner/postgres1000-practice:1.1`

## What's in the image

- PostgreSQL 16.15, configured exactly as the book's 1,000 examples
  were verified against - parallelism and JIT off, `work_mem` 4MB,
  `default_statistics_target` 1000, cluster locale `C`
- JupyterLab 4.2.5 with ipython-sql, pandas, matplotlib
- `ecommerce` schema preloaded - 5,000 orders, 14,998 order lines
- `hr` schema preloaded - 1,200 employees, for Chapter 49
- `ecommerce_lg` loadable on demand - 2,000,000 orders, for Part VIII
- Extensions preinstalled: pg_stat_statements, pgcrypto, uuid-ossp,
  tablefunc, hstore, btree_gin, pg_trgm
- 53 chapter folders, one notebook in each

## Connect any SQL client

pgAdmin, DBeaver, DataGrip, PyCharm and the VS Code SQL extensions:

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `pg1000` |
| Username | `book` |
| Password | `book` |

Or a shell: `docker exec -it <container> psql -U book -d pg1000`

## How to use

1. Open the book on Kindle, pick an example
2. Open the matching chapter notebook in JupyterLab
3. Each example gives you the problem and an empty cell - write your own SQL
4. Shift+Enter - compare your output to the book
5. Read the book's Explanation, Common Mistake, Recommendation, Pattern Insight

The notebooks are deliberately problems, not answers. You will remember a
pattern you worked on for ten minutes; you will not remember one you read.

## Part VIII needs the large dataset

```bash
docker exec -it <container> load-large-dataset
```

About three minutes and 850 MB. Index selection, partition pruning and BRIN
cannot be demonstrated on five thousand rows.

## Check your environment matches the book

```bash
docker exec -it <container> python3 /opt/verify_env.py
```

Prints the collation, the settings that decide execution plans, and the row
counts. Paste its output into any errata report.

## Tags

| Tag | What it is |
|---|---|
| `1.1` | pinned release - use this one |
| `latest` | most recent release |

Released through the build workflow for `linux/amd64` and `linux/arm64`, so
Apple Silicon runs natively.

## Companion repository

Full source and setup guide: https://github.com/bitoollearner/postgresql-1000-examples

## Buy the book

[PostgreSQL: 1,000 Examples on Amazon Kindle](https://www.amazon.com/dp/REPLACE-WITH-ASIN)

## License

MIT. Image contents include third-party software under their own licenses.
Book content is copyright (c) 2026 Bi Learner - available on Amazon Kindle.
