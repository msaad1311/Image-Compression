import os
import yaml
import argparse
from pathlib import Path

import numpy as np
import torch as T
import torch.nn as nn
from torch.utils.data import DataLoader

from data_loader import ImageFolder720p
from utils import save_imgs
import matplotlib.pylab as plt

# from bagoftools.namespace import Namespace
# from bagoftools.logger import Logger

from models.cae_32x32x32_zero_pad_bin import CAE

model = CAE()

model.load_state_dict(T.load(r'../checkpoint\model_yt_small_final.state'))

encoded = T.load('something.pt', map_location=T.device('cpu'))
print(encoded.shape)

out = model.decode(encoded)
print(out.shape)

plt.imshow(out[0].detach().permute(1,2,0))
plt.show()