import os
import numpy as np
import cv2
import matplotlib.pylab as plt
# from bagoftools.logger import Logger

import torch

from models.cae_32x32x32_zero_pad_bin import CAE

def imgTransformer(inputFolder,name):
    print(name)
    image = cv2.imread(os.path.join(inputFolder,name))
    image = np.array(image)
    pad = ((24, 24), (0, 0), (0, 0))

    img = np.pad(image, pad, mode="edge") / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).float()
    print(img.shape)
    patches = np.reshape(img, (3, 6, 128, 10, 128))
    patches = np.transpose(patches, (0, 1, 3, 2, 4))
    
    return img,patches,name
    

def imgPreprocess(inputFolder):
    print(f'The input folder specified is {str(inputFolder)}')
    img,patch,name = [],[],[]
    for images in os.listdir(inputFolder):
        img.append(imgTransformer(inputFolder,images)[0].numpy())
        patch.append(imgTransformer(inputFolder,images)[1].numpy())
        name.append(imgTransformer(inputFolder,images)[2])
    img = np.array(img)
    patch = np.array(patch)
    
    return img,patch,name

def imgEncoding(name,patches,checkpoint,interFolder):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    encoder = CAE()
    encoder.load_state_dict(torch.load(checkpoint))
    encoder.eval()
    
    encoder.to(device)
    
    for idx,patcher in enumerate(patches):
        out=[]
        name[idx] = name[idx].split('.')[0]
        patch = torch.tensor(patcher).to(device)
        print('the patch shape is:',patch.shape)
        out = torch.zeros(6,10, 32, 32, 32)
        for i in range(6):
            for j in range(10):
                x = patch[None,:, i, j, :, :]
                y = encoder(x)
                # print('The shape is y',y.shape)
                out[i,j]=y.data
        # print('the output final shapoe is:',out.shape)
        # out = np.array(out)
        torch.save(out,os.path.join(interFolder,str(name[idx])+'.pt'))
        
    # logger.info('The images are encoded and saved') 
    
    return encoder

def imgDetransformation(img):
    out = np.transpose(img, (0, 3, 1, 4, 2))
    out = np.reshape(img, (768, 1280, 3))
    # out = np.transpose(out, (2, 0, 1))
    return out

def imgDeymstify(inFolder,outFolder,model):
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    torch.cuda.empty_cache()
    for encoded in os.listdir(inFolder):
        imgEncoded = torch.load(os.path.join(inFolder,encoded))
        imgEncoded = torch.tensor(imgEncoded).to(device)
        # imgEncoded = imgEncoded.squeeze(1)
        out = torch.zeros(6,10, 3, 128, 128)
        for i in range(6):
            for j in range(10):
                result = model.decode(imgEncoded[i][j].unsqueeze(0))
                out[i,j] = result.data
        print('the outut is',out.shape)
        out = imgDetransformation(out.detach().cpu().numpy())
        print(out.shape)
        plt.imshow(out)
        plt.show()
        
    

if __name__ == '__main__':
    outputFolder = r'../output'
    inputFolder  = r'../input'
    interFolder  = r'../intermediate'
    
    os.makedirs(outputFolder, exist_ok=True)
    os.makedirs(inputFolder, exist_ok=True)
    os.makedirs(interFolder, exist_ok=True)
    
    images,patches,names = imgPreprocess(inputFolder)
    print(patches.shape)
    model = imgEncoding(names,patches,r'../checkpoint/model_final.state',interFolder)
    imgDeymstify(interFolder,outputFolder,model)
    
    