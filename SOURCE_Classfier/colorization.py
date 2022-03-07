import os
import tensorflow as tf
import config as config
import numpy as np
import cv2
import dataClass as data
from keras import applications
from keras.models import load_model
from keras.backend.tensorflow_backend import set_session

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
config_1 = tf.ConfigProto()
config_1.gpu_options.allow_growth = True
set_session(tf.Session(config=config_1))

def deprocess(imgs):
    imgs = imgs * 255
    imgs[imgs > 255] = 255
    imgs[imgs < 0] = 0
    return imgs.astype(np.uint8)

def reconstruct(batchX, predictedY, filelist):
    result = np.concatenate((batchX, predictedY), axis=2)
    result = cv2.cvtColor(result, cv2.COLOR_Lab2BGR)
    save_results_path = config.RESULT_DIR
    if not os.path.exists(save_results_path):
        os.makedirs(save_results_path)
    save_path = os.path.join(save_results_path, filelist +  "_reconstructed.jpg" )
    cv2.imwrite(save_path, result)
    return result

def reconstruct_no(batchX, predictedY):
    result = np.concatenate((batchX, predictedY), axis=2)
    result = cv2.cvtColor(result, cv2.COLOR_Lab2BGR)
    return result

def sample_images():
    VGG_modelF = applications.vgg16.VGG16(weights='imagenet', include_top=True) 
    save_models_path = config.MODEL_DIR
    save_path = os.path.join(save_models_path, config.PRETRAINED)
    # print(save_path) 
    colorizationModel = load_model(save_path)
    test_data = data.TEST_DATA(config.TEST_DIR)
    assert config.BATCH_SIZE<=test_data.size, "The batch size should be smaller or equal to the number of testing images --> modify it in config.py"
    total_batch = int(test_data.size/config.BATCH_SIZE)
    print("number of images to inpaint " + str(test_data.size))
    print("total number of batches to colorize " + str(total_batch))
    for b in range(total_batch):          
            batchX, batchY,  filelist, original, labimg_oritList  = test_data.generate_batch()
            predY, A, B = colorizationModel.predict(np.tile(batchX,[1,1,1,3]))
       
            for i in range(config.BATCH_SIZE):
                originalResult = original[i]
                height, width, channels = originalResult.shape
                predY_2 = deprocess(predY[i])
                predY_2 = cv2.resize(predY_2, (width,height))
                labimg_oritList_2 =np.expand_dims(labimg_oritList[i], axis=2)
                predResult_2= reconstruct_no(deprocess(labimg_oritList_2), predY_2)
                save_results_path = config.RESULT_DIR
                if not os.path.exists(save_results_path):
                    os.makedirs(save_results_path)
                save_path = os.path.join(save_results_path, filelist[i][:-4] +  "_reconstructed.jpg" )
                cv2.imwrite(save_path, predResult_2)               
            print("Batch " + str(b)+"/"+str(total_batch))
            
if __name__ == '__main__':
    sample_images()
