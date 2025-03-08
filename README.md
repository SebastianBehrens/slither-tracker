# README
## TODO List
- [x] build data pipeline from api to data warehouse
- [ ] build analytics tables from the raw data
    - [ ] longest duration in top 10 (drilldown by server)
    - [ ] user most often in top 10 (drilldown by server)

- [ ] build frontend

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