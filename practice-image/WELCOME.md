# Start here

Welcome to the practice environment for **[PostgreSQL: 1,000 Examples](https://www.amazon.com/dp/REPLACE-WITH-ASIN)**.

Everything is already running. PostgreSQL 16.15 is up with the book's
datasets loaded, and the 53 chapter notebooks are in this folder.

## How to use this

Each notebook gives you the problems from one chapter. For every example you
get the question and an empty cell:

```sql
%%sql
-- Example 291. Your answer here.
```

Write your SQL, run it, then check yourself against the book. The verified
solution, the explanation, the common mistakes and the pattern insight are all
there — that is what the book is for.

Working a problem before reading the answer is the entire point. You will
remember a pattern you struggled with for ten minutes; you will not remember
one you read.

## Connecting

The first cell of every notebook connects for you. If you want a plain `psql`
session instead:

```bash
docker exec -it pg1000-practice psql -U book -d pg1000
```

Or point any client at `postgresql://book:book@localhost:5432/pg1000`.

## The datasets

| Schema | What it is |
|---|---|
| `ecommerce` | 5,000 orders. Most of the book. |
| `hr` | 1,200 employees. Chapter 49. |
| `ecommerce_lg` | 2,000,000 orders. Part VIII only — load it on demand. |

**Before you start Part VIII (chapters 35-39), read this.** Those chapters
query `ecommerce_lg`, and it is not in the image. Until you load it, every
example in that part fails with `relation "..." does not exist` - which looks
like broken SQL and is not.

```bash
docker exec -it pg1000-practice load-large-dataset
```

About three minutes and 850 MB, and it prints nothing until it finishes. Each
of those five notebooks opens with a cell that checks for you and says whether
you are ready, so you do not have to remember this.

It is not preloaded because index selection, partition pruning and BRIN cannot
be demonstrated on five thousand rows - at that size the planner correctly
prefers a sequential scan and every lesson in the part inverts. Paying 850 MB
for it up front, on every reader, for one part of eleven, was the worse trade.

The data contains deliberate defects — NULL emails, customers who never
ordered, orders with no payment, employees reporting to managers who have
left. Examples that produce an odd-looking result are usually meeting one of
them on purpose. `_chapter-index/` lists every example by number and title.

## Your work is saved

Anything you change in this folder persists in the container's volume and
survives `docker compose down`. To start fresh, remove the volume.
