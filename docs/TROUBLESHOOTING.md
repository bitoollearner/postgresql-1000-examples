# Troubleshooting

## My results are in a different order from the book

Almost always collation. Check it:

```bash
docker exec -it pg1000-practice psql -U book -d pg1000 -c \
  "SELECT datcollate FROM pg_database WHERE datname='pg1000'"
```

It must be `C`. Under any other collation, `ORDER BY` on text sorts
differently — `C` is byte order, so uppercase sorts before lowercase, and
`en_US.utf8` and `C.UTF-8` do not do that.

If you built your own cluster, it has to be `initdb --locale=C`. There is no
way to change it afterwards; the cluster must be recreated.

## An execution plan differs from the printed one

Check the settings the book depends on:

```bash
docker exec -it pg1000-practice python3 /opt/verify_env.py
```

The ones that change plans most often:

| Setting | Must be | Why |
|---|---|---|
| `max_parallel_workers_per_gather` | `0` | parallel plans vary with core count |
| `jit` | `off` | changes plan output and timing |
| `work_mem` | `4MB` | decides whether a sort spills to disk |
| `default_statistics_target` | `1000` | makes row estimates converge |

Part VIII examples also need `ecommerce_lg`. On the 5,000-row dataset the
planner correctly prefers a sequential scan and the lesson inverts.

## Port 5432 or 8888 is already in use

Map different host ports:

```bash
docker run -d -p 8889:8888 -p 5433:5432 bilearner/postgres1000-practice:1.0
```

Connect on 5433, browse on 8889. The ports inside the container do not change.

## JupyterLab asks for a token

The image sets no token by default. If you set `JUPYTER_TOKEN`, use it — or
unset it to go back to no token.

## The container exits immediately

```bash
docker logs pg1000-practice
```

Usually a port clash or not enough memory. The image needs about 1 GB of RAM
to run comfortably, and more while loading the large dataset.

## `load-large-dataset` seems to hang

It takes about three minutes and prints nothing until it finishes. Give it
five before investigating.

## I want to start completely fresh

```bash
docker rm -f pg1000-practice
docker volume rm pg1000-work      # if you created one
docker run -d --name pg1000-practice -p 8888:8888 -p 5432:5432 \
  bilearner/postgres1000-practice:1.0
```

The database lives inside the image, so a fresh container is always a fresh,
correctly loaded database.

## Something else

[Open an issue](https://github.com/bitoollearner/postgresql-1000-examples/issues/new/choose) with the output of
`verify_env.py`.
