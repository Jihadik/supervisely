# coding: utf-8

import numpy as np

import supervisely_lib as sly


WORKSPACE_ID = int('%%WORKSPACE_ID%%')
SRC_PROJECT_NAME = '%%IN_PROJECT_NAME%%'
DST_PROJECT_NAME = '%%OUT_PROJECT_NAME%%'
BATCH_SIZE = int('%%batch_size:50%%')  # annotations for the batch are stored in memory


api = sly.Api.from_env()

# read source project
src_project = api.project.get_info_by_name(WORKSPACE_ID, SRC_PROJECT_NAME)
src_project_meta_json = api.project.get_meta(src_project.id)
src_project_meta = sly.ProjectMeta.from_json(src_project_meta_json)

# create destination project
dst_project = api.project.create(WORKSPACE_ID, DST_PROJECT_NAME, change_name_if_conflict=True)
sly.logger.info('Destination project created.', extra={'project_id': dst_project.id, 'project_name': dst_project.name})

# mapping polygons -> bitmaps
new_classes_lst = []
for cls in src_project_meta.obj_classes:
    new_class = cls.clone(geometry_type=sly.Bitmap) if cls.geometry_type == sly.Polygon else cls.clone()
    new_classes_lst.append(new_class)
dst_classes = sly.ObjClassCollection().add_items(new_classes_lst)

# create destination meta
dst_project_meta = src_project_meta.clone(obj_classes=dst_classes)
api.project.update_meta(dst_project.id, dst_project_meta.to_json())


def account_label(lbl: sly.Label) -> bool:
    g_type = lbl.obj_class.geometry_type
    return g_type == sly.Bitmap or g_type == sly.Polygon


def convert_to_nonoverlapping(src_ann: sly.Annotation) -> sly.Annotation:
    common_img = np.zeros(src_ann.img_size, np.uint32)  # size is (h, w)
    for idx, lbl in enumerate(src_ann.labels, start=1):
        if account_label(lbl):
            lbl.draw(common_img, color=idx)

    new_labels = []
    for idx, lbl in enumerate(src_ann.labels, start=1):
        new_cls = dst_project_meta.obj_classes.get(lbl.obj_class.name)
        if not account_label(lbl):
            new_lbl = lbl.clone(obj_class=new_cls)
            new_labels.append(new_lbl)
        else:
            mask = common_img == idx
            if np.any(mask):  # figure may be entirely covered by others
                g = lbl.geometry
                new_bmp = sly.Bitmap(data=mask,
                                     labeler_login=g.labeler_login,
                                     updated_at=g.updated_at,
                                     created_at=g.created_at)
                new_lbl = lbl.clone(geometry=new_bmp, obj_class=new_cls)
                new_labels.append(new_lbl)

    return src_ann.clone(labels=new_labels)


for ds_info in api.dataset.get_list(src_project.id):
    ds_progress = sly.Progress('Processing dataset: {!r}/{!r}'.format(src_project.name, ds_info.name),
                               total_cnt=ds_info.images_count)
    dst_dataset = api.dataset.create(dst_project.id, ds_info.name)
    img_infos_all = api.image.get_list(ds_info.id)

    for img_infos in sly.batched(img_infos_all, batch_size=BATCH_SIZE):
        img_names, img_ids, img_metas = zip(*((x.name, x.id, x.meta) for x in img_infos))

        ann_infos = api.annotation.download_batch(ds_info.id, img_ids)
        anns = [sly.Annotation.from_json(x.annotation, src_project_meta) for x in ann_infos]

        new_anns = [convert_to_nonoverlapping(ann) for ann in anns]

        new_img_infos = api.image.upload_ids(dst_dataset.id, img_names, img_ids, metas=img_metas)
        new_img_ids = [x.id for x in new_img_infos]
        api.annotation.upload_anns(new_img_ids, new_anns)

        ds_progress.iters_done_report(len(img_infos))

sly.logger.info('Finished.')
