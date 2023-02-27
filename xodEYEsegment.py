# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEyeSegment.py))::__
#
# Python Image Segmentation Experiments
# required lib:
#
#
# Requirements
# python3-tk: sudo apt-get install python3-tk
# skimage: pip3 install scikit-image
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os
import sys
import numpy as np
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance
from scipy import ndimage as nd
import imageio as imio
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from skimage import data, img_as_float, img_as_ubyte
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.metrics import peak_signal_noise_ratio
from skimage.util import random_noise


currentDir = os.getcwd()
rootDir = os.path.dirname(currentDir)
dataDir = rootDir+'/data'
movDir = dataDir+'/src/mov'

sys.path.insert(0, rootDir+'/xodEYE')
import xodEYEutil as eyeutil

sys.path.insert(0, rootDir+'/xodUtil')
import xodPlotUtil as xodplt


# temp python debugger - use >>>pdb.set_trace() to set break
import pdb


# // *--------------------------------------------------------------* //

def segmentEYEhist(eyeSrc):
    """ estimate the noise standard deviation from the noisy image
        sigma_est = np.mean(estimate_sigma(noisy, multichannel=True))
        // multichannel depricated -> channel_axis
    """

    sigma_est = np.mean(estimate_sigma(eyeSrc, channel_axis=-1))
    print("estimated noise standard deviation = {}".format(sigma_est))

    patch_kw = dict(patch_size=5,  # 5x5 patches
                    patch_distance=6,  # 13x13 search area
                    channel_axis=-1)  # (changed from multichannel=True)

    # Denoise Cut-off Distance - higher value = more blurring
    # blurThresh = 0.15
    blurThresh = 1.15

    denoise = denoise_nl_means(eyeSrc, h=blurThresh * sigma_est, fast_mode=True, **patch_kw)
    denoise_ubyte = img_as_ubyte(denoise)
    denoise_gray = eyeutil.grayConversion(denoise_ubyte)

    segm1 = (denoise_gray <= 75)
    segm2 = (denoise_gray > 75) & (denoise_gray <= 150)
    segm3 = (denoise_gray > 150) & (denoise_gray <= 225)
    segm4 = (denoise_gray > 225)

    # all_segments = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))
    #
    # all_segments[segm1] = (1, 0, 0)
    # all_segments[segm2] = (0, 1, 0)
    # all_segments[segm3] = (0, 0, 1)
    # all_segments[segm4] = (1, 1, 0)

    segm1_opened = nd.binary_opening(segm1, np.ones((3, 3)))
    segm1_closed = nd.binary_closing(segm1_opened, np.ones((3, 3)))

    segm2_opened = nd.binary_opening(segm2, np.ones((3, 3)))
    segm2_closed = nd.binary_closing(segm2_opened, np.ones((3, 3)))

    segm3_opened = nd.binary_opening(segm3, np.ones((3, 3)))
    segm3_closed = nd.binary_closing(segm3_opened, np.ones((3, 3)))

    segm4_opened = nd.binary_opening(segm4, np.ones((3, 3)))
    segm4_closed = nd.binary_closing(segm4_opened, np.ones((3, 3)))

    all_segments_clean = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))

    all_segments_clean[segm1_closed] = (0.86, 0, 0)
    all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
    all_segments_clean[segm3_closed] = (0.86, 1, 0.0)
    all_segments_clean[segm4_closed] = (0, 0, 0.2)

    eyeRes = all_segments_clean

    return eyeRes


def segmentEYEhistPlot(eyeSrc):
    """ estimate the noise standard deviation from the noisy image
        sigma_est = np.mean(estimate_sigma(noisy, multichannel=True))
        // multichannel depricated -> channel_axis
    """

    sigma_est = np.mean(estimate_sigma(eyeSrc, channel_axis=-1))
    print("estimated noise standard deviation = {}".format(sigma_est))

    patch_kw = dict(patch_size=5,  # 5x5 patches
                    patch_distance=6,  # 13x13 search area
                    channel_axis=-1)  # (changed from multichannel=True)

    # Denoise Cut-off Distance - higher value = more blurring
    # blurThresh = 0.15
    blurThresh = 1.15

    denoise = denoise_nl_means(eyeSrc, h=blurThresh * sigma_est, fast_mode=True, **patch_kw)
    denoise_ubyte = img_as_ubyte(denoise)
    denoise_gray = eyeutil.grayConversion(denoise_ubyte)

    segm1 = (denoise_gray <= 75)
    segm2 = (denoise_gray > 75) & (denoise_gray <= 150)
    segm3 = (denoise_gray > 150) & (denoise_gray <= 225)
    segm4 = (denoise_gray > 225)

    # all_segments = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))
    #
    # all_segments[segm1] = (1, 0, 0)
    # all_segments[segm2] = (0, 1, 0)
    # all_segments[segm3] = (0, 0, 1)
    # all_segments[segm4] = (1, 1, 0)

    segm1_opened = nd.binary_opening(segm1, np.ones((3, 3)))
    segm1_closed = nd.binary_closing(segm1_opened, np.ones((3, 3)))

    segm2_opened = nd.binary_opening(segm2, np.ones((3, 3)))
    segm2_closed = nd.binary_closing(segm2_opened, np.ones((3, 3)))

    segm3_opened = nd.binary_opening(segm3, np.ones((3, 3)))
    segm3_closed = nd.binary_closing(segm3_opened, np.ones((3, 3)))

    segm4_opened = nd.binary_opening(segm4, np.ones((3, 3)))
    segm4_closed = nd.binary_closing(segm4_opened, np.ones((3, 3)))

    all_segments_clean = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))

    all_segments_clean[segm1_closed] = (0.86, 0, 0)
    all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
    all_segments_clean[segm3_closed] = (0.86, 1, 0.0)
    all_segments_clean[segm4_closed] = (0, 0, 0.2)

    # PLOTTING:

    plt.figure(5)
    plt.hist(denoise_gray.flat, bins=100, range=(0, 225))

    # plt.figure(3)
    # plt.imshow(all_segments)

    plt.figure(4)
    plt.imshow(all_segments_clean)
    # set_title('Trunkjuice Image Segmentator')

    # fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(12, 5), sharex=True, sharey=True)
    # ax1[0].imshow(eye01)
    # ax1[0].axis('off')
    # ax1[0].set_title('Image Source')
    # ax1[1].imshow(denoise)
    # ax1[1].axis('off')
    # ax1[1].set_title('Image Denoise')
    # fig1.tight_layout()

    fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(12, 5), sharex=True, sharey=True)
    ax2[0].imshow(eye01, cmap='gray', vmin=0, vmax=255)
    ax2[0].axis('off')
    ax2[0].set_title('Img Src')
    ax2[1].imshow(denoise_gray, cmap='gray', vmin=0, vmax=255)
    ax2[1].axis('off')
    ax2[1].set_title('Img Gray Denoise')
    fig2.tight_layout()

    # print PSNR metric for each case
    psnr = peak_signal_noise_ratio(eye01, denoise)
    print(f'PSNR (slow) = {psnr:0.2f}')

    plt.show()

    return

# // *--------------------------------------------------------------* //


def segmentEYEmask(eyeSrc, imgArr):
    """ estimate the noise standard deviation from the noisy image
        sigma_est = np.mean(estimate_sigma(noisy, multichannel=True))
        // multichannel depricated -> channel_axis
    """

    sigma_est = np.mean(estimate_sigma(eyeSrc, channel_axis=-1))
    print("estimated noise standard deviation = {}".format(sigma_est))

    patch_kw = dict(patch_size=5,  # 5x5 patches
                    patch_distance=6,  # 13x13 search area
                    channel_axis=-1)  # (changed from multichannel=True)

    # Denoise Cut-off Distance - higher value = more blurring
    # blurThresh = 0.15
    blurThresh = 1.15

    denoise = denoise_nl_means(eyeSrc, h=blurThresh * sigma_est, fast_mode=True, **patch_kw)
    denoise_ubyte = img_as_ubyte(denoise)
    denoise_gray = eyeutil.grayConversion(denoise_ubyte)

    segm1 = (denoise_gray <= 75)
    segm2 = (denoise_gray > 75) & (denoise_gray <= 150)
    segm3 = (denoise_gray > 150) & (denoise_gray <= 225)
    segm4 = (denoise_gray > 225)

    # all_segments = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))
    #
    # all_segments[segm1] = (1, 0, 0)
    # all_segments[segm2] = (0, 1, 0)
    # all_segments[segm3] = (0, 0, 1)
    # all_segments[segm4] = (1, 1, 0)

    segm1_opened = nd.binary_opening(segm1, np.ones((3, 3)))
    segm1_closed = nd.binary_closing(segm1_opened, np.ones((3, 3)))

    segm2_opened = nd.binary_opening(segm2, np.ones((3, 3)))
    segm2_closed = nd.binary_closing(segm2_opened, np.ones((3, 3)))

    segm3_opened = nd.binary_opening(segm3, np.ones((3, 3)))
    segm3_closed = nd.binary_closing(segm3_opened, np.ones((3, 3)))

    segm4_opened = nd.binary_opening(segm4, np.ones((3, 3)))
    segm4_closed = nd.binary_closing(segm4_opened, np.ones((3, 3)))

    all_segments_clean = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))

    # all_segments_clean[segm1_closed] = (0.86, 0, 0)
    # all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
    # all_segments_clean[segm3_closed] = (0.86, 1, 0.0)

    all_segments_clean[segm1_closed] = (0.86, 0, 0)
    all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
    all_segments_clean[segm3_closed] = (0.86, 1, 0.0)
    all_segments_clean[segm4_closed] = (0, 0, 0.2)

    eyeRes = all_segments_clean



    return eyeRes


if 0:
    # debug..
    # astro = img_as_float(data.astronaut())
    # astro = astro[30:280, 150:400]

    #sigma = 0.08
    #noisy = random_noise(eye01, var=sigma**2)

    # Import Images:
    # guumon_paulkaiju_sparkman_480x270.png
    # guumon_paulkaiju_sparkinvert_480x270.png
    # iguana_1920x1080.png

    # eye01 = imio.imread("/home/eschei/xodmk/xodPython/data/src/eye/guumon_paulkaiju_sparkman_480x270.png")
    # eye01 = imio.imread("/home/eschei/xodmk/xodPython/data/src/eye/iguana_1920x1080.png")
    eye01 = imio.imread(movDir + "/spiceIndicator1080/spiceIndicatorGnk000139.jpg")

    segmentEYEhistPlot(eye01)
