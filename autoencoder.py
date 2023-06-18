import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
import os
os.environ["KMP_DUPLICATE_LIB_OK"]='TRUE'
import skimage
import cv2
import torchxrayvision as xrv

# Sampled https://github.com/mlmed/torchxrayvision/blob/master/scripts/autoencoder.ipynb

def view(img):
    print(img.shape)
    cv2.imshow("windowd", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

resizer = lambda x: cv2.resize(x, (224, 224))

original = skimage.io.imread(r"datasets/converted/1c32170b4af4ce1a3030eb8167753b06.png")
print(original.shape)
resized = resizer(original)
view(resized)
# image = cv2.normalize(resized, None, 0, 255, cv2.NORM_MINMAX)
image = xrv.utils.normalize(original, 255) # convert 8-bit image to [-1024, 1024] range
view(image)
# image = image.mean(2)[None, ...]
image = resizer(image)[None, ...]
view(image[0])
transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop()])

image = torch.from_numpy(image).unsqueeze(0)
print(image.shape)

ae = xrv.autoencoders.ResNetAE(weights="101-elastic") # trained on PadChest, NIH, CheXpert, and MIMIC
z = ae.encode(image)
image2 = ae.decode(z)
view(image2.detach().numpy()[0][0])