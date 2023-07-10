import csv
import os
from os.path import join
from PIL import Image
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import pandas as pd
import numpy as np
import cv2
import math
from google.cloud import storage

DESTINATION_FOLDER = 'datasets'
DATASET_FOLDER = join('datasets', 'vindr-cxr-original')
ANNOTATED_FOLDER = join(DESTINATION_FOLDER, 'annotated')
PNG_FOLDER = join(DESTINATION_FOLDER, 'converted') # wear to save converted photos
TRAIN_FILE = join(DATASET_FOLDER, 'train.csv')
TRAIN_FOLDER = join(DATASET_FOLDER, 'train')
PROJECT_ID = 'charlie-x-ray'
BUCKET_NAME = 'charlie-x-ray.appspot.com'
ORIGINAL_PREFIX = 'original/'
LEARN_PREFIX = 'learn/'
BROWSE_PREFIX = 'browse/'
STORAGE_CLIENT = storage.Client(project=PROJECT_ID)
BUCKET = STORAGE_CLIENT.get_bucket(BUCKET_NAME)


def read_xray(path, voi_lut=True, fix_monochrome=True):
    # Original from: https://www.kaggle.com/raddar/convert-dicom-to-np-array-the-correct-way
    dicom = pydicom.read_file(path)
    dicom.BitsStored = 16
    # print(dicom.BitsStored)

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

def resize(im, size, keep_ratio=False, resample=Image.Resampling.LANCZOS):
    # Original from: https://www.kaggle.com/xhlulu/vinbigdata-process-and-resize-to-image
    
    im = Image.fromarray(im)

    if keep_ratio:
        im.thumbnail((size, size), resample)
    else:
        im = im.resize((size, size), resample)

    return np.asarray(im)

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

    added_coords = [] 

    def close(new_coord, old_coord):

        if new_coord['class_id'] != old_coord['class_id']:
            return False

        old_x0, old_y0, old_x1, old_y1 = old_coord['x0'], old_coord['y0'], old_coord['x1'], old_coord['y1']
        new_x0, new_y0, new_x1, new_y1 = new_coord['x0'], new_coord['y0'], new_coord['x1'], new_coord['y1']

        measure_dist = lambda x0, y0, x1, y1: math.sqrt(abs(x0 - x1)**2) + math.sqrt(abs(y0 - y1)**2)

        too_close = 300

        # assuming x0,y0 is really top left
        coord0_close = min(measure_dist(old_x0, old_y0, new_x0, new_y0), measure_dist(old_x0, old_y0, new_x1, new_y1)) < too_close
        coord1_close = min(measure_dist(old_x1, old_y1, new_x1, new_y1), measure_dist(old_x1, old_y1, new_x1, new_y1)) < too_close

        return coord0_close and coord1_close

    for coord in box_coords:
        '''Draw box'''

        to_add = True

        for old_coord in added_coords:
            # print(f'New:{coord}')
            # print(f'Old:{old_coord}')
            # print(close(coord, old_coord))
            if close(coord, old_coord):
                to_add = False
                break
        
        if to_add:
            x0, y0, x1, y1 = coord['x0'], coord['y0'], coord['x1'], coord['y1']
            img = cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 100), 3) # not sure which should be x which should be y
            img = cv2.putText(img, coord['class_name'], (x0, y0), 0, 2, (0, 0, 255), 3)
            added_coords.append(coord)

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

    number_of_images = 100 

    dicom_datas = retrieve_dicom_data(number_of_images, TRAIN_FILE)
    for i, dicom_datum in enumerate(dicom_datas):

        image_id = dicom_datum['image_id']
        
        # Opens the dicom file and reads the saved file
        dicom_path = join(TRAIN_FOLDER, image_id + '.dicom')
        img_og = read_xray(dicom_path)

        # Saves the xray as a png
        annotated_path = join(ANNOTATED_FOLDER, image_id + '.png')
        png_path = join(PNG_FOLDER, image_id + '.png')
        cv2.imwrite(annotated_path, img_og)
        cv2.imwrite(png_path, resize(img_og, 512))

        # Reads the saved png files
        img_saved = cv2.imread(annotated_path)
        print(f'Drawing boxes for {image_id}')
        img = draw_boxes(img_saved, dicom_datum['coords'])
        img = resize(img, 512)

        # Saves the images with boxes
        cv2.imwrite(annotated_path, img)
        upload_xray(png_path, annotated_path,
                    dicom_datum['coords'][0]['class_name'],
                    for_browse = (i % 2 == 0) )
        

def upload_xray(xray_path, annotated_path, condition, for_browse = True):
    filename = os.path.basename(xray_path)
    # print("Buckets:")
    # for bucket in buckets:
    #     print(bucket.name)
    # print("Listed all storage buckets.")

    original_blob = BUCKET.blob(ORIGINAL_PREFIX + filename)
    target_blob = BUCKET.blob((BROWSE_PREFIX if for_browse else LEARN_PREFIX) + filename)

    metadata = {'condition': condition}

    original_blob.upload_from_filename(xray_path)
    target_blob.upload_from_filename(annotated_path)

    original_blob = BUCKET.get_blob(ORIGINAL_PREFIX + filename)
    target_blob = BUCKET.get_blob((BROWSE_PREFIX if for_browse else LEARN_PREFIX) + filename)

    original_blob.metadata = metadata
    target_blob.metadata = metadata
    
    original_blob.patch()
    target_blob.patch()





if __name__ == '__main__':
    main()
