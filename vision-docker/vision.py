import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
import os
import skimage
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"]='TRUE'

import torchxrayvision as xrv

dn = xrv.models.DenseNet(weights="all")

def diagnose(img, model=dn):
  img = img - np.min(img)
  img = img / np.max(img)
  img = (img * 255).astype(np.uint8)
  img  = xrv.datasets.normalize(img, 255)
  img = img[None, :, :]       
  transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),
                                              xrv.datasets.XRayResizer(224)])
  img = transform(img)
  img = torch.from_numpy(img).unsqueeze(0)
  with torch.no_grad():
    out = model(img)
  outdict = dict(zip(model.pathologies,out[0].detach().numpy().tolist()))
  return outdict

psp = xrv.baseline_models.chestx_det.PSPNet()

def segment(img, model=psp):
  img = img - np.min(img)
  img = img / np.max(img)
  img = (img * 255).astype(np.uint8)
  img = xrv.datasets.normalize(img, 255) # convert 8-bit image to [-1024, 1024] range
  img = img[None, ...] # Make single color channel

  transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),xrv.datasets.XRayResizer(512)])

  img = transform(img)
  img = torch.from_numpy(img)
  with torch.no_grad():
    pred = model(img)
  
  save_dir = Path(".") / "segmented"
  
  for i in range(len(model.targets)):
    filename = save_dir / f'{model.targets[i]}.png'
    plt.imsave(filename, pred[0, i])
    if 'Heart.png' in str(filename):
      return filename.as_posix()
  
  return filename.as_posix()

