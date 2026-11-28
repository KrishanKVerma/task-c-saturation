from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
import taskc_eval

BASE = taskc_eval.task_c()
BASE_SAMPLE = BASE.dataset[0]

def record_to_sample(record):
    return Sample(
        id=record["id"],
        input=record["framing"] + BASE_SAMPLE.input,
        target=BASE_SAMPLE.target,
        metadata={"framing": record["id"]},
    )

@task
def task_c_variants():
    return Task(
        dataset=json_dataset("variants.jsonl", sample_fields=record_to_sample),
        solver=BASE.solver,
        scorer=BASE.scorer,
    )
