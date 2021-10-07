import numpy as np
import cv2
import os
import config as config
import math

class DATA():

    def __init__(self, dirname):
        self.dir_path = os.path.join(config.DATA_DIR, dirname)
        self.filelist = os.listdir(self.dir_path)
        self.batch_size = config.BATCH_SIZE
        self.size = len(self.filelist)
        self.data_index = 0

    def read_img(self, filename):
        IMAGE_SIZE = 224
        MAX_SIDE = 1500
        img = cv2.imread(filename, 3)
        height, width, channels = img.shape
        if height > MAX_SIDE or width > MAX_SIDE:
            print("Image " + filename + " is of size (" + str(height) + "," + str(width) +  ").")
            print("The maximum image size allowed is (" + str(MAX_SIDE) + "," + str(MAX_SIDE) +  ").")
            r = min(MAX_SIDE/height,MAX_SIDE/width)
            height = math.floor(r*height) 
            width = math.floor(r*width)
            img = cv2.resize(img,(width,height))
            print("It has been resized to (" + str(height) + "," + str(width) + ")")
        min_hw = int(min(height,width)/2)
        img = img[int(height/2)-min_hw:int(height/2)+min_hw,int(width/2)-min_hw:int(width/2)+min_hw,:]
        labimg = cv2.cvtColor(cv2.resize(img, (IMAGE_SIZE, IMAGE_SIZE)), cv2.COLOR_BGR2Lab)
        labimg_ori = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        return np.reshape(labimg[:,:,0], (config.IMAGE_SIZE, config.IMAGE_SIZE, 1)), labimg[:, :, 1:], img, np.reshape(labimg_ori[:,:,0], (height, width, 1))
        
    def generate_batch(self):
        batch = []
        labels = []
        filelist = []
        labimg_oritList = []
        originalList = []
        for i in range(self.batch_size):
            filename = os.path.join(config.DATA_DIR, self.dir_path, self.filelist[self.data_index])
            filelist.append(self.filelist[self.data_index])
            greyimg, colorimg, original, labimg_ori = self.read_img(filename)
            batch.append(greyimg)
            labels.append(colorimg)
            labimg_oritList.append(labimg_ori)
            originalList.append(original)
            self.data_index = (self.data_index + 1) % self.size
        batch = np.asarray(batch)/255 # values between 0 and 1
        labels = np.asarray(labels)/255 # values between 0 and 1
        originalList = np.asarray(originalList)
        labimg_oritList = np.asarray(labimg_oritList)/255 # values between 0 and 1
        return batch, labels, filelist, originalList, labimg_oritList
