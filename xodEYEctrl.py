# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEYEctrl.py))::__
#
# Python XODMK img processing research testbench
# requires: xodEYEutil.py, xodEYEdata.py, xodEYEu.py, xodEYEv.py, xodFFmpeg.py
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os, sys
from math import ceil
import glob
#import shutil
import random
import numpy as np
#import scipy as sp
import imageio as imio
#from scipy import misc
#from scipy import ndimage
import soundfile as sf
import matplotlib.pyplot as plt

# temp python debugger - use >>> pdb.set_trace() to set break
import pdb

# from PIL import Image
# from PIL import ImageOps
# from PIL import ImageEnhance


# *-- Set img/video file source --*
# rootDir = 'C:/XODMK/xodmkCode/xodmkPython/'
# eyeDir = rootDir+'eye/'
# eyeSrcDir = rootDir+'eye/eyeSrc/'
# audioScrDir = '../audio/wavsrc/'
# audioOutDir = '../audio/wavout/'
# audioTestDir = '../audio/testout/'


# // *---------------------------------------------------------------------* //
# // *---------------------------------------------------------------------* //

# transfer from alt pc
# runDir = 'C:/XODMK/xodmkCode/xodmkPython/eye/'
# os.chdir(runDir)
# import xodEyeSetRootDir as xdir
# sys.path.insert(1, xdir.rootDir+'DSP/')

# assumes python projects are located in /python/
# assumes currentDir is directory containing xodEYEx.py source, ex: /python/xodEYE/

currentDir = os.getcwd()
rootDir = os.path.dirname(currentDir)

eyeSrcDir = currentDir + "/eye/src"

audioSrcDir = rootDir + "/audio/wavsrc"
audioOutDir = rootDir + "/audio/wavout"

print("currentDir: " + currentDir)
print("rootDir: " + rootDir)


sys.path.insert(0, rootDir+'xodEYE/')
import xodEYEdata as eyedata
import xodEYEutil as eyeutil
import xodEYEu as xodeyeu
import xodEYEv as xodeyev
import xodFFmpeg as xodffm
# import xodEYEx as xodeyex


sys.path.insert(1, rootDir+'/git/xodDSP/')
import xodClocks as clks
import xodWavGen as wavGen


sys.path.insert(2, rootDir+'/xodUtil/')
# import xodPlotUtil as xodplt


sys.path.insert(3, rootDir+'/xodma/')
import xodmaAudioTools as xodaudio


# Audio Detect Onset & Wav segmentation

from xodmaAudioTools import load_wav, samples_to_time, time_to_samples, fix_length
from xodmaOnset import detectOnset, getOnsetSampleSegments, getOnsetTimeSegments
from xodmaSpectralTools import amplitude_to_db, stft, istft, peak_pick
from xodmaSpectralTools import magphase
#from xodmaVocoder import pvTimeStretch, pvPitchShift
from xodmaSpectralUtil import frames_to_time
from xodmaSpectralPlot import specshow


print('// //////////////////////////////////////////////////////////////// //')
print('// *--------------------------------------------------------------* //')
print('// *---:: XODMK EYE ESP ::---*')
print('// *--------------------------------------------------------------* //')
print('// \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ //')

# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# // *--------------------------------------------------------------* //
# // # // *---:: Select Program Control ::---*')
# // *--------------------------------------------------------------* //


cntrlEYE = eyedata.xodEYEutil_dict["ResizeAll"]
#cntrlEYE = eyedata.xodEYEutil_dict["FrameIntpLin"]
#cntrlEYE = eyedata.xodEYEutil_dict["FrameIntpStride"]
#cntrlEYE = eyedata.xodEYEv_dict["LinEFFX"]
#cntrlEYE = eyedata.xodEYEv_dict["AutoSeq"]
#cntrlEYE = eyedata.xodEYEv_dict["ChainSeq"]
#cntrlEYE = eyedata.xodEYEu_dict["MskDualESP"]
#cntrlEYE = 0

srcSequence = 0
xfadeSel = 0
ctrlSel = 0
effxSel = 0
cntrlOnsetDet = 0
postProcess = 0
cntrlRender = 0


# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# // *--------------------------------------------------------------* //
# // *---:: CryptResonator USR PARAM ::---*
# // *--------------------------------------------------------------* //


# *-- wavlength: processing length (seconds) ---------------------*

# 0   => full length of input .wav file
# ### => usr defined length in SECONDS

wavlength = 0
#wavlength = 56

#fs = 48000.0        # audio sample rate:
framesPerSec = 30 # video frames per second:

bpm = 133
timeSig = 4         # time signature: 4 = 4/4; 3 = 3/4

# set format of source img { fjpg, fbmp }
imgFormat = 'fjpg'


# HD Standard video aspect ratio

SzX = 1920
#SzY = 1080
SzY = 1920

#SzX = 1920
#SzY = 1280

# B4
#SzX = 4299
#SzY = 3035


#SzX = 8018
#SzY = 8018

# Golden ratio frames:
#mstrSzX = 1076
#mstrSzY = 666

#mstrSzX = 1257
#mstrSzY = 777

#mstrSzX = 1436
#mstrSzY = 888


# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# // *--------------------------------------------------------------* //
# // *---:: Set wav file source ::---*
# // *--------------------------------------------------------------* //

#earSrcNm = 'gorgulans_beatx01.wav'                 # ~7  sec = 220 frames
#earSrcNm = 'antimatterbk06.wav'                    # ~14 sec = 434 frames
#earSrcNm = 'dmttv-axon23.wav'                      # ~23
earSrcNm = 'ebolaCallibriscian_uCCrhythm.wav'       # ~28
#earSrcNm = 'cabalisk_abstract.wav'                 # ~53
#earSrcNm = 'cabalisk_spaced.wav'                   # ~1.49
#earSrcNm = 'The_Amen_Break_48K.wav'


earSrc = audioSrcDir + '/' + earSrcNm

# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# // *--------------------------------------------------------------* //
# // *---:: Set processing directories ::---*
# // *--------------------------------------------------------------* //

xodEyeDir = currentDir + "/eye/"    # ** extra / for this path

# GFX
#sourceDir = ['src/8018x/xodMetalSphynxEye8018x/']

# MOV
sourceDir = ['src/eyeRes_EXP05/']


# *** must have / at end of variable ***
#outDir = 'testout/cgbwCryptWitch8018/'
outDir = 'eyeRes/'

# *** FIXIT - check if outDir is Empty - halt ***
# currently errors with: OverflowError: cannot convert float infinity to integer

#eyeOutFileName = 'humanEyeESP_pinealResonator1080_'
eyeOutFileName = 'chrSphyxExp5_1920x'


# *---------------------------------------------------------------------------*

# set Effects Dictionary

effxDict = eyedata.xodLinSQFX_dict
# effxDict = eyedata.xodExpFX_dict


# *---------------------------------------------------------------------------*

# Auxilliary 

if cntrlEYE == 'xodChainSeq':
    autoTimeArray = [56.059, 28.025, 28.036, 84.081]
    
    effxArray = ['xodLinSQFX_fwd', 'xodLinSQFX_fwd', 'xodLinSQFX_fwd', 'xodLinSQFX_fwd']

# *---------------------------------------------------------------------------*

maskDir = xodEyeDir + 'src/8018x/mask8018x/'

maskArray = sorted(glob.glob(maskDir+'*'))

#pdb.set_trace()

# *---------------------------------------------------------------------------*
    
if cntrlRender == 1:

    mvSrc = sourceDir
    eyeSrcMvDir = xodEyeDir + mvSrc[0]

    mvDir = 'testout/vexpTestx_mv/'    # output movie directory
    eyeOutMvDir = xodEyeDir + mvDir
    
    # number of digits before image file extension, required by ffmpeg..
    # numDigits: 0 = Auto (n_digits from length of .wav -> numFrames)
    # numDigits: # = explixit #
    numDigits = 0
    
    os.makedirs(eyeOutMvDir, exist_ok=True)  # If Dir does not exist, makedir


# *---------------------------------------------------------------------------*
# *---------------------------------------------------------------------------*

eyeOutDir = xodEyeDir+outDir

os.makedirs(eyeOutDir, exist_ok=True)  # If Dir does not exist, makedir

# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

print('\n// *--------------------------------------------------------------* //')
print('// *---:: User Parameters ::---*')
print('// *--------------------------------------------------------------* //')


print('CTRL Src-Sequence  = '+str(srcSequence))
print('CTRL Eye-Algorithm = '+str(cntrlEYE))
print('CTRL Post-Process  = '+str(postProcess))
print('CTRL Render Video  = '+str(cntrlRender))


firstSourceDir = xodEyeDir+sourceDir[0]
print('\nImg Source Directory (first if array):\n'+firstSourceDir+'\n')
print('Img Output Directory:\n'+eyeOutDir+'\n')
if cntrlRender == 1:
    print('Movie Output Directory:\n'+eyeOutMvDir+'\n')
print('Wav Source Directory:\n'+earSrc+'\n')


print('\nXodEYE bpm: --------------------------- '+str(bpm))
print('XodEYE timeSig: ----------------------- '+str(timeSig)+'/4')
print('XodEYE Img Format: -------------------- '+imgFormat)
print('XodEYE Img Dimensions [X, Y]: --------- '+str(SzX)+' x '+str(SzY))


# /////////////////////////////////////////////////////////////////////////////
# *--- End: USER INTERFACE --*
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


print('\n// *--------------------------------------------------------------* //')
print('// *---:: Audio - Load .wav file ::---*')
print('// *--------------------------------------------------------------* //')

[wavSrc, numChannels, fs, xLength, xSamples] = xodaudio.load_wav(earSrc, wavlength)
print('\nLoaded .wav file [ '+earSrc+' ]\n')

if numChannels == 2:
    wavSrc_ch1 = wavSrc[:, 0]
    wavSrc_ch2 = wavSrc[:, 1]
else:
    wavSrc_ch1 = wavSrc
    wavSrc_ch2 = 0


# length of input signal - '0' => length of input .wav file
print('Channel A Source Audio:') 
print('wavSrc Channels: --------------------- '+str(len(np.shape(wavSrc))))
print('length of input signal in seconds: --- '+str(xLength))
print('length of input signal in samples: --- '+str(xSamples))
print('audio sample rate: ------------------- '+str(fs))
print('wav file datatype: ------------------- '+str(sf.info(earSrc).subtype))

period = 1.0 / fs


# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

print('\n// *--------------------------------------------------------------* //')
print('// *---:: Audio - Detect Onset Events & Wav Segmentation ::---*')
print('// *--------------------------------------------------------------* //')

if cntrlOnsetDet == 1:

    peakThresh = 7.7
    peakWait = 0.93 

    plots = 1

    onsetSamplesCH1, onsetTimeCH1 = detectOnset(wavSrc_ch1, peakThresh, peakWait)
    # onsetSamplesCH2, onsetTimeCH2 = detectOnset(wavSrc_ch2, peakThresh, peakWait)

    wavSegmentSamplesCH1 = getOnsetSampleSegments(onsetSamplesCH1, xSamples)
    wavSegmentTimesCH1 = getOnsetTimeSegments(onsetTimeCH1, xLength)

    numOnsets = len(onsetSamplesCH1)
    print('\nNumber of Onsets Detected: ' + str(numOnsets))
    # print('\nonsetSamplesCH1: ' + str(onsetSamplesCH1))
    print('\nonsetTimeCH1: ' + str(onsetTimeCH1))

    # print('\nwavSegmentSamplesCH1: ' + str(wavSegmentSamplesCH1))
    # print('\nwavSegmentTimesCH1: ' + str(wavSegmentTimesCH1))

    autoSeqArray = wavSegmentSamplesCH1
    
    # pdb.set_trace()
    
# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


print('\n// *--------------------------------------------------------------* //')
print('// *---::Instantiate objects::---*')
print('// *--------------------------------------------------------------* //')

eyeClks = clks.XodClocks(xLength, fs, bpm, framesPerSec)
print('\nCreated a xodClocks object')

numFrames = int(ceil(xLength * framesPerSec))

framesPerBeat = int(np.ceil(eyeClks.framesPerBeat))

n_digits = int(ceil(np.log10(numFrames))) + 3

eyeu = xodeyeu.xodEYEu(xLength, bpm, timeSig, SzX, SzY, imgFormat, 
                       framesPerSec=framesPerSec, fs=fs)
print('Created a xodEYEu object')

eyev = xodeyev.xodEYEv(xLength, bpm, timeSig, SzX, SzY, imgFormat,
                       framesPerSec=framesPerSec, fs=fs)
print('Created a xodEYEv object')


# *---------------------------------------------------------------------------*

print('\n// *--------------------------------------------------------------* //')
print('// *---::system Parameters::---*')
print('// *--------------------------------------------------------------* //')


print('\nSequence Length (seconds): ---------- '+str(xLength))
print('Video Frames per Second: ------------ '+str(framesPerSec))
print('Video Frame Dimensions [X, Y]: ------ '+str(SzX)+' x '+str(SzY))
print('Total Output Frames: ---------------- '+str(numFrames))


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : img pre-processing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


if cntrlEYE == 'xodRenameAll':

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::Rename All images in SRC Directory to bmp::---*')
    print('// *--------------------------------------------------------------* //')

    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')
    else:
        srcDir = xodEyeDir + sourceDir[0]

    eyeutil.xodRenameAll(srcDir, n_digits, eyeOutFileName)

    print('Saved Renamed images to the following location:')
    print(eyeOutDir)
    print('\n')


if cntrlEYE == 'convJPGtoBMP':

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::Convert All images in SRC Directory to bmp::---*')
    print('// *--------------------------------------------------------------* //')

    # define output directory for scaled img
    # Dir path must end with backslash /
    os.makedirs(eyeOutDir, exist_ok=True)
    
    eyeutil.convertJPGtoBMP(sourceDir, eyeOutDir, reName=eyeOutFileName)

    print('Saved converted images to the following location:')
    print(eyeOutDir)
    print('\n')


if cntrlEYE == 'convBMPtoJPG':

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::Convert All images in SRC Directory to jpg::---*')
    print('// *--------------------------------------------------------------* //')
    
    eyeutil.convertBMPtoJPG(sourceDir, eyeOutDir, reName=eyeOutFileName)

    print('Saved converted images to the following location:')
    print(eyeOutDir)
    print('\n')
        

# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# end : img pre-processing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : img Src Sequencing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        
    
print('\n// *--------------------------------------------------------------* //')
print('// *---:: Create Source Image Array ::---*')
print('// *--------------------------------------------------------------* //')
    
if srcSequence == 0:

    imgSeqArray, imgSrcDir = eyeutil.createSrcArray(xodEyeDir, sourceDir)

    print('\nCreated *imgSrcArray* - Array of directories of sequenced .jpg file paths:\n')

    for p in range(len(imgSrcDir)):
        print(imgSrcDir[p])
        print("# of images in directory: " + str(len(imgSeqArray[p])))
             
              
# Auxilliary Chained Sequence:

if cntrlEYE == 'xodChainSeq':              

    print("__xodChainSeq__ - autoNFrameArray: ")
    for i in range(len(autoTimeArray)):            
        print(str(int(autoTimeArray[i] * framesPerSec)))

    print('\n// *--------------------------------------------------------------* //')

# if srcSequence == 0:
#
#    #imgSeqArray = sorted(glob.glob(srcDir+'*'))   
#    srcDir = []
#    imgSeqArray = []
#    for d in range(len(sourceDir)):
#        sDirTmp = xodEyeDir+sourceDir[d]
#        srcDir.append(sDirTmp)
#        sortedDir = sorted(glob.glob(sDirTmp+'*'))
#        for s in sortedDir:
#            imgSeqArray.append(s.replace('\\', '/'))


if srcSequence == 1:
    
    print('\n// *--------------------------------------------------------------* //')
    print('// *---:: XODMKVIDEO - SRC-SEQ - LFO video scanner ::---*')
    print('// *--------------------------------------------------------------* //')
    
    # LFO video scanner - scans video directories by LFO modulation

    fsLfo = 500.0
    TLfo = 1.0 / fsLfo
    tbLFOGen = wavGen.xodWavGen(fsLfo, audioOutDir)
    
    testLFOfreq = 30
    xCtrl = tbLFOGen(numFrames, testLFOfreq, 'sin', fs=fsLfo)

    # scale and quantize xCtrl input
    for i in range(len(xCtrl)):
        xCtrl[i] = int(len(srcDirList)*xCtrl[i])

    imgSeqArray = eyeutil.scanImagDir(srcDirList, numFrames, xCtrl)
    
    print('\nCreated *imgSeqArray* - sequenced list of .jpg file paths')
    print('// *--------------------------------------------------------------* //')


elif srcSequence == 2:

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::ODMKVIDEO - SRC-SEQ - Image Pulse Scanner ::---*')
    print('// *--------------------------------------------------------------* //')

    # Pulse video scanner - pulse = log based array index, random stream switch
    
    pulseLen = framesPerBeat*2
    
    imgSeqArray = eyeutil.pulseScanRnd(srcDirList, numFrames, pulseLen)

    print('\nCreated *imgSeqArray* - sequenced list of .jpg file paths')
    print('// *--------------------------------------------------------------* //')


elif srcSequence == 3:

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::ODMKVIDEO - Two Stream imgSeqArray ::---*')
    print('// *--------------------------------------------------------------* //')

    # imgSeqArray: LFO video scanner - scans video directories by LFO modulation
    # imgAltArray: Pulse video scanner - pulse = log based array index, random stream switch

    # imgSeqArray:
    fsLfo = 500.0
    TLfo = 1.0 / fsLfo
    tbLFOGen = wavGen.xodWavGen(fsLfo, audioOutDir)
    
    testLFOfreq = 30
    xCtrl = tbLFOGen(numFrames, testLFOfreq, 'sin', fs=fsLfo)

    # scale and quantize xCtrl input
    for i in range(len(xCtrl)):
        xCtrl[i] = int(len(srcDirList)*xCtrl[i])

    imgSeqArray = eyeutil.scanImagDir(srcDirList, numFrames, xCtrl)    
    
    print('\nCreated *imgSeqArray* - sequenced list of .jpg file paths')

    # imgAltArray:
    pulseLen = framesPerBeat*2
    
    imgAltArray = eyeutil.pulseScanRnd(altDirList, numFrames, pulseLen)

    print('Created *imgAltArray* - sequenced list of .jpg file paths')
    print('// *--------------------------------------------------------------* //')
    

elif srcSequence == 5:

    imgSeqArray = sorted(glob.glob(srcDir+'*'))

    print('// *--------------------------------------------------------------* //')   
    

# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : XODMK EYE image processing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodResizeAll':
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')
    else:
        srcDir = xodEyeDir + sourceDir[0]

    reSzX = SzX
    reSzY = SzY
    
    if ctrlSel == 1:
        aspectCtrl='height'
    elif ctrlSel == 2:
        aspectCtrl='width'
    else:
        aspectCtrl='None'

    eyeutil.xodResizeAll(srcDir, reSzX, reSzY, eyeOutDir,
                         imgOutNm=eyeOutFileName, keepAspect=aspectCtrl)

    print('Saved Resized images to the following location:')
    print(eyeOutDir)
    print('\n')
    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodCropAll':
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')

    srcDir = xodEyeDir + sourceDir[0]
    
    resizeNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    resizedir = eyeOutDir

    reSzX = SzX
    reSzY = SzY
    
    if ctrlSel >= 1:
        cropHigh = 1
    else:
        cropHigh = 0
    
    eyeutil.xodCropAll(srcDir, reSzX, reSzY, resizedir, imgOutNm=resizeNm, high=cropHigh)

    print('Saved Cropped images to the following location:')
    print(eyeOutDir)
    print('\n')
    print('// *--------------------------------------------------------------* //')

    
# // *********************************************************************** //
# // *********************************************************************** //
    
if cntrlEYE == 'xodConcatAllDir':

    concatOutDir = eyeOutDir
    os.makedirs(concatOutDir, exist_ok=True)
    
    # *** names must be different from source ***
    concatOutName = eyeOutFileName
    
    srcDir = []
    imgSeqArray = []
    for d in range(len(sourceDir)):
        sDirTmp = xodEyeDir+sourceDir[d]
        srcDir.append(sDirTmp)
        
    eyeutil.concatAllDir(srcDir, concatOutDir, concatOutName)
    

# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodFrameIntpLin':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - xodFrameInterpolate linear xFade ::---*')
    print('// *--------------------------------------------------------------* //')
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')
    else:
        srcDir = xodEyeDir + sourceDir[0]

    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    
    # xfadeFrames = framesPerBeat
    xfadeFrames = xfadeSel
    ctrl = ctrlSel
    # effx = 0

    eyeutil.xodFrameInterpolate(imgSrcArray[0], xfadeFrames, ctrl, n_digits,
                                eyeOutDir, eyeOutFileName)

    print('\nOutput all images to: ' + eyeOutDir)
    
    print('// *--------------------------------------------------------------* //')
    

if cntrlEYE == 'xodFrameIntpCos':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - xodFrameInterpolate Cosine xFade ::---*')
    print('// *--------------------------------------------------------------* //')
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')
    else:
        srcDir = xodEyeDir + sourceDir[0]

    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    
    # xfadeFrames = framesPerBeat
    xfadeFrames = xfadeSel
    ctrl = ctrlSel
    effx = 1

    eyeutil.xodFrameInterpolate(imgSrcArray[0], xfadeFrames, ctrl, effx, n_digits,
                                eyeOutDir, eyeOutFileName)

    print('\nOutput all images to: ' + eyeOutDir)
    
    print('// *--------------------------------------------------------------* //')

if cntrlEYE == 'xodStrideIntp':    
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - xodStrideInterpolate stride xFade ::---*')
    print('// *--------------------------------------------------------------* //')
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')
    else:
        srcDir = xodEyeDir + sourceDir[0]

    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    
    #xfadeFrames = framesPerBeat
    xfadeFrames = ctrlSel
    effx = effxSel
    
    eyeutil.xodStrideInterpolate(imgSrcArray[0], xfadeFrames, effx, n_digits,
                                 eyeOutDir, eyeOutFileName)

    print('\nOutput all images to: ' + eyeOutDir)
    
    print('// *--------------------------------------------------------------* //')    

# // *********************************************************************** //
# // *********************************************************************** ///

if cntrlEYE == 'xodImgRndSel':

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Random Select Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # for n frames:
    # randomly select an image from the source dir, hold for h frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgRndSelNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgRndSeldir = eyeOutDir
    os.makedirs(imgRndSeldir, exist_ok=True)  # If Dir does not exist, makedir

    eyeu.xodImgRndSel(imgSeqArray, numFrames, n_digits, imgRndSeldir,
                      imgOutNm=imgRndSelNm)

    print('\nodmkImgRndSel function output => Created python lists:')
    print('<<<imgRndSelOutA>>>   (ndimage objects)')
    print('<<<imgRndSelNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(imgRndSeldir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodImgXfade':

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMK Image CrossFade Sequencer::---*')
    print('// *---Crossfade a sequence of images, period = framesPerBeat---*')
    print('// *--------------------------------------------------------------* //')

    XfadeNm = eyeOutFileName
    
    #pdb.set_trace()
    
    outXfadeDir = eyeOutDir

    # xfadeFrames = int(np.ceil(eyeClks.framesPerBeat))
    xfadeFrames = 3 * int(np.ceil(eyeClks.framesPerBeat))
    
    
    
    eyeu.xodImgXfade(imgSeqArray, xLength, framesPerSec, xfadeFrames, n_digits,
                     outXfadeDir, imgOutNm=XfadeNm)
    

    print('\nProcessed images output to the following directory:')
    print(outXfadeDir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //    
    
if cntrlEYE == 'xodXfadeTelescopeI':
    
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::XODMKEYE - Cross-fade Telescope I f::---*')
    print('// *--------------------------------------------------------------* //')


    xodXfadeTelescNm = eyeOutFileName
    xodXfadeTelescDir = eyeOutDir
    os.makedirs(xodXfadeTelescDir, exist_ok=True)

    xfadeFrames = framesPerBeat

    sLength = xLength

    inOut = 0       # telescope direction: 0 = out, 1 = in
    rndFocal = 0    # random focal point: 0 = center, 1 = random pixel loc

    eyeu.xodXfadeTelescopeI(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                             inOut, rndFocal, n_digits, xodXfadeTelescDir, 
                             imgOutNm=xodXfadeTelescNm)
    
    print('\nProcessed images output to the following directory:')
    print(xodXfadeTelescDir)

    print('// *--------------------------------------------------------------* //')
    

# // *********************************************************************** //
# // *********************************************************************** //
    
if cntrlEYE == 'xodXfadeTelescopeII':
    
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::XODMKEYE - Cross-fade Telescope II f::---*')
    print('// *--------------------------------------------------------------* //')

    xodXfadeTelescNm = eyeOutFileName
    xodXfadeTelescDir = eyeOutDir
    os.makedirs(xodXfadeTelescDir, exist_ok=True)

    xfadeFrames = framesPerBeat

    sLength = xLength

    inOut = 0      # telescope direction: 0 = out, 1 = in
    rndFocal = 0    # random focal point: 0 = center, 1 = random pixel loc
    rotate = 0      # rotating cross-fade: 0 = no ; 1 = cw ; 2 = ccw
    usemask = 1     # use mask: 0 = no ; 1 = use base img ; 2 = use mask dir
    randomFX = 0    # randomize FX: 0 = none ; # = switch randomize every # crossfades
    
    
    eyeu.xodXfadeTelescopeII(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                             inOut, rndFocal, rotate, usemask, randomFX, n_digits,
                             xodXfadeTelescDir, imgOutNm=xodXfadeTelescNm)
    
    print('\nProcessed images output to the following directory:')
    print(xodXfadeTelescDir)
    
    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //



# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : XODMK EYE image generator
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


if cntrlEYE == 'xodAutoSeq':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE XOD Auto Sequence::---*')
    print('// *--------------------------------------------------------------* //')


    ctrl = ctrlSel

    eyev.xodAutoSeq(imgSrcArray, autoSeqArray, effxDict, framesPerSec,
                    ctrl, n_digits, eyeOutDir, eyeOutFileName)

    print('\nProcessed images output to the following directory:')
    print(eyeOutDir)

    print('// *--------------------------------------------------------------* //')
    
    
# // *********************************************************************** //    
    
    
if cntrlEYE == 'xodChainSeq':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE XOD Chain Sequence::---*')
    print('// *--------------------------------------------------------------* //')


    eyev.xodChainSeq(imgSrcArray, autoTimeArray, effxArray, framesPerSec,
                    n_digits, eyeOutDir, eyeOutFileName)

    print('\nProcessed images output to the following directory:')
    print(eyeOutDir)

    print('// *--------------------------------------------------------------* //')
    

# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodPxlRndRotate':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE Pixel Random Replace f::---*')
    print('// *--------------------------------------------------------------* //')


    pxlRndRotateNm = eyeOutFileName
    pxlRndRotateDir = eyeOutDir
    os.makedirs(pxlRndRotateDir, exist_ok=True)

    xfadeFrames = framesPerBeat

    sLength = xLength

    #inOrOut = 1     # telescope direction: 0 = in, 1 = out

    eyeu.xodPxlRndRotate(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                         n_digits, pxlRndRotateDir, pxlRndRotateNm)

    print('\nProcessed images output to the following directory:')
    print(pxlRndRotateDir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodBSlothGlitch':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Bananasloth Glitch 2 f::---*')
    print('// *--------------------------------------------------------------* //')


    bSlothGlitchNm = eyeOutFileName
    bSlothGlitchDir = eyeOutDir
    os.makedirs(bSlothGlitchDir, exist_ok=True)

    xfadeFrames = framesPerBeat

    sLength = xLength

    #inOrOut = 1     # telescope direction: 0 = in, 1 = out

    eyeu.xodBSlothGlitch(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                         n_digits, bSlothGlitchDir, imgOutNm=bSlothGlitchNm)

    print('\nProcessed images output to the following directory:')
    print(bSlothGlitchDir)

    print('// *--------------------------------------------------------------* //')
    
    
# // *********************************************************************** //
# // *********************************************************************** //
    
if cntrlEYE == 'xodBSlothSwitch':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Bananasloth Glitch 2 f::---*')
    print('// *--------------------------------------------------------------* //')

    bSlothSwitchNm = eyeOutFileName
    bSlothSwitchDir = eyeOutDir
    os.makedirs(bSlothSwitchDir, exist_ok=True)

    xfadeFrames = framesPerBeat

    sLength = xLength

    eyeu.xodBSlothSwitch(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                         n_digits, bSlothSwitchDir, imgOutNm=bSlothSwitchNm)

    print('\nProcessed images output to the following directory:')
    print(bSlothSwitchDir)

    print('// *--------------------------------------------------------------* //')   

    
# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodFxSlothCult':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::XODMKEYE - EYE xodFxSlothCult ::---*')
    print('// *--------------------------------------------------------------* //')

    fxSlothCultNm = eyeOutFileName
    fxSlothCultDir = eyeOutDir
    os.makedirs(fxSlothCultDir, exist_ok=True)

    # xfadeFrames = framesPerBeat*2
    xfadeFrames = framesPerBeat

    sLength = xLength

    eyeu.xodFxSlothCult(imgSeqArray, maskArray, sLength, framesPerSec, xfadeFrames,
                        n_digits, fxSlothCultDir, imgOutNm=fxSlothCultNm)

    print('\nProcessed images output to the following directory:')
    print(fxSlothCultDir)

    print('// *--------------------------------------------------------------* //')
    
 
# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodFxSlothCultII':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::XODMKEYE - EYE xodFxSlothCultII ::---*')
    print('// *--------------------------------------------------------------* //')

    fxSlothCultNm = eyeOutFileName
    fxSlothCultDir = eyeOutDir
    os.makedirs(fxSlothCultDir, exist_ok=True)

    # xfadeFrames = framesPerBeat*2
    xfadeFrames = framesPerBeat

    sLength = xLength

    eyeu.xodFxSlothCultII(imgSeqArray, maskArray, sLength, framesPerSec, xfadeFrames,
                        n_digits, fxSlothCultDir, imgOutNm=fxSlothCultNm)

    print('\nProcessed images output to the following directory:')
    print(fxSlothCultDir)

    print('// *--------------------------------------------------------------* //')

    
# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodLfoParascope':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE xodLfoParascope ::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxLfoParascopeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxLfoParascopeDir = eyeOutDir
    os.makedirs(fxLfoParascopeDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()


    eyeu.xodLfoParascope(imgSeqArray, sLength, framesPerSec, xfadeFrames, n_digits,
                         fxLfoParascopeDir, imgOutNm=fxLfoParascopeNm)

    print('\nProcessed images output to the following directory:')
    print(fxLfoParascopeDir)

    print('// *--------------------------------------------------------------* //')
    
    
# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodMskLfoParascope':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE xodLfoParascope ::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    # eyeOutFileName = 'myOutputFileName'    # defined above
    fxMskLfoParascopeNm = eyeOutFileName
    # eyeOutDir = 'myOutputDirName'    # defined above
    fxMskLfoParascopeDir = eyeOutDir
    os.makedirs(fxMskLfoParascopeDir, exist_ok=True)

    # xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    # xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    # xfadeFrames = xLength
    
    lfoDepth = 56

    sLength = xLength
    
    #pdb.set_trace()

    eyeu.xodMskLfoParascope(imgSeqArray, sLength, framesPerSec, xfadeFrames, lfoDepth,
                            n_digits,fxMskLfoParascopeDir, imgOutNm=fxMskLfoParascopeNm)

    print('\nProcessed images output to the following directory:')
    print(fxMskLfoParascopeDir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodMskDualESP':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE xodMskDualESP ::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    xodMskDualESPNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    xodMskDualESPDir = eyeOutDir

    os.makedirs(xodMskDualESPDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    #xfadeFrames = int(framesPerBeat / 3)
    xfadeFrames = int(framesPerBeat * 4)
    #xfadeFrames = xLength
    
    inOut = 2       # 0: telescope out, 1: telescope in, 2: random per xfade

    sLength = xLength

    eyeu.xodMskDualESP(imgSeqArray, maskArray, sLength, framesPerSec, xfadeFrames,
                       n_digits, xodMskDualESPDir, imgOutNm=xodMskDualESPNm,
                       effx=effxSel, inOrOut=inOut)

    print('\nProcessed images output to the following directory:')
    print(xodMskDualESPDir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
    
# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : XODMK EYE video generator
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# // *********************************************************************** //
# // *********************************************************************** //
    
elif cntrlEYE == 'xodImgLinSel':

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::XODMKVIDEOu - Image Linear Select ::---*')
    print('// *--------------------------------------------------------------* //')

    os.makedirs(eyeOutDir, exist_ok=True)
    
    if len(imgSrcArray) > 1:
        print("WARNING: Multiple Directory Array - using only first entry")
        
    #pdb.set_trace()
    
    imgSeqArray = imgSrcArray[0]

    eyev.xodImgLinSel(imgSeqArray, xLength, framesPerSec, ctrlSel,
                      n_digits, eyeOutDir, eyeOutFileName)
    
    print('\nProcessed images output to the following directory:')
    print(eyeOutDir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

elif cntrlEYE == 'xodLinEFFX':

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::XODMKVIDEOu - Image Linear EFFX xFade Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    ''' Tempo based linear effects
        numFrames - total video output frames
        xBFrames - frames per beat
        effx      - effects type: 0 = random ; 1 = fwd/rev ; 2 = solarize ;
                                  3 = div ; 4 = sobelXY ; 5 sobelZ
        fadeInOut - effx direction: 0 = random ; 1 = clean->effx ; 2 = effx->clean
        fwdRrev   - frame direction: 0 = random ; 1 = fwd ; 0 = rev
        imgOutDir - full path output directory '''

    # eyeOutFileName = 'myOutputFileName'    # defined above

    # If Dir does not exist, makedir:
    os.makedirs(eyeOutDir, exist_ok=True)
    fadeInOut = 0
    fwdRev = 0
    effx = effxSel

    xFrames = int(np.ceil(eyeClks.framesPerBeat))
    #xFrames = int(np.ceil(eyeClks.framesPerBeat) / 3)
    
    #pdb.set_trace()
    #imgSeqArray = imgSrcArray[0]
    
    eyev.xodLinEFFX(imgSeqArray, xLength, framesPerSec, xFrames, effx, fadeInOut, fwdRev,
                    n_digits, eyeOutDir, eyeOutFileName)

    
    print('\nProcessed images output to the following directory:')
    print(eyeOutDir)


    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodVLfoParascope':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE VideoGoreXXZ01::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxVLfoParascopeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxVLfoParascopeDir = eyeOutDir
    os.makedirs(fxVLfoParascopeDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat*2
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()

    eyev.xodVLfoParascope(imgSeqArray, sLength, framesPerSec, xfadeFrames, n_digits,
                           fxVLfoParascopeDir, imgOutNm=fxVLfoParascopeNm)

    print('\nProcessed images output to the following directory:')
    print(fxVLfoParascopeDir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
    
    
if cntrlEYE == 'xodVideoGoreXXZ01':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE VideoGoreXXZ01::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    videoGoreXXZ01Nm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    videoGoreXXZ01Dir = eyeOutDir
    os.makedirs(videoGoreXXZ01Dir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat*2
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()

    eyev.xodVideoGoreXXZ01(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                           n_digits, videoGoreXXZ01Dir, videoGoreXXZ01Nm, inOrOut=0)
    
    print('\nProcessed images output to the following directory:')
    print(videoGoreXXZ01Dir)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : XODMK EXPERIMENTAL
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    
    
# // *********************************************************************** //
# // *********************************************************************** //
    
if cntrlEYE == 'imgInterlaceDir':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - imgInterlaceDir interlace files in directories::---*')
    print('// *--------------------------------------------------------------* //')

    srcDir1 = xodEyeDir+imgInterlaceSrcDir1
    srcDir2 = xodEyeDir+imgInterlaceSrcDir2
    
    interlaceNm = imgInterlaceReName
    
    imgInterlaceDir = xodEyeDir+imgInterlaceOutDir
    os.makedirs(imgInterlaceDir, exist_ok=True)

    eyeutil.imgInterlaceDir(srcDir1, srcDir2, imgInterlaceDir, reName=interlaceNm)    
    print('\nOutput all images to: '+imgInterlaceDir)
    
    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
    
if cntrlEYE == 'imgInterLaceBpmDir':

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - imgInterlaceDir interlace files in directories::---*')
    print('// *--------------------------------------------------------------* //')

    srcDir1 = xodEyeDir+imgInterlaceSrcDir1
    srcDir2 = xodEyeDir+imgInterlaceSrcDir2
    
    interlaceNm = imgInterlaceReName
    
    imgInterlaceBpmDir = xodEyeDir + imgInterlaceOutDir
    os.makedirs(imgInterlaceBpmDir, exist_ok=True)
    
    
    xfadeFrames = framesPerBeat

    
    eyeutil.imgInterLaceBpmDir(srcDir1, srcDir2, imgInterlaceBpmDir, xfadeFrames,
                               reName=interlaceNm)
    
    print('\nOutput all images to: ' + imgInterlaceBpmDir)
    
    print('// *--------------------------------------------------------------* //')
    


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


if cntrlEYE == 102:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Rotate Linear Select Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # for n frames:
    # randomly select an image from the source dir, hold for h frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgLinSelNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgLinSeldir = xodEyeDir+eyeOutDir
    os.makedirs(imgLinSeldir, exist_ok=True)  # If Dir does not exist, makedir

    xfadeFrames = int(np.ceil(eyeClks.framesPerBeat))

    eyeu.odmkImgRotLinSel(imgSeqArray, numFrames, xfadeFrames, imgLinSeldir, imgOutNm=imgLinSelNm)

    print('\nodmkImgRndSel function output => Created python lists:')
    print('<<<imgRndSelOutA>>>   (ndimage objects)')
    print('<<<imgRndSelNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(imgLinSeldir)

    print('// *--------------------------------------------------------------* //')



# // *********************************************************************** //


elif cntrlEYE == 2:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Random BPM Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # for n frames:
    # randomly select an image from the source dir, hold for n frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgRndBpmNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgRndBpmdir = xodEyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs(imgRndBpmdir, exist_ok=True)

    # generate the downFrames sequence:
    eyeDFrames = eyeClks.clkDownFrames()


    eyeu.odmkImgRndBpm(imgSeqArray, numFrames, eyeDFrames, imgRndBpmdir, imgOutNm=imgRndBpmNm)

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //



# ***GOOD -> FUNCTIONALIZEIT***

elif cntrlEYE == 3:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Random Select Telescope Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # for n frames: 
    # randomly select an image from the source dir, hold for h frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgTelescRndNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgTelescRnddir = xodEyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs( imgTelescRnddir, exist_ok=True)

    # For now, assume tlPeriod * tlItr matches final video length
    frameRate = 30
    tlItr = 7       # number of periods of telescoping period
    tlPeriod = 30   # number of frames for telescoping period
    numFrames = tlItr * tlPeriod
    # final video length in seconds = numFrames / 30
    # eyeLength = numFrames / frameRate

    # defined above!
    #SzX = SzX
    #SzY = SzY

    inOrOut = 0     # telescope direction: 0 = in, 1 = out
    hop_sz = 4

    imgTelescRndNmArray = []
    imgTelescRndArray = []

    #create an array of random index
    #use numFrames + tlItr to allow to increment starting image each tlPeriod
    rIdxArray = eyeutil.randomIdx(numFrames+tlItr, len(imgSeqArray))

    imgCount = numFrames
    n_digits = int(ceil(np.log10(imgCount))) + 2
    nextInc = 0
    for i in range(tlItr):
        newDimX = SzX
        newDimY = SzY
        imgClone = imgSeqArray[rIdxArray[i]]
        for t in range(tlPeriod):
            # select random image telescope in for select period
            
            newDimX -= hop_sz
            if newDimX < 2:
                newDimX = 2
            newDimY -= hop_sz   
            if newDimY < 2:
                newDimY = 2
                
#            if newDimX > 2:
#                newDimX -= hop_sz
#            if newDimY > 2:
#                newDimY -= hop_sz
            
            # scale image to new dimensions
            imgItr = eyeutil.odmkEyeRescale(imgClone, newDimX, newDimY)
            # region = (left, upper, right, lower)
            # subbox = (i + 1, i + 1, newDimX, newDimY)
            for j in range(SzY):
                for k in range(SzX):
                    if ((j > t+hop_sz) and (j < newDimY) and (k > t+hop_sz) and (k < newDimX)):
                        imgClone[j, k, :] = imgItr[j - t, k - t, :]
            nextInc += 1
            zr = ''
            if inOrOut == 1:
                for j in range(n_digits - len(str(nextInc))):
                    zr += '0'
                strInc = zr+str(nextInc)
            else:
                for j in range(n_digits - len(str(imgCount - (nextInc)))):
                    zr += '0'
                strInc = zr+str(imgCount - (nextInc))
            imgNormalizeNm = imgTelescRndNm+strInc+'.jpg'
            imgRndSelFull = imgTelescRnddir+imgNormalizeNm
            imio.imsave(imgRndSelFull, imgClone)


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


# // *---------------------------------------------------------------------* //
# // *--Image Rotate & alternate sequence--*
# // *---------------------------------------------------------------------* //


elif cntrlEYE == 5:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE odmkImgRotateAlt::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    imgRotateAltNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    imgRotateAltDir = xodEyeDir+eyeOutDir
    os.makedirs(imgRotateAltDir, exist_ok=True)

    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength


    eyeu.odmkImgRotateAlt(imgSrcArray, sLength, framesPerSec, xfadeFrames, imgRotateAltDir, imgOutNm=imgRotateAltNm)

    print('\nProcessed images output to the following directory:')
    print(imgRotateAltDir)


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


# // *--------------------------------------------------------------* //
# // *---::ODMKEYE - Image CrossFade Rotate Sequencer::---*')
# // *--------------------------------------------------------------* //


if cntrlEYE == 8:
# *****CURRENT - CHECKIT*****

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMK Image CrossFade Rotate::---*')
    print('// *-----Crossfade & Rotate a sequence of images---*')
    print('// *-----sequence period = framesPerBeat---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outXfadeRotNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outXfadeRotDir = xodEyeDir+eyeOutDir
    os.makedirs(outXfadeRotDir, exist_ok=True)


    # [imgSrcObj, imgSrcObjNm] = importAllJpg(srcXfadeRotDir)

    rotD = 0    # rotation direction: 0=counterclockwise ; 1=clockwise
    framesPerBeat = int(np.ceil(eyeClks.framesPerBeat))
    #xFrames = framesPerBeat

    xFrames = int(ceil(xLength * framesPerSec) / 4)   # 1 fade whole length

    eyeu.odmkImgXfadeRot(imgSrcArray, xLength, framesPerSec, xFrames, outXfadeRotDir, imgOutNm=outXfadeRotNm, rotDirection=rotD)

    #[xfadeRotRepeatA, xfadeRotRepeatNmA] = repeatDir(outXfadeRotDir, 3, w=1, repeatDir=xodEyeDir+'eyeXfadeRotRepeat/', repeatName='eyeXfadeRotR')

    print('\nodmkImgXfadeRot function output => Created python lists:')
    print('<<<xfadeRotOutA>>>   (ndimage objects)')
    print('<<<xfadeRotOutNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(outXfadeRotDir)

    #print('\nrepeatDir function output => Created python lists:')
    #print('<<<xfadeRotRepeatA>>>   (ndimage objects)')
    #print('<<<xfadeRotRepeatNmA>>> (img names)')

    #print('\noutput processed img to the following directory:')
    #print(xodEyeDir+'eyeXfadeRotRepeat')

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //

## *-----BYPASS BEGIN-----*
if cntrlEYE == 9:
## *****CHECKIT*****

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image telescope Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # iterate zoom out & overlay, zoom in & overlay for n frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgTelescNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgTelescOutDir = xodEyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs( imgTelescOutDir, exist_ok=True)


    # num frames per beat (quantized)
    fpb = int(np.ceil(eyeClks.framesPerBeat))
    fps = framesPerSec

    inOrOut = 0     # telescope direction: 0 = in, 1 = out
        

    eyeu.odmkImgTelescope(imgSrcArray, xLength, fps, fpb, imgTelescOutDir, imgOutNm=imgTelescNm, inOut=inOrOut)

    print('Saved Processed images to the following location:')
    print(imgTelescOutDir)
    print('\n')

    print('// *--------------------------------------------------------------* //')



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //

elif cntrlEYE == 12:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - odmkEyeEchoBpm Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # for n frames:
    # randomly select an image from the source dir, hold for n frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgRndBpmNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgRndBpmdir = xodEyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs(imgRndBpmdir, exist_ok=True)

    # generate the downFrames sequence:
    eyeDFrames = eyeClks.clkDownFrames()
    
    numECHOES = 16
    stepECHOES = 5          # 1 or greater
    decayECHOES = 'None'

    # final video length in seconds
    numFrames = int(np.ceil(xLength * framesPerSec))

    # [eyeECHO_Bpm_Out, eyeECHO_Bpm_Nm] =  odmkEyeEchoBpm(imgSrcArray, numFrames, eyeDFrames, numECHOES, stepECHOES, imgRndBpmdir, echoDecay = decayECHOES, imgOutNm=imgRndBpmNm)
    eyeu.odmkEyeEchoBpm(imgSrcArray, numFrames, eyeDFrames, numECHOES, stepECHOES, imgRndBpmdir, echoDecay = decayECHOES, imgOutNm=imgRndBpmNm)
    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


if cntrlEYE == 22:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Pixel Random Replace::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outPxlRndRepNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outPxlRndRepDir = xodEyeDir+eyeOutDir
    os.makedirs(outPxlRndRepDir, exist_ok=True)


    sLength = xLength

    
    eyeu.odmkPxlRndReplace(imgSrcArray, sLength, framesPerSec, outPxlRndRepDir,
                           imgOutNm=outPxlRndRepNm)


    print('\noutput processed img to the following directory:')
    print(outPxlRndRepDir)


    print('// *--------------------------------------------------------------* //')
    

if cntrlEYE == 222:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Pixel Random Rotate::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outPxlRndRotNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outPxlRndRotDir = xodEyeDir+eyeOutDir
    os.makedirs(outPxlRndRotDir, exist_ok=True)


    sLength = xLength

    
    eyeu.odmkPxlRndRotate(imgSrcArray, sLength, framesPerSec, framesPerBeat,
                          outPxlRndRotDir, imgOutNm=outPxlRndRotNm)


    print('\noutput processed img to the following directory:')
    print(outPxlRndRotDir)


    print('// *--------------------------------------------------------------* //')


if cntrlEYE == 23:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE LFO Modulated Parascope f::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    lfoParascopeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    lfoParascopeDir = xodEyeDir+eyeOutDir
    os.makedirs(lfoParascopeDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength

    inOrOut = 0     # telescope direction: 0 = in, 1 = out
    
    eyeu.odmkLfoParascope(imgSrcArray, sLength, framesPerSec, xfadeFrames,
                          lfoParascopeDir, imgOutNm=lfoParascopeNm, inOrOut=inOrOut)

    print('\nProcessed images output to the following directory:')
    print(lfoParascopeDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(xodEyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')
    
    
if cntrlEYE == 233:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE odmkLfoParascopeII::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxLfoParascopeIINm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxLfoParascopeIIDir = xodEyeDir+eyeOutDir
    os.makedirs(fxLfoParascopeIIDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()


    eyeu.odmkLfoParascopeII(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                            fxLfoParascopeIIDir, imgOutNm=fxLfoParascopeIINm)

    print('\nProcessed images output to the following directory:')
    print(fxLfoParascopeIIDir)


    print('// *--------------------------------------------------------------* //')    

if cntrlEYE == 234:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE odmkLfoParascopeII::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxLfoParascopeIINm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxLfoParascopeIIDir = xodEyeDir+eyeOutDir
    os.makedirs(fxLfoParascopeIIDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()


    eyeu.odmkLfoParascopeIII(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                             fxLfoParascopeIIDir, imgOutNm=fxLfoParascopeIINm)

    print('\nProcessed images output to the following directory:')
    print(fxLfoParascopeIIDir)


    print('// *--------------------------------------------------------------* //')


if cntrlEYE == 24:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Bananasloth Recursive f::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    bSlothRecursNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    bSlothRecursDir = xodEyeDir+eyeOutDir
    os.makedirs(bSlothRecursDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength

    #inOrOut = 1     # telescope direction: 0 = in, 1 = out

    eyeu.odmkBSlothRecurs(imgSrcArray, sLength, framesPerSec, xfadeFrames,
                          bSlothRecursDir, imgOutNm=bSlothRecursNm)

    print('\nProcessed images output to the following directory:')
    print(bSlothRecursDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(xodEyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')




if cntrlEYE == 'xodMskDualV':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE xodMskDualESP ::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    xodMskDualESPNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    xodMskDualESPDir = eyeOutDir
    os.makedirs(xodMskDualESPDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength
    
    inOut = 2       # 0: telescope out, 1: telescope in, 2: random per xfade

    sLength = xLength
    
    #pdb.set_trace()


    eyev.xodMskDualV(imgSeqArray, maskArray, sLength, framesPerSec, xfadeFrames,
                       n_digits, xodMskDualESPDir, imgOutNm=xodMskDualESPNm,
                       effx=effxSel, inOrOut=inOut)

    print('\nProcessed images output to the following directory:')
    print(xodMskDualESPDir)


    print('// *--------------------------------------------------------------* //')
    
# // *********************************************************************** //
# // *********************************************************************** //
    
   
   
if cntrlEYE == 627:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE VideoGoreXXZ01::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = xodEyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxVideoGoreNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxVideoGoreDir = xodEyeDir+eyeOutDir
    os.makedirs(fxVideoGoreDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()

    #inOrOut = 1     # telescope direction: 0 = in, 1 = out

    eyev.odmkVideoGoreXXZ01(imgSeqArray, sLength, framesPerSec, xfadeFrames,
                            fxVideoGoreDir, imgOutNm=fxVideoGoreNm)

    print('\nProcessed images output to the following directory:')
    print(fxVideoGoreDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(xodEyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')



# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : img post-processing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


if postProcess == 1:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::Repeat All images in SRC Directory::---*')
    print('// *--------------------------------------------------------------* //')
    # repeatAllImg - operates on directory
    # renames and repeats all images in the srcDir in alternating reverse order
    # n=1 -> reversed, n=2 -> repeat, n=3 -> reversed, ...
    n=1

    # srcDir defined above - source image directory
    repeatSrcDir = xodEyeDir+srcDir

    # eyeOutFileName = 'myOutputFileName'    # defined above
    repeatNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    repeatDir = xodEyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs(eyeutil.repeatRevDir, exist_ok=True)

    eyeutil.repeatAllImg(srcDir, n, w=1, repeatDir=repeatDir, repeatName=repeatNm)


elif postProcess == 2:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::Repeat Reverse All images in SRC Directory::---*')
    print('// *--------------------------------------------------------------* //')
    # repeatReverseAllImg - operates on directory
    # renames and repeats all images in the srcDir in alternating reverse order
    # n=1 -> reversed, n=2 -> repeat, n=3 -> reversed, ...
    n=1

    # srcDir defined above - source image directory
    repeatSrcDir = xodEyeDir+srcDir

    # eyeOutFileName = 'myOutputFileName'    # defined above
    repeatRevNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    repeatRevDir = xodEyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs( repeatRevDir, exist_ok=True)


    eyeutil.repeatReverseAllImg(repeatSrcDir, n, w=1, repeatReverseDir=repeatRevDir,
                                repeatReverseName=repeatRevNm)



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


elif postProcess == 4:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - mirrorHV4 list of files in directory::---*')
    print('// *--------------------------------------------------------------* //')


    srcDir = xodEyeDir+mirrorHV4SrcDir   
    
    mirrorHV4Nm = mirrorHV4ReName
    
    mirrorHV4Dir = xodEyeDir+mirrorHV4OutDir
    os.makedirs(mirrorHV4Dir, exist_ok=True)
    
    outSzX = 1920
    outSzY = 1080
    
    ctrlQuadrant = ctrlQ

    
    eyeu.mirrorHV4AllImg(srcDir, outSzX, outSzY, mirrorHV4Dir, mirrorHV4Nm, ctrl=ctrlQuadrant)    
    print('\nOutput all images to: '+mirrorHV4Dir)
    
    print('// *--------------------------------------------------------------* //')




# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


elif postProcess == 5:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - mirrorTemporalHV4 list of files in directory::---*')
    print('// *--------------------------------------------------------------* //')


    srcDir = xodEyeDir+mirrorTemporalHV4SrcDir   
    
    mirrorTemporalHV4Nm = mirrorTemporalHV4ReName
    
    mirrorTemporalHV4Dir = xodEyeDir+mirrorTemporalHV4OutDir
    os.makedirs(mirrorTemporalHV4Dir, exist_ok=True)
    
    outSzX = 1920
    outSzY = 1080
    
    ctrlQuadrant = ctrlQ
    frameDly = ctrlDly

    
    eyeu.mirrorTemporalHV4AllImg(srcDir, outSzX, outSzY, mirrorTemporalHV4Dir, mirrorTemporalHV4Nm, frameDly, ctrl=ctrlQuadrant)    
    print('\nOutput all images to: '+mirrorTemporalHV4Dir)
    
    print('// *--------------------------------------------------------------* //')



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


elif postProcess == 7:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - imgXfadeDir interlace files in directories::---*')
    print('// *--------------------------------------------------------------* //')


    srcDir1 = xodEyeDir+imgXfadeSrcDir1
    srcDir2 = xodEyeDir+imgXfadeSrcDir2
    
    XfadeNm = imgXfadeReName
    
    imgXfadeDir = xodEyeDir+imgXfadeOutDir
    os.makedirs(imgXfadeDir, exist_ok=True)


    # get length from shortest img dir
    imgFileList1 = []
    imgFileList2 = []
    
    if imgFormat=='fjpg':
        imgFileList1.extend(sorted(glob.glob(srcDir1+'*.jpg')))
        imgFileList2.extend(sorted(glob.glob(srcDir2+'*.jpg')))    
    elif imgFormat=='fbmp':
        imgFileList1.extend(sorted(glob.glob(srcDir1+'*.bmp')))
        imgFileList2.extend(sorted(glob.glob(srcDir2+'*.bmp')))     

    imgCount = 2*min(len(imgFileList1), len(imgFileList2))

    tbWavGen = wavGen.odmkWavGen1(imgCount, fs)


    secondsPerBeat = eyeClks.spb


    pwmOutFreq = 20000*secondsPerBeat
    pwmCtrlFreq = 1000*secondsPerBeat
    phaseInc = pwmOutFreq/fs

    pulseWidthCtrl = 0.5*tbWavGen.monosin(pwmCtrlFreq) + 0.5

    pwmOut = np.zeros([imgCount])

    for i in range(imgCount):
        pwmOut[i] = tbWavGen.pulseWidthMod(phaseInc, pulseWidthCtrl[i])

    eyeu.imgXfadeDir(srcDir1, srcDir2, pwmOut, imgXfadeDir, reName=XfadeNm)    
    print('\nOutput all images to: '+imgXfadeDir)
    
    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


# *----- RENDER VIDEO BEGIN -----*

if cntrlRender == 1:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::XODMKEYE - Render Video::---*')
    print('// *--------------------------------------------------------------* //')

    if numDigits == 0:
        nDigits = n_digits
    else:
        nDigits = numDigits

    #pdb.set_trace()

    eyemv = xodffm.xodFFmpeg(framesPerSec) 
    eyemv(nDigits, earSrc, eyeSrcMvDir, eyeOutMvDir)


# *----- RENDER VIDEO END -----*

# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# end : img post-processing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::done::---*')
print('// *--------------------------------------------------------------* //')


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# Notes:
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


## image division blend algorithm..
#c = a/((b.astype('float')+1)/256)
## saturating function - if c[m,n] > 255, set to 255:
#d = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
#
#eyeDivMixFull = outXfadeDir+'eyeDivMix.jpg'
#misc.imsave(eyeDivMixFull, d)

# ***End: division blend ALT algorithm***


# ***
# convert from Image image to Numpy array:
# arr = array(img)

# convert from Numpy array to Image image:
# img = Image.fromarray(array)


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# Experimental:
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# *** Add sound clip synched to each pixelbang itr
# *** add complete soundtrack synched to frame-rate

# create util func to reverse numbering of img

# *** randomly select pixelbang algorithm for each itr
# ***define 'channels' interleaved pixelbang algorithms of varying duration


# randome pixel replacement from img1 to img2
# -replace x% of pixels randomly each frame, replaced pixels pulled out of pool
# -for next random selection to choose from until all pixels replaced

# 2D wave eqn modulation
# modulate colors/light or modulate between two images ( > 50% new image pixel)

# 2D wave modulation iterating zoom

# trails, zoom overlay interpolation...

# fractal pixel replace - mandelbrot set algorithm

# random pixel replace through rotating image set - image is rotated by
# randomly replacing pixels while skipping through bounded sliding window of
# incrementally rotated windows

# sliding probability window -> for vector of length n, randomly choose values
# bounded by a sliding window (goal is to evolve through a list of img)

# // *---------------------------------------------------------------------* //