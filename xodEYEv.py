    # -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEYEv.py))::__
#
# Python ODMK img processing research
# ffmpeg experimental
#
#
# <<<PRIMARY-PARAMETERS>>>
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
import scipy as sp
import imageio as imio
from scipy import ndimage
from scipy import misc
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance


rootDir = '../'


sys.path.insert(0, rootDir+'eye')
import xodEYEutil as eyeutil

#sys.path.insert(1, 'C:/odmkDev/odmkCode/odmkPython/DSP')
sys.path.insert(1, rootDir+'DSP')


# temp python debugger - use >>>pdb.set_trace() to set break
import pdb


# // *---------------------------------------------------------------------* //

# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : function definitions
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : object definition
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 

class xodEYEv:
    ''' # Python ODMK img processing research
        # ffmpeg experimental
        --xLength: length of output video/audio file
        --bpm: tempo of video/audio
        --timeSig: 4/4 or 3/4
        --imgFormat: img format
        --SzX, SzY: video dimensions
        --framesPerSec: video frames per second
        --fs: audio sample rate
        --rootDir: root directory of Python code
        >>tbEYEu = eyeInst.odmkEYEu(eyeLength, 93, 30.0, 41000, rootDir)
    '''

    def __init__(self, bpm, timeSig, SzX, SzY, imgFormat, framesPerSec=30.0, fs=48000, rootDir='None'):

        # *---set primary parameters from inputs---*

        if rootDir != 'None':
            self.rootDir = rootDir
            os.makedirs(rootDir, exist_ok=True)
        else:
            self.rootDir = os.path.dirname(os.path.abspath(__file__))
        self.odmkEYEuOutDir = os.path.join(self.rootDir, "odmkVIDEOuOutDir/")
        os.makedirs(self.odmkEYEuOutDir, exist_ok=True)
        # myfile_path = os.path.join(self.rootDir, "myfile.txt")

        self.fs = fs
        self.bWidth = 24         # audio sample bit width
        # ub313 bpm = 178 , 267
        self.bpm = bpm    #glamourGoat14 = 93        
        self.timeSig = timeSig         # time signature: 4 = 4/4; 3 = 3/4
        
        self.imgFormat = imgFormat    # imgFormat => { fbmp, fjpg }

        self.framesPerSec = framesPerSec

        self.eyeDir = rootDir+'eye/eyeSrc/'
        os.makedirs(self.eyeDir, exist_ok=True)

        # // *-------------------------------------------------------------* //
        # // *---::Set Master Dimensions::---* //
        self.mstrSzX = SzX
        self.mstrSzY = SzY        
        
        
        # // *-------------------------------------------------------------* //
        
        

    # #########################################################################
    # end : object definition
    # #########################################################################

    # #########################################################################
    # begin : member method definition
    # #########################################################################

   
    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img Post-processing func::---*
    # // *********************************************************************** //
    # // *********************************************************************** //


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
            misc.imsave(imgMirrorHV4NmFull, imgMirrorHV4)
    
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
            misc.imsave(imgMirrorTemporalHV4NmFull, imgMirrorTemporalHV4)
    
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
                            if ((j >= hop_sz) and (j < newDimY+(hop_sz)/2) and (k >= hop_sz) and (k < newDimX+(hop_sz)/2)):
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
    # // *---::XODMKEYE - Image Linear EFFX Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    
    def xodLinEFFX(self, imgSeqArray, numFrames, xBFrames, effx, fadeInOut, fwdRev,
                   n_digit, eyeOutDirName, eyeOutFileName):
        
        ''' Tempo based linear effects
            numFrames - total video output frames
            xBFrames - frames per beat
            effx      - effects type: 0 = random ; 1 = fwd/rev ; 2 = solarize ;
                                      3 = div ; 4 = sobelXY ; 5 sobelZ
            fadeInOut - effx direction: 0 = random ; 1 = clean->effx ; 2 = effx->clean
            fwdRrev   - frame direction: 0 = random ; 1 = fwd ; 0 = rev
            imgOutDir - full path output directory '''
            
    
        xBeats = int(np.floor(numFrames/xBFrames))
        xTail = int(np.floor(numFrames - xBeats*xBFrames))


        for i in range(xBeats):
            offsetIdx = eyeutil.circ_idx(i*xBFrames, len(imgSeqArray))
            self.xodImgLinEFFX(imgSeqArray[offsetIdx:len(imgSeqArray)], xBFrames, effx, 
                               fadeInOut, fwdRev, n_digit, eyeOutDirName, eyeOutFileName)
        
        offsetIdx = eyeutil.circ_idx(xBeats*xBFrames, len(imgSeqArray))
        self.xodImgLinEFFX(imgSeqArray[offsetIdx:len(imgSeqArray)], xTail, effx, 
                           fadeInOut, fwdRev, n_digit, eyeOutDirName, eyeOutFileName)

        return
    
    
    
    def xodImgLinEFFX(self, imgFileList, numFrames, effx, fadeInOut, fwdRev, 
                      n_digits, imgOutDir, imgOutNm='None'):
    
        ''' x-fades from clean <-> effx over numFrames
            imgFileList - list of full path file names, .jpg
            numFrames - length of output sequence written to out dir
            effx      - effects type: 0 = random ; 1 = fwd/rev ; 2 = solarize ;
                                      3 = div ; 4 = sobelXY ; 5 sobelZ
            fadeInOut - effx direction: 0 = random ; 1 = clean->effx ; 2 = effx->clean
            fwdRrev   - frame direction: 0 = random ; 1 = fwd ; 2 = rev
            imgOutDir - full path output directory '''
            
        
        # constant internal value equals number of implemented effects
        numEffx = 5
        
        
        if imgOutNm != 'None':
            imgLinEFFXNm = imgOutNm
        else:
            imgLinEFFXNm = 'imgLinEFFX'
            
        f_idx = eyeutil.getLatestIdx(imgOutDir, imgLinEFFXNm)

            
        nextInc = 1 + f_idx

        
        if effx == 0:
            effx = round((numEffx-1)*random.random())+1
        
        if effx == 2:
            solarX = np.linspace(5.0, 255.0, numFrames)
        elif effx == 3 or effx == 4 or effx == 5:
            alphaX = np.linspace(0.0001, 1.0, numFrames)
            
            
        if fadeInOut == 0:
            fadeInOut = round(random.random())+1
    
        if fwdRev == 0:
            fwdRev = round(random.random())+1


        
        for i in range(numFrames):
            
            if fwdRev == 2:
                img1 = imio.imread(imgFileList[(numFrames-1-i) % len(imgFileList)])
            else:
                img1 = imio.imread(imgFileList[i % len(imgFileList)])
            
            # linear select (no-effx) fwd <-> back
            if effx == 1:
                resImg = img1

            if effx == 2:
                imgPIL1 = Image.fromarray(img1)
                if fadeInOut == 2:
                    solarB = ImageOps.solarize(imgPIL1, solarX[numFrames-1-i])
                else:
                    solarB = ImageOps.solarize(imgPIL1, solarX[i])
                solarB = ImageOps.autocontrast(solarB, cutoff=0)
                resImg = np.array(solarB)

            elif effx == 3:
                if fwdRev == 2:
                    img2 = imio.imread(imgFileList[(numFrames-1-i) % len(imgFileList)])
                else:
                    img2 = imio.imread(imgFileList[(i+1) % len(imgFileList)])
                #imgPIL2 = Image.fromarray(imgB)
                
                if fadeInOut == 2:
                    # image division blend algorithm..
                    c = img1/((img2.astype('float')+1)/(256*alphaX[i]))
                    # saturating function - if c[m,n] > 255, set to 255:
                    imgDIVB = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
                    
                else:
                    # image division blend algorithm..
                    c = img1/((img2.astype('float')+1)/(256*alphaX[numFrames-1-i]))
                    # saturating function - if c[m,n] > 255, set to 255:
                    imgDIVB = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
                imgDIVpil = Image.fromarray(imgDIVB.astype(np.uint8))
                imgAutoCon = ImageOps.autocontrast(imgDIVpil, cutoff=0)
                resImg = np.array(imgAutoCon)
                resImg = resImg.astype(np.uint8)
                
            elif effx == 4:
                imgPIL1 = Image.fromarray(img1)
                sobelXY = eyeutil.eyeSobelXY(img1)
                imgPIL2 = Image.fromarray(sobelXY)
                
                if fadeInOut == 2:
                    alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
                else:
                    alphaB = Image.blend(imgPIL2, imgPIL1, alphaX[i])
                alphaB = ImageOps.autocontrast(alphaB, cutoff=0)
                resImg = np.array(alphaB)
                
            elif effx == 5:
                imgPIL1 = Image.fromarray(img1)
                imgSmooth = eyeutil.median_filter_rgb(img1, 16)
                sobelXY = eyeutil.eyeSobelXY(imgSmooth)
                imgPIL2 = Image.fromarray(sobelXY)
                
                if fadeInOut == 2:
                    alphaB = Image.blend(imgPIL1, imgPIL2, alphaX[i])
                else:
                    alphaB = Image.blend(imgPIL2, imgPIL1, alphaX[i])
                alphaB = ImageOps.autocontrast(alphaB, cutoff=0)
                resImg = np.array(alphaB)
            
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgLinEFFXNm+strInc+'.jpg'
            imgLinSelFull = imgOutDir+imgNormalizeNm
            imio.imwrite(imgLinSelFull, resImg)

            nextInc += 1
            
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Linear F<->B Select Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkImgRotLinSel(self, imgList, numFrames, imgOutDir, imgOutNm='None'):
    
        if imgOutNm != 'None':
            imgRndSelNm = imgOutNm
        else:
            imgRndSelNm = 'imgRndSelOut'
    
    
        zn = eyeutil.cyclicZn(numFrames-1)    # less one, then repeat zn[0] for full 360
        
        idx = 0
        
        imgCount = numFrames
        n_digits = int(ceil(np.log10(imgCount))) + 2
        nextInc = 1
        xfdirection = 1
        for i in range(numFrames):
            
            raw_gz1 = imgList[idx]
            ang = (atan2(zn[i % (numFrames-1)].imag, zn[i % (numFrames-1)].real))*180/np.pi
            rotate_gz1 = ndimage.rotate(raw_gz1, ang, reshape=False)            
            rotate_gz1 = self.cropZoom(rotate_gz1, 2)

            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgNormalizeNm = imgRndSelNm+strInc+'.jpg'
            imgRndSelFull = imgOutDir+imgNormalizeNm
            imio.imwrite(imgRndSelFull, rotate_gz1)

            if (nextInc % len(imgList)-1) == 0:
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
            
        return
        
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - Image Rotate Sequence Algorithm::---*')
    # // *--------------------------------------------------------------* //
    
    def odmkImgRotateSeq(self, imgSrc, numFrames, imgOutDir, imgOutNm='None', rotDirection=0):
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
            rotate_gz1 = ndimage.rotate(imgSrc, ang, reshape=False)
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgRotateSeqFull = imgOutDir+imgRotateSeqNm+strInc+'.jpg'
            imio.imwrite(imgRotateSeqFull, rotate_gz1)
    
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
                    frameCnt += 1
    
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
        
        if echoDecay == 'cos':
            qtrcos = eyeutil.quarterCos(numEcho)    # returns a quarter period cosine wav of length n    
        
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
                misc.imsave(imgRndSelFull, imgList[echoImgIdx])
                echoFrames = (numEcho + 1) * echoStep
                k += 1
                h = 1
            elif (h <= echoFrames and (h % echoStep) == 0):
                imio.imwrite(imgRndSelFull, imgList[echoImgIdx])
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
    
        #zn = cyclicZn(framesPerBeat-1)    # less one, then repeat zn[0] for full 360
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
    # // *---::ODMKEYEV - Frame Parascope telescope video f::---*
    # // *--------------------------------------------------------------* //
    
    def xodVFrameParascope(self, imgFileList, xLength, framesPerSec, xfadeFrames, 
                           n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' xodVFrameParascope function '''
    
        if imgOutNm != 'None':
            imgVFrameParascopeNm = imgOutNm
        else:
            imgVFrameParascopeNm = 'imgVFrameParascope'
    
        #imgObjTemp1 = Image.open(imgFileList[eyeutil.randomIdx(numImg)])
        imgObjTemp1 = Image.open(imgFileList[0])

        SzX = imgObjTemp1.width
        SzY = imgObjTemp1.height
    
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
        #hop_sz = 12
        #hop_sz = 44
        #hop_sz = 56
        hop_sz = 76
        
        alphaX = np.linspace(0.0, 1.0, xfadeFrames)



        # generate an LFO sin control signal - 1 cycle per xfadeFrames
        T = 1.0 / framesPerSec    # sample period
        LFO_T = 8 * xfadeFrames * T
        # create composite sin source
        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        x = x[0:len(x)-1]
        LFOAMP = 300
        LFO = LFOAMP*np.sin(LFO_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):

            #imgClone1 = misc.imread(imgFileList[j*xfadeFrames % numImg])
            #imgClone2 = misc.imread(imgFileList[(j*xfadeFrames+int(xfadeFrames/2)) % numImg])
            imgClone1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = Image.open(imgFileList[round(numImg*random.random()) % numImg])

                
            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            imgBpTscOut = imgClone1.copy()

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY


            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length

                    #print('LFO of t = '+str(int(LFO[t])))
                    hop_sz_mod = LFO[t] * hop_sz

                    if newDimX > hop_sz_mod:
                        newDimX -= 3*hop_sz
                        if newDimX < 2:
                            newDimX = 2
                        #newDimX -= hop_sz_mod
                        newDimX = int(newDimX)
                    if newDimY > hop_sz_mod:
                        newDimY -= 3*hop_sz
                        if newDimY < 2:
                            newDimY = 2
                        #newDimY -= hop_sz_mod
                        newDimY = int(newDimY)
                           
                    #print('*****LFO[t] = '+str(LFO[t])+', hop_sz_mod = '+str(hop_sz_mod)+', newDimX = '+str(newDimX)+', newDimY = '+str(newDimY))
                        
                    #pdb.set_trace()  
                        
                    # scale image to new dimensions
                    imgClone3 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
                    imgItr1 = imgClone3.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    imgItr2 = imgClone2.resize((newDimX, newDimY), resample=Image.BICUBIC)
                    
                    imgArrItr1 = np.array(imgItr1)
                    imgArrItr2 = np.array(imgItr2)
                    imgArrTsc1 = np.array(imgBpTsc1)
                    imgArrTsc2 = np.array(imgBpTsc2)

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
                                imgArrTsc1[j, k, :] = imgArrItr1[r, s, :]
                                imgArrTsc2[j, k, :] = imgArrItr2[r, s, :]
                                
                            if (k >= (SzX-newDimX)/2) and (k < (SzX - (SzX-newDimX)/2)):
                                s += 1
                        if (j >= (SzY-newDimY)/2) and (j < (SzY - (SzY-newDimY)/2)):
                            r += 1                                

                    imgBpTscOut = Image.blend(Image.fromarray(imgArrTsc1), Image.fromarray(imgArrTsc2), alphaX[t])
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
                    imgVFrameParascopeFull = imgOutDir+imgVFrameParascopeNm+strInc+'.jpg'
                    imgBpTscOut.save(imgVFrameParascopeFull)
                    
                    frameCnt += 1
    
        return
    
    
    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYEV - Lfo Parascope telescope video f::---*
    # // *--------------------------------------------------------------* //
    
    def xodVLfoParascope(self, imgFileList, xLength, framesPerSec, xfadeFrames, 
                         n_digits, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' xodVLfoParascope function '''
    
        if imgOutNm != 'None':
            imgVLfoParascopeNm = imgOutNm
        else:
            imgVLfoParascopeNm = 'imgVLfoParascope'
    
        imgBpTscOut = Image.open(imgFileList[0])
        imgBpTsc2 = Image.open(imgFileList[0])

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
        LFO1_T = 6 * xfadeFrames * T
        LFO2_T = 5 * xfadeFrames * T
        LFO3_T = 2 * xfadeFrames * T
        # create composite sin source
        x = np.linspace(0.0, (xfadeFrames+1)*T, xfadeFrames+1)
        x = x[0:len(x)-1]
        LFO1AMP = SzY/6
        LFO2AMP = SzY/5
        LFO3AMP = 1
        LFO1 = LFO1AMP*np.sin(LFO1_T * 2.0*np.pi * x)
        LFO2 = LFO2AMP*np.sin(LFO2_T * 2.0*np.pi * x)
        LFO3 = LFO3AMP*np.sin(LFO3_T * 2.0*np.pi * x)

        frameCnt = 0
        for j in range(numXfades):

            imgClone1 = Image.open(imgFileList[round(numImg*random.random()) % numImg])
            imgClone2 = Image.open(imgFileList[round(numImg*random.random()) % numImg])

                
            # initialize output 
            imgBpTsc1 = imgClone1.copy()
            imgBpTsc2 = imgClone2.copy()
            #imgBpTsc2 = imgBpTsc1

            newDimX = SzX     # start with master img dimensions
            newDimY = SzY


            # functionalize then call for each telescope    
            for t in range(xfadeFrames):
                if frameCnt < numFrames:    # process until end of total length
                    
                    #pdb.set_trace()

                    focalMod[0] = focal1[0] + LFO3[t]*LFO1[t]
                    focalMod[1] = focal1[1] + LFO3[t]*LFO2[t]

                    #print('LFO of t = '+str(int(LFO[t])))
                    #hop_sz_mod = LFO1[t] * hop_sz

                    if newDimX > hop_sz:
                        newDimX -= hop_sz
                        if newDimX < 2:
                            newDimX = 2
                        #newDimX -= hop_sz_mod
                        newDimX = int(newDimX)
                    if newDimY > hop_sz:
                        newDimY -= hop_sz
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
                    imgVLfoParascopeFull = imgOutDir+imgVLfoParascopeNm+strInc+'.jpg'
                    imgBpTscOut.save(imgVLfoParascopeFull)
                    
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
    
    def odmkBSlothGlitch1(self, imgArray, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0, indexOffset='None'):
        ''' BSlothGlitch1 function '''
    
        if imgOutNm != 'None':
            imgBSlothGlitch1Nm = imgOutNm
        else:
            imgBSlothGlitch1Nm = 'imgBSlothGlitch1'
    
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
                    imgBSlothGlitch1Full = imgOutDir+imgBSlothGlitch1Nm+strInc+'.jpg'
                    imio.imwrite(imgBSlothGlitch1Full, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
                    
        #print('\n// *---Final Frame Count = '+str(frameCnt)+'---*')
    
        return


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - ODMKEYE - EYE FxSlothCultLife Glitch::---*
    # // *--------------------------------------------------------------* //
    
    def odmkFxSlothCult(self, imgFileList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' BSlothGlitch1 function '''

        imgObjTemp1 = imio.imread(imgFileList[0])  
        imgObjTemp2 = imio.imread(imgFileList[0])        

        SzX = imgObjTemp1.shape[1]
        SzY = imgObjTemp1.shape[0]
        
        #pdb.set_trace()
        
        if imgObjTemp2.shape[1] != SzX or imgObjTemp2.shape[0] != SzY:
            print('ERROR: image arrays must be the same size')
            return 1
    
        if imgOutNm != 'None':
            imgFxSlothCultNm = imgOutNm
        else:
            imgFxSlothCultNm = 'imgFxSlothCult'


    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgFileList)        
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        # example internal control signal 
        hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
    
 
    
        frameCnt = 0
        for j in range(numXfades):
                                # random img grap from image Array

                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgBpTsc1 = misc.imread(imgFileList[j*xfadeFrames % numImg])
            imgBpTscOut = misc.imread(imgFileList[j*xfadeFrames % numImg])
            
            # offset by n frames
            #imgBpTsc1 = misc.imread(imgFileList[(j*xfadeFrames+5560) % numImg])
            #imgBpTscOut = misc.imread(imgFileList[(j*xfadeFrames+4560) % numImg])

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
#            if (round(random.random())):
#                rotateSubFrame1 = 1
#                if (round(random.random())):
#                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
#            if (round(random.random())):
#                rotateSubFrame2 = 1
#                if (round(random.random())):
#                    rotDirection2 = 1

            # functionalize then call for each telescope
#            xfadeMpy = round(3*random.random())
#            if xfadeMpy == 0:
#                xfadeMpy = 1
#            xFrames = xfadeFrames*xfadeMpy    # randomly mpy xfadeFrames 1:3
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
                
                    imgBpTsc2 = misc.imread(imgFileList[frameCnt % numImg])
                    #imgBpTsc2 = misc.imread(imgFileList[(frameCnt+5560) % numImg])

                    if newDimX > hop_sz:
                        #newDimX -= 2*hop_sz
                        newDimX -= hop_sz
                    if newDimY > hop_sz:
                        #newDimY -= 2*hop_sz
                        newDimY -= hop_sz
                        
                    # scale image to new dimensions
                    imgObjTemp1 = misc.imread(imgFileList[frameCnt % numImg])
                    #imgObjTemp1 = misc.imread(imgFileList[(frameCnt+5560) % numImg])
                    imgItr1 = self.odmkEyeRescale(imgObjTemp1, newDimX, newDimY)
                    if rotateSubFrame1 == 1:
                        
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        imgItr1 = ndimage.rotate(imgItr1, ang, reshape=False)

                    imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                    if rotateSubFrame2 == 1:
                    
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        imgItr2 = ndimage.rotate(imgItr2, ang, reshape=False)


                    # region = (left, upper, right, lower)
                    # subbox = (i + 1, i + 1, newDimX, newDimY)

                    for j in range(SzY):
                        for k in range(SzX):
                            
                            if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
                                
                                if (j+offsetY >= 0  and j+offsetY < SzY) and (k+offsetX >= 0  and k+offsetX < SzX):
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
                    imgFxSlothCultFull = imgOutDir+imgFxSlothCultNm+strInc+'.jpg'
                    imio.imwrite(imgFxSlothCultFull, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
    
        return
        # return [imgBSlothRecursArray, imgBSlothRecursNmArray]



    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - ODMKEYE - EYE FxSlothCultLife Glitch::---*
    # // *--------------------------------------------------------------* //
    
    def odmkVideoGoreXXZ01(self, imgFileList, xLength, framesPerSec, xfadeFrames, imgOutDir, imgOutNm='None', inOrOut=0):
        ''' odmkVideoGoreXXZ01 function '''

        #pdb.set_trace()
        imgObjTemp1 = imio.imread(imgFileList[0])  
        imgObjTemp2 = imio.imread(imgFileList[0])        

        SzX = imgObjTemp1.shape[1]
        SzY = imgObjTemp1.shape[0]
        
        #pdb.set_trace()
        
        if imgObjTemp2.shape[1] != SzX or imgObjTemp2.shape[0] != SzY:
            print('ERROR: image arrays must be the same size')
            return 1
    
        if imgOutNm != 'None':
            imgFxSlothCultNm = imgOutNm
        else:
            imgFxSlothCultNm = 'imgFxSlothCult'


    
        numFrames = int(ceil(xLength * framesPerSec))
        numXfades = int(ceil(numFrames / xfadeFrames))
        numFinalXfade = int(ceil(numFrames - (floor(numFrames / xfadeFrames) * xfadeFrames)))
    
        print('// *---source image dimensions = '+str(SzX)+' x '+str(SzY))
        print('// *---numFrames = '+str(numFrames)+'---*')
        print('// *---numxfadeImg = '+str(xfadeFrames)+'---*')
        print('// *---numXfades = '+str(numXfades)+'---*')    
    
        numImg = len(imgFileList)        
    
        n_digits = int(ceil(np.log10(numFrames))) + 2
        nextInc = 0
        # example internal control signal 
        hop_sz = ceil(np.log(SzX/xfadeFrames))  # number of pixels to scale img each iteration
    
 
    
        frameCnt = 0
        for j in range(numXfades):
                                # random img grap from image Array

                
            # initialize output
            # ***** normally use imgClone1.copy(), but this function abuses the assignment
            imgBpTsc1 = imio.imread(imgFileList[j*xfadeFrames % numImg])
            imgBpTscOut = imio.imread(imgFileList[j*xfadeFrames % numImg])
            
            # offset by n frames
            #imgBpTsc1 = misc.imread(imgFileList[(j*xfadeFrames+5560) % numImg])
            #imgBpTscOut = misc.imread(imgFileList[(j*xfadeFrames+4560) % numImg])

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
#            if (round(random.random())):
#                rotateSubFrame1 = 1
#                if (round(random.random())):
#                    rotDirection1 = 1

            rotateSubFrame2 = 0             # randomly set rotation on/off
            rotDirection2 = 0            
#            if (round(random.random())):
#                rotateSubFrame2 = 1
#                if (round(random.random())):
#                    rotDirection2 = 1

            # functionalize then call for each telescope
#            xfadeMpy = round(3*random.random())
#            if xfadeMpy == 0:
#                xfadeMpy = 1
#            xFrames = xfadeFrames*xfadeMpy    # randomly mpy xfadeFrames 1:3
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
                
                    imgBpTsc2 = misc.imread(imgFileList[frameCnt % numImg])

                    if newDimX > hop_sz:
                        #newDimX -= 2*hop_sz
                        newDimX -= hop_sz
                    if newDimY > hop_sz:
                        #newDimY -= 2*hop_sz
                        newDimY -= hop_sz
                        
                    # scale image to new dimensions
                    imgObjTemp1 = misc.imread(imgFileList[frameCnt % numImg])            
                    imgObjTemp2 = misc.imread(imgFileList[(numFrames-frameCnt-1) % numImg])
                    
                    imgItr = self.eyePhiFrame3(imgObjTemp1, imgObjTemp2, 'UR')    
                    
                    imgItr = self.odmkEyeRescale(imgItr, newDimX, newDimY)
                    
                    if rotateSubFrame1 == 1:
                        
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection1 == 1:
                            ang = -ang
                            
                        imgItr1 = ndimage.rotate(imgItr, ang, reshape=False)

                    imgItr2 = self.odmkEyeRescale(imgBpTsc1, newDimX, newDimY)
                    if rotateSubFrame2 == 1:
                    
                        ang = (atan2(zn[t % (xFrames-1)].imag, zn[t % (xFrames-1)].real))*180/np.pi
                        if rotDirection2 == 1:
                            ang = -ang
                            
                        imgItr2 = ndimage.rotate(imgItr2, ang, reshape=False)


                    # region = (left, upper, right, lower)
                    # subbox = (i + 1, i + 1, newDimX, newDimY)

                    for j in range(SzY):
                        for k in range(SzX):
                            
                            if ((j >= (t+1)*hop_sz) and (j < newDimY+((t+1)*hop_sz)/2) and (k >= (t+1)*hop_sz) and (k < newDimX+((t+1)*hop_sz)/2)):
                                
                                if (j+offsetY >= 0  and j+offsetY < SzY) and (k+offsetX >= 0  and k+offsetX < SzX):
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
                    imgFxSlothCultFull = imgOutDir+imgFxSlothCultNm+strInc+'.jpg'
                    imio.imwrite(imgFxSlothCultFull, imgBpTscOut)
    
                    # optional write to internal buffers
                    # imgDualBipolarTelescNmArray.append(imgDualBipolarTelescFull)
                    # imgDualBipolarTelescArray.append(imgBpTsc)

                    xCnt -= 1                    
                    frameCnt += 1
    
        return
    


    # // *********************************************************************** //    
    # // *********************************************************************** //
    # // *---::ODMK img masking Algorithms::---*
    # // *********************************************************************** //
    # // *********************************************************************** //


    # // *--------------------------------------------------------------* //
    # // *---::ODMKEYE - 2 Channel Mask Algorithm::---*
    # // *--------------------------------------------------------------* //
    
    def odmkMask2EFFX(self, imgSeqArray, imgAltArray, maskArray, numFrames, xBFrames,
                      effx, fadeInOut, fwdRev, eyeOutDirName, eyeOutFileName):
    
        ''' outputs a sequence of masked rotated images (static img input)
            360 deg - period = xBFrames * 4 (alternate rotation) '''
            
            
        imgSeq0 = imio.imread(imgSeqArray[0])
        imgAlt0 = imio.imread(imgAltArray[0])
        mask0 = imio.imread(maskArray[0])
        
        
        if imgSeq0.shape[1] != imgAlt0.shape[1] or imgSeq0.shape[0] != imgAlt0.shape[0]:
            print('ERROR: image arrays must be the same size')
            return 1
        
        if mask0.shape[1] != imgAlt0.shape[1] or mask0.shape[0] != imgAlt0.shape[0]:
            print('ERROR: mask & image must be the same size')
            return 1
            
            
    
        zn = eyeutil.cyclicZn(numFrames-1)    # less one, then repeat zn[0] for full 360
    
        #imgCount = numFrames
        #n_digits = int(ceil(np.log10(imgCount))) + 2
        n_digits = 8
        nextInc = 0
        maskIdx = 0
        for i in range(numFrames):
            
            # imgSeqArray rotate sequence
            ang = (atan2(zn[i % (numFrames-1)].imag, zn[i % (numFrames-1)].real))*180/np.pi
            if (i % 4*xBFrames) == 0:
                ang = -ang
            if (i % 6*xBFrames) == 0:
                mask = imio.imread(maskArray[eyeutil.circ_idx(maskIdx, len(maskArray))])
                maskIdx += 1
            raw_gz1 = imio.imread(imgSeqArray[eyeutil.circ_idx(i, len(imgSeqArray))])
            imgPIL1 = Image.fromarray(raw_gz1)
            rotate_gz1 = ndimage.rotate(imgPIL1, ang, reshape=False)            
            rotate_gz1 = eyeutil.cropZoom(rotate_gz1, 2)
            
            
            imgAlt = imio.imread(imgAltArray[eyeutil.circ_idx(i, len(imgAltArray))])
            
#            maskPIL1 = Image.fromarray(imgMask)
#            if maskResize ==1:
#                eyeMask = np.array(maskPIL1.resize(imgSeqArray[0].shape[1::-1], Image.BILINEAR))
#            else:
#                eyeMask = imgMask
                
            # mask 
            eyeFmask = eyeutil.eyeMask2Ch(mask, rotate_gz1, imgAlt)
            
            nextInc += 1
            zr = ''
            for j in range(n_digits - len(str(nextInc))):
                zr += '0'
            strInc = zr+str(nextInc)
            imgRotateSeqFull = eyeOutDirName+eyeOutFileName+strInc+'.jpg'
            imio.imwrite(imgRotateSeqFull, eyeFmask)

            
        return    
    
    
    
    
    
    
    
    

# // *---------------------------------------------------------------------* //


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# Notes:
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# ***
# convert from Image image to Numpy array:
# arr = np.array(img)

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






