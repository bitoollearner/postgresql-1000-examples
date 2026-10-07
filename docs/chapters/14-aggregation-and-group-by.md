# Chapter 14 — Aggregation and GROUP BY

Examples 241–278 · Part III: Querying

| # | Example | Level |
|---:|---|---|
| 241 | Count rows, count values, and the difference NULL makes | Beginner |
| 242 | Total, average, smallest and largest line value | Beginner |
| 243 | Distinguish how many orders from how many customers | Beginner |
| 244 | AVG ignores NULLs, and why that changes the answer | Beginner |
| 245 | MIN and MAX on dates and text, not just numbers | Beginner |
| 246 | Aggregate over a filtered subset | Beginner |
| 247 | Orders per channel with GROUP BY | Beginner |
| 248 | Sort by an aggregate you computed | Beginner |
| 249 | Group by two columns at once | Beginner |
| 250 | Keep only groups above a threshold with HAVING | Beginner |
| 251 | WHERE and HAVING reaching the same answer differently | Intermediate |
| 252 | Net revenue by category with a mobile-channel split | Intermediate |
| 253 | Group by a date expression to get monthly totals | Intermediate |
| 254 | Group by a CASE expression to build value bands | Intermediate |
| 255 | Collapse rows into a delimited list with STRING_AGG | Intermediate |
| 256 | Build arrays per group with ARRAY_AGG | Intermediate |
| 257 | Test whether all or any rows in a group satisfy a condition | Intermediate |
| 258 | Several segment cuts of one total in a single pass | Intermediate |
| 259 | COUNT DISTINCT survives a join fan-out; COUNT does not | Intermediate |
| 260 | LEFT JOIN and the difference between zero and NULL | Intermediate |
| 261 | Aggregate an aggregate: average of per-customer totals | Intermediate |
| 262 | Percentage of total with a window function | Intermediate |
| 263 | Statistical aggregates: spread, not just centre | Intermediate |
| 264 | Median and quartiles with ordered-set aggregates | Intermediate |
| 265 | Find the most frequent value per group with MODE | Intermediate |
| 266 | Prefer named grouping expressions over ordinals | Intermediate |
| 267 | Reconcile payments against order value | Intermediate |
| 268 | Fill gaps in a time series with generate_series | Intermediate |
| 269 | The fan-out trap: summing a parent column across a join | Advanced |
| 270 | COUNT DISTINCT versus pre-aggregation | Advanced |
| 271 | HashAggregate versus GroupAggregate, and work_mem | Advanced |
| 272 | Pre-aggregate before joining, not after | Advanced |
| 273 | One conditional pass instead of several scans | Advanced |
| 274 | Let an index answer the aggregate | Advanced |
| 275 | Cohort table: signup month against order month | Advanced |
| 276 | When GROUP BY is the wrong tool and a window is right | Advanced |
| 277 | Aggregate over a rolling window of days | Advanced |
| 278 | Decide when an aggregate should be materialised | Advanced |

The solutions and explanations are in [the book](https://www.amazon.com/dp/REPLACE-WITH-ASIN).
