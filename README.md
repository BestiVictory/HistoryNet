# HistoryNet
![image](https://user-images.githubusercontent.com/22883072/136405882-0ad2523f-9ff8-4e77-9185-0547c97b66fe.png)

In industry, there exist plenty of scenarios where old gray photos need to be automatically colored, such as video sites and archives. In this paper, we present the HistoryNet focusing on historical person’s diverse high fidelity clothing colorization based on fine grained semantic understanding and prior. Colorization of historical persons is realistic and practical, however, existing methods do not perform well in the regards. In this paper, a HistoryNet including three parts, namely, classification, fine grained semantic parsing and colorization, is proposed. Classification sub-module supplies classifying of images according to the eras, nationalities and garment types; Parsing sub-network supplies the semantic for person contours, clothing and background in the image to achieve more accurate colorization of clothes and persons and prevent color overflow. In the training process, we integrate classification and semantic parsing features into the coloring generation network to improve colorization. Through the design of classification and parsing subnetwork, the accuracy of image colorization can be improved and the boundary of each part of image can be more clearly. Moreover, we also propose a novel Modern Historical Movies Dataset(MHMD) containing 1,353,166 images and 42 labels of eras, nationalities, and garment types for automatic colorization from 147 historical movies or TV series made in modern time. Various quantitative and qualitative comparisons demonstrate that our method outperforms the state-of-the-art colorization methods, especially on military uniforms, which has correct colors according to the historical literatures.

[Focusing on Persons: Colorizing Old Images Learning from Modern Historical Movies](https://arxiv.org/abs/2108.06515)  
Xin Jin, Zhonglan Li, Ke Liu, Dongqing Zou, Xiaodong Li, Xingfan Zhu, Ziyin Zhou, Qilong Sun, Qingyu Liu  
ACM International Conference on Multimedia (ACM MM), 2021

## Prerequisites
* Python3  
* OpenCV-Python  
* Tensorflow  

## Getting Started
1. Clone this repo:  
```
   git clone https://github.com/BestiVictory/HistoryNet.git  
   cd HistoryNet
``` 
2. Create a Virtual Environment  
```
   conda create -n HistoryNet python=3.6 
```
3. Install all the dependencies  
```
   pip install -r requirements.txt
```
## Model
1. Download it from [BaiduCloud](https://pan.baidu.com/s/1KQnVA77EBF3huCwG4dVsHQ) (code: j0gi)  
2. Now the model should place in `MODEL`. 

## Colorize Images
Enter `HistoryNet/SOURCE`. Please follow the command below to colorize all the images in `TEST` folder.
```
python HistoryNetPrint.py
```
All the colorized results would save in `RESULTS` folder.

Note: You can update `config.py` to change the paths of model, test and result folder. 

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
