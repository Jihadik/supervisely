# coding: utf-8

import tensorflow as tf
from deeplab.common import ModelOptions
import deeplab.model as model_lib

slim = tf.contrib.slim


def construct_model(model_dir, input_size, train_config, out_class_mapping):
    with tf.get_default_graph().as_default():
        inputs = tf.placeholder(tf.float32, shape=((None,) + input_size + (3,)))

        model_options = ModelOptions(
            outputs_to_num_classes={'semantic': max(out_class_mapping.keys()) + 1},
            crop_size=input_size,
            atrous_rates=train_config['atrous_rates'],
            output_stride=train_config['output_stride'])

        outputs_to_scales_to_logits = model_lib.multi_scale_logits(
            images=inputs,
            model_options=model_options,
            image_pyramid=None,
            weight_decay=train_config['weight_decay'],
            is_training=False,
            fine_tune_batch_norm=False
        )

        logits = outputs_to_scales_to_logits['semantic']['merged_logits']
        logits = tf.image.resize_bilinear(
            logits,
            input_size,
            align_corners=True)
        probabilities = tf.nn.softmax(logits)

        saver = tf.train.Saver(slim.get_variables_to_restore())
        session = tf.train.MonitoredTrainingSession(master='')
        saver.restore(session, model_dir + '/model_weights/model.ckpt')
    return session, inputs, probabilities
