# Setup

## The one-command route

```bash
docker run -d --name pg1000-practice \
  -p 8888:8888 -p 5432:5432 \
  bilearner/postgres1000-practice:1.0
```

Open <http://localhost:8888/lab>. That is the whole setup.

Or with Compose, which also gives you a named volume so your notebook edits
survive:

```bash
git clone https://github.com/bitoollearner/postgresql-1000-examples.git
cd postgresql-1000-examples
docker compose up -d
```

## Connecting a GUI client

Start the container, then point your client at:

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `pg1000` |
| Username | `book` |
| Password | `book` |

pgAdmin, DBeaver, DataGrip, PyCharm and the VS Code SQL extensions all connect
this way.

## A psql session

```bash
docker exec -it pg1000-practice psql -U book -d pg1000
```

## The large dataset

Part VIII needs `ecommerce_lg`, which is not in the image because it would add
roughly 850 MB:

```bash
docker exec -it pg1000-practice load-large-dataset
```

About three minutes.

## Checking your environment

```bash
docker exec -it pg1000-practice python3 /opt/verify_env.py
```

This reports the server version, collation, the settings the book depends on,
and the row counts. Paste its output into any errata report.

## Running without Docker

You can use any PostgreSQL 13 or later, but the book assumes the container's
configuration and some output will differ.

The cluster **must** be initialised with the `C` locale:

```bash
initdb -D /your/data --locale=C --encoding=UTF8
```

Text sort order depends on collation. Under `C`, `ORDER BY` on text is byte
order and uppercase sorts before lowercase; under `C.UTF-8` or `en_US.utf8` it
does not. Every ordered result in the book containing mixed-case text depends
on this, and getting it wrong breaks a large number of examples in a way that
looks like broken SQL.

Then apply `conf/postgresql.conf`, install the extensions in
`conf/initdb/`, and load the datasets:

```bash
python datasets/ecommerce/generate.py --size sm --out datasets/ecommerce/data
psql -v schema=ecommerce -f datasets/ecommerce/ddl.sql
# \copy each table from datasets/ecommerce/data/*.tsv

python datasets/hr/generate.py --out datasets/hr/data
psql -v schema=hr -f datasets/hr/ddl.sql
# \copy each table from datasets/hr/data/*.tsv
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
