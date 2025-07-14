from datetime import datetime

from app.myapp import add, bad_throw, is_pycurl_available, bad_throw_base
from celery import group
import time

# create queue test


worker_prefetch_multiplier = 16
num_iters = 10
num_tasks = worker_prefetch_multiplier * 8

tasks = [add.s(1, 2) for _ in range(num_tasks)]
# tasks.append(bad_throw.s(2,3))
# tasks.append(bad_throw_base.s(2,3))
# tasks.append(is_pycurl_available.s())

is_pycurl_available()
# is_pycurl_available.delay()
# exit()

all_times = []
print("start,run,time,throughput")
for i in range(num_iters):
    # print(f"run {i} start {datetime.now()}")
    g = group(tasks)
    start_dtime = datetime.now()
    start_time = time.time()
    result = g.apply_async()
    result.get()
    end_time = time.time()
    total_time = end_time - start_time
    throughput = num_tasks / total_time
    all_times.append(total_time)
    # print(f"Processed {num_tasks} tasks in {total_time:.2f} seconds")
    # print(f"Throughput: {throughput:.2f} tasks per second")
    print(f"{start_dtime},{i},{total_time},{throughput}")

print(f"iterations: {num_iters}")
print(f"tasks in iteration: {num_tasks}")
print(f"total tasks: {num_tasks * num_iters}")
print(f"total time: {sum(all_times):.2f} seconds")
print(f"average time of iteration: {sum(all_times) / len(all_times):.2f} seconds")
print(f"average throughput: {num_tasks * num_iters / sum(all_times):.2f} tasks per second")
