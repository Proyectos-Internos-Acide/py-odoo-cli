import requests
import threading
import time

URL = "https://www.waykitrek.net/"
THREADS = 1000
REQUESTS_PER_THREAD = 200

success = 0
errors = 0
lock = threading.Lock()

# Si usas un certificado autofirmado en localhost
requests.packages.urllib3.disable_warnings()

def worker():
    global success, errors

    session = requests.Session()

    for _ in range(REQUESTS_PER_THREAD):
        try:
            r = session.get(URL, timeout=5, verify=False)

            with lock:
                if r.status_code == 200:
                    success += 1
                else:
                    errors += 1

        except Exception:
            with lock:
                errors += 1

threads = []

inicio = time.time()

for _ in range(THREADS):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

fin = time.time()

total = THREADS * REQUESTS_PER_THREAD

print(f"Total requests : {total}")
print(f"Success        : {success}")
print(f"Errors         : {errors}")
print(f"Tiempo         : {fin - inicio:.2f} s")
print(f"Req/s          : {total / (fin - inicio):.2f}")