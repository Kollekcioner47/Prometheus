# Чек-лист приёмки итоговой работы трека «3 дня»

Отмечайте результат команды, а не своё впечатление. Пункт, который
не подтверждён выводом команды, считается невыполненным: половина
ошибок в мониторинге — это уверенность «у меня работает».

## Пункт 1. Prometheus и цели

  systemctl is-active prometheus
  promtool check config /etc/prometheus/prometheus.yml
  curl -s http://localhost:9090/api/v1/targets | grep -c '"health":"up"'

Ожидается: `active`, `SUCCESS`, число не меньше семи целей
(шесть без win1). Страница Status → Targets: все цели `UP`,
кроме win1, если этой машины в стенде нет.

## Пункт 2. Экспортёры на четырёх машинах

  for h in 10.0.2.5 10.0.2.11 10.0.2.12 10.0.2.13; do \
      curl -s -o /dev/null -w "$h %{http_code}\n" http://$h:9100/metrics; done
  curl -s http://10.0.2.11:9113/metrics | grep -c '^nginx_'
  curl -s http://10.0.2.12:9187/metrics | grep '^pg_up'
  curl -s http://10.0.2.13:8080/metrics | grep -c '^container_'

Ожидается: четыре ответа `200`; у nginx и postgres счётчики больше
нуля; `pg_up 1`; у cAdvisor есть строки `container_*`.

## Пункт 3. Правила

  promtool check rules /etc/prometheus/rules/alerting.rules.yml
  promtool test rules /etc/prometheus/rules/tests/rules.test.yml
  curl -s http://localhost:9090/api/v1/rules | grep -c '"name"'

Ожидается: `SUCCESS` дважды, `FAILED` ни разу. На странице Alerts
видно шесть правил; `Watchdog` в состоянии `Firing` — это признак,
что вычисление идёт.

## Пункт 4. Alertmanager и доставка

  systemctl is-active alertmanager
  amtool check-config /etc/alertmanager/alertmanager.yml
  amtool config routes show --config.file=/etc/alertmanager/alertmanager.yml
  amtool alert query --alertmanager.url=http://localhost:9093
  tail -n 20 /home/engineer/webhook.log

Ожидается: `active`, `SUCCESS`, дерево из трёх маршрутов с вложенным
маршрутом Watchdog, в логе приёмника — JSON с полем `status`.
Проверка доставки: `up == 0` на любой цели даёт сообщение через
1–2 минуты, возврат службы — сообщение со `status: resolved`.

## Пункт 5. Grafana

  systemctl is-active grafana-server
  curl -s -u admin:Console47 http://localhost:3000/api/datasources | grep -c prometheus
  curl -s -u admin:Console47 "http://localhost:3000/api/search?query=Состояние" | grep -c lab-fleet-state

Ожидается: `active`, источник данных найден, дашборд
`lab-fleet-state` в списке, на панелях данные по всем четырём
машинам и работающая переменная `instance`.

## Уборка после приёмки

  ssh engineer@10.0.2.13 'ls -lh /home/engineer/fill.bin'
  ssh engineer@10.0.2.11 'sudo ufw status numbered'

Ожидается: файл `fill.bin` удалён, правило для порта 9113 снято,
`ufw` выключен. Снимок стенда сделан после уборки: снимок
со учебными отказами внутри бесполезен как точка возврата.
