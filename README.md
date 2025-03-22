# README
This repo contains a small side project analyzing player performance on ![slither.io](https://slither.io).

To do that a simple data pipeline has been built to scrape a website, store the data in a database and run some basic analytics.
The results are then visualized through a react frontend using ![echarts](https://echarts.apache.org/).

The whole application is dockerized and can be run locally by running `docker compose up` in the root directory after cloning this repository.

## TODO List
- [x] build data pipeline from api to data warehouse
- [ ] build analytics tables from the raw data
    - [ ] longest duration (run) in top 10 (drilldown by server)
    - [ ] user most often in top 10 (drilldown by server)

- [ ] build frontend
# Data Model
## Raw Data
### Server User Rank
- server_id
- server_time
- flg_active
- rank
- nick
- score
## Analytics Layer
### Longest Run (duration) in top 10 (drilldown by server)
- maybe flg_active in server_user_rank does not make sense. server_user_rank entry is always valid.
- instead have a table where the runs are stored
- on new entry in server_user_rank open run
  - on higher rank update run
  - on lower rank update run
  - when no longer visible (rank < 10) close run
- on write of raw data run query to update runs
- using flg_active one can only run analysis on active servers
```sql
```


## Tracking Logic
### Changing rank
 t_1         t_2
  |           |
  v           v
  +-----------+-----------+
  |   rank a  |   rank b  |  ← User A
  +-----------+-----------+
### No rank
 t_1         t_2
  |           |
  v           v
  +-----------+-----------+
  |   rank a  |  no rank  |  ← User A
  +-----------+-----------+