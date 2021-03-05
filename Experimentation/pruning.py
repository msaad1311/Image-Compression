import numpy as np
import pickle

import torch
import imgEncoding

from models.cae_32x32x32_zero_pad_bin import CAE

def prunedWeight(percentage,weightPath):
    sd = torch.load(weightPath)  # load the state dicd
    for k in sd.keys():
        if not 'weight' in k:
            continue  # skip biases and other saved parameters
        w = sd[k]

    sd[k] = w * (abs(w) > percentage*torch.max(abs(w)))  # set to zero weights smaller than thr 
    torch.save(sd, r'../checkpoint/pruned_weights.state')
    return

pruningPercentage = [1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.0]
originalWeight = r'../checkpoint\model_final.state'

for percent in pruningPercentage:
    prunedWeight(percent,originalWeight)
    