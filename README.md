# mjs-contest-utils

## `mjs.py`

Updates https://dyto4lbher7lu.cloudfront.net/results/results_season_1.csv with the results.
See [workflow file](.github/workflows/sync-results.yml) to edit the season, or other parameters.

## `league-scheduling.py`

Creates matchups.

Parameters: 
- 10 players
- 6 weeks

Hard requirements:
- 4 games per week per player
- games can be scheduled such that two games can run at the same time (can be paired)

Soft requirements: 
- variety in matchups (important)
- even seat distribution (less important)
