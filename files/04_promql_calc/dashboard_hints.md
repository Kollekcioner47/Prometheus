# files/04_promql_calc — подсказки для панелей Grafana

Это не готовый дашборд и не JSON. Здесь короткая таблица: какой
запрос из `queries.promql` в какую панель Grafana превращается,
как называется единица измерения и что на панели видно человеку.
Полноценный дашборд собирается в практике 5, когда Grafana уже
установлена.

Правило, которое действует для всех панелей сразу: **запрос надо
сначала проверить в Prometheus**, во вкладке `Graph`. Если запрос
возвращает десятки тысяч рядов, панель его не «спрячет» — она
нарисует их все и станет нечитаемой.

## Панели «парк машин»

| Панель | Запрос | Тип | Единица |
|---|---|---|---|
| Доступность целей | `up{env="lab"}` | Stat | нет |
| Число целей по заданиям | `count by (job) (up)` | Bar gauge | нет |
| Загрузка CPU | `100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])))` | Time series | percent (0-100) |
| Занятая память | `100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)` | Time series | percent (0-100) |
| Свободное место | `100 * node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}` | Gauge | percent (0-100) |
| Средняя загрузка | `avg(node_load1{env="lab"})` | Stat | нет |
| Время работы | `(time() - node_boot_time_seconds) / 86400` | Stat | days |

## Панели «сеть и диск»

| Панель | Запрос | Тип | Единица |
|---|---|---|---|
| Трафик, приём | `rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8` | Time series | bits/sec |
| Трафик, отдача | `rate(node_network_transmit_bytes_total{device!="lo"}[5m]) * 8` | Time series | bits/sec |
| Операции ввода-вывода | `rate(node_disk_writes_completed_total[5m])` | Time series | ops/sec |
| Свободное место по разделам | `node_filesystem_avail_bytes{fstype!~"tmpfs|devtmpfs|squashfs|overlay"} / 1073741824` | Table | gigabytes |
| Прогноз заполнения | `predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[1h], 4 * 3600) / 1073741824` | Time series | gigabytes |

## Панели по гистограммам

| Панель | Запрос | Тип | Единица |
|---|---|---|---|
| Время ответа, 95-й процентиль | `histogram_quantile(0.95, sum by (le) (rate(prometheus_http_request_duration_seconds_bucket[5m])))` | Time series | seconds |
| Время ответа, медиана | `histogram_quantile(0.5, sum by (le) (rate(prometheus_http_request_duration_seconds_bucket[5m])))` | Time series | seconds |
| Среднее время ответа | `sum(rate(prometheus_http_request_duration_seconds_sum[5m])) / sum(rate(prometheus_http_request_duration_seconds_count[5m]))` | Stat | seconds |
| Распределение по интервалам | `sum by (le) (rate(prometheus_http_request_duration_seconds_bucket[5m]))` | Heatmap | seconds |

## Три вещи, которые ломают панель

  * **Запрос с `topk` без агрегации.** На большом диапазоне
    `topk` пересчитывается на каждой точке, и ряды в легенде
    «прыгают»: машина то в списке, то нет. Для панели надёжнее
    агрегировать (`sum by`), а `topk` оставить для таблицы.
  * **Единица измерения, оставленная по умолчанию.** Grafana
    покажет `0.043` там, где имеется в виду 43 процента.
    Поле `Unit` заполняется всегда, вместе с `Min` и `Max`.
  * **Диапазон времени больше срока хранения.** В курсе это
    `15d`; панель на 30 дней нарисует половину графика и ни слова
    не скажет о том, что данных просто нет. Пустой график
    и «нет данных» выглядят одинаково — это разбирается
    в разделе «Если что-то пошло не так» практики 5.
