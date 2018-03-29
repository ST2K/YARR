import os
import numpy as np
import tensorflow as tf
import config_utils as config
import data_utils as data_utils

from nets import STVNet

slim = tf.contrib.slim
os.environ["CUDA_VISIBLE_DEVICES"] = "3" # config.FLAGS.gpu_list


def turn_into_bbox(x1, x2, x3, x4, y1, y2, y3, y4, num):
    bboxes = []
    for i in range(num):
        x = [x1[i], x2[i], x3[i], x4[i]]
        y = [y1[i], y2[i], y3[i], y4[i]]
        xmin = min(x) / 300.0
        xmax = max(x) / 300.0
        ymin = min(y) / 300.0
        ymax = max(y) / 300.0

        if xmin < 0:
            xmin = 0
        if ymin < 0:
            ymin = 0

        bbox = [ymin, xmin, ymax, xmax]
        bboxes.append(bbox)

    return bboxes


def generate_batch_bboxes(b_x1, b_x2, b_x3, b_x4, b_y1, b_y2, b_y3, b_y4, b_bbox_num):
    batch_bboxes = []
    for i in range(len(b_bbox_num)):
        bboxes = turn_into_bbox(b_x1[i], b_x2[i], b_x3[i], b_x4[i], b_y1[i], b_y2[i], b_y3[i], b_y4[i], b_bbox_num[i][0])
        batch_bboxes.append(bboxes)
    # print(bboxes)

    return batch_bboxes



def main():

    image, x1_r, x2_r, x3_r, x4_r, y1_r, y2_r, y3_r, y4_r, bbox_num = data_utils.read_and_decode()
    
    inputs = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='inputs')
    predictions, localisations, logits, end_points = STVNet.model(inputs)

    anchors = STVNet.ssd_anchors_all_layers()
    label = tf.placeholder(tf.int64, shape=[None], name='labels')
    bboxes = tf.placeholder(tf.float32, shape=[None, 4], name='bboxes')
    gc, gl, gs = STVNet.tf_ssd_bboxes_encode(label, bboxes, anchors)

    loss = STVNet.ssd_losses(logits, localisations, gc, gl, gs)

    optimizer = tf.train.GradientDescentOptimizer(config.FLAGS.learning_rate)
    global_step = tf.Variable(0, name='global_step', trainable=False)

    train_op = optimizer.minimize(loss, global_step=global_step)
    tf.summary.scalar("loss", loss)
    merged = tf.summary.merge_all()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)

        summary_writer = tf.summary.FileWriter('/home/hcxiao/STVLogs', sess.graph)

        b_image, b_x1, b_x2, b_x3, b_x4, b_y1, b_y2, b_y3, b_y4, b_bbox_num = \
            sess.run([image, x1_r, x2_r, x3_r, x4_r, y1_r, y2_r, y3_r, y4_r, bbox_num])

        b_bboxes = generate_batch_bboxes(b_x1, b_x2, b_x3, b_x4, b_y1, b_y2, b_y3, b_y4, b_bbox_num)

        for i in range(10):
            # pres, locs, f_score, f_geo = sess.run([predictions, localisations, logits, end_points], feed_dict={inputs: [b_image[i]]})
            
            # gclasses, glocal, gscores = sess.run([gc, gl, gs], feed_dict={label: labels, bboxes: b_bboxes[i]})
            # loss = STVNet.ssd_losses(f_score, locs, gclasses, glocal, gscores)

            # loc_loss = sess.run(loss, feed_dict={inputs: [b_image[i]], label: labels, bboxes: b_bboxes[i]})

            labels = [1 for i in range(b_bbox_num[i][0])]
            _, loc_loss, summary_str = sess.run([train_op, loss, merged], feed_dict={inputs: [b_image[i]], label: labels, bboxes: b_bboxes[i]})
            print('step: ', i, ', loss: ', loc_loss)

            # summary_str = sess.run(merged, feed_dict={loss:loc_loss})
            summary_writer.add_summary(summary_str, i)
            summary_writer.flush()

        coord.request_stop()
        coord.join(threads)


if __name__ == '__main__':
    main()
