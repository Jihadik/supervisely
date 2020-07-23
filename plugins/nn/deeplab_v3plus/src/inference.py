# coding: utf-8

import os
import cv2
import numpy as np

import supervisely_lib as sly
from supervisely_lib.nn.hosted.constants import SETTINGS
from supervisely_lib.nn.hosted.inference_single_image import SingleImageInferenceBase, GPU_DEVICE
from supervisely_lib.nn.hosted.inference_batch import BatchInferenceApplier
from supervisely_lib.nn import raw_to_labels
from supervisely_lib.nn.hosted.inference_modes import InfModeFullImage
from supervisely_lib.nn.config import JsonConfigValidator
from common_inference import construct_model
import config as config_lib


class DeeplabSingleImageApplier(SingleImageInferenceBase):

    @staticmethod
    def get_default_config():
        return {
            GPU_DEVICE: 0,
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
        JsonConfigValidator().validate_inference_cfg(config)

    def _construct_and_fill_model(self):
        super()._construct_and_fill_model()
        self.device_ids = sly.env.remap_gpu_devices([self._config[GPU_DEVICE]])

        self.session, self.inputs, self.probabilities = construct_model(
            sly.TaskPaths.MODEL_DIR,
            self.input_size,
            self.train_config[SETTINGS],
            self.out_class_mapping
        )
        sly.logger.info('Weights are loaded.')

    def inference(self, img, ann):
        h, w = img.shape[:2]
        # Resize to requested model input size
        input_image = sly.image.resize(img, self.input_size)
        input_image_var = np.expand_dims(input_image.astype(np.float32), 0)
        raw_pixelwise_probas_array = self.session.run(self.probabilities, feed_dict={self.inputs: input_image_var})
        # Resize back to the original
        pixelwise_probas_array = cv2.resize(np.squeeze(raw_pixelwise_probas_array[0]), (w, h), cv2.INTER_LINEAR)

        labels = raw_to_labels.segmentation_array_to_sly_bitmaps(self.out_class_mapping,
                                                                 np.argmax(pixelwise_probas_array, axis=2))

        pixelwise_scores_labels = raw_to_labels.segmentation_scores_to_per_class_labels(self.out_class_mapping,
                                                                                        pixelwise_probas_array)
        return sly.Annotation(ann.img_size, labels=labels, pixelwise_scores_labels=pixelwise_scores_labels)


def main():
    single_image_applier = DeeplabSingleImageApplier()
    default_inference_mode_config = InfModeFullImage.make_default_config(model_result_suffix='_deeplab')
    dataset_applier = BatchInferenceApplier(single_image_inference=single_image_applier,
                                            default_inference_mode_config=default_inference_mode_config,
                                            config_validator=JsonConfigValidator())
    dataset_applier.run_inference()


if __name__ == '__main__':
    if os.getenv('DEBUG_LOG_TO_FILE', None):
        sly.add_default_logging_into_file(sly.logger, sly.TaskPaths.DEBUG_DIR)
    sly.main_wrapper('DEEPLAB_INFERENCE', main)
