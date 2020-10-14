# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header begin-----------------------------------------------------------------
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
# header end-------------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os, sys
import glob, shutil
from math import floor, ceil
import random
import numpy as np
import scipy as sp
from scipy.signal import convolve2d
import imageio as imio
from scipy import ndimage
#from scipy import misc
from PIL import Image
from PIL import ImageOps
#from PIL import ImageEnhance


rootDir = '../'


#sys.path.insert(0, 'C:/odmkDev/odmkCode/odmkPython/util')
sys.path.insert(0, rootDir+'util')


# temp python debugger - use >>>pdb.set_trace() to set break
import pdb



# // *---------------------------------------------------------------------* //
#clear_all()

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


class odmkFibonacci:
    ''' Iterator that generates numbers in the Fibonacci sequence '''

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
    ''' Returns a list of image file names '''
    imgFileList = []
    for i in range(len(dirList)):
        imgFileList.extend(sorted(glob.glob(dirList[i]+'*')))
    return imgFileList


def getLatestIdx(imgDir, imgNm):
    f_list = glob.glob(imgDir+'/*.jpg')
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
    """
    generates an incrementing sequence of filenames from imgFileList
    """
    j = 0
    while True:
        file_name = imgFileList[j]
        if j == (len(imgFileList)):
            j = 0
        else:
            j+=1
        yield file_name



def genRandFilename(imgFileList):
    """
    generates a sequence of randomly selected filenames from imgFileList
    """
    while True:
        file_name = imgFileList[randomIdx(len(imgFileList))]
        yield file_name
                

def genRandBurstFilename(imgFileList, burst):
    """
    generates a sequence of randomly selected filenames from imgFileList
    """
    while True:
        startIdx = randomIdx(len(imgFileList))
        for burstIdx in range(burst):
            file_name = imgFileList[(startIdx + burstIdx) % (len(imgFileList) - 1)]
        yield file_name


def xodResizeAll(srcDir, SzX, SzY, outDir, outName='None'):
    ''' resizes all .jpg files in image object list. '''


    os.makedirs(outDir, exist_ok=True)
    
    if outName != 'None':
        imgScaledOutNm = outName
    else:
        imgScaledOutNm = 'xodResizeAllOut'

        
    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*')))
    imgCount = len(imgFileList)
    # Find num digits required to represent max index
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    for k in range(imgCount):
        srcImg = Image.open(imgFileList[k])
        imgScaled = srcImg.resize((SzX, SzY), Image.BICUBIC)
        # auto increment output file name
        nextInc += 1
        zr = ''    # reset lead-zero count to zero each itr
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        imgScaledNm = imgScaledOutNm+strInc+'.jpg'

        imgScaledFull = outDir+imgScaledNm
        imio.imwrite(imgScaledFull, imgScaled)


    return


def odmkScaleAll(srcDir, SzX, SzY, outDir, outName='None', high=0):
    ''' rescales and normalizes all .jpg files in image object list.
        scales, zooms, & crops images to dimensions SzX, SzY
        Assumes srcObjList of ndimage objects exists in program memory
        Typically importAllJpg is run first. '''


    os.makedirs(outDir, exist_ok=True)
    
    if outName != 'None':
        imgScaledOutNm = outName
    else:
        imgScaledOutNm = 'odmkScaleAllOut'

        
    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*')))
    imgCount = len(imgFileList)
    # Find num digits required to represent max index
    n_digits = int(ceil(np.log10(imgCount))) + 2
    #nextInc = 0
    nextInc = 1441
    for k in range(imgCount):
        srcObj = imio.imread(imgFileList[k])
        imgScaled = odmkEyeDim(srcObj, SzX, SzY, high)
        # auto increment output file name
        nextInc += 1
        zr = ''    # reset lead-zero count to zero each itr
        for j in range(n_digits - len(str(nextInc))):
            zr += '0'
        strInc = zr+str(nextInc)
        imgScaledNm = imgScaledOutNm+strInc+'.jpg'

        imgScaledFull = outDir+imgScaledNm
        imio.imwrite(imgScaledFull, imgScaled)


    return



# // *--------------------------------------------------------------* //
# // *---::ODMKEYE - concat all files in directory list::---*
# // *--------------------------------------------------------------* //


def convertJPGtoBMP(srcDir, outDir, reName='None'):
    ''' converts .jpg  images to .bmp images,
        renames and concatenates all files into new arrays. '''


    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*.jpg')))

    #pdb.set_trace()

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
    ''' converts .bmp  images to .jpg images,
        renames and concatenates all files into new arrays. '''


    imgFileList = []
    imgFileList.extend(sorted(glob.glob(srcDir+'*.bmp')))

    #pdb.set_trace()

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



# // *********************************************************************** //    
# // *********************************************************************** //
# // *---::ODMK img Src Sequencing func::---*
# // *********************************************************************** //
# // *********************************************************************** //




# // *--------------------------------------------------------------* //
# // *---::ODMKEYE - repeat list of files in directory n times::---*
# // *--------------------------------------------------------------* //


def repeatAllImg(srcDir, n, w=0, repeatDir='None', repeatName='None'):
    ''' repeats a list of .jpg images in srcDir n times,
        duplicates and renames all files in the source directory.
        The new file names are formatted for processing with ffmpeg
        if w = 1, write files into output directory.
        if concatDir specified, change output dir name.
        if concatName specified, change output file names'''

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

    #return imgRepeatSrcList
    return




# // *--------------------------------------------------------------* //
# // *---::ODMKEYE - concat all files in directory list::---*
# // *--------------------------------------------------------------* //


def concatAllDir(dirList, concatDir, reName):
    ''' Takes a list of directories containing .jpg /.bmp images,
        renames and concatenates all files into new arrays.
        The new file names are formatted for processing with ffmpeg
        if w = 1, write files into output directory.
        if concatDir specified, change output dir name.
        if concatName specified, change output file names'''
            
    imgFileList = []
    for i in range(len(dirList)):
        imgFileList.extend(sorted(glob.glob(dirList[i]+'*')))                
            
    #pdb.set_trace()

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
# // *---::ODMKEYE - interlace img files in two directoroies::---*
# // *--------------------------------------------------------------* //

def imgInterlaceDir(self, dir1, dir2, interlaceDir, reName):
    ''' Takes two directories containing .jpg /.bmp images,
        renames and interlaces all files into output dir. 
        The shortest directory length determines output (min length)'''


    imgFileList1 = []
    imgFileList2 = []
    

    if self.imgFormat=='fjpg':
        imgFileList1.extend(sorted(glob.glob(dir1+'*.jpg')))
        imgFileList2.extend(sorted(glob.glob(dir2+'*.jpg')))    
    elif self.imgFormat=='fbmp':
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
        if self.imgFormat=='fjpg':
            imgNormalizeNm = reName+strInc+'.jpg' 
        elif self.imgFormat=='fbmp':
            imgNormalizeNm = reName+strInc+'.bmp'
        #imgConcatNmFull = concatDir+imgNormalizeNm
        if i%2 == 1: 
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
        #pdb.set_trace()

    return




# // *********************************************************************** //    
# // *********************************************************************** //
# // *---::ODMK img Src Sequencing func::---*
# // *********************************************************************** //
# // *********************************************************************** //


def circ_idx(idx, arrayLen):
    if idx >= arrayLen:
        circIdx = idx % arrayLen
    else:
        circIdx = idx
    return circIdx


def scanImagDir(dirList, numFrames, xCtrl):
    ''' scans image directory selection with xCtrl value
        dirList is a 2D list of n of (variable length list) 
        output is a list sequence of length numFrames '''
    
    #genObjx = scanImgDirGen
    
        # check xCtrl is bounded by len(dirList)
    if (len(xCtrl) != numFrames):
        print('ERROR: length of xCtrl must equal length of src dir')
        return
        
    imgArray = [[] for i in range(len(dirList))]
    for i in range(len(dirList)):
        tmpArray = []
        tmpArray.extend(sorted(glob.glob(dirList[i]+'*')))
        # print('Length of imgArray'+str(i)+' = '+str(len(tmpArray)))
        imgArray[i] = tmpArray

    #pdb.set_trace()
    
    
    srcImgArray = []
    for i in range(numFrames):

        if (xCtrl[i] > len(dirList)):
            print('Warning: xCtrl value exceeds # of input src dir')
            xCtrl[i] = int(len(dirList))
        else:
            xCtrl[i] =int(xCtrl[i])

        xIdx = int(xCtrl[i])
        yIdx = int(circ_idx( i, len(imgArray[int(xCtrl[i])]) ))

        
        # srcDir length are arbitrary - read frames (% by srcDir length to roll) then inc corresponding index
        #srcImgArray.append(next(genObjx))
        srcImgArray.append(imgArray[xIdx][yIdx])
        
        #pdb.set_trace()

    return srcImgArray


def pulseScanRnd(dirList, numFrames, pulseLen):
    ''' Scans frames from a list of img directories, creates new renamed sequence
        pulse = log based array index ( np.logspace(...) )
        xLength - length of final sequence (seconds)
        framesPerSec - video frames per second
        framesPerBeat - video frames per beat (tempo sync)
        xCtrl - directory selector, quantized to # of src dir
        returns: imgArray - sequenced list of fullpath img names '''

    # check xCtrl is bounded by len(dirList)
    if (pulseLen > numFrames):
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
    
    #pdb.set_trace()

    srcImgArray = []
    for i in range(numFrames):
        if (i%pulseLen == 0):
            xCtrlPrev = xCtrl
            xCtrl=random.randint(0,len(dirList)-1)
            while xCtrl==xCtrlPrev:
                xCtrl=random.randint(0,len(dirList)-1)
            ss=random.randint(0,len(imgArray[xCtrl]))
            pulseIdx = 0
        yIdx = int(circ_idx( ss+pulse[pulseIdx], len(imgArray[xCtrl]) ))
        assert xCtrl < len(dirList), "xCtrl = "+str(xCtrl)
        assert yIdx < len(imgArray[xCtrl]), "yIdx = "+str(yIdx)
        #print("pulseScanRnd: xCtrl = "+str(xCtrl)+", yIdx = "+str(yIdx)+", ss = "+str(ss))
        srcImgArray.append(imgArray[xCtrl][yIdx])
        pulseIdx+=1
        imgIdx+=1;


    return srcImgArray


# // *********************************************************************** //    
# // *********************************************************************** //
# // *---::ODMK img Pre-processing func::---*
# // *********************************************************************** //
# // *********************************************************************** //

# def odmkEyePrint(self, img, title, idx):
    # imgWidth = img.shape[1]
    # imgHeight = img.shape[0]
    # figx = plt.figure(num=idx, facecolor='silver', edgecolor='k')
    # plt.imshow(img)
    # plt.xlabel('Src Width = '+str(imgWidth))
    # plt.ylabel('Src Height = '+str(imgHeight))
    # plt.title(title)


#def odmkEyeRescale(img, SzX, SzY):
#    # Rescale Image to SzW width and SzY height:
#    # *****misc.imresize returns img with [Y-dim, X-dim] format instead of X,Y*****    
#    if (len(img.shape) < 3):
#        imgRescale = misc.imresize(img, [SzY, SzX], interp='cubic')
#    else:
#        img_r = img[:, :, 0]
#        img_g = img[:, :, 1]
#        img_b = img[:, :, 2]
#        imgRescale_r = img_r.resize((SzY, SzX))
#        imgRescale_g = img_g.resize((SzY, SzX))
#        imgRescale_b = img_b.resize((SzY, SzX))
#        imgRescale = np.dstack((imgRescale_r, imgRescale_g, imgRescale_b))
#    return imgRescale

def odmkEyeRescale(img, SzX, SzY):
    # Rescale Image to SzW width and SzY height:
    # img = Image.fromarray(array) ??  
    img2 = Image.fromarray(img)
    imgRescale = img2.resize((SzX, SzY), resample=Image.BICUBIC)
    return imgRescale


def odmkEyeZoom(img, Z):
    # Zoom Image by factor Z:
    img_r = img[:, :, 0]
    img_g = img[:, :, 1]
    img_b = img[:, :, 2]
    imgZoom_r = ndimage.interpolation.zoom(img_r, Z)
    imgZoom_g = ndimage.interpolation.zoom(img_g, Z)
    imgZoom_b = ndimage.interpolation.zoom(img_b, Z)
    imgZoom = np.dstack((imgZoom_r, imgZoom_g, imgZoom_b))
    return imgZoom



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
    #zoomSzY = int(np.round(zoom_factor * SzYY))
    #zoomSzX = int(np.round(zoom_factor * SzXX))

    # for multichannel images we don't want to apply the zoom factor to the RGB
    # dimension, so instead we create a tuple of zoom factors, one per array
    # dimension, with 1's for any trailing dimensions after the width and height.
    # *** (xxx,) * n => (xxx, xxx, ... xxx) repeated n times
    # zoom_tuple = (zoom_factor,) * 2 + (1,) * (img.ndim - 2)
    zoom_tuple = [zoom_factor,] * 2 + [1,] * (img.ndim - 2)    # outputs [2, 2, 1]


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
    if (out.shape[0] != SzY or out.shape[1] != SzX):
        out = out[0:SzY, 0:SzX]

    #pdb.set_trace()


    # if zoom_factor == 1, just return the input array
    else:
        out = img
    return out



def odmkEyeCrop(img, SzX, SzY, high):
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


def odmkEyeDim(img, SzX, SzY, high):
    ''' Zoom and Crop image to match source dimensions '''

    imgWidth = img.shape[1]
    imgHeight = img.shape[0]

    #pdb.set_trace()

    if (imgWidth == SzX and imgHeight == SzY):
        # no processing
        imgScaled = img

    elif (imgWidth == SzX and imgHeight > SzY):
        # cropping only
        imgScaled = odmkEyeCrop(img, SzX, SzY, high)

    elif (imgWidth > SzX and imgHeight == SzY):
        # cropping only
        imgScaled = odmkEyeCrop(img, SzX, SzY, high)

    elif (imgWidth > SzX and imgHeight > SzY):
        # downscaling and cropping
        wRatio = SzX / imgWidth
        hRatio = SzY / imgHeight
        if wRatio >= hRatio:
            zoomFactor = wRatio
        else:
            zoomFactor = hRatio
        imgScaled = odmkEyeZoom(img, zoomFactor)
        imgScaled = odmkEyeCrop(imgScaled, SzX, SzY, high)

    elif (imgWidth < SzX and imgHeight == SzY):
        # upscaling and cropping
        wdiff = SzX - imgWidth
        zoomFactor = (imgWidth + wdiff) / imgWidth
        imgScaled = odmkEyeZoom(img, zoomFactor)
        imgScaled = odmkEyeCrop(imgScaled, SzX, SzY, high)

    elif (imgWidth == SzX and imgHeight < SzY):
        # upscaling and cropping
        hdiff = SzY - imgHeight
        zoomFactor = (imgHeight + hdiff) / imgHeight
        imgScaled = odmkEyeZoom(img, zoomFactor)
        imgScaled = odmkEyeCrop(imgScaled, SzX, SzY, high)

    elif (imgWidth < SzX and imgHeight < SzY):
        # upscaling and cropping (same aspect ratio -> upscaling only)
        wRatio = SzX / imgWidth
        hRatio = SzY / imgHeight
        if wRatio >= hRatio:
            zoomFactor = wRatio
        else:
            zoomFactor = hRatio
        imgScaled = odmkEyeZoom(img, zoomFactor)
        imgScaled = odmkEyeCrop(imgScaled, SzX, SzY, high)

    elif (imgWidth > SzX and imgHeight < SzY):
        # upscaling and cropping
        # wdiff = imgWidth - SzX
        hdiff = SzY - imgHeight
        zoomFactor = (imgHeight + hdiff) / imgHeight
        imgScaled = odmkEyeZoom(img, zoomFactor)
        imgScaled = odmkEyeCrop(imgScaled, SzX, SzY, high)

    elif (imgWidth < SzX and imgHeight > SzY):
        # upscaling and cropping
        wdiff = SzX - imgWidth
        # hdiff = imgHeight - SzY
        zoomFactor = (imgWidth + wdiff) / imgWidth
        imgScaled = odmkEyeZoom(img, zoomFactor)
        imgScaled = odmkEyeCrop(imgScaled, SzX, SzY, high)

    return imgScaled


def eyeRotate(img, ang, rotd=0):
    ''' example rotate image
        img: PIL image object
        ang = angle of rotation
        rotd: rotation direction - 0 = clock, 1 = anti-clock
        
        '''
    #eyeBox = img.getbbox()
    
    #pdb.set_trace()
    
    SzX = img.width
    SzY = img.height
    
    rotScale = 1.618
        
    if rotd == 1:
        ang = -ang
    imgRot = img.resize(( int(SzX*rotScale), int(SzY*rotScale) ))
    
    # new center pixel
    cenX = int(imgRot.width/2)
    cenY = int(imgRot.height/2)
    
    
    imgRot = imgRot.rotate(ang, resample=Image.BICUBIC)
    imgRot = imgRot.crop((int(cenX-SzX/2), int(cenY-SzY/2), 
                          int(cenX+SzX/2), int(cenY+SzY/2) ))
        
    return imgRot



# // *********************************************************************** //    
# // *********************************************************************** //
# // *---::ODMK img Pixel-Banging Basic Func::---*
# // *********************************************************************** //
# // *********************************************************************** //



def eyeSubInsert(imgBase1, imgBase2, imgSub1, imgSub2, SzX, SzY, nDimX, nDimY, alphaX):
    ''' inserts subframe images into base images & blends '''

    # region = (left, upper, right, lower)
    # subbox = (i + 1, i + 1, newDimX, newDimY)
    r = 0
    for j in range(SzY):
        s = 0
        for k in range(SzX):

           
            if ( (j >= ((SzY-1)-nDimY)/2) and (j < ((SzY-1) - ((SzY-1)-nDimY)/2)) and (k >= ((SzX-1)-nDimX)/2) and (k < ((SzX-1) - ((SzX-1)-nDimX)/2)) ):
                                                
                #if (j==1058 or r==1058):
                #    print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                #    pdb.set_trace()                                                                
                                                
                imgBase1[j, k, :] = imgSub1[r, s, :]
                imgBase2[j, k, :] = imgSub2[r, s, :]
                
            if (k >= (SzX-nDimX)/2) and (k < (SzX - (SzX-nDimX)/2)):
                s += 1
        if (j >= (SzY-nDimY)/2) and (j < (SzY - (SzY-nDimY)/2)):
            r += 1

    imgModOut = Image.blend(Image.fromarray(imgBase1), Image.fromarray(imgBase2), alphaX)
    #imgBpTscOut = self.eyePhiFrame1(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2))
    imgModOut = ImageOps.autocontrast(imgModOut, cutoff=0)
    
    return imgModOut


# *---FIXIT---*


#def odmkHelixPxl(vLength, theta):
#    helixPxlArray = []
#    # generate a vector of 'center pixels' moving around unit circle
#    # quantized cyclicZn coordinates!
#    # theta = angle of rotation per increment
#    return helixPxlArray
#
#
#def odmkFiboPxl(vLength, theta):
#    fiboPxlArray = []
#    # generate a vector of 'center pixels' tracing a fibonnaci spiral
#    # quantized fibonnaci coordinates!
#    # theta = angle of rotation per increment
#    return fiboPxlArray



def eyeBox1(img1, img2, boxSzX, boxSzY, pxlLoc, alpha):
    ''' alpha blends random box from img2 onto img1
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 '''


    if img1.size != img2.size:
        print('ERROR: img1, img2 must be same Dim')
        return        

   
    SzX = img1.size[0]
    SzY = img1.size[1]
    #imgDim = [SzX, SzY]

    
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

    #print('eyeSubCC X = '+str(eyeSubCC.shape[1])+', eyeSubCC Y = '+str(eyeSubCC.shape[0])+)
    #pdb.set_trace()

    # left frame
    img1.paste(eyeSubCC, boxCC)

    
    return img1



# // *********************************************************************** //
# // *---::ODMK horizontal trails::---*
# // *********************************************************************** //


def horizTrails(img, SzX, SzY, nTrail, ctrl):
    ''' reconstructs img with left & right trails
        img - a PIL image (Image.fromarray(eye2))
        nTrail controls number of trails
        ctrl controls x-axis coordinates '''
    
    if ctrl == 0:    # linear
        trails = np.linspace(0, SzX/2, nTrail+2)
        trails = trails[1:len(trails)-1]
    
    else:    # log spaced    
        trails = np.log(np.linspace(1,10,nTrail+2))
        sc = 1/max(trails)
        trails = trails[1:len(trails)-1]
        trails = trails*sc*int(SzX/2)
    
    alpha = np.linspace(0, 1, nTrail)
    
    # coordinates = (left, lower, right, upper)
    boxL = (0, 0, int(SzX / 2), SzY)
    eyeSubL = img.crop(boxL)
    
    boxR = (int(SzX / 2), 0, SzX, SzY)
    eyeSubR = img.crop(boxR)
    
    
    alphaCnt = 0
    for trail in trails:
    
        itrail = int(trail)
    
        boxL_itr1 = (itrail, 0, int(SzX / 2), SzY)
        eyeSubL_itr1 = img.crop(boxL_itr1)
        #print('\nboxL_itr1 = '+str(boxL_itr1))    
        
        boxR_itr1 = (int(SzX / 2), 0, SzX - itrail, SzY)
        eyeSubR_itr1 = img.crop(boxR_itr1)
        #print('\nboxR_itr1 = '+str(boxR_itr1))
        # if tcnt == 2:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        #pdb.set_trace()  
        
        boxL_base1 = (0, 0, int(SzX / 2) - itrail, SzY)
        eyeSubL_base1 = img.crop(boxL_base1)
        
        boxR_base1 = (int((SzX / 2) + itrail), 0, SzX, SzY)
        eyeSubR_base1 = img.crop(boxR_base1)
        
        eyeFadeL_itr1 = Image.blend(eyeSubL_itr1, eyeSubL_base1, alpha[alphaCnt])
        eyeFadeR_itr1 = Image.blend(eyeSubR_itr1, eyeSubR_base1, alpha[alphaCnt])
        
        #pdb.set_trace()
        
        boxL_sb1 = (0, 0, int(SzX / 2) - itrail, SzY)
        boxR_sb1 = (itrail, 0, int(SzX / 2), SzY)    
       
        
        #eye1subL.paste(eye1subL_itr1, boxL_sb1)
        #eye2subR.paste(eye2subR_itr1, boxR_sb1)
        eyeSubL.paste(eyeFadeL_itr1, boxL_sb1)
        eyeSubR.paste(eyeFadeR_itr1, boxR_sb1)    
        
        
        img.paste(eyeSubL, boxL)
        img.paste(eyeSubR, boxR)
    
        alphaCnt += 1    

    return img



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
    
    
def eyeMirrorTemporalHV4(img1, img2, img3, img4, SzX, SzY, ctrl='UL'):
    ''' generates composite 4 frame resized images
        Order = clockwise from ctrl setting
        SzX, SzY: output image dimentions
        img: PIL image object
        ctrl: { UL, UR, LL, LR} - selects base quadrant '''
    
    
    if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
        print('ERROR: ctrl must be {UL, UR, LL, LR} <string>')
        return
    
    imgSzX = img1.size[0]
    imgSzY = img1.size[1]

    imgDim = (SzX, SzY)


    mirrorTemporalImg = Image.new('RGB', imgDim)  # e.g. ('RGB', (640, 480))
    
    if (SzX == 2*imgSzX and SzY == 2*imgSzY):
        subDim = (imgSzX, imgSzY)
        imgX1 = img1
        imgX2 = img2
        imgX3 = img3
        imgX4 = img4
    else:
        subDim = (int(SzX/2), int(SzY/2))
        imgX1 = img1.resize(subDim)
        imgX2 = img2.resize(subDim)
        imgX3 = img3.resize(subDim)
        imgX4 = img4.resize(subDim)


    #boxUL = (0, SzY, SzX-1, 2*SzY-1)
    boxUL = (0, subDim[1], subDim[0], imgDim[1])
    boxUR = (subDim[0], subDim[1], imgDim[0], imgDim[1]) 
    boxLL = (0, 0, subDim[0], subDim[1])
    boxLR = (subDim[0], 0, imgDim[0], subDim[1])
    

    if ctrl == 'LL':
        eyeSubUL = imgX1
        eyeSubUR = ImageOps.mirror(imgX2)
        eyeSubLL = ImageOps.flip(imgX3)
        eyeSubLR = ImageOps.flip(imgX4)
        eyeSubLR = ImageOps.mirror(eyeSubLR)        
        
        
    if ctrl == 'LR':
        eyeSubUL = ImageOps.mirror(imgX4)
        eyeSubUR = imgX1
        eyeSubLL = ImageOps.flip(imgX2)
        eyeSubLL = ImageOps.mirror(eyeSubLL)
        eyeSubLR = ImageOps.flip(imgX3)
        
        
    if ctrl == 'UL':
        eyeSubUL = ImageOps.flip(imgX3)
        eyeSubUR = ImageOps.flip(imgX4)
        eyeSubUR = ImageOps.mirror(eyeSubUR)
        eyeSubLL = imgX1
        eyeSubLR = ImageOps.mirror(imgX2)


    if ctrl == 'UR':
        eyeSubUL = ImageOps.flip(imgX2)
        eyeSubUL = ImageOps.mirror(eyeSubUL)
        eyeSubUR = ImageOps.flip(imgX3)
        eyeSubLL = ImageOps.mirror(imgX4)
        eyeSubLR = imgX1


    #pdb.set_trace()

    mirrorTemporalImg.paste(eyeSubUL, boxUL)
    mirrorTemporalImg.paste(eyeSubUR, boxUR)
    mirrorTemporalImg.paste(eyeSubLL, boxLL)
    mirrorTemporalImg.paste(eyeSubLR, boxLR)

    
    #eyeOutFileName = 'eyeMirrorHV4'
    #eyeMirrorHV4Full = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeMirrorHV4Full, mirrorImg)
    
    return mirrorTemporalImg



def eyePhiHorizFrame1(img1, img2, img3, ctrl=1):
    ''' generates composite 4 frame resized images
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 '''


    if (img1.size != img2.size != img3.size):
        print('ERROR: img1, img2 must be same Dim')
        return        

    #phi = 1.6180339887
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
    
    #eyeSubTC = img2.resize(subDim)
    #eyeSubBC = img2.copy().crop(boxC_B)

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
    #phiFrameImg.paste(eyeSubTC, boxC_T)
    #phiFrameImg.paste(eyeSubBC, boxC_B)
    
    # center center
    phiFrameImg.paste(eyeSubCC, boxCC)

    
    #eyeOutFileName = 'eyeMirrorHV4'
    #eyeMirrorHV4Full = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeMirrorHV4Full, mirrorImg)
    
    return phiFrameImg


def eyePhiFrame1(img1, img2, ctrl=1):
    ''' generates composite 4 frame resized images
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 '''


    if img1.size != img2.size:
        print('ERROR: img1, img2 must be same Dim')
        return        

    #phi = 1.6180339887
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
    
    #eyeSubTC = img2.resize(subDim)
    #eyeSubBC = img2.copy().crop(boxC_B)

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
    #phiFrameImg.paste(eyeSubTC, boxC_T)
    #phiFrameImg.paste(eyeSubBC, boxC_B)
    
    # center center
    phiFrameImg.paste(eyeSubCC, boxCC)

    
    #eyeOutFileName = 'eyeMirrorHV4'
    #eyeMirrorHV4Full = imgOutDir+eyeOutFileName+'.jpg'
    #misc.imsave(eyeMirrorHV4Full, mirrorImg)
    
    return phiFrameImg


def eyePhiFrame2(img1, img2, ctrl='UL'):
    ''' generates subframes increasing by fibonacci sequence
        sub dimensions defined by pxlLoc [x, y]
        img1: img4 PIL images
        ctrl: toggle background - 0 = no background img (black), 1 = use img1 '''


    if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
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
        
        if bb%2==1:
            boxBB = (0, 0, dimXarray[len(dimXarray) - bb - 1], dimYarray[len(dimYarray) - bb - 1])
            eyeSub = phiSubImg1.copy().crop(boxBB)
            phiFrameImg.paste(eyeSub, boxBB)
        else:
            boxBB = (0, 0, dimXarray[len(dimXarray) - bb - 1], dimYarray[len(dimYarray) - bb - 1])
            eyeSub = phiSubImg2.copy().crop(boxBB)
            phiFrameImg.paste(eyeSub, boxBB)
           
    
    return phiFrameImg


def eyeSobelXY(img):
    ''' 2D Convolution Sobel filter (edge detect) '''

    sobel_x = np.c_[
        [-1,0,1],
        [-2,0,2],
        [-1,0,1]
    ]
    
    sobel_y = np.c_[
        [1,2,1],
        [0,0,0],
        [-1,-2,-1]
    ]
    
    ims = []
    for d in range(3):
        sx = convolve2d(img[:,:,d], sobel_x, mode="same", boundary="symm")
        sy = convolve2d(img[:,:,d], sobel_y, mode="same", boundary="symm")
        ims.append(np.sqrt(sx*sx + sy*sy))
    
    im_conv = np.stack(ims, axis=2).astype("uint8")
    
    return im_conv


def median_filter_rgb(im_small, window_size):
    """
    Applies a median filer to all colour channels
    """
    ims = []
    for d in range(3):
        im_conv_d = ndimage.median_filter(im_small[:,:,d], size=(window_size,window_size))
        ims.append(im_conv_d)

    im_conv = np.stack(ims, axis=2).astype("uint8")
    
    return im_conv




# // *********************************************************************** //
# // *---:: ODMK Masking Functions ::---*
# // *********************************************************************** //


def eyeMask2Ch(mask, img1, img2):
    ''' mask multiplexor: pos/neg mask region mux 
        inputs are numpy 2D array RGB stackd
        works clean with black/white mask, 
        also produces funk results with random color image for mask '''

        
    if not( img1.shape[0]==img2.shape[0] and img1.shape[1]==img2.shape[1] and 
            img1.shape[0]==mask.shape[0] and img1.shape[1]==mask.shape[1] ):
        print('ERROR: image & mask sizes must be equl')
        return
    
    mask = mask / 255
    dstPos = img1 * mask
    dstNeg = img2 * (1-mask)
    dst = np.sqrt((dstPos**2) + (dstNeg**2))
    eyeOut = dst.astype(np.uint8)
    
    return eyeOut