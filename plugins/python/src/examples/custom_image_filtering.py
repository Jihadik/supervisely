import os
import supervisely_lib as sly
from supervisely_lib.api.api import SUPERVISELY_TASK_ID
import re

# all the field below will be automatically displayed in UI
WORKSPACE_ID = int('%%WORKSPACE_ID%%')
project_name = '%%IN_PROJECT_NAME%%'
result_project_name = '%%RESULT_PROJECT_NAME%%'
result_dataset_name = '%%RESULT_DATASET_NAME:None%%'
range_begin_value = int('%%RANGE_BEGIN_VALUE%%')
range_end_value = int('%%RANGE_END_VALUE%%')

image_ids_range = [range_begin_value, range_end_value]

if result_dataset_name == 'None':
    result_dataset_name = None


api = sly.Api(server_address=os.environ['SERVER_ADDRESS'], token=os.environ['API_TOKEN'])


#to add created project to a task list (output column)
task_id = int(os.getenv(SUPERVISELY_TASK_ID))
api.add_additional_field('taskId', task_id)
#api.add_header('x-task-id', str(task_id))


# Verify input values
workspace = api.workspace.get_info_by_id(WORKSPACE_ID)
if workspace is None:
    raise RuntimeError("Workspace {!r} not found".format(WORKSPACE_ID))

project = api.project.get_info_by_name(workspace.id, project_name)
if project is None:
    raise RuntimeError("Project {!r} not found".format(project_name))

print("Workspace: id={}, name={}".format(workspace.id, workspace.name))
print("Project: id={}, name={}".format(project.id, project.name))


# Create resulting project
res_project = api.project.create(workspace.id, result_project_name, change_name_if_conflict=True)
print("Resulting project: id={}, name={}".format(res_project.id, res_project.name))

#clone project meta (list of classes and tags) from input project to the resulting one
project_meta_json = api.project.get_meta(project.id)
api.project.update_meta(res_project.id, project_meta_json)

# create dataset in resulting project if needed
res_dataset = None
if result_dataset_name is not None:
    res_dataset = api.dataset.create(res_project.id, result_dataset_name, change_name_if_conflict=False)


# filtering funtion
def filter_image_by_name(image_name, image_ids_range=[3, 11]):
    need_keep = False

    numbers = list(map(int, re.findall(r'\d+', image_name)))
    image_id = numbers[1]

    if image_id >= image_ids_range[0] and image_id <= image_ids_range[1]:
        need_keep = True

    return need_keep


# Iterate over all images, filter and combine them if needed
for dataset in api.dataset.get_list(project.id):
    sly.logger.info('Dataset: {}'.format(dataset.name))

    dst_dataset = None
    if result_dataset_name is None:
        dst_dataset = api.dataset.create(res_project.id, dataset.name)
    else:
        dst_dataset = res_dataset

    images_in_dataset = api.image.get_list(dataset.id)

    filtered_image_ids = []
    for image_info in images_in_dataset:
        need_keep = filter_image_by_name(image_info.name)
        if need_keep == True:
            filtered_image_ids.append(image_info.id)

    if len(filtered_image_ids) > 0:
        copied_images = api.image.copy_batch(dst_dataset.id, filtered_image_ids, change_name_if_conflict=False,
                                             with_annotations=True)

    sly.logger.info("Number of copied images = {}".format(len(filtered_image_ids)))


sly.logger.info('PROJECT_CREATED', extra={'event_type': sly.EventType.PROJECT_CREATED, 'project_id': res_project.id})