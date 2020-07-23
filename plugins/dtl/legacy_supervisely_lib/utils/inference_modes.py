# coding: utf-8

from copy import deepcopy

import numpy as np

from legacy_supervisely_lib.figure.fig_classes import FigClasses
from legacy_supervisely_lib.figure.rectangle import Rect
from legacy_supervisely_lib.figure.figure_rectangle import FigureRectangle
from legacy_supervisely_lib.figure.sliding_windows import SlidingWindows
from legacy_supervisely_lib.figure.helper import crop_image_with_rect
from legacy_supervisely_lib.utils.config_readers import rect_from_bounds
from legacy_supervisely_lib.utils.nn_data import prediction_to_sly_bitmaps


EXISTING_OBJECTS = 'existing_objects'
# TODO "classes" here for backwards compatibility, consider unifying.
MODEL_OBJECTS = 'model_classes'


MODE = 'mode'
SOURCE = 'source'


MATCH_ALL = '__all__'


def is_object_title_included(title, enabled_titles):
    return (enabled_titles == MATCH_ALL) or (title in enabled_titles)


class Renamer:
    ADD_SUFFIX = 'add_suffix'
    SAVE_CLASSES = 'save_classes'

    def __init__(self, add_suffix='', enabled_classes=None):
        self._add_suffix = add_suffix
        self._enabled_classes = enabled_classes or MATCH_ALL

    def rename(self, name):
        return (name + self._add_suffix) if is_object_title_included(name, self._enabled_classes) else None

    def to_json(self):
        return {Renamer.ADD_SUFFIX: self._add_suffix, Renamer.SAVE_CLASSES: self._enabled_classes}

    @staticmethod
    def from_json(renamer_json):
        return Renamer(add_suffix=renamer_json[Renamer.ADD_SUFFIX], enabled_classes=renamer_json[Renamer.SAVE_CLASSES])


def get_renamed_classes(renamer, input_classes, shape_override=None):
    renamed_classes = FigClasses()
    for src_cls in input_classes:
        src_title = src_cls['title']
        renamed_title = renamer.rename(src_title)
        if renamed_title is not None:
            renamed_class = deepcopy(src_cls)
            renamed_class['title'] = renamed_title
            renamed_class['shape'] = shape_override or renamed_class['shape']
            renamed_classes.add(renamed_class)
    return renamed_classes


def rename_and_filter_figures(renamer, figures):
    """Renames figures (whenever renamer accepts the name) in-place. Returns only successfully renamed figures."""
    renamed_figures = []
    for figure in figures:
        renamed_title = renamer.rename(figure.class_title)
        if renamed_title is not None:
            figure.class_title = renamed_title
            renamed_figures.append(figure)
    return renamed_figures


def make_intermediate_bbox_class(class_title):
    return None if class_title is None else {'title': class_title, 'shape': 'rectangle'}


class InferenceFeederBase:
    def __init__(self, in_meta):
        self._out_meta = deepcopy(in_meta)

    def _add_out_class_or_die(self, out_class):
        if out_class['title'] in self._out_meta.classes:
            raise RuntimeError('Unable to determine output classes due to non-unique result class names.')
        else:
            self._out_meta.add(out_class)

    def _update_out_meta(self, renamer, in_classes, shape_override=None):
        for out_class in get_renamed_classes(renamer, in_classes, shape_override):
            self._add_out_class_or_die(out_class)

    @property
    def out_meta(self):
        return self._out_meta


def get_objects_for_bbox(img, roi, inference_callback, renamer):
    """Runs inference within the given roi; renames the resulting figures and moves to global reference frame."""
    img_cropped = crop_image_with_rect(img, roi)
    inference_result = inference_callback(img_cropped, None)
    for fig in inference_result.figures:
        fig.shift((roi.left, roi.top))
    return rename_and_filter_figures(renamer, inference_result.figures)


class InferenceFeederWithModelOutClasses(InferenceFeederBase):
    """Common base for all feeders working with spatial figures. Supports separate renaming settings for existing
        objects in the annotation and new objects introduced by the model."""

    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(in_meta)
        self._renamer_existing = Renamer.from_json(settings[EXISTING_OBJECTS])
        self._update_out_meta(self._renamer_existing, in_meta.classes)
        self._renamer_model = Renamer.from_json(settings[MODEL_OBJECTS])
        self._update_out_meta(self._renamer_model, model_out_classes)

    def _init_feed(self, ann):
        """Initializes all the containers to accumulate objects from possible respective sources."""
        src_objects = rename_and_filter_figures(self._renamer_existing, ann['objects'])
        model_objects = []
        interm_objects = []
        img_wh = ann.image_size_wh
        return src_objects, model_objects, interm_objects, img_wh


class InfFeederFullImage(InferenceFeederWithModelOutClasses):
    @staticmethod
    def make_default_settings(model_result_suffix):
        return {
            MODEL_OBJECTS: Renamer(add_suffix=model_result_suffix, enabled_classes=MATCH_ALL).to_json(),
            EXISTING_OBJECTS: Renamer(add_suffix='', enabled_classes=[]).to_json(),
            MODE: {
                SOURCE: 'full_image'
            },
        }

    def feed(self, img, ann, inference_cback):
        inference_result = inference_cback(img, ann)
        src_objects = rename_and_filter_figures(self._renamer_existing, ann['objects'])
        found_objects = rename_and_filter_figures(self._renamer_model, inference_result.figures)
        ann['objects'] = src_objects + found_objects
        return ann


class InfFeederRoi(InferenceFeederWithModelOutClasses):
    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(settings, in_meta, model_out_classes)
        self._mode_conf = settings[MODE]
        self._intermediate_bbox_class = make_intermediate_bbox_class(self._mode_conf.get('intermediate_class', None))
        if self._intermediate_bbox_class is not None:
            self._add_out_class_or_die(self._intermediate_bbox_class)

    def feed(self, img, ann, inference_cback):
        src_objects, model_objects, interm_objects, img_wh = self._init_feed(ann)

        roi = rect_from_bounds(self._mode_conf['bounds'], *img_wh)
        rect_img = Rect.from_size(img_wh)
        if roi.is_empty or (not rect_img.contains(roi)):
            raise RuntimeError('Mode "roi": result crop bounds are invalid.')
        model_objects = get_objects_for_bbox(img, roi, inference_cback, self._renamer_model)

        if self._intermediate_bbox_class is not None:
            interm_objects.extend(FigureRectangle.from_rect(self._intermediate_bbox_class['title'], img_wh, roi))

        ann['objects'] = src_objects + interm_objects + model_objects
        return ann


def all_filtered_bbox_rois(ann, included_classes, padding_settings, img_wh):
    for src_obj in ann['objects']:
        if is_object_title_included(src_obj.class_title, included_classes):
            bbox = src_obj.get_bbox().round()
            roi = rect_from_bounds(padding_settings, img_w=bbox.width, img_h=bbox.height, shift_inside=False)
            roi = roi.move((bbox.left, bbox.top)).intersection(Rect.from_size(img_wh))
            if not roi.is_empty:
                yield src_obj, roi


class InfFeederBboxes(InferenceFeederWithModelOutClasses):
    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(settings, in_meta, model_out_classes)
        self._mode_conf = settings[MODE]

        self._renamer_intermediate = None
        if self._mode_conf['save']:
            self._renamer_intermediate = Renamer(add_suffix=self._mode_conf.get('intermediate_add_suffix', ''),
                    enabled_classes=self._mode_conf['from_classes', ''])
            self._update_out_meta(self._renamer_intermediate, in_meta.classes, shape_override='rectangle')

    def feed(self, img, ann, inference_cback):
        src_objects, model_objects, interm_objects, img_wh = self._init_feed(ann)
        for src_obj, roi in all_filtered_bbox_rois(ann, self._mode_conf['from_classes'], self._mode_conf['padding'],
                                                   img_wh):
            model_objects.extend(get_objects_for_bbox(img, roi, inference_cback, self._renamer_model))

            if self._renamer_intermediate is not None:
                intermediate_figure = FigureRectangle.from_rect(src_obj.class_title, img_wh, roi)
                interm_objects.extend(rename_and_filter_figures(self._renamer_intermediate, [intermediate_figure]))

        ann['objects'] = src_objects + interm_objects + model_objects
        return ann


class InfFeederSidinglWindowBase(InferenceFeederWithModelOutClasses):
    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(settings, in_meta, model_out_classes)
        self._num_model_out_classes = len(model_out_classes)
        self._mode_conf = settings[MODE]

        window_config = self._mode_conf['window']
        window_wh = (window_config['width'], window_config['height'])
        min_overlap_config = self._mode_conf['min_overlap']
        min_overlap_xy = (min_overlap_config['x'], min_overlap_config['y'])
        self._sliding_windows = SlidingWindows(window_wh, min_overlap_xy)

        self._intermediate_bbox_class = make_intermediate_bbox_class(self._mode_conf.get('intermediate_class', None))
        if self._intermediate_bbox_class is not None:
            self._add_out_class_or_die(self._intermediate_bbox_class)

    def _maybe_make_intermediate_bbox(self, img_wh, roi):
        if self._intermediate_bbox_class is not None:
            return FigureRectangle.from_rect(self._intermediate_bbox_class['title'], img_wh, roi)
        else:
            return []


# for image segmentation only
class InfFeederSlWindow(InfFeederSidinglWindowBase):
    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(settings, in_meta, model_out_classes)

    def feed(self, img, ann, inference_cback):
        src_objects, model_objects, interm_objects, img_wh = self._init_feed(ann)
        summed_probas = np.zeros((img_wh[1], img_wh[0], self._num_model_out_classes), dtype=np.float64)
        cls_mapping = None
        for roi in self._sliding_windows.get(img_wh):
            img_cropped = crop_image_with_rect(img, roi)
            inference_result = inference_cback(img_cropped, None)
            cls_mapping = inference_result.pixelwise_class_probas.class_title_to_idx_out_mapping
            summed_probas[roi.top:roi.bottom, roi.left:roi.right, :] += inference_result.pixelwise_class_probas.probas
            interm_objects.extend(self._maybe_make_intermediate_bbox(img_wh, roi))

        if np.sum(summed_probas, axis=2).min() == 0:
            raise RuntimeError('Wrong sliding window moving, implementation error.')

        model_objects_raw = prediction_to_sly_bitmaps(cls_mapping, np.argmax(summed_probas, axis=2))
        model_objects = rename_and_filter_figures(self._renamer_model, model_objects_raw)
        ann['objects'] = src_objects + interm_objects + model_objects
        return ann


class InfFeederSlWindowDetection(InfFeederSidinglWindowBase):
    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(settings, in_meta, model_out_classes)

    # 'max' NMS
    @classmethod
    def _single_class_nms(cls, figures_rect, iou_thresh):
        incr_score = sorted(figures_rect, key=lambda x: x.data['score'])  # ascending
        out_figs = []
        for curr_fig in incr_score:
            curr_bbox = curr_fig.get_bbox()
            # suppress earlier (with less thresh)
            out_figs = list(filter(lambda x: x.get_bbox().iou(curr_bbox) <= iou_thresh, out_figs))
            out_figs.append(curr_fig)

        return out_figs

    # @TODO: move out
    @classmethod
    def general_nms(cls, figures_rect, iou_thresh):
        if not all(isinstance(x, FigureRectangle) for x in figures_rect):
            raise RuntimeError('NMS expects FigureRectangle.')
        if not all('score' in x.data for x in figures_rect):
            raise RuntimeError('NMS expects "score" field in figures.')

        use_classes = set(x.class_title for x in figures_rect)
        res = []
        for cls_title in sorted(list(use_classes)):
            class_figures = list(filter(lambda x: x.class_title == cls_title, figures_rect))
            res.extend(cls._single_class_nms(class_figures, iou_thresh))
        return res

    def feed(self, img, ann, inference_cback):
        src_objects, model_objects, interm_objects, img_wh = self._init_feed(ann)
        for roi in self._sliding_windows.get(img_wh):
            model_objects.extend(get_objects_for_bbox(img, roi, inference_cback, self._renamer_model))
            interm_objects.extend(self._maybe_make_intermediate_bbox(img_wh, roi))

        nms_conf = self._mode_conf['nms_after']
        if nms_conf['enable']:
            model_objects = self.general_nms(figures_rect=model_objects, iou_thresh=nms_conf['iou_threshold'])

        ann['objects'] = src_objects + interm_objects + model_objects
        return ann


class InfFeederBboxesOCR(InferenceFeederBase):
    def __init__(self, settings, in_meta, model_out_classes):
        super().__init__(in_meta)
        self._mode_conf = settings[MODE]
        self._renamer_existing = Renamer.from_json(settings[EXISTING_OBJECTS])
        self._update_out_meta(self._renamer_existing, in_meta.classes)

    def feed(self, img, ann, inference_cback):
        img_wh = ann.image_size_wh
        src_titles = self._mode_conf['from_classes']
        for src_obj, roi in all_filtered_bbox_rois(ann, src_titles, self._mode_conf['padding'], img_wh):
            img_cropped = crop_image_with_rect(img, roi)
            _ = inference_cback(img_cropped, src_obj.data)  # no need to crop & pass figures now

        ann['objects'] = rename_and_filter_figures(self._renamer_existing, ann['objects'])
        return ann


class InferenceFeederFactory:
    mapping = {
        'full_image': InfFeederFullImage,
        'roi': InfFeederRoi,
        'bboxes': InfFeederBboxes,
        'sliding_window': InfFeederSlWindow,
        'sliding_window_det': InfFeederSlWindowDetection,
        'bboxes_ocr': InfFeederBboxesOCR
    }

    @classmethod
    def create(cls, settings, *args, **kwargs):
        key = settings[MODE][SOURCE]
        feeder_cls = cls.mapping.get(key)
        if feeder_cls is None:
            raise NotImplementedError()
        res = feeder_cls(settings, *args, **kwargs)
        return res
