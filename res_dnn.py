import tensorflow as tf
import numpy as np
INPUT_NODE = 784
OUTPUT_NODE = 10

IMAGE_SIZE = 28
NUM_CHANNELS = 1
NUM_LABELS = 10

CONV1_DEEP = 16
CONV1_SIZE = 3

CONV2_DEEP = 32
CONV2_SIZE = 3

FC_SIZE = 512

def inference(input_tensor, train, regularizer,train_label):
	with tf.variable_scope('layer1-conv1'):
		conv1_weights = tf.get_variable(
			"weight", [CONV1_SIZE, CONV1_SIZE, NUM_CHANNELS, CONV1_DEEP],
			initializer=tf.truncated_normal_initializer(stddev=0.1))
		conv1_biases = tf.get_variable("bias", [CONV1_DEEP], initializer=tf.constant_initializer(0.0))
		conv1 = tf.nn.conv2d(input_tensor, conv1_weights, strides=[1, 1, 1, 1], padding='SAME')
             #   conv1=tf.layers.batch_normalization(conv1, is_training)
		relu1 = tf.nn.relu(tf.nn.bias_add(conv1, conv1_biases))

	with tf.name_scope("layer2-pool1"):
		pool1 = tf.nn.max_pool(relu1, ksize = [1,2,2,1],strides=[1,2,2,1],padding="SAME")
		
	with tf.variable_scope('res-conv1'):
                res1_weights = tf.get_variable(
                        "weight", [3,3,16,16],
                        initializer=tf.truncated_normal_initializer(stddev=0.1))
                res1_biases = tf.get_variable("bias", [16], initializer=tf.constant_initializer(0.0))
                res_conv1 = tf.nn.conv2d(pool1,res1_weights, strides=[1, 1, 1, 1], padding='SAME')
                res_relu1 = tf.nn.relu(tf.nn.bias_add(res_conv1,res1_biases))

	with tf.variable_scope('res-conv2'):
                res2_weights = tf.get_variable(
                        "weight", [3,3,16,16],
                        initializer=tf.truncated_normal_initializer(stddev=0.1))
                res2_biases = tf.get_variable("bias", [16], initializer=tf.constant_initializer(0.0))
                res_conv2 = tf.nn.conv2d(res_relu1,res2_weights, strides=[1, 1, 1, 1], padding='SAME')
                res_relu2 = tf.nn.relu(tf.nn.bias_add(res_conv2,res2_biases)+pool1)

	with tf.variable_scope("layer3-conv2"):
		conv2_weights = tf.get_variable(
			"weight", [CONV2_SIZE, CONV2_SIZE, CONV1_DEEP, CONV2_DEEP],
			initializer=tf.truncated_normal_initializer(stddev=0.1))
		conv2_biases = tf.get_variable("bias", [CONV2_DEEP], initializer=tf.constant_initializer(0.0))
		conv2 = tf.nn.conv2d(res_relu2, conv2_weights, strides=[1, 1, 1, 1], padding='SAME')
		relu2 = tf.nn.relu(tf.nn.bias_add(conv2, conv2_biases))

	with tf.name_scope("layer4-pool2"):
		pool2 = tf.nn.max_pool(relu2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		pool_shape = pool2.get_shape()
		nodes = pool_shape[1] * pool_shape[2] * pool_shape[3]
		reshaped = tf.reshape(pool2, [-1, nodes])

	with tf.variable_scope('layer5-fc1'):
		fc1_weights = tf.get_variable("weight", [nodes, FC_SIZE],
									  initializer=tf.truncated_normal_initializer(stddev=0.1))
		if regularizer != None: tf.add_to_collection('losses', regularizer(fc1_weights))
		fc1_biases = tf.get_variable("bias", [FC_SIZE], initializer=tf.constant_initializer(0.1))

		fc1 = tf.nn.relu(tf.matmul(reshaped, fc1_weights) + fc1_biases)
		if train: fc1 = tf.nn.dropout(fc1, 0.7)

	with tf.variable_scope('layer6-fc2'):
		fc2_weights = tf.get_variable("weight", [FC_SIZE, NUM_LABELS],
									  initializer=tf.truncated_normal_initializer(stddev=0.1))
		if regularizer != None: tf.add_to_collection('losses', regularizer(fc2_weights))

		x=fc1
		w=fc2_weights
		normed_weights = tf.nn.l2_normalize(w, 0, 1e-10, name='weights_norm')
		normed_features = tf.nn.l2_normalize(x, 1, 1e-10, name='features_norm')
		cosine = tf.matmul(normed_features, normed_weights)
		cosine = tf.clip_by_value(cosine, -1, 1, name='cosine_clip') - 0.35* tf.one_hot(train_label,10, on_value=1., off_value=0., axis=-1, dtype=tf.float32)
		return cosine,tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=train_label,logits=30* cosine))		
