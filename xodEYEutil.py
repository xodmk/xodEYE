# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEYEutil.py))::__
#
# Python ODMK img processing utility functions
# Basic image processing function library
# Base library for odmkEYEu.py & odmkVIDEOu.py
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os
# import sys
import glob
import shutil
from math import floor, ceil
import random
import numpy as np
import scipy as sp
from scipy.signal import convolve2d
import imageio as imio
from scipy import ndimage
from PIL import Image
from PIL import ImageOps
# from PIL import ImageEnhance


# temp python debugger - use >>>pdb.set_trace() to set break
import pdb


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : utility function definitions
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def cyclicZn(n):
    """ calculates the Zn roots of unity """
    cZn = np.zeros((n, 1))*(0+0j)    # column vector of zero complex values
    for k in range(n):
        # z(k) = e^(((k)*2*pi*1j)/n)        # Define cyclic group Zn points
        cZn[k] = np.cos(((k)*2*np.pi)/n) + np.sin(((k)*2*np.pi)/n)*1j   # Euler's identity

    return cZn


def quarterCos(n):
    """ returns a quarter period cosine wav of length n """
    t = np.linspace(0, np.pi/4, n)
    qtrcos = np.zeros(n)
    for j in range(n):
        qtrcos[j] = sp.cos(t[j])
    return qtrcos


def randomIdx(k):
    """ returns a random index in range 0 - k-1 """
    randIdx = round(random.random()*(k-1))
    return randIdx


def randomIdxArray(n, k):
    """ for an array of k elements, returns a list of random elements
       of length n (n integers rangin from 0:k-1) """
    randIdxArray = []
    for i in range(n):
        randIdxArray.append(round(random.random()*(k-1)))
    return randIdxArray


def randomPxlLoc(SzX, SzY):
    """ Returns a random location in a 2D array of SzX by SzY """
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


class odmkFibonacci:
    """ Iterator that generates numbers in the Fibonacci sequence """

    def __init__(self, max):
        self.max = max

    def __iter__(self):
        self.a = 0
        self.b = 1
        return self

    def __next__(self):
        fib = self.a
        if fib > self.max:
            raise StopIteration
        self.a, self.b = self.b, self.a + self.b
        return fib


def genFileList(dirList):
    """ Returns a list of image file names """
    imgFileList = []
    for i in range(len(dirList)):
        imgFileList.extend(sorted(glob.glob(dirList[i]+'*')))
    return imgFileList


def getLatestIdx(imgDir, imgNm):
    f_list = []
    imagelist = glob.glob(imgDir+'/*.jpg')
    for s in imagelist:
        f_list.append(s.replace('\\', '/'))
    # f_list = glob.glob(imgDir+'/*.jpg')
    if not f_list:
        f_idx = 0
    else:
        f_latest = max(f_list, key=os.path.getctime)
        f_fname = os.path.split(f_latest)[1]
        f_idx = f_fname.replace(imgNm, '')
        f_idx = int(f_idx.replace('.jpg', ''))
        
    return f_idx


# generator - use next()
def genNextFilename(imgFileList):
    """ generates an incrementing sequence of filenames from imgFileList """
    j = 0
    while True:
        file_name = imgFileList[j]
        if j == (len(imgFileList)):
            j = 0
        else:
            j+=1
        yield file_name


def genRandFilename(imgFileList):
    """ generates a sequence of randomly selected filenames from imgFileList """
    while True:
        file_name = imgFileList[randomIdx(len(imgFileList))]
        yield file_name
                

def genRandBurstFilename(imgFileList, burst):
    """ generates a sequence of randomly selected filenames from imgFileList """
    while True:
        startIdx = randomIdx(len(imgFileList))
        for burstIdx in range(burst):
            file_name = imgFileList[(startIdx + burstIdx) % (len(imgFileList) - 1)]
        yield file_name


def circ_idx(idx, arrayLen):
    if idx >= arrayLen:
        circIdx = idx % arrayLen
    else:
        circIdx = idx
    return circIdx


def samples2frames(numSamples, sr, framesPerSec):
    return int((numSamples/sr) * framesPerSec)


def isValidPIL(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False


def xodRenameAll(srcDir, n_digits, dstName):

    try:
        next(os.scandir(srcDir))
    except:
        print('Soure directory is empty')
        return False

    nextInc = 0
    for count, filename in enumerate(os.listdir(srcDir)):

        nextInc += 1
        zr = ''  # reset lead-zero count to zero each itr
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr + str(nextInc)
        newNm = dstName + '_' + strInc + '.jpg'

        src = f"{srcDir}/{filename}"  # foldername/filename, if .py file is outside folder
        dst = f"{srcDir}/{newNm}"

        # rename() function will
        # rename all the files
        os.rename(src, dst)

    return


def grayConversion(image):
    grayValue = 0.07 * image[:, :, 2] + 0.72 * image[:, :, 1] + 0.21 * image[:, :, 0]
    gray_img = grayValue.astype(np.uint8)
    return gray_img


# // *--------------------------------------------------------------* //
# // *---:: XODMKEYE - concat all files in directory list::---*
# // *--------------------------------------------------------------* //

def convertJPGtoBMP(srcDir, outDir, reName='None'):
    """ converts .jpg  images to .bmp images,
        renames and concatenates all files into new arrays. """

    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*.jpg')))

    imgCount = len(imgFileList)
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0 
    for i in range(imgCount):
        imgObj = imio.imread(imgFileList[i])
        nextInc += 1
        zr = ''
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        imgNormalizeNm = reName+strInc+'.bmp'
        imgNmFull = os.path.join(outDir+imgNormalizeNm)
        imio.imwrite(imgNmFull, imgObj)
    return


def convertBMPtoJPG(srcDir, outDir, reName='None'):
    """ converts .bmp  images to .jpg images,
        renames and concatenates all files into new arrays. """

    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*.bmp')))

    imgCount = len(imgFileList)
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0 
    for i in range(imgCount):
        imgObj = imio.imread(imgFileList[i])
        nextInc += 1
        zr = ''
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        imgNormalizeNm = reName+strInc+'.jpg'
        imgNmFull = os.path.join(outDir+imgNormalizeNm)
        imio.imwrite(imgNmFull, imgObj)
    return


# // *--------------------------------------------------------------* //
# // *---:: XODEYE Utility Reshaping Functions ::---*
# // *--------------------------------------------------------------* //

def cropZoom(img, zoom_factor, **kwargs):
    SzY, SzX = img.shape[:2]

    # ensure that the final image is >=, then crop
    if SzX % 2 != 0:
        SzXX = SzX + 1
    else:
        SzXX = SzX

    if SzY % 2 != 0:
        SzYY = SzY + 1
    else:
        SzYY = SzY

    # width and height of the zoomed image
    # zoomSzY = int(np.round(zoom_factor * SzYY))
    # zoomSzX = int(np.round(zoom_factor * SzXX))

    # for multichannel images we don't want to apply the zoom factor to the RGB
    # dimension, so instead we create a tuple of zoom factors, one per array
    # dimension, with 1's for any trailing dimensions after the width and height.
    # *** (xxx,) * n => (xxx, xxx, ... xxx) repeated n times
    # zoom_tuple = (zoom_factor,) * 2 + (1,) * (img.ndim - 2)
    zoom_tuple = [zoom_factor, ] * 2 + [1, ] * (img.ndim - 2)  # outputs [2, 2, 1]

    # bounding box of the clip region within the input array
    # img[bottom:top, left:right] - crops image to range

    deltaX = SzXX // 4
    deltaY = SzYY // 4
    halfSzX = SzXX // 2
    halfSzY = SzYY // 2

    # out = ndimage.zoom(img[deltaY:zoomSzY - deltaY, deltaX:zoomSzX - deltaX], zoom_tuple, **kwargs)
    out = ndimage.zoom(img[deltaY:deltaY + halfSzY, deltaX:deltaX + halfSzX], zoom_tuple, **kwargs)

    # `out` might still be slightly larger than `img` due to rounding, so
    # trim off any extra pixels at the edges
    if out.shape[0] != SzY or out.shape[1] != SzX:
        out = out[0:SzY, 0:SzX]

    # if zoom_factor == 1, just return the input array
    else:
        out = img
    return out


def xodEyeCrop(img, SzX, SzY, high):
    """ crop img to SzX width x SzY height
        high: crops from center top [good for heads] """

    imgWidth = img.width
    imgHeight = img.height

    if imgWidth < SzX:
        print('ERROR: imgWidth is smaller than crop width')
        return 1
    elif imgWidth > SzX:
        cropLeft = floor((imgWidth - SzX) / 2)
    else:
        cropLeft = 0

    if imgHeight < SzY:
        print('ERROR: imgHeight is smaller than crop height')
        return 1
    elif imgHeight > SzY and high == 0:
        cropTop = floor((imgHeight - SzY) / 2)
    else:
        cropTop = 0

    # box=(left, upper, right, lower)
    if high == 1:
        imgCrop = img.crop((cropLeft, 0, cropLeft + SzX, SzY))
    else:
        imgCrop = img.crop((cropLeft, cropTop, cropLeft + SzX, cropTop + SzY))

    return imgCrop


def xodEyeReshape(img, SzX, SzY, high):
    """ Reshape img to SzX width x SzY height
        Detect closest dimension (X or Y) scale then crop or resize
        img: assumes PIL image format
        high: crops from center top [good for heads] """

    srcWidth = img.width
    srcHeight = img.height

    if srcWidth == SzX and srcHeight == SzY:
        return img

    expandX = 0
    expandY = 0
    compressX = 0
    compressY = 0
    xdiff = 0
    ydiff = 0
    cropLeft = 0
    cropTop = 0

    # Find minimum dimension difference
    if srcWidth < SzX:
        expandX = 1
        xdiff = np.abs(SzX - srcWidth)
    elif srcWidth > SzX:
        compressX = 1
        xdiff = np.abs(SzX - srcWidth)

    if srcHeight < SzY:
        expandY = 1
        ydiff = np.abs(SzY - srcHeight)
    elif srcHeight > SzY:
        compressY = 1
        ydiff = np.abs(SzY - srcHeight)

    # ** Resize if necessary **
    # calculate aspect ratio of src (X / Y):
    srcAspect = srcWidth / srcHeight

    # Expand: if either dimension is smaller than target, expand by the largest difference
    if expandX or expandY:
        if xdiff >= ydiff:
            newWidth = SzX
            newHeight = int(SzX / srcAspect)
            # crop vertical dimension
            cropTop = floor((newHeight - SzY) / 2)
        else:
            newWidth = int(SzY * srcAspect)
            # crop horizontal dimension
            cropLeft = floor((newWidth - SzX) / 2)
            newHeight = SzY
        imgResized = img.resize((newWidth, newHeight), Image.BICUBIC)

    # Compress: if either dimension is smaller than target, expand by the largest difference
    elif compressX or compressY:
        if xdiff <= ydiff:
            newWidth = SzX
            newHeight = int(SzX / srcAspect)
            # crop vertical dimension
            cropTop = floor((newHeight - SzY) / 2)
        else:
            newWidth = int(SzY * srcAspect)
            # crop horizontal dimension
            cropLeft = floor((newWidth - SzX) / 2)
            newHeight = SzY
        imgResized = img.resize((newWidth, newHeight), Image.BICUBIC)

    # ** Crop if necessary **
    # box=(left, upper, right, lower)
    if high == 1:
        imgReshape = imgResized.crop((cropLeft, 0, cropLeft + SzX, SzY))
    else:
        imgReshape = imgResized.crop((cropLeft, cropTop, cropLeft + SzX, cropTop + SzY))

    return imgReshape


# // *********************************************************************** //

def xodResizeAll(srcDir, SzX, SzY, outDir, imgOutNm='None', keepAspect='None'):
    """ resizes all .jpg files in srcDir
        keepAspect:
            width = uses SzX & auto calculates Y to preserve aspect ratio
            height = uses SzY & auto calculates X """

    try:
        next(os.scandir(srcDir))
    except:
        print('Soure directory is empty')
        return False

    try:
        os.path.isdir(outDir)
    except:
        print('Output directory is does not exist')
        return False

    if imgOutNm != 'None':
        imgScaledOutNm = imgOutNm
    else:
        imgScaledOutNm = 'xodResizeAllOut'

    # if keepAspect == width:

    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir + '*')))
    imgCount = len(imgFileList)
    # Find num digits required to represent max index
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    for k in range(imgCount):
        srcImg = Image.open(imgFileList[k])

        if keepAspect == 'width':
            scaleSzX = round(SzX)
            scaleSzY = round(scaleSzX * srcImg.size[1] / srcImg.size[0])
        elif keepAspect == 'height':
            scaleSzY = round(SzY)
            scaleSzX = round(scaleSzY * srcImg.size[0] / srcImg.size[1])
        else:
            scaleSzX = round(SzX)
            scaleSzY = round(SzY)

        imgScaled = srcImg.resize((scaleSzX, scaleSzY), Image.BICUBIC)
        # auto increment output file name
        nextInc += 1
        zr = ''  # reset lead-zero count to zero each itr
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr + str(nextInc)
        imgScaledNm = imgScaledOutNm + strInc + '.jpg'

        imgScaledFull = outDir + imgScaledNm
        imio.imwrite(imgScaledFull, imgScaled)

    return


def xodCropAll(srcDir, SzX, SzY, outDir, imgOutNm='None', high=0):
    """ crops all .jpg files in srcDir.
        high:
            0 = crops horizontally & vertically centered
            1 = crops from top==0, horizontally centered """

    try:
        next(os.scandir(srcDir))
    except:
        print('Soure directory is empty')
        return False

    try:
        os.path.isdir(outDir)
    except:
        print('Output directory is does not exist')
        return False

    if imgOutNm != 'None':
        imgCropOutNm = imgOutNm
    else:
        imgCropOutNm = 'xodCropOut'

    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir + '*')))
    imgCount = len(imgFileList)
    # Find num digits required to represent max index
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    for k in range(imgCount):
        srcImg = Image.open(imgFileList[k])

        imgCrop = xodEyeCrop(srcImg, SzX, SzY, high)

        # pdb.set_trace()

        # auto increment output file name
        nextInc += 1
        zr = ''  # reset lead-zero count to zero each itr
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr + str(nextInc)
        imgCropNm = imgCropOutNm + strInc + '.jpg'

        imgCropFull = outDir + imgCropNm
        imio.imwrite(imgCropFull, imgCrop)

    return


# // *********************************************************************** //
# // *---:: XODEYE Utility Rotation Functions ::---*
# // *********************************************************************** //

def eyeRotate(img, ang, rotd=0):
    """ example rotate image
        img: PIL image object
        ang = angle of rotation
        rotd: rotation direction - 0 = clock, 1 = anti-clock """

    SzX = img.width
    SzY = img.height

    rotScale = 1.618

    if rotd == 1:
        ang = -ang
    imgRot = img.resize((int(SzX * rotScale), int(SzY * rotScale)))

    # new center pixel
    cenX = int(imgRot.width / 2)
    cenY = int(imgRot.height / 2)

    imgRot = imgRot.rotate(ang, resample=Image.BICUBIC)
    imgRot = imgRot.crop((int(cenX - SzX / 2), int(cenY - SzY / 2),
                          int(cenX + SzX / 2), int(cenY + SzY / 2)))

    return imgRot


# // *********************************************************************** //    
# // *********************************************************************** //
# // *---:: XODEYE img Src Sequencing func::---*
# // *********************************************************************** //
# // *********************************************************************** //

# // *--------------------------------------------------------------* //
# // *---:: XODEYE - repeat list of files in directory n times::---*
# // *--------------------------------------------------------------* //


def repeatAllImg(srcDir, n, w=0, repeatDir='None', repeatName='None'):
    """ repeats a list of .jpg images in srcDir n times,
        duplicates and renames all files in the source directory.
        The new file names are formatted for processing with ffmpeg
        if w = 1, write files into output directory.
        if concatDir specified, change output dir name.
        if concatName specified, change output file names"""

    # check write condition, if w=0 ignore outDir
    if w == 0 and repeatDir != 'None':
        print('Warning: write = 0, outDir ignored')
    if w == 1:
        if repeatDir == 'None':
            print('Warning: if w=1, repeatDir must be specified; processed img will not be saved')
            w = 0
        else:
            # If Dir does not exist, makedir:
            os.makedirs(repeatDir, exist_ok=True)
            
    if repeatName != 'None':
        reName = repeatName
    else:
        reName = 'imgRepeat'

    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*')))
    imgCount = len(imgFileList)

    imgRepeatSrcList = []
    imgCount = len(imgFileList) * n
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    for i in range(n):
        for j in range(imgCount):
            nextInc += 1
            zr = ''
            for h in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgRepeatNm = reName+strInc+'.jpg'
            # append new name to imgConcatSrcList
            imgRepeatSrcList.append(imgFileList[j].replace(imgFileList[j], imgRepeatNm))
            imgRepeatNmFull = repeatDir+imgRepeatNm
            imgSrcTemp = imio.imread(imgFileList[j])
            imio.imwrite(imgRepeatNmFull, imgSrcTemp)

    return


# // *--------------------------------------------------------------* //
# // *---:: XODEYE - concat all files in directory list::---*
# // *--------------------------------------------------------------* //


def concatAllDir(dirList, concatDir, reName):
    """ Takes a list of directories containing .jpg /.bmp images,
        renames and concatenates all files into new arrays.
        The new file names are formatted for processing with ffmpeg
        if w = 1, write files into output directory.
        if concatDir specified, change output dir name.
        if concatName specified, change output file names"""
            
    imgFileList = []
    for i in range(len(dirList)):
        imgFileList.extend(sorted(glob.glob(dirList[i]+'*')))

    imgCount = len(imgFileList)
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    for i in range(imgCount):
        nextInc += 1
        zr = ''
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        imgNormalizeNm = reName+strInc+'.jpg'
        currentNm = os.path.split(imgFileList[i])[1]
        shutil.copy(imgFileList[i], concatDir)
        currentFile = os.path.join(concatDir+currentNm)
        imgConcatNmFull = os.path.join(concatDir+imgNormalizeNm)
        os.rename(currentFile, imgConcatNmFull)

    return


# // *--------------------------------------------------------------* //
# // *---:: XODEYE - interlace img files in two directoroies::---*
# // *--------------------------------------------------------------* //

def imgInterlaceDir(self, dir1, dir2, interlaceDir, reName):
    """ Takes two directories containing .jpg /.bmp images,
        renames and interlaces all files into output dir.
        The shortest directory length determines output (min length)"""

    imgFileList1 = []
    imgFileList2 = []

    if self.imgFormat == 'fjpg':
        imgFileList1.extend(sorted(glob.glob(dir1+'*.jpg')))
        imgFileList2.extend(sorted(glob.glob(dir2+'*.jpg')))    
    elif self.imgFormat == 'fbmp':
        imgFileList1.extend(sorted(glob.glob(dir1+'*.bmp')))
        imgFileList2.extend(sorted(glob.glob(dir2+'*.bmp')))     

    imgCount = 2*min(len(imgFileList1), len(imgFileList2))
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    dirIdx = 0
    for i in range(imgCount):
        nextInc += 1
        zr = ''
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        # print('strInc = '+str(strInc))
        if self.imgFormat == 'fjpg':
            imgNormalizeNm = reName+strInc+'.jpg' 
        elif self.imgFormat == 'fbmp':
            imgNormalizeNm = reName+strInc+'.bmp'
        # imgConcatNmFull = concatDir+imgNormalizeNm
        if i % 2 == 1:
            currentNm = os.path.split(imgFileList1[dirIdx])[1]
            shutil.copy(imgFileList1[dirIdx], interlaceDir)
            currentFile = os.path.join(interlaceDir+currentNm)
            dirIdx += 1
        else:
            currentNm = os.path.split(imgFileList2[dirIdx])[1]                
            shutil.copy(imgFileList2[dirIdx], interlaceDir)
            currentFile = os.path.join(interlaceDir+currentNm)
        
        imgInterlaceDirNmFull = os.path.join(interlaceDir+imgNormalizeNm)
        os.rename(currentFile, imgInterlaceDirNmFull)

    return


# // *--------------------------------------------------------------* //
# // *---:: XODEYE - interlace img files in two directoroies::---*
# // *--------------------------------------------------------------* //

def imgInterLaceBpmDir(self, dir1, dir2, interlaceDir, xfadeFrames, reName):
    """ Takes two directories containing .jpg /.bmp images,
        renames and interlaces all files into output dir.
        xfadeFrames specifies n frames for each switch
        length is determined by 2 * largest directory """

    imgFileList1 = []
    imgFileList2 = []

    if self.imgFormat == 'fjpg':
        imgFileList1.extend(sorted(glob.glob(dir1+'*.jpg')))
        imgFileList2.extend(sorted(glob.glob(dir2+'*.jpg')))    
    elif self.imgFormat == 'fbmp':
        imgFileList1.extend(sorted(glob.glob(dir1+'*.bmp')))
        imgFileList2.extend(sorted(glob.glob(dir2+'*.bmp')))     

    imgCount = 2*max(len(imgFileList1), len(imgFileList2))
    
    list1Count = len(imgFileList1)
    list2Count = len(imgFileList2)
    
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    dirIdx1 = 0
    dirIdx2 = 0
    sel = 0
    for i in range(imgCount):
        nextInc += 1
        zr = ''
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        # print('strInc = '+str(strInc))
        if self.imgFormat == 'fjpg':
            imgNormalizeNm = reName+strInc+'.jpg' 
        elif self.imgFormat == 'fbmp':
            imgNormalizeNm = reName+strInc+'.bmp'
        # imgConcatNmFull = concatDir+imgNormalizeNm
        if i % xfadeFrames == 0:
            sel = not sel
        if sel == 0: 
            currentNm = os.path.split(imgFileList1[dirIdx1 % list1Count])[1]
            shutil.copy(imgFileList1[dirIdx1 % list1Count], interlaceDir)
            currentFile = os.path.join(interlaceDir+currentNm)
            dirIdx1 += 1
        else:
            currentNm = os.path.split(imgFileList2[dirIdx2 % list2Count])[1]                
            shutil.copy(imgFileList2[dirIdx2 % list2Count], interlaceDir)
            currentFile = os.path.join(interlaceDir+currentNm)
            dirIdx2 += 1
        
        imgInterlaceDirNmFull = os.path.join(interlaceDir+imgNormalizeNm)
        os.rename(currentFile, imgInterlaceDirNmFull)

    return


# // *********************************************************************** //    
# // *********************************************************************** //
# // *---:: XODEYE Utility img Src Sequencing func::---*
# // *********************************************************************** //
# // *********************************************************************** //

def createLinearSeqArray(xodEyeDir, inputSrcDir):
    for sd in inputSrcDir:
        # print(str(i))
        p = lambda i: os.path.isdir(xodEyeDir + sd)
        if p:
            # print("Found src dir: " + xodEyeDir + sourceDir[i])
            print("Found src dir: " + xodEyeDir + sd)
        else:
            print("Error Source Dir doesn't exist: " + xodEyeDir + sd)
    imgSeqArray, imgSeqDir = createLinearSrcArray(xodEyeDir, inputSrcDir)

    print('\nCreated linear imgSeqArray: - Array of .jpg file paths\n')
    print("# of images in Array: " + str(len(imgSeqArray)))

    pdb.set_trace()

    print('\nCreated "imgSeqArray, imgSeqDir" => Array of .jpg file paths in source dir\n')
    return imgSeqArray, imgSeqDir


def createLinearSrcArray(eyeRootDir, sourceDir):
    srcDir = []
    imgSrcArray = []

    for d in range(len(sourceDir)):
        imgSeqArray = []
        sDirTmp = eyeRootDir + sourceDir[d]
        srcDir.append(sDirTmp)
        sortedDir = sorted(glob.glob(sDirTmp + '*'))
        for s in sortedDir:
            imgSeqArray.append(s.replace('\\', '/'))
        imgSrcArray.extend(imgSeqArray)

    return imgSrcArray, srcDir


def createMultiImgSeqArray(xodEyeDir, inputSrcDir):
    for sd in inputSrcDir:
        # print(str(i))
        p = lambda i: os.path.isdir(xodEyeDir + sd)
        if p:
            # print("Found src dir: " + xodEyeDir + sourceDir[i])
            print("Found src dir: " + xodEyeDir + sd)
        else:
            print("Error Source Dir doesn't exist: " + xodEyeDir + sd)
    multiSeqArray, multiSeqDir = createMultiSrcArray(xodEyeDir, inputSrcDir)
    print('\nCreated imgSrcArray: - Array of .jpg file paths\n')
    # pdb.set_trace()
    for q in range(len(multiSeqDir)):
        print(multiSeqDir[q])
        print("# of images in Multi Array: " + str(len(multiSeqArray[q])))
    return multiSeqArray, multiSeqDir


def createMultiSrcArray(eyeRootDir, sourceDir):
    multiSrcDir = []
    multiSeqArray = []

    for d in range(len(sourceDir)):
        tempSeqArray = []
        sDirTmp = eyeRootDir + sourceDir[d]
        multiSrcDir.append(sDirTmp)
        sortedDir = sorted(glob.glob(sDirTmp + '*'))
        for s in sortedDir:
            tempSeqArray.append(s.replace('\\', '/'))
        tempSeqArray.extend(tempSeqArray)
        multiSeqArray.append(tempSeqArray)

    return multiSeqArray, multiSrcDir


def scanImagDir(dirList, numFrames, xCtrl):
    """ scans image directory selection with xCtrl value
        dirList is a 2D list of n of (variable length list)
        output is a list sequence of length numFrames """
    
    # check xCtrl is bounded by len(dirList)
    if len(xCtrl) != numFrames:
        print('ERROR: length of xCtrl must equal length of src dir')
        return
        
    imgArray = [[] for i in range(len(dirList))]
    for i in range(len(dirList)):
        tmpArray = []
        tmpArray.extend(sorted(glob.glob(dirList[i]+'*')))
        # print('Length of imgArray'+str(i)+' = '+str(len(tmpArray)))
        imgArray[i] = tmpArray

    srcImgArray = []
    for i in range(numFrames):

        if xCtrl[i] > len(dirList):
            print('Warning: xCtrl value exceeds # of input src dir')
            xCtrl[i] = int(len(dirList))
        else:
            xCtrl[i] = int(xCtrl[i])

        xIdx = int(xCtrl[i])
        yIdx = int(circ_idx(i, len(imgArray[int(xCtrl[i])])))

        # srcDir length are arbitrary - read frames (% by srcDir length to roll) then inc corresponding index
        srcImgArray.append(imgArray[xIdx][yIdx])

    return srcImgArray


def pulseScanRnd(dirList, numFrames, pulseLen):
    """ Scans frames from a list of img directories, creates new renamed sequence
        pulse = log based array index ( np.logspace(...) )
        xLength - length of final sequence (seconds)
        framesPerSec - video frames per second
        framesPerBeat - video frames per beat (tempo sync)
        xCtrl - directory selector, quantized to # of src dir
        returns: imgArray - sequenced list of fullpath img names """

    # check xCtrl is bounded by len(dirList)
    if pulseLen > numFrames:
        print('ERROR: numFrames must be greater than pulseLen')
        return 1
        
    imgArray = [[] for i in range(len(dirList))]
    for i in range(len(dirList)):
        tmpArray = []
        tmpArray.extend(sorted(glob.glob(dirList[i]+'*')))
        imgArray[i] = tmpArray

    pulse = np.logspace(0.01, 2, pulseLen, dtype=int, endpoint=False)
      
    random.seed(56)
    xCtrl = 0
    xCtrlPrev = 0
    imgIdx = 0
    pulseIdx = 0

    srcImgArray = []
    for i in range(numFrames):
        if i % pulseLen == 0:
            xCtrlPrev = xCtrl
            xCtrl = random.randint(0, len(dirList)-1)
            while xCtrl == xCtrlPrev:
                xCtrl = random.randint(0, len(dirList)-1)
            ss=random.randint(0, len(imgArray[xCtrl]))
            pulseIdx = 0
        yIdx = int(circ_idx(ss + pulse[pulseIdx], len(imgArray[xCtrl])))
        assert xCtrl < len(dirList), "xCtrl = "+str(xCtrl)
        assert yIdx < len(imgArray[xCtrl]), "yIdx = "+str(yIdx)
        # print("pulseScanRnd: xCtrl = "+str(xCtrl)+", yIdx = "+str(yIdx)+", ss = "+str(ss))
        srcImgArray.append(imgArray[xCtrl][yIdx])
        pulseIdx += 1
        imgIdx += 1

    return srcImgArray


# XOD Rotate Color Function  
def xodColorRotate(img, rotateStep):
    """ rotateStep [0:1] - linear mix from 100%r -> 100%b etc.
        - red case:   (0%)r -> (33%)g -> (66%)b - (100%)r
        - green case: (0%)g -> (33%)b -> (66%)r - (100%)g
        - blue case:  (0%)b -> (33%)r -> (66%)g - (100%)b """

    if isinstance(img, Image.Image):
        
        if rotateStep < 0 or rotateStep > 1.0:
            print('ERROR: rotateStep must be in range [0:1]')
            return 1

        r, g, b = img.split()
        
        # case: 0% -> 33%
        if rotateStep < 0.333:
            mixVal = rotateStep * (1/0.333)
            # newR = (1 - mixVal) * r + mixVal * g
            newR = Image.blend(r, g, mixVal)
            # newG = (1 - mixVal) * g + mixVal * b
            newG = Image.blend(g, b, mixVal)
            # newB = (1 - mixVal) * b + mixVal * r
            newB = Image.blend(b, r, mixVal)
            
        # case: 33% -> 66%
        elif 0.333 <= rotateStep < 0.666:
            mixVal = (rotateStep - 0.333) * (2/0.666)
            if mixVal > 1.0:
                mixVal = 1.0
            # newR = (1 - mixVal) * g + mixVal * b
            newR = Image.blend(g, b, mixVal)
            # newG = (1 - mixVal) * b + mixVal * r
            newG = Image.blend(b, r, mixVal)
            # newB = (1 - mixVal) * r + mixVal * g
            newB = Image.blend(r, g, mixVal)

        # case: 66% -> 100%
        else:
            mixVal = (rotateStep - 0.666) * (1/0.333)
            if mixVal > 1.0:
                mixVal = 1.0
            # newR = (1 - mixVal) * b + mixVal * r
            newR = Image.blend(b, r, mixVal)
            # newG = (1 - mixVal) * r + mixVal * g
            newG = Image.blend(r, g, mixVal)
            # newB = (1 - mixVal) * g + mixVal * b
            newB = Image.blend(g, b, mixVal)

        return Image.merge('RGB', (newR, newG, newB))
    else:
        print('ERROR: source image must be PIL Image')
        return None


# // *--------------------------------------------------------------* //
# // *---:: XODEYE Utility Linear interpolate between frames::---*
# // *--------------------------------------------------------------* //

def xodFrameInterpolate(imgFileList, xfadeFrames, ctrl, n_digits,
                        imgOutDir, imgOutNm):
    """ Interpolate (blend) between frames in directory
        imgFileList - image source directory
        xfadeFrames - number of frames per xfade
        effx: 0 = linear fade, 1 = cosine fade
    """
    print('// __xodFrameInterpolate__ ')
        
    # if (???check for valid images in dir???):
    #    print('ERROR: directory does not contain valid images')
    #    return 1

    numImg = len(imgFileList)
    
    print('// *---numImg = '+str(numImg)+'---*')
    print('// *---xfadeFrames = '+str(xfadeFrames)+'---*')
    
    n_digits = int(ceil(np.log10(numImg * xfadeFrames))) + 2

    alphaX = np.linspace(0.0, 1.0, xfadeFrames + 1)
    if ctrl > 0:
        alphaCosX = (-np.cos(np.pi * alphaX) + 1) / 2
        
    frameCnt = 0
    for j in range(numImg - 1):
        
        imgPIL1 = Image.open(imgFileList[j])
        imgPIL2 = Image.open(imgFileList[j + 1])

        for i in range(xfadeFrames):
            if ctrl > 0:
                alphaB = Image.blend(imgPIL1, imgPIL2, alphaCosX[i])
            else:
                alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
            zr = ''
            for j in range(n_digits - len(str(frameCnt))):
                zr += '0'
            strInc = zr+str(frameCnt)
            imgFrameIFull = imgOutDir + imgOutNm + strInc+'.jpg'
            imio.imwrite(imgFrameIFull, alphaB)
            frameCnt += 1
    return


# // *--------------------------------------------------------------* //
# // *---::XODMKEYE - Stride interpolate between frames::---*
# // *--------------------------------------------------------------* //
    
def xodStrideInterpolate(imgFileList, xfadeFrames, effx, n_digits,
                         imgOutDir, imgOutNm):
    """ Interpolate (blend) between Strided frames in directory
        (stride - skips n frames each step)
        imgFileList - image source directory
        xfadeFrames - number of frames per xfade
        effx=>Stride: 2 or greater - use every stride frames
    """
    print('// __xodFrameInterpolate__ ')
        
    # if (???check for valid images in dir???):
    #    print('ERROR: directory does not contain valid images')
    #    return 1

    if effx < 2:
        print('ERROR - stride must be 2 or greater')
        return

    numImg = len(imgFileList)
    
    print('// *---numImg = '+str(numImg)+'---*')
    print('// *---xfadeFrames = '+str(xfadeFrames)+'---*')
    
    n_digits = int(ceil(np.log10(numImg * xfadeFrames))) + 2

    alphaX = np.linspace(0.0, 1.0, xfadeFrames + 1)
    alphaCosX = (-np.cos(np.pi * alphaX) + 1) / 2
    stride = effx
        
    frameCnt = 0
    idx = 0
    for j in range(numImg - 1):

        imgPIL1 = Image.open(imgFileList[circ_idx(idx, numImg)])
        imgPIL2 = Image.open(imgFileList[circ_idx(idx + stride, numImg)])

        for i in range(xfadeFrames):
            alphaB = Image.blend(imgPIL1, imgPIL2, alphaCosX[i])
            alphaB = ImageOps.autocontrast(alphaB, cutoff=0)
            zr = ''
            for j in range(n_digits - len(str(frameCnt))):
                zr += '0'
            strInc = zr+str(frameCnt)
            imgFrameIFull = imgOutDir + imgOutNm + strInc+'.jpg'
            imio.imwrite(imgFrameIFull, alphaB)
            frameCnt += 1
            
        idx = (idx + stride) % numImg
        
    return


# // *********************************************************************** //    
# // *********************************************************************** //
# // *---:: XODMK img Pixel-Banging Basic Func::---*
# // *********************************************************************** //
# // *********************************************************************** //

def eyeSubInsert(imgBase1, imgBase2, imgSub1, imgSub2, SzX, SzY, nDimX, nDimY, alphaX):
    """ inserts subframe images into base images & blends """

    # region = (left, upper, right, lower)
    # subbox = (i + 1, i + 1, newDimX, newDimY)
    r = 0
    for j in range(SzY):
        s = 0
        for k in range(SzX):

            if (j >= ((SzY - 1) - nDimY) / 2) and (j < ((SzY - 1) - ((SzY - 1) - nDimY) / 2)) \
                    and (k >= ((SzX - 1) - nDimX) / 2) and (k < ((SzX - 1) - ((SzX - 1) - nDimX) / 2)):
                                                
                # if (j==1058 or r==1058):
                #    print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                #    pdb.set_trace()                                                                
                                                
                imgBase1[j, k, :] = imgSub1[r, s, :]
                imgBase2[j, k, :] = imgSub2[r, s, :]
                
            if (k >= (SzX-nDimX)/2) and (k < (SzX - (SzX-nDimX)/2)):
                s += 1
        if (j >= (SzY-nDimY)/2) and (j < (SzY - (SzY-nDimY)/2)):
            r += 1

    imgModOut = Image.blend(Image.fromarray(imgBase1), Image.fromarray(imgBase2), alphaX)
    # imgBpTscOut = self.eyePhiFrame1(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2))
    imgModOut = ImageOps.autocontrast(imgModOut, cutoff=0)
    
    return imgModOut


def eyeBox1(img1, img2, boxSzX, boxSzY, pxlLoc, alpha):
    """ alpha blends random box from img2 onto img1
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 """

    if img1.size != img2.size:
        print('ERROR: img1, img2 must be same Dim')
        return        
   
    SzX = img1.size[0]
    SzY = img1.size[1]

    subDim_L = int(pxlLoc[0] - boxSzX//2)
    if subDim_L < 0:
        subDim_L = 0
    subDim_R = int(pxlLoc[0] + boxSzX//2)
    if subDim_R > SzX:
        subDim_R = SzX-1
    subDim_B = int(pxlLoc[1] - boxSzY//2)
    if subDim_B < 0:
        subDim_B = 0
    subDim_T = int(pxlLoc[1] + boxSzX//2)
    if subDim_T > SzY:
        subDim_T = SzY-1

    # coordinates = (left, lower, right, upper)
    boxCC = (subDim_L, subDim_B, subDim_R, subDim_T)
    
    if alpha == 1:
        eyeSubCC = img2.copy().crop(boxCC)       

    else:        
        eyeSub1 = img1.copy().crop(boxCC)
        eyeSub2 = img2.copy().crop(boxCC)    

        eyeSubCC = Image.blend(eyeSub1, eyeSub2, alpha)
        eyeSubCC = ImageOps.autocontrast(eyeSubCC, cutoff=0)

    # print('eyeSubCC X = '+str(eyeSubCC.shape[1])+', eyeSubCC Y = '+str(eyeSubCC.shape[0])+)
    # pdb.set_trace()

    img1.paste(eyeSubCC, boxCC)

    return img1


# // *********************************************************************** //
# // *---:: Xod Mirror Functions ::---*
# // *********************************************************************** //


def eyeMirrorLR(img, ctrl='LL', fullscl=0):
    """ Selects a quadrant from source image, mirrors H & V
        * img: PIL image object
        * ctrl: { UL, UR, LL, LR} - selects base quadrant
          Default output dimension = input dimension
        * resizeX, resizeY: forces a new output image dimention
        * fullscl: if > 0 scales full image & repeats in 4 quadrants
          Default: crops image to base quadrant & repeats cropped image
        Usage:
        mirrorQuadTest1 = eyeutil.eyeMirrorQuad(eye5img)
        mirrorQuadTest2 = eyeutil.eyeMirrorQuad(eye5img, ctrl='LR')
        mirrorQuadTest5 = eyeutil.eyeMirrorQuad(eye5img, ctrl='UL', fullscl=1)
    """

    if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
        print('ERROR: ctrl must be {UL, UR, LL, LR} <string>')
        return

    # calculate subDim as Quater frame of source image
    SzX = img.size[0]
    SzY = img.size[1]
        
    SzXD2 = int(SzX/2)
    SzYD2 = int(SzY/2)
    imgDim = (SzX, SzY)
    subDim = (SzXD2, SzYD2)
    
    # Plus extra index max+1 (why...)
    # box=( (left, upper) , (right, lower) )
    boxUL = (0,0, SzXD2, SzYD2)
    boxUR = (SzXD2, 0, SzX, SzYD2) 
    boxLL = (0, SzYD2, SzXD2, SzY)
    boxLR = (SzXD2, SzYD2, SzX, SzY)
        
    mirrorImg = Image.new('RGB', imgDim)  # e.g. ('RGB', (640, 480))

    if ctrl == 'LL':
        
        if fullscl > 0:
            # use full scaled image
            imgX = img.resize(subDim)
        else:
            # use cropped quadrant image
            # box=(left, upper, right, lower)
            imgX = img.crop((0, SzYD2, SzXD2, SzY))
        
        eyeSubUL = imgX
        eyeSubUR = ImageOps.mirror(imgX)
        eyeSubLL = ImageOps.flip(imgX)
        eyeSubLR = ImageOps.flip(imgX)
        eyeSubLR = ImageOps.mirror(eyeSubLR)        

    if ctrl == 'LR':
        
        if fullscl > 0:
            imgX = img.resize(subDim)
        else:
            imgX = img.resize(imgDim)
            imgX = img.crop((SzXD2, SzYD2, SzX, SzY))
        
        eyeSubUL = ImageOps.mirror(imgX)
        eyeSubUR = imgX
        eyeSubLL = ImageOps.flip(imgX)
        eyeSubLL = ImageOps.mirror(eyeSubLL)
        eyeSubLR = ImageOps.flip(imgX)

    if ctrl == 'UL':
        
        if fullscl > 0:
            imgX = img.resize(subDim)
        else:
            imgX = img.resize(imgDim)
            imgX = img.crop((0, 0, SzXD2, SzYD2))
        
        eyeSubUL = ImageOps.flip(imgX)
        eyeSubUR = ImageOps.flip(imgX)
        eyeSubUR = ImageOps.mirror(eyeSubUR)
        eyeSubLL = imgX
        eyeSubLR = ImageOps.mirror(imgX)

    if ctrl == 'UR':
        
        if fullscl > 0:
            # use full scaled image
            imgX = img.resize(subDim)
        else:
            imgX = img.resize(imgDim)
            # use cropped quadrant image
            # box=(left, upper, right, lower)
            imgX = img.crop((SzXD2, 0, SzX, SzYD2))
        
        eyeSubUL = ImageOps.flip(imgX)
        eyeSubUL = ImageOps.mirror(eyeSubUL)
        eyeSubUR = ImageOps.flip(imgX)
        eyeSubLL = ImageOps.mirror(imgX)
        eyeSubLR = imgX

    mirrorImg.paste(eyeSubUL, boxUL)
    mirrorImg.paste(eyeSubUR, boxUR)
    mirrorImg.paste(eyeSubLL, boxLL)
    mirrorImg.paste(eyeSubLR, boxLR)
    
    return mirrorImg


def eyeMirrorQuad(img, ctrl='LL', fullscl=0):
    """ Selects a quadrant from source image, mirrors H & V
        * img: PIL image object
        * ctrl: { UL, UR, LL, LR} - selects base quadrant
          Default output dimension = input dimension
        * resizeX, resizeY: forces a new output image dimention
        * fullscl: if > 0 scales full image & repeats in 4 quadrants
          Default: crops image to base quadrant & repeats cropped image
        Usage:
        mirrorQuadTest1 = eyeutil.eyeMirrorQuad(eye5img)
        mirrorQuadTest2 = eyeutil.eyeMirrorQuad(eye5img, ctrl='LR')
        mirrorQuadTest5 = eyeutil.eyeMirrorQuad(eye5img, ctrl='UL', fullscl=1)
    """

    if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
        print('ERROR: ctrl must be {UL, UR, LL, LR} <string>')
        return

    # calculate subDim as Quater frame of source image
    SzX = img.size[0]
    SzY = img.size[1]
        
    SzXD2 = int(SzX/2)
    SzYD2 = int(SzY/2)
    imgDim = (SzX, SzY)
    subDim = (SzXD2, SzYD2)
    
    # Plus extra index max+1 (why...)
    # box=( (left, upper) , (right, lower) )
    boxUL = (0,0, SzXD2, SzYD2)
    boxUR = (SzXD2, 0, SzX, SzYD2) 
    boxLL = (0, SzYD2, SzXD2, SzY)
    boxLR = (SzXD2, SzYD2, SzX, SzY)
        
    mirrorImg = Image.new('RGB', imgDim)  # e.g. ('RGB', (640, 480))

    if ctrl == 'LL':
        
        if fullscl > 0:
            # use full scaled image
            imgX = img.resize(subDim)
        else:
            # use cropped quadrant image
            # box=(left, upper, right, lower)
            imgX = img.crop((0, SzYD2, SzXD2, SzY))
        
        eyeSubUL = imgX
        eyeSubUR = ImageOps.mirror(imgX)
        eyeSubLL = ImageOps.flip(imgX)
        eyeSubLR = ImageOps.flip(imgX)
        eyeSubLR = ImageOps.mirror(eyeSubLR)        

    if ctrl == 'LR':
        
        if fullscl > 0:
            imgX = img.resize(subDim)
        else:
            imgX = img.resize(imgDim)
            imgX = img.crop((SzXD2, SzYD2, SzX, SzY))
        
        eyeSubUL = ImageOps.mirror(imgX)
        eyeSubUR = imgX
        eyeSubLL = ImageOps.flip(imgX)
        eyeSubLL = ImageOps.mirror(eyeSubLL)
        eyeSubLR = ImageOps.flip(imgX)

    if ctrl == 'UL':
        
        if fullscl > 0:
            imgX = img.resize(subDim)
        else:
            imgX = img.resize(imgDim)
            imgX = img.crop((0, 0, SzXD2, SzYD2))
        
        eyeSubUL = ImageOps.flip(imgX)
        eyeSubUR = ImageOps.flip(imgX)
        eyeSubUR = ImageOps.mirror(eyeSubUR)
        eyeSubLL = imgX
        eyeSubLR = ImageOps.mirror(imgX)

    if ctrl == 'UR':
        
        if fullscl > 0:
            # use full scaled image
            imgX = img.resize(subDim)
        else:
            imgX = img.resize(imgDim)
            # use cropped quadrant image
            # box=(left, upper, right, lower)
            imgX = img.crop((SzXD2, 0, SzX, SzYD2))
        
        eyeSubUL = ImageOps.flip(imgX)
        eyeSubUL = ImageOps.mirror(eyeSubUL)
        eyeSubUR = ImageOps.flip(imgX)
        eyeSubLL = ImageOps.mirror(imgX)
        eyeSubLR = imgX

    mirrorImg.paste(eyeSubUL, boxUL)
    mirrorImg.paste(eyeSubUR, boxUR)
    mirrorImg.paste(eyeSubLL, boxLL)
    mirrorImg.paste(eyeSubLR, boxLR)
    
    return mirrorImg


# // *********************************************************************** //
# // *---:: Xod Mirror Functions ::---*
# // *********************************************************************** //


def eyePhiHorizFrame1(img1, img2, img3, ctrl=1):
    """ generates composite 4 frame resized images
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 """

    if (img1.size != img2.size != img3.size):
        print('ERROR: img1, img2 must be same Dim')
        return        

    # phi = 1.6180339887
    phiInv = 0.6180339887
    oneMphiInv = 0.38196601129
   
    SzX = img1.size[0]
    SzY = img1.size[1]
    imgDim = [SzX, SzY]
    
    # toggle background on/off
    if ctrl == 0:
        phiFrameImg = Image.new('RGB', imgDim)  # e.g. ('RGB', (640, 480)) 
    else:    
        phiFrameImg = img1.copy()   
    
    dimH_L = int(SzX*oneMphiInv)
    dimH_R = int(SzX*phiInv)
    
    dimC_B = int(SzY*oneMphiInv)
    dimC_T = int(SzY*phiInv)
    
    dimCC_L = int(dimH_L/2)
    dimCC_R = SzX - int(dimH_L/2)
    dimCC_B = int(dimC_B/2)
    dimCC_T = SzY - int(dimC_B/2)    

    # coordinates = (left, lower, right, upper)
#    boxL = (0, 0, dimH_L, SzY)
#    boxC = (dimH_L, 0, dimH_R, SzY)
#    boxR = (dimH_R, 0, dimH_R, SzY)    
#    
#    boxC_B = (dimH_L, dimC_T, dimH_R, SzY)
#    boxC_T = (dimH_L, 0, dimH_R, dimC_B)    
  
    boxCC = (dimCC_L, dimCC_B, dimCC_R, dimCC_T)

    boxL_B = (0, dimC_T, dimH_L, SzY)
    boxL_T = (0, 0, dimH_L, dimC_B)
    
    boxR_B = (dimH_R, dimC_T, SzX, SzY)
    boxR_T = (dimH_R, 0, SzX, dimC_B)

    eyeSubLT = img1.copy().crop(boxL_T)
    eyeSubLB = img2.copy().crop(boxL_B)
    
    # eyeSubTC = img2.resize(subDim)
    # eyeSubBC = img2.copy().crop(boxC_B)

    eyeSubRT = img2.copy().crop(boxR_T)
    eyeSubRB = img1.copy().crop(boxR_B) 

    subDimCC = (dimCC_R - int(dimH_L/2), dimCC_T - int(dimC_B/2))

    eyeSubCC = img1.copy().resize(subDimCC)
    eyeSubCC2 = img2.copy().resize(subDimCC)
    eyeSubCC = Image.blend(eyeSubCC, eyeSubCC2, 0.5)
    eyeSubCC = ImageOps.autocontrast(eyeSubCC, cutoff=0)

    # left frame
    phiFrameImg.paste(eyeSubLT, boxL_T)
    phiFrameImg.paste(eyeSubLB, boxL_B)
    
    # rigth frame
    phiFrameImg.paste(eyeSubRT, boxR_T)
    phiFrameImg.paste(eyeSubRB, boxR_B)

    # center frame
    # phiFrameImg.paste(eyeSubTC, boxC_T)
    # phiFrameImg.paste(eyeSubBC, boxC_B)
    
    # center center
    phiFrameImg.paste(eyeSubCC, boxCC)

    # eyeOutFileName = 'eyeMirrorHV4'
    # eyeMirrorHV4Full = imgOutDir+eyeOutFileName+'.jpg'
    # misc.imsave(eyeMirrorHV4Full, mirrorImg)
    
    return phiFrameImg


def eyePhiFrame1(img1, img2, ctrl=1):
    """ generates composite 4 frame resized images
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 """

    if img1.size != img2.size:
        print('ERROR: img1, img2 must be same Dim')
        return        

    # phi = 1.6180339887
    phiInv = 0.6180339887
    oneMphiInv = 0.38196601129
   
    SzX = img1.size[0]
    SzY = img1.size[1]
    imgDim = [SzX, SzY]
    
    # toggle background on/off
    if ctrl == 0:
        phiFrameImg = Image.new('RGB', imgDim)  # e.g. ('RGB', (640, 480)) 
    else:    
        phiFrameImg = img1.copy()   
    
    dimH_L = int(SzX*oneMphiInv)
    dimH_R = int(SzX*phiInv)
    
    dimC_B = int(SzY*oneMphiInv)
    dimC_T = int(SzY*phiInv)
    
    dimCC_L = int(dimH_L/2)
    dimCC_R = SzX - int(dimH_L/2)
    dimCC_B = int(dimC_B/2)
    dimCC_T = SzY - int(dimC_B/2)    

    # coordinates = (left, lower, right, upper)
#    boxL = (0, 0, dimH_L, SzY)
#    boxC = (dimH_L, 0, dimH_R, SzY)
#    boxR = (dimH_R, 0, dimH_R, SzY)    
#    
#    boxC_B = (dimH_L, dimC_T, dimH_R, SzY)
#    boxC_T = (dimH_L, 0, dimH_R, dimC_B)    
  
    boxCC = (dimCC_L, dimCC_B, dimCC_R, dimCC_T)

    boxL_B = (0, dimC_T, dimH_L, SzY)
    boxL_T = (0, 0, dimH_L, dimC_B)
    
    boxR_B = (dimH_R, dimC_T, SzX, SzY)
    boxR_T = (dimH_R, 0, SzX, dimC_B)

    eyeSubLT = img1.copy().crop(boxL_T)
    eyeSubLB = img2.copy().crop(boxL_B)
    
    # eyeSubTC = img2.resize(subDim)
    # eyeSubBC = img2.copy().crop(boxC_B)

    eyeSubRT = img2.copy().crop(boxR_T)
    eyeSubRB = img1.copy().crop(boxR_B) 

    subDimCC = (dimCC_R - int(dimH_L/2), dimCC_T - int(dimC_B/2))

    eyeSubCC = img1.copy().resize(subDimCC)
    eyeSubCC2 = img2.copy().resize(subDimCC)
    eyeSubCC = Image.blend(eyeSubCC, eyeSubCC2, 0.5)
    eyeSubCC = ImageOps.autocontrast(eyeSubCC, cutoff=0)

    # left frame
    phiFrameImg.paste(eyeSubLT, boxL_T)
    phiFrameImg.paste(eyeSubLB, boxL_B)
    
    # rigth frame
    phiFrameImg.paste(eyeSubRT, boxR_T)
    phiFrameImg.paste(eyeSubRB, boxR_B)

    # center frame
    # phiFrameImg.paste(eyeSubTC, boxC_T)
    # phiFrameImg.paste(eyeSubBC, boxC_B)
    
    # center center
    phiFrameImg.paste(eyeSubCC, boxCC)

    # eyeOutFileName = 'eyeMirrorHV4'
    # eyeMirrorHV4Full = imgOutDir+eyeOutFileName+'.jpg'
    # misc.imsave(eyeMirrorHV4Full, mirrorImg)
    
    return phiFrameImg


def eyePhiFrame2(img1, img2, ctrl='UL'):
    """ generates subframes increasing by fibonacci sequence
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 """

    if not(ctrl == 'UL' or ctrl == 'UR' or ctrl == 'LL' or ctrl == 'LR'):
        print('ERROR: ctrl must be {UL, UR, LL, LR} <string>')
        return

    if img1.size != img2.size:
        print('ERROR: img1, img2 must be same Dim')
        return        

    SzX = img1.size[0]
    SzY = img1.size[1]
    imgDim = [SzX, SzY]
    
    # coordinates = (left, lower, right, upper)

    if ctrl == 'LL':
        boxQTR = (0, int(SzY/2), int(SzX/2), SzY)        
    elif ctrl == 'LR':
        boxQTR = (int(SzX/2), int(SzY/2), SzX, SzY)        
    elif ctrl == 'UL':
        boxQTR = (0, 0, int(SzX/2), int(SzY/2))
    elif ctrl == 'UR':
        boxQTR = (int(SzX/2), 0, SzX, int(SzY/2))

    phiFrameImg = img1.copy()
    phiSubImg1 = img1.copy().crop(boxQTR)
    phiSubImg1 = phiSubImg1.resize(imgDim)
    phiSubImg2 = img2.copy().crop(boxQTR)
    phiSubImg2 = phiSubImg2.resize(imgDim)

    dimXarray = []
    for xx in odmkFibonacci(SzX):
        if xx > 8:
            dimXarray.append(xx)
            # print(str(xx))
            
    dimYarray = []
    for yy in dimXarray:
        dimYarray.append(int(yy*SzY/SzX))

    for bb in range(len(dimXarray)):
        
        if bb % 2 == 1:
            boxBB = (0, 0, dimXarray[len(dimXarray) - bb - 1], dimYarray[len(dimYarray) - bb - 1])
            eyeSub = phiSubImg1.copy().crop(boxBB)
            phiFrameImg.paste(eyeSub, boxBB)
        else:
            boxBB = (0, 0, dimXarray[len(dimXarray) - bb - 1], dimYarray[len(dimYarray) - bb - 1])
            eyeSub = phiSubImg2.copy().crop(boxBB)
            phiFrameImg.paste(eyeSub, boxBB)

    return phiFrameImg


def eyeSobelXY(img):
    """ 2D Convolution Sobel filter (edge detect) """

    sobel_x = np.c_[
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ]
    
    sobel_y = np.c_[
        [1, 2, 1],
        [0, 0, 0],
        [-1, -2, -1]
    ]
    
    ims = []
    for d in range(3):
        sx = convolve2d(img[:, :, d], sobel_x, mode="same", boundary="symm")
        sy = convolve2d(img[:, :, d], sobel_y, mode="same", boundary="symm")
        ims.append(np.sqrt(sx*sx + sy*sy))
    
    im_conv = np.stack(ims, axis=2).astype("uint8")
    
    return im_conv


def median_filter_rgb(im_small, window_size):
    """ Applies a median filer to all colour channels """
    ims = []
    for d in range(3):
        im_conv_d = ndimage.median_filter(im_small[:, :, d], size=(window_size, window_size))
        ims.append(im_conv_d)

    im_conv = np.stack(ims, axis=2).astype("uint8")
    
    return im_conv


# // *********************************************************************** //
# // *---:: ODMK Masking Functions ::---*
# // *********************************************************************** //


def eyeMask2Ch(mask, img1, img2):
    """ mask multiplexor: pos/neg mask region mux
        inputs are numpy 2D array RGB stackd
        works clean with black/white mask,
        also produces funk results with random color image for mask """

    if not(img1.shape[0] == img2.shape[0] and img1.shape[1] == img2.shape[1] and
           img1.shape[0] == mask.shape[0] and img1.shape[1] == mask.shape[1]):
        print('ERROR: image & mask sizes must be equl')
        return
    
    mask = mask / 255
    dstPos = img1 * mask
    dstNeg = img2 * (1-mask)
    dst = np.sqrt((dstPos**2) + (dstNeg**2))
    eyeOut = dst.astype(np.uint8)
    
    return eyeOut


# // *********************************************************************** //
# // *********************************************************************** //
