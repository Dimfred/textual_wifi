import threading as th
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=4)


def run_background(f, *args, **kwargs):
    th.Thread(target=f, args=args, kwargs=kwargs).start()
