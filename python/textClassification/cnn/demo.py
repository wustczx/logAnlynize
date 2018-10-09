import tensorflow as tf
import numpy as np
import os
import data_helpers
from text_cnn import TextCNN
from tensorflow.contrib import learn

tf.flags.DEFINE_string("positive_data_file","","Positive Data Source")
tf.flags.DEFINE_string("negative_data_file","","Negative Data Source")

tf.flags.DEFINE_integer("embedding_dim", 128, "Dimensionality of character embedding (default: 128)")
tf.flags.DEFINE_string("filter_sizes", "3,4,5", "Comma-separated filter sizes (default: '3,4,5')")
tf.flags.DEFINE_integer("num_filters", 128, "Number of filters per filter size (default: 128)")
tf.flags.DEFINE_float("dropout_keep_prob", 0.5, "Dropout keep probability (default: 0.5)")
tf.flags.DEFINE_float("l2_reg_lambda", 0.0, "L2 regularization lambda (default: 0.0)")

tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_integer("num_epochs", 200, "Number of training epochs (default: 200)")
tf.flags.DEFINE_integer("evaluate_every", 100, "Evaluate model on dev set after this many steps (default: 100)")
tf.flags.DEFINE_integer("checkpoint_every", 100, "Save model after this many steps (default: 100)")
tf.flags.DEFINE_integer("num_checkpoints", 5, "Number of checkpoints to store (default: 5)")

tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")
tf.flags.DEFINE_string("summary_dir","/tmp/wust","summary dir path")

FLAGS = tf.flags.FLAGS
FLAGS.flag_values_dict()

print("Loading Data...")
negative_xtexts = data_helpers.load_data("../../../data/sample_train.log")
positive_xtexts = data_helpers.load_data("../../../data/sender_train.log")
positive_ylabels = data_helpers.load_labels(positive_xtexts.shape[0], 2,[0,1])
negative_ylabels = data_helpers.load_labels(negative_xtexts.shape[0], 2,[1,0])

print("pos:",positive_xtexts.shape)
print("neg:",negative_xtexts.shape)
xtexts = np.vstack((positive_xtexts, negative_xtexts))
ylabels = np.vstatck((positive_ylabels, negative_ylabels))




