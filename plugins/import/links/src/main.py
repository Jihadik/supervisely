# coding: utf-8

import os
from slugify import slugify

from supervisely_lib.io.json import load_json_file, dump_json_file
from supervisely_lib import TaskPaths
import supervisely_lib as sly


def create_project(api, workspace_id, project_name, append_to_existing_project):
    if append_to_existing_project is True:
        dst_project = api.project.get_info_by_name(workspace_id, project_name)
        if dst_project is None:
            raise RuntimeError("Project {!r} not found".format(project_name))
    else:
        dst_project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    return dst_project


def process_dataset_links(api, project_info, file_path, normalize_url=True):
    dataset_name = os.path.relpath(os.path.splitext(file_path)[0], TaskPaths.DATA_DIR).replace(os.sep, '__')
    links_counter = 0

    with open(file_path) as in_file:
        urls = [line.strip() for line in in_file]

    if len(urls) > 0:
        dst_dataset = api.dataset.create(project_info.id, dataset_name, change_name_if_conflict=True)
        progress = sly.Progress('Importing dataset: {}'.format(dataset_name), len(urls))
        for url in urls:
            if url:
                try:
                    basename = os.path.basename(url)
                    sly.image.validate_ext(basename)
                    file_name, file_ext = os.path.splitext(basename)
                    #if file_ext == '':
                    #    file_ext = sly.image.DEFAULT_IMG_EXT
                    if normalize_url is True:
                        image_name = slugify(file_name, lowercase=False, save_order=True) + file_ext
                    else:
                        image_name = file_name + file_ext
                    image_name = api.image.get_free_name(dst_dataset.id, image_name)
                    api.image.upload_link(dst_dataset.id, image_name, url)
                    links_counter += 1

                except Exception as e:
                    exc_str = str(e)
                    sly.logger.warn('Input link skipped due to error: {}'.format(exc_str), exc_info=True, extra={
                        'exc_str': exc_str,
                        'file_path': file_path,
                        'link': url,
                    })
            progress.iter_done_report()
    return links_counter


def main():
    task_config = load_json_file(TaskPaths.TASK_CONFIG_PATH)

    convert_options = task_config['options']
    normalize_url = True
    if convert_options is not None:
        normalize_url = convert_options.get('normalize_image_name', True)

    server_address = task_config['server_address']
    token = task_config['api_token']
    append_to_existing_project = task_config['append_to_existing_project']

    api = sly.Api(server_address, token)
    task_info = api.task.get_info_by_id(task_config['task_id'])
    # TODO migrate to passing workspace id via the task config.
    project_info = create_project(
        api, task_info["workspaceId"], task_config['res_names']['project'], append_to_existing_project)

    total_counter = 0
    for file_path in sly.fs.list_files_recursively(
            TaskPaths.DATA_DIR, filter_fn=lambda path: sly.fs.get_file_ext(path).lower() == '.txt'):
        total_counter += process_dataset_links(api, project_info, file_path, normalize_url=normalize_url)

    if total_counter == 0:
        raise RuntimeError('Result project is empty! No valid links find in files.')

    dump_json_file({'project_id': project_info.id}, os.path.join(TaskPaths.RESULTS_DIR, 'project_info.json'))


if __name__ == '__main__':
    sly.main_wrapper('IMAGES_LINKS_IMPORT', main)
