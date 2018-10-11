import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN
from tensorflow.contrib import learn
from sklearn.model_selection import train_test_split

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
tf.flags.DEFINE_string("summary_dir","/tmp/czx","summary dir path")

FLAGS = tf.flags.FLAGS
FLAGS.flag_values_dict()

print("Loading Data...")
#negative_xtexts = data_helpers.load_data("../../../data/sample_train.log")
#positive_xtexts = data_helpers.load_data("../../../data/sender_train.log")
positive_xtexts = data_helpers.load("../../../data/sender_test.res")
negative_xtexts = data_helpers.load("../../../data/sample_test.res")
positive_ylabels = data_helpers.load_labels(positive_xtexts.shape[0], 2,[0,1])
negative_ylabels = data_helpers.load_labels(negative_xtexts.shape[0], 2,[1,0])

print("pos:",positive_xtexts.shape)
print("neg:",negative_xtexts.shape)
print(type(positive_xtexts))
#xtexts = np.vstack((positive_xtexts, negative_xtexts))
#ylabels = np.vstatck((positive_ylabels, negative_ylabels))
xtexts = np.concatenate((positive_xtexts,negative_xtexts),axis=0)
ylabels = np.concatenate((positive_ylabels, negative_ylabels),axis=0)


max_sentence_length = max([ len(x.split(" ")) for x in xtexts])
vocab_processor = learn.preprocessing.VocabularyProcessor( max_sentence_length)
x = np.array(list(vocab_processor.fit_transform(xtexts)))

np.random.seed(10)
shuffle_indices = np.random.permutation(np.arange(len(ylabels)))
x_shuffled = x[shuffle_indices]
y_shuffled = ylabels[shuffle_indices]

x_train,x_test,y_train,y_test = train_test_split(x_shuffled,y_shuffled,test_size=0.1,random_state=0)
print("Vocabulary Size: {:d}".format(len(vocab_processor.vocabulary_)))
print("Train/Test Split: {:d}/{:d}".format(len(x_train), len(x_test)))


with tf.Graph().as_default():
    session_conf = tf.ConfigProto(
            allow_soft_placement = FLAGS.allow_soft_placement,
            log_device_placement = FLAGS.log_device_placement)
    sess = tf.Session(config = session_conf)
    with sess.as_default():
        cnn = TextCNN(
                  sequence_length=x_train.shape[1],
            	  num_classes=y_train.shape[1],
            	  vocab_size=len(vocab_processor.vocabulary_),
            	  embedding_size=FLAGS.embedding_dim,
            	  filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
                  num_filters=FLAGS.num_filters,
                  l2_reg_lambda=FLAGS.l2_reg_lambda)

        global_step = tf.Variable(0, name="global_step", trainable=False)
        optimizer = tf.train.AdamOptimizer(1e-3)
        grads_and_vars = optimizer.compute_gradients(cnn.loss)
        train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)
        
        grad_summaries = []
        for g, v in grads_and_vars:
            if g is not None:
                grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name), g)
                sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name), tf.nn.zero_fraction(g))
                grad_summaries.append(grad_hist_summary)
                grad_summaries.append(sparsity_summary)
        grad_summaries_merged = tf.summary.merge(grad_summaries)

        out_dir = os.path.abspath(FLAGS.summary_dir)
        print("Writing to {}\n".format(out_dir))

        loss_summary = tf.summary.scalar("loss", cnn.loss)
        acc_summary = tf.summary.scalar("accuracy", cnn.accuracy)

        # Train Summaries
        train_summary_op = tf.summary.merge([loss_summary, acc_summary, grad_summaries_merged])
        train_summary_dir = os.path.join(out_dir, "summaries", "train")
        train_summary_writer = tf.summary.FileWriter(train_summary_dir, sess.graph)

        # Test summaries
        test_summary_op = tf.summary.merge([loss_summary, acc_summary])
        test_summary_dir = os.path.join(out_dir, "summaries", "test")
        test_summary_writer = tf.summary.FileWriter(test_summary_dir, sess.graph)

        checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
        checkpoint_prefix = os.path.join(checkpoint_dir, "model")
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        saver = tf.train.Saver(tf.global_variables(), max_to_keep=FLAGS.num_checkpoints)

        vocab_processor.save(os.path.join(out_dir, "vocab"))

        sess.run(tf.global_variables_initializer())

        def train_step(x_batch, y_batch):
            """
            A single training step
            """
            feed_dict = { cnn.input_x: x_batch, cnn.input_y: y_batch, cnn.dropout_keep_prob: FLAGS.dropout_keep_prob }
            _, step, summaries, loss, accuracy = sess.run([train_op, global_step, train_summary_op, cnn.loss, cnn.accuracy],feed_dict)
            time_str = datetime.datetime.now().isoformat()
            print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
            train_summary_writer.add_summary(summaries, step)

        def test_step(x_batch, y_batch, writer=None):
            """
            Evaluates model on a test set
            """
            feed_dict = { cnn.input_x: x_batch,cnn.input_y: y_batch,cnn.dropout_keep_prob: 1.0 }
            step, summaries, loss, accuracy = sess.run([global_step, test_summary_op, cnn.loss, cnn.accuracy],feed_dict)
            time_str = datetime.datetime.now().isoformat()
            print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
            if writer:
                writer.add_summary(summaries, step)

        batches = data_helpers.batch_iter(list(zip(x_train, y_train)), FLAGS.batch_size, FLAGS.num_epochs)
        for batch in batches:
            x_batch, y_batch = zip(*batch)
            train_step(x_batch, y_batch)
            current_step = tf.train.global_step(sess, global_step)
            if current_step % FLAGS.evaluate_every == 0:
                print("\nEvaluation:")
                test_step(x_test, y_test, writer=test_summary_writer)
            if current_step % FLAGS.checkpoint_every == 0:
                path = saver.save(sess, checkpoint_prefix, global_step=current_step)
                print("Saved model checkpoint to {}\n".format(path))

