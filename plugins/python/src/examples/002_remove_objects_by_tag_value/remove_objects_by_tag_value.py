import supervisely_lib as sly
import operator

WORKSPACE_ID = int('%%WORKSPACE_ID%%')
SRC_PROJECT_NAME = '%%IN_PROJECT_NAME%%'
DST_PROJECT_NAME = '%%RESULT_PROJECT_NAME%%'
TAG_NAME = '%%TAG_NAME%%'
CLASS_NAMES = '%%CLASS_NAMES:a,b%%'
OPERATOR_STR = '%%OPERATOR_STR:<=%%'
CLASS_THRESHOLDS = '%%CLASS_THRESHOLD:0.75,0.5%%'

# WORKSPACE_ID = 38
# SRC_PROJECT_NAME = "tutorial_project"
# DST_PROJECT_NAME = "result_filtered"
#
# TAG_NAME = "confidence"
# CLASS_NAMES = "car,dog"
# OPERATOR_STR = "<="
# CLASS_THRESHOLDS = "0.75,0.6"

CLASS_NAMES = list(map(str.strip, CLASS_NAMES.split(',')))
CLASS_THRESHOLDS = map(str.strip, CLASS_THRESHOLDS.split(','))
CLASS_THRESHOLDS = list(map(float, CLASS_THRESHOLDS))

operators = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq}

api = sly.Api.from_env()

project = api.project.get_info_by_name(WORKSPACE_ID, SRC_PROJECT_NAME)
meta_json = api.project.get_meta(project.id)
meta = sly.ProjectMeta.from_json(meta_json)

# validate input parameters
if OPERATOR_STR not in operators.keys():
    raise ValueError("Unknown operator {!r}".format(OPERATOR_STR))
if len(CLASS_NAMES) != len(CLASS_THRESHOLDS):
    raise ValueError("Inconsistent class names and thresholds")

tag_meta = meta.tag_metas.get(TAG_NAME)
if tag_meta is None:
    raise ValueError("Project does not have tag {!r}".format(TAG_NAME))
if tag_meta.value_type not in [sly.TagValueType.ANY_NUMBER, sly.TagValueType.ANY_STRING]:
    raise ValueError("Invalid tag {!r}".format(TAG_NAME))

for class_name in CLASS_NAMES:
    if meta.obj_classes.get(class_name) is None:
        raise ValueError("Project does not have class {!r}".format(class_name))

class_to_threshold = {}
for class_name, threshold in zip(CLASS_NAMES, CLASS_THRESHOLDS):
    class_to_threshold[class_name] = threshold

dst_project = api.project.create(WORKSPACE_ID, DST_PROJECT_NAME, change_name_if_conflict=True)
api.project.update_meta(dst_project.id, meta_json)

progress = sly.Progress("Processing", api.project.get_images_count(project.id))
for dataset in api.dataset.get_list(project.id):
    new_dataset = api.dataset.create(dst_project.id, dataset.name)
    images = api.image.get_list(dataset.id)
    for batch in sly.batched(images):
        image_ids = [image_info.id for image_info in batch]
        image_names = [image_info.name for image_info in batch]
        ann_infos = api.annotation.download_batch(dataset.id, image_ids)
        new_anns = []
        for ann_info in ann_infos:
            ann = sly.Annotation.from_json(ann_info.annotation, meta)
            new_labels = []
            for label in ann.labels:
                class_name = label.obj_class.name
                if class_name in CLASS_NAMES:
                    tag = label.tags.get(TAG_NAME)
                    if tag is None:
                        new_labels.append(label)
                    elif not operators[OPERATOR_STR](tag.value, class_to_threshold[class_name]):
                        new_labels.append(label)
                else:
                    new_labels.append(label)
            new_anns.append(ann.clone(labels=new_labels))

        new_image_infos = api.image.upload_ids(new_dataset.id, image_names, image_ids)
        new_image_ids = [img_info.id for img_info in new_image_infos]
        api.annotation.upload_anns(new_image_ids, new_anns)
        progress.iters_done_report(len(batch))

sly.logger.info('PROJECT_CREATED', extra={'event_type': sly.EventType.PROJECT_CREATED, 'project_id': dst_project.id})