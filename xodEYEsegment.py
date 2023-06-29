# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodSegment.py))::__
#
# Python Image Segmentation Experiments
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
# from PIL import Image
# from PIL import ImageOps
# from PIL import ImageEnhance
from scipy import ndimage as nd
# import imageio as imio
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from skimage import data, img_as_float, img_as_ubyte
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.metrics import peak_signal_noise_ratio
from skimage.exposure import histogram
# from skimage.util import random_noise


currentDir = os.getcwd()
rootDir = os.path.dirname(currentDir)
dataDir = rootDir+'/data'
movDir = dataDir+'/src/mov'

sys.path.insert(0, rootDir+'/xodma')
from xodmaSpectralTools import peak_pick

sys.path.insert(1, rootDir+'/xodEYE')
import xodEYEutil as eyeutil

sys.path.insert(2, rootDir+'/xodUtil')
import xodPlotUtil as xodplt


# temp python debugger - use >>>pdb.set_trace() to set break
import pdb

# // *--------------------------------------------------------------* //


def xodmaPeaks(wavIn, sr, hop, peakThresh, peakWait, **kwargs):
    """
    Wrapper for XODMA peak_pick function (modified clone of librosa func)
    wavIn      - input 1D time domain signal (audio, signal, envelope, etc.)
    sr         - sample rate (normalized for STFT 48KHz audio)
    hop        - STFT Hop length (normalized for hop length 256 (?!))
    peakThresh - ignore peaks below certain threshold
    peakWait   - wait to ensure peoks are adequately spaced
    # Example:
    # Matches - peaks = peak_pick(onset_env, 7, 7, 7, 7, 0.5, 5)  # -> default librosa params
    # >> peakThresh = 0.5
    # >> peakWait = 0.002674
    """

    kwargs.setdefault('pre_max', 0.04 * sr // hop)      # 7.0
    kwargs.setdefault('post_max', 0.04 * sr // hop)     # 7.0
    kwargs.setdefault('pre_avg', 0.04 * sr // hop)      # 7.0
    kwargs.setdefault('post_avg', 0.04 * sr // hop)     # 7.0
    kwargs.setdefault('wait', peakWait * sr // hop)  # 30ms
    kwargs.setdefault('delta', peakThresh)

    peaks = peak_pick(wavIn, **kwargs)

    return peaks


# // *--------------------------------------------------------------* //

def segmentEYEhistFixed(eyeSrc):
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

# // *--------------------------------------------------------------* //


def segmentEYEhist(eyeSrc):
    """ estimate the noise standard deviation from the noisy image
        sigma_est = np.mean(estimate_sigma(noisy, multichannel=True))
        // multichannel depricated -> channel_axis
    """

    numSegments = 4

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

    # // *--------------------------------------------------------------* //
    # exp : compute histogram, find peaks in hist => major clusters of pixel data
    hist, hist_centers = histogram(denoise_gray, nbins=256)

    # peaks_xodma = peak_pick(onset_envelope, 7, 7, 7, 7, 0.5, 5)
    # peaks_hist = peak_pick(hist[0:225], 7, 7, 7, 7, 0.5, 5)

    # Matches: peaks = peak_pick(onset_env, 7, 7, 7, 7, 0.5, 5)
    sr = 48000  # (sample rate only used to force parameter values)
    hop = 256   # (only used to force parameter values)
    peakThresh = 23     # ? arbitrary - ignore peaks below certain threshold
    peakWait = 0.002674
    # peaks_hist = xodmaPeaks(hist[0:225], sr, hop, peakThresh, peakWait)
    peaks_hist = xodmaPeaks(hist, sr, hop, peakThresh, peakWait)
    peakVal = hist[peaks_hist]

    print("peaks_hist = " + str(peaks_hist))
    print("peakVal = " + str(peakVal))

    # peaks_hist should provide more peaks than actual segments
    # use largest peaks to define segment regions (required peaks = numSegments - 1)
    # select largest peaks, sort in accending order & save locations
    maxPeakSorted = sorted(zip(peakVal, peaks_hist), reverse=True)[:numSegments - 1]
    maxPeakValsList, maxPeaksList = zip(*maxPeakSorted)
    maxPeaks = np.array(sorted(maxPeaksList))
    maxPeakVals = np.array(sorted(maxPeakValsList))

    print("Max Peak Locations" + str(maxPeaks))
    print("Max Peak Values" + str(maxPeakVals))

    # pdb.set_trace()

    # // *--------------------------------------------------------------* //

    # segm1 = (denoise_gray <= maxPeaks[0])
    # segm2 = (denoise_gray > maxPeaks[0]) & (denoise_gray <= maxPeaks[1])
    # segm3 = (denoise_gray > maxPeaks[1]) & (denoise_gray <= 225)
    # segm4 = (denoise_gray > 225)

    # divide segments into regions containing max peaks from pixel histogram
    segm1 = (denoise_gray <= int(maxPeaks[0] - maxPeaks[0] / 8))
    segm2 = (denoise_gray > int(maxPeaks[0] - maxPeaks[0] / 8)) & \
            (denoise_gray <= int(maxPeaks[1] - (maxPeaks[1] - maxPeaks[0]) / 2))
    segm3 = (denoise_gray > int(maxPeaks[1] - (maxPeaks[1] - maxPeaks[0]) / 2)) & \
            (denoise_gray <= int(maxPeaks[2] - (maxPeaks[2] - maxPeaks[1]) / 2))
    segm4 = (denoise_gray > int(maxPeaks[2] - (maxPeaks[2] - maxPeaks[1]) / 2))

    # pdb.set_trace()

    # segm1 = (denoise_gray <= 75)
    # segm2 = (denoise_gray > 75) & (denoise_gray <= 150)
    # segm3 = (denoise_gray > 150) & (denoise_gray <= 225)
    # segm4 = (denoise_gray > 225)

    # // *--------------------------------------------------------------* //
    # // *--- perform opening/closing to remove edge noise ---*

    segm1_opened = nd.binary_opening(segm1, np.ones((3, 3)))
    segm1_closed = nd.binary_closing(segm1_opened, np.ones((3, 3)))

    segm2_opened = nd.binary_opening(segm2, np.ones((3, 3)))
    segm2_closed = nd.binary_closing(segm2_opened, np.ones((3, 3)))

    segm3_opened = nd.binary_opening(segm3, np.ones((3, 3)))
    segm3_closed = nd.binary_closing(segm3_opened, np.ones((3, 3)))

    segm4_opened = nd.binary_opening(segm4, np.ones((3, 3)))
    segm4_closed = nd.binary_closing(segm4_opened, np.ones((3, 3)))

    all_segments_clean = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))

    # assign arbitrary colors for segments...
    all_segments_clean[segm1_closed] = (0.86, 0, 0)
    all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
    all_segments_clean[segm3_closed] = (0.86, 1, 0.0)
    all_segments_clean[segm4_closed] = (0, 0, 0.2)

    eyeRes = all_segments_clean

    # Debug / Inspection: Plot intermediate & final results
    if 0:

        # // *--------------------------------------------------------------* //
        # PLOTTING:

        fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(12, 5), sharex=True, sharey=True)
        ax2[0].imshow(eyeSrc, cmap='gray', vmin=0, vmax=255)
        ax2[0].axis('off')
        ax2[0].set_title('Img Src')
        ax2[1].imshow(denoise_gray, cmap='gray', vmin=0, vmax=255)
        ax2[1].axis('off')
        ax2[1].set_title('Img Gray Denoise')
        fig2.tight_layout()

        # plt.figure(3)
        # plt.imshow(all_segments)

        plt.figure(4)
        plt.plot(hist[0:225])   # remove white background pixels for plot view
        plt.title('Img Grayscale Histogram[0:225]')
        plt.xlabel('pixel bin # [0:225]')

        # N = len(hist[0:225])
        N = len(hist)
        t = np.linspace(0, N, N)

        plt.figure(5)
        # plt.plot(t, hist[0:225])
        plt.plot(t, hist)
        plt.grid(False)
        # plt.vlines(t[maxPeaks], 0, hist[0:225].max(), color='r', alpha=0.7)
        plt.vlines(t[maxPeaks], 0, hist.max(), color='r', alpha=0.7)
        plt.title('peaks_hist')
        plt.xlabel('Pixel Bins [0:225]')
        plt.xlim(0, N)
        plt.ylim(0)

        plt.figure(6)
        plt.hist(denoise_gray.flat, bins=100, range=(0, 225))

        plt.figure(7)
        plt.imshow(all_segments_clean)
        plt.title('Trunkjuice Image Segmentator')

        # print PSNR metric for each case
        psnr = peak_signal_noise_ratio(eyeSrc, denoise)
        print(f'PSNR (slow) = {psnr:0.2f}')

        # plt.show()

    return eyeRes

# // *--------------------------------------------------------------* //


def segmentEYEmask_FourSg(eyeSrc, imgArr):
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
    # blurThresh = 3.15

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

    colors = 0
    if colors == 1:

        all_segments_clean[segm1_closed] = (0.86, 0, 0)
        all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
        all_segments_clean[segm3_closed] = (0.86, 1, 0.0)
        all_segments_clean[segm4_closed] = (0, 0, 0.2)

    else:

        maskEyeSrc1 = imgArr[0]
        maskEyeSrc2 = imgArr[1]
        maskEyeSrc3 = imgArr[2]
        maskEyeSrc4 = imgArr[3]
        # fill segment with src channel data of same positions
        all_segments_clean[segm1_closed] = maskEyeSrc1[segm1_closed]        # (0.86, 0, 0)
        all_segments_clean[segm2_closed] = maskEyeSrc2[segm2_closed]        # (0, 0.86, 0.86)
        all_segments_clean[segm3_closed] = maskEyeSrc3[segm3_closed]        # (0.86, 1, 0.0)
        all_segments_clean[segm4_closed] = maskEyeSrc4[segm4_closed]        # (0, 0, 0.2)

        # all_segments_clean = eyeutil.median_filter_rgb(all_segments_clean, 13)

    eyeRes = all_segments_clean

    # // *--------------------------------------------------------------* //
    # exp
    # all_segments_mask = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))
    # for row, pxl in enumerate(pxls):
    #     for col, pxll in enumerate(pxl):
    #         all_segments_clean
    # // *--------------------------------------------------------------* //

    return eyeRes


def segmentEYEmaskFour(maskSrc, eyeSrcArray):
    """ estimate the noise standard deviation from the noisy image
        sigma_est = np.mean(estimate_sigma(noisy, multichannel=True))
        // multichannel depricated -> channel_axis
        maskSrc: np.array (2D image array)
        eyeSrcArray: 4 element array of np.array (4 x 2D image array)
    """

    numSegments = 4
    sigma_est = np.mean(estimate_sigma(maskSrc, channel_axis=-1))
    # print("estimated noise standard deviation = {}".format(sigma_est))

    patch_kw = dict(patch_size=5,  # 5x5 patches
                    patch_distance=6,  # 13x13 search area
                    channel_axis=-1)  # (changed from multichannel=True)

    # Denoise Cut-off Distance - higher value = more blurring
    # blurThresh = 0.15
    blurThresh = 1.15

    denoise = denoise_nl_means(maskSrc, h=blurThresh * sigma_est, fast_mode=True, **patch_kw)
    denoise_ubyte = img_as_ubyte(denoise)
    denoise_gray_raw = eyeutil.grayConversion(denoise_ubyte)

    denoise_gray = eyeutil.median_filter_gray(denoise_gray_raw, 11)

    # // *--------------------------------------------------------------* //
    # exp : compute histogram, find peaks in hist => major clusters of pixel data
    hist, hist_centers = histogram(denoise_gray, nbins=256)

    # peaks_xodma = peak_pick(onset_envelope, 7, 7, 7, 7, 0.5, 5)
    # peaks_hist = peak_pick(hist[0:225], 7, 7, 7, 7, 0.5, 5)

    # Matches: peaks = peak_pick(onset_env, 7, 7, 7, 7, 0.5, 5)
    sr = 48000  # (sample rate only used to force parameter values)
    hop = 256   # (only used to force parameter values)
    peakThresh = 23     # ? arbitrary - ignore peaks below certain threshold
    peakWait = 0.002674
    # peaks_hist = xodmaPeaks(hist[0:225], sr, hop, peakThresh, peakWait)
    peaks_hist = xodmaPeaks(hist, sr, hop, peakThresh, peakWait)

    # ** if peaks_hist < 3, need to insert a false peak to prevent error
    if len(peaks_hist) == 2:
        peaks_hist = np.insert(peaks_hist, 1, (peaks_hist[1] - peaks_hist[0]) // 2)
    if len(peaks_hist) == 1:
        peaks_hist = np.insert(peaks_hist, 0, peaks_hist[0] // 2)
        peaks_hist = np.insert(peaks_hist, 2, (len(hist) - peaks_hist[1]) // 2)
    if len(peaks_hist) == 0:
        peaks_hist = np.array([len(hist) // 4, 2 * (len(hist) // 4), 3 * (len(hist) // 4)])

    peakVal = hist[peaks_hist]

    # print("length of hist = " + str(len(hist)))
    # print("peaks_hist = " + str(peaks_hist))
    # print("peakVal = " + str(peakVal))

    # peaks_hist should provide more peaks than actual segments
    # use largest peaks to define segment regions (required peaks = numSegments - 1)
    # select largest peaks, sort in accending order & save locations
    maxPeakSorted = sorted(zip(peakVal, peaks_hist), reverse=True)[:numSegments - 1]
    maxPeakValsList, maxPeaksList = zip(*maxPeakSorted)
    maxPeaks = np.array(sorted(maxPeaksList))
    # maxPeakVals = np.array(sorted(maxPeakValsList))   # currently not used

    # print("Max Peak Locations" + str(maxPeaks))
    # print("Max Peak Values" + str(maxPeakVals))
    # print("peaks_hist" + str(peaks_hist) + ",    Max Peak Locations" + str(maxPeaks))

    # pdb.set_trace()

    # // *--------------------------------------------------------------* //

    # segm1 = (denoise_gray <= maxPeaks[0])
    # segm2 = (denoise_gray > maxPeaks[0]) & (denoise_gray <= maxPeaks[1])
    # segm3 = (denoise_gray > maxPeaks[1]) & (denoise_gray <= 225)
    # segm4 = (denoise_gray > 225)

    # divide segments into regions containing max peaks from pixel histogram
    segm1 = (denoise_gray <= int(maxPeaks[0] - maxPeaks[0] / 8))
    segm2 = (denoise_gray > int(maxPeaks[0] - maxPeaks[0] / 8)) & \
            (denoise_gray <= int(maxPeaks[1] - (maxPeaks[1] - maxPeaks[0]) / 2))
    segm3 = (denoise_gray > int(maxPeaks[1] - (maxPeaks[1] - maxPeaks[0]) / 2)) & \
            (denoise_gray <= int(maxPeaks[2] - (maxPeaks[2] - maxPeaks[1]) / 2))
    segm4 = (denoise_gray > int(maxPeaks[2] - (maxPeaks[2] - maxPeaks[1]) / 2))

    # pdb.set_trace()

    # // *--------------------------------------------------------------* //
    # // *--- perform opening/closing to remove edge noise ---*

    segm1_opened = nd.binary_opening(segm1, np.ones((3, 3)))
    segm1_closed = nd.binary_closing(segm1_opened, np.ones((3, 3)))

    segm2_opened = nd.binary_opening(segm2, np.ones((3, 3)))
    segm2_closed = nd.binary_closing(segm2_opened, np.ones((3, 3)))

    segm3_opened = nd.binary_opening(segm3, np.ones((3, 3)))
    segm3_closed = nd.binary_closing(segm3_opened, np.ones((3, 3)))

    segm4_opened = nd.binary_opening(segm4, np.ones((3, 3)))
    segm4_closed = nd.binary_closing(segm4_opened, np.ones((3, 3)))

    all_segments_clean = np.zeros((denoise_gray.shape[0], denoise_gray.shape[1], 3))

    colors = 0
    if colors == 1:
        # assign arbitrary colors for segments...
        all_segments_clean[segm1_closed] = (0.86, 0, 0)
        all_segments_clean[segm2_closed] = (0, 0.86, 0.86)
        all_segments_clean[segm3_closed] = (0.86, 1, 0.0)
        all_segments_clean[segm4_closed] = (0, 0, 0.2)

    else:
        maskEyeSrc1 = eyeSrcArray[0]
        maskEyeSrc2 = eyeSrcArray[1]
        maskEyeSrc3 = eyeSrcArray[2]
        maskEyeSrc4 = eyeSrcArray[3]
        # fill segment with src channel data of same positions
        all_segments_clean[segm1_closed] = maskEyeSrc1[segm1_closed]        # (0.86, 0, 0)
        all_segments_clean[segm2_closed] = maskEyeSrc2[segm2_closed]        # (0, 0.86, 0.86)
        all_segments_clean[segm3_closed] = maskEyeSrc3[segm3_closed]        # (0.86, 1, 0.0)
        all_segments_clean[segm4_closed] = maskEyeSrc4[segm4_closed]        # (0, 0, 0.2)

    eyeRes = all_segments_clean.astype("uint8")

    # Debug / Inspection: Plot intermediate & final results
    if 0:

        # // *--------------------------------------------------------------* //
        # PLOTTING:

        fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(12, 5), sharex=True, sharey=True)
        ax2[0].imshow(maskSrc, cmap='gray', vmin=0, vmax=255)
        ax2[0].axis('off')
        ax2[0].set_title('Img Src')
        ax2[1].imshow(denoise_gray, cmap='gray', vmin=0, vmax=255)
        ax2[1].axis('off')
        ax2[1].set_title('Img Gray Denoise')
        fig2.tight_layout()

        # plt.figure(3)
        # plt.imshow(all_segments)

        plt.figure(4)
        plt.plot(hist[0:225])   # remove white background pixels for plot view
        plt.title('Img Grayscale Histogram[0:225]')
        plt.xlabel('pixel bin # [0:225]')

        # N = len(hist[0:225])
        N = len(hist)
        t = np.linspace(0, N, N)

        plt.figure(5)
        # plt.plot(t, hist[0:225])
        plt.plot(t, hist)
        plt.grid(False)
        # plt.vlines(t[maxPeaks], 0, hist[0:225].max(), color='r', alpha=0.7)
        plt.vlines(t[maxPeaks], 0, hist.max(), color='r', alpha=0.7)
        plt.title('peaks_hist')
        plt.xlabel('Pixel Bins [0:225]')
        plt.xlim(0, N)
        plt.ylim(0)

        plt.figure(6)
        plt.hist(denoise_gray.flat, bins=100, range=(0, 225))

        plt.figure(7)
        plt.imshow(all_segments_clean)
        plt.title('Trunkjuice Image Segmentator')

        # print PSNR metric for each case
        psnr = peak_signal_noise_ratio(maskSrc, denoise)
        print(f'PSNR (slow) = {psnr:0.2f}')

        # plt.show()

    return eyeRes

# // *--------------------------------------------------------------* //


# // *--------------------------------------------------------------* //
# // *---- Plotting Functions -----* //

def plotEyeSegmentRes(eyeSrc, eyeRes):

    # // *--------------------------------------------------------------* //
    # PLOTTING:

    fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(12, 5), sharex=True, sharey=True)
    ax2[0].imshow(eyeSrc, cmap='gray', vmin=0, vmax=255)
    ax2[0].axis('off')
    ax2[0].set_title('Img Src')
    ax2[1].imshow(eyeRes, cmap='gray', vmin=0, vmax=255)
    ax2[1].axis('off')
    ax2[1].set_title('Eye Segmented Result')
    fig2.tight_layout()

    plt.figure(3)
    plt.imshow(eyeRes)
    plt.title('Trunkjuice Image Segmentator')

    # plt.show()

    return
