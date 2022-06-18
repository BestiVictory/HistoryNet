import numpy as np
import cv2
import os
import config as config

class DATA():

    def __init__(self, dirname):
        self.dir_path = dirname
        # self.filelist = os.listdir(self.dir_path)
        self.filelist = [filename for filename in os.listdir(self.dir_path) if filename.endswith("jpg")]
        self.batch_size = config.BATCH_SIZE
        self.size = len(self.filelist)
        self.data_index = 0

    def read_img(self, filename):
        #print(filename)
        img = cv2.imread(filename, 3)
        labimg = cv2.cvtColor(cv2.resize(img, (config.IMAGE_SIZE, config.IMAGE_SIZE)), cv2.COLOR_BGR2Lab)
        labimg_ori = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        return np.reshape(labimg[:,:,0], (config.IMAGE_SIZE, config.IMAGE_SIZE, 1)), labimg[:, :, 1:], img, labimg_ori[:,:,0]

    def generate_batch(self):
        batch = []
        labels = []
        filelist = []
        labimg_oritList= []
        originalList = []
        for i in range(self.batch_size):
            filename = os.path.join(self.dir_path, self.filelist[self.data_index])
            filelist.append(self.filelist[self.data_index])
            greyimg, colorimg, original, labimg_ori = self.read_img(filename)
            batch.append(greyimg)
            labels.append(colorimg)
            originalList.append(original)
            labimg_oritList.append(labimg_ori)
            self.data_index = (self.data_index + 1) % self.size
        batch = np.asarray(batch)/255 # values between 0 and 1
        labels = np.asarray(labels)/255 # values between 0 and 1
        originalList = np.asarray(originalList)
        labimg_oritList = np.asarray(labimg_oritList)/255 # values between 0 and 1
        return batch, labels, filelist , originalList, labimg_oritList
