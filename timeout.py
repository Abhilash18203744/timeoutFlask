import functools
from multiprocessing import Process, Queue

def timeout(seconds=10, error_message=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            q = Queue()

            def target(q, *args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    q.put((None, result))
                except Exception as e:
                    q.put((e, None))

            p = Process(target=target, args=(q,) + args, kwargs=kwargs)
            p.start()
            p.join(seconds)

            if p.is_alive():
                p.terminate()
                raise TimeoutError(error_message or f"Function {func.__name__} timed out after {seconds} seconds")

            exception, result = q.get()
            if exception:
                raise exception

            return result

        return wrapper
    return decorator
