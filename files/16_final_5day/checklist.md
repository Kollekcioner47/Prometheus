# Чек-лист приёмки итоговой работы. Практика 16.

Каждый пункт проверяется командой и имеет однозначный результат:
«работает» здесь означает конкретный вывод, а не общее впечатление.
Пункты, которые нельзя проверить командой, вынесены в конец
отдельным разделом — они не спрятаны среди проверяемых.

## 1. Prometheus собирает метрики

```
curl -s 'http://10.0.2.5:9090/api/v1/query?query=sum(up{env="lab"})'
```

Ожидаемый результат: `"value":[<время>,"7"]` или больше — число
целей стенда со значением 1. Ноль означает, что конфигурация
не применилась.

## 2. Цели обнаружены из файла, а не из static_configs

```
curl -s 'http://10.0.2.5:9090/api/v1/targets?state=active' \
  | grep -c 'node.json'
```

Ожидаемый результат: не ноль — метка `__meta_filepath` указывает
на файл. Дополнительно: в `/etc/prometheus/prometheus.yml` нет
ни одной строки `static_configs` внутри задания `node`.

## 3. Правила записи вычисляются

```
curl -s 'http://10.0.2.5:9090/api/v1/query?query=instance:node_cpu_utilization:ratio'
```

Ожидаемый результат: по одному ряду на каждую машину, значения
от 0 до 1. Пустой ответ означает, что правила не подключены или
в них ошибка.

## 4. Правила оповещения подключены и здоровы

```
curl -s 'http://10.0.2.5:9090/api/v1/rules' | grep -c '"name": "lab.alerting"'
curl -s 'http://10.0.2.5:9090/api/v1/query?query=increase(prometheus_rule_evaluation_failures_total[10m])'
```

Ожидаемый результат: группа найдена, приращение ошибок равно 0.

## 5. Тесты правил проходят

```
cd /etc/prometheus
promtool test rules rules/tests/rules.test.yml
```

Ожидаемый результат: `SUCCESS`. Ошибка `FAILED` указывает номер
теста и ожидаемое оповещение.

## 6. Конфигурация разбирается

```
cd /etc/prometheus
promtool check config prometheus.yml
promtool check rules rules/recording.rules.yml rules/alerting.rules.yml
cd /etc/alertmanager
amtool check-config alertmanager.yml
```

Ожидаемый результат: `SUCCESS: ... is valid prometheus config file`
у первой команды, `SUCCESS: N rules found` у второй,
`SUCCESS` у третьей.

## 7. Маршрутизация соответствует требованию

```
amtool config routes show --config.file=/etc/alertmanager/alertmanager.yml
```

Ожидаемый результат: три маршрута — `severity="critical"`,
`severity="warning"`, `severity="info"` — и разные получатели.

## 8. Пробное оповещение доходит до получателя

```
amtool alert add LabTestAlert severity=warning instance=10.0.2.11:9100 \
  --alertmanager.url=http://localhost:9093 \
  --annotation=summary="проверка канала оповещения"
```

Ожидаемый результат: сообщение появилось в почте дежурного
не позднее чем через час (`group_interval` маршрута warning).

## 9. Источник данных и дашборд пришли из файлов

```
sudo grep -c 'lab-prometheus' /etc/grafana/provisioning/datasources/prometheus.yml
sudo journalctl -u grafana-server -n 50 --no-pager | grep -i provision
curl -s -u engineer:Console47 \
  'http://localhost:3000/api/dashboards/uid/lab-fleet-overview' \
  | grep -o '"title":"Lab: состояние парка"'
```

Ожидаемый результат: источник и дашборд найдены, в журнале есть
строка про завершённый провижининг.

## 10. Свой экспортёр в строю

```
curl -s 'http://10.0.2.13:9200/metrics' | grep -E '^lab_(queue_depth|job_duration_seconds_count)'
curl -s 'http://10.0.2.5:9090/api/v1/query?query=job:lab_queue_depth:avg5m'
```

Ожидаемый результат: метрики отдаются экспортёром и видны
в Prometheus как правило записи.

## 11. Внешняя проверка работает

```
curl -s 'http://10.0.2.5:9090/api/v1/query?query=probe_success{env="lab"}'
```

Ожидаемый результат: по одному ряду на каждую цель заданий
`blackbox_http` и `blackbox_tls`, значение 1.

## 12. Резервная копия сделана и проверена

```
ls -l /home/engineer/monitoring-config-*.tar.gz
tar tzf /home/engineer/monitoring-config-*.tar.gz | head
ls -R /home/engineer/restore-check/etc/prometheus | head
```

Ожидаемый результат: архив существует, содержит конфигурацию
и правила, распакован в отдельный каталог, и `promtool check config`
на распакованном файле даёт `SUCCESS`.

## 13. Учётные записи и права

```
ps -o user= -C prometheus
ps -o user= -C alertmanager
sudo stat -c '%U %a %n' /etc/alertmanager/alertmanager.yml
```

Ожидаемый результат: `prometheus` у обеих служб,
`prometheus 600 /etc/alertmanager/alertmanager.yml`.

## 14. Учебные отказы разобраны и убраны

```
df -h /
ls -l /tmp/fill-disk.img
sudo ufw status
```

Ожидаемый результат: файл заполнения удалён, `ufw` выключен,
на стенде нет следов учебных отказов.

## Что осталось ручным шагом

Эти пункты командой не проверяются, и в рабочей среде их закрывают
системой управления конфигурацией или конвейером:

* **установка и обновление бинарников.** Архивы скачиваются руками,
  подмена файла в `/usr/local/bin` делается руками. Проверяется
  глазами: `prometheus --version` и `promtool --version`.
* **создание учётных записей служб.** `useradd` выполняется один раз
  и нигде не записан, кроме практик 1 и 9.
* **права на каталоги.** `chown prometheus:prometheus` и `chmod`
  после восстановления из копии — ручная последовательность.
* **создание файла паролей для прокси.** `htpasswd -B` требует
  ввода пароля и в конвейер не встраивается.
* **проверка, что оповещение дошло.** Доставку письма подтверждает
  человек, а не команда: Alertmanager гарантирует повтор,
  а не доставку.
* **сертификаты.** На стенде они самоподписанные; в рабочей среде
  это заявка во внешнюю систему.
* **снимок стенда.** Делается средствами гипервизора.
