import supervisely_lib as sly


# screenshot
# https://prnt.sc/taz5a3

team_id = 1
workspace_id = 1
agent_name = "max_server"
model_name = "YOLO v3 (COCO)"

api = sly.Api.from_env()

team = api.team.get_info_by_id(team_id)
workspace = api.workspace.get_info_by_id(workspace_id)

agent = api.agent.get_info_by_name(team.id, agent_name)
model = api.model.get_info_by_name(workspace.id, model_name)

task_ids = api.model.get_deploy_tasks(model.id)
if len(task_ids) == 0:
    print('Model {!r} is not deployed. Deploying...'.format(model.name))
    task_id = api.task.deploy_model(agent.id, model.id)
else:
    print('Model {!r} has been already deployed'.format(model.name))
    task_id = task_ids[0]

print('Deploy task_id = {}'.format(task_id))

api.task.stop(task_id)
api.task.wait(task_id, api.task.Status.STOPPED)
print("Task stopped")