import os
import numpy as np
import cv2
import logging

import torch

from models.cae_32x32x32_zero_pad_bin import CAE

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def imgTransformer(inputFolder,name):
    print(name)
    image = cv2.imread(os.path.join(inputFolder,name))
    image = np.array(image)
    pad = ((24, 24), (0, 0), (0, 0))

    img = np.pad(image, pad, mode="edge") / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).float()
    
    patches = np.reshape(img, (3, 6, 128, 10, 128))
    patches = np.transpose(patches, (0, 1, 3, 2, 4))
    
    logging.info(f'The image {name} is patched and tensored!')
    
    return img,patches,name
    

def imgPreprocess(inputFolder):
    patch = torch.empty(len(os.listdir(inputFolder)),3,6,10,128,128)
    img = torch.empty(len(os.listdir(inputFolder)),3,768,1280)
    name = []
    for idx,images in enumerate(os.listdir(inputFolder)):
        img[idx]=imgTransformer(inputFolder,images)[0]
        patch[idx]=imgTransformer(inputFolder,images)[1]
        name.append(imgTransformer(inputFolder,images)[2])
    logging.info('All the images are processed')
    
    return img,patch,name

def imgEncoding(name,patches,checkpoint,interFolder):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    encoder = CAE()
    encoder.load_state_dict(torch.load(checkpoint))
    encoder.eval()
    
    encoder.to(device)
    
    for idx,patcher in enumerate(patches):
        logging.info(f'Doing for {name[idx]}')
        out = torch.zeros(6,10, 32, 32, 32)
        for i in range(6):
            for j in range(10):
                x = patcher[None,:, i, j, :, :].to(device)
                y = encoder(x)
                out[i,j]=y.data
        torch.save(out,os.path.join(interFolder,str(name[idx])+'.pt'))
    
    logging.info('Images are encoded')
    
    return encoder

def imgDetransformation(img):
    out = np.transpose(img, (0, 3, 1, 4, 2))
    out = np.reshape(out, (768, 1280, 3))
    return out.detach().numpy()

def imgDeymstify(inFolder,outFolder,model,name):
    print(name)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'  
    model.to(device)
    torch.cuda.empty_cache()
    
    for idx,encoded in enumerate(os.listdir(inFolder)):
        print(idx)
        imgEncoded = torch.load(os.path.join(inFolder,encoded))
        imgEncoded = imgEncoded.to(device)
        print(f'the name is {encoded} and the type is {type(encoded)} and the output is initialized')
        out = torch.zeros(6,10, 3, 128, 128)
        for i in range(6):
            for j in range(10):
                result = model.decode(imgEncoded[i,j,:,:,:].unsqueeze(0))
                out[i,j] = result.data
        out1 = imgDetransformation(out)
        norm_image = cv2.normalize(out1, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_32F)
        norm_image = norm_image.astype(np.uint8)
        cv2.imwrite(os.path.join(outFolder,str(idx)+'.png'),norm_image)
        del(out)
        print('===============================================================================================')
        

if __name__ == '__main__':
    outputFolder = r'../output'
    inputFolder  = r'../input'
    interFolder  = r'../intermediate'
    checkpoint   = r'../checkpoint/pruned_weights.state'
    
    os.makedirs(outputFolder, exist_ok=True)
    os.makedirs(inputFolder, exist_ok=True)
    os.makedirs(interFolder, exist_ok=True)
    
    images,patches,names = imgPreprocess(inputFolder)
    print(patches.shape)
    model = imgEncoding(names,patches,checkpoint,interFolder)
    imgDeymstify(interFolder,outputFolder,model,names)
    
    