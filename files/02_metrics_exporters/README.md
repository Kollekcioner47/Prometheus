# files/02_metrics_exporters — файлы практики 2

Каталог относится к практике 2 «Метрики, формат exposition и первый
экспортёр».

## Что здесь лежит

* `prometheus.yml` — полная конфигурация Prometheus для этого шага:
  `global` (`scrape_interval`, `evaluation_interval`, `external_labels`)
  и два задания: `prometheus` и `node` с четырьмя целями. Это тот же
  текст, что напечатан в практике 2, шаг 8.
* `node_exporter.service` — юнит-файл systemd для node_exporter 1.12.1.
  Кладётся в `/etc/systemd/system/node_exporter.service` на каждой
  из четырёх Linux-машин. Тот же текст напечатан в шаге 5.
* `example_metrics.txt` — правдоподобный фрагмент вывода
  `http://10.0.2.5:9100/metrics` со строками `# HELP`, `# TYPE`
  и метриками типов counter, gauge и histogram. Разбирается
  в шагах 2 и 3.

## Как пользоваться

Файлы нужны, чтобы взять готовое, если что-то не набралось вручную.
На занятии конфигурация и юнит-файл набираются вместе с
преподавателем: смысл практики в том, чтобы увидеть каждую строку
и понять, что она делает.

Скопировать конфигурацию на место:

    sudo cp prometheus.yml /etc/prometheus/prometheus.yml
    sudo chown root:root /etc/prometheus/prometheus.yml
    sudo chmod 0644 /etc/prometheus/prometheus.yml

Проверить перед перезагрузкой:

    promtool check config /etc/prometheus/prometheus.yml

## Чего в каталоге нет

Готовых скриптов установки: `.sh`, `.ps1`, `.bat` здесь не лежит
и лежать не должно. Скрипт «сделай практику» экономит десять минут
и отнимает весь смысл занятия.
