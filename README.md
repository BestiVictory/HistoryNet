# HistoryNet
![image](https://user-images.githubusercontent.com/22883072/136405882-0ad2523f-9ff8-4e77-9185-0547c97b66fe.png)

In industry, there exist plenty of scenarios where old gray photos need to be automatically colored, such as video sites and archives. In this paper, we present the HistoryNet focusing on historical person’s diverse high fidelity clothing colorization based on fine grained semantic understanding and prior. Colorization of historical persons is realistic and practical, however, existing methods do not perform well in the regards. In this paper, a HistoryNet including three parts, namely, classification, fine grained semantic parsing and colorization, is proposed. Classification sub-module supplies classifying of images according to the eras, nationalities and garment types; Parsing sub-network supplies the semantic for person contours, clothing and background in the image to achieve more accurate colorization of clothes and persons and prevent color overflow. In the training process, we integrate classification and semantic parsing features into the coloring generation network to improve colorization. Through the design of classification and parsing subnetwork, the accuracy of image colorization can be improved and the boundary of each part of image can be more clearly. Moreover, we also propose a novel Modern Historical Movies Dataset(MHMD) containing 1,353,166 images and 42 labels of eras, nationalities, and garment types for automatic colorization from 147 historical movies or TV series made in modern time. Various quantitative and qualitative comparisons demonstrate that our method outperforms the state-of-the-art colorization methods, especially on military uniforms, which has correct colors according to the historical literatures.

[Focusing on Persons: Colorizing Old Images Learning from Modern Historical Movies](https://arxiv.org/abs/2108.06515)  
Xin Jin, Zhonglan Li, Ke Liu, Dongqing Zou, Xiaodong Li, Xingfan Zhu, Ziyin Zhou, Qilong Sun, Qingyu Liu  
ACM International Conference on Multimedia (ACM MM), 2021

## Prerequisites 
* keras==2.2.4
* numpy==1.15.4
* opencv-python==4.1.0.25
* tensorflow==1.14.0
* tensorflow-gpu==1.14.0
* h5py==2.10.0
* python==3.6.0

## Getting Started
1. Clone this repo:  
```
   git clone https://github.com/BestiVictory/HistoryNet.git  
   cd SOURCE_HistoryNet
``` 
2. Create a Virtual Environment  
```
   conda create -n HistoryNet python=3.6 
   conda activate HistoryNet
```
3. Install all the dependencies  
```
   pip install -r requirements.txt
```
## Dataset
MHMD can be download [here](https://github.com/BestiVictory/MHMD).
You can also choose your own dataset.

## Model
1. Download it from [BaiduCloud](https://pan.baidu.com/s/1KQnVA77EBF3huCwG4dVsHQ) (code: j0gi)  
2. Now the model should be placed in `MODEL` in the root directory.

## Parameters
If you want to colorize images, you can update `TEST_DIR` and the colorization images are in `RESULT_DIR`. And `PRETRAINED` is the path of colorization model. If you want to train all the time, you need to update `TRAIN_DATA` and `TEST_DATA`. `TRAIN_DATA` is the path of training dataset and `TEST_DATA` is the path of testing dataset.
```
import os

# DIRECTORY INFORMATION
TEST_NAME ="HistoryNet"
SIGN_NAME = "sign.txt"
ROOT_DIR = os.path.abspath('../')
OUT_DIR = os.path.join(ROOT_DIR, 'RESULT/'+TEST_NAME+'/')
MODEL_DIR = os.path.join(ROOT_DIR, 'MODEL/'+TEST_NAME+'/')
LOG_DIR = os.path.join(ROOT_DIR, 'LOGS/'+TEST_NAME+'/')

TRAIN_DATA = os.path.join(ROOT_DIR, 'DATASET/'+'train')
TEST_DATA = os.path.join(ROOT_DIR, 'DATASET/'+'test')

TEST_NAME_2 = "HistoryNet_test"
TEST_DIR = os.path.join(ROOT_DIR, 'TEST/'+TEST_NAME_2+'/')
RESULT_DIR = os.path.join(ROOT_DIR, 'RESULT/'+TEST_NAME_2+'/')

# DATA INFORMATION
IMAGE_SIZE = 224
BATCH_SIZE = 16

# TRAINING INFORMATION
PRETRAINED = "my_model_colorizationEpoch7.h5"
NUM_EPOCHS = 8
```

## Colorize Images
```
cd SOURCE_HistoryNet
python colorization.py
```
## Train 
```
cd SOURCE_HistoryNet
python HistoryNet.py
```

## Citation
If you find our code/models useful, please consider citing our paper: 
```
@inproceedings{  
    author = {Xin Jin, Zhonglan Li, Ke Liu, Dongqing Zou, Xiaodong Li, Xingfan Zhu, Ziyin Zhou, Qilong Sun, Qingyu Liu},  
    title = {Focusing on Persons: Colorizing Old Images Learning from Modern Historical Movies},  
    booktitle = {ACM International Conference on Multimedia (ACM MM)},  
    year = {2021}  
}
```
