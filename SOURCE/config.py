import os

TEST_NAME ="HistoryNet"
SIGN_NAME = "sign.txt"
ROOT_DIR = os.path.abspath('../') #上一级目录
DATA_DIR = os.path.join(ROOT_DIR, 'DATASET/'+'/')
OUT_DIR = os.path.join(ROOT_DIR, 'RESULT/'+TEST_NAME)
MODEL_DIR = os.path.join(ROOT_DIR, 'MODEL/')
LOG_DIR = os.path.join(ROOT_DIR, 'LOGS/'+'/')

TRAIN_DIR = "train"  # UPDATE
#TEST_DIR = "test" # UPDATE
TEST_DIR = os.path.join(ROOT_DIR, 'TEST/'+TEST_NAME)

# DATA INFORMATION
IMAGE_SIZE = 224
BATCH_SIZE = 4


# TRAINING INFORMATION
PRETRAINED = "my_model_colorizationEpoch7.h5" # UPDATE
NUM_EPOCHS = 8

