import numpy as np
import torch
import pickle
from models.cae_32x32x32_zero_pad_bin import CAE

# model = CAE()
# model.load_state_dict(torch.load(r'../checkpoint\model_final.state'))
# for params in model.parameters():
#     print(params)
#     break
# print(model.parameters)
thr = 0.001
sd = torch.load(r'../checkpoint\model_final.state')  # load the state dicd
for k in sd.keys():
  if not 'weight' in k:
    continue  # skip biases and other saved parameters
  w = sd[k]

  sd[k] = w * (abs(w) > 0.1*torch.max(abs(w)))  # set to zero weights smaller than thr 
torch.save(sd, r'../checkpoint/pruned_weights.state')