# Каталог files/12_push_blackbox/

Файлы практики 12 «Push-модель: Pushgateway, textfile, blackbox».
Все они изучаются в тексте практики и напечатаны там целиком.

## Что за файлы

| Файл | К какому шагу | Как использовать |
|---|---|---|
| `blackbox.yml` | шаг 8 | конфигурация `/etc/blackbox_exporter/blackbox.yml`; модули `http_2xx`, `http_post_2xx`, `tcp_connect`, `icmp` |
| `blackbox_exporter.service` | шаг 8 | юнит-файл systemd для blackbox_exporter на `mon`, порт 9115, пользователь `blackbox` |
| `pushgateway.service` | шаг 4 | юнит-файл systemd для Pushgateway на `mon`, порт 9091, пользователь `pushgateway` |
| `textfile/lab_backup.prom` | шаг 2 | образец файла для textfile collector node_exporter; кладётся в `/var/lib/node_exporter/textfile` |
| `prometheus.fragment.yml` | шаги 4 и 10 | фрагмент `scrape_configs` с заданиями `pushgateway` и `blackbox_http` |

## Чего в каталоге нет

Готовых решающих скриптов здесь нет и быть не должно: студент,
запустивший готовое, не поймёт ничего. `textfile/lab_backup.prom` —
это данные, а не скрипт: файл формата exposition, который читает
node_exporter. Задание `backup` на `db1` пишет такой файл само,
а в практике показано, как именно.

## Как пользоваться

Файлы берут там, где запись не набралась, и сверяют с тем, что
напечатано в практике. Копировать `prometheus.fragment.yml` целиком
в `/etc/prometheus/prometheus.yml` нельзя: это фрагмент одного
раздела, без `global`, `external_labels` и `alerting`.

Пути и имена в файлах совпадают с реестром сущностей курса:
`mon` 10.0.2.5, `db1` 10.0.2.12, порты 9091 и 9115, учётные записи
`pushgateway` и `blackbox`, каталог `/etc/blackbox_exporter`.
