import tensorflow as tf
import numpy as np
import cv2
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

Groundtruth_path = ""   #the path of source images folder 
Output_path = ""        #the path of colorization images folder 

dir1 = os.listdir(Groundtruth_path)
dir2 = os.listdir(Output_path)
num=len(dir1)
avg_ssim = 0
avg_psnr = 0

for line2 in dir2:
    name = line2.split("_reconstructed")
    pic_name = name[0]+'.jpg'
    for line1 in dir1:
        if pic_name==line1:
           originalResult = cv2.imread(os.path.join(Groundtruth_path,line1))
           predResult = cv2.imread(os.path.join(Output_path,line2))
           avg_ssim += tf.keras.backend.eval(tf.image.ssim(tf.convert_to_tensor(originalResult, dtype=tf.float32),
                                                    tf.convert_to_tensor(predResult, dtype=tf.float32), max_val=255))
           avg_psnr += tf.keras.backend.eval(tf.image.psnr(tf.convert_to_tensor(originalResult, dtype=tf.float32),
                                                    tf.convert_to_tensor(predResult, dtype=tf.float32), max_val=255))
 
print(" ----------  ssim loss =", "{:.8f}------------------".format(avg_ssim/num))
print(" ----------  psnr loss =", "{:.8f}------------------".format(avg_psnr/num))