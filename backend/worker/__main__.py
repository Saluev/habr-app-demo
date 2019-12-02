import argparse
import uuid

import rq
from rq.job import Job

import backend.wiring

parser = argparse.ArgumentParser(description="Run worker.")
parser.add_argument(
    "--burst",
    action="store_const",
    const=True,
    default=False,
    help="enable burst mode")
args = parser.parse_args()

wiring = backend.wiring.Wiring()


class JobWithWiring(Job):

    @property
    def kwargs(self):
        result = dict(super().kwargs)
        result["wiring"] = backend.wiring.Wiring()
        return result

    @kwargs.setter
    def kwargs(self, value):
        super().kwargs = value


with rq.Connection(wiring.redis):
    w = rq.Worker(
        queues=[wiring.settings.TASK_QUEUE_NAME],
        name=uuid.uuid4().hex,
        job_class=JobWithWiring)
    w.work(burst=args.burst)
