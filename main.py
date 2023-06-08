import csv
import os
from os.path import join
from PIL import Image
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import pandas as pd
import numpy as np
import cv2

DESTINATION_FOLDER = 'outputs'
DATASET_FOLDER = r'..\datasets\vinbigdata-chest-xray-abnormalities-detection'
ANNOTATED_FOLDER = join(DESTINATION_FOLDER, 'annotated')
PNG_FOLDER = join(DESTINATION_FOLDER, 'converted')
TRAIN_FILE = join(DATASET_FOLDER, 'train.csv')
TRAIN_FOLDER = join(DATASET_FOLDER, 'train')


def read_xray(path, voi_lut=True, fix_monochrome=True):
    # Original from: https://www.kaggle.com/raddar/convert-dicom-to-np-array-the-correct-way
    dicom = pydicom.read_file(path)

    # VOI LUT (if available by DICOM device) is used to transform raw DICOM data to
    # "human-friendly" view
    if voi_lut:
        data = apply_voi_lut(dicom.pixel_array, dicom)
    else:
        data = dicom.pixel_array

    # depending on this value, X-ray may look inverted - fix that:
    if fix_monochrome and dicom.PhotometricInterpretation == "MONOCHROME1":
        data = np.amax(data) - data

    data = data - np.min(data)
    data = data / np.max(data)
    data = (data * 255).astype(np.uint8)

    return data

def resize(im, size, keep_ratio=False, resample=Image.LANCZOS):
    # Original from: https://www.kaggle.com/xhlulu/vinbigdata-process-and-resize-to-image
    im = Image.fromarray(im)

    if keep_ratio:
        im.thumbnail((size, size), resample)
    else:
        im = im.resize((size, size), resample)

    return im

def draw_boxes(img, box_coords):
    '''Draws boxes around pngs and returns it'''

    coord_example = {
        'class_name': '',
        'class_id': '',
        'x0': 0,
        'y0': 0,
        'x1': 0,
        'y1': 0,
        'rad_id': '',
    }

    for coord in box_coords:
        '''Draw box'''
        x0, y0, x1, y1 = coord['x0'], coord['y0'], coord['x1'], coord['y1']
        img = cv2.rectangle(img, (y0, x0), (y1, x1), (0, 255, 100), 3)

    return img

def retrieve_dicom_data(num: int, train_file: str):
    '''Retrieves meta data for dicom files'''

    df = pd.read_csv(train_file)
    unique_ids = df[df['class_name'] != 'No finding'].loc[:,'image_id'].unique()[:num]

    image_metadatas = []
    for id in unique_ids:
        coords = []

        df_f = df[df['image_id'] == id][['class_name', 'class_id', 'x_min', 'y_min', 'x_max', 'y_max', 'rad_id']]

        for row in df_f.values:
            coords.append({
                'class_name': row[0],
                'class_id': row[1],
                'x0': int(row[2]),
                'y0': int(row[3]),
                'x1': int(row[4]),
                'y1': int(row[5]),
                'rad_id': row[6],
            })
        
        image_metadatas.append({ 'image_id': id, 'coords': coords, })

    return image_metadatas

def main():
    assert os.path.exists(DATASET_FOLDER)

    number_of_images = 20

    dicom_datas = retrieve_dicom_data(number_of_images, TRAIN_FILE)
    for dicom_datum in dicom_datas:
        dicom_path = join(TRAIN_FOLDER, dicom_datum['image_id'] + '.dicom')
        img = read_xray(dicom_path)
        # img = resize(img, 512)
        cv2.imwrite(join(PNG_FOLDER, dicom_datum['image_id'] + '.png'), img)
        img = cv2.imread(join(PNG_FOLDER, dicom_datum['image_id'] + '.png'))
        img = draw_boxes(img, dicom_datum['coords'])
        cv2.imshow(dicom_path, cv2.resize(img, (512, 512)))
        cv2.waitKey(0)
        cv2.destroyWindow(dicom_path)



if __name__ == '__main__':
    main()
