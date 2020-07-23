# coding: utf-8

import os

import cv2

import numpy as np
import supervisely_lib as sly
from supervisely_lib import sly_logger
from supervisely_lib.annotation.annotation import Annotation
from supervisely_lib.sly_logger import logger
from supervisely_lib.task.paths import TaskPaths
from supervisely_lib.nn.hosted.inference_single_image import SingleImageInferenceBase, GPU_DEVICE
from supervisely_lib.nn.hosted.inference_batch import BatchInferenceApplier
from supervisely_lib.nn.hosted.inference_modes import InfModeFullImage
from supervisely_lib.nn import raw_to_labels
from supervisely_lib.nn.pytorch import inference as pytorch_inference

from common import create_model_for_inference, UnetJsonConfigValidator
from dataset import input_image_normalizer
import config as config_lib


class UnetV2SingleImageApplier(SingleImageInferenceBase):

    @staticmethod
    def get_default_config():
        return {
            GPU_DEVICE: 0
        }

    @property
    def train_classes_key(self):
        return config_lib.train_classes_key()

    @property
    def class_title_to_idx_key(self):
        return config_lib.class_to_idx_config_key()

    def _load_train_config(self):
        super()._load_train_config()
        self._determine_model_input_size()

    def _validate_model_config(self, config):
        UnetJsonConfigValidator().validate_inference_cfg(config)

    def _construct_and_fill_model(self):
        super()._construct_and_fill_model()

        self.device_ids = sly.env.remap_gpu_devices([self._config[GPU_DEVICE]])
        n_cls = (max(self.out_class_mapping.keys()) + 1)
        self.model = create_model_for_inference(n_cls=n_cls,
                                                device_ids=self.device_ids,
                                                model_dir=TaskPaths.MODEL_DIR)
        logger.info('Weights are loaded.')


    """ how to use probabilities (example)
        # let's consider pixel at position (5, 7). Number of classes == 3
        
        pixel_row = 5
        pixel_col = 7
        classes_count = 3
        probas = []
        for class_index in range(classes_count):
            probas.append(pixelwise_scores_labels[class_index].geometry._data[pixel_row, pixel_col])

        sum(probas)
        >>> array([1.], dtype=float32)
    """

    def inference(self, img, ann):
        resized_img = cv2.resize(img, self.input_size[::-1])
        model_input = input_image_normalizer(resized_img)
        # sum(pixelwise_probas_array[0, 0, :]) == 1
        pixelwise_probas_array = pytorch_inference.infer_per_pixel_scores_single_image(
            self.model, model_input, img.shape[:2])
        labels = raw_to_labels.segmentation_array_to_sly_bitmaps(
            self.out_class_mapping, np.argmax(pixelwise_probas_array, axis=2))
        pixelwise_scores_labels = raw_to_labels.segmentation_scores_to_per_class_labels(
            self.out_class_mapping, pixelwise_probas_array)
        return Annotation(ann.img_size, labels=labels, pixelwise_scores_labels=pixelwise_scores_labels)


def main():
    single_image_applier = UnetV2SingleImageApplier()
    default_inference_mode_config = InfModeFullImage.make_default_config(model_result_suffix='_unet')
    dataset_applier = BatchInferenceApplier(single_image_inference=single_image_applier,
                                            default_inference_mode_config=default_inference_mode_config,
                                            config_validator=UnetJsonConfigValidator())
    dataset_applier.run_inference()


if __name__ == '__main__':
    if os.getenv('DEBUG_LOG_TO_FILE', None):
        sly_logger.add_default_logging_into_file(logger, TaskPaths.DEBUG_DIR)
    sly.main_wrapper('UNET_V2_INFERENCE', main)
