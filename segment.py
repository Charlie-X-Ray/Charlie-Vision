
import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
import os
import skimage
import cv2

os.environ["KMP_DUPLICATE_LIB_OK"]='TRUE'

import torchxrayvision as xrv

model = xrv.baseline_models.chestx_det.PSPNet()
print(model)

original = cv2.imread(r"datasets/converted/1c32170b4af4ce1a3030eb8167753b06.png")
img = xrv.datasets.normalize(original, 255) # convert 8-bit image to [-1024, 1024] range
img = img.mean(2)[None, ...]
print(img.shape)

transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),xrv.datasets.XRayResizer(512)])

img = transform(img)
img = torch.from_numpy(img)

with torch.no_grad():
    pred = model(img)

cv2.imshow("original", original)
cv2.imshow(model.targets[4], pred[0,4].numpy())
cv2.waitKey(0)

# output = model(img)
# print(output.shape)
# print(output[0,0])
