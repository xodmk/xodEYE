# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEYEu.py))::__
#
# Python ODMK img processing research
# ODMK image processing algorithms
#
# The original image funk mutilator
# 
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os
import sys
import numpy as np
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


import glob, shutil
from math import atan2, floor, ceil
import random
#import scipy as sp
#from scipy.signal import convolve2d
import imageio as imio
from scipy import ndimage
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance


currentDir = os.getcwd()
rootDir = os.path.dirname(currentDir)

eyeDir = currentDir + "/eye/"
eyeSrcDir = currentDir + "/eye/src/"

audioSrcDir = rootDir + "/audio/wavsrc/"
audioOutDir = rootDir + "/audio/wavout/"

print("currentDir: " + currentDir)
print("rootDir: " + rootDir)

sys.path.insert(0, rootDir+'xodEYE/')
import xodEYEutil as eyeutil

sys.path.insert(2, rootDir+'git/xodDSP')
# import xodClocks as clks

# temp python debugger - use >>>pdb.set_trace() to set break
import pdb


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 

class xodEYEu:
    ''' # Python ODMK img processing research
        # ffmpeg experimental
        --xLength: length of output video/audio file
        --bpm: tempo of video/audio
        --timeSig: 4/4 or 3/4
        --imgFormat: img format
        --SzX, SzY: video dimensions
        --framesPerSec: video frames per second
        --fs: audio sample rate
        >>tbEYEu = eyeInst.odmkEYEu(eyeLength, 93, 30.0, 48000)
    '''

    def __init__(self, xLength, bpm, timeSig, SzX, SzY, imgFormat, framesPerSec=30.0, fs=48000):

        # *---set primary parameters from inputs---*

        self.xLength = xLength
        self.fs = fs
        self.bWidth = 24         # audio sample bit width
        # ub313 bpm = 178 , 267
        self.bpm = bpm    #glamourGoat14 = 93        
        self.timeSig = timeSig         # time signature: 4 = 4/4; 3 = 3/4
        
        self.imgFormat = imgFormat    # imgFormat => { fbmp, fjpg }

        self.framesPerSec = framesPerSec

        # // *-------------------------------------------------------------* //
        # // *---::Set Default Directories::---* //
        
        # self.eyeDir = eyeDir
        # self.maskDir = eyeDir+'/eye/src/8018x/mask8018x/'

        self.goldratio = 1.6180339887
        self.goldratioinv = 0.618033988768953

        # // *-------------------------------------------------------------* //
        # // *---::Set Master Dimensions::---* //
        self.mstrSzX = SzX
        self.mstrSzY = SzY        

        # // *-------------------------------------------------------------* //
        # // Instantiate clocking/sequencing object::-*')
        
        # self.eyeClks = clks.xodClocks(self.xLength, self.fs, self.bpm, self.framesPerSec)
        
        #print('\n*****odmkEYEuObj: An odmkEYEu object has been instanced with:')
        #print('xLength = '+str(self.xLength)+', bpm = '+str(self.bpm)+
        #      ', timeSig = '+str(self.timeSig)+', framesPerSec = '+str(self.framesPerSec)+
        #      ', fs = '+str(self.fs))



    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img Pre-processing func::---*
    # // *********************************************************************** //
    # // *********************************************************************** //




    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - phiFrame2 img files in two directoroies::---*
    # // *--------------------------------------------------------------* //

    def imgPhiFrame2Array(self, imgList1, imgList2, numFrames, xCtrl='UL'):
        ''' ? '''

        if not(xCtrl=='UL' or xCtrl=='UR' or xCtrl=='LL' or xCtrl=='LR'):
            print('ERROR: xCtrl must be {UL, UR, LL, LR} <string>')
            return


        srcImgArray = []

        nextInc = 0
        for i in range(numFrames):
            nextInc += 1         
            
            eye1img = imio.imread(imgList1[i])
            eye2img = imio.imread(imgList2[i]) 
            
            phiFrame2 = self.eyePhiFrame2(eye1img, eye2img, xCtrl)

            srcImgArray.append(phiFrame2)            
            
            #pdb.set_trace()
    
        return srcImgArray


   
    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img Post-processing func::---*
    # // *********************************************************************** //
    # // *********************************************************************** //


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
            
        pdb.set_trace()

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


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - interlace img files in two directoroies::---*
    # // *--------------------------------------------------------------* //

    def imgXfadeDir(self, dir1, dir2, xCtrl, interlaceDir, reName):
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
        dirIdx1 = 0
        dirIdx2 = 0
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
            if xCtrl[i] == 1: 
                currentNm = os.path.split(imgFileList1[dirIdx1])[1]
                shutil.copy(imgFileList1[dirIdx1], interlaceDir)
                currentFile = os.path.join(interlaceDir+currentNm)
                dirIdx1 += 1
            else:
                currentNm = os.path.split(imgFileList2[dirIdx2])[1]                
                shutil.copy(imgFileList2[dirIdx2], interlaceDir)
                currentFile = os.path.join(interlaceDir+currentNm)
                dirIdx2 += 1
            
            imgInterlaceDirNmFull = os.path.join(interlaceDir+imgNormalizeNm)
            os.rename(currentFile, imgInterlaceDirNmFull)
            #pdb.set_trace()
    
        return





    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - mirrorHV4 list of files in directory::---*
    # // *--------------------------------------------------------------* //
    
    def mirrorHV4AllImg(self, srcDir, SzX, SzY, mirrorHV4Dir, mirrorHV4Nm, ctrl='LR'):
        ''' mirrors image horizontally & vertically - outputs 4 mirrored subframes
            srcDir: input image directory
            SzX, SzY: output image frame size (input img pre-scaled if required)
            mirrorHV4Dir: processed img output directory
            mirrorHV4Nm: processed img root name
            ctrl: quadrant location of initial subframe {UL, UR, LL, LR}'''
    
        # check write condition, if w=0 ignore outDir
        if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
            print('ERROR: ctrl must be {UL, UR, LL, LR}')
            return
            
        # If Dir does not exist, makedir:
        os.makedirs(mirrorHV4Dir, exist_ok=True)
            
        [imgObjList, imgSrcList] = self.importAllJpg(srcDir)


        imgCount = len(imgObjList)
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(imgCount):
            
            pilImg = Image.fromarray(imgObjList[i])
            imgMirrorHV4 = self.eyeMirrorHV4(pilImg, SzX, SzY, ctrl)           
            
            nextInc += 1
            zr = ''
            for h in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgMirrorHV4Nm = mirrorHV4Nm+strInc+'.jpg'

            imgMirrorHV4NmFull = mirrorHV4Dir+imgMirrorHV4Nm
            imio.imwrite(imgMirrorHV4NmFull, imgMirrorHV4)
    
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - mirrorHV4 list of files in directory::---*
    # // *--------------------------------------------------------------* //
    
    def mirrorTemporalHV4AllImg(self, srcDir, SzX, SzY, mirrorTemporalHV4Dir, mirrorTemporalHV4Nm, frameDly, ctrl='LR'):
        ''' mirrors image horizontally & vertically - outputs 4 mirrored subframes
            srcDir: input image directory
            SzX, SzY: output image frame size (input img pre-scaled if required)
            mirrorHV4Dir: processed img output directory
            mirrorHV4Nm: processed img root name
            ctrl: quadrant location of initial subframe {UL, UR, LL, LR}'''
    
        # check write condition, if w=0 ignore outDir
        if not(ctrl=='UL' or ctrl=='UR' or ctrl=='LL' or ctrl=='LR'):
            print('ERROR: ctrl must be {UL, UR, LL, LR}')
            return
            
        # If Dir does not exist, makedir:
        os.makedirs(mirrorTemporalHV4Dir, exist_ok=True)
            
        [imgObjList, imgSrcList] = self.importAllJpg(srcDir)


        imgCount = len(imgObjList)
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(imgCount):
            
            pilImg1 = Image.fromarray(imgObjList[i])
            pilImg2 = Image.fromarray(imgObjList[(i + frameDly) % imgCount])
            pilImg3 = Image.fromarray(imgObjList[(i + 2*frameDly) % imgCount])
            pilImg4 = Image.fromarray(imgObjList[(i + 3*frameDly) % imgCount])            
            #imgMirrorHV4 = self.eyeMirrorHV4(pilImg, SzX, SzY, ctrl)
            
            imgMirrorTemporalHV4 = self.eyeMirrorTemporalHV4(pilImg1, pilImg2, pilImg3, pilImg4, SzX, SzY, ctrl)
            
            nextInc += 1
            zr = ''
            for h in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgMirrorTemporalHV4Nm = mirrorTemporalHV4Nm+strInc+'.jpg'

            imgMirrorTemporalHV4NmFull = mirrorTemporalHV4Dir+imgMirrorTemporalHV4Nm
            imio.imwrite(imgMirrorTemporalHV4NmFull, imgMirrorTemporalHV4)
    
        return

    
    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img Pixel-Banging Algorithms::---*
    # // *********************************************************************** //
    # // *********************************************************************** //
    
    
    # <<<selects pixel banging algorithm>>>
    # *---------------------------------------------------------------------------*
    # 0  => Bypass
    
    
    
    # 1  => EYE Random Select Algorithm              ::odmkImgRndSel::
    # 2  => EYE Random BPM Algorithm                 ::odmkImgRndSel::
    # 3  => EYE Random Select Telescope Algorithm    ::**nofunc**::
    # 4  => EYE BPM rotating Sequence Algorithm      ::odmkImgRotateSeq::
    # 5  => EYE Rotate & alternate sequence          ::**nofunc**::
    # 6  => EYE CrossFade Sequencer (alpha-blend)    ::odmkImgXfade::
    # 67 => EYE CrossFade Sequencer (solarize)       ::odmkImgSolXfade::
    # 7  => EYE Divide CrossFade Sequencer           ::odmkImgDivXfade::
    # 8  => EYE CrossFade Rotate sequence            ::odmkImgXfadeRot::
    # 9  => EYE telescope sequence                   ::odmkImgTelescope::
    # 10 => EYE CrossFade telescope Sequence         ::odmkImgXfadeTelescope::
    # 11 => EYE Div Xfade telescope Sequence         ::odmkImgDivXfadeTelescope::
    # 12 => Eye Echo BPM Sequencer                   ::odmkEyeEchoBpm::
    # 20 => EYE Color Enhance BPM Algorithm          ::odmkImgColorEnhance::
    # 22 => EYE Pixel Random Replace Algorithm       ::odmkPxlRndReplace::
    # 23 => EYE Dual Bipolar Telescope Algorithm     ::odmkDualBipolarTelesc::
    # 24 => EYE Bananasloth Recursive Algorithm      ::odmkBSlothRecurs::
    # 26 => EYE Bananasloth Glitch 1                 ::odmkBSlothGlitch1::
    # 28 => EYE lfo horizontal trails                ::odmkLfoHtrails::



    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img Basic func::---*
    # // *********************************************************************** //
    # // *********************************************************************** //
    

    # // *--------------------------------------------------------------* //
    # // *---::XODMKEYE - Image Random Select Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def xodImgRndSel(self, imgFileList, numFrames, n_digits, imgOutDir, imgOutNm):

        imgCount = numFrames
        nextInc = 0
        for i in range(numFrames):
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgOutNm + strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            imio.imwrite(imgRndSelFull, imio.imread(imgFileList[eyeutil.randomIdx(len(imgFileList))]))

        return


    # // *--------------------------------------------------------------* //
    # // *---::XODMKEYE - Image Rotate Sequence Algorithm::---*')
    # // *--------------------------------------------------------------* //
    
    def xodImgRotateSeq(self, imgFileList, numFrames, imgOutDir, imgOutNm='None', rotDirection=0):
        ''' outputs a sequence of rotated images (static img input)
            360 deg - period = numFrames
            (ndimage.rotate: ex, rotate image by 45 deg:
             rotate_gz1 = ndimage.rotate(gz1, 45, reshape=False)) '''
    
        if imgOutNm != 'None':
            imgRotateSeqNm = imgOutNm
        else:
            imgRotateSeqNm = 'imgRotateSeqOut'
    
        zn = eyeutil.cyclicZn(numFrames-1)    # less one, then repeat zn[0] for full 360
    
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(numFrames):
            ang = (atan2(zn[i % (numFrames-1)].imag, zn[i % (numFrames-1)].real))*180/np.pi
            if rotDirection == 1:
                ang = -ang            
            raw_gz1 = imio.imread(imgFileList[eyeutil.circ_idx(i, len(imgFileList))])
            imgPIL1 = Image.fromarray(raw_gz1)
            rotate_gz1 = ndimage.rotate(imgPIL1, ang, reshape=False)            
            rotate_gz1 = self.cropZoom(rotate_gz1, 2)
            
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgRotateSeqFull = imgOutDir+imgRotateSeqNm+strInc+'.jpg'
            imio.imwrite(imgRotateSeqFull, rotate_gz1)
    
        return



    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img Batch Manipulation function::---*
    # // *********************************************************************** //
    # // *********************************************************************** //

    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE image array processing prototype::---*
    # // *--------------------------------------------------------------* //
    
    def odmkEYEprototype(self, imgFileList, xLength, framesPerSec, FrameCtrl, imgOutDir, imgOutNm='None', usrCtrl=0):
        ''' basic prototype function '''
    
        if imgOutNm != 'None':
            imgPrototypeNm = imgOutNm
        else:
            imgPrototypeNm = 'imgXfadeRot'
    
        SzX = imgFileList[0].shape[1]
        SzY = imgFileList[0].shape[0]
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / FrameCtrl))
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---FrameCtrl = '+str(FrameCtrl)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgFileList)
        numxfadeImg = numImg * FrameCtrl
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        # example internal control signal 
        alphaX = np.linspace(0.0, 1.0, FrameCtrl)
        
        
        hop_sz = 56
    
    
        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades - 1):
            if frameCnt <= numFrames:    # process until end of total length
            
                newDimX = SzX
                newDimY = SzY
                
                # example cloned img
                imgClone1 = imgFileList[j]
    
                img = Image.new( 'RGB', (255,255), "black") # create a new black image
                imgPxl = img.load() # create the pixel map
    
                # scroll forward -> backward -> forward... through img array
                if (frameCnt % numxfadeImg) == 0:
                    xfdirection = -xfdirection
                if xfdirection == 1:
                    imgPIL1 = Image.fromarray( imio.imread(imgFileList[j % (numImg-1)]) )
                    imgPIL2 = Image.fromarray( imio.imread(imgFileList[(j % (numImg-1)) + 1]) )
                else:
                    imgPIL1 = Image.fromarray( imio.imread(imgFileList[(numImg-2) - (j % numImg) + 1]) )
                    imgPIL2 = Image.fromarray( imio.imread(imgFileList[(numImg-2) - (j % numImg)]) )
    
                # process frameCtrl timed sub-routine:
                for i in range(FrameCtrl):
    
                    # example usrCtrl update                
                    if newDimX > 2:
                        newDimX -= 2*hop_sz
                    if newDimY > 2:
                        newDimY -= 2*hop_sz
                    
                    # example algorithmic process
                    alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
    
                    # process sub-frame
                    for j in range(SzY):
                        for k in range(SzX):
                            #if ((j >= (t+1)*hop_sz) and (j < (newDimY+(SzY-newDimY)/2)) and (k >= (t+1)*hop_sz) and (k < (newDimX+(SzX-newDimX)/2))):
                            if ((j >= hop_sz) and (j < newDimY+hop_sz/2) and (k >= hop_sz) and (k < newDimX+hop_sz/2)):
                                #imgClone[j+(SzY-newDimY)/2, k+(SzX-newDimX)/2, :] = imgItr[j - t, k - t, :]
                                imgClone1[j, k, :] = alphaB[j - (SzY-newDimY)/2, k - (SzX-newDimX)/2, :]
    
                    # ***sort out img.size vs. imgList[0].shape[1]
                    # bit-banging
                    for i in range(img.size[0]):    # for every pixel:
                        for j in range(img.size[1]):
                            imgPxl[i,j] = (i, j, 1) # set the colour accordingly
    
    
                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    imgPrototypeFull = imgOutDir+imgPrototypeNm+strInc+'.jpg'
                    
                    # write img to disk
                    imio.imwrite(imgPrototypeFull, alphaB)

                    frameCnt += 1

        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Linear F<->B Select Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgRotLinSel(self, imgFileList, numFrames, xFrames, imgOutDir, imgOutNm='None'):
    
        if imgOutNm != 'None':
            imgRndSelNm = imgOutNm
        else:
            imgRndSelNm = 'imgRndSelOut'
    
    
        zn = eyeutil.cyclicZn(xFrames-1)    # less one, then repeat zn[0] for full 360
        
        idx = 0
        
        numImg = len(imgFileList)
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 1
        xfdirection = 1
        for i in range(numFrames):
            
            raw_gz1 = imio.imread(imgFileList[i % numImg])
            imgPIL1 = Image.fromarray(raw_gz1)
            ang = (atan2(zn[i % (xFrames-1)].imag, zn[i % (xFrames-1)].real))*180/np.pi
            rotate_gz1 = ndimage.rotate(imgPIL1, ang, reshape=False)            
            rotate_gz1 = self.cropZoom(rotate_gz1, 2)

            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgRndSelNm+strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            imio.imwrite(imgRndSelFull, rotate_gz1)

            if (nextInc % numImg-1) == 0:
                xfdirection = -xfdirection
            if xfdirection == 1:
                idx += 1                
            else:
                idx -= 1
           
            nextInc += 1
            
        #return [imgRndSelArray, imgRndSelNmArray]
        return    

    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image BPM Random Select Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgRndBpm(self, imgList, numFrames, frameHold, imgOutDir, imgOutNm='None'):
    
        if imgOutNm != 'None':
            imgRndSelNm = imgOutNm
        else:
            imgRndSelNm = 'imgRndSelOut'
    
        #imgRndSelNmArray = []
        #imgRndSelArray = []
        
        rIdxArray = eyeutil.randomIdxArray(numFrames, len(imgList))
        
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        k = 0
        for i in range(numFrames):
            if frameHold[i] == 1:
                k += 1
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgRndSelNm+strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            imio.imwrite(imgRndSelFull, imgList[rIdxArray[k]])
            
        #return [imgRndSelArray, imgRndSelNmArray]
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Rotate Sequence Algorithm::---*')
    # // *--------------------------------------------------------------* //
    
    def odmkImgRotateAlt(self, imgFileList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of rotated images (static img input)
            360 deg - period = numFrames
            (ndimage.rotate: ex, rotate image by 45 deg:
             rotate_gz1 = ndimage.rotate(gz1, 45, reshape=False)) '''
    
        if imgOutNm != 'None':
            imgRotateSeqNm = imgOutNm
        else:
            imgRotateSeqNm = 'imgRotateSeqOut'
            
        imgObjTemp1 = imio.imread(imgFileList[0])  
        

        SzX = imgObjTemp1.shape[1]
        SzY = imgObjTemp1.shape[0]
        
        numImg = len(imgFileList)

        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        # finalXfade = int(floor(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---Total number of frames = '+str(numFrames)+'---*')
        print('// *---number of img per xfade = '+str(xfadeFrames)+'---*')
        print('// *---number of xfades = '+str(numXfades)+'---*')
        print('// *---number of img for Final xfade = '+str(numFinalXfade)+'---*')
        print('\nProcessing ... ... ...\n\n')

    
        zn = eyeutil.cyclicZn((xfadeFrames*4)-1)    # less one, then repeat zn[0] for full 360
    
    
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(numFrames):
            
            if i%(xfadeFrames*4)==0:
                gz1 = imio.imread(imgFileList[(2*i+90) % numImg])
                gz2 = imio.imread(imgFileList[(2*i+1+90) % numImg])
            #gz2 = imio.imread(imgFileList[(2*i+1) % numImg])
            
            ang = (atan2(zn[i % ((xfadeFrames*4)-1)].imag, zn[i % ((xfadeFrames*4)-1)].real))*180/np.pi
            #if ((i % 2) == 0):
            if ((i % 4) == 1 or (i % 4) == 2):
                rotate_gz = ndimage.rotate(gz1, ang, reshape=False)
                #zoom_gz1 = self.cropZoom(rotate_gz1, 2)
            else:
                rotate_gz = ndimage.rotate(gz2, -ang, reshape=False)
                #zoom_gz1 = self.cropZoom(rotate_gz1, 2)
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgRotateSeqFull = imgOutDir+imgRotateSeqNm+strInc+'.jpg'
            imio.imwrite(imgRotateSeqFull, rotate_gz)
    
        return    
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image CrossFade Sequence Algorithm::---*')
    # // *--------------------------------------------------------------* //
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image CrossFade Sequence Algorithm::---*')
    # // *--------------------------------------------------------------* // 
    

        
    def xodImgXfade(self, imgFileList, xLength, framesPerSec, xfadeFrames,
                    n_digits, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of images fading from img1 -> img2 for xLength seconds
            Linearly alpha-blends images using PIL Image.blend
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgXfadeNm = imgOutNm
        else:
            imgXfadeNm = 'ImgXfade'
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numImg = len(imgFileList)
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xfadeFrames = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    

        alphaX = np.linspace(0.0, 1.0, xfadeFrames)
        alphaCosX = (-np.cos(np.pi * alphaX) + 1) / 2

    
        frameCnt = 0
        for j in range(numXfades):
            
            
                imgPIL1 = Image.open(imgFileList[j % numImg])
                imgPIL2 = Image.open(imgFileList[(j + 1) % numImg])

                
                for i in range(xfadeFrames):
                    if frameCnt <= numFrames:
                        alphaB = Image.blend(imgPIL1, imgPIL2, alphaCosX[i])
                        zr = ''
                        for j in range(n_digits - len(str(frameCnt))):
                            zr += '0'
                        strInc = zr+str(frameCnt)
                        imgXfadeFull = imgOutDir+imgXfadeNm+strInc+'.jpg'
                        imio.imwrite(imgXfadeFull, alphaB)
                        frameCnt += 1    
    
        return

    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image solarize CrossFade Sequence::---*')
    # // *--------------------------------------------------------------* //    
        
    def odmkImgSolXfade(self, imgList, sLength, framesPerSec, xFrames, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of images fading from img1 -> img2
            Linearly alpha-blends images using PIL Image.blend
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgXfadeNm = imgOutNm
        else:
            imgXfadeNm = 'imgSolXfadeOut'
    
        numFrames = int(ceil(sLength * framesPerSec))
        numXfades = int(ceil(numFrames / xFrames))
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xFrames = '+str(xFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgList)

        n_digits = int(ceil(np.log10(numFrames))) + 2
        solarX = np.linspace(5.0, 255.0, xFrames)

        frameCnt = 0
        indexCnt = 0
        xfdirection = -1
        for j in range(numXfades - 1):
            if frameCnt <= numFrames:
                if (j % int(numImg/3)) == 0:
                    xfdirection = -xfdirection
                if xfdirection == 1:
                    indexCnt += 1
                    imgPIL1 = Image.fromarray(imgList[3*indexCnt])
                else:
                    indexCnt -= 1
                    imgPIL1 = Image.fromarray(imgList[3*indexCnt])
                #pdb.set_trace()
                # imgPIL2 = Image.fromarray(imgList[j + 1])
                for i in range(xFrames):
                    #solarB = ImageOps.solarize(imgPIL1, solarX[xFrames-i-1])
                    solarB = ImageOps.solarize(imgPIL1, solarX[i])
                    solarB = ImageOps.autocontrast(solarB, cutoff=0)
                    #solarB = ImageOps.autocontrast(solarB, cutoff=0)
                    zr = ''
                    for k in range(n_digits - len(str(frameCnt))):
                        zr += '0'
                    strInc = zr+str(frameCnt)
                    imgXfadeFull = imgOutDir+imgXfadeNm+strInc+'.jpg'
                    imio.imwrite(imgXfadeFull, solarB)
                    frameCnt += 1
    
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Division CrossFade Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgDivXfade(self, imgList, numFrames, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of images fading from img1 -> img2
            Experimental Division Blending images using numpy
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgDivXfadeNm = imgOutNm
        else:
            imgDivXfadeNm = 'imgDivXfade'
    
        numImg = len(imgList)
        imgCount = numFrames * (numImg - 1)
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        alphaX = np.linspace(0.0001, 1.0, numFrames)

    
        for j in range(numImg - 1):
            imgPIL1 = imgList[j]
            imgPIL2 = imgList[j + 1]
            for i in range(numFrames):
                # image division blend algorithm..
                c = imgPIL1/((imgPIL2.astype('float')+1)/(256*alphaX[i]))
                # saturating function - if c[m,n] > 255, set to 255:
                imgDIVB = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
                nextInc += 1
                zr = ''
                for j in range(n_digits - len(str(nextInc))):
                    zr += '0'
                strInc = zr+str(nextInc)
                imgDivXfadeFull = imgOutDir+imgDivXfadeNm+strInc+'.jpg'
                imio.imwrite(imgDivXfadeFull, imgDIVB)
    
        return

    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Telescope Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def xodImgTelescope(self, imgList, xLength, framesPerSec, framesPerBeat, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' outputs a sequence of telescoping images (zoom in or zoom out)
            The period of telescoping sequence synched to framesPerBeat
            assumes images in imgList are normalized (scaled/cropped) numpy arrays '''
    
    
        if imgOutNm != 'None':
            imgTelescNm = imgOutNm
        else:
            imgTelescNm = 'imgTelescope'
    
        # find number of source images in src dir
        numSrcImg = len(imgList)
        # initialize SzX, SzY to dimensions of src img
        SzX = imgList[0].shape[1]
        SzY = imgList[0].shape[0]
    
        numFrames = int(ceil(xLength * framesPerSec))
        numBeats = int(ceil(numFrames / framesPerBeat))         
    
        hop_sz = 4*ceil(np.log(SzX/framesPerBeat))  # number of pixels to scale img each iteration
    
        #imgTelescopeNmArray = []
        #imgTelescopeArray = []
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        for i in range(numBeats):
            newDimX = SzX
            newDimY = SzY
            imgClone = imgList[i%numSrcImg]    # mod to rotate through src img
            for t in range(framesPerBeat):
                if newDimX > 2:
                    #newDimX -= 2*hop_sz
                    newDimX -= hop_sz
                if newDimY > 2:
                    #newDimY -= 2*hop_sz
                    newDimY -= hop_sz
                # scale image to new dimensions
                imgItr = self.odmkEyeRescale(imgClone, newDimX, newDimY)
                # region = (left, upper, right, lower)
                # subbox = (i + 1, i + 1, newDimX, newDimY)
                for j in range(SzY):
                    for k in range(SzX):
                        #if ((j >= (t+1)*hop_sz) and (j < (newDimY+(SzY-newDimY)/2)) and (k >= (t+1)*hop_sz) and (k < (newDimX+(SzX-newDimX)/2))):
                        if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
                            #imgClone[j+(SzY-newDimY)/2, k+(SzX-newDimX)/2, :] = imgItr[j - t, k - t, :]
                            imgClone[j, k, :] = imgItr[j - (SzY-newDimY)/2, k - (SzX-newDimX)/2, :]
                nextInc += 1
                if nextInc < numFrames:
                    zr = ''
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            zr += '0'
                        strInc = zr+str(numFrames - (nextInc))
                    imgTelescFull = imgOutDir+imgTelescNm+strInc+'.jpg'
                    imio.imwrite(imgTelescFull, imgClone)
                else:
                    break
                
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Img Xfade Telescope Sequence Algorithm I::---*
    # // *--------------------------------------------------------------* //fc
    
    def xodXfadeTelescopeI(self, imgFileList, xLength, framesPerSec, xfadeFrames,
                           inOut, rndFocal, n_digits, imgOutDir, imgOutNm='None'):
        
        ''' outputs a sequence of telescoping images (zoom in or zoom out)
            The period of telescoping sequence synched to framesPerBeat
            Telescoping xfades from one source image to another
            
            inOut = 0       # telescope direction: 0 = out, 1 = in
            rndFocal = 0    # random focal point: 0 = center, 1 = random pixel loc
        '''

    
        if imgOutNm != 'None':
            imgXfTelescNm = imgOutNm
        else:
            imgXfTelescNm = 'imgTelescope'
    
        numImg = len(imgFileList)
        
        
        imgFirst = Image.open(imgFileList[0])      

        SzX = imgFirst.width
        SzY = imgFirst.height        
        
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---Total number of frames = '+str(numFrames)+'---*')
        print('// *---number of img per xfade = '+str(xfadeFrames)+'---*')
        print('// *---number of xfades = '+str(numXfades)+'---*')
        print('// *---number of img for Final xfade = '+str(numFinalXfade)+'---*')
        print('\nProcessing ... ... ...\n\n')
        
        
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)            
    
        hop_sz = ceil(SzX/xfadeFrames)  # number of pixels to scale img each iteration
    
        nextInc = 0
        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
            imgClone2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgXfTsc1 = imgClone1
            imgXfTsc2 = imgClone2
            imgXfTscOut = imgClone1

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY

            center = np.zeros(2)
            center[0] = int(SzX/2)
            center[1] = int(SzY/2)

            focal = np.zeros(2)
            if rndFocal == 1:
                focal = eyeutil.randomPxlLoc(int(SzX), int(SzY))
            else:
                #centered focal point
                focal[0] = int(SzX/2)
                focal[1] = int(SzY/2)
                
            focalTraject = np.linspace(center, focal, numXfades)

            
            # handles final xfade
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xfadeFrames
            curInc = nextInc
            
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length

                    if newDimX > hop_sz:
                        newDimX -= hop_sz
                    if newDimY > hop_sz:
                        newDimY -= hop_sz

                    # scale image to new dimensions
                    imgItr1 = imgXfTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr2 = imgXfTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)

                    imgReBlend = Image.blend(imgItr1, imgItr2, alphaX[t])
                    imgReBlend = ImageOps.autocontrast(imgReBlend, cutoff=0)

                    # calculate box = tuple
                    #newXYbox = ( int(focal[0] - newDimX/2), int(focal[1] - newDimY/2) )
                    newXYbox = ( int(focalTraject[t][0] - newDimX/2), int(focalTraject[t][1] - newDimY/2) )
                    imgXfTscOut.paste(imgReBlend, box=newXYbox, mask=None)


                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # inOrOut controls direction of parascope func
                    if inOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    imgXfTelescNmFull = imgOutDir+imgXfTelescNm+strInc+'.jpg'
                    #imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
                    imgXfTscOut.save(imgXfTelescNmFull)

                    xCnt -= 1                    
                    frameCnt += 1
                    
                    
        print('\n// *---Final Frame Count = '+str(frameCnt)+'---*')
                
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Img Xfade Telescope Sequence Algorithm II::---*
    # // *--------------------------------------------------------------* //fc
    
    def xodXfadeTelescopeII(self, imgFileList, xLength, framesPerSec, xfadeFrames,
                             inOut, rndFocal, rotate, usemask, randomFX,
                             n_digits, imgOutDir, usrMaskDir='None', imgOutNm='None'):
        
        ''' outputs a sequence of telescoping images (zoom in or zoom out)
            The period of telescoping sequence synched to framesPerBeat
            Telescoping xfades from one source image to another
            
            inOut    : telescope direction: 0 = out, 1 = in
            rndFocal : random focal point: 0 = center, 1 = random pixel loc
            rotate   : rotating cross-fade: 0 = no ; 1 = cw ; 2 = ccw
            usemask  : use mask: 0 = no ; 1 = use base img ; 2 = use mask dir
            randomFX : randomize FX: 0 = none ; # = switch randomize every # crossfades
        '''

    
        if imgOutNm != 'None':
            imgXfTelescNm = imgOutNm
        else:
            imgXfTelescNm = 'imgTelescope'
            
            
        if usrMaskDir != 'None' and usemask == 2:
            imgMskDir = usrMaskDir
        else:
            imgMskDir = self.maskDir
            
            

    
        numImg = len(imgFileList)
        
        
        imgFirst = Image.open(imgFileList[0])      

        SzX = imgFirst.width
        SzY = imgFirst.height        
        
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---Total number of frames = '+str(numFrames)+'---*')
        print('// *---number of img per xfade = '+str(xfadeFrames)+'---*')
        print('// *---number of xfades = '+str(numXfades)+'---*')
        print('// *---number of img for Final xfade = '+str(numFinalXfade)+'---*')
        print('\nProcessing ... ... ...\n\n')
        
        
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)            
    
        hop_sz = ceil(SzX/xfadeFrames)  # number of pixels to scale img each iteration
    
        nextInc = 0
        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
            imgClone2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgXfTsc1 = imgClone1
            imgXfTsc2 = imgClone2
            imgXfTscOut = imgClone1

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
                              

            #focal = np.zeros(2)
            #if rndFocal == 1:
            #    focal = eyeutil.randomPxlLoc(int(SzX), int(SzY))


            focal = np.zeros(2)
            center = np.zeros(2)
            center[0] = int(SzX/2)
            center[1] = int(SzY/2)
            if rndFocal == 1:
                focal = eyeutil.randomPxlLoc(int(SzX), int(SzY))
            else:
                focal = center
                    
                
            # calculate a focal trajectory - random point to center
            #slope = (focal[1] - center[1]) / (focal[0] - center[0])
            focalTraject = np.linspace(center, focal, numXfades)

                
                
            # handles final xfade
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xfadeFrames
            curInc = nextInc
            
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length

                    if newDimX > hop_sz:
                        #newDimX -= 2*hop_sz
                        newDimX -= hop_sz
                    if newDimY > hop_sz:
                        #newDimY -= 2*hop_sz
                        newDimY -= hop_sz
                

                    # scale image to new dimensions
                    imgItr1 = imgXfTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr2 = imgXfTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)

                    imgReBlend = Image.blend(imgItr1, imgItr2, alphaX[t])
                    imgReBlend = ImageOps.autocontrast(imgReBlend, cutoff=0)
                
                    
                    
                    if (usemask == 1):
                        
                        #imgMsk2 = imgClone4.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgMsk = imgItr2.convert("L")
                        
                        # calculate box = tuple
                        newXYbox = ( int(focalTraject[t][0] - newDimX/2), int(focalTraject[t][1] - newDimY/2) )
                        imgXfTscOut.paste(imgReBlend, box=newXYbox, mask=imgMsk)                    
                    
                    else:
                        # calculate box = tuple
                        newXYbox = ( int(focalTraject[t][0] - newDimX/2), int(focalTraject[t][1] - newDimY/2) )
                        imgXfTscOut.paste(imgReBlend, box=newXYbox, mask=None)


                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # inOrOut controls direction of parascope func
                    if inOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    imgXfTelescNmFull = imgOutDir+imgXfTelescNm+strInc+'.jpg'
                    #imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
                    imgXfTscOut.save(imgXfTelescNmFull)

                    xCnt -= 1                    
                    frameCnt += 1
                    
                    
        print('\n// *---Final Frame Count = '+str(frameCnt)+'---*')
                
        return 


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Img DivXfade Telescope Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgDivXfadeTelescope(self, imgList, framesPerBeat, imgOutDir, inOut=0, imgOutNm='None'):
        ''' outputs a sequence of telescoping images (zoom in or zoom out)
            The period of telescoping sequence synched to framesPerBeat
            assumes images in imgList are normalized (scaled/cropped) numpy arrays '''
    
        if imgOutNm != 'None':
            imgTelescNm = imgOutNm
        else:
            imgTelescNm = 'imgTelescope'
    
        # find number of source images in src dir
        numSrcImg = len(imgList)
        # initialize SzX, SzY to dimensions of src img
        SzX = imgList[0].shape[1]
        SzY = imgList[0].shape[0]
    
        numFrames = numSrcImg * framesPerBeat
    
        alphaX = np.linspace(0.0001, 1.0, framesPerBeat)               
    
        hop_sz = ceil(np.log(SzX/framesPerBeat))  # number of pixels to scale img each iteration
    
        #imgTelescopeNmArray = []
        #imgTelescopeArray = []
    
        imgCount = numFrames    # counter to increment output name
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(numSrcImg):
            imgClone1 = imgList[i]
            imgClone2 = imgList[(i + 1) % numSrcImg]  # final img+1 -> first img
            
            newDimX = SzX
            newDimY = SzY
            for t in range(framesPerBeat):
                if newDimX > 2:
                    newDimX -= 2*hop_sz
                if newDimY > 2:
                    newDimY -= 2*hop_sz
                # scale image to new dimensions
                imgItr1 = self.odmkEyeRescale(imgClone1, newDimX, newDimY)
                imgItr2 = self.odmkEyeRescale(imgClone2, newDimX, newDimY)
                # image division blend algorithm..
                c = imgItr1/((imgItr2.astype('float')+1)/(256*alphaX[t]))
                # saturating function - if c[m,n] > 255, set to 255:
                imgDIVB = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
                # region = (left, upper, right, lower)
                # subbox = (i + 1, i + 1, newDimX, newDimY)
                for j in range(SzY):
                    for k in range(SzX):
                        #if ((j >= (t+1)*hop_sz) and (j < (newDimY+(SzY-newDimY)/2)) and (k >= (t+1)*hop_sz) and (k < (newDimX+(SzX-newDimX)/2))):
                        if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
                            #imgClone[j+(SzY-newDimY)/2, k+(SzX-newDimX)/2, :] = imgItr[j - t, k - t, :]
                            imgClone1[j, k, :] = imgDIVB[j - (SzY-newDimY)/2, k - (SzX-newDimX)/2, :]
                nextInc += 1
                zr = ''
                if inOut == 1:
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                else:
                    for j in range(n_digits - len(str(imgCount - (nextInc)))):
                        zr += '0'
                    strInc = zr+str(imgCount - (nextInc))
                imgTelescFull = imgOutDir+imgTelescNm+strInc+'.jpg'
                imio.imwrite(imgTelescFull, imgClone1) 
                
        return
   
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE ECHO Bpm Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkEyeEchoBpm(self, imgList, numFrames, echoTrig, numEcho, echoStep, imgOutDir, echoDecay = 'None', imgOutNm='None'):
        ''' Outputs a random sequence of img with downbeat echoes repeat images
            numFrames => total # frames
            echoTrig => trigger echoes [1D array of 0 & 1] - length = numFrames
            numEcho => number of repeats each downbeat
            echoStep => number of frames between each echo
            echoDecay => 'None': no decay ; 'cos': cosine decay
        '''
    
        if imgOutNm != 'None':
            eyeEchoBpmNm = imgOutNm
        else:
            eyeEchoBpmNm = 'eyeEchoBpm'
    
        # eyeEchoBpmNmArray = []
        # eyeEchoBpmArray = []
        
        rIdxArray = eyeutil.randomIdxArray(numFrames, len(imgList))
        rIdxEchoArray = eyeutil.randomIdxArray(numFrames, len(imgList))
        
#        if echoDecay == 'cos':
#            qtrcos = eye.quarterCos(numEcho)    # returns a quarter period cosine wav of length n    
        
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        k = 0
        echoFrames = 0
        for i in range(numFrames):
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = eyeEchoBpmNm+strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            if echoTrig[i] == 1:
                echoImgIdx = rIdxEchoArray[k]
                imio.imsave(imgRndSelFull, imgList[echoImgIdx])
                echoFrames = (numEcho + 1) * echoStep
                k += 1
                h = 1
            elif (h <= echoFrames and (h % echoStep) == 0):
                imio.imsave(imgRndSelFull, imgList[echoImgIdx])
                h += 1
            else:
                imio.imwrite(imgRndSelFull, imgList[rIdxArray[i]])
                h += 1
            
        return      
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Color Enhance::---*')
    # // *--------------------------------------------------------------* //    
        
    def odmkImgColorEnhance(self, imgList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of images fading from img1 -> img2 for xLength seconds
            Linearly alpha-blends images using PIL Image.blend
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgcEnhancerNm = imgOutNm
        else:
            imgcEnhancerNm = 'ImgXfade'
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xfadeFrames = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgList)
        numxfadeImg = numImg * xfadeFrames
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        factorX = np.linspace(0.1, 2.0, xfadeFrames)


        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades - 1):
            if frameCnt <= numFrames:
                if (frameCnt % numxfadeImg) == 0:
                    xfdirection = -xfdirection
                if xfdirection == 1:
                    imgPIL1 = Image.fromarray(imgList[j % numImg])
                    cEnhancer = ImageEnhance.Color(imgPIL1)
                else:
                    imgPIL1 = Image.fromarray(imgList[(numImg-1) - (j % numImg) ])
                    cEnhancer = ImageEnhance.Color(imgPIL1)
                for i in range(xfadeFrames):
                    imgCEn = cEnhancer.enhance(factorX[i])
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    imgcEnhancerFull = imgOutDir+imgcEnhancerNm+strInc+'.jpg'
                    imio.imwrite(imgcEnhancerFull, imgCEn)
                    frameCnt += 1
    
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE Pixel Random Replace::---*
    # // *--------------------------------------------------------------* //

    #def odmkPxlRndReplace(self, imgArray, sLength, framesPerSec, frameCtrl, imgOutDir, imgOutNm='None'):
    def odmkPxlRndReplace(self, imgArray, sLength, framesPerSec, imgOutDir, imgOutNm='None'):
        ''' swap n pixels per frame from consecutive images'''
    
        if imgOutNm != 'None':
            pxlRndReplaceNm = imgOutNm
        else:
            pxlRndReplaceNm = 'pxlRndReplace'
    
        SzX = imgArray[0].shape[1]
        SzY = imgArray[0].shape[0]
    
        numFrames = int(ceil(sLength * framesPerSec))
        #numXfades = int(ceil(numFrames / frameCtrl))

        print('// *---numFrames = '+str(numFrames)+'---*')
        #print('// *---FrameCtrl = '+str(frameCtrl)+'---*')
        #print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgArray)
        #numxfadeImg = numImg * frameCtrl
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0

        eyeBox1 = Image.fromarray(imgArray[eyeutil.randomIdx(numImg)])
        
        frameCnt = 0

        for j in range(numFrames):

            imgPIL1 = Image.fromarray(imgArray[j % (numImg-1)])
          
            boxSzX = round(SzX*random.random()) + 30
            boxSzY = round(SzY*random.random()) + 30

            rndPxlLoc = eyeutil.randomPxlLoc(SzX, SzY)
            alpha = random.random()

            eyeBox1 = self.eyeBox1(eyeBox1, imgPIL1, boxSzX, boxSzY, rndPxlLoc, alpha)



            # update name counter & concat with base img name    
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            pxlRndReplaceFull = imgOutDir+pxlRndReplaceNm+strInc+'.jpg'
            
            # write img to disk
            imio.imwrite(pxlRndReplaceFull, eyeBox1)
            
            frameCnt += 1
    
        return
  
  
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE Pixel Random Replace::---*
    # // *--------------------------------------------------------------* //

    
    #def xodPxlRndRotate(self, imgArray, sLength, framesPerSec, framesPerBeat, imgOutDir, imgOutNm='None'):
    def xodPxlRndRotate(self, imgFileList, xLength, framesPerSec, xfadeFrames, 
                        n_digits, imgOutDir, imgOutNm):
        
        ''' swap n pixels per frame from consecutive images'''
        
        
        numImg = len(imgFileList)
        #numMsk = len(mskFileList)
            
        #imgInit = Image.open(imgFileList[round(numImg*random.random()) % numImg])
        imgInit = Image.open(imgFileList[0])
        
        SzX = imgInit.width
        SzY = imgInit.height
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        #numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')
    

        nextInc = 0

        eyeBase1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
    
        zn = eyeutil.cyclicZn(xfadeFrames)    # less one, then repeat zn[0] for full 360

        zoomScalarXArr = np.linspace(16, SzX//3, numXfades) 
        zoomScalarYArr = np.linspace(9, SzY//3, numXfades)
            
        alphaX = np.linspace(0.0001, 1.0, numXfades)



        frameCnt = 0
        for j in range(numXfades):
            
            imgZoom1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            imgZoom2 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            zoomVertex1 = eyeutil.randomPxlLoc(SzX, SzY)
            rotDirection = round(random.random())
            
            for i in range(xfadeFrames):
                
                if frameCnt <= numFrames:

                    # background image base (pxlRndReplace)
                    #----------------------------------------------------------
                    
                    boxSzX = round(SzX*random.random()) + 16
                    boxSzY = round(SzY*random.random()) + 9                    
 
                    rndPxlLoc = eyeutil.randomPxlLoc(SzX, SzY)
                    alpha = random.random()

                    imgPIL1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                    eyeBase1 = eyeutil.eyeBox1(eyeBase1, imgPIL1, boxSzX, boxSzY, rndPxlLoc, alpha)

                    #----------------------------------------------------------

                    # setup crop coordinates for Zoom sub image
                    # coordinates = (left, bottom, right, top)

                    if (zoomVertex1[0] - int(zoomScalarXArr[i])) < 0:
                        zBoxLeft = 0
                    else:
                        zBoxLeft = zoomVertex1[0] - int(zoomScalarXArr[i])

                    if (zoomVertex1[1] - int(zoomScalarYArr[i])) < 0:
                        zBoxBottom = 0
                    else:
                        zBoxBottom = zoomVertex1[1] - int(zoomScalarYArr[i])                   

                    if (zoomVertex1[0] + int(zoomScalarXArr[i])) > SzX:
                        zBoxRight = SzX
                    else:
                        zBoxRight = zoomVertex1[0] + int(zoomScalarXArr[i])

                    if (zoomVertex1[1] + int(zoomScalarYArr[i])) > SzX:
                        zBoxTop = SzX
                    else:
                        zBoxTop = zoomVertex1[1] + int(zoomScalarYArr[i])

                    boxZoom = (int(zBoxLeft), int(zBoxBottom), int(zBoxRight), int(zBoxTop))
                    
                    subSzX = boxZoom[2] - boxZoom[0]
                    subSzY = boxZoom[3] - boxZoom[1]
                    
                    subLeft = int(SzX//2 - subSzX//2)
                    subBottom = int(SzY//2 - subSzY//2)
                    subRight = subLeft + subSzX
                    subTop = subBottom + subSzY
                    subBox = (subLeft, subBottom, subRight, subTop)
                    eyeSub1 = imgZoom1.crop(subBox) 
                    eyeSub2 = imgZoom2.crop(subBox)

                    alphaB = Image.blend(eyeSub1, eyeSub2, alphaX[i])
                    alphaB = np.array(alphaB)
                    
                    ang = (atan2(zn[i % (numXfades-1)].imag, zn[i % (numXfades-1)].real))*180/np.pi
                    if rotDirection == 1:
                        ang = -ang

                    rotate_alphaB = ndimage.rotate(alphaB, ang, reshape=False)
                    rotate_alphaZ = eyeutil.cropZoom(rotate_alphaB, 2)
                    rotate_alphaZ = Image.fromarray(rotate_alphaZ)
                    
                    eyeBase1.paste(rotate_alphaZ, boxZoom)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    pxlRndReplaceFull = imgOutDir + imgOutNm + strInc + '.jpg'
                    imio.imwrite(pxlRndReplaceFull, eyeBase1)
            
                    frameCnt += 1
    
        return

    
    def odmkLfoParascopeIII(self, imgFileList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' lfoParascope III function '''
    
        if imgOutNm != 'None':
            imgLfoParascopeNm = imgOutNm
        else:
            imgLfoParascopeNm = 'imgLfoParascope'
    
        imgObjTemp1 = imio.imread(imgFileList[0])         

        SzX = imgObjTemp1.shape[1]
        SzY = imgObjTemp1.shape[0]
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgFileList)
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        
        #hop_szA = np.linspace(555, 2, xfadeFrames)
        #hop_szA = np.linspace(6, 196, xfadeFrames)
        
        
        alphaX = np.linspace(0.3, 0.7, xfadeFrames)



        # generate an LFO sin control signal - 1 cycle per xfadeFrames
#        T = 1.0 / framesPerSec    # sample period
#        LFO_T = 8 * xfadeFrames * T
#        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
#        x = x[0:len(x)-1]
#        LFOAMP = 46
#        LFO = LFOAMP*np.sin(LFO_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):
            
            # sequential img grap from image Array
            #imgClone1 = imio.imread(imgFileList[j*xfadeFrames % numImg])
            #imgClone2 = imio.imread(imgFileList[(j*xfadeFrames+int(xfadeFrames/2)) % numImg])
            
            # random img grap from image Array
            imgClone1 = imio.imread(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = imio.imread(imgFileList[round(numImg*random.random()) % numImg])

                
            # initialize output 
            #imgBpTsc1 = imgClone1.copy()
            #imgBpTsc2 = imgClone2.copy()
            imgSub2 = imgClone1.copy()
            imgBpTscOut = imgClone2.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            
            hopScl = round(270*random.random())
            #hop_szA = np.linspace(20*hopScl, 276*hopScl, xfadeFrames)
            #hop_szA = np.linspace(56, 360, xfadeFrames)
                              
            # calculate X-Y random focal point to launch telescope
#            focalRnd1 = randomPxlLoc(SzX, SzY)
#            if (focalRnd1[0] < SzX/2):
#                offsetX = -int(SzX/2 - focalRnd1[0])
#            else:
#                offsetX = int(focalRnd1[0] - SzX/2)
#            if (focalRnd1[1] < SzY/2):
#                offsetY = -int(SzY/2 - focalRnd1[1])
#            else:
#                offsetY = int(focalRnd1[1] - SzY/2)

            #print('focalRnd1 = ['+str(focalRnd1[0])+', '+str(focalRnd1[1])+']')
            #print('offsetX = '+str(offsetX))
            #print('offsetY = '+str(offsetY))

            # focalRnd2 = randomPxlLoc(SzX, SzY)


            # *** previous ***

            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                    
                    newDimX -= hopScl
                    if newDimX < 2560:
                        newDimX = 2560
                    newDimX = int(newDimX)
                    
                    newDimY -= hopScl
                    if newDimY < 2560:
                        newDimY = 2560
                    newDimY = int(newDimY)
                    
#                    newDimX -= hop_szA[t]
#                    if newDimX < 660:
#                        newDimX = 660
#                    newDimX = int(newDimX)
#                    
#                    newDimY -= hop_szA[t]
#                    if newDimY < 660:
#                        newDimY = 660
#                    newDimY = int(newDimY)

                        
                    # scale image to new dimensions
                    #imgItr1 = self.odmkEyeRescale(imio.imread(imgFileList[t*xfadeFrames % numImg]), newDimX, newDimY)
                    imgItr1 = self.odmkEyeRescale(imgClone1, newDimX, newDimY)
                   
                    imgItr2 = self.odmkEyeRescale(imgSub2, newDimX, newDimY)
                    
                    imgItr3 = self.odmkEyeRescale(imio.imread(imgFileList[round(numImg*random.random()) % numImg]), newDimX, newDimY)
                    
                    imgMix1 = Image.blend(Image.fromarray(imgItr1), Image.fromarray(imgItr3), 0.5)
                    imgMix1 = ImageOps.autocontrast(imgMix1, cutoff=0)
                    imgMix1 = np.array(imgMix1)
                    
                    imgMix2 = Image.blend(Image.fromarray(imgItr1), Image.fromarray(imgItr2), 0.5)
                    imgMix2 = ImageOps.autocontrast(imgMix2, cutoff=0)
                    
                    imgMixTemp = Image.blend(Image.fromarray(imgItr1), Image.fromarray(imgItr3), 0.5)
                    imgMixTemp = ImageOps.autocontrast(imgMix2, cutoff=0)
                    imgMix3 = Image.blend(Image.fromarray(imgItr2), imgMixTemp, 0.5)
                    imgMix3 = ImageOps.autocontrast(imgMix3, cutoff=0)
                    imgMix3 = np.array(imgMix3)
                    
                    if (round(random.random())):
                        imgSub1 = imgMix1
                    else:
                        imgSub1 = imgItr1
                        
                    if (round(random.random())):
                        imgSub2 = imgItr2
                    else:
                        imgSub2 = imgMix3
                        
                        
                    #imgBpTscOut = self.eyeSubInsert(imgBpTsc1, imgBpTsc2, imgSub1, imgSub2, SzX, SzY, newDimX, newDimY, alphaX[t])
                    imgBpTscOut = self.eyeSubInsert(imgClone1, imgClone2, imgSub1, imgSub2, SzX, SzY, newDimX, newDimY, alphaX[t])
                            

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # rewrite inOrOut as bipolar toggle switch in loop above
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            zr += '0'
                        strInc = zr+str(numFrames - (nextInc))
                    imgLfoParascopeFull = imgOutDir+imgLfoParascopeNm+strInc+'.jpg'
                    imio.imwrite(imgLfoParascopeFull, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)
                    
                    frameCnt += 1
    
        return
  


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE Bananasloth Recursion::---*
    # // *--------------------------------------------------------------* //
    
    def odmkBSlothRecurs(self, imgArray, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', indexOffset='None'):
        ''' BSlothRecurs function '''
    
        if imgOutNm != 'None':
            imgBSlothRecursNm = imgOutNm
        else:
            imgBSlothRecursNm = 'imgBSlothRecurs'
            
            
#        if indexOffset != 'None':
#            idxOffset = indexOffset
#        else:
#            idxOffset = 0       
            
    
        SzX = imgArray[0].shape[1]
        SzY = imgArray[0].shape[0]
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgArray)
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        # example internal control signal 
        #hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
        #hop_sz = 5
    
        imgRndIdxArray = eyeutil.randomIdxArray(numFrames, numImg)   

        # imgBSlothRecursNmArray = []
        # imgBSlothRecursArray = []

        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades):
            
            hop_sz = round(16*random.random())
            if hop_sz == 0:
                hop_sz = 5      # avoid zero - 5 is good default
            
            
            inOrOut = round(random.random())        
            
            # forword <-> backward img grap from rnd img dir
            if (frameCnt % numXfades) == 0:
                xfdirection = -xfdirection
            if xfdirection == 1:
                imgClone1 = imgArray[imgRndIdxArray[j]]
                imgClone2 = imgArray[imgRndIdxArray[j+1]]                
            else:
                imgClone1 = imgArray[imgRndIdxArray[(numImg-2) - j]]
                imgClone2 = imgArray[imgRndIdxArray[(numImg-2) - j+1]]

                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgBpTsc1 = imgClone1
            imgBpTsc2 = imgClone2
            imgBpTscOut = imgClone1

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
                              
            # calculate X-Y random focal point to launch telescope
            pxlLocScaler = 3*(round(7*random.random())+1)
            #pxlLocScaler = 3*(round(5*random.random())+1)
            pxlLocScaler2x = pxlLocScaler * 2
            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/pxlLocScaler), int(SzY/pxlLocScaler))
            if (focalRnd1[0] < SzX/pxlLocScaler2x):
                offsetX = -int(SzX/pxlLocScaler2x - focalRnd1[0])
            else:
                offsetX = int(focalRnd1[0] - SzX/pxlLocScaler2x)
            if (focalRnd1[1] < SzY/pxlLocScaler2x):
                offsetY = -int(SzY/pxlLocScaler2x - focalRnd1[1])
            else:
                offsetY = int(focalRnd1[1] - SzY/pxlLocScaler2x)


            rotateSubFrame1 = 0             # randomly set rotation on/off
            rotDirection1 = 0
            if (round(13*random.random()) > 7):
                offsetX = 0
                offsetY = 0
                rotateSubFrame1 = 1
                hop_sz = round(56*random.random())
                if (round(random.random())):
                    rotDirection1 = 1


            # functionalize then call for each telescope
#            xfadeMpy = round(6*random.random())
#            if xfadeMpy == 0:
#                xfadeMpy = 1
#            xFrames = int(xfadeFrames/xfadeMpy)    # randomly mpy xfadeFrames 1:3
            xFrames = xfadeFrames
            
            alphaX = np.linspace(0.0, 1.0, xFrames)   
            zn = eyeutil.cyclicZn(xFrames-1)    # less one, then repeat zn[0] for full 360            
            
            xCnt  = xFrames
            curInc = nextInc
            
            for t in range(xFrames):
                if frameCnt < numFrames:    # process until end of total length

                    if newDimX > hop_sz + 1:
                        #newDimX -= 2*hop_sz
                        newDimX -= hop_sz
                    if newDimY > hop_sz + 1:
                        #newDimY -= 2*hop_sz
                        newDimY -= hop_sz
                        
                    # scale image to new dimensions
                    imgItr1 = self.odmkEyeRescale(imgBpTsc2, newDimX, newDimY)
                    if rotateSubFrame1 == 1:
                        
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        imgItr1 = ndimage.rotate(imgItr1, ang, reshape=False)
                        
                        imgItr1 = self.cropZoom(imgItr1, 2)

                    imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                    if rotateSubFrame1 == 1:
                    
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection1 == 0:
                            ang = -ang
                            
                        imgItr2 = ndimage.rotate(imgItr2, ang, reshape=False)
                        
                        imgItr2 = self.cropZoom(imgItr2, 2)


                    # region = (left, upper, right, lower)
                    # subbox = (i + 1, i + 1, newDimX, newDimY)
                    for j in range(SzY):
                        for k in range(SzX):
                            
                            # calculate bipolar subframes then interleave (out = priority)
                            # will require handling frame edges (no write out of frame)
                            # update index math to handle random focal points
                           
                            if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):                                
                                
                                #imgBpTsc1[j, k, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
                                #imgBpTsc2[j, k, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]

                                    
                                if ( (j+offsetY >= 0)  and (j+offsetY < SzY) and (k+offsetX >= 0)  and (k+offsetX < SzX) ):
                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; j+offsetY = '+str(j+offsetY)+'; k+offsetX = '+str(k+offsetX))
                                    imgBpTsc1[j+offsetY, k+offsetX, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
                                    imgBpTsc2[j+offsetY, k+offsetX, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]                                    
                                    

                    imgBpTscOut = Image.blend(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2), alphaX[t])
                    imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # inOrOut controls direction of parascope func
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    if self.imgFormat == 'fjpg':
                        imgBSlothRecursFull = imgOutDir+imgBSlothRecursNm+strInc+'.jpg'
                    else:
                        imgBSlothRecursFull = imgOutDir+imgBSlothRecursNm+strInc+'.bmp'                            
                    imio.imwrite(imgBSlothRecursFull, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)
                    
                    xCnt -= 1
                    frameCnt += 1
    
        return
        # return [imgBSlothRecursArray, imgBSlothRecursNmArray]

    
    # // *--------------------------------------------------------------* //
    # // *---::XODMKEYE - EYE Bananasloth Glitch Recursion Switch::---*
    # // *--------------------------------------------------------------* //
    
    def xodBSlothSwitch(self, imgFileList, xLength, framesPerSec, xfadeFrames, 
                        n_digits, imgOutDir, imgOutNm='None', inOrOut=0, indexOffset='None'):
        ''' XODMK BSlothSwitch function '''
    
    
        if imgOutNm != 'None':
            imgBSlothGlitch1Nm = imgOutNm
        else:
            imgBSlothGlitch1Nm = 'imgBSlothGlitch1'    

        numImg = len(imgFileList)

        imgBpTscOut = Image.open(imgFileList[eyeutil.randomIdx(numImg)])      

        SzX = imgBpTscOut.width
        SzY = imgBpTscOut.height

    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        # finalXfade = int(floor(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---Total number of frames = '+str(numFrames)+'---*')
        print('// *---number of img per xfade = '+str(xfadeFrames)+'---*')
        print('// *---number of xfades = '+str(numXfades)+'---*')
        print('// *---number of img for Final xfade = '+str(numFinalXfade)+'---*')
        print('\nProcessing ... ... ...\n\n')
        
        #pdb.set_trace()

        nextInc = 0
        # example internal control signal 
        hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
     
    
        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
            imgClone2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgBpTsc1 = imgClone1
            imgBpTsc2 = imgClone2
            imgBpTscOut = imgClone1

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
                              
            # calculate X-Y random focal point to launch telescope
            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
            focal1 = (focalRnd1[0] + SzX/4, focalRnd1[1] + SzY/4)
            focalRnd2 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
            focal2 = (focalRnd2[0] + SzX/4, focalRnd2[1] + SzY/4)


            rotateSubFrame1 = 0             # randomly set rotation on/off
            rotDirection1 = 0
            if (round(8*random.random()) > 6):
                rotateSubFrame1 = 1
                if (round(random.random())):
                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
            if (round(8*random.random()) > 6):
                rotateSubFrame2 = 1
                if (round(random.random())):
                    rotDirection2 = 1
                    
            
            # functionalize then call for each telescope
#            xfadeMpy = round(6*random.random())
#            if xfadeMpy == 0:
#                xfadeMpy = 1
#            xFrames = int(xfadeFrames/xfadeMpy)    # randomly mpy xfadeFrames 1:3
            xFrames = xfadeFrames            
            
            
            alphaX = np.linspace(0.0, 1.0, xFrames)   
            #zn = cyclicZn(2*xFrames-1)    # less one, then repeat zn[0] for full 360 
            zn = eyeutil.cyclicZn(2*xFrames)    # less one, then repeat zn[0] for full 360 

            # handles final xfade 
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xFrames
            curInc = nextInc
            

            # __Process xFrames length xFades between two images__            
            
            xFadeSel = round(3*random.random())
            
            if xFadeSel==0:
            
                # ***** FX Tempo Synched FADE FX I *****
                
                for t in range(xFrames):
                    if frameCnt < numFrames:    # process until end of total length
    
                        if newDimX > hop_sz:
                            newDimX -= 2*hop_sz
                            #newDimX -= 3*hop_sz
                        if newDimY > hop_sz:
                            newDimY -= 2*hop_sz
                            #newDimY -= 3*hop_sz
                            
                        # scale image to new dimensions
                        imgItr1 = imgBpTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = eyeutil.eyeRotate(imgItr1, ang, rotd=rotDirection2)
    
                        imgItr2 = imgBpTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame2 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection2 == 1:
                                ang = -ang
                                
                            imgItr2 = eyeutil.eyeRotate(imgItr2, ang, rotd=rotDirection2)
                                        
                        # calculate box = tuple
                        newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                        newXYbox2 = ( int(focal2[0] - newDimX/2), int(focal2[1] - newDimY/2) )
                        imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                        imgBpTsc2.paste(imgItr2, box=newXYbox2, mask=None)
    
                        imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                        imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)
    
                        # update name counter & concat with base img name    
                        nextInc += 1
                        zr = ''
        
                        # inOrOut controls direction of parascope func
                        if inOrOut == 1:
                            for j in range(n_digits - len(str(nextInc))):
                                zr += '0'
                            strInc = zr+str(nextInc)
                        else:
                            #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imgBpTscOut.save(imgBSlothGlitch1Full)
    
                        xCnt -= 1                    
                        frameCnt += 1


            elif xFadeSel==1:
                        
                # ***** FX Tempo Synched FADE FX II *****
                
                for t in range(xFrames):
                    if frameCnt < numFrames:    # process until end of total length
    
                        if newDimX > hop_sz:
                            newDimX -= 4*hop_sz
                            #newDimX -= 3*hop_sz
                            #newDimX -= hop_sz
                        if newDimY > hop_sz:
                            newDimY -= 4*hop_sz
                            #newDimY -= 3*hop_sz
                            #newDimY -= hop_sz
                            
                        # scale image to new dimensions
                        imgItr1 = imgBpTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = eyeutil.eyeRotate(imgItr1, ang, rotd=rotDirection2)
    
                        imgItr2 = imgBpTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame2 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection2 == 1:
                                ang = -ang
                                
                            imgItr2 = eyeutil.eyeRotate(imgItr2, ang, rotd=rotDirection2)
                                        
                        # calculate box = tuple
                        newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                        newXYbox2 = ( int(focal2[0] - newDimX/2), int(focal2[1] - newDimY/2) )
                        imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                        imgBpTsc2.paste(imgItr2, box=newXYbox2, mask=None)
    
                        imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                        imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)
    
                        # update name counter & concat with base img name    
                        nextInc += 1
                        zr = ''
        
                        # inOrOut controls direction of parascope func
                        if inOrOut == 1:
                            for j in range(n_digits - len(str(nextInc))):
                                zr += '0'
                            strInc = zr+str(nextInc)
                        else:
                            #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imgBpTscOut.save(imgBSlothGlitch1Full)
    
                        xCnt -= 1                    
                        frameCnt += 1
                        
                    # // END <if frameCnt < numFrames:    # process until end of total length>
                # // END <for t in range(xFrames):>
                # // END - xFade II

            elif xFadeSel==2:                        
                        
                # ***** FX Tempo Synched FADE FX III *****
                
                for t in range(xFrames):
                    if frameCnt < numFrames:    # process until end of total length
    
                        if newDimX > hop_sz + 1:
                            newDimX -= 2*hop_sz
                            #newDimX -= hop_sz
                        if newDimY > hop_sz + 1:
                            newDimY -= 2*hop_sz
                            #newDimY -= hop_sz
                            
                        # scale image to new dimensions
                        imgItr1 = imgBpTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = eyeutil.eyeRotate(imgItr1, ang, rotd=rotDirection2)
    
                        imgItr2 = imgBpTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame1 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 0:
                                ang = -ang
                                
                            imgItr2 = eyeutil.eyeRotate(imgItr2, ang, rotd=rotDirection2)
    
    
                        # calculate box = tuple
                        newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                        newXYbox2 = ( int(focal2[0] - newDimX/2), int(focal2[1] - newDimY/2) )
                        imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                        imgBpTsc2.paste(imgItr2, box=newXYbox2, mask=None)
    
                        imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                        imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)    


                        # update name counter & concat with base img name    
                        nextInc += 1
                        zr = ''
        
                        # inOrOut controls direction of parascope func
                        if inOrOut == 1:
                            for j in range(n_digits - len(str(nextInc))):
                                zr += '0'
                            strInc = zr+str(nextInc)
                        else:
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imgBpTscOut.save(imgBSlothGlitch1Full)


                        xCnt -= 1
                        frameCnt += 1
                        
                    # // END <if frameCnt < numFrames:    # process until end of total length>
                # // END <for t in range(xFrames):>
                # // END - xFade III

            elif xFadeSel==3:                        
                        
                # ***** FX Tempo Synched FADE FX IV *****
                
                for t in range(xFrames):
                    if frameCnt < numFrames:    # process until end of total length
    
                        if newDimX > hop_sz:
                            newDimX -= 9*hop_sz
                            #newDimX -= 3*hop_sz
                        if newDimY > hop_sz:
                            newDimY -= 9*hop_sz
                            #newDimY -= 3*hop_sz
                            
                        # scale image to new dimensions
                        imgItr1 = imgBpTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = eyeutil.eyeRotate(imgItr1, ang, rotd=rotDirection2)
    
                        imgItr2 = imgBpTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        if rotateSubFrame2 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection2 == 1:
                                ang = -ang
                                
                            imgItr2 = eyeutil.eyeRotate(imgItr2, ang, rotd=rotDirection2)
                            
                            
                        # arr = array(img)
                        # convert from Numpy array to Image image:
                        # img = Image.fromarray(array)
                            
                        # image division blend algorithm..
                        # c = imgItr1/((imgItr2.astype('float')+1)/(256*alphaX[t]))
                        c = np.array(imgItr1)/((np.array(imgItr2).astype('float')+1)/(256*alphaX[t]))
                        
                        # saturating function - if c[m,n] > 255, set to 255:
                        imgDIVB = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
                        #pdb.set_trace()
                        imgDivBImg = Image.fromarray(imgDIVB.astype('uint8'))
                                
                        # calculate box = tuple
                        newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                        newXYbox2 = ( int(focal2[0] - newDimX/2), int(focal2[1] - newDimY/2) )
                        imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                        imgBpTsc2.paste(imgDivBImg, box=newXYbox2, mask=None)
    
                        imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                        imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)
    
                        # update name counter & concat with base img name    
                        nextInc += 1
                        zr = ''
        
                        # inOrOut controls direction of parascope func
                        if inOrOut == 1:
                            for j in range(n_digits - len(str(nextInc))):
                                zr += '0'
                            strInc = zr+str(nextInc)
                        else:
                            #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imgBpTscOut.save(imgBSlothGlitch1Full)

                        xCnt -= 1                    
                        frameCnt += 1
                    
                    
        print('\n// *---Final Frame Count = '+str(frameCnt)+'---*')
    
        return


    # // *--------------------------------------------------------------* //
    # // *---::XODMKEYE - EYE Bananasloth Glitch Recursion::---*
    # // *--------------------------------------------------------------* //

    def xodBSlothGlitch(self, imgFileList, xLength, framesPerSec, xfadeFrames, n_digits, imgOutDir, imgOutNm='None', inOrOut=0, indexOffset='None'):
        ''' xodBSlothGlitch function '''
 
        if imgOutNm != 'None':
            imgBSlothGlitch1Nm = imgOutNm
        else:
            imgBSlothGlitch1Nm = 'imgBSlothGlitch1'    

        numImg = len(imgFileList)

        imgBpTscOut = Image.open(imgFileList[eyeutil.randomIdx(numImg)])      

        SzX = imgBpTscOut.width
        SzY = imgBpTscOut.height

    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        # finalXfade = int(floor(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---Total number of frames = '+str(numFrames)+'---*')
        print('// *---number of img per xfade = '+str(xfadeFrames)+'---*')
        print('// *---number of xfades = '+str(numXfades)+'---*')
        print('// *---number of img for Final xfade = '+str(numFinalXfade)+'---*')
        print('\nProcessing ... ... ...\n\n')


        nextInc = 0
        # example internal control signal 
        hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration

   
        # imgBSlothRecursNmArray = []
        # imgBSlothRecursArray = []   
    
        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
            imgClone2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgBpTsc1 = imgClone1
            imgBpTsc2 = imgClone2
            imgBpTscOut = imgClone1

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            
            # calculate X-Y random focal point to launch telescope
            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
            focal1 = (focalRnd1[0] + SzX/4, focalRnd1[1] + SzY/4)
            focalRnd2 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
            focal2 = (focalRnd2[0] + SzX/4, focalRnd2[1] + SzY/4)

            rotateSubFrame1 = 0             # randomly set rotation on/off
            rotDirection1 = 0
            if (round(8*random.random()) > 6):
                rotateSubFrame1 = 1
                if (round(random.random())):
                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
            if (round(8*random.random()) > 6):
                rotateSubFrame2 = 1
                if (round(random.random())):
                    rotDirection2 = 1
                    
            
            # functionalize then call for each telescope
#            xfadeMpy = round(6*random.random())
#            if xfadeMpy == 0:
#                xfadeMpy = 1
#            xFrames = int(xfadeFrames/xfadeMpy)    # randomly mpy xfadeFrames 1:3
            xFrames = xfadeFrames
            
            
            alphaX = np.linspace(0.0, 1.0, xFrames)
            zn = eyeutil.cyclicZn(xFrames-1)    # less one, then repeat zn[0] for full 360            

            # handles final xfade
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xFrames
            curInc = nextInc
            
            for t in range(xFrames):
                if frameCnt < numFrames:    # process until end of total length

                    if newDimX > hop_sz:
                        #newDimX -= 2*hop_sz
                        newDimX -= hop_sz
                    if newDimY > hop_sz:
                        #newDimY -= 2*hop_sz
                        newDimY -= hop_sz
                        
                    # scale image to new dimensions
                    imgItr1 = imgBpTsc2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    if rotateSubFrame1 == 1:
                        
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        imgItr1 = eyeutil.eyeRotate(imgItr1, ang, rotd=rotDirection2)

                    imgItr2 = imgBpTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    if rotateSubFrame2 == 1:
                    
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        imgItr2 = eyeutil.eyeRotate(imgItr2, ang, rotd=rotDirection2)
                        
                        
                    # calculate box = tuple
                    newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                    newXYbox2 = ( int(focal2[0] - newDimX/2), int(focal2[1] - newDimY/2) )
                    imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                    imgBpTsc2.paste(imgItr2, box=newXYbox2, mask=None)


                    #imgBpTscOut = Image.blend(Image.fromarray(imgArrTsc1), Image.fromarray(imgArrTsc2), alphaX[t])
                    imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                    imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # inOrOut controls direction of parascope func
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                    #imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
                    imgBpTscOut.save(imgBSlothGlitch1Full)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
                    
        print('\n// *---Final Frame Count = '+str(frameCnt)+'---*')
    
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - ODMKEYE - EYE FxSlothCultLife Glitch::---*
    # // *--------------------------------------------------------------* //
    
    def xodFxSlothCult(self, imgFileList, mskFileList, xLength, framesPerSec,
                       xfadeFrames, n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' FxSlothCult function '''


        if imgOutNm != 'None':
            imgFxSlothCultNm = imgOutNm
        else:
            imgFxSlothCultNm = 'imgFxSlothCult'
            
        numImg = len(imgFileList)
        numMsk = len(mskFileList)

        imgSrc1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
        imgBpTscOut = Image.open(imgFileList[eyeutil.randomIdx(numImg)])

        SzX = imgSrc1.width
        SzY = imgSrc1.height


        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    

    
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)
        
        nextInc = 0
        frameCnt = 0
        for j in range(numXfades):
            
            imgMsk1 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk1 = imgMsk1.convert("L")
            imgMsk2 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk2 = imgMsk2.convert("L")
            imgMsk3 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk3 = imgMsk3.convert("L")
            imgMsk4 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk4 = imgMsk4.convert("L")

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            
            # number of pixels to scale img each iteration
            hop_szx = int( (SzX/(1*xfadeFrames))*random.random() + int(SzX/23) )
            hop_szy = int( (SzY/(1*xfadeFrames))*random.random() + int(SzY/23) )
            
            
            #hop_szx = 32
            #hop_szy = 32
                              
            focal0 = (int(SzX/2), int(SzY/2))
            # calculate X-Y random focal point to launch telescope
            focalRnd1 = eyeutil.randomPxlLoc(SzX, SzY)
            focal1 = (focalRnd1[0], focalRnd1[1])
            focalRnd2 = eyeutil.randomPxlLoc(SzX, SzY)
            focal2 = (focalRnd2[0]/4, focalRnd2[1]/4)
#            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
#            focal1 = (focalRnd1[0] + SzX/4, focalRnd1[1] + SzY/4)
#            focalRnd2 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
#            focal2 = (focalRnd2[0] + SzX/4, focalRnd2[1] + SzY/4)


            rotateSubFrame1 = 0             # randomly set rotation on/off
            rotDirection1 = 0
            if (round(random.random())):
                rotateSubFrame1 = 1
                if (round(random.random())):
                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
            if (round(random.random())):
                rotateSubFrame2 = 1
                if (round(random.random())):
                    rotDirection2 = 1

            
            #alphaX = np.linspace(0.3, 0.7, xfadeFrames)   
            zn = eyeutil.cyclicZn(xfadeFrames-1)    # less one, then repeat zn[0] for full 360            

            # handles final xfade 
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xfadeFrames
            curInc = nextInc
            
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                    
                    imgSrc2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
                    # imgSrc3 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])

                    if newDimX > hop_szx:
                        newDimX -= hop_szx
                    if newDimY > hop_szy:
                        newDimY -= hop_szy
                        
                    #print('newDimX = '+str(newDimX))
                        
                    # scale image to new dimensions
                    #imgObjTemp1 = Image.open(imgFileList[frameCnt % numImg])
                    #imgObjTemp1 = imgBpTscOut.copy()
                    mskCpy1 = imgMsk1.copy()
                    mskItr1 = mskCpy1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    if rotateSubFrame1 == 1:
                        ang = (atan2(zn[t % (xfadeFrames-1)].imag, zn[t % (xfadeFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        mskItr1 = eyeutil.eyeRotate(mskItr1, ang, rotd=rotDirection1)
                        
                    mskCpy2 = imgMsk2.copy()
                    mskItr2 = mskCpy2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    if rotateSubFrame2 == 1:
                        ang = (atan2(zn[t % (xfadeFrames-1)].imag, zn[t % (xfadeFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        mskItr2 = eyeutil.eyeRotate(mskItr2, ang, rotd=rotDirection2)
                        
                    #imgBpTscX = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                    
                    # calculate box = tuple
                    newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                    newXYbox2 = ( int(focal2[0] + newDimX/2), int(focal2[1] + newDimY/2) )
                    
                    imgMsk1.paste(mskItr1, box=newXYbox1, mask=None)
                    imgMsk2.paste(mskItr2, box=newXYbox2, mask=None)

                    #imgBlend1 = Image.blend(imgCpy1, imgCpy2, alphaX[t])
                    #imgBlend1 = ImageOps.autocontrast(imgBlend1, cutoff=0)
                    imgSrc3 = Image.blend(imgSrc1, imgSrc2, alphaX[t])
                    imgSrc3 = ImageOps.autocontrast(imgSrc3, cutoff=0)
                    
                    newXYbox3 = ( int(focal0[0] - SzX/2), int(focal0[1] - SzY/2) )
                    
                    imgSrc1.paste(imgSrc3, box=newXYbox3, mask=imgMsk1)
                    imgSrc2.paste(imgSrc3, box=newXYbox3, mask=imgMsk2)
                    
                    imgBpTscOut.paste(imgSrc1, box=newXYbox3, mask=imgMsk3)
                    imgBpTscOut.paste(imgSrc2, box=newXYbox3, mask=imgMsk3)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # inOrOut controls direction of parascope func
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    imgFxSlothCultFull = imgOutDir+imgFxSlothCultNm+strInc+'.jpg'
                    #imio.imwrite(imgFxSlothCultFull, imgBpTscOut)
                    imgBpTscOut.save(imgFxSlothCultFull)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
                    
            imgSrc1 = imgBpTscOut
    
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - ODMKEYE - EYE xodFxSlothCultII Glitch::---*
    # // *--------------------------------------------------------------* //
    
    def xodFxSlothCultII(self, imgFileList, mskFileList, xLength, framesPerSec,
                       xfadeFrames, n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' FxSlothCult function '''


        if imgOutNm != 'None':
            imgFxSlothCultNm = imgOutNm
        else:
            imgFxSlothCultNm = 'imgFxSlothCult'
            
        numImg = len(imgFileList)
        numMsk = len(mskFileList)

        imgSrc1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
        imgBpTscOut = Image.open(imgFileList[eyeutil.randomIdx(numImg)])

        SzX = imgSrc1.width
        SzY = imgSrc1.height


        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    

    
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)
        
        nextInc = 0
        frameCnt = 0
        for j in range(numXfades):
            
            imgMsk1 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk1 = imgMsk1.convert("L")
            imgMsk2 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk2 = imgMsk2.convert("L")
            imgMsk3 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk3 = imgMsk3.convert("L")
            imgMsk4 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk4 = imgMsk4.convert("L")

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            
            # number of pixels to scale img each iteration
            hop_szx = int( (SzX/(1*xfadeFrames))*random.random() + int(SzX/23) )
            hop_szy = int( (SzY/(1*xfadeFrames))*random.random() + int(SzY/23) )
            
            
            #hop_szx = 32
            #hop_szy = 32
                              
            focal0 = (int(SzX/2), int(SzY/2))
            # calculate X-Y random focal point to launch telescope
            focalRnd1 = eyeutil.randomPxlLoc(SzX, SzY)
            focal1 = (focalRnd1[0], focalRnd1[1])
            focalRnd2 = eyeutil.randomPxlLoc(SzX, SzY)
            focal2 = (focalRnd2[0]/4, focalRnd2[1]/4)
#            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
#            focal1 = (focalRnd1[0] + SzX/4, focalRnd1[1] + SzY/4)
#            focalRnd2 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
#            focal2 = (focalRnd2[0] + SzX/4, focalRnd2[1] + SzY/4)


            rotateSubFrame1 = 0             # randomly set rotation on/off
            rotDirection1 = 0
            if (round(random.random())):
                rotateSubFrame1 = 1
                if (round(random.random())):
                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
            if (round(random.random())):
                rotateSubFrame2 = 1
                if (round(random.random())):
                    rotDirection2 = 1

            
            #alphaX = np.linspace(0.3, 0.7, xfadeFrames)   
            zn = eyeutil.cyclicZn(xfadeFrames-1)    # less one, then repeat zn[0] for full 360            

            # handles final xfade 
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xfadeFrames
            curInc = nextInc
            
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                    
                    imgSrc2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
                    # imgSrc3 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])

                    if newDimX > hop_szx:
                        newDimX -= hop_szx
                    if newDimY > hop_szy:
                        newDimY -= hop_szy
                        
                    #print('newDimX = '+str(newDimX))
                        
                    # scale image to new dimensions
                    #imgObjTemp1 = Image.open(imgFileList[frameCnt % numImg])
                    #imgObjTemp1 = imgBpTscOut.copy()
                    mskCpy1 = imgMsk1.copy()
                    mskItr1 = mskCpy1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    if rotateSubFrame1 == 1:
                        ang = (atan2(zn[t % (xfadeFrames-1)].imag, zn[t % (xfadeFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        mskItr1 = eyeutil.eyeRotate(mskItr1, ang, rotd=rotDirection1)
                        
                    mskCpy2 = imgMsk2.copy()
                    mskItr2 = mskCpy2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    if rotateSubFrame2 == 1:
                        ang = (atan2(zn[t % (xfadeFrames-1)].imag, zn[t % (xfadeFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        mskItr2 = eyeutil.eyeRotate(mskItr2, ang, rotd=rotDirection2)
                        
                    #imgBpTscX = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                    
                    # calculate box = tuple
                    newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                    newXYbox2 = ( int(focal2[0] + newDimX/2), int(focal2[1] + newDimY/2) )
                    
                    imgMsk1.paste(mskItr1, box=newXYbox1, mask=None)
                    imgMsk2.paste(mskItr2, box=newXYbox2, mask=None)

                    #imgBlend1 = Image.blend(imgCpy1, imgCpy2, alphaX[t])
                    #imgBlend1 = ImageOps.autocontrast(imgBlend1, cutoff=0)
                    imgSrc3 = Image.blend(imgSrc1, imgSrc2, alphaX[t])
                    imgSrc3 = ImageOps.autocontrast(imgSrc3, cutoff=0)
                    
                    newXYbox3 = ( int(focal0[0] - SzX/2), int(focal0[1] - SzY/2) )
                    
                    imgSrc1.paste(imgSrc3, box=newXYbox3, mask=imgMsk1)
                    imgSrc2.paste(imgSrc3, box=newXYbox3, mask=imgMsk2)
                    imgSrc2 = eyeutil.eyeMirrorQuad(imgSrc2)
                    
                    imgBpTscOut.paste(imgSrc1, box=newXYbox3, mask=imgMsk3)
                    imgBpTscOut.paste(imgSrc2, box=newXYbox3, mask=imgMsk3)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # inOrOut controls direction of parascope func
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    imgFxSlothCultFull = imgOutDir+imgFxSlothCultNm+strInc+'.jpg'
                    #imio.imwrite(imgFxSlothCultFull, imgBpTscOut)
                    imgBpTscOut.save(imgFxSlothCultFull)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
                    
            imgSrc1 = imgBpTscOut
    
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYEu - LFO Parascope telescope img f::---*
    # // *--------------------------------------------------------------* //
    
    def xodLfoParascope(self, imgFileList, xLength, framesPerSec, xfadeFrames, 
                         n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' xodLfoParascope function '''
    
        if imgOutNm != 'None':
            imgLfoParascopeNm = imgOutNm
        else:
            imgLfoParascopeNm = 'imgLfoParascope'
    
        #imgObjTemp1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
        imgBpTscOut = Image.open(imgFileList[0])

        SzX = imgBpTscOut.width
        SzY = imgBpTscOut.height
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgFileList)
    
        nextInc = 0
        # example internal control signal 
        #hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
        hop_sz = SzY/42
        
        alphaX = np.linspace(0.3, 0.7, xfadeFrames)

        focal1 = (int(SzX/2), int(SzY/2))
        focalMod = np.array([int(SzX/2), int(SzY/2)])

        # generate an LFO sin control signal - 1 cycle per xfadeFrames
        T = 1.0 / framesPerSec    # sample period
        LFO1_T = 3 * xfadeFrames * T
        LFO2_T = 2 * xfadeFrames * T
        # create composite sin source
        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        x = x[0:len(x)-1]
        LFO1AMP = SzY/6
        LFO2AMP = SzY/5
        LFO1 = LFO1AMP*np.sin(LFO1_T * 2.0*np.pi * x)
        LFO2 = LFO2AMP*np.sin(LFO2_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = Image.open(imgFileList[round(numImg*random.random()) % numImg])

                
            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            #imgBpTscOut = imgClone1.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY


            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                    
                    #pdb.set_trace()

                    focalMod[0] = focal1[0] + LFO1[t]
                    focalMod[1] = focal1[1] + LFO2[t]

                    #print('LFO of t = '+str(int(LFO[t])))
                    hop_sz_mod = LFO1[t] * hop_sz

                    if newDimX > hop_sz_mod:
                        newDimX -= 2*hop_sz
                        if newDimX < 2:
                            newDimX = 2
                        #newDimX -= hop_sz_mod
                        newDimX = int(newDimX)
                    if newDimY > hop_sz_mod:
                        newDimY -= 2*hop_sz
                        if newDimY < 2:
                            newDimY = 2
                        #newDimY -= hop_sz_mod
                        newDimY = int(newDimY)
                           
                    #print('*****LFO[t] = '+str(LFO[t])+', hop_sz_mod = '+str(hop_sz_mod)+', newDimX = '+str(newDimX)+', newDimY = '+str(newDimY))
                        
                    # scale image to new dimensions
                    imgClone3 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                    #imgClone3 = imgBpTscOut
                    imgItr1 = imgClone3.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr2 = imgClone2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    
                    
                    # calculate box = tuple
                    newXYbox1 = ( int(focalMod[0] - newDimX/2), int(focalMod[1] - newDimY/2) )
                    imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                    imgBpTsc2.paste(imgItr2, box=newXYbox1, mask=None)


                    imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                    imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # rewrite inOrOut as bipolar toggle switch in loop above
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            zr += '0'
                        strInc = zr+str(numFrames - (nextInc))
                    imgLfoParascopeFull = imgOutDir+imgLfoParascopeNm+strInc+'.jpg'
                    imgBpTscOut.save(imgLfoParascopeFull)
                    
                    frameCnt += 1
    
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYEu - Masked LFO Parascope telescope img f::---*
    # // *--------------------------------------------------------------* //
    
    def xodMskLfoParascope(self, imgFileList, xLength, framesPerSec, xfadeFrames, 
                           lfoDepth, n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' xodMskLfoParascope function '''
    
        if imgOutNm != 'None':
            imgMskLfoParascopeNm = imgOutNm
        else:
            imgMskLfoParascopeNm = 'imgMskLfoParascope'
            
        if lfoDepth > 100:
            print('WARNING - lfoDepth out of bounds, setting to max = 100')
            lfoDepth = 100
    
        #imgObjTemp1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
        imgBpTscOut = Image.open(imgFileList[0])

        SzX = imgBpTscOut.width
        SzY = imgBpTscOut.height
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgFileList)
    
        nextInc = 0
        # example internal control signal 
        #hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
        hop_sz = SzY/42
        
        alphaX = np.linspace(0.3, 0.7, xfadeFrames)

        focal1 = (int(SzX/2), int(SzY/2))
        focalMod = np.array([int(SzX/2), int(SzY/2)])

        # generate an LFO sin control signal - 1 cycle per xfadeFrames
        T = 1.0 / framesPerSec    # sample period
        LFO1_T = 3 * xfadeFrames * T
        LFO2_T = 2 * xfadeFrames * T
        # create composite sin source
        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        x = x[0:len(x)-1]
        LFO1AMP = lfoDepth*(SzY/600)
        LFO2AMP = lfoDepth*(SzY/500)
        LFO1 = LFO1AMP*np.sin(LFO1_T * 2.0*np.pi * x)
        LFO2 = LFO2AMP*np.sin(LFO2_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = Image.open(imgFileList[round(numImg*random.random()) % numImg])

                
            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            #imgBpTscOut = imgClone1.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY


            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                    
                    #pdb.set_trace()

                    focalMod[0] = focal1[0] + LFO1[t]
                    focalMod[1] = focal1[1] + LFO2[t]

                    #print('LFO of t = '+str(int(LFO[t])))
                    hop_sz_mod = LFO1[t] * hop_sz

                    if newDimX > hop_sz_mod:
                        newDimX -= 2*hop_sz
                        if newDimX < 2:
                            newDimX = 2
                        #newDimX -= hop_sz_mod
                        newDimX = int(newDimX)
                    if newDimY > hop_sz_mod:
                        newDimY -= 2*hop_sz
                        if newDimY < 2:
                            newDimY = 2
                        #newDimY -= hop_sz_mod
                        newDimY = int(newDimY)
                           
                    #print('*****LFO[t] = '+str(LFO[t])+', hop_sz_mod = '+str(hop_sz_mod)+', newDimX = '+str(newDimX)+', newDimY = '+str(newDimY))
                        
                    # scale image to new dimensions
                    imgClone3 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                    imgClone4 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                    
                    
                    #imgClone3 = imgBpTscOut
                    imgItr1 = imgClone3.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr2 = imgClone2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgMsk2 = imgClone4.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    
                    #pdb.set_trace()
                    
                    imgMsk = imgMsk2.convert("L")
                    
                    # calculate box = tuple
                    newXYbox1 = ( int(focalMod[0] - newDimX/2), int(focalMod[1] - newDimY/2) )
                    imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=imgMsk)
                    imgBpTsc2.paste(imgItr2, box=newXYbox1, mask=imgMsk)
                    

                    imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                    imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=1)

                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
    
                    # rewrite inOrOut as bipolar toggle switch in loop above
                    if inOrOut == 1:
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            zr += '0'
                        strInc = zr+str(numFrames - (nextInc))
                    imgMskLfoParascopeFull = imgOutDir+imgMskLfoParascopeNm+strInc+'.jpg'
                    imgBpTscOut.save(imgMskLfoParascopeFull)
                    
                    frameCnt += 1
    
        return

    # // *--------------------------------------------------------------* //
    # // *---::XODMKEYEu - Dual Channel Masked Telescope img f::---*
    # // *--------------------------------------------------------------* //
    
    def xodMskDualESP(self, imgFileList, mskFileList, xLength, framesPerSec, xfadeFrames, 
                      n_digits, imgOutDir, imgOutNm='None', effx=0, inOrOut=0):
        ''' xodMskDualESP function 
            effx = 0 -> full frame fade
            effx = 1 -> telescope fades 
            effx = 2 -> heavy telescope fades
            effx = 3 -> maddog telescope fades
            effx = 4 -> random switch between 0 - 3 per xFade
        '''
    
        if imgOutNm != 'None':
            xodMskDualESPNm = imgOutNm
        else:
            xodMskDualESPNm = 'imgMskLfoParascope'
            

        numImg = len(imgFileList)
        numMsk = len(mskFileList)

        #pdb.set_trace()
            
        imgBpTscOut = Image.open(imgFileList[round(numImg*random.random()) % numImg])
        #imgBpTscAlt = Image.open(imgFileList[round(numImg*random.random()) % numImg])
        imgBpTscAlt = Image.open(mskFileList[round(numImg * random.random()) % numMsk])


        if effx > 2:
            imgBpTscX   = Image.open(imgFileList[round(numImg*random.random()) % numImg])
        

        SzX = imgBpTscOut.width
        SzY = imgBpTscOut.height
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')

        
        alphaX = np.linspace(0.2, 0.8, xfadeFrames)

        focal = np.array([int(SzX/2), int(SzY/2)])

        # generate an LFO sin control signal - 1 cycle per xfadeFrames
        # T = 1.0 / framesPerSec    # sample period
        # LFO1_T = 3 * xfadeFrames * T
        # x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        # x = x[0:len(x)-1]
        # LFO1AMP = 2
        # LFO1 = LFO1AMP*np.sin(LFO1_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):
            
            if inOrOut == 0:        # fade out fx
                inOut = 0
            elif inOrOut == 1:      # fade in fx
                inOut = 1
            else:
                inOut = round(random.random())
                
            if effx > 3:
                fx = round(3*random.random())
            else:
                fx = effx

            imgMsk1 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk1 = imgMsk1.convert("L")
            imgMsk2 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
            imgMsk2 = imgMsk2.convert("L")

            imgClone1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            if fx == 0:
                imgClone3 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                imgClone4 = imgBpTscAlt
            elif fx == 1:
                imgClone3 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                imgClone4 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            elif fx == 2:
                imgClone3 = imgBpTscOut
                imgClone4 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                imgMsk3 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
                imgMsk3 = imgMsk3.convert("L")
            else:
                imgClone3 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                imgClone4 = imgBpTscAlt
                imgClone5 = imgBpTscOut
                imgMsk3 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
                imgMsk3 = imgMsk3.convert("L")
                imgMsk4 = Image.open(mskFileList[round(numMsk*random.random()) % numMsk])
                imgMsk4 = imgMsk4.convert("L")

            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            imgBpTsc3 = imgClone3.copy()
            imgBpTsc4 = imgClone4.copy()
            if fx > 2:
                imgBpTsc5 = imgClone5.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            if fx > 1:
                newDimX2 = SzX
                newDimY2 = SzY
            if fx > 2:
                newDimX3 = SzX
                newDimY3 = SzY
            
            # Set size of iteration subframe resize
            if fx == 0:
                hop_sz = 0
            elif effx == 1:
                hopScl = 0.1 + 6 * random.random()
                hop_sz = np.ceil(SzX / (hopScl * xfadeFrames))
            elif fx == 2:
                hopScl = 0.1 + 3 * random.random()
                hop_sz = np.ceil(SzX / (hopScl * xfadeFrames))
                hopScl2 = 0.1 + 3 * random.random()
                hop_sz2 = np.ceil(SzX / (hopScl2 * xfadeFrames))
            else:
                if int(random.random()):
                    hopScl = 0.1 + 3 * random.random()
                    hop_sz = np.ceil(SzX / (hopScl * xfadeFrames))
                else:
                    hop_sz = 0
                hopScl2 = 0.1 + 5 * random.random()
                hop_sz2 = np.ceil(SzX / (hopScl2 * xfadeFrames))
                hopScl3 = 0.1 + 9 * random.random()
                hop_sz3 = np.ceil(SzX / (hopScl3 * xfadeFrames))
                                 

            # handles final xfade 
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xfadeFrames
            curInc = frameCnt

            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length

                    if newDimX > hop_sz:
                        newDimX -= hop_sz
                        if newDimX < 2:
                            newDimX = 2
                        newDimX = int(newDimX)
                    if newDimY > hop_sz:
                        newDimY -= hop_sz
                        if newDimY < 2:
                            newDimY = 2
                        newDimY = int(newDimY)

                    if fx > 1:
                        if newDimX2 > hop_sz2:
                            newDimX2 -= hop_sz2
                            if newDimX2 < 2:
                                newDimX2 = 2
                            newDimX2 = int(newDimX2)
                        if newDimY2 > hop_sz2:
                            newDimY2 -= hop_sz2
                            if newDimY2 < 2:
                                newDimY2 = 2
                            newDimY2 = int(newDimY2)
                            
                    if fx > 2:
                        if newDimX3 > hop_sz3:
                            newDimX3 -= hop_sz3
                            if newDimX3 < 2:
                                newDimX3 = 2
                            newDimX3 = int(newDimX3)
                        if newDimY3 > hop_sz3:
                            newDimY3 -= hop_sz3
                            if newDimY3 < 2:
                                newDimY3 = 2
                            newDimY3 = int(newDimY3)

                        
                    # scale image to new dimensions
                    if fx == 0:
                        newXYbox0 = ( int(focal[0] - SzX/2), int(focal[1] - SzY/2) )
                        imgBpTsc1.paste(imgClone1, box=newXYbox0, mask=imgMsk1)
                        imgBpTsc2.paste(imgClone4, box=newXYbox0, mask=imgMsk2)
                        imgBpTsc3.paste(imgClone4, box=newXYbox0)
                        imgBpTsc4.paste(imgClone3, box=newXYbox0)
                    elif fx == 1:
                        imgItr1 = imgClone1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgItr2 = imgClone2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgItr3 = imgClone3.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgItr4 = imgClone4.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        newXYbox0 = ( int(focal[0] - newDimX/2), int(focal[1] - newDimY/2) )
                        imgMsk3 = imgMsk2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgBpTsc1.paste(imgItr2, box=newXYbox0, mask=imgMsk3)
                        imgBpTsc2.paste(imgItr1, box=newXYbox0, mask=imgMsk3)
                        imgBpTsc3.paste(imgClone4, box=newXYbox0)
                        imgBpTsc4.paste(imgClone3, box=newXYbox0)
                    elif fx == 2:
                        imgItr1 = imgClone1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgItr2 = imgClone2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgClone3 = imgBpTscOut.copy()
                        imgItr3 = imgClone3.resize((newDimX2, newDimY2), resample=Image.BICUBIC)
                        imgItr4 = imgClone4.resize((newDimX2, newDimY2), resample=Image.BICUBIC)
                        newXYbox0 = ( int(focal[0] - newDimX/2), int(focal[1] - newDimY/2) )
                        newXYbox1 = ( int(focal[0] - newDimX2/2), int(focal[1] - newDimY2/2) )
                        imgMsk3 = imgMsk2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgMsk4 = imgMsk3.resize((newDimX2, newDimY2), resample=Image.BICUBIC)
                        imgBpTsc1.paste(imgItr2, box=newXYbox0, mask=imgMsk3)
                        imgBpTsc2.paste(imgItr1, box=newXYbox0, mask=imgMsk3)
                        imgBpTsc3.paste(imgItr3, box=newXYbox1, mask=imgMsk4)
                        imgBpTsc4.paste(imgItr4, box=newXYbox1, mask=imgMsk4)
                    else:
                        imgItr1 = imgClone1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgItr2 = imgClone2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgItr3 = imgClone4.resize((newDimX2, newDimY2), resample=Image.BICUBIC)
                        imgItr4 = imgClone3.resize((newDimX2, newDimY2), resample=Image.BICUBIC)
                        imgItr5 = imgClone5.resize((newDimX3, newDimY3), resample=Image.BICUBIC)
                        newXYbox0 = ( int(focal[0] - newDimX/2), int(focal[1] - newDimY/2) )
                        newXYbox1 = ( int(focal[0] - newDimX2/2), int(focal[1] - newDimY2/2) )
                        newXYbox2 = ( int(focal[0] - newDimX3/2), int(focal[1] - newDimY2/2) )
                        imgMsk3 = imgMsk1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                        imgMsk4 = imgMsk2.resize((newDimX2, newDimY2), resample=Image.BICUBIC)
                        imgMsk5 = imgMsk3.resize((newDimX3, newDimY3), resample=Image.BICUBIC)
                        imgBpTsc1.paste(imgItr2, box=newXYbox0, mask=imgMsk3)
                        imgBpTsc2.paste(imgItr1, box=newXYbox0, mask=imgMsk3)
                        imgBpTsc3.paste(imgItr3, box=newXYbox1, mask=imgMsk4)
                        imgBpTsc4.paste(imgItr4, box=newXYbox1, mask=imgMsk4)
                        imgBpTsc5.paste(imgItr5, box=newXYbox2, mask=imgMsk5)


                    # output base image
                    outXYbox = ( int(focal[0] - SzX/2), int(focal[1] - SzY/2) )
                    imgBpTscOut = Image.blend(imgBpTsc1, imgBpTsc2, alphaX[t])
                    imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=1)
                    imgBpTscAlt = Image.blend(imgBpTsc3, imgBpTsc4, alphaX[t])
                    imgBpTscAlt = ImageOps.autocontrast(imgBpTscAlt, cutoff=1)
                    if fx > 2:
                        imgBpTscX = Image.blend(imgBpTsc5, imgBpTsc1, alphaX[t])
                        imgBpTscX = ImageOps.autocontrast(imgBpTscX, cutoff=1)
                        imgBpTscAlt.paste(imgBpTscX, box=outXYbox, mask=imgMsk1)
                    imgBpTscOut.paste(imgBpTscAlt, box=outXYbox, mask=imgMsk1)

                    # update name counter & concat with base img name
                    # inOrOut controls direction of parascope func
                    zr = ''
                    if inOut == 1:
                        for j in range(n_digits - len(str(frameCnt))):
                            zr += '0'
                        strInc = zr+str(frameCnt)
                    else:
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    xodMskDualESPFull = imgOutDir+xodMskDualESPNm+strInc+'.jpg'
                    imgBpTscOut.save(xodMskDualESPFull)
                    
                    xCnt -= 1
                    frameCnt += 1                    
    
        return


    
    # /////////////////////////////////////////////////////////////////////////
    # #########################################################################
    # end : function definitions
    # #########################################################################
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# // *---------------------------------------------------------------------* //


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# Notes:
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# ***
# convert from Image image to Numpy array:
# arr = array(img)

# convert from Numpy array to Image image:
# img = Image.fromarray(array)





# #########################################################################
# Tools
# #########################################################################



## // *---------------------------------------------------------------------* //
## // *---Plotting---*
## // *---------------------------------------------------------------------* //
#
## define a sub-range for wave plot visibility
#tLen = 50
#
#fnum = 1
#pltTitle = 'Input Signal y1 (first '+str(tLen)+' samples)'
#pltXlabel = 'y1: '+str(testFreq1)+' Hz'
#pltYlabel = 'Magnitude'
#
#
#sig = y1[0:tLen]
## define a linear space from 0 to 1/2 Fs for x-axis:
#xaxis = np.linspace(0, tLen, tLen)
#
#
#odmkplt.odmkPlot1D(fnum, sig, xaxis, pltTitle, pltXlabel, pltYlabel)
#
#
#fnum = 2
#pltTitle = 'FFT Mag: y1_FFTscale '+str(testFreq1)+' Hz'
#pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
#pltYlabel = 'Magnitude (scaled by 2/N)'
#
## sig <= direct
#
## define a linear space from 0 to 1/2 Fs for x-axis:
#xfnyq = np.linspace(0.0, 1.0/(2.0*T), N/2)
#
#odmkplt.odmkPlot1D(fnum, y1_FFTscale, xfnyq, pltTitle, pltXlabel, pltYlabel)
#
#
#
## // *---------------------------------------------------------------------* //
## // *---Multi Plot - source signal array vs. FFT MAG out array---*
## // *---------------------------------------------------------------------* //
#
#fnum = 3
#pltTitle = 'Input Signals: sinArray (first '+str(tLen)+' samples)'
#pltXlabel = 'sinArray time-domain wav'
#pltYlabel = 'Magnitude'
#
## define a linear space from 0 to 1/2 Fs for x-axis:
#xaxis = np.linspace(0, tLen, tLen)
#
#odmkplt.odmkMultiPlot1D(fnum, sinArray, xaxis, pltTitle, pltXlabel, pltYlabel, colorMp='hsv')
#
#
#fnum = 4
#pltTitle = 'FFT Mag: yScaleArray multi-osc '
#pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
#pltYlabel = 'Magnitude (scaled by 2/N)'
#
## define a linear space from 0 to 1/2 Fs for x-axis:
#xfnyq = np.linspace(0.0, 1.0/(2.0*T), N/2)
#
#odmkplt.odmkMultiPlot1D(fnum, yScaleArray, xfnyq, pltTitle, pltXlabel, pltYlabel, colorMp='hsv')
