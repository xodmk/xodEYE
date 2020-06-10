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

import os, sys
import glob, shutil
from math import atan2, floor, ceil
import random
import numpy as np
#import scipy as sp
#from scipy.signal import convolve2d
import imageio as imio
from scipy import ndimage
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance


rootDir = '../'

sys.path.insert(0, rootDir+'eye')
import xodEYEutil as eyeutil

sys.path.insert(1, rootDir+'DSP')
import xodClocks as clks

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
        
        self.goldratio = 1.6180339887
        self.goldratioinv = 0.618033988768953

        
        # // *-------------------------------------------------------------* //
        # // *---::Set Master Dimensions::---* //
        self.mstrSzX = SzX
        self.mstrSzY = SzY        

        # // *-------------------------------------------------------------* //
        # // Instantiate clocking/sequencing object::-*')
        
        self.eyeClks = clks.xodClocks(self.xLength, self.fs, self.bpm, self.framesPerSec)
        
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
    # // *---::ODMKEYE - repeat list of files in directory n times::---*
    # // *--------------------------------------------------------------* //
    
    def repeatAllImg(self, srcDir, n, w=0, repeatDir='None', repeatName='None'):
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
    
        [imgObjList, imgSrcList] = self.importAllJpg(srcDir)
    
        if repeatName != 'None':
            reName = repeatName
        else:
            reName = 'imgRepeat'

        imgCount = len(imgObjList) * n
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(n):
            for j in range(len(imgObjList)):
                nextInc += 1
                zr = ''
                for h in range(n_digits - len(str(nextInc))):
                    zr += '0'
                strInc = zr+str(nextInc)
                imgRepeatNm = reName+strInc+'.jpg'
  
                imgRepeatNmFull = repeatDir+imgRepeatNm
                imio.imwrite(imgRepeatNmFull, imgObjList[j])
    
        return
        
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - concat all files in directory list::---*
    # // *--------------------------------------------------------------* //


    def concatAllDir(self, dirList, concatDir, reName):
        ''' Takes a list of directories containing .jpg /.bmp images,
            renames and concatenates all files into new arrays.
            The new file names are formatted for processing with ffmpeg
            if w = 1, write files into output directory.
            if concatDir specified, change output dir name.
            if concatName specified, change output file names'''


#        imgFileList = []
#        for i in range(len(dirList)):
#            if self.imgFormat=='fjpg':
#                imgFileList.extend(sorted(glob.glob(dirList[i]+'*.jpg')))                
#            elif self.imgFormat=='fbmp':
#                imgFileList.extend(sorted(glob.glob(dirList[i]+'*.bmp')))
                
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

            if self.imgFormat=='fjpg':
                imgNormalizeNm = reName+strInc+'.jpg' 
            elif self.imgFormat=='fbmp':
                imgNormalizeNm = reName+strInc+'.bmp'

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
    # 21 => EYE Color Enhance Telescope Algorithm    ::odmkImgCEnTelescope::
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
    # // *---::XODMKEYE - Image Linear Select Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def xodImgLinSel(self, imgFileList, numFrames, imgOutDir, imgOutNm='None'):
    
        if imgOutNm != 'None':
            imgRndSelNm = imgOutNm
        else:
            imgRndSelNm = 'imgRndSelOut'
        
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 1
        for i in range(numFrames):
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgRndSelNm+strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            imgTmp = imio.imread(imgFileList[eyeutil.circ_idx(i, len(imgFileList))])
            imio.imwrite(imgRndSelFull, imgTmp)

            nextInc += 1
            
        return


    # // *--------------------------------------------------------------* //
    # // *---::XODMKEYE - Image Random Select Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def xodImgRndSel(self, imgFileList, numFrames, imgOutDir, imgOutNm='None'):
    
        if imgOutNm != 'None':
            imgRndSelNm = imgOutNm
        else:
            imgRndSelNm = 'imgRndSelOut'
    
        # imgRndSelNmArray = []
        # imgRndSelArray = []
        
        rIdxArray = eyeutil.randomIdxArray(numFrames, len(imgFileList))
        
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        for i in range(numFrames):
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgRndSelNm+strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            imio.imwrite(imgRndSelFull, imgFileList[rIdxArray[i]])

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
        
    def odmkImgXfade(self, imgList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of images fading from img1 -> img2 for xLength seconds
            Linearly alpha-blends images using PIL Image.blend
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgXfadeNm = imgOutNm
        else:
            imgXfadeNm = 'ImgXfade'
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xfadeFrames = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgList)
        numxfadeImg = numImg * xfadeFrames
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)

    
        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades - 1):
            if frameCnt <= numFrames:
                if (frameCnt % numxfadeImg) == 0:
                    xfdirection = -xfdirection
                if xfdirection == 1:
                    imgPIL1 = Image.fromarray(imgList[j % (numImg-1)])
                    imgPIL2 = Image.fromarray(imgList[(j % (numImg-1)) + 1])
                else:
                    imgPIL1 = Image.fromarray(imgList[(numImg-2) - (j % numImg) + 1])
                    imgPIL2 = Image.fromarray(imgList[(numImg-2) - (j % numImg)])
                for i in range(xfadeFrames):
                    alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    imgXfadeFull = imgOutDir+imgXfadeNm+strInc+'.jpg'
                    imio.imwrite(imgXfadeFull, alphaB)
                    frameCnt += 1
    
        return
        
        
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image CrossFade Sequence Algorithm::---*')
    # // *--------------------------------------------------------------* //    
        
    def odmkImgXfadeAll(self, imgList, xfadeFrames, imgOutDir, imgOutNm='None'):
        ''' outputs a sequence of images fading from img1 -> img2
            for all images in src directory. 
            The final total frame count is determined by #src images * xfadeFrames (?check?)
            Linearly alpha-blends images using PIL Image.blend
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgXfadeNm = imgOutNm
        else:
            imgXfadeNm = 'imgRotateSeqOut'
    
        numImg = len(imgList)
        imgCount = xfadeFrames * (numImg - 1)
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 0
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)

    
        for j in range(numImg - 1):
            imgPIL1 = Image.fromarray(imgList[j])
            imgPIL2 = Image.fromarray(imgList[j + 1])
            for i in range(xfadeFrames):
                alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
                nextInc += 1
                zr = ''
                for j in range(n_digits - len(str(nextInc))):
                    zr += '0'
                strInc = zr+str(nextInc)
                imgXfadeFull = imgOutDir+imgXfadeNm+strInc+'.jpg'
                imio.imwrite(imgXfadeFull, alphaB)
  
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
    # // *---::ODMKEYE - Image CrossFade Rotate Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgXfadeRot(self, imgList, sLength, framesPerSec, xFrames, imgOutDir, imgOutNm='None', rotDirection=0):
        ''' outputs a sequence of images fading from img1 -> img2
            Linearly alpha-blends images using PIL Image.blend
            imgList: python list of img objects
            sLength the lenth of output sequence (total number of frames)
            framesPerSec: video frames per second
            xFrames: number of frames for each cross-fade (framesPer(beat/sec))
            imgOutDir: output directory path/name
            rotation direction: 0=counterclockwise ; 1=clockwise
            assume images in imgList are numpy arrays '''
    
        if imgOutNm != 'None':
            imgXfadeRotNm = imgOutNm
        else:
            imgXfadeRotNm = 'imgXfadeRot'


        zn = eyeutil.cyclicZn(xFrames-1)    # less one, then repeat zn[0] for full 360
    
        numFrames = int(ceil(sLength * framesPerSec))
        numXfades = int(ceil(numFrames / xFrames))
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xFrames = '+str(xFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgList)
        numxfadeImg = numImg * xFrames
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        alphaX = np.linspace(0.0, 1.0, xFrames)
    
    
        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades - 1):
            if frameCnt <= numFrames:
                if (frameCnt % numxfadeImg) == 0:
                    xfdirection = -xfdirection
                if xfdirection == 1:
                    imgPIL1 = Image.fromarray(imgList[j % (numImg-1)])
                    imgPIL2 = Image.fromarray(imgList[(j % (numImg-1)) + 1])
                else:
                    imgPIL1 = Image.fromarray(imgList[(numImg-2) - (j % numImg) + 1])
                    imgPIL2 = Image.fromarray(imgList[(numImg-2) - (j % numImg)])
                for i in range(xFrames):
                    alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
                    ang = (atan2(zn[i % (xFrames-1)].imag, zn[i % (xFrames-1)].real))*180/np.pi
                    if rotDirection == 1:
                        ang = -ang
                    rotate_alphaB = ndimage.rotate(alphaB, ang, reshape=False)
                    rotate_alphaZ = self.cropZoom(rotate_alphaB, 2)

        
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    imgXfadeRotFull = imgOutDir+imgXfadeRotNm+strInc+'.jpg'
                    imio.imwrite(imgXfadeRotFull, rotate_alphaZ)
                    frameCnt += 1
    
        return
      

    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image CrossFade Rotate Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgXfadeShift(self, imgList, sLength, framesPerSec, xFrames, imgOutDir, imgOutNm='None', rotDirection=0):
        ''' outputs a sequence of images fading from img1 -> img2
            Linearly alpha-blends images using PIL Image.blend
            imgList: python list of img objects
            sLength the lenth of output sequence (total number of frames)
            framesPerSec: video frames per second
            xFrames: number of frames for each cross-fade (framesPer(beat/sec))
            imgOutDir: output directory path/name
            rotation direction: 0=counterclockwise ; 1=clockwise
            assume images in imgList are numpy arrays '''
    
        if imgOutNm != 'None':
            imgXfadeRotNm = imgOutNm
        else:
            imgXfadeRotNm = 'imgXfadeRot'
    
        zn = eyeutil.cyclicZn(xFrames-1)    # less one, then repeat zn[0] for full 360
    
        numFrames = int(ceil(sLength * framesPerSec))
        numXfades = int(ceil(numFrames / xFrames))
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xFrames = '+str(xFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgList)
        numxfadeImg = numImg * xFrames
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        alphaX = np.linspace(0.0, 1.0, xFrames)
    
        # imgXfadeRotNmArray = []
        # imgXfadeRotArray = []
    
        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades - 1):
            if frameCnt <= numFrames:
                if (frameCnt % numxfadeImg) == 0:
                    xfdirection = -xfdirection
                if xfdirection == 1:
                    imgPIL1 = Image.fromarray(imgList[j % (numImg-1)])
                    imgPIL2 = Image.fromarray(imgList[(j % (numImg-1)) + 1])
                else:
                    imgPIL1 = Image.fromarray(imgList[(numImg-2) - (j % numImg) + 1])
                    imgPIL2 = Image.fromarray(imgList[(numImg-2) - (j % numImg)])
                for i in range(xFrames):
                    alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
                    ang = (atan2(zn[i % (xFrames-1)].imag, zn[i % (xFrames-1)].real))*180/np.pi
                    if rotDirection == 1:
                        ang = -ang
                    rotate_alphaB = ndimage.rotate(alphaB, ang, reshape=False)
        
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    imgXfadeRotFull = imgOutDir+imgXfadeRotNm+strInc+'.jpg'
                    imio.imwrite(imgXfadeRotFull, rotate_alphaB)
                    # imgXfadeRotNmArray.append(imgXfadeRotFull)
                    # imgXfadeRotArray.append(alphaB)
                    frameCnt += 1
    
        # return [imgXfadeRotArray, imgXfadeRotNmArray]
        return      
      
      
      
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Telescope Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgTelescope(self, imgList, xLength, framesPerSec, framesPerBeat, imgOutDir, imgOutNm='None', inOrOut=0):
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
    # // *---::ODMKEYE - Img Xfade Telescope Sequence Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgXfadeTelescope(self, imgList, framesPerBeat, imgOutDir, inOut=0, imgOutNm='None'):
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
    
        alphaX = np.linspace(0.0, 1.0, framesPerBeat)               
    
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
                imgItr1 = Image.fromarray(self.odmkEyeRescale(imgClone1, newDimX, newDimY))
                imgItr2 = Image.fromarray(self.odmkEyeRescale(imgClone2, newDimX, newDimY))
                alphaB = Image.blend(imgItr1, imgItr2, alphaX[t])
                alphaX = np.array(alphaB)
                # region = (left, upper, right, lower)
                # subbox = (i + 1, i + 1, newDimX, newDimY)
                for j in range(SzY):
                    for k in range(SzX):
                        #if ((j >= (t+1)*hop_sz) and (j < (newDimY+(SzY-newDimY)/2)) and (k >= (t+1)*hop_sz) and (k < (newDimX+(SzX-newDimX)/2))):
                        if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
                            #imgClone[j+(SzY-newDimY)/2, k+(SzX-newDimX)/2, :] = imgItr[j - t, k - t, :]
                            imgClone1[j, k, :] = alphaX[j - (SzY-newDimY)/2, k - (SzX-newDimX)/2, :]
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
    # // *---::ODMKEYE - Image Color Enhance::---*')
    # // *--------------------------------------------------------------* //    
        
    def odmkImgCEnTelescope(self, imgList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOut=0):
        ''' outputs a sequence of images fading from img1 -> img2 for xLength seconds
            Linearly alpha-blends images using PIL Image.blend
            assume images in imgList are numpy arrays'''
    
        if imgOutNm != 'None':
            imgCEnTelescopeNm = imgOutNm
        else:
            imgCEnTelescopeNm = 'ImgXfade'
    
        # initialize SzX, SzY to dimensions of src img
        SzX = imgList[0].shape[1]
        SzY = imgList[0].shape[0]
    
        numFrames = int(ceil(xLength * framesPerSec))
        numBeats = int(ceil(numFrames / xfadeFrames))         
    
        #hop_sz = 4*ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
        #hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
        hop_sz = 1
    
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---xfadeFrames = '+str(xfadeFrames)+'---*')
        print('// *---numBeats = '+str(numBeats)+'---*')    
    
        # find number of source images in src dir
        numSrcImg = len(imgList)
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        factorX = np.linspace(0.1, 2.0, xfadeFrames)
    
        #imgcEnhancerNmArray = []
        #imgcEnhancerArray = []
    
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        for i in range(numBeats):
            newDimX = SzX
            newDimY = SzY
            imgClone = imgList[i%numSrcImg]    # mod to rotate through src img
            for t in range(xfadeFrames):
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
                    if inOut == 1:
                        imgCloneCEn = Image.fromarray(imgClone)
                        cEnhancer = ImageEnhance.Color(imgCloneCEn)           
                        imgCloneCEn = cEnhancer.enhance(factorX[t])
                        imgCloneCEn = np.array(imgCloneCEn)
                        for j in range(n_digits - len(str(nextInc))):
                            zr += '0'
                        strInc = zr+str(nextInc)
                    else:
                        imgCloneCEn = Image.fromarray(imgClone)
                        cEnhancer = ImageEnhance.Color(imgCloneCEn)           
                        imgCloneCEn = cEnhancer.enhance(factorX[(xfadeFrames-1)-t])
                        imgCloneCEn = np.array(imgCloneCEn)                    
                        for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            zr += '0'
                        strInc = zr+str(numFrames - (nextInc))
                    imgTelescFull = imgOutDir+imgCEnTelescopeNm+strInc+'.jpg'
                    imio.imwrite(imgTelescFull, imgCloneCEn)
                else:
                    break
                
        return
    
    # convert from Image image to Numpy array:
    # arr = np.array(img)
    
    # convert from Numpy array to Image image:
    # img = Image.fromarray(array)
    
    
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

    #def odmkPxlRndReplace(self, imgArray, sLength, framesPerSec, frameCtrl, imgOutDir, imgOutNm='None'):
    def odmkPxlRndRotate(self, imgArray, sLength, framesPerSec, framesPerBeat, imgOutDir, imgOutNm='None'):
        ''' swap n pixels per frame from consecutive images'''
    
        if imgOutNm != 'None':
            pxlRndReplaceNm = imgOutNm
        else:
            pxlRndReplaceNm = 'pxlRndReplace'
    
        SzX = imgArray[0].shape[1]
        SzY = imgArray[0].shape[0]
    
        numFrames = int(ceil(sLength * framesPerSec))

        framesPerBeat = int(2 * framesPerBeat)

        numBeats = int(ceil(numFrames / framesPerBeat))


        print('// *---numFrames = '+str(numFrames)+'---*')
        #print('// *---FrameCtrl = '+str(frameCtrl)+'---*')
        #print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgArray)
        #numxfadeImg = numImg * frameCtrl
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0

        eyeBase1 = Image.fromarray(imgArray[eyeutil.randomIdx(numImg)])
    
        #zn = eyeutil.cyclicZn(framesPerBeat-1)    # less one, then repeat zn[0] for full 360
        zn = eyeutil.cyclicZn(2*framesPerBeat)    # less one, then repeat zn[0] for full 360

        zoomScalarXArr = np.linspace(16, SzX//3, framesPerBeat) 
        zoomScalarYArr = np.linspace(9, SzY//3, framesPerBeat)
            
        alphaX = np.linspace(0.0001, 1.0, framesPerBeat)



        frameCnt = 0
        for j in range(numBeats - 1):
            
            imgZoom1 = Image.fromarray(imgArray[eyeutil.randomIdx(numImg)])
            imgZoom2 = Image.fromarray(imgArray[eyeutil.randomIdx(numImg)])
            zoomVertex1 = eyeutil.randomPxlLoc(SzX, SzY)
            rotDirection = round(random.random())
            
            if frameCnt <= numFrames:
                
                for i in range(framesPerBeat):

                    # background image base (pxlRndReplace)
                    #----------------------------------------------------------
                    
                    boxSzX = round(SzX*random.random()) + 16
                    boxSzY = round(SzY*random.random()) + 9                    
 
                    rndPxlLoc = eyeutil.randomPxlLoc(SzX, SzY)
                    alpha = random.random()

                    # imgPIL1 = Image.fromarray(imgArray[i % (numImg-1)])
                    imgPIL1 = Image.fromarray(imgArray[eyeutil.randomIdx(numImg)])
    
                    eyeBase1 = self.eyeBox1(eyeBase1, imgPIL1, boxSzX, boxSzY, rndPxlLoc, alpha)

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
                    
                    #pdb.set_trace()                  
                    
                    #eyeSub1 = imgZoom1.crop(boxZoom) 
                    #eyeSub2 = imgZoom2.crop(boxZoom)
                    eyeSub1 = imgZoom1.crop(subBox) 
                    eyeSub2 = imgZoom2.crop(subBox)

                    
                    alphaB = Image.blend(eyeSub1, eyeSub2, alphaX[i])
                    
                    alphaB = np.array(alphaB)
                    ang = (atan2(zn[i % (framesPerBeat-1)].imag, zn[i % (framesPerBeat-1)].real))*180/np.pi
                    if rotDirection == 1:
                        ang = -ang

                    rotate_alphaB = ndimage.rotate(alphaB, ang, reshape=False)

                    
                    rotate_alphaZ = self.cropZoom(rotate_alphaB, 2)
                    rotate_alphaZ = Image.fromarray(rotate_alphaZ)
                    

                    #----------------------------------------------------------
                    
                    eyeBase1.paste(rotate_alphaZ, boxZoom)


                    # update name counter & concat with base img name    
                    nextInc += 1
                    zr = ''
                    for j in range(n_digits - len(str(nextInc))):
                        zr += '0'
                    strInc = zr+str(nextInc)
                    pxlRndReplaceFull = imgOutDir+pxlRndReplaceNm+strInc+'.jpg'
                    
                    # write img to disk
                    imio.imwrite(pxlRndReplaceFull, eyeBase1)
            
                    frameCnt += 1
    
        return  
  
  
   
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE Dual Bipolar Oscillating telescope f::---*
    # // *--------------------------------------------------------------* //
    
    def odmkLfoParascope(self, imgArray, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' lfoParascope function '''
    
        if imgOutNm != 'None':
            imgLfoParascopeNm = imgOutNm
        else:
            imgLfoParascopeNm = 'imgLfoParascope'
    
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
        hop_sz = 1
        
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)
        imgRndIdxArray = eyeutil.randomIdxArray(numFrames, numImg)
   
        # imgDualBipolarTelescNmArray = []
        # imgDualBipolarTelescArray = []

        # generate an LFO sin control signal - 1 cycle per xfadeFrames
        T = 1.0 / framesPerSec    # sample period
        LFO_T = 8 * xfadeFrames * T
        # create composite sin source
        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        x = x[0:len(x)-1]
        LFOAMP = 200
        LFO = LFOAMP*np.sin(LFO_T * 2.0*np.pi * x)

        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades):
                                # random img grap from image Array

            if (frameCnt % numXfades) == 0:
                xfdirection = -xfdirection
            if xfdirection == 1:
                imgClone1 = imgArray[imgRndIdxArray[j]]
                imgClone2 = imgArray[imgRndIdxArray[j+1]]                
            else:
                imgClone1 = imgArray[imgRndIdxArray[(numImg-2) - j]]
                imgClone2 = imgArray[imgRndIdxArray[(numImg-2) - j+1]]
                
            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            imgBpTscOut = imgClone1.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
                              
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


            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length

                    print('LFO of t = '+str(int(LFO[t])))
                    hop_sz_mod = LFO[t] * hop_sz

                    if newDimX > hop_sz_mod:
                        #newDimX -= 2*hop_sz
                        newDimX -= hop_sz_mod
                        newDimX = int(newDimX)
                    if newDimY > hop_sz_mod:
                        #newDimY -= 2*hop_sz
                        newDimY -= hop_sz_mod
                        newDimY = int(newDimY)
                           
                    #print('*****LFO[t] = '+str(LFO[t])+', hop_sz_mod = '+str(hop_sz_mod)+', newDimX = '+str(newDimX)+', newDimY = '+str(newDimY))
                        
                    #pdb.set_trace()  
                        
                    # scale image to new dimensions
                    imgItr1 = self.odmkEyeRescale(imgClone1, newDimX, newDimY)
                    imgItr2 = self.odmkEyeRescale(imgClone2, newDimX, newDimY)                    

                    # region = (left, upper, right, lower)
                    # subbox = (i + 1, i + 1, newDimX, newDimY)
                    r = 0
                    for j in range(SzY):
                        s = 0
                        for k in range(SzX):
                            
                            # calculate bipolar subframes then interleave (out = priority)
                            # will require handling frame edges (no write out of frame)
                            # update index math to handle random focal points
                           
                            if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):
                                                                
                                #print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                                imgBpTsc1[j, k, :] = imgItr1[r, s, :]
                                imgBpTsc2[j, k, :] = imgItr2[r, s, :]
                                
                            if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                s += 1
                        if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                            r += 1                                

                    imgBpTscOut = Image.blend(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2), alphaX[t])
                    #imgBpTscOut = self.eyePhiFrame1(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2))
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
                    imio.imwrite(imgLfoParascopeFull, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)
                    
                    frameCnt += 1
    
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - LFO Parascope telescope II f::---*
    # // *--------------------------------------------------------------* //

    def odmkLfoParascopeII(self, imgFileList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' lfoParascope function '''
    
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
        # example internal control signal 
        #hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
        #hop_sz = 230
        
        #hop_szA = np.linspace(555, 2, xfadeFrames)
        #hop_szA = np.linspace(6, 196, xfadeFrames)
        
        
        alphaX = np.linspace(0.3, 0.7, xfadeFrames)



        # generate an LFO sin control signal - 1 cycle per xfadeFrames
        T = 1.0 / framesPerSec    # sample period
#        LFO_T = 8 * xfadeFrames * T
        # create composite sin source
        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        x = x[0:len(x)-1]
#        LFOAMP = 46
#        LFO = LFOAMP*np.sin(LFO_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):
            
            # random img grap from image Array
            #imgClone1 = imio.imread(imgFileList[j*xfadeFrames % numImg])
            #imgClone2 = imio.imread(imgFileList[(j*xfadeFrames+int(xfadeFrames/2)) % numImg])
            imgClone1 = imio.imread(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = imio.imread(imgFileList[round(numImg*random.random()) % numImg])

                
            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            imgBpTscOut = imgClone2.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            
            hopScl = round(70*random.random())
            #hop_szA = np.linspace(20*hopScl, 276*hopScl, xfadeFrames)
            hop_szA = np.linspace(330, 880, xfadeFrames)
                              
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
                    
                    newDimX -= hop_szA[t]
                    if newDimX < hopScl:
                        newDimX = hopScl
                    newDimX = int(newDimX)
                    
                    newDimY -= hop_szA[t]
                    if newDimY < hopScl:
                        newDimY = hopScl
                    newDimY = int(newDimY)

                        
                    # scale image to new dimensions
                    #imgItr1 = self.odmkEyeRescale(imio.imread(imgFileList[t*xfadeFrames % numImg]), newDimX, newDimY)
                    imgItr1 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                   
                    imgItr2 = self.odmkEyeRescale(imgBpTsc2, newDimX, newDimY)
                    
                    imgItr3 = self.odmkEyeRescale(imio.imread(imgFileList[round(numImg*random.random()) % numImg]), newDimX, newDimY)
                    
                    imgMix1 = Image.blend(Image.fromarray(imgItr1), Image.fromarray(imgItr3), 0.5)
                    imgMix1 = ImageOps.autocontrast(imgMix1, cutoff=0)
                    imgMix1 = np.array(imgMix1)
                    
                    imgMix2 = Image.blend(Image.fromarray(imgItr1), Image.fromarray(imgItr2), 0.5)
                    imgMix2 = ImageOps.autocontrast(imgMix2, cutoff=0)
                    imgMix2 = np.array(imgMix2)
                    
                    if (round(random.random())):
                        imgSub1 = imgMix1
                    else:
                        imgSub1 = imgItr1
                        
                    if (round(random.random())):
                        imgSub2 = imgMix2
                    else:
                        imgSub2 = imgItr3
                            
                    

                    # region = (left, upper, right, lower)
                    # subbox = (i + 1, i + 1, newDimX, newDimY)
                    r = 0
                    for j in range(SzY):
                        s = 0
                        for k in range(SzX):
                            
                            # calculate bipolar subframes then interleave (out = priority)
                            # will require handling frame edges (no write out of frame)
                            # update index math to handle random focal points
                           
                            if ( (j >= ((SzY-1)-newDimY)/2) and (j < ((SzY-1) - ((SzY-1)-newDimY)/2)) and (k >= ((SzX-1)-newDimX)/2) and (k < ((SzX-1) - ((SzX-1)-newDimX)/2)) ):
                                                                
                                #if (j==1058 or r==1058):
                                #    print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                                #    pdb.set_trace()                                                                
                                                                
                                imgBpTsc1[j, k, :] = imgSub1[r, s, :]
                                imgBpTsc2[j, k, :] = imgSub2[r, s, :]
                                
                            if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                s += 1
                        if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                            r += 1

                    imgBpTscOut = Image.blend(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2), alphaX[t])
                    #imgBpTscOut = self.eyePhiFrame1(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2))
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
                    imio.imwrite(imgLfoParascopeFull, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)
                    
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
    # // *---::ODMKEYE - EYE Bananasloth Recursion::---*
    # // *--------------------------------------------------------------* //
    
    def odmkBSlothGlitch2(self, imgArray, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0, indexOffset='None'):
        ''' BSlothGlitch2 function '''
    
        if imgOutNm != 'None':
            imgBSlothGlitch1Nm = imgOutNm
        else:
            imgBSlothGlitch1Nm = 'imgBSlothGlitch1'
    
        SzX = imgArray[0].shape[1]
        SzY = imgArray[0].shape[0]
    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        # finalXfade = int(floor(numFrames / xfadeFrames))
        if (numFrames % xfadeFrames) == 0:
            numFinalXfade = xfadeFrames
        else:
            numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// ****BSlothGlitch2 function*****')
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---Total number of frames = '+str(numFrames)+'---*')
        print('// *---number of img per xfade = '+str(xfadeFrames)+'---*')
        print('// *---number of xfades = '+str(numXfades)+'---*')
        print('// *---number of img for Final xfade = '+str(numFinalXfade)+'---*')
        print('\nProcessing ... ... ...\n\n')
        
        #pdb.set_trace()
    
        numImg = len(imgArray)
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        # example internal control signal 
        hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
    
        imgRndIdxArray = eyeutil.randomIdxArray(numFrames, numImg)   
   
   
        # imgBSlothRecursNmArray = []
        # imgBSlothRecursArray = []   
    
        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades):
                                # random img grap from image Array

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
#            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY))
#            if (focalRnd1[0] < SzX/2):
#                offsetX = -int(SzX/2 - focalRnd1[0])
#            else:
#                offsetX = int(focalRnd1[0] - SzX/2)
#            if (focalRnd1[1] < SzY/2):
#                offsetY = -int(SzY/2 - focalRnd1[1])
#            else:
#                offsetY = int(focalRnd1[1] - SzY/2)


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
                        imgItr1 = self.odmkEyeRescale(imgBpTsc2, newDimX, newDimY)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = ndimage.rotate(imgItr1, ang, reshape=False)
                            imgItr1 = self.cropZoom(imgItr1, 2)
                            #imgItr1 = Image.fromarray(imgItr1)
    
                        imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                        if rotateSubFrame2 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection2 == 1:
                                ang = -ang
                                
                            imgItr2 = ndimage.rotate(imgItr2, ang, reshape=False)
                            imgItr2 = self.cropZoom(imgItr2, 2)
                            #imgItr2 = Image.fromarray(imgItr2) 
                                        
                        # region = (left, upper, right, lower)
                        # subbox = (i + 1, i + 1, newDimX, newDimY)
                        r = 0
                        for j in range(SzY):
                            s = 0
                            for k in range(SzX):
                                
                                # calculate bipolar subframes then interleave (out = priority)
                                # will require handling frame edges (no write out of frame)
                                # update index math to handle random focal points
                               
                                if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):
                                                                    
                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                                    imgBpTsc1[j, k, :] = imgItr1[r, s, :]
                                    imgBpTsc2[j, k, :] = imgItr2[r, s, :]
                                    
                                if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                    s += 1
                            if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                                r += 1                
    
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
                            #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
        
                        # optional write to internal buffers
                        # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                        # imgDualBipolarTelescArray.append(imgBpTsc)
    
                        xCnt -= 1                    
                        frameCnt += 1
                        
                    # // END <if frameCnt < numFrames:    # process until end of total length>
                # // END <for t in range(xFrames):>
                # // END - xFade I

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
                        imgItr1 = self.odmkEyeRescale(imgBpTsc2, newDimX, newDimY)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = ndimage.rotate(imgItr1, ang, reshape=False)
                            imgItr1 = self.cropZoom(imgItr1, 2)
                            #imgItr1 = Image.fromarray(imgItr1)
    
                        imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                        if rotateSubFrame2 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection2 == 1:
                                ang = -ang
                                
                            imgItr2 = ndimage.rotate(imgItr2, ang, reshape=False)
                            imgItr2 = self.cropZoom(imgItr2, 2)
                            #imgItr2 = Image.fromarray(imgItr2) 
                                        
                        # region = (left, upper, right, lower)
                        # subbox = (i + 1, i + 1, newDimX, newDimY)
                        r = 0
                        for j in range(SzY):
                            s = 0
                            for k in range(SzX):
                                
                                # calculate bipolar subframes then interleave (out = priority)
                                # will require handling frame edges (no write out of frame)
                                # update index math to handle random focal points
                               
                                if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):
                                                                    
                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                                    imgBpTsc1[j, k, :] = imgItr1[r, s, :]
                                    imgBpTsc2[j, k, :] = imgItr2[r, s, :]
                                    
                                if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                    s += 1
                            if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                                r += 1                
    
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
                            #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
        
                        # optional write to internal buffers
                        # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                        # imgDualBipolarTelescArray.append(imgBpTsc)
    
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
    
    
                        r = 0
                        for j in range(SzY):
                            s = 0
                            for k in range(SzX):
                                
                                # calculate bipolar subframes then interleave (out = priority)
                                # will require handling frame edges (no write out of frame)
                                # update index math to handle random focal points
                               
                                if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):
                                                                    
                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                                    imgBpTsc1[j, k, :] = imgItr1[r, s, :]
                                    imgBpTsc2[j, k, :] = imgItr2[r, s, :]
                                    
                                if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                    s += 1
                            if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                                r += 1                
    
                        imgBpTscOut = Image.blend(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2), alphaX[t])
                        imgBpTscOut = ImageOps.autocontrast(imgBpTscOut, cutoff=0)    

    
    
#                        for j in range(SzY):
#                            for k in range(SzX):
#                                
#                                # calculate bipolar subframes then interleave (out = priority)
#                                # will require handling frame edges (no write out of frame)
#                                # update index math to handle random focal points
#                               
#                                if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):                                
#                                    
#                                    #imgBpTsc1[j, k, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
#                                    #imgBpTsc2[j, k, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
#    
#                                        
#                                    if ( (j+offsetY >= 0)  and (j+offsetY < SzY) and (k+offsetX >= 0)  and (k+offsetX < SzX) ):
#                                        #print('*****j = '+str(j)+'; k = '+str(k)+'; j+offsetY = '+str(j+offsetY)+'; k+offsetX = '+str(k+offsetX))
#                                        imgBpTsc1[j+offsetY, k+offsetX, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
#                                        imgBpTsc2[j+offsetY, k+offsetX, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]                                    
#                                        
#    
#                        imgBpTscOut = Image.blend(Image.fromarray(imgBpTsc1), Image.fromarray(imgBpTsc2), alphaX[t])
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
                            imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        else:
                            imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.bmp'                            
                        imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)

        
                        # optional write to internal buffers
                        # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                        # imgDualBipolarTelescArray.append(imgBpTsc)
                        
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
                        imgItr1 = self.odmkEyeRescale(imgBpTsc2, newDimX, newDimY)
                        if rotateSubFrame1 == 1:
                            
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection1 == 1:
                                ang = -ang
                                
                            imgItr1 = ndimage.rotate(imgItr1, ang, reshape=False)
                            imgItr1 = self.cropZoom(imgItr1, 2)
                            #imgItr1 = Image.fromarray(imgItr1)
    
                        imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                        if rotateSubFrame2 == 1:
                        
                            ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                            if rotDirection2 == 1:
                                ang = -ang
                                
                            imgItr2 = ndimage.rotate(imgItr2, ang, reshape=False)
                            imgItr2 = self.cropZoom(imgItr2, 2)
                            #imgItr2 = Image.fromarray(imgItr2)
                            
                        # image division blend algorithm..
                        c = imgItr1/((imgItr2.astype('float')+1)/(256*alphaX[t]))
                        # saturating function - if c[m,n] > 255, set to 255:
                        imgDIVB = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
                                        
                        # region = (left, upper, right, lower)
                        # subbox = (i + 1, i + 1, newDimX, newDimY)
                        r = 0
                        for j in range(SzY):
                            s = 0
                            for k in range(SzX):
                                
                                # calculate bipolar subframes then interleave (out = priority)
                                # will require handling frame edges (no write out of frame)
                                # update index math to handle random focal points
                               
                                if ( (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)) and (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)) ):
                                                                    
                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; r = '+str(r)+'; s = '+str(s))
                                    imgBpTsc1[j, k, :] = imgItr1[r, s, :]
                                    imgBpTsc2[j, k, :] = imgDIVB[r, s, :]
                                    
                                if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                    s += 1
                            if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                                r += 1                
    
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
                            #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                            for j in range(n_digits - len(str(curInc + xCnt))):
                                zr += '0'
                            strInc = zr+str(curInc + xCnt)
                        imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                        imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
        
                        # optional write to internal buffers
                        # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                        # imgDualBipolarTelescArray.append(imgBpTsc)
    
                        xCnt -= 1                    
                        frameCnt += 1
                        
                    # // END <if frameCnt < numFrames:    # process until end of total length>
                # // END <for t in range(xFrames):>
                # // END - xFade IV
                        
            # end xFadeSel FX selector
                    
                    
        print('\n// *---Final Frame Count = '+str(frameCnt)+'---*')
    
        return



    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - EYE Bananasloth Recursion::---*
    # // *--------------------------------------------------------------* //
    
    def odmkBSlothGlitch3(self, imgArray, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0, indexOffset='None'):
        ''' BSlothGlitch3 function '''
    
        if imgOutNm != 'None':
            imgBSlothGlitch3Nm = imgOutNm
        else:
            imgBSlothGlitch3Nm = 'imgBSlothGlitch3'
    
        SzX = imgArray[0].shape[1]
        SzY = imgArray[0].shape[0]
    
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
    
        numImg = len(imgArray)
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        # example internal control signal 
        hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
    
        imgRndIdxArray = eyeutil.randomIdxArray(numFrames, numImg)   
   
   
        # imgBSlothRecursNmArray = []
        # imgBSlothRecursArray = []   
    
        frameCnt = 0
        xfdirection = 1    # 1 = forward; -1 = backward
        for j in range(numXfades):
                                # random img grap from image Array

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
            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY))
            if (focalRnd1[0] < SzX/2):
                offsetX = -int(SzX/2 - focalRnd1[0])
            else:
                offsetX = int(focalRnd1[0] - SzX/2)
            if (focalRnd1[1] < SzY/2):
                offsetY = -int(SzY/2 - focalRnd1[1])
            else:
                offsetY = int(focalRnd1[1] - SzY/2)

            #print('focalRnd1 = ['+str(focalRnd1[0])+', '+str(focalRnd1[1])+']')
            #print('offsetX = '+str(offsetX))
            #print('offsetY = '+str(offsetY))

            # focalRnd2 = randomPxlLoc(SzX, SzY)

            rotateSubFrame1 = 0             # randomly set rotation on/off
            rotDirection1 = 0
            if (round(8*random.random()) > 5):
                rotateSubFrame1 = 1
                if (round(random.random())):
                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
            if (round(8*random.random()) > 2):
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
            
            for t in range(xFrames):
                if frameCnt < numFrames:    # process until end of total length

                    if newDimX > hop_sz:
                        newDimX -= 9*hop_sz
                        #newDimX -= hop_sz
                    if newDimY > hop_sz:
                        newDimY -= 7*hop_sz
                        #newDimY -= hop_sz
                        
                    # scale image to new dimensions
                    imgItr1 = self.odmkEyeRescale(imgBpTsc2, newDimX, newDimY)
                    imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                    if rotateSubFrame1 == 1:
                        
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        imgItr1 = ndimage.rotate(imgItr2, ang, reshape=False)
                        imgItr1 = self.cropZoom(imgItr1, 2)
                        #imgItr1 = Image.fromarray(imgItr1)

                    if rotateSubFrame2 == 1:
                    
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        imgItr2 = ndimage.rotate(imgItr1, ang, reshape=False)
                        imgItr2 = self.cropZoom(imgItr2, 2)
                        #imgItr2 = Image.fromarray(imgItr2)

                    # region = (left, upper, right, lower)
                    # subbox = (i + 1, i + 1, newDimX, newDimY)
                    for j in range(SzY):
                        for k in range(SzX):
                            
                            # calculate bipolar subframes then interleave (out = priority)
                            # will require handling frame edges (no write out of frame)
                            # update index math to handle random focal points
                           
                           # ***** FIXIT ***** - refer to 23 above
                            if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
                                
                                # imgBpTsc1[j, k, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
                                # imgBpTsc2[j, k, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
                                if (j+offsetY >= 0  and j+offsetY < SzY) and (k+offsetX >= 0  and k+offsetX < SzX):
                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; j+offsetY = '+str(j+offsetY)+'; k+offsetX = '+str(k+offsetX))
                                    imgBpTsc1[j+offsetY, k+offsetX, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
                                    imgBpTsc2[j+offsetY, k+offsetX, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]                                

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
                        #for j in range(n_digits - len(str(numFrames - (nextInc)))):
                        for j in range(n_digits - len(str(curInc + xCnt))):
                            zr += '0'
                        strInc = zr+str(curInc + xCnt)
                    imgBSlothGlitch3Full = imgOutDir+imgBSlothGlitch3Nm+strInc+'.jpg'
                    imio.imwrite(imgBSlothGlitch3Full, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

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
            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY))
            if (focalRnd1[0] < SzX/2):
                offsetX = -int(SzX/2 - focalRnd1[0])
            else:
                offsetX = int(focalRnd1[0] - SzX/2)
            if (focalRnd1[1] < SzY/2):
                offsetY = -int(SzY/2 - focalRnd1[1])
            else:
                offsetY = int(focalRnd1[1] - SzY/2)

            #print('focalRnd1 = ['+str(focalRnd1[0])+', '+str(focalRnd1[1])+']')
            #print('offsetX = '+str(offsetX))
            #print('offsetY = '+str(offsetY))

            # focalRnd2 = randomPxlLoc(SzX, SzY)
            
            
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


#                    imgArrItr1 = np.array(imgItr1)
#                    imgArrItr2 = np.array(imgItr2)
#                    imgArrTsc1 = np.array(imgBpTsc1)
#                    imgArrTsc2 = np.array(imgBpTsc2)
#                    # region = (left, upper, right, lower)
#                    # subbox = (i + 1, i + 1, newDimX, newDimY)
#                    for j in range(SzY):
#                        for k in range(SzX):
#                            
#                            # calculate bipolar subframes then interleave (out = priority)
#                            # will require handling frame edges (no write out of frame)
#                            # update index math to handle random focal points
#                           
#                           # ***** FIXIT ***** - refer to 23 above
#                            if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
#                                
#                                # imgBpTsc1[j, k, :] = imgItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
#                                # imgBpTsc2[j, k, :] = imgItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
#                                if (j+offsetY >= 0  and j+offsetY < SzY) and (k+offsetX >= 0  and k+offsetX < SzX):
#                                    #print('*****j = '+str(j)+'; k = '+str(k)+'; j+offsetY = '+str(j+offsetY)+'; k+offsetX = '+str(k+offsetX))
#                                    imgArrTsc1[j+offsetY, k+offsetX, :] = imgArrItr2[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]
#                                    imgArrTsc2[j+offsetY, k+offsetX, :] = imgArrItr1[int(j - (SzY-newDimY)/2), int(k - (SzX-newDimX)/2), :]                                

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
    
    def xodFxSlothCult(self, imgFileList, xLength, framesPerSec, xfadeFrames, n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' FxSlothCult function '''


        if imgOutNm != 'None':
            imgFxSlothCultNm = imgOutNm
        else:
            imgFxSlothCultNm = 'imgFxSlothCult'
            
        numImg = len(imgFileList)

        imgBpTscOut = Image.open(imgFileList[eyeutil.randomIdx(numImg)])      

        SzX = imgBpTscOut.width
        SzY = imgBpTscOut.height


        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    

    
        #n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
    
    
        frameCnt = 0
        for j in range(numXfades):

                
            # initialize output
            imgBpTsc1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
            #imgBpTscOut = Image.open(imgFileList[(j*xfadeFrames+156) % numImg])
            imgBpTsc1 = Image.blend(imgBpTsc1, imgBpTscOut, 0.5)
            imgBpTsc1 = ImageOps.autocontrast(imgBpTsc1, cutoff=0)

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY
            
            # number of pixels to scale img each iteration
            hop_szx = int( (SzX/(1*xfadeFrames))*random.random() + int(SzX/23) )
            hop_szy = int( (SzY/(1*xfadeFrames))*random.random() + int(SzY/23) )
            hopModuloX = np.ceil(hop_szx/xfadeFrames)
            hopModuloY = np.ceil(hop_szy/xfadeFrames)
            
            
            #hop_szx = 32
            #hop_szy = 32
                              
            # calculate X-Y random focal point to launch telescope
#            focalRnd1 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
#            focal1 = (focalRnd1[0] + SzX/4, focalRnd1[1] + SzY/4)
#            focalRnd2 = eyeutil.randomPxlLoc(int(SzX/2), int(SzY/2))
#            focal2 = (focalRnd2[0] + SzX/4, focalRnd2[1] + SzY/4)
            
            focal1 = (int(SzX/2), int(SzY/2))


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

            
            
            alphaX = np.linspace(0.3, 0.7, xfadeFrames)   
            zn = eyeutil.cyclicZn(xfadeFrames-1)    # less one, then repeat zn[0] for full 360            

            # handles final xfade 
            if j == numXfades-1:
                xCnt = numFinalXfade
            else:
                xCnt = xfadeFrames
            curInc = nextInc
            
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                
                    #imgBpTsc2 = Image.open(imgFileList[frameCnt % numImg])
                    imgBpTsc2 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])

                    if (newDimX > hop_szx and (t%hopModuloX==0)):
                        newDimX -= hop_szx
                    if (newDimY > hop_szy and (t%hopModuloY==0)):
                        newDimY -= hop_szy
                        
                    #print('newDimX = '+str(newDimX))
                        
                    # scale image to new dimensions
                    #imgObjTemp1 = Image.open(imgFileList[frameCnt % numImg])
                    #imgObjTemp1 = imgBpTscOut.copy()
                    imgObjTemp1 = imgBpTsc2.copy()
                    imgItr1 = imgObjTemp1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr1 = ImageOps.autocontrast(imgItr1, cutoff=0)
                    if rotateSubFrame1 == 1:
                        ang = (atan2(zn[t % (xfadeFrames-1)].imag, zn[t % (xfadeFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        imgItr1 = eyeutil.eyeRotate(imgItr1, ang, rotd=rotDirection1)

                    imgItr2 = imgBpTsc1.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr2 = ImageOps.autocontrast(imgItr2, cutoff=0)
                    if rotateSubFrame2 == 1:
                        ang = (atan2(zn[t % (xfadeFrames-1)].imag, zn[t % (xfadeFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        imgItr2 = eyeutil.eyeRotate(imgItr2, ang, rotd=rotDirection2)
                    
                    # calculate box = tuple
                    newXYbox1 = ( int(focal1[0] - newDimX/2), int(focal1[1] - newDimY/2) )
                    #newXYbox2 = ( int(focal2[0] - newDimX/2), int(focal2[1] - newDimY/2) )
                    imgBpTsc1.paste(imgItr1, box=newXYbox1, mask=None)
                    imgBpTsc2.paste(imgItr2, box=newXYbox1, mask=None)


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
                    imgFxSlothCultFull = imgOutDir+imgFxSlothCultNm+strInc+'.jpg'
                    #imio.imwrite(imgFxSlothCultFull, imgBpTscOut)
                    imgBpTscOut.save(imgFxSlothCultFull)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
    
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
                         n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' xodMskLfoParascope function '''
    
        if imgOutNm != 'None':
            imgMskLfoParascopeNm = imgOutNm
        else:
            imgMskLfoParascopeNm = 'imgMskLfoParascope'
    
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
    # // *---::ODMKEYE - EYE LFO Horizontal trails f::---*
    # // *--------------------------------------------------------------* //
    
#    def odmkLfoHtrails(self, imgArray, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None'):
#        ''' LfoHtrails function '''
#    
#        if imgOutNm != 'None':
#            imgLfoHtrailsNm = imgOutNm
#        else:
#            imgLfoHtrailsNm = 'imgLfoHtrails'
#    
#        SzX = imgArray[0].shape[1]
#        SzY = imgArray[0].shape[0]
#    
#        numFrames = int(ceil(xLength * framesPerSec))
#        numXfades = int(ceil(numFrames / xfadeFrames))
#    
#        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
#        print('// *---numFrames = '+str(numFrames)+'---*')
#        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
#        print('// *---numXfades = '+str(numXfades)+'---*')    
#    
#        numImg = len(imgArray)
#    
#        n_digits = int(ceil(np.log10(numFrames))) + 2
#        nextInc = 0
#
#        
#        alphaX = np.linspace(0.0, 1.0, xfadeFrames)
#        imgRndIdxArray = eyeutil.randomIdxArray(numFrames, numImg)
#   
#        # imgDualBipolarTelescNmArray = []
#        # imgDualBipolarTelescArray = []
#
#        # generate an LFO sin control signal - 1 cycle per xfadeFrames
#        T = 1.0 / framesPerSec    # sample period
#        #LFO_T = 8 * xfadeFrames * T
#        LFO_T = 8 * xfadeFrames * T
#        
#        
#        # create composite sin source
#        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
#        x = x[0:len(x)-1]
#        LFOAMP = 3
#        LFO = LFOAMP*np.sin(LFO_T * 2.0*np.pi * x) + 3
#        
#
#        #pdb.set_trace()
#
#        frameCnt = 0
#        xfdirection = 1    # 1 = forward; -1 = backward
#        for j in range(numXfades):
#                                # random img grap from image Array
#
#            if (frameCnt % numXfades) == 0:
#                xfdirection = -xfdirection
#            if xfdirection == 1:
#                imgClone1 = imgArray[imgRndIdxArray[j]]
#                imgClone2 = imgArray[imgRndIdxArray[j+1]]               
#            else:
#                imgClone1 = imgArray[imgRndIdxArray[(numImg-2) - j]]
#                imgClone2 = imgArray[imgRndIdxArray[(numImg-2) - j+1]]
#               
#            imgClone1 = Image.fromarray(imgClone1)
#            imgClone2 = Image.fromarray(imgClone2)               
#               
#            # initialize output 
##            imgBpTsc1 = imgClone1.copy()
##            imgBpTsc2 = imgClone2.copy()
##            imgBpTscOut = imgClone1.copy()
#
#                              
#            alphaBl = round(random.random())                
#                             
#
#
#            # functionalize then call for each telescope    
#            for t in range(xfadeFrames):
#                if frameCnt < numFrames:    # process until end of total length
#
#                    print('LFO of t = '+str(int(LFO[t])))
#                    nFrameTrail = int(LFO[t])
#                    #nFrameTrail = 5
#                    
#                    imgCpy1 = imgClone1.copy()
#                    imgCpy2 = imgClone2.copy()
#
#                    if t > 0:
#                        imgCpy1 = self.horizTrails(imgClone1, SzX, SzY, nFrameTrail, 0)
#                        imgCpy2 = self.horizTrails(imgClone2, SzX, SzY, nFrameTrail, 0)
#
#                    if alphaBl == 1:
#                        imgCpy1 = Image.blend(imgCpy1, imgCpy2, alphaX[t])
#
#                    # update name counter & concat with base img name    
#                    nextInc += 1
#                    zr = ''
#    
#                    for j in range(n_digits - len(str(nextInc))):
#                        zr += '0'
#                    strInc = zr+str(nextInc)
#                    imgLfoHtrailsFull = imgOutDir+imgLfoHtrailsNm+strInc+'.jpg'
#                    imio.imsave(imgLfoHtrailsFull, imgCpy1)
#    
#                    # optional write to internal buffers
#                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
#                    # imgDualBipolarTelescArray.append(imgBpTsc)
#                    
#                    frameCnt += 1
#    
#        return
#        # return [imgLfoParascopeArray, imgLfoParascopeNmArray]


    
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
