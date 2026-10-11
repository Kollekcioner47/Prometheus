# files/08_rules — файлы практики 8

Каталог относится к практике 8 «Правила записи и оповещения»
(файл `8_rules.txt`). Содержимое всех файлов напечатано и в самой
практике: на занятии правила набираются вместе с преподавателем,
а этот каталог нужен, чтобы взять готовое, если что-то не набралось.

Готовых решающих скриптов здесь нет. Юнит-тест `tests/rules.test.yml`
скриптом не является: это файл входных данных для `promtool`, и его
текст — предмет изучения целиком.

## Что лежит в каталоге

| Файл | К какому шагу | Что это |
|---|---|---|
| `recording.rules.yml` | шаг 5 | правила записи: `job:node_cpu:ratio` |
| `alerting.rules.yml` | шаги 7, 8, 11 | правила оповещения: `InstanceDown`, |
|  |  | `HostOutOfMemory`, `DiskWillFillIn4Hours`, `Watchdog` |
| `prometheus.fragment.yml` | шаги 2 и 10 | фрагмент `prometheus.yml`: |
|  |  | `rule_files` и закомментированная секция `alerting` |
| `tests/rules.test.yml` | шаг 10 | юнит-тест правил для `promtool test rules` |

## Как этим пользоваться

1. **Куда кладутся правила.** Файлы правил лежат не рядом
   с `prometheus.yml`, а в каталоге `/etc/prometheus/rules/`:

        sudo install -d -o prometheus -g prometheus /etc/prometheus/rules
        sudo install -o prometheus -g prometheus -m 0644 \
            recording.rules.yml /etc/prometheus/rules/recording.rules.yml
        sudo install -o prometheus -g prometheus -m 0644 \
            alerting.rules.yml /etc/prometheus/rules/alerting.rules.yml

   В конфигурации Prometheus каталог подключается целиком:

        rule_files:
          - /etc/prometheus/rules/*.yml

2. **Проверка до перезагрузки.** Оба файла проверяются `promtool`
   отдельно от конфигурации:

        promtool check rules /etc/prometheus/rules/recording.rules.yml
        promtool check rules /etc/prometheus/rules/alerting.rules.yml

3. **Юнит-тест.** Запускается из этого каталога, потому что путь
   к файлу правил внутри теста относительный:

        cd files/08_rules
        promtool test rules tests/rules.test.yml

   Ожидаемый результат — `SUCCESS` и строка о числе проверенных
   групп и правил. Если тест не находит `alerting.rules.yml`,
   значит команда запущена из другого каталога.

4. **`prometheus.fragment.yml`** — фрагмент, а не полный файл:
   Prometheus с ним не запустится, в нём нет полноценного парка целей.
   Он показывает, что именно дописывается в `/etc/prometheus/prometheus.yml`
   на машине `mon`. Секция `alerting` в нём закомментирована: она
   включается в практике 9, когда появляется Alertmanager.

## Что важно помнить

* Правило записи и правило оповещения — разные вещи. Поле `record`
  создаёт новый ряд, поле `alert` включает состояние оповещения.
  У одного правила не может быть одновременно `record` и `alert`.
* `for` без `evaluation_interval` не работает как задумано: выдержка
  отсчитывается в вычислениях, а не в секундах стенных часов.
* `severity` — обычная метка. Prometheus по ней ничего не решает;
  по ней маршрутизирует Alertmanager в практике 9.
* Правило может показывать `SUCCESS` от `promtool` и при этом
  не работать: `promtool check rules` проверяет текст файла, а не то,
  что файл подключён в `rule_files`.

## Чего в каталоге нет и почему

* **Готового `prometheus.yml` целиком** здесь нет: правила — часть
  рабочей конфигурации машины `mon`, и она собирается по шагам
  в практиках 2–6.
* **`alertmanager.yml`** здесь тоже нет: получатели и маршруты —
  тема практики 9.
* **Готовых `.sh` и `.ps1`** нет по общему правилу курса.

Единый реестр сущностей курса — в `МЕТОДИКА_курса.md`, раздел 5.
