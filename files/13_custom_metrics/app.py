#!/usr/bin/env python3
"""Экспортёр очереди разовых заданий для практики 13 курса.

Файл намеренно написан целиком и с комментариями: в курсе он
и есть предмет изучения. Прочитайте его построчно, прежде чем
запускать. Подробный разбор каждой строки — в практике 13.

Учебные значения: адрес прослушивания 0.0.0.0, порт 9200.
"""

import argparse
import logging
import random
import signal
import threading

from prometheus_client import (Counter, Gauge, Histogram,
                               start_http_server)

LOG = logging.getLogger("lab_exporter")

# Флаг остановки. Он на уровне модуля, а не внутри main(): до него
# дотягиваются и рабочие потоки, и обработчик сигнала.
STOP = threading.Event()

# Порт 9200 закреплён в реестре сущностей курса (МЕТОДИКА, раздел 5).
DEFAULT_PORT = 9200

# Единица измерения одна: секунды. Бакеты подобраны под поведение
# задания лаборатории: оно заканчивается за минуту-две.
JOB_DURATION_BUCKETS = (0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0,
                        120.0, 300.0)

# Метрика 1: длина очереди в штуках заданий. Это gauge: значение
# ходит вверх и вниз, суммировать его во времени нельзя.
QUEUE_DEPTH = Gauge(
    "lab_queue_depth",
    "Сколько разовых заданий ждёт обработки прямо сейчас")

# Метрика 2: длительность одного задания в секундах. Это
# histogram: ряд значений раскладывается по бакетам, и из бакетов
# потом считается квантиль.
JOB_DURATION = Histogram(
    "lab_job_duration_seconds",
    "Сколько секунд заняло одно разовое задание",
    buckets=JOB_DURATION_BUCKETS)

# Метрика 3: сколько заданий обработано с момента запуска службы.
# Это counter: имя заканчивается на _total, значение только растёт,
# и по нему считают скорость через rate().
JOBS_DONE = Counter(
    "lab_batch_jobs_total",
    "Сколько разовых заданий обработано с момента запуска")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Экспортёр очереди разовых заданий (практика 13)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="порт для /metrics, по умолчанию 9200")
    return parser.parse_args()


def on_signal(signum, frame):
    """SIGTERM и SIGINT: выходим из цикла, а не падаем с трейсбеком."""
    LOG.info("получен сигнал %s, завершаемся", signum)
    STOP.set()


def do_one_job():
    """Одно задание: работа, метрика длительности, счётчик, запись."""
    seconds = random.uniform(0.2, 20.0)
    if STOP.wait(seconds):
        return None
    JOB_DURATION.observe(seconds)
    JOBS_DONE.inc()
    LOG.info("задание обработано за %.2f с", seconds)
    return seconds


def producer(queue):
    """Имитация притока заданий: то очередь растёт, то пустеет."""
    while not STOP.is_set():
        queue[0] += random.randint(1, 3)
        QUEUE_DEPTH.set(queue[0])
        LOG.info("в очередь добавлено, теперь %d", queue[0])
        STOP.wait(random.uniform(2.0, 15.0))


def consumer(queue):
    """Имитация разбора очереди: забираем по одному заданию."""
    while not STOP.is_set():
        if queue[0] > 0:
            queue[0] -= 1
            QUEUE_DEPTH.set(queue[0])
            LOG.info("задание взято из очереди, осталось %d", queue[0])
        STOP.wait(random.uniform(1.0, 8.0))


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    # Метрики отдаёт отдельный поток; основной занят работой задания.
    start_http_server(args.port, addr="0.0.0.0")
    LOG.info("метрики на http://0.0.0.0:%d/metrics", args.port)

    # queue — список из одного числа: своя копия значения, чтобы
    # не заглядывать во внутренние поля объекта Gauge.
    queue = [0]
    threading.Thread(target=producer, args=(queue,), daemon=True).start()
    threading.Thread(target=consumer, args=(queue,), daemon=True).start()

    while not STOP.is_set():
        try:
            do_one_job()
        except Exception:
            # Операцию, которая упала, в счётчик успеха не пишем:
            # иначе метрика начнёт врать.
            LOG.exception("задание упало, счётчик успеха не трогаем")
    LOG.info("остановлено")


if __name__ == "__main__":
    main()
