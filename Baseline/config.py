import os

# DIRECTORY INFORMATION
TEST_NAME ="Baseline"
ROOT_DIR = os.path.abspath('../')
OUT_DIR = os.path.join(ROOT_DIR, 'RESULT/'+TEST_NAME+'/')
MODEL_DIR = os.path.join(ROOT_DIR, 'MODEL/'+TEST_NAME+'/')
LOG_DIR = os.path.join(ROOT_DIR, 'LOGS/'+TEST_NAME+'/')

TRAIN_DATA = os.path.join(ROOT_DIR, 'DATASET/'+'dataset_train')
TEST_DATA = os.path.join(ROOT_DIR, 'DATASET/'+'dataset_second')

TEST_NAME_2 = "Baseline_test"
TEST_DIR = os.path.join(ROOT_DIR, 'TEST/'+TEST_NAME_2+'/')
RESULT_DIR = os.path.join(ROOT_DIR, 'RESULT/'+TEST_NAME_2+'/')

# DATA INFORMATION
IMAGE_SIZE = 224
BATCH_SIZE = 16

# TRAINING INFORMATION
GPU_ID = "1"
PRETRAINED = "my_model_colorizationEpoch7.h5" # UPDATE
NUM_EPOCHS = 8