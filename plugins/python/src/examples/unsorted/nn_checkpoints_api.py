import pprint
import supervisely_lib as sly
import random
pp = pprint.PrettyPrinter(indent=4)

api = sly.Api.from_env()

task_id = 916

metrics = api.task.get_training_metrics(task_id)
#pp.pprint(metrics)

ckpts_info = api.task.list_checkpoints(task_id)
#pp.pprint(ckpts_info)

print("cnt checkpoints = ", len(ckpts_info))
random_ckpt_info = random.choice(ckpts_info)
random_ckpt_id = random_ckpt_info["id"]

new_model_name = api.model.create_from_checkpoint(task_id, random_ckpt_id, "my_model_name", change_name_if_conflict=True)
print("finish. New model name = ", new_model_name)

