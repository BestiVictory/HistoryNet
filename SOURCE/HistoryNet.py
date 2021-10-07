import os
import tensorflow as tf
import config as config
import numpy as np
import cv2
import dataClass as data
import datetime
from functools import partial

import keras
from keras import applications
from keras.callbacks import TensorBoard
from keras.optimizers import Adam
from keras.layers import Input
from keras.layers.merge import _Merge
from keras.layers.advanced_activations import LeakyReLU
from keras import backend as K
from keras.models import load_model, model_from_json, Model

GRADIENT_PENALTY_WEIGHT = 10  

def deprocess(imgs):
    imgs = imgs * 255
    imgs[imgs > 255] = 255
    imgs[imgs < 0] = 0
    return imgs.astype(np.uint8)

def reconstruct(batchX, predictedY, filelist):
    
    result = np.concatenate((batchX, predictedY), axis=2)
    result = cv2.cvtColor(result, cv2.COLOR_Lab2BGR)
    save_results_path = os.path.join(config.OUT_DIR,config.TEST_NAME)
    if not os.path.exists(save_results_path):
        os.makedirs(save_results_path)
    save_path = os.path.join(save_results_path, filelist +  "_reconstructed.jpg" )
    cv2.imwrite(save_path, result)
    return result

def reconstruct_no(batchX, predictedY):
    
    result = np.concatenate((batchX, predictedY), axis=2)
    result = cv2.cvtColor(result, cv2.COLOR_Lab2BGR)
    return result

def write_log(callback, names, logs, batch_no):
    
    for name, value in zip(names, logs):
        summary = tf.Summary()
        summary_value = summary.value.add()
        summary_value.simple_value = value
        summary_value.tag = name
        callback.writer.add_summary(summary, batch_no)
        callback.writer.flush()

def wasserstein_loss(y_true, y_pred):
    return tf.reduce_mean(y_pred)

def gradient_penalty_loss(y_true, y_pred, averaged_samples,
                          gradient_penalty_weight):
    
    gradients = K.gradients(y_pred, averaged_samples)[0]
    gradients_sqr = K.square(gradients)
    gradients_sqr_sum = K.sum(gradients_sqr,
                              axis=np.arange(1, len(gradients_sqr.shape)))
    gradient_l2_norm = K.sqrt(gradients_sqr_sum)
    gradient_penalty = gradient_penalty_weight * K.square(1 - gradient_l2_norm)
    return K.mean(gradient_penalty)
    
class RandomWeightedAverage(_Merge):
   
    def _merge_function(self, inputs):
        weights = K.random_uniform((config.BATCH_SIZE, 1, 1, 1))
        return (weights * inputs[0]) + ((1 - weights) * inputs[1])

class MODEL():

    def __init__(self):
        
        self.img_shape_1 = (config.IMAGE_SIZE, config.IMAGE_SIZE, 1)
        self.img_shape_2 = (config.IMAGE_SIZE, config.IMAGE_SIZE, 2)
        self.img_shape_3 = (config.IMAGE_SIZE, config.IMAGE_SIZE, 3)

        optimizer = Adam(0.00002, 0.5)
        self.discriminator = self.discriminator()
        self.discriminator.compile(loss=[wasserstein_loss],
                                   loss_weights=[1.0],
                                   optimizer=optimizer)

        self.colorizationModel = self.colorization_model()
        self.colorizationModel.compile(loss=['mse', 'kld', 'mse', 'kld'],
                                       loss_weights=[1.0, 1.0, 1.0, 0.0],
                                       optimizer=optimizer)

        self.classcifiModel = self.classcifi()
        self.classcifiModel.compile(loss=['kld'],
                                    loss_weights=[1.0],
                                    optimizer=optimizer)

        img_L_3 = Input(shape= self.img_shape_3)
        img_L = Input(shape= self.img_shape_1)
        img_ab_real = Input(shape= self.img_shape_2)

        self.colorizationModel.trainable = False
        predAB, substracted, preseg, info = self.colorizationModel(img_L_3)
        cinfo = self.classcifiModel(predAB)
        discPredAB = self.discriminator([predAB, img_L])
        discriminator_output_from_real_samples = self.discriminator([img_ab_real, img_L])

        averaged_samples = RandomWeightedAverage()([img_ab_real,
                                            predAB])
        averaged_samples_out = self.discriminator([averaged_samples, img_L])
        partial_gp_loss = partial(gradient_penalty_loss,
                          averaged_samples=averaged_samples,
                          gradient_penalty_weight=GRADIENT_PENALTY_WEIGHT)
        partial_gp_loss.__name__ = 'gradient_penalty'

        self.discriminator_model = Model(inputs=[img_L, img_ab_real, img_L_3],
                            outputs=[discriminator_output_from_real_samples,
                                     discPredAB,
                                     averaged_samples_out])
        self.discriminator_model.compile(optimizer=optimizer,
                            loss=[wasserstein_loss,
                                  wasserstein_loss,
                                  partial_gp_loss], loss_weights=[-1.0, 1.0, 1.0])

        self.classcification_model = Model(inputs=[img_L_3],
                                           outputs=[cinfo])
        self.classcification_model.compile(loss=['kld'],
                                           loss_weights=[1.0],
                                           optimizer=optimizer)

        self.colorizationModel.trainable = True
        self.discriminator.trainable = False
        self.classcifiModel.trainable = False
        self.combined = Model(inputs=[img_L_3, img_L],
                              outputs=[ predAB, substracted, discPredAB, preseg, cinfo, info])
        self.combined.compile(loss=['mse','kld', wasserstein_loss, 'mse', 'kld', 'kld'],
                              loss_weights=[2.0, 0.002, -0.1, 0.002, 0.002, 0.0],
                              optimizer=optimizer) # 1/300

        self.log_path= os.path.join(config.LOG_DIR,config.TEST_NAME)
        self.callback = TensorBoard(self.log_path)
        self.callback.set_model(self.combined)
        self.train_names = ['loss', 'mse_loss', 'kullback_loss', 'wasserstein_loss']
        self.disc_names = ['disc_loss', 'disc_valid', 'disc_fake','disc_gp']

        self.test_loss_array = []
        self.g_loss_array = []

    def discriminator(self):
        
        input_ab = Input(shape=self.img_shape_2, name='ab_input')
        input_l = Input(shape=self.img_shape_1, name='l_input')
        net = keras.layers.concatenate([input_l, input_ab])
        net =  keras.layers.Conv2D(64, (4, 4), padding='same', strides=(2, 2))(net) # 112, 112, 64
        net = LeakyReLU()(net)
        net =  keras.layers.Conv2D(128, (4, 4), padding='same', strides=(2, 2))(net) # 56, 56, 128
        net = LeakyReLU()(net)
        net =  keras.layers.Conv2D(256, (4, 4), padding='same', strides=(2, 2))(net) # 28, 28, 256
        net = LeakyReLU()(net)
        net =  keras.layers.Conv2D(512, (4, 4), padding='same', strides=(1, 1))(net) # 28, 28, 512
        net = LeakyReLU()(net)
        net =  keras.layers.Conv2D(1, (4, 4), padding='same', strides=(1, 1))(net)  # 28, 28,1
        return Model([input_ab, input_l], [net])

    def classcifi(self):
        input_ab = Input(shape=self.img_shape_2, name='ab_input')
        net =  keras.layers.Conv2D(64, (4, 4), padding='same', strides=(2, 2))(input_ab) # 112, 112, 64
        net = LeakyReLU()(net)
        net =  keras.layers.Conv2D(128, (4, 4), padding='same', strides=(2, 2))(net) # 56, 56, 128
        net = LeakyReLU()(net)
        net = keras.layers.BatchNormalization()(net)
        net =  keras.layers.Conv2D(256, (4, 4), padding='same', strides=(2, 2))(net) # 28, 28, 256
        net = LeakyReLU()(net)
        net = keras.layers.BatchNormalization()(net)
        net =  keras.layers.Conv2D(512, (4, 4), padding='same', strides=(2, 2))(net) # 14, 14, 512
        net = LeakyReLU()(net)
        net = keras.layers.BatchNormalization()(net)
        net =  keras.layers.Conv2D(512, (4, 4), padding='same', strides=(2, 2))(net) # 7, 7, 512
        net = LeakyReLU()(net)
        net = keras.layers.BatchNormalization()(net)
        net = keras.layers.Flatten()(net)
        net = keras.layers.Dense(1024)(net)
        net = keras.layers.Dense(256)(net)
        return Model([input_ab], [net])

    def colorization_model(self):
        
        input_img = Input(shape=self.img_shape_3)

        # VGG16 Full
        VGG_modelF = applications.vgg16.VGG16(weights='imagenet', include_top=True) # none, 1000
        for layer in VGG_modelF.layers:
            layer.trainable = False
        model_ = Model(VGG_modelF.input,VGG_modelF.output)
        VGG_modelFull = model_(input_img)

        # VGG16 without top layers
        VGG_model = applications.vgg16.VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        model_ = Model(VGG_model.input,VGG_model.layers[-6].output)
        model = model_(input_img)

        # Global Features
        global_features = keras.layers.Conv2D(512, (3, 3), padding='same', strides=(2, 2), activation='relu')(model)
        global_features = keras.layers.BatchNormalization()(global_features)
        global_features = keras.layers.Conv2D(512, (3, 3), padding='same', strides=(1, 1), activation='relu')(global_features)
        global_features = keras.layers.BatchNormalization()(global_features)

        global_features = keras.layers.Conv2D(512, (3, 3), padding='same', strides=(2, 2), activation='relu')(global_features)
        global_features = keras.layers.BatchNormalization()(global_features)
        global_features = keras.layers.Conv2D(512, (3, 3), padding='same', strides=(1, 1), activation='relu')(global_features)
        global_features = keras.layers.BatchNormalization()(global_features)

        global_features2 = keras.layers.Flatten()(global_features)
        global_features2 = keras.layers.Dense(1024)(global_features2)
        global_features2 = keras.layers.Dense(512)(global_features2)
        global_features2 = keras.layers.Dense(256)(global_features2)
        info_features = global_features2
        global_features2 = keras.layers.RepeatVector(28*28)(global_features2)
        global_features2 = keras.layers.Reshape((28,28, 256))(global_features2)

        global_featuresClass = keras.layers.Flatten()(global_features)
        global_featuresClass = keras.layers.Dense(4096)(global_featuresClass)
        global_featuresClass = keras.layers.Dense(420)(global_featuresClass)
        global_featuresClass = keras.layers.Dense(42, activation='softmax')(global_featuresClass)

        # Segment Features
        segment_features = keras.layers.Conv2D(512, (3, 3), padding='same', strides=(1, 1), activation='relu')(model)
        segment_features = keras.layers.BatchNormalization()(segment_features)
        segment_features = keras.layers.Conv2D(512, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)
        segment_features = keras.layers.BatchNormalization()(segment_features)

        # Midlevel Features
        midlevel_features = keras.layers.Conv2D(512, (3, 3),  padding='same', strides=(1, 1), activation='relu')(model)
        midlevel_features = keras.layers.BatchNormalization()(midlevel_features)
        midlevel_features = keras.layers.Conv2D(256, (3, 3),  padding='same', strides=(1, 1), activation='relu')(midlevel_features)
        midlevel_features = keras.layers.BatchNormalization()(midlevel_features)

        # fusion of (VGG16 + Midlevel) + (VGG16 + Global)
        modelFusion = keras.layers.concatenate([midlevel_features, global_features2]) # 512

        segment_features = keras.layers.Conv2D(256, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)
        segment_features = keras.layers.Conv2D(128, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)

        # Fusion + Colorization
        outputModel =  keras.layers.Conv2D(256, (1, 1), padding='same', strides=(1, 1), activation='relu')(modelFusion)
        outputModel =  keras.layers.Conv2D(128, (3, 3), padding='same', strides=(1, 1), activation='relu')(outputModel)
        outputModel =  keras.layers.concatenate([outputModel, segment_features]) # 256
        outputModel =  keras.layers.Conv2D(128, (3, 3), padding='same', strides=(1, 1), activation='relu')(outputModel)

        segment_features = keras.layers.Conv2D(128, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)
        segment_features =  keras.layers.UpSampling2D(size=(2,2))(segment_features)
        segment_features = keras.layers.Conv2D(64, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)

        outputModel =  keras.layers.UpSampling2D(size=(2,2))(outputModel)
        outputModel =  keras.layers.Conv2D(64, (3, 3), padding='same', strides=(1, 1), activation='relu')(outputModel)
        outputModel =  keras.layers.concatenate([outputModel, segment_features])
        outputModel =  keras.layers.Conv2D(64, (3, 3), padding='same', strides=(1, 1), activation='relu')(outputModel)

        segment_features = keras.layers.Conv2D(64, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)
        segment_features =  keras.layers.UpSampling2D(size=(2,2))(segment_features)
        segment_features = keras.layers.Conv2D(32, (3, 3), padding='same', strides=(1, 1), activation='relu')(segment_features)

        outputModel =  keras.layers.UpSampling2D(size=(2,2))(outputModel)
        outputModel =  keras.layers.Conv2D(32, (3, 3), padding='same', strides=(1, 1), activation='relu')(outputModel)
        outputModel =  keras.layers.concatenate([outputModel, segment_features])
        outputModel =  keras.layers.Conv2D(32, (3, 3), padding='same', strides=(1, 1), activation='relu')(outputModel)
        outputModel =  keras.layers.Conv2D(2, (3, 3), padding='same', strides=(1, 1), activation='sigmoid')(outputModel)
        outputModel =  keras.layers.UpSampling2D(size=(2,2))(outputModel)

        segment_features = keras.layers.Conv2D(1, (3, 3), padding='same', strides=(1, 1), activation='sigmoid')(segment_features)
        segment_features =  keras.layers.UpSampling2D(size=(2,2))(segment_features)
        final_model = Model(input=input_img, outputs = [outputModel, global_featuresClass, segment_features, info_features])

        return final_model

    def train(self, data,test_data, log,sample_interval=1):
        
        # Create folder to save models if needed.
        save_models_path =os.path.join(config.MODEL_DIR,config.TEST_NAME)
        if not os.path.exists(save_models_path):
                os.makedirs(save_models_path)
        
        # Real, Fake and Dummy for Discriminator
        positive_y = np.ones((config.BATCH_SIZE, 1), dtype=np.float32)
        negative_y = -positive_y
        dummy_y = np.zeros((config.BATCH_SIZE, 1), dtype=np.float32)
        
        # total number of batches in one epoch
        total_batch = int(data.size/config.BATCH_SIZE)

        for epoch in range(config.NUM_EPOCHS):
                for batch in range(total_batch):
                    # new batch
                    trainL, trainAB, _, predict, segment = data.generate_batch()
                    l_3=np.tile(trainL,[1,1,1,3])

                    _, __, ___, info= self.colorizationModel.predict(l_3)
                    # train generator
                    g_loss =self.combined.train_on_batch([l_3, trainL],
                                                        [trainAB, predict, positive_y, segment, info, info])
                    # train discriminator
                    d_loss = self.discriminator_model.train_on_batch([trainL, trainAB, l_3], [positive_y, negative_y, dummy_y])

                    c_loss = self.classcification_model.train_on_batch([l_3], [info])

                    # update log files
                    write_log(self.callback, self.train_names, g_loss, (epoch*total_batch+batch+1))
                    write_log(self.callback, self.disc_names, d_loss, (epoch*total_batch+batch+1))
                    
                    if (batch+1)%1 ==0: 
                        print("[Epoch %d] [Batch %d/%d] [generator loss: %08f] [discriminator loss: %08f] [classcifier loss: %08f]" %
                              ( epoch, batch,total_batch, g_loss[0], d_loss[0], c_loss))
          
                # save models after each epoch
                save_path = os.path.join(save_models_path, "my_model_combinedEpoch%d.h5" % epoch)
                self.combined.save(save_path) 
                save_path = os.path.join(save_models_path, "my_model_colorizationEpoch%d.h5" % epoch)
                self.colorizationModel.save(save_path) 
                save_path = os.path.join(save_models_path, "my_model_discriminatorEpoch%d.h5" % epoch)
                self.discriminator.save(save_path) 
                
                # sample images after each epoch
                self.sample_images(test_data)

    def sample_images(self,test_data):
        total_batch = int(test_data.size/config.BATCH_SIZE)
        for _ in range(total_batch):
                # load test data
                testL, __ ,  filelist  = test_data.generate_batch_wosign()
                
                # predict AB channels
                predAB, ____, _____, ______  = self.colorizationModel.predict(np.tile(testL,[1,1,1,3]))
                
                # print results
                for i in range(config.BATCH_SIZE):
                        predResult = reconstruct(deprocess(testL)[i], deprocess(predAB)[i], filelist[i][:-4] )

if __name__ == '__main__':
    
    # Create log folder if needed.
    log_path= os.path.join(config.LOG_DIR,config.TEST_NAME)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        
    with open(os.path.join(log_path, str(datetime.datetime.now().strftime("%Y%m%d")) + "_" + str(config.BATCH_SIZE) + "_" + str(config.NUM_EPOCHS) + ".txt"), "w") as log:
        log.write(str(datetime.datetime.now()) + "\n")

        print('load training data from '+ config.TRAIN_DIR)
        train_data = data.DATA("/home/ubuntu/zxf/colorization/dataset_train")
        test_data = data.DATA("/home/ubuntu/zxf/colorization/dataset_second")
        assert config.BATCH_SIZE<=train_data.size, "The batch size should be smaller or equal to the number of training images --> modify it in config.py"
        print("Train data loaded")
        
        print("Initiliazing Model...")
        colorizationModel = MODEL()
        print("Model Initialized!")
        
        print("Start training")
        colorizationModel.train(train_data,test_data, log)