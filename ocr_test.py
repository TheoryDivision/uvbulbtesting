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
    
    sato_res = sato(im, mode='reflect')
    im_filt = img_as_ubyte(sato_res)
    val = threshold_otsu(im_filt)
    im_filt = img_as_ubyte(im_filt >= val)
    
    custom_config = r'-c tessedit_char_whitelist=0123456789. --psm 5 -l letsgodigital'
    res = pytesseract.image_to_string(im_filt, config=custom_config)
    
    return res
    
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
        
    # Tesseract
    text_res = get_text(local_im) 
    
    return text_res
    
if __name__=='__main__':
    tag = sys.argv[1]
    proc_res = process_im(tag)
    print(proc_res)
    
    