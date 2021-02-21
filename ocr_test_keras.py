#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import numpy as np
import skimage
from skimage import io
from skimage import exposure
from skimage.filters import threshold_otsu, sato, sobel
from skimage.filters.rank import otsu
from skimage.morphology import closing, white_tophat, erosion, dilation, opening
from skimage.morphology import black_tophat, square, disk
from skimage.feature import canny
from skimage.util import img_as_ubyte
from skimage.color import grey2rgb
from scipy import ndimage as ndi
import imutils
import cv2
import pytesseract
import keras_ocr


def check_rang(x_rang=None, y_rang=None, x_slice=None, y_slice=None):
    x_res = (x_rang[x_slice][0] < np.percentile(x_rang, 1, interpolation='midpoint')) | (np.flip(x_rang[x_slice])[0] > np.percentile(x_rang, 99, interpolation='midpoint'))
    y_res = (y_rang[y_slice][0] < np.percentile(y_rang, 1, interpolation='midpoint')) | (np.flip(y_rang[y_slice])[0] > np.percentile(y_rang, 99, interpolation='midpoint'))
    
    return np.logical_not(x_res | y_res)


def crop_med(im=None, im_obj=None):
    
    x_rang = np.arange(0, im.shape[0])
    y_rang = np.arange(0, im.shape[1])
    idx = [check_rang(x_rang, y_rang, im_obj[i][0], im_obj[i][1]) for i in range(len(im_obj))]
    if np.count_nonzero(idx) == 0:
        print("No median object region detected!")
        
    elif np.count_nonzero(idx) > 1:
        print(">1 median object region detected!")
    
    x_rang = x_rang[im_obj[np.where(idx)[0].item()][0]]
    y_rang = y_rang[im_obj[np.where(idx)[0].item()][1]]
    im = im[im_obj[np.where(idx)[0].item()][0],im_obj[np.where(idx)[0].item()][1]]
    
    return im

def crop_extr(im=None, im_obj=None):
    x_rang = np.arange(0, im.shape[0])
    y_rang = np.arange(0, im.shape[1])
    idx = [check_rang(x_rang, y_rang, im_obj[i][0], im_obj[i][1]) for i in range(len(im_obj))]
    if np.count_nonzero(idx) == 0:
        print("No median object region detected!")
    elif np.count_nonzero(idx) > 1:
        print(">1 median object region detected!")
    
    x_rang = x_rang[im_obj[np.where(idx)[0].item()][0]]
    y_rang = y_rang[im_obj[np.where(idx)[0].item()][1]]
    im = im[im_obj[np.where(idx)[0].item()][0],im_obj[np.where(idx)[0].item()][1]]
    
    return im
    

def crop_med_v(im=None):
    x_rang = np.arange(0, im.shape[0])
    y_rang = np.arange(0, im.shape[1])
    x_rang = slice(int(np.percentile(x_rang, 25, interpolation='midpoint')), 
                   int(np.percentile(x_rang, 75, interpolation='midpoint')), 1)
    y_rang = slice(int(np.percentile(y_rang, 10, interpolation='midpoint')), 
                   int(np.percentile(y_rang, 90, interpolation='midpoint')), 1)

    im = im[x_rang, y_rang]
    
    return im

    
def map_obj(im=None):
    """
    Identify rectangular dark region using morphological closing
    Remove noise using global OTSU
    Identify objects
    Select only object that corresponds to screen of device (around middle of image)
    """
    
    im_b = img_as_ubyte(closing(im, square(125)))
    val = threshold_otsu(im_b)
    local_mask = np.zeros_like(im_b)
    local_mask[im_b < val] = 1
    im_b_l = ndi.label(local_mask)
    im_b_obj = ndi.find_objects(im_b_l[0])
    c_mass = ndi.center_of_mass(local_mask, im_b_l[0], index=np.arange(im_b_l[1])+1)
    im_crop = crop_extr(im=im, im_obj=im_b_obj)
    
    return skimage.exposure.equalize_adapthist(im_crop)
    

def exp_corr(im=None):
    """
    Correct exposure using CLAHE
    """
    im = skimage.exposure.equalize_adapthist(im)
    
    return im


def get_text(im=None):
    """
    Extract digits using tesseract
    """
    
    #val = threshold_otsu(im)
    #im_filt = img_as_ubyte(im >= val)
    
    custom_config = r'-c tessedit_char_whitelist=.0123456789 --psm 7 -l letsgodigital'
    res = pytesseract.image_to_string(img_as_ubyte(exp_corr(im)), config=custom_config)
    
    return res
    

def get_reg(im=None, coor=None):
    y_min = int(np.floor(np.min(coor[::,0])))
    y_max = int(np.ceil(np.max(coor[::,0])))
    x_min = int(np.floor(np.min(coor[::,1])))
    x_max = int(np.ceil(np.max(coor[::,1])))
    temp = im[slice(x_min, x_max, 1), slice(y_min, y_max, 1)]
    
    return temp
    
    
def filt_groups(x=None):
    
    filt = []
    for i in range(len(x)):
        temp = x[i][0].lower()
        if (temp != 'unit') & (temp != 'c') & (not temp.startswith('m')):
            filt.append(x[i])
            
    return filt[len(filt)-1][1]
    
    
def process_im(tag=None):
    """ 
    Exposure correct and map rectangular object ~ median region
    Arbitrary shape size - suboptimal
    Extract Text
    """
    
    # Correct
    im = io.imread(tag, as_gray=True)
    local_im = exp_corr(crop_med_v(im))
    
    # Map object
    local_im = map_obj(local_im)
        
    # Keras-OCR
    pipeline = keras_ocr.pipeline.Pipeline()
    prediction_groups = pipeline.recognize([grey2rgb(img_as_ubyte(exp_corr(local_im)))])
    
    #fig, axs = plt.subplots(1, 1, figsize=(6, 6))
    #keras_ocr.tools.drawAnnotations(image=grey2rgb(img_as_ubyte(exp_corr(local_im))), predictions=prediction_groups[0], ax=axs)
    
    temp_coord = filt_groups(prediction_groups[0])
    local_im = get_reg(im=local_im, coor=temp_coord)
    
    
    # Tesseract
    text_res = get_text(local_im) 
    
    return text_res
    
if __name__=='__main__':
    tag = sys.argv[1]
    proc_res = process_im(tag)
    print("Image\t{}\t{}".format(tag, proc_res))
    
    
