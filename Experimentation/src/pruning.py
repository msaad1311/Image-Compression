import numpy as np
import os
import cv2
import gc
import time
from skimage.metrics import structural_similarity as ssim

import torch
import imgEncoding as im

from models.cae_32x32x32_zero_pad_bin import CAE

def applyPruning(percentage, weightPath):
    sd = torch.load(weightPath)  # load the state dicd
    for k in sd.keys():
        if not 'weight' in k:
            continue  # skip biases and other saved parameters
        w = sd[k]
        # set to zero weights smaller than thr
        sd[k] = w * (abs(w) > percentage*torch.max(abs(w)))
    torch.save(sd, r'../checkpoint/pruned_weights.state')


def metric(im1, im2):
    result = ssim(im1, im2, multichannel=True)
    return round(result, 2)


pruningPercentage = [1, 0.9, 0.8, 0.7, 0.6, 0.5,
                     0.4, 0.3, 0.2, 0.1, 0.05, 0.025, 0.0125, 0]
originalWeight = r'../checkpoint/model_final.state'
prunedWeight = r'../checkpoint/pruned_weights.state'
singleOutput = r'../singleOutput'
singleInput = r'../singleInput'
singleInter = r'../singleInter'
fileName = r'femaleActress.jpg'

os.makedirs(singleOutput, exist_ok=True)
os.makedirs(singleInput, exist_ok=True)
os.makedirs(singleInter, exist_ok=True)

img, timer, index = [], [], []
for percent in pruningPercentage:
    print(
        f'========================= Working for {percent}================================')

    applyPruning(percent, originalWeight)
    stime = time.time()

    images, patches, names = im.imgPreprocess(singleInput)
    model = im.imgEncoding(names, patches, prunedWeight, singleInter)
    im.imgDeymstify(singleInter, singleOutput, model, names)

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    video = cv2.VideoWriter('./animation.avi', fourcc, 1, (1280, 720))

    originalImage = cv2.imread(os.path.join(singleInput, fileName))
    generateImage = cv2.imread(os.path.join(singleOutput, '0.png'))

    index.append(metric(originalImage, generateImage))
    img.append(generateImage)
    os.remove(prunedWeight)

    gc.collect()
    timer.append(time.time()-stime)

for i in range(len(img)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img[i], 'Pruning Percentage:' + str(pruningPercentage[i]
                                                    * 100)+'%',  (50, 50), font, 1, (0, 0, 0),  2, cv2.LINE_4)
    
    cv2.putText(img[i], 'Time taken:' + str(round(timer[i], 2)),
                (50, 100),  font, 1,  (0, 0, 0),  2,  cv2.LINE_4)
    
    cv2.putText(img[i], 'Similarity Index:'+str(index[i]),
                (50, 150), font, 1, (0, 0, 0), 2, cv2.LINE_4)
    
    video.write(img[i])

video.release()
