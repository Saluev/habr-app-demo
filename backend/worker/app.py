import functools

import backend.wiring
from backend.tasks.index import index
from backend.tasks.parse import parse_card_markup

wiring = backend.wiring.Wiring()
app = wiring.celery_app


per_process_wiring = None


def provide_wiring(task):

    @functools.wraps(task)
    def wrapped_task(*args, **kwargs):
        global per_process_wiring
        if per_process_wiring is None:
            per_process_wiring = backend.wiring.Wiring()
        return task(*args, **kwargs, wiring=per_process_wiring)

    return wrapped_task


for task in [
    index,
    parse_card_markup,
]:
    app.task(provide_wiring(task))
