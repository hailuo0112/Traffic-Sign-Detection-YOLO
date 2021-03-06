import tensorflow as tf
from data_reader import *
import numpy as np
from uncompress import *
import os
import tensorflow.contrib.layers as lays
import cPickle


def log(message,file_path=os.path.join('ae_logs_2','ae_log.txt')):

    print message
    f1=open(file_path, 'a+')
    f1.write(message)
    f1.close()

def autoencoder(inputs):
    # encoder
    # 50 x 86796 x 1  ->  50 x 10850 x 32
    # 50 x 10850 x 32  ->  50 x 5825 x 16
    # 50 x 5825 x 16    ->  50 x 1357 x 8
    encoder_1 = lays.conv2d(inputs, 32, [5, 5], stride=(1,8), padding='SAME')
    encoder_2 = lays.conv2d(encoder_1, 16, [5, 5], stride=(1,2), padding='SAME')
    compressed = lays.conv2d(encoder_2, 8, [5, 5], stride=(1,4), padding='SAME')
    # decoder
    # 50 x 1357 x 8    ->  50 x 5825 x 16 
    # 50 x 5825 x 16   ->  50 x 10850 x 32
    # 50 x 10850 x 32  ->   50 x 86796 x 1
    decoder_1 = lays.conv2d_transpose(compressed, 16, [5, 5], stride=(1,4), padding='SAME')
    decoder_2 = lays.conv2d_transpose(decoder_1, 32, [5, 5], stride=(1,2), padding='SAME')
    decoder_3 = lays.conv2d_transpose(decoder_2, 1, [5, 5], stride=(1,8), padding='SAME', activation_fn=tf.nn.tanh)
    return decoder_3[:,:,0:inputs.get_shape().as_list()[2],:],compressed,encoder_1,encoder_2,decoder_1,decoder_2


def compress(input,x=None,return_x=False):
    
    input_size = 50
    learning_rate = 0.00001
    X = tf.placeholder(tf.float32, [None, input_size,86796,1])

    reconstruction, compressed, encoder_1, encoder_2, decoder_1, decoder_2 = autoencoder(X)
    
    # print encoder_1.get_shape,encoder_2.get_shape
    # exit(0)

    loss_op = tf.reduce_mean(tf.square(reconstruction - X))

    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op)


    if(return_x):
	
    	saver = tf.train.Saver()
    	x = saver._var_list
        print x
    	return x
    #print type(x)
    saver = tf.train.Saver(var_list=x)
	
    # saver = tf.train.Saver(var_list=x)
    with tf.Session() as sess1:

        # Run the initializer
        # sess1.run(init)
        
        # print 'restoring ae session'
        # saver.restore(sess1, "ae_logs_1/save.ckpt")
        # print 'done loading'
        # exit(0)
        # init_new_vars_op = tf.variables_initializer([reconstruction, compressed])
        init_new_op = tf.variables_initializer([v for v in tf.global_variables() if v.name.split(':')[0] in set(sess1.run(tf.report_uninitialized_variables()))])
    
        sess1.run(init_new_op)

        batch_x = uncompress(input,86796)
        # Run optimization op (backprop)
        [_,data_point] = sess1.run([reconstruction, compressed], feed_dict={X: batch_x})
        
        # print np.stack(ae_output).shape
    return data_point

def print_intermediate():

    learning_rate = 0.00001
    # np.set_printoptions(threshold=np.nan)
    num_epoch = 1
    batch_size = 1
    display_step = 1
    input_size = 50
   
    X = tf.placeholder(tf.float32, [None, input_size,86796,1])

    reconstruction, compressed, encoder_1, encoder_2, decoder_1, decoder_2 = autoencoder(X)

    loss_op = tf.reduce_mean(tf.square(reconstruction - X))

    tf.summary.scalar('loss',loss_op)
    # optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    # train_op = optimizer.minimize(loss_op)

    init = tf.global_variables_initializer()

    data_X,_ = load_data()
    
    indices = np.random.permutation(np.arange(data_X.shape[0]))

    data_X = data_X[indices,:,:]

    tf.contrib.layers.summarize_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
    merged = tf.summary.merge_all()
    saver = tf.train.Saver()

    with tf.Session() as sess:

        train_writer = tf.summary.FileWriter("ae_logs_2/",
                                    sess.graph)

        # Run the initializer
        sess.run(init)
        i = 0
        print 'started training'
        for epoch in range(num_epoch):
            for step in range(data_X.shape[0]/batch_size):
                batch_x = data_X[step*batch_size:(step+1)*batch_size]

                i+=1

                batch_x = uncompress(batch_x,86796)


                print 'restoring ae session'
                saver.restore(sess, "ae_logs_1/save.ckpt")
                print 'done loading'

                init_new_op = tf.variables_initializer([v for v in tf.global_variables() if v.name.split(':')[0] in set(sess.run(tf.report_uninitialized_variables()))])
    
                sess.run(init_new_op)


                
                print 'input - '
                print 'input shape - ', batch_x.shape
                print batch_x


                stage1,stage2,stage3 = sess.run([encoder_1, encoder_2,compressed],feed_dict={X: batch_x})

                print '******stage 1******'
                print '******stage 1 shape', stage1.shape
                print stage1

                print '******stage 2******'
                print '******stage 2 shape', stage2.shape
                print stage2

                print '******stage 3******'
                print '******stage 3 shape', stage3.shape
                print stage3

                exit(0)




               	
        print 'done!'
        

if __name__=='__main__':

    # os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    #compress()
    # x = compress(None,None,True)
    # print x
    # batch_x = np.identity((2,50,50))
    # batch_x = compress(batch_x,x)
    # exit(0)

    print_intermediate()
    exit(0)

    learning_rate = 0.00001

    num_epoch = 1
    batch_size = 1
    display_step = 1
    input_size = 50
   
    X = tf.placeholder(tf.float32, [None, input_size,86796,1])

    reconstruction, compressed, encoder_1, encoder_2, decoder_1, decoder_2 = autoencoder(X)

    loss_op = tf.reduce_mean(tf.square(reconstruction - X))

    tf.summary.scalar('loss',loss_op)
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op)

    init = tf.global_variables_initializer()

    data_X,_ = load_data()
    
    indices = np.random.permutation(np.arange(data_X.shape[0]))

    data_X = data_X[indices,:,:]

    tf.contrib.layers.summarize_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
    merged = tf.summary.merge_all()
    saver = tf.train.Saver()

    with tf.Session() as sess:

        train_writer = tf.summary.FileWriter("ae_logs_2/",
                                    sess.graph)

        # Run the initializer
        sess.run(init)

        '''

        print 'restoring session'
        saver.restore(sess, "logs3/epoch0i180.ckpt")
        print 'done loading'
        # exit(0) '''

        i = 0
        print 'started training'
        for epoch in range(num_epoch):
            for step in range(data_X.shape[0]/batch_size):
                batch_x = data_X[step*batch_size:(step+1)*batch_size]

                i+=1

                batch_x = uncompress(batch_x,86796)

                # Run optimization op (backprop)
                _,summary = sess.run([train_op,merged], feed_dict={X: batch_x})
                train_writer.add_summary(summary, i)
                if step % display_step == 0:
                    # Calculate batch loss and accuracy
                    loss = sess.run(loss_op, feed_dict={X: batch_x})
                    log("LR : "+str(learning_rate)+" Epoch : " + str(epoch) + " Step " + str(step) + ", Loss= " + \
                        "{:.4f}".format(loss))

                
                if i%20 == 0:

                    print 'saving checkpoint'
                    save_path = saver.save(sess, os.path.join('ae_logs_2','save.ckpt'))
                    print("Model saved in path: %s" % save_path)              

        print 'done!'
        
