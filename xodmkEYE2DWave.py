# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header begin-----------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

# __::((xodmkEYE2DWave.py))::__

# Python ODMK img processing research
# ffmpeg experimental


# // *** 2D Harmonics Basic - Blend LightSource / Shade imgaes

# https://docs.scipy.org/doc/scipy-0.18.1/reference/ndimage.html
# https://docs.scipy.org/doc/scipy-0.18.1/reference/tutorial/ndimage.html

# http://www.pythonware.com/media/data/pil-handbook.pdf


# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header end-------------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os, sys
import glob, shutil
from math import atan2, floor, ceil
import random
import numpy as np
import scipy as sp
from scipy import ndimage
from scipy import misc

from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance

import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

rootDir = 'C:\\odmkDev\\odmkCode\\odmkPython\\'
audioScrDir = 'C:\\odmkDev\\odmkCode\\odmkPython\\audio\\wavsrc\\'
audioOutDir = 'C:\\odmkDev\\odmkCode\\odmkPython\\audio\\wavout\\'


sys.path.insert(0, rootDir+'util')
import xodPlotUtil as xodplt


#sys.path.insert(1, 'C:/odmkDev/odmkCode/odmkPython/DSP')
sys.path.insert(2, rootDir+'DSP')
import odmkClocks as clks
import odmkSigGen1 as sigGen



# temp python debugger - use >>>pdb.set_trace() to set break
import pdb



# // *---------------------------------------------------------------------* //

plt.close('all')


# // *---------------------------------------------------------------------* //

# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : function definitions
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# -----------------------------------------------------------------------------
# utility func
# -----------------------------------------------------------------------------

def cyclicZn(n):
    ''' calculates the Zn roots of unity '''
    cZn = np.zeros((n, 1))*(0+0j)    # column vector of zero complex values
    for k in range(n):
        # z(k) = e^(((k)*2*pi*1j)/n)        # Define cyclic group Zn points
        cZn[k] = np.cos(((k)*2*np.pi)/n) + np.sin(((k)*2*np.pi)/n)*1j   # Euler's identity

    return cZn


def quarterCos(n):
    ''' returns a quarter period cosine wav of length n '''
    t = np.linspace(0, np.pi/4, n)
    qtrcos = np.zeros((n))
    for j in range(n):
        qtrcos[j] = sp.cos(t[j])
    return qtrcos


def randomIdx(k):
    '''returns a random index in range 0 - k-1'''
    randIdx = round(random.random()*(k-1))
    return randIdx

def randomIdxArray(n, k):
    '''for an array of k elements, returns a list of random elements
       of length n (n integers rangin from 0:k-1)'''
    randIdxArray = []
    for i in range(n):
        randIdxArray.append(round(random.random()*(k-1)))
    return randIdxArray
      
def randomPxlLoc(SzX, SzY):
    '''Returns a random location in a 2D array of SzX by SzY'''
    randPxlLoc = np.zeros(2)
    randPxlLoc[0] = int(round(random.random()*(SzX-1)))
    randPxlLoc[1] = int(round(random.random()*(SzY-1)))
    return randPxlLoc


class odmkWeightRnd:
    def __init__(self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items():
            self.__max += weight
            self.__weights.append((self.__max, value))

    def random(self):
        r = random.random() * self.__max
        for wtceil, value in self.__weights:
            if wtceil > r:
                return value

# a random 0 or 1
# rndIdx = round(random.random())
# -----------------------------------------------------------------------------
# color func ?????
# -----------------------------------------------------------------------------

def rgb_to_hsv(rgb):
    ''' Translated from source of colorsys.rgb_to_hsv
      r,g,b should be a numpy arrays with values between 0 and 255
      rgb_to_hsv returns an array of floats between 0.0 and 1.0. '''
      
    rgb = rgb.astype('float')
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select(
        [r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc)
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv

def hsv_to_rgb(hsv):
    ''' Translated from source of colorsys.hsv_to_rgb
      h,s should be a numpy arrays with values between 0.0 and 1.0
      v should be a numpy array with values between 0.0 and 255.0
      hsv_to_rgb returns an array of uints between 0 and 255. '''
      
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype('uint8')
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 0] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 1] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype('uint8')


def shift_hue(img,hout):
    hsv = rgb_to_hsv(img)
    hsv[...,0] = hout
    rgb = hsv_to_rgb(hsv)
    return rgb



# ???check???
def circleMask(SzX, SzY, pxlLoc, radius):
    a, b = pxlLoc
    y, x = np.ogrid[-a:SzX-a, -b:SzY-b]
    cmask = x*x + y*y <= radius*radius
    
    return cmask




# -----------------------------------------------------------------------------
# img scrolling functions
# -----------------------------------------------------------------------------


def scrollH(image, delta, ctrl):
    ''' Scroll an image sideways
        delta = number of pixels to roll image
        ctrl: 0 = left; 1 = right '''
    xsize, ysize = image.size
    delta = delta % xsize
    image2 = image.copy()
    if delta == 0: return image
    if ctrl==0:    # left scroll
        part1 = image.crop((0, 0, delta, ysize))
        part2 = image2.crop((delta, 0, xsize, ysize))
        image.paste(part1, (xsize-delta, 0, xsize, ysize))
        image.paste(part2, (0, 0, xsize-delta, ysize))
    elif ctrl==1:    # right scroll
        part1 = image.crop((0, 0, xsize-delta, ysize))
        part2 = image2.crop((xsize-delta, 0, xsize, ysize))
        image.paste(part1, (delta, 0, xsize, ysize))
        image.paste(part2, (0, 0, delta, ysize))       
    return image


def scrollV(image, delta, ctrl):
    ''' Scroll an image vertically
        delta = number of pixels to scroll image
        ctrl: 0 = down; 1 = up '''
    xsize, ysize = image.size
    delta = delta % xsize
    image2 = image.copy()
    if delta == 0: return image
    if ctrl==0:    # down scroll
        part1 = image.crop((0, delta, xsize, ysize))
        part2 = image2.crop((0, 0, xsize, delta))
        image.paste(part1, (0, 0, xsize, ysize-delta))
        image.paste(part2, (0, ysize-delta, xsize, ysize))
    elif ctrl==1:    # up scroll
        part1 = image.crop((0, ysize-delta, xsize, ysize))
        part2 = image2.crop((0, 0, xsize, ysize-delta))
        image.paste(part1, (0, 0, xsize, delta))
        image.paste(part2, (0, delta, xsize, ysize))
    return image


def scrollDiag(image, delta, ctrl):
    ''' Scroll an image diagonally
        delta = number of pixels to scroll image (horizontally - vertical follows proportionally)
        ctrl: 0 = up left; 1 = down left; 2 = up right; 3 = down right '''
    if not(ctrl==0 or ctrl==1 or ctrl==2 or ctrl==3):
        print('ERROR: ctrl must be {0, 1, 2, 3}')
    xsize, ysize = image.size
    delta = delta % xsize
    image2 = image.copy()
    image3 = image.copy()
    image4 = image.copy()
    if delta == 0: return image
    if ctrl==0:    # down scroll
        part1 = image.crop((0, delta, xsize, ysize))
        part2 = image2.crop((0, 0, xsize, delta))
        image.paste(part1, (0, 0, xsize, ysize-delta))
        image.paste(part2, (0, ysize-delta, xsize, ysize))
    elif ctrl==1:    # up scroll
        part1 = image.crop((0, ysize-delta, xsize, ysize))
        part2 = image2.crop((0, 0, xsize, ysize-delta))
        image.paste(part1, (0, 0, xsize, delta))
        image.paste(part2, (0, delta, xsize, ysize))
    if ctrl==2:    # down scroll
        part1 = image.crop((0, delta, xsize, ysize))
        part2 = image2.crop((0, 0, xsize, delta))
        image.paste(part1, (0, 0, xsize, ysize-delta))
        image.paste(part2, (0, ysize-delta, xsize, ysize))
    elif ctrl==3:    # up scroll
        part1 = image.crop((0, ysize-delta, xsize, ysize))
        part2 = image2.crop((0, 0, xsize, ysize-delta))
        image.paste(part1, (0, 0, xsize, delta))
        image.paste(part2, (0, delta, xsize, ysize))        
    return image


# -----------------------------------------------------------------------------
# img scaling / zooming / cropping functions
# -----------------------------------------------------------------------------


def odmkEyeRescale(self, img, SzX, SzY):
    # Rescale Image to SzW width and SzY height:
    # *****misc.imresize returns img with [Y-dim, X-dim] format instead of X,Y*****
    img_r = img[:, :, 0]
    img_g = img[:, :, 1]
    img_b = img[:, :, 2]
    imgRescale_r = misc.imresize(img_r, [SzY, SzX], interp='cubic')
    imgRescale_g = misc.imresize(img_g, [SzY, SzX], interp='cubic')
    imgRescale_b = misc.imresize(img_b, [SzY, SzX], interp='cubic')
    imgRescale = np.dstack((imgRescale_r, imgRescale_g, imgRescale_b))
    return imgRescale


def odmkEyeZoom(self, img, Z):
    # Zoom Image by factor Z:
    img_r = img[:, :, 0]
    img_g = img[:, :, 1]
    img_b = img[:, :, 2]
    imgZoom_r = ndimage.interpolation.zoom(img_r, Z)
    imgZoom_g = ndimage.interpolation.zoom(img_g, Z)
    imgZoom_b = ndimage.interpolation.zoom(img_b, Z)
    imgZoom = np.dstack((imgZoom_r, imgZoom_g, imgZoom_b))
    return imgZoom


def odmkEyeCrop(self, img, SzX, SzY, high):
    ''' crop img to SzX width x SzY height '''

    imgWidth = img.shape[1]
    imgHeight = img.shape[0]

    img_r = img[:, :, 0]
    img_g = img[:, :, 1]
    img_b = img[:, :, 2]

    imgCrop_r = np.zeros((SzY, SzX))
    imgCrop_g = np.zeros((SzY, SzX))
    imgCrop_b = np.zeros((SzY, SzX))

    wdiff_lhs = 0
    hdiff_ths = 0

    if imgWidth > SzX:
        wdiff = floor(imgWidth - SzX)
        if (wdiff % 2) == 1:    # wdiff is odd
            wdiff_lhs = floor(wdiff / 2)
            # wdiff_rhs = ceil(wdiff / 2)
        else:
            wdiff_lhs = wdiff / 2
            # wdiff_rhs = wdiff / 2

    if imgHeight > SzY:
        hdiff = floor(imgHeight - SzY)
        if (hdiff % 2) == 1:    # wdiff is odd
            hdiff_ths = floor(hdiff / 2)
            # hdiff_bhs = ceil(wdiff / 2)
        else:
            hdiff_ths = hdiff / 2
            # hdiff_bhs = hdiff / 2

    for j in range(SzY):
        for k in range(SzX):
            if high == 1:
                imgCrop_r[j, k] = img_r[j, int(k + wdiff_lhs)]
                imgCrop_g[j, k] = img_g[j, int(k + wdiff_lhs)]
                imgCrop_b[j, k] = img_b[j, int(k + wdiff_lhs)]
            else:
                # pdb.set_trace()
                imgCrop_r[j, k] = img_r[int(j + hdiff_ths), int(k + wdiff_lhs)]
                imgCrop_g[j, k] = img_g[int(j + hdiff_ths), int(k + wdiff_lhs)]
                imgCrop_b[j, k] = img_b[int(j + hdiff_ths), int(k + wdiff_lhs)]
        # if j == SzY - 1:
            # print('imgItr ++')
    imgCrop = np.dstack((imgCrop_r, imgCrop_g, imgCrop_b))
    return imgCrop







# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# end : function definitions
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


print('// //////////////////////////////////////////////////////////////// //')
print('// *--------------------------------------------------------------* //')
print('// *---::ODMK EYE Image processing Experiments::---*')
print('// *--------------------------------------------------------------* //')
print('// \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ //')


#xLength = 19.492
xLength = 13
fs = 48000.0        # audio sample rate:
framesPerSec = 60.0 # video frames per second:
# ub313 bpm = 178 , 267
bpm = 78            # 39 - 78 - 156
timeSig = 4         # time signature: 4 = 4/4; 3 = 3/4


# ?D Standard video aspect ratio
SzX = 1280
SzY = 720



eyeDir = rootDir+'eye\\eyeSrc\\'


# eyeOutFileName = 'microscopic'
# eyeOutDirName = 'microscopicDir/'


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //

## Load input image:
#gorgulan11 = misc.imread(srcDir+'keiLHC.jpeg')
#
#numImg = 33
#
#hRotVal = np.linspace(0, 6*np.pi, numImg)
#hRotVal = np.sin(hRotVal)
#
#
##green_hue = (180-78)/360.0
##red_hue = (180-180)/360.0
##rot_hue = (50)/360.0
#
#
#
##gorgulanRed = shift_hue(gorgulan11, rot_hue)
#
##eyeHueFull = outDir+'eyeHue.jpg'
##misc.imsave(eyeHueFull, gorgulanRed)
#
#
#n_digits = int(ceil(np.log10(numImg))) + 2
#nextInc = 0
#for i in range(numImg):
#    
#    gorgulanShift = shift_hue(gorgulan11, hRotVal[i])    
#    
#    nextInc += 1
#    zr = ''
#    for j in range(n_digits - len(str(nextInc))):
#        zr += '0'
#    strInc = zr+str(nextInc)
#    eyeHueIdxNm = eyeHueNm+strInc+'.jpg'
#    eyeHueFull = outDir+eyeHueIdxNm
#    misc.imsave(eyeHueFull, gorgulanShift)



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


jpgSrcDir = eyeDir+'odmkG1Src\\'




#eyeExp1 = jpgSrcDir+'bananasloth0036.jpg'
#eyeExp2 = jpgSrcDir+'bananasloth0039.jpg'
#
#eyeExp3 = jpgSrcDir+'bSlothCultLife0098.jpg'
#eyeExp4 = jpgSrcDir+'bSlothCultLife004.jpg'
#eyeExp5 = jpgSrcDir+'bSlothCultLife000108.jpg'
#eyeExp6 = jpgSrcDir+'bSlothCultLife0586.jpg'
#eyeExp7 = jpgSrcDir+'bSlothCultLife00757.jpg'
#
#eyeIn1 = jpgSrcDir+'microscopic00617.jpg'
#eyeIn2 = jpgSrcDir+'microscopic00525.jpg'

eyeOutDirName = 'eyeBasicTestDir\\'


# output dir where processed img files are stored:
# eyeOutDirName = 'myOutputDirName'    # defined above
imgOutDir = eyeDir+eyeOutDirName
# If Dir does not exist, makedir:
os.makedirs(imgOutDir, exist_ok=True)



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //



def eyeMirrorHV4(img, SzX, SzY, ctrl='UL'):
    ''' generates composite 4 frame resized images
        SzX, SzY: output image dimentions
        img: PIL image object
        ctrl: { UL, UR, LL, LR} - selects base quadrant '''
    
    
    if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
        print('ERROR: ctrl must be {UL, UR, LL, LR} <string>')
        return
    
    imgSzX = img.size[0]
    imgSzY = img.size[1]
    
    imgDim = (SzX, SzY)
    
    if (SzX == 2*imgSzX and SzY == 2*imgSzY):
        subDim = (imgSzX, imgSzY)
        imgX = img
    else:
        subDim = (int(SzX/2), int(SzY/2))
        imgX = img.resize(subDim)
    
    
    mirrorImg = Image.new('RGB', imgDim)  # e.g. ('RGB', (640, 480))
    

    #boxUL = (0, SzY, SzX-1, 2*SzY-1)
    boxUL = (0, subDim[1], subDim[0], imgDim[1])
    boxUR = (subDim[0], subDim[1], imgDim[0], imgDim[1]) 
    boxLL = (0, 0, subDim[0], subDim[1])
    boxLR = (subDim[0], 0, imgDim[0], subDim[1])
    

    if ctrl == 'LL':
        eyeSubUL = imgX
        eyeSubUR = ImageOps.mirror(imgX)
        eyeSubLL = ImageOps.flip(imgX)
        eyeSubLR = ImageOps.flip(imgX)
        eyeSubLR = ImageOps.mirror(eyeSubLR)        
        
        
    if ctrl == 'LR':
        eyeSubUL = ImageOps.mirror(imgX)
        eyeSubUR = imgX
        eyeSubLL = ImageOps.flip(imgX)
        eyeSubLL = ImageOps.mirror(eyeSubLL)
        eyeSubLR = ImageOps.flip(imgX)
        
        
    if ctrl == 'UL':
        eyeSubUL = ImageOps.flip(imgX)
        eyeSubUR = ImageOps.flip(imgX)
        eyeSubUR = ImageOps.mirror(eyeSubUR)
        eyeSubLL = imgX
        eyeSubLR = ImageOps.mirror(imgX)


    if ctrl == 'UR':
        eyeSubUL = ImageOps.flip(imgX)
        eyeSubUL = ImageOps.mirror(eyeSubUL)
        eyeSubUR = ImageOps.flip(imgX)
        eyeSubLL = ImageOps.mirror(imgX)
        eyeSubLR = imgX


    #pdb.set_trace()

    mirrorImg.paste(eyeSubUL, boxUL)
    mirrorImg.paste(eyeSubUR, boxUR)
    mirrorImg.paste(eyeSubLL, boxLL)
    mirrorImg.paste(eyeSubLR, boxLR)

    
    #eyeOutFileName = 'eyeMirrorHV4'
    #eyeMirrorHV4Full = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeMirrorHV4Full, mirrorImg)
    
    return mirrorImg


if (0):

    eyeExp1 = jpgSrcDir+'bananasloth0036.jpg'
    eyeExp2 = jpgSrcDir+'bananasloth0039.jpg'
    eyeExp3 = jpgSrcDir+'microscopic00652.jpg'
    eyeExp4 = jpgSrcDir+'microscopic00640.jpg'
    eyeExp5 = jpgSrcDir+'microscopic0042.jpg'
    
    eye1 = misc.imread(eyeExp2)
    eye2 = misc.imread(eyeExp5)
    
    
    #eye1img = Image.fromarray(eye1)
    eye1img = Image.fromarray(eye1)
    eye2img = Image.fromarray(eye2)
    
    #ctrl = 1
    
    mirrorHV4reScl = eyeMirrorHV4(eye2img, SzX, SzY, ctrl='LR')
    mirrorHV4noScl = eyeMirrorHV4(eye2img, 2*SzX, 2*SzY, ctrl='LL')
    
    
    eyeOutFileName = 'eye1img'
    eye1imgFull = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeBoxFull, eye1imgCpy)
    misc.imsave(eye1imgFull, eye1img)
    
    eyeOutFileName = 'mirrorHV4reSclTest'
    mirrorHV4reSclFull = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeBoxFull, eye1imgCpy)
    misc.imsave(mirrorHV4reSclFull, mirrorHV4reScl)
    
    eyeOutFileName = 'mirrorHV4noSclTest'
    mirrorHV4noSclFull = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeBoxFull, eye1imgCpy)
    misc.imsave(mirrorHV4noSclFull, mirrorHV4noScl)


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //




# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //



if (0):     # z??? check this***
    
    # // *-----------------------------------------------------------------* //
    # // *-----------------------------------------------------------------* //

    # // *** 2D Harmonics Basic - Blend LightSource / Shade imgaes
    
    X00, Y00 = np.mgrid[-3.6:3.6:0.01, -6.4:6.4:0.01]
    X01, Y01 = np.mgrid[-3.6:3.6:0.01, -6.4:6.4:0.01]
    X02, Y02 = np.mgrid[-3.6:3.6:0.01, -6.4:6.4:0.01]
    
    X03, Y03 = np.mgrid[-7.2:7.2:0.02, -12.8:12.8:0.02]
    X04, Y04 = np.mgrid[-7.2:7.2:0.02, -12.8:12.8:0.02]
    X05, Y05 = np.mgrid[-7.2:7.2:0.02, -12.8:12.8:0.02]

    X06, Y06 = np.mgrid[-14.4:14.4:0.04, -25.6:25.6:0.04]
    X07, Y07 = np.mgrid[-14.4:14.4:0.04, -25.6:25.6:0.04]
    X08, Y08 = np.mgrid[-14.4:14.4:0.04, -25.6:25.6:0.04]

#    X06, Y06 = np.mgrid[-36:36:0.1, -64:64:0.1]
#    X07, Y07 = np.mgrid[-36:36:0.1, -64:64:0.1]
#    X08, Y08 = np.mgrid[-36:36:0.1, -64:64:0.1]

#    X06, Y06 = np.mgrid[-0.36:0.36:0.001, -0.64:0.64:0.001]
#    X07, Y07 = np.mgrid[-0.36:0.36:0.001, -0.64:0.64:0.001]
#    X08, Y08 = np.mgrid[-0.36:0.36:0.001, -0.64:0.64:0.001]

    #X0, Y0 = np.mgrid[-6.4:6.4:0.01, -6.4:6.4:0.01]
    #Z0 = np.sqrt(X0**2 + Y0**2) + np.sin(X0**4 + Y0**2)
    Z00 = np.sqrt(X00**2 + Y00**2) + np.sin(X00**2 + Y00**2)
    Z01 = np.sqrt(X01**2 + Y01**2) + 1.5*np.cos(X01**2 + Y01**2)
    Z02 = np.sqrt(X02**2 + Y02**2) + 2*np.sin(X02**2 + Y02**2)
    
    Z03 = np.sqrt(X03**2 + Y03**2) + 1.5*np.sin(X03**4 + Y03**2)
    Z04 = np.sqrt(X04**2 + Y04**2) + 1.5*np.cos(X04**3 + Y04**3)
    Z05 = np.sqrt(X05**2 + Y05**2) + np.sin(X05**3 + Y05**3)

    Z06 = np.sqrt(X06**2 + Y06**2) + 1.5*np.cos(X06**2 + Y06**3)
    Z07 = np.sqrt(X07**2 + Y07**2) + 1.5*np.sin(X07**2 + Y07**4)
    Z08 = np.sqrt(X08**2 + Y08**2) + 1.5*np.cos(X08**3 + Y08**2)

    
    print('size of Z00 = '+str(Z00.shape))   
    print('size of Z03 = '+str(Z03.shape))    
    print('size of Z06 = '+str(Z06.shape))
    
    
    rgbRawScl00 = Z00*(255 // np.amax(Z00))
    rgbRawScl01 = Z01*(255 // np.amax(Z01))
    rgbRawScl02 = Z02*(255 // np.amax(Z02))
    
    rgbRawScl03 = Z03*(255 // np.amax(Z03))
    rgbRawScl04 = Z04*(255 // np.amax(Z04))
    rgbRawScl05 = Z05*(255 // np.amax(Z05))

    rgbRawScl06 = Z06*(255 // np.amax(Z06))
    rgbRawScl07 = Z07*(255 // np.amax(Z07))
    rgbRawScl08 = Z08*(255 // np.amax(Z08))
        
    
    print('size of rgbRawScl00 = '+str(rgbRawScl00.shape))
    print('size of rgbRawScl03 = '+str(rgbRawScl03.shape))
    print('size of rgbRawScl06 = '+str(rgbRawScl06.shape))
    
    #print('rgbRaw00 sample row max = '+str(max(Z00[444,:])))
    print('rgbRaw00 array max = '+str(np.amax(Z00)))
    #print('rgbRawScl00 sample row max = '+str(max(rgbRawScl00[444,:])))
    print('rgbRawScl00 array max = '+str(np.amax(rgbRawScl00)))    
    
    #print('rgbRaw03 sample row max = '+str(max(Z03[444,:])))
    print('rgbRaw03 array max = '+str(np.amax(Z03)))    
    #print('rgbRawScl03 sample row max = '+str(max(rgbRawScl03[444,:])))
    print('rgbRawScl03 array max = '+str(np.amax(rgbRawScl03))) 
   
    #print('rgbRaw06 sample row max = '+str(max(Z06[444,:])))
    print('rgbRaw06 array max = '+str(np.amax(Z06)))
    #print('rgbRawScl06 sample row max = '+str(max(rgbRawScl06[444,:])))
    print('rgbRawScl06 array max = '+str(np.amax(rgbRawScl06)))
    
    
#    sclFactor00 = 255 // np.amax(Z00) 
#    sclFactor01 = 255 // np.amax(Z00)
#    sclFactor02 = 255 // np.amax(Z00)
#    sclFactor03 = 255 // np.amax(Z00)
#    sclFactor04 = 255 // np.amax(Z00)
#    sclFactor05 = 255 // np.amax(Z00)
#    sclFactor06 = 255 // np.amax(Z00)
#    sclFactor07 = 255 // np.amax(Z00)
#    sclFactor08 = 255 // np.amax(Z00)    
   
    rgbRawScl00_r = np.zeros((SzY, SzX, 1))
    rgbRawScl00_g = np.zeros((SzY, SzX, 1))
    rgbRawScl00_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl00_r[:, :, 0] = rgbRawScl00
    rgbRawScl00_g[:, :, 0] = rgbRawScl00
    rgbRawScl00_b[:, :, 0] = rgbRawScl00
        
    rgbRawScl00_img = np.dstack((rgbRawScl00_r, rgbRawScl00_g, rgbRawScl00_b))
    rgbRawScl00_img = rgbRawScl00_img.astype('uint8')

    print('size of rgbRawScl00_img = '+str(rgbRawScl00_img.shape))


    rgbRawScl01_r = np.zeros((SzY, SzX, 1))
    rgbRawScl01_g = np.zeros((SzY, SzX, 1))
    rgbRawScl01_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl01_r[:, :, 0] = rgbRawScl01
    rgbRawScl01_g[:, :, 0] = rgbRawScl01
    rgbRawScl01_b[:, :, 0] = rgbRawScl01
        
    rgbRawScl01_img = np.dstack((rgbRawScl01_r, rgbRawScl01_g, rgbRawScl01_b))
    rgbRawScl01_img = rgbRawScl01_img.astype('uint8')
    
    
    rgbRawScl02_r = np.zeros((SzY, SzX, 1))
    rgbRawScl02_g = np.zeros((SzY, SzX, 1))
    rgbRawScl02_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl02_r[:, :, 0] = rgbRawScl02
    rgbRawScl02_g[:, :, 0] = rgbRawScl02
    rgbRawScl02_b[:, :, 0] = rgbRawScl02
        
    rgbRawScl02_img = np.dstack((rgbRawScl02_r, rgbRawScl02_g, rgbRawScl02_b))
    rgbRawScl02_img = rgbRawScl02_img.astype('uint8')

    
    rgbRawScl03_r = np.zeros((SzY, SzX, 1))
    rgbRawScl03_g = np.zeros((SzY, SzX, 1))
    rgbRawScl03_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl03_r[:, :, 0] = rgbRawScl03
    rgbRawScl03_g[:, :, 0] = rgbRawScl03
    rgbRawScl03_b[:, :, 0] = rgbRawScl03
        
    rgbRawScl03_img = np.dstack((rgbRawScl03_r, rgbRawScl03_g, rgbRawScl03_b))
    rgbRawScl03_img = rgbRawScl03_img.astype('uint8')    
    
    
    rgbRawScl04_r = np.zeros((SzY, SzX, 1))
    rgbRawScl04_g = np.zeros((SzY, SzX, 1))
    rgbRawScl04_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl04_r[:, :, 0] = rgbRawScl04
    rgbRawScl04_g[:, :, 0] = rgbRawScl04
    rgbRawScl04_b[:, :, 0] = rgbRawScl04
        
    rgbRawScl04_img = np.dstack((rgbRawScl04_r, rgbRawScl04_g, rgbRawScl04_b))
    rgbRawScl04_img = rgbRawScl04_img.astype('uint8')    
    
    
    rgbRawScl05_r = np.zeros((SzY, SzX, 1))
    rgbRawScl05_g = np.zeros((SzY, SzX, 1))
    rgbRawScl05_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl05_r[:, :, 0] = rgbRawScl05
    rgbRawScl05_g[:, :, 0] = rgbRawScl05
    rgbRawScl05_b[:, :, 0] = rgbRawScl05
        
    rgbRawScl05_img = np.dstack((rgbRawScl05_r, rgbRawScl05_g, rgbRawScl05_b))
    rgbRawScl05_img = rgbRawScl05_img.astype('uint8')    
    
    
    rgbRawScl06_r = np.zeros((SzY, SzX, 1))
    rgbRawScl06_g = np.zeros((SzY, SzX, 1))
    rgbRawScl06_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl06_r[:, :, 0] = rgbRawScl06
    rgbRawScl06_g[:, :, 0] = rgbRawScl06
    rgbRawScl06_b[:, :, 0] = rgbRawScl06
        
    rgbRawScl06_img = np.dstack((rgbRawScl06_r, rgbRawScl06_g, rgbRawScl06_b))
    rgbRawScl06_img = rgbRawScl06_img.astype('uint8')


    rgbRawScl07_r = np.zeros((SzY, SzX, 1))
    rgbRawScl07_g = np.zeros((SzY, SzX, 1))
    rgbRawScl07_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl07_r[:, :, 0] = rgbRawScl07
    rgbRawScl07_g[:, :, 0] = rgbRawScl07
    rgbRawScl07_b[:, :, 0] = rgbRawScl07
        
    rgbRawScl07_img = np.dstack((rgbRawScl07_r, rgbRawScl07_g, rgbRawScl07_b))
    rgbRawScl07_img = rgbRawScl07_img.astype('uint8')    
    
    
    rgbRawScl08_r = np.zeros((SzY, SzX, 1))
    rgbRawScl08_g = np.zeros((SzY, SzX, 1))
    rgbRawScl08_b = np.zeros((SzY, SzX, 1))   
    
    rgbRawScl08_r[:, :, 0] = rgbRawScl08
    rgbRawScl08_g[:, :, 0] = rgbRawScl08
    rgbRawScl08_b[:, :, 0] = rgbRawScl08
        
    rgbRawScl08_img = np.dstack((rgbRawScl08_r, rgbRawScl08_g, rgbRawScl08_b))
    rgbRawScl08_img = rgbRawScl08_img.astype('uint8')



    # Create output 2D harmonic img
    omdk2DHarmonic1 = Image.fromarray(rgbRawScl00_img)
    omdk2DHarmonic2 = Image.fromarray(rgbRawScl01_img)
    omdk2DHarmonic3 = Image.fromarray(rgbRawScl02_img)
    
    omdk2DHarmonic4 = Image.fromarray(rgbRawScl03_img)
    omdk2DHarmonic5 = Image.fromarray(rgbRawScl04_img)
    omdk2DHarmonic6 = Image.fromarray(rgbRawScl05_img)
    
    omdk2DHarmonic7 = Image.fromarray(rgbRawScl06_img)
    omdk2DHarmonic8 = Image.fromarray(rgbRawScl07_img)
    omdk2DHarmonic9 = Image.fromarray(rgbRawScl08_img)
    #omdk2DHarmonic1 = ImageOps.autocontrast(omdk2DHarmonic1, cutoff=0)


    #2DHarmonicSet = [omdk2DHarmonic1, omdk2DHarmonic2, omdk2DHarmonic3, omdk2DHarmonic4, omdk2DHarmonic5, omdk2DHarmonic6, omdk2DHarmonic7, omdk2DHarmonic8, omdk2DHarmonic9]

    fig50 = plt.figure(num=50, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl00_img)
    plt.title('fig100')
    plt.xticks([])
    plt.yticks([])


    fig51 = plt.figure(num=51, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl01_img)
    plt.title('fig101')
    plt.xticks([])
    plt.yticks([])


    fig52 = plt.figure(num=52, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl02_img)
    plt.title('fig102')
    plt.xticks([])
    plt.yticks([])



    fig53 = plt.figure(num=53, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl03_img)
    plt.title('fig103')
    plt.xticks([])
    plt.yticks([])


    fig54 = plt.figure(num=54, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl04_img)
    plt.title('fig104')
    plt.xticks([])
    plt.yticks([])


    fig55 = plt.figure(num=55, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl05_img)
    plt.title('fig105')
    plt.xticks([])
    plt.yticks([])


    fig56 = plt.figure(num=56, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl06_img)
    plt.title('fig106')
    plt.xticks([])
    plt.yticks([])


    fig57 = plt.figure(num=57, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl07_img)
    plt.title('fig107')
    plt.xticks([])
    plt.yticks([])


    fig58 = plt.figure(num=58, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(rgbRawScl08_img)
    plt.title('fig108')
    plt.xticks([])
    plt.yticks([])    






if (1):
    
    # // *-----------------------------------------------------------------* //
    # // *-----------------------------------------------------------------* //

    print('// *--------------------------------------------------------------* //')
    print('// *---::2D Harmonics Basic - Blend LightSource / Shade imgaes::---*')
    print('// *--------------------------------------------------------------* //')


    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    #X0, Y0 = np.mgrid[-360:360:1, -640:640:1]
    
    
    #X00, Y00 = np.mgrid[-0.36:0.36:0.001, -0.64:0.64:0.001]
    X00, Y00 = np.mgrid[-3.6:3.6:0.01, -6.4:6.4:0.01]
    X01, Y01 = np.mgrid[-36:36:0.1, -64:64:0.1]
    X02, Y02 = np.mgrid[-36:36:0.1, -64:64:0.1]
    
    X03, Y03 = np.mgrid[-36:36:0.1, -64:64:0.1]
    X04, Y04 = np.mgrid[-36:36:0.1, -64:64:0.1]
    X05, Y05 = np.mgrid[-3.6:3.6:0.01, -6.4:6.4:0.01]

    X06, Y06 = np.mgrid[-36:36:0.1, -64:64:0.1]
    X07, Y07 = np.mgrid[-36:36:0.1, -64:64:0.1]
    X08, Y08 = np.mgrid[-36:36:0.1, -64:64:0.1]

    #X0, Y0 = np.mgrid[-6.4:6.4:0.01, -6.4:6.4:0.01]
    #Z0 = np.sqrt(X0**2 + Y0**2) + np.sin(X0**4 + Y0**2)
    Z00 = np.sqrt(X00**2 + Y00**2) + np.sin(X00**2 + Y00**2)
    Z01 = np.sqrt(X01**2 + Y01**2) + 3*np.sin(X01**2 + Y01**2)
    Z02 = np.sqrt(X02**2 + Y02**2) + 3*np.sin(X02**2 + Y02**2)
    
    Z03 = np.sqrt(X03**2 + Y03**2) + 2*np.cos(X03**2 + Y03**2)
    Z04 = np.sqrt(X04**2 + Y04**2) + 2*np.cos(X04**3 + Y04**3)
    Z05 = np.sqrt(X05**2 + Y05**2) + 2*np.cos(X05**4 + Y05**4)

    Z06 = np.sqrt(X06**2 + Y06**2) + np.cos(X06**2 + Y06**2)
    Z07 = np.sqrt(X07**2 + Y07**2) + np.sin(X07**2 + Y07**2)
    Z08 = np.sqrt(X08**2 + Y08**2) + 6*np.cos(X08**2 + Y08**2)

    
    print('size of Z00 = '+str(Z00.shape))   
    print('size of Z03 = '+str(Z03.shape))    
    print('size of Z06 = '+str(Z06.shape))
    
    
    rgbRawScl00 = Z00*(255 // np.amax(Z00))
    rgbRawScl01 = Z01*(255 // np.amax(Z01))
    rgbRawScl02 = Z02*(255 // np.amax(Z02))
    
    rgbRawScl03 = Z03*(255 // np.amax(Z03))
    rgbRawScl04 = Z04*(255 // np.amax(Z04))
    rgbRawScl05 = Z05*(255 // np.amax(Z05))

    rgbRawScl06 = Z06*(255 // np.amax(Z06))
    rgbRawScl07 = Z07*(255 // np.amax(Z07))
    rgbRawScl08 = Z08*(255 // np.amax(Z08))
        
    
    print('size of rgbRawScl00 = '+str(rgbRawScl00.shape))
    print('size of rgbRawScl03 = '+str(rgbRawScl03.shape))
    print('size of rgbRawScl06 = '+str(rgbRawScl06.shape))
    
    #print('rgbRaw00 sample row max = '+str(max(Z00[444,:])))
    print('rgbRaw00 array max = '+str(np.amax(Z00)))
    #print('rgbRawScl00 sample row max = '+str(max(rgbRawScl00[444,:])))
    print('rgbRawScl00 array max = '+str(np.amax(rgbRawScl00)))    
    
    #print('rgbRaw03 sample row max = '+str(max(Z03[444,:])))
    print('rgbRaw03 array max = '+str(np.amax(Z03)))    
    #print('rgbRawScl03 sample row max = '+str(max(rgbRawScl03[444,:])))
    print('rgbRawScl03 array max = '+str(np.amax(rgbRawScl03))) 
   
    #print('rgbRaw06 sample row max = '+str(max(Z06[444,:])))
    print('rgbRaw06 array max = '+str(np.amax(Z06)))
    #print('rgbRawScl06 sample row max = '+str(max(rgbRawScl06[444,:])))
    print('rgbRawScl06 array max = '+str(np.amax(rgbRawScl06)))
    
    
#    sclFactor00 = 255 // np.amax(Z00) 
#    sclFactor01 = 255 // np.amax(Z00)
#    sclFactor02 = 255 // np.amax(Z00)
#    sclFactor03 = 255 // np.amax(Z00)
#    sclFactor04 = 255 // np.amax(Z00)
#    sclFactor05 = 255 // np.amax(Z00)
#    sclFactor06 = 255 // np.amax(Z00)
#    sclFactor07 = 255 // np.amax(Z00)
#    sclFactor08 = 255 // np.amax(Z00)    
   
#    rgbRawScl00_r = np.zeros((SzY, SzX, 1))
#    rgbRawScl00_g = np.zeros((SzY, SzX, 1))
#    rgbRawScl00_b = np.zeros((SzY, SzX, 1))   
#   
#    
#    rgbRawScl00_r[:, :, 0] = rgbRawScl00
#    rgbRawScl00_g[:, :, 0] = rgbRawScl00
#    rgbRawScl00_b[:, :, 0] = rgbRawScl00
#        
#        
#    rgbRawScl00_img = np.dstack((rgbRawScl00_r, rgbRawScl00_g, rgbRawScl00_b))
#    print('size of rgbRawScl00_img = '+str(rgbRawScl00_img.shape))
        
        
    
    # create light source object.
    ls00 = LightSource(azdeg=0, altdeg=66)
    ls01 = LightSource(azdeg=0, altdeg=66)
    ls02 = LightSource(azdeg=0, altdeg=66)
    
    ls03 = LightSource(azdeg=0, altdeg=66)
    ls04 = LightSource(azdeg=0, altdeg=66)    
    ls05 = LightSource(azdeg=0, altdeg=13)
    
    ls06 = LightSource(azdeg=0, altdeg=26)    
    ls07 = LightSource(azdeg=0, altdeg=108)    
    ls08 = LightSource(azdeg=0, altdeg=156)    


    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    shade00 = ls00.shade(Z00, plt.cm.gist_gray)
    shade01 = ls01.shade(Z01, plt.cm.gist_gray)
    shade02 = ls02.shade(Z02, plt.cm.gist_gray)

    shade03 = ls03.shade(Z03, plt.cm.prism)
    shade04 = ls04.shade(Z04, plt.cm.magma_r)
    shade05 = ls05.shade(Z05, plt.cm.gnuplot_r)

    shade06 = ls06.shade(Z06, plt.cm.Wistia_r)
    shade07 = ls07.shade(Z07, plt.cm.bone_r)
    shade08 = ls08.shade(Z08, plt.cm.afmhot_r)


    print('size of shade00 = '+str(shade00.shape))
    print('size of shade03 = '+str(shade03.shape))
    print('size of shade06 = '+str(shade06.shape))

    print('shade00 sample row max = '+str(max(shade00[444,:,1])))
    print('shade03 sample row max = '+str(max(shade03[444,:,1])))    
    print('shade06 sample row max = '+str(max(shade06[444,:,1])))    
    


    shadeScl00 = shade00[:,:,0:3]
    shadeScl01 = shade01[:,:,0:3]
    shadeScl02 = shade02[:,:,0:3]

    shadeScl03 = shade03[:,:,0:3]
    shadeScl04 = shade04[:,:,0:3]
    shadeScl05 = shade05[:,:,0:3]

    shadeScl06 = shade06[:,:,0:3]
    shadeScl07 = shade07[:,:,0:3]
    shadeScl08 = shade08[:,:,0:3]


    shadeSclRnd00 = np.round(shadeScl00 * 255)
    shadeSclRnd01 = np.round(shadeScl01 * 255)
    shadeSclRnd02 = np.round(shadeScl02 * 255)

    shadeSclRnd03 = np.round(shadeScl03 * 255)
    shadeSclRnd04 = np.round(shadeScl04 * 255)
    shadeSclRnd05 = np.round(shadeScl05 * 255)

    shadeSclRnd06 = np.round(shadeScl06 * 255)
    shadeSclRnd07 = np.round(shadeScl07 * 255)
    shadeSclRnd08 = np.round(shadeScl08 * 255)


    shadeUint8_00 = shadeSclRnd00.astype('uint8')
    shadeUint8_01 = shadeSclRnd01.astype('uint8')
    shadeUint8_02 = shadeSclRnd02.astype('uint8')
    
    shadeUint8_03 = shadeSclRnd03.astype('uint8')
    shadeUint8_04 = shadeSclRnd04.astype('uint8')
    shadeUint8_05 = shadeSclRnd05.astype('uint8')

    shadeUint8_06 = shadeSclRnd06.astype('uint8')
    shadeUint8_07 = shadeSclRnd07.astype('uint8')
    shadeUint8_08 = shadeSclRnd08.astype('uint8')
    
    
    # Create output 2D harmonic img
    omdk2DHarmonic1 = Image.fromarray(shadeUint8_00)
    omdk2DHarmonic2 = Image.fromarray(shadeUint8_01)
    omdk2DHarmonic3 = Image.fromarray(shadeUint8_02)
    
    omdk2DHarmonic4 = Image.fromarray(shadeUint8_03)
    omdk2DHarmonic5 = Image.fromarray(shadeUint8_04)
    omdk2DHarmonic6 = Image.fromarray(shadeUint8_05)
    
    omdk2DHarmonic7 = Image.fromarray(shadeUint8_06)
    omdk2DHarmonic8 = Image.fromarray(shadeUint8_07)
    omdk2DHarmonic9 = Image.fromarray(shadeUint8_08)
    #omdk2DHarmonic1 = ImageOps.autocontrast(omdk2DHarmonic1, cutoff=0)    
    
    
    
    
    

    #pdb.set_trace()
    
    
    fig100 = plt.figure(num=100, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl00)
    plt.title('fig100')
    plt.xticks([])
    plt.yticks([])
    
    
    fig101 = plt.figure(num=101, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl01)
    plt.title('fig101')
    plt.xticks([])
    plt.yticks([])    
    

    fig102 = plt.figure(num=102, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl02)
    plt.title('fig102')
    plt.xticks([])
    plt.yticks([])
    
    
    fig103 = plt.figure(num=103, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl03)
    plt.title('fig103')
    plt.xticks([])
    plt.yticks([])


    fig104 = plt.figure(num=104, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl04)
    plt.title('fig104')
    plt.xticks([])
    plt.yticks([])
    
    
    fig105 = plt.figure(num=105, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl05)
    plt.title('fig105')
    plt.xticks([])
    plt.yticks([])    
    

    fig106 = plt.figure(num=106, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl06)
    plt.title('fig106')
    plt.xticks([])
    plt.yticks([])
    
    
    fig107 = plt.figure(num=107, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl07)
    plt.title('fig107')
    plt.xticks([])
    plt.yticks([])
    
    
    fig108 = plt.figure(num=108, figsize=(9, 9), facecolor='silver', edgecolor='k')
    plt.imshow(shadeScl08)
    plt.title('fig108')
    plt.xticks([])
    plt.yticks([])  
    
    
    
    
    eyeOutFileName = 'omdk2DHarmonic1'
    omdk2DHarmonic1Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic1Full,omdk2DHarmonic1)
    
    eyeOutFileName = 'omdk2DHarmonic2'
    omdk2DHarmonic2Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic2Full, omdk2DHarmonic2)
    
    eyeOutFileName = 'omdk2DHarmonic3'
    omdk2DHarmonic3Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic3Full,omdk2DHarmonic3)
    
    
    eyeOutFileName = 'omdk2DHarmonic4'
    omdk2DHarmonic4Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic4Full,omdk2DHarmonic4)
    
    eyeOutFileName = 'omdk2DHarmonic5'
    omdk2DHarmonic5Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic5Full, omdk2DHarmonic5)
    
    eyeOutFileName = 'omdk2DHarmonic6'
    omdk2DHarmonic6Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic6Full,omdk2DHarmonic6)
    
    
    eyeOutFileName = 'omdk2DHarmonic7'
    omdk2DHarmonic7Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic7Full,omdk2DHarmonic7)
    
    eyeOutFileName = 'omdk2DHarmonic8'
    omdk2DHarmonic8Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic8Full, omdk2DHarmonic8)
    
    eyeOutFileName = 'omdk2DHarmonic9'
    omdk2DHarmonic9Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHarmonic9Full,omdk2DHarmonic9)




    eyeExp1 = jpgSrcDir+'bananasloth0036.jpg'
    eyeExp2 = jpgSrcDir+'bananasloth0039.jpg'
    eyeExp3 = jpgSrcDir+'microscopic00652.jpg'
    eyeExp4 = jpgSrcDir+'microscopic00640.jpg'
    eyeExp5 = jpgSrcDir+'microscopic0042.jpg'
    
    eye1 = misc.imread(eyeExp2)
    eye2 = misc.imread(eyeExp5)
    
    
    #eye1img = Image.fromarray(eye1)
    eye1img = Image.fromarray(eye1)
    eye2img = Image.fromarray(eye2)


    omdk2DHBlend1 = Image.blend(omdk2DHarmonic1, eye2img, 0.5)
    #omdk2DHBlend1 = ImageOps.autocontrast(omdk2DHBlend1, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend1'
    omdk2DHBlend1Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend1Full,omdk2DHBlend1)
    
    
    omdk2DHBlend2 = Image.blend(omdk2DHarmonic2, eye2img, 0.5)
    #omdk2DHBlend2 = ImageOps.autocontrast(omdk2DHarmonic2, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend2'
    omdk2DHBlend2Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend2Full,omdk2DHBlend2)
    
    
    omdk2DHBlend3 = Image.blend(omdk2DHarmonic3, eye2img, 0.5)
    #omdk2DHBlend2 = ImageOps.autocontrast(omdk2DHarmonic2, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend3'
    omdk2DHBlend3Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend3Full,omdk2DHBlend3)
    
    
    
    omdk2DHBlend4 = Image.blend(omdk2DHarmonic4, eye2img, 0.5)
    omdk2DHBlend4 = ImageOps.autocontrast(omdk2DHBlend4, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend4'
    omdk2DHBlend4Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend4Full, omdk2DHBlend4)
    
    
    omdk2DHBlend5 = Image.blend(omdk2DHarmonic5, eye2img, 0.5)
    omdk2DHBlend5 = ImageOps.autocontrast(omdk2DHBlend5, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend5'
    omdk2DHBlend5Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend5Full, omdk2DHBlend5)
    
    
    omdk2DHBlend6 = Image.blend(omdk2DHarmonic6, eye2img, 0.5)
    omdk2DHBlend6 = ImageOps.autocontrast(omdk2DHBlend6, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend6'
    omdk2DHBlend6Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend6Full, omdk2DHBlend6)
    
    
    
    omdk2DHBlend7 = Image.blend(omdk2DHarmonic7, eye2img, 0.5)
    omdk2DHBlend7 = ImageOps.autocontrast(omdk2DHBlend7, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend7'
    omdk2DHBlend7Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend7Full, omdk2DHBlend7)
    
    
    omdk2DHBlend8 = Image.blend(omdk2DHarmonic8, eye2img, 0.5)
    omdk2DHBlend8 = ImageOps.autocontrast(omdk2DHBlend8, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend8'
    omdk2DHBlend8Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend8Full, omdk2DHBlend8)
    
    
    omdk2DHBlend9 = Image.blend(omdk2DHarmonic9, eye2img, 0.5)
    omdk2DHBlend9 = ImageOps.autocontrast(omdk2DHBlend9, cutoff=0)
    eyeOutFileName = 'omdk2DHBlend9'
    omdk2DHBlend9Full = imgOutDir+eyeOutFileName+'.jpg'
    misc.imsave(omdk2DHBlend9Full, omdk2DHBlend9)





if (1):
    
    # // *-----------------------------------------------------------------* //
    # // *-----------------------------------------------------------------* //

    # // *** plot LightSource / Shade imgaes    
    
    
    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    X1, Y1 = np.mgrid[-7.2:7.2:0.01, -12.8:12.8:0.01]
    Z1 = np.sqrt(X1**2 + Y1**2) + np.sin(X1**2 + Y1**3)
    
    # create light source object.
    ls1 = LightSource(azdeg=0, altdeg=65)
    
    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    rgb1 = ls1.shade(Z1, plt.cm.prism)
    
    #print('size of rgb1 = '+str(rgb1.shape))
    
    fig1 = plt.figure(num=1, figsize=(9, 9), facecolor='silver', edgecolor='k')
    # plt.figure(figsize=(12, 5))
    plt.imshow(rgb1)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])
    
   
    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    X2, Y2 = np.mgrid[-11:11:0.01, -11:11:0.01]
    Z2 = 3*np.sqrt(X2**2 + Y2**2) + np.cos(X2**2 + Y2**3)
    
    # create light source object.
    ls2 = LightSource(azdeg=0, altdeg=65)
    
    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    rgb2 = ls2.shade(Z2, plt.cm.afmhot_r)
    
    fig2 = plt.figure(num=2, figsize=(9, 9), facecolor='silver', edgecolor='k')
    # plt.figure(figsize=(12, 5))
    plt.imshow(rgb2)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])
    
    
    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    X3, Y3 = np.mgrid[-11:11:0.01, -11:11:0.01]
    Z3 = np.sqrt(X3**2 + Y3**2) + np.sin(X3**4 + Y3**2)
    
    # create light source object.
    ls3 = LightSource(azdeg=0, altdeg=120)
    
    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    rgb3 = ls3.shade(Z3, plt.cm.Accent_r)
    
    fig3 = plt.figure(num=3, figsize=(9, 9), facecolor='silver', edgecolor='k')
    # plt.figure(figsize=(12, 5))
    plt.imshow(rgb3)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])

  
    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    X4, Y4 = np.mgrid[-11:11:0.01, -11:11:0.01]
    Z4 = np.sqrt(X4**2 + Y4**2) + np.cos(X4**3 + Y4**3)
    
    # create light source object.
    ls4 = LightSource(azdeg=0, altdeg=120)
    
    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    rgb4 = ls4.shade(Z4, plt.cm.prism)
    
    fig4 = plt.figure(num=4, figsize=(9, 9), facecolor='silver', edgecolor='k')
    # plt.figure(figsize=(12, 5))
    plt.imshow(rgb4)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])
    
    
    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    X5, Y5 = np.mgrid[-11:11:0.01, -11:11:0.01]
    Z5 = np.sqrt(X5**2 + Y5**2) + np.cos(X5**3 + Y5**3)
    
    # create light source object.
    ls5 = LightSource(azdeg=0, altdeg=36)
    
    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    rgb5 = ls5.shade(Z5, plt.cm.seismic_r)
    
    fig5 = plt.figure(num=5, figsize=(9, 9), facecolor='silver', edgecolor='k')
    # plt.figure(figsize=(12, 5))
    plt.imshow(rgb5)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])
    
    
    # test data
    #X, Y = np.mgrid[-5:5:0.05, -5:5:0.05]
    X6, Y6 = np.mgrid[-11:11:0.01, -11:11:0.01]
    Z6 = np.sqrt(X6**2 + Y6**2) + np.cos(X6**3 + Y6**3)
    
    # create light source object.
    ls6 = LightSource(azdeg=45, altdeg=36)
    
    #rgb = ls.shade(Z, plt.cm.gnuplot_r)
    rgb6 = ls6.shade(Z6, plt.cm.magma)
    
    fig6 = plt.figure(num=6, figsize=(9, 9), facecolor='silver', edgecolor='k')
    # plt.figure(figsize=(12, 5))
    plt.imshow(rgb6)
    plt.title('imshow')
    plt.xticks([])
    plt.yticks([])


# ::<<< color select >>>::
#prism
#afmhot_r
#Accent_r
#magma_r
#magma


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //