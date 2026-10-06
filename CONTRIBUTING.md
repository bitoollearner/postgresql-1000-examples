# Contributing

## Errata

If an example in the book does not reproduce, or a figure looks wrong, please
[open an errata report](https://github.com/bitoollearner/postgresql-1000-examples-companion/issues/new?template=errata-report.md).

Include:

- the example number
- what the book prints
- what you got
- the output of `python scripts/verify_env.py`

That last one matters more than it looks. Most reports that turn out not to be
errata come from an environment that differs from the book's — usually a
cluster initialised with a collation other than `C`, which changes how text
sorts and therefore the order of printed rows.

Errata are credited in the next revision unless you ask otherwise.

## Questions

Questions about an example are welcome as
[issues](https://github.com/bitoollearner/postgresql-1000-examples-companion/issues/new?template=question.md). Please include the example
number.

## Pull requests

PRs are welcome for the companion's own code: the image, the scripts, the
notebooks' structure, documentation.

PRs that add solution SQL to the notebooks will be declined. The notebooks are
deliberately problems-only — the solutions are the book. There is a build-time
check (`assert_no_solutions`) that fails the build if solution text appears,
so this is enforced rather than merely requested.
