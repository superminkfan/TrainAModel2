import sys
import time
import threading
import itertools

def animate():
    symbols = itertools.cycle("/|\\-")  # Циклическая смена символов
    while not stop_event.is_set():
        sys.stdout.write(f"\r[{next(symbols)}] Идет обработка... ")
        sys.stdout.flush()
        time.sleep(0.2)  # Интервал смены символов

def long_running_task():
    time.sleep(10)  # Симуляция долгой работы

# Флаг для остановки анимации
stop_event = threading.Event()

# Запускаем анимацию в отдельном потоке
animation_thread = threading.Thread(target=animate)
animation_thread.start()

# Запускаем длительную задачу
long_running_task()

# Останавливаем анимацию
stop_event.set()
animation_thread.join()

# Очищаем строку анимации
sys.stdout.write("\rГотово!            \n")
sys.stdout.flush()
