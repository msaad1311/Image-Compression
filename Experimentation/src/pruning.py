import numpy as np
import os
import cv2

import torch
import imgEncoding as im

from models.cae_32x32x32_zero_pad_bin import CAE

def applyPruning(percentage,weightPath):
    sd = torch.load(weightPath)  # load the state dicd
    for k in sd.keys():
        if not 'weight' in k:
            continue  # skip biases and other saved parameters
        w = sd[k]
        sd[k] = w * (abs(w) > percentage*torch.max(abs(w)))  # set to zero weights smaller than thr 
    torch.save(sd, r'../checkpoint/pruned_weights.state')
    return

def videoCreator(output,name,videoObj):
    image = cv2.imread(os.path.join(output,name))
    
    return
    

pruningPercentage = [1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.0]
originalWeight = r'../checkpoint\model_final.state'
prunedWeight = r'../checkpoint/pruned_weights.state'
singleOutput = r'../singleOutput'
singleInput  = r'../singleInput'
singleInter  = r'../singleInter'

os.makedirs(singleOutput, exist_ok=True)
os.makedirs(singleInput, exist_ok=True)
os.makedirs(singleInter, exist_ok=True)

for percent in pruningPercentage:
    print(f'========================= Working for {percent}================================')
    applyPruning(percent,originalWeight)
    images,patches,names = im.imgPreprocess(singleInput)
    print(names)
    names = str(names[0].split('.')[0])+str(percent) +'.'+ str(names[0].split('.')[1])
    model = im.imgEncoding([names],patches,prunedWeight,singleInter)
    im.imgDeymstify(singleInter,singleOutput,model,[names])
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    video = cv2.VideoWriter('./noise.avi', fourcc, 15.0, (1280, 768))
    img = cv2.imread(os.path.join(singleOutput,names))
    print(img.shape)
    video.write(img)

video.release()
    
    