import numpy as np
import torch
import pickle

output = r'../intermediate/frame_6.pt'
x = torch.load(output)
# x = x.to(torch.float16)
torch.save(x.clone(),'testing.pt')
print(x.dtype)
print(x.__sizeof__())
y = x.cpu().numpy()
y = np.transpose(y,(0,2,1,3,4))
y = np.reshape(y,(6*32,10*32,-1))
y = np.reshape(y,(-1,320*32))
np.savetxt('tester.txt',y)
print(y.shape)

# np.savetxt(r'../intermediate/frame_6.npy',y)
###Load into file
