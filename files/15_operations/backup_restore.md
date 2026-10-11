Резервная копия мониторинга и проверка восстановления

Файл к шагу части 1 практики 15. Здесь собрано то, что нужно знать
о резервном копировании мониторинга до того, как копия понадобится.

Главная мысль

Мониторинг восстанавливается из конфигурации, а не из данных.
Конфигурация занимает килобайты, данные — гигабайты, и именно
конфигурация определяет, что мониторинг делает.

Обратное утверждение тоже верно и его стоит сказать прямо:
восстановление одного без другого не восстанавливает мониторинг.
Копия каталога данных при потерянной конфигурации даёт набор
непонятных каталогов с блоками, которые нечем прочитать.

Что копировать

В таблице три колонки: что копируем, где это лежит и зачем нужно
именно оно.

  * Конфигурация Prometheus
        где: /etc/prometheus/prometheus.yml
        зачем: цели, интервалы сбора, внешние метки
  * Файлы правил
        где: /etc/prometheus/rules/
        зачем: правила записи и правила оповещения
  * Файлы обнаружения целей
        где: /etc/prometheus/targets/
        зачем: списки целей для file_sd
  * Конфигурация Alertmanager
        где: /etc/alertmanager/alertmanager.yml
        зачем: дерево маршрутов, получатели, подавление
  * Шаблоны сообщений
        где: /etc/alertmanager/templates/
        зачем: текст оповещений для получателя
  * Провижининг Grafana
        где: /etc/grafana/provisioning/
        зачем: источник данных и провайдер дашбордов
  * Дашборды как код
        где: /var/lib/grafana/dashboards/
        зачем: JSON дашбордов, взятые из git
  * Настройки Grafana
        где: /etc/grafana/grafana.ini
        зачем: порт, пути, срок жизни сессии
  * Юнит-файлы служб
        где: /etc/systemd/system/*.service
        зачем: как именно запускается служба и от какой учётной записи
  * Конфигурация blackbox
        где: /etc/blackbox_exporter/blackbox.yml
        зачем: модули внешних проверок

Проверочные файлы для promtool (*.test.yml) копируются вместе
с правилами: без них после восстановления нельзя ответить
на вопрос «правило вообще работает».

Что не копировать

  * База данных TSDB
        где: /var/lib/prometheus/
        почему нет: десятки гигабайт, и её восстановление
        не восстанавливает мониторинг
  * Данные Alertmanager
        где: /var/lib/alertmanager/
        почему нет: история silence и групп; потеря неприятна,
        но не отказ
  * Журналы
        где: journalctl, /var/log/
        почему нет: нужны для разбора, но не для восстановления
  * Кэш Grafana
        где: /var/lib/grafana/
        почему нет: пересоздаётся сам
  * Архивы релизов
        где: /home/engineer/distr/
        почему нет: скачиваются заново

Почему TSDB не копируют, хотя «данные же жалко»:

* она большая — на стенде курса это единицы гигабайт, в рабочей
  среде это сотни гигабайт, и копия такого размера не проверяется
  ни разу, а значит, восстановлению не подлежит;
* она быстро устаревает: копия часовой давности уже не отвечает
  на вопрос «что было, когда сломалось»;
* она не восстанавливает мониторинг: Prometheus с целой TSDB
  и без prometheus.yml не поднимется вообще;
* долгое хранение решается не копией, а remote_write в отдельное
  хранилище — об этом была практика 14.

Копию TSDB делают, когда переносят Prometheus на другую машину
и хотят сохранить историю. Это отдельная задача с отдельным
порядком действий, и в курсе она не разбирается.

Команды

Копия делается на другую машину: копия на том же диске защищает
от ошибки человека, но не от отказа диска.

  # На mon: собираем конфигурацию в один архив.
  sudo tar czf /home/engineer/monitoring-config-$(date +%F).tar.gz \
    -C / \
    etc/prometheus \
    etc/alertmanager \
    etc/grafana/provisioning \
    etc/grafana/grafana.ini \
    etc/blackbox_exporter \
    var/lib/grafana/dashboards \
    etc/systemd/system/prometheus.service \
    etc/systemd/system/alertmanager.service \
    etc/systemd/system/blackbox_exporter.service

  # На mon: закрываем архив от посторонних и отправляем на web1.
  # В архиве лежит alertmanager.yml с токеном бота, поэтому права
  # 600, а не 644 по умолчанию при umask 022.
  sudo chmod 600 /home/engineer/monitoring-config-*.tar.gz
  scp /home/engineer/monitoring-config-*.tar.gz engineer@10.0.2.11:/home/engineer/

  # Контрольная сумма: нужна, чтобы отличить «архив побился»
  # от «мы распаковали не то».
  sha256sum /home/engineer/monitoring-config-*.tar.gz

Список файлов в архиве проверяется до отправки: tar tzf
показывает содержимое без распаковки.

  tar tzf /home/engineer/monitoring-config-2026-05-14.tar.gz | head -20
  etc/prometheus/prometheus.yml
  etc/prometheus/rules/lab.rules.yml
  etc/alertmanager/alertmanager.yml
  ...

Проверка восстановления

Проверка делается в отдельный каталог и без остановки работающего
мониторинга. Копия, которую ни разу не распаковывали,
копией не является.

  # Распаковываем в отдельный каталог, а не в корень.
  mkdir -p /home/engineer/restore-check
  tar xzf /home/engineer/monitoring-config-2026-05-14.tar.gz \
    -C /home/engineer/restore-check
  ls -R /home/engineer/restore-check/etc/prometheus

Проверка набранного из копии конфигурации — теми же командами,
что и обычно:

  cd /home/engineer/restore-check/etc/prometheus
  promtool check config prometheus.yml
  promtool check rules rules/*.rules.yml
  cd /home/engineer/restore-check/etc/alertmanager
  amtool check-config alertmanager.yml

Проверка запуском — единственный способ убедиться, что конфигурация
не только разбирается, но и работает. Запускаем второй экземпляр
Prometheus из копии на свободном порту и с отдельным каталогом
данных. Работающий экземпляр при этом не трогаем.

Второй экземпляр запускается временной службой systemd, а не фоном
из оболочки: тогда у него свои журнал и признак активности, а после
перезагрузки он не остаётся в списке служб. Имя модуля указано
явно (--unit=prometheus-restore), иначе systemd присвоит случайное
и остановить экземпляр будет нечем.

  sudo mkdir -p /var/lib/prometheus-restore
  sudo chown prometheus:prometheus /var/lib/prometheus-restore
  sudo systemd-run --unit=prometheus-restore \
    --uid=prometheus --gid=prometheus \
    /usr/local/bin/prometheus \
    --config.file=/home/engineer/restore-check/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus-restore \
    --web.listen-address=127.0.0.1:9097
  curl -s localhost:9097/-/ready
  Prometheus Server is Ready.

После проверки второй экземпляр останавливают и убирают за ним:

  sudo systemctl stop prometheus-restore
  sudo rm -rf /var/lib/prometheus-restore /home/engineer/restore-check

Порядок восстановления на чистой машине

1. Поставить те же версии из архивов: Prometheus 3.15.0,
   Alertmanager 0.34.1, экспортёры — те же, что были.
2. Создать учётные записи служб: prometheus, node_exporter,
   blackbox, pushgateway. Учётные записи — часть конфигурации,
   и в архив они не попадают.
3. Создать каталоги: /etc/prometheus, /var/lib/prometheus,
   /etc/alertmanager, /var/lib/alertmanager — с владельцем
   prometheus и правами 0755.
4. Распаковать архив конфигурации поверх /.
5. Вернуть права: chmod 600 /etc/alertmanager/alertmanager.yml,
   chown prometheus:prometheus /etc/prometheus/prometheus.yml.
6. Восстановить юнит-файлы, выполнить systemctl daemon-reload,
   включить и запустить службы.
7. Проверить: promtool check config, amtool check-config,
   страница Targets, тестовое оповещение.

Первые две минуты после восстановления Prometheus покажет пустые
графики. Это не ошибка: каталог данных пуст, и история начинается
заново. Ошибка — если после этого цели в состоянии DOWN: значит,
не восстановлены права или файлы обнаружения целей.

Чего не делать

* Не проверять копию распаковкой в корень работающей системы.
  Ошибка в один путь затирает боевую конфигурацию — и тогда
  восстановление понадобится раньше, чем планировалось.
* Не считать копией файл, который лежит рядом с оригиналом
  на том же диске.
* Не отправлять архив с alertmanager.yml по почте или в мессенджер:
  в нём токен бота и пароль SMTP.
* Не хранить копию только в одном месте и не проверять её раз в год.
