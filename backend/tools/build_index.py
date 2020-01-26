from backend.tasks.index import index
from backend.wiring import Wiring

if __name__ == "__main__":
    wiring = Wiring()
    wiring.task_queue.enqueue_call(index)
