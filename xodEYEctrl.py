# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header begin-----------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEYEctrl.py))::__
#
# Python ODMK img processing research testbench
# testbench for odmkEYEuObj.py
# ffmpeg experimental
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header end-------------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os, sys
from math import ceil
import glob
#import shutil
#import random
import numpy as np
#import scipy as sp
import imageio as imio
#from scipy import misc
#from scipy import ndimage
import soundfile as sf

# from PIL import Image
# from PIL import ImageOps
# from PIL import ImageEnhance

rootDir = 'C:/XODMK/xodmkCode/xodmkPython/'


# temp python debugger - use >>> pdb.set_trace() to set break
import pdb


#rootDir = '../'
#audioScrDir = '../audio/wavsrc/'
#audioOutDir = '../audio/wavout/'


sys.path.insert(0, rootDir+'eye/')
import xodEYEutil as eyeutil
import xodEYEu as xodeyeu
import xodEYEv as xodeyev
import xodFFmpeg as xodffm
#import xodEYEx as xodeyex


sys.path.insert(1, rootDir+'DSP/')
import xodClocks as clks
import xodWavGen as wavGen


sys.path.insert(2, rootDir+'audio/xodma/')
#from xodmaAudioTools import load_wav
#from xodmaAudioTools import fix_length#, samples_to_time, time_to_samples
#from xodmaOnset import onset_strength, get_peak_regions

import xodmaAudioTools as xodaudio



#sys.path.insert(3, rootDir+'audio\\spectralTools')
#from odmkSpectralTools import amplitude_to_db, stft, istft, peak_pick
#from odmkSpectralTools import phase_vocoder, magphase
#from odmkSpectralUtil import frames_to_time
#from odmkSpectralPlot import specshow



print('// //////////////////////////////////////////////////////////////// //')
print('// *--------------------------------------------------------------* //')
print('// *---:: XODMK EYE ESP ::---*')
print('// *--------------------------------------------------------------* //')
print('// \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ //')



# /////////////////////////////////////////////////////////////////////////////
# *--- Begin: USER INTERFACE --*
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# *-- Set img/video file source --*
eyeDir = rootDir+'eye/eyeSrc/'

audioScrDir = 'C:/XODMK/xodmkCode/xodmkPython/audio/wavsrc/'
audioOutDir = 'C:/XODMK/xodmkCode/xodmkPython/audio/wavout/'


# // *---:: Select Program Control ::---*')

# __xodEYEutil-Preprocess__
# 'xodResizeAll'         =>  [ctrl: 0: SzX/SzY, 1: keepAspect height, 2: width
# 'xodCropAll'           =>  Crop to dimensions SzX/SzY, high: 0 center, 1 top
# 'concatAllDir'

# __xodEYEutil__
# 'xodFrameIntpLin'      =>  Linear XFade series of images in directory [ctrl: (int) xFadeFrames]
# 'xodFrameIntpCos'      =>  XCosFade series of images in directory [ctrl: (int) xFadeFrames]
# 'xodMirrorLR'          =>  Left/Right Mirror [ctrlSel: 0, 1]
# 'xodMirrorQuad'        =>  Quad Mirror [ctrlSel: 0, 1]
# 'xodImgRndSel'         =>  EYE Random Select Algorithm
# 'xodImgRotateSeq'      =>  EYE Image Rotate Sequence Algorithm
# 'xodXfadeTelescopeI'   =>  EYE Image Xfade telescope Algorithm I
# 'xodXfadeTelescopeII'  =>  EYE Image Xfade telescope Algorithm II
# 'imgInterlaceDir'      =>  EYE interlace two directories
# 'imgInterLaceBpmDir'   =>  EYE BPM synched interlace two directories

xodEYEutil_dict = {
            "eyeutil01": 'xodResizeAll',
            "eyeutil02": 'xodCropAll',
            "eyeutil03": 'concatAllDir',
            "eyeutil04": 'xodFrameIntpLin',
            "eyeutil05": 'xodFrameIntpCos',
            "eyeutil06": 'xodMirrorLR',
            "eyeutil07": 'xodImgRndSel',
            "eyeutil08": 'xodImgRotateSeq',
            "eyeutil09": 'xodXfadeTelescopeI',
            "eyeutil10": 'xodXfadeTelescopeII',
            "eyeutil11": 'imgInterlaceDir',
            "eyeutil12": 'imgInterLaceBpmDir'
        }

# __xodEYEu__
# 'xodFxSlothCult'       =>  [effx: 0, 1]
# 'xodFxSlothCultII'     =>  [effx: 0, 1]
# 'xodLfoParascope'      =>  FIXIT
# 'xodPxlRndRotate'      =>  FIXIT Sub-Box replace w/ rnd rotation
# 'xodMskLfoParascope'   =>  X img algorithm { lfoDepth<0:100> }
# 'xodMskDualESP'        =>  Dual Channel Mask Telescope [effx: 0, 1, 2, 3, 4]

xodEYEu_dict = {
            "eyeu01": 'xodFxSlothCult',
            "eyeu02": 'xodFxSlothCultII',
            "eyeu03": 'xodLfoParascope',
            "eyeu04": 'xodPxlRndRotate',
            "eyeu05": 'xodMskLfoParascope',
            "eyeu06": 'xodMskDualESP'
        }

# __xodEYEv__
# 'xodImgLinSel'         =>  EYE Image Linear EFFX Algorithm
# 'xodLinEFFX'           =>  EYE Image Linear EFFX Algorithm
# 'xodImgXfade'          =>  EYE Image Xfade img1 -> img2
# 'xodBSlothGlitch'      =>  FIXIT
# 'xodBSlothSwitch'      =>  Random Focal Frame Parascope FX
# 'xodVFrameParascope'   =>  FIXIT ???
# 'xodVLfoParascope'     =>  X video algorithm
# 'xodVideoGoreXXZ01'    =>  X video algorithm
# 'xodMskDualV'

# cntrlRender = 0 / 1    => 0: no video, 1: generate video 

xodEYEv_dict = {
            "eyev01": 'xodImgLinSel',
            "eyev02": 'xodLinEFFX',
            "eyev03": 'xodImgXfade',
            "eyev04": 'xodBSlothGlitch',
            "eyev05": 'xodBSlothSwitch',
            "eyev06": 'xodVFrameParascope',
            "eyev07": 'xodVLfoParascope',
            "eyev08": 'xodVideoGoreXXZ01',
            "eyev09": 'xodMskDualV'
        }





preProcess = 0
srcSequence = 0                     # 0: imgSeqArray (single dir), > 0 sequence
#cntrlEYE = xodEYEutil_dict["eyeutil04"]
cntrlEYE = xodEYEv_dict["eyev01"]
#cntrlEYE = 0
effxSel = 0
ctrlSel = 4
postProcess = 0
cntrlRender = 1



print('\n// *--------------------------------------------------------------* //')
print('// *---:: Set processing directories ::---*')
print('// *--------------------------------------------------------------* //')

# *---------------------------------------------------------------------------*
# *-- Set wav file source --*

#earSrcNm = 'gorgulans_beatx01.wav'         # ~7  sec = 220 frames
#earSrcNm = 'antimatterbk06.wav'            # ~14 sec = 434 frames
#earSrcNm = 'dmttv-axon23.wav'               # ~23
#earSrcNm = 'cabalisk_abstract.wav'         # ~53
earSrcNm = 'cabalisk_spaced.wav'            # ~1.49



earSrcDir = audioScrDir
earSrc = earSrcDir+earSrcNm


# *---------------------------------------------------------------------------*
# *---------------------------------------------------------------------------*

# GFX
#sourceDir = ['8018x/xodsolomon8018x/']

# MOV SRC RAW
#sourceDir = ['xodmkMvSrc/asatoLifeBallX2/']
#sourceDir = ['xodmkMvSrc/returnToOzUnlockHeadCrypt_neuralIguana/']


# MOV GEN
#sourceDir = ['1920x1080/asatoLifeBallX2/']
#sourceDir = ['1920x1080/hardNeuralDragon1080/']
sourceDir = ['1920x1080/returnToOzUnlockHeadCrypt_neuralIguanaxLin4/']


#sourceDir = ['testout/skullFromTheVoid_x0_1x/', 'testout/skullFromTheVoid_x0_2x/']
#             'testout/skullOffering_x2x/', 'testout/skullOffering_x3x/',
#             'testout/skullOffering_x4x/', 'testout/skullOffering_x5_1x/',
#             'testout/skullOffering_x5_2x/', 'testout/skullOffering_x5_3x/',
#             'testout/skullOffering_x6x/']
    

#outDir = 'testout/cgbwCryptWitch8018/'
#outDir = '1920x1080/returnToOzUnlockHeadCrypt_neuralIguanaxLin4/'
outDir = 'testout/vexpTest/'



outBaseName = 'unlockHeadCrypt_neuralIguanaxLin4_'
  

# *---------------------------------------------------------------------------*
    
#maskDir = eyeDir + '1560x/mask1560/'
maskDir = eyeDir + '8018x/mask8018x/'
    
# *---------------------------------------------------------------------------*
    
if cntrlRender==1:
    
    mvDir = 'testout/vexpTestx_mv/'    # output movie directory
    
    eyeOutMvDir = eyeDir+mvDir
    
    # number of digits before image file extension, required by ffmpeg..
    # numDigits: 0 = Auto (n_digits from length of .wav -> numFrames)
    # numDigits: # = explixit #
    numDigits = 0

# *---------------------------------------------------------------------------*
# *---------------------------------------------------------------------------*


# *-- wavlength: processing length (seconds) ---------------------*

# 0   => full length of input .wav file
# ### => usr defined length in SECONDS

wavlength = 0
#wavlength = 56

#fs = 48000.0        # audio sample rate:
framesPerSec = 30 # video frames per second:

#bpm = 186            # 93 - 186 - 372
#bpm = 408            # 68 - 136 - 272 - 544 - (408)
#bpm = 93          # 66.5 - 99.75 - 133 - 199.5 - 266 - 399 - 532
bpm = 133
timeSig = 4         # time signature: 4 = 4/4; 3 = 3/4

# set format of source img { fjpg, fbmp }
imgFormat = 'fjpg'


# HD Standard video aspect ratio

SzX = 1920
SzY = 1080

#SzX = 1920
#SzY = 1280

# B4
#SzX = 4299
#SzY = 3035

#SzX = 3508
#SzY = 3508

#SzX = 1560
#SzY = 1560

#SzX = 1080
#SzY = 1080

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


eyeOutFileName = outBaseName
eyeOutDir = eyeDir+outDir
os.makedirs(eyeOutDir, exist_ok=True)  # If Dir does not exist, makedir


# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


print('\n// *--------------------------------------------------------------* //')
print('// *---:: User Parameters ::---*')
print('// *--------------------------------------------------------------* //')


print('\nCTRL Pre-Process = '+str(preProcess))
print('CTRL Src-Sequence  = '+str(srcSequence))
print('CTRL Eye-Algorithm = '+str(cntrlEYE))
print('CTRL Post-Process  = '+str(postProcess))
print('CTRL Render Video  = '+str(cntrlRender))


firstSourceDir = eyeDir+sourceDir[0]
print('\nImg Source Directory (first if array):\n'+firstSourceDir+'\n')
print('Img Output Directory:\n'+eyeOutDir+'\n')
if cntrlRender==1:
    print('Movie Output Directory:\n'+eyeOutMvDir+'\n')
print('Wav Source Directory:\n'+earSrc+'\n')


print('\nXodEYE bpm: --------------------------- '+str(bpm))
print('XodEYE timeSig: ----------------------- '+str(timeSig)+'/4')
print('XodEYE Img Format: -------------------- '+imgFormat)
print('XodEYE Img Dimensions [X, Y]: --------- '+str(SzX)+' x '+str(SzY))


# /////////////////////////////////////////////////////////////////////////////
# *--- End: USER INTERFACE --*
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        

# /////////////////////////////////////////////////////////////////////////////
# *---Begin MAIN: Select top-level switches--*
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# <<< img array sequencing function Select >>>
# *---------------------------------------------------------------------------*
# 0  => Bypass
# 1  => 1 directory of frames

# <<< Pixel Banging Algorithm Select >>>
# *---------------------------------------------------------------------------*

# ### - EYE BASIC (odmkEYEu) - ###
# *** operates on batch of numFrames img - used as sub-process ***

# "xodeyeu.odmkImgLinSel"    =>  EYE Linear Select Algorithm 
# "xodeyeu.odmkImgRndSel"    =>  EYE Random Select Algorithm
# "xodeyeu.odmkImgRotateSeq  =>  EYE Image Rotate Sequence Algorithm




# <<< Pixel Banging Algorithm Select >>>
# *---------------------------------------------------------------------------*


# 101  => EYE Rotate Linear Select Algorithm     ::odmkImgRotLinSel::
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
# 222 => EYE Pixel Random Rotate Algorithm       ::odmkPxlRndRotate::
# 23 => EYE LFO Modulated Parascope Algorithm    ::odmkLfoParascope::
# 233 => EYE LFO Modulated Parascope Algorithm   ::odmkLfoParascopeII::
# 234 => EYE LFO Modulated Parascope Algorithm   ::odmkLfoParascopeIII::
# 24 => EYE Bananasloth Recursive Algorithm      ::odmkBSlothRecurs::
# 25 => EYE Bananasloth Glitch 1                 ::odmkBSlothGlitch1::
# 26 => EYE Bananasloth Glitch 2                 ::odmkBSlothGlitch2::
# 27 => EYE Bananasloth Glitch 3                 ::odmkBSlothGlitch3::

# 202  => EYE RanSel LFO Algorithm                 ::odmkImgRndSel::

# 623 => EYE FxSlothCultLife Glitch 1            ::odmkFxSlothCult1::

# 626 => EYE FxSlothCultLife Glitch 1            ::odmkFxSlothCult1::

# 627 => EYE Video VideoGoreXXZ01                ::odmkVideoGoreXXZ01::

# 628 => EYE Video


# *--------------------------...






# ### - IMG Manipulation Algorithms (odmkVIDEOu) - ###
# *** operates on batch of numFrames img - used as sub-process ***

# 14  => EYE Random Select Telescope Algorithm    ::**nofunc**::
# 16  => EYE Rotate & alternate sequence          ::**nofunc**::
# 17  => EYE CrossFade Sequencer (alpha-blend)    ::odmkImgXfade::
# 18  => EYE CrossFade Sequencer (solarize)       ::odmkImgSolXfade::


# ### - Pixel Banging Algorithms (odmkVIDEOu) - ###
# *** Full video output ***

# 7   => EYE Divide CrossFade Sequencer           ::odmkImgDivXfade::
# 8   => EYE CrossFade Rotate sequence            ::odmkImgXfadeRot::
# 9   => EYE telescope sequence                   ::odmkImgTelescope::
# 10  => EYE CrossFade telescope Sequence         ::odmkImgXfadeTelescope::
# 11  => EYE Div Xfade telescope Sequence         ::odmkImgDivXfadeTelescope::
# 12  => Eye Echo BPM Sequencer                   ::odmkEyeEchoBpm::
# 20  => EYE Color Enhance BPM Algorithm          ::odmkImgColorEnhance::
# 21  => EYE Color Enhance Telescope Algorithm    ::odmkImgCEnTelescope::
# 22  => EYE Pixel Random Replace Algorithm       ::odmkPxlRndReplace::
# 222 => EYE Pixel Random Rotate Algorithm        ::odmkPxlRndRotate::
# 23  => EYE LFO Modulated Parascope Algorithm    ::odmkLfoParascope::
# 233 => EYE LFO Modulated Parascope Algorithm    ::odmkLfoParascopeII::
# 234 => EYE LFO Modulated Parascope Algorithm    ::odmkLfoParascopeIII::
# 24  => EYE Bananasloth Recursive Algorithm      ::odmkBSlothRecurs::
# 25  => EYE Bananasloth Glitch 1                 ::odmkBSlothGlitch1::
# 26  => EYE Bananasloth Glitch 2                 ::odmkBSlothGlitch2::
# 27  => EYE Bananasloth Glitch 3                 ::odmkBSlothGlitch3::




# TEMP - FIXIT - EXP

# 623 => EYE FxSlothCultLife Glitch 1            ::odmkFxSlothCult1::
# 626 => EYE FxSlothCultLife Glitch 1            ::odmkFxSlothCult1::
# 627 => EYE Video VideoGoreXXZ01                ::odmkVideoGoreXXZ01::
# 628 => EYE Video 
# *--------------------------...

    
 
    
# <<< Pre/Post Processing Function Select >>>
# *---------------------------------------------------------------------------*
# 0  => Bypass
# 1  => renameAll                                   ::renameAll::
# 2  => scale all img in dir                        ::odmkScaleAll::
# 3  => convert .jpg img to .bmp                    ::convertJPGtoBMP::
# 4  => convert .bmp img to .jpg                    ::convertToJPG::
# 5  => Concatenate all img in directory list       ::concatAllDir::
# 6  => 4-quadrant img mirror                       ::mirrorHV4AllImg::
# 7  => 4-quadrant temporal dly img mirror          ::mirrorTemporalHV4AllImg::
# 8  => interlace 2 directories



# <<< src sequencing >>>
# *---------------------------------------------------------------------------*
# 0  => Bypass
# 1  => seq1EXP                                    ::?::
# 2  => seq2EXP                                    ::?::
    
    

# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


print('\n// *--------------------------------------------------------------* //')
print('// *---:: Load .wav file ::---*')
print('// *--------------------------------------------------------------* //')


    
[wavSrc, numChannels, fs, xLength, xSamples] = xodaudio.load_wav(earSrc, wavlength)
print('\nLoaded .wav file [ '+earSrc+' ]\n')



if numChannels == 2:
    wavSrc_ch1 = wavSrc[:,0];
    wavSrc_ch2 = wavSrc[:,1];
else:
    wavSrc_ch1 = wavSrc;
    wavSrc_ch2 = 0;



# length of input signal - '0' => length of input .wav file
print('Channel A Source Audio:') 
print('wavSrc Channels: --------------------- '+str(len(np.shape(wavSrc))))
print('length of input signal in seconds: --- '+str(xLength))
print('length of input signal in samples: --- '+str(xSamples))
print('audio sample rate: ------------------- '+str(fs))
print('wav file datatype: ------------------- '+str(sf.info(earSrc).subtype))

period = 1.0 / fs

    
# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


print('\n// *--------------------------------------------------------------* //')
print('// *---::Instantiate objects::---*')
print('// *--------------------------------------------------------------* //')


eyeClks = clks.xodClocks(xLength, fs, bpm, framesPerSec)
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


if preProcess == 3:

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


if preProcess == 4:

    print('\n// *--------------------------------------------------------------* //')
    print('// *---::Convert All images in SRC Directory to jpg::---*')
    print('// *--------------------------------------------------------------* //')
    

    # define output directory for scaled img
    # Dir path must end with backslash /
    os.makedirs(eyeOutDir, exist_ok=True)  
    
    eyeutil.convertBMPtoJPG(srcDir, eyeOutDir, reName=eyeOutFileName)


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
    
    

maskArray = sorted(glob.glob(maskDir+'*'))

    
if srcSequence == 0:

    #imgSeqArray = sorted(glob.glob(srcDir+'*'))   
    srcDir = []
    imgSeqArray = []
    for d in range(len(sourceDir)):
        sDirTmp = eyeDir+sourceDir[d]
        srcDir.append(sDirTmp)
        sortedDir = sorted(glob.glob(sDirTmp+'*'))
        for s in sortedDir:
            imgSeqArray.append(s.replace('\\', '/'))
            
        #pdb.set_trace()

        
        
#if srcSequence == 0:
#
#    #imgSeqArray = sorted(glob.glob(srcDir+'*'))   
#    srcDir = []
#    imgSeqArray = []
#    for d in range(len(sourceDir)):
#        sDirTmp = eyeDir+sourceDir[d]
#        srcDir.append(sDirTmp)
#        imgSeqArray.extend(sorted(glob.glob(sDirTmp+'*')))

    
if srcSequence == 1:
    
    print('\n// *--------------------------------------------------------------* //')
    print('// *---::ODMKVIDEO - SRC-SEQ - LFO video scanner ::---*')
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
        srcDir = eyeDir + sourceDir[0]
    
    resizeNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    resizedir = eyeOutDir

    reSzX = SzX
    reSzY = SzY
    
    if ctrlSel == 1:
        aspectCtrl='height'
    elif ctrlSel == 2:
        aspectCtrl='width'
    else:
        aspectCtrl='None'
    
    
    eyeutil.xodResizeAll(srcDir, reSzX, reSzY, resizedir, imgOutNm=resizeNm, keepAspect=aspectCtrl)

    
    print('Saved Rezized images to the following location:')
    print(eyeOutDir)
    print('\n')
    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 'xodCropAll':
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')

    srcDir = eyeDir + sourceDir[0]
    
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
    
if cntrlEYE == 'concatAllDir':


    concatOutDir = eyeOutDir
    os.makedirs(concatOutDir, exist_ok=True)
    
    # *** names must be different from source ***
    concatOutName = eyeOutFileName
    
    srcDir = []
    imgSeqArray = []
    for d in range(len(sourceDir)):
        sDirTmp = eyeDir+sourceDir[d]
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
        srcDir = eyeDir + sourceDir[0]
    
    xodFrameINm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    xodFrameIdir = eyeOutDir
    
    #xfadeFrames = framesPerBeat
    xfadeFrames = ctrlSel
    effx = 0

    eyeutil.xodFrameInterpolate(imgSeqArray, xfadeFrames, effx, n_digits,
                                xodFrameIdir, xodFrameINm)

    print('\nOutput all images to: ' + xodFrameIdir)
    
    print('// *--------------------------------------------------------------* //')
    

if cntrlEYE == 'xodFrameIntpCos':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - xodFrameInterpolate Cosine xFade ::---*')
    print('// *--------------------------------------------------------------* //')
    
    if len(sourceDir) > 1:
        print('sourceDir contains more than one directory')
    else:
        srcDir = eyeDir + sourceDir[0]
    
    xodFrameINm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    xodFrameIdir = eyeOutDir
    
    #xfadeFrames = framesPerBeat
    xfadeFrames = ctrlSel
    effx = 1

    eyeutil.xodFrameInterpolate(imgSeqArray, xfadeFrames, effx, n_digits,
                                xodFrameIdir, xodFrameINm)

    print('\nOutput all images to: ' + xodFrameIdir)
    
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

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat))
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

    #inOrOut = 1     # telescope direction: 0 = in, 1 = out

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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxMskLfoParascopeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxMskLfoParascopeDir = eyeOutDir
    os.makedirs(fxMskLfoParascopeDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength
    
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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
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
    

    eyev.xodImgLinSel(imgSeqArray, xLength, framesPerSec, n_digits, eyeOutDir, eyeOutFileName)
    
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
    
    
    #xFrames = int(np.ceil(eyeClks.framesPerBeat))
    #xFrames = int(np.ceil(eyeClks.framesPerBeat) / 3)
    xFrames = int(np.ceil(eyeClks.framesPerBeat)) * 3
    
    #pdb.set_trace()
    
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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
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


    srcDir1 = eyeDir+imgInterlaceSrcDir1
    srcDir2 = eyeDir+imgInterlaceSrcDir2
    
    interlaceNm = imgInterlaceReName
    
    imgInterlaceDir = eyeDir+imgInterlaceOutDir
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


    srcDir1 = eyeDir+imgInterlaceSrcDir1
    srcDir2 = eyeDir+imgInterlaceSrcDir2
    
    interlaceNm = imgInterlaceReName
    
    imgInterlaceBpmDir = eyeDir + imgInterlaceOutDir
    os.makedirs(imgInterlaceBpmDir, exist_ok=True)
    
    
    xfadeFrames = framesPerBeat

    
    eyeutil.imgInterLaceBpmDir(srcDir1, srcDir2, imgInterlaceBpmDir, xfadeFrames,
                               reName=interlaceNm)
    
    print('\nOutput all images to: ' + imgInterlaceBpmDir)
    
    print('// *--------------------------------------------------------------* //')
    

    
    
    
    
# // *********************************************************************** //



if cntrlEYE == 101:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Linear Solarize Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # for n frames:
    # randomly select an image from the source dir, hold for h frames

    # eyeOutFileName = 'myOutputFileName'    # defined above
    imgLinSolNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    imgLinSoldir = eyeDir+eyeOutDir
    os.makedirs(imgLinSoldir, exist_ok=True)  # If Dir does not exist, makedir
    
    xfadeFrames = int(np.ceil(eyeClks.framesPerBeat))

    eyeu.odmkImgLinSol(imgSeqArray, numFrames, xfadeFrames, imgLinSoldir, imgOutNm=imgLinSolNm)

    print('\nodmkImgRndSel function output => Created python lists:')
    print('<<<imgRndSelOutA>>>   (ndimage objects)')
    print('<<<imgRndSelNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(imgLinSoldir)

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
    imgLinSeldir = eyeDir+eyeOutDir
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
    imgRndBpmdir = eyeDir+eyeOutDir
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
    imgTelescRnddir = eyeDir+eyeOutDir
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


# *-----BYPASS BEGIN-----*

# *****CHECKIT*****

elif cntrlEYE == 4:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::Output a sequence of rotates images::---*')
    print('// *-----360 deg rotation period = numFrames-----*')
    print('// *--------------------------------------------------------------* //')

    # num_gz = 192
    numFrames = 111
    # zn = cyclicZn(numFrames) -- called in func
    
    rotD = 0    # rotation direction: 0=counterclockwise ; 1=clockwise

    imgSrc = processScaledArray[9]

    outDir = eyeDir+'imgRotateOut/'
    os.makedirs(outDir, exist_ok=True)
    outNm = 'imgRotate'

    eyeu.odmkImgRotateSeq(imgSrc, numFrames, outDir, imgOutNm=outNm, rotDirection=rotD)


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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    imgRotateAltNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    imgRotateAltDir = eyeDir+eyeOutDir
    os.makedirs(imgRotateAltDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()

    imgSrcArray = []
    imgSrcArray.extend(sorted(glob.glob(imgSeqArray+'*')))

    eyeu.odmkImgRotateAlt(imgSrcArray, sLength, framesPerSec, xfadeFrames, imgRotateAltDir, imgOutNm=imgRotateAltNm)

    print('\nProcessed images output to the following directory:')
    print(imgRotateAltDir)


# *****FUNCTIONALIZEIT*****

#elif cntrlEYE == 5:
#
#    # dir where processed img files are stored:
#    gzdir = 'C:/usr/eschei/odmkPython/odmk/eye/imgSrc/exp1/'
#
#    eye_name = 'odmkRotFlash1'
#
#    # num_gz = 192
#    num_gz = 256
#    zn = cyclicZn(num_gz)
#
#    gz1NmArray = []
#    gz1Array = []
#
#    nextInc = 0
#    for i in range(num_gz):
#        zr = ''
#        ang = (atan2(zn[i].imag, zn[i].real))*180/np.pi
#        if ((i % 4) == 1 or (i % 4) == 2):
#            rotate_gz1 = ndimage.rotate(gz1, ang, reshape=False)
#        else:
#            rotate_gz1 = ndimage.rotate(gzRESIZEx02, ang, reshape=False)
#        nextInc += 1
#        # Find num digits required to represent max index
#        n_digits = int(ceil(np.log10(num_gz))) + 2
#        for j in range(n_digits - len(str(nextInc))):
#            zr += '0'
#        strInc = zr+str(nextInc)
#        gz1Nm = gzdir+eye_name+strInc+'.jpg'
#         .imsave(gz1Nm, rotate_gz1)
#        gz1NmArray.append(gz1Nm)
#        gz1Array.append(rotate_gz1)


# // *********************************************************************** //



#if cntrlEYE == 'xodImgXfade':
#
#    print('\n')
#    print('// *--------------------------------------------------------------* //')
#    print('// *---::ODMK Image CrossFade Sequencer::---*')
#    print('// *---Crossfade a sequence of images, period = framesPerBeat---*')
#    print('// *--------------------------------------------------------------* //')
#
#    outXfadeNm = eyeOutFileName
#    outXfadeDir = eyeOutDir
#    os.makedirs(outXfadeDir, exist_ok=True)
#
#    xfadeFrames = int(np.ceil(eyeClks.framesPerBeat))
#    #xfadeFrames = 4
#    sLength = xLength
#    
#    eyeu.xodImgXfade(imgSeqArray, sLength, framesPerSec, xfadeFrames, n_digits,
#                     outXfadeDir, imgOutNm=outXfadeNm)
#
#    print('\nProcessed images output to the following directory:')
#    print(outXfadeDir)
#
#    print('// *--------------------------------------------------------------* //')
    
    


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


# *****CHECKIT*****
if cntrlEYE == 666:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMK Image CrossFade Sequencer::---*')
    print('// *---Crossfade a sequence of images, period = framesPerBeat---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outXfadeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outXfadeDir = eyeDir+eyeOutDir
    os.makedirs(outXfadeDir, exist_ok=True)

    xfadeFrames = 2*int(np.ceil(eyeClks.framesPerBeat))

    eyeu.odmkImgXfadeAll(imgSrcArray, xfadeFrames, outXfadeDir, imgOutNm=outXfadeNm)

    print('\nodmkImgDivXfade function output => Created python lists:')
    print('<<<xfadeOutA>>>   (ndimage objects)')
    print('<<<xfadeOutNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(outXfadeDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(eyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //

if cntrlEYE == 67:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMK Image Solarize CrossFade Sequencer::---*')
    print('// *---Crossfade a sequence of images, period = framesPerBeat---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outSolXfadeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outSolXfadeDir = eyeDir+eyeOutDir
    os.makedirs(outSolXfadeDir, exist_ok=True)
    
    sLength = xLength

    #framesPerBeat = int(np.ceil(eyeClks.framesPerBeat))

    eyeu.odmkImgSolXfade(imgSrcArray, sLength, framesPerSec, framesPerBeat, outSolXfadeDir, imgOutNm=outSolXfadeNm)

    #[xfadeRepeatA, xfadeRepeatNmA] = repeatDir(outXfadeDir, 3, w=1, repeatDir=eyeDir+'eyeXfadeRepeat/', repeatName='eyeXfadeR')

    print('\nodmkImgSolXfade function output => Created python lists:')
    print('<<<xSolOutA>>>   (ndimage objects)')
    print('<<<xSolOutNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(eyeDir+'outSolXfadeDir')

    print('// *--------------------------------------------------------------* //')


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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outXfadeRotNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outXfadeRotDir = eyeDir+eyeOutDir
    os.makedirs(outXfadeRotDir, exist_ok=True)


    # [imgSrcObj, imgSrcObjNm] = importAllJpg(srcXfadeRotDir)

    rotD = 0    # rotation direction: 0=counterclockwise ; 1=clockwise
    framesPerBeat = int(np.ceil(eyeClks.framesPerBeat))
    #xFrames = framesPerBeat

    xFrames = int(ceil(xLength * framesPerSec) / 4)   # 1 fade whole length

    eyeu.odmkImgXfadeRot(imgSrcArray, xLength, framesPerSec, xFrames, outXfadeRotDir, imgOutNm=outXfadeRotNm, rotDirection=rotD)

    #[xfadeRotRepeatA, xfadeRotRepeatNmA] = repeatDir(outXfadeRotDir, 3, w=1, repeatDir=eyeDir+'eyeXfadeRotRepeat/', repeatName='eyeXfadeRotR')

    print('\nodmkImgXfadeRot function output => Created python lists:')
    print('<<<xfadeRotOutA>>>   (ndimage objects)')
    print('<<<xfadeRotOutNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(outXfadeRotDir)

    #print('\nrepeatDir function output => Created python lists:')
    #print('<<<xfadeRotRepeatA>>>   (ndimage objects)')
    #print('<<<xfadeRotRepeatNmA>>> (img names)')

    #print('\noutput processed img to the following directory:')
    #print(eyeDir+'eyeXfadeRotRepeat')

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
    imgTelescOutDir = eyeDir+eyeOutDir
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

if cntrlEYE == 10:
# *****check v results*****

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Xfade telescope Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # function: odmkImgDivXfadeTelescope
    # iterate zoom out & overlay, zoom in & overlay for n frames

    # loaded images into the following arrays (defined above)

    # jpgSrcDir = eyeDir+'gorgulanScale/'    # pre-scaled img list
    # [processObjList, processSrcList] = importAllJpg(jpgSrcDir)

    # num frames per beat (quantized)
    fpb = 2*int(np.ceil(eyeClks.framesPerBeat))

    inOrOut = 1     # telescope direction: 0 = in, 1 = out

    #eyeOutFileName = 'myOutputFileName'    # defined above
    #imgXfadeTelNm = eyeOutFileName
    # dir where processed img files are stored:
    #eyeOutDir = 'myOutputDirName'    # defined above
    imgXfadeTelOutDir = eyeDir+eyeOutDir
    os.makedirs(imgXfadeTelOutDir, exist_ok=True)
    if inOrOut == 0:
        imgXfadeTelNm = eyeOutFileName+'_telIn'
    else:
        imgXfadeTelNm = eyeOutFileName+'_telOut'

    eyeu.odmkImgXfadeTelescope(processScaledArray, fpb, imgXfadeTelOutDir, inOut=inOrOut, imgOutNm=imgXfadeTelNm)

    print('Saved Processed images to the following location:')
    print(imgXfadeTelOutDir)
    print('\n')

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //

# *-----BYPASS BEGIN-----*
if cntrlEYE == 11:
# *****check v results*****

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - Image Div Xfade telescope Algorithm::---*')
    print('// *--------------------------------------------------------------* //')

    # function: odmkImgDivXfadeTelescope
    # iterate zoom out & overlay, zoom in & overlay for n frames

    # loaded images into the following arrays (defined above)

    # jpgSrcDir = eyeDir+'gorgulanScale/'    # pre-scaled img list
    # [processObjList, processSrcList] = importAllJpg(jpgSrcDir)

    # num frames per beat (quantized)
    fpb = 2*int(np.ceil(eyeClks.framesPerBeat))

    inOrOut = 1     # telescope direction: 0 = in, 1 = out

    # dir where processed img files are stored:
    imgDivXfadeTelOutDir = eyeDir+'odmkDivXfadeTelOut/'
    os.makedirs(imgDivXfadeTelOutDir, exist_ok=True)
    if inOrOut == 0:
        imgDivXfadeTelNm = 'divXfadeTelIn'
    else:
        imgDivXfadeTelNm = 'divXfadeTelOut'

    eyeu.odmkImgDivXfadeTelescope(processScaledArray, fpb, imgDivXfadeTelOutDir, inOut=inOrOut, imgOutNm=imgDivXfadeTelNm)

    print('Saved Processed images to the following location:')
    print(imgDivXfadeTelOutDir)
    print('\n')
    
    print('// *--------------------------------------------------------------* //')    

# *-----BYPASS END-----*

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
    imgRndBpmdir = eyeDir+eyeOutDir
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


if cntrlEYE == 20:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMK Image Color Enhance::---*')
    print('// *---Color Enhance a sequence of images, period = framesPerBeat---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outXfadeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outXfadeDir = eyeDir+eyeOutDir
    os.makedirs(outXfadeDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames    
    sLength = xLength
    
    eyeu.odmkImgColorEnhance(imgSrcArray, sLength, framesPerSec, xfadeFrames, outXfadeDir, imgOutNm=outXfadeNm)

    print('\nodmkImgColorEnhance function output => Created python lists:')
    print('<<<xCEnOutA>>>   (ndimage objects)')
    print('<<<xCEnOutNmA>>> (img names)')

    print('\noutput processed img to the following directory:')
    print(outXfadeDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(eyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')


# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //



if cntrlEYE == 22:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Pixel Random Replace::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outPxlRndRepNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outPxlRndRepDir = eyeDir+eyeOutDir
    os.makedirs(outPxlRndRepDir, exist_ok=True)


    sLength = xLength

    
    eyeu.odmkPxlRndReplace(imgSrcArray, sLength, framesPerSec, outPxlRndRepDir, imgOutNm=outPxlRndRepNm)


    print('\noutput processed img to the following directory:')
    print(outPxlRndRepDir)


    print('// *--------------------------------------------------------------* //')
    

if cntrlEYE == 222:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Pixel Random Rotate::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    outPxlRndRotNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    outPxlRndRotDir = eyeDir+eyeOutDir
    os.makedirs(outPxlRndRotDir, exist_ok=True)


    sLength = xLength

    
    eyeu.odmkPxlRndRotate(imgSrcArray, sLength, framesPerSec, framesPerBeat, outPxlRndRotDir, imgOutNm=outPxlRndRotNm)


    print('\noutput processed img to the following directory:')
    print(outPxlRndRotDir)


    print('// *--------------------------------------------------------------* //')


if cntrlEYE == 23:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE LFO Modulated Parascope f::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    lfoParascopeNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    lfoParascopeDir = eyeDir+eyeOutDir
    os.makedirs(lfoParascopeDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength

    inOrOut = 0     # telescope direction: 0 = in, 1 = out
    
    eyeu.odmkLfoParascope(imgSrcArray, sLength, framesPerSec, xfadeFrames, lfoParascopeDir, imgOutNm=lfoParascopeNm, inOrOut=inOrOut)

    print('\nProcessed images output to the following directory:')
    print(lfoParascopeDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(eyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')
    
    
if cntrlEYE == 233:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE odmkLfoParascopeII::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxLfoParascopeIINm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxLfoParascopeIIDir = eyeDir+eyeOutDir
    os.makedirs(fxLfoParascopeIIDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()


    eyeu.odmkLfoParascopeII(imgSeqArray, sLength, framesPerSec, xfadeFrames, fxLfoParascopeIIDir, imgOutNm=fxLfoParascopeIINm)

    print('\nProcessed images output to the following directory:')
    print(fxLfoParascopeIIDir)


    print('// *--------------------------------------------------------------* //')    

if cntrlEYE == 234:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE odmkLfoParascopeII::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxLfoParascopeIINm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxLfoParascopeIIDir = eyeDir+eyeOutDir
    os.makedirs(fxLfoParascopeIIDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength
    
    #pdb.set_trace()


    eyeu.odmkLfoParascopeIII(imgSeqArray, sLength, framesPerSec, xfadeFrames, fxLfoParascopeIIDir, imgOutNm=fxLfoParascopeIINm)

    print('\nProcessed images output to the following directory:')
    print(fxLfoParascopeIIDir)


    print('// *--------------------------------------------------------------* //')


if cntrlEYE == 24:
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - EYE Bananasloth Recursive f::---*')
    print('// *--------------------------------------------------------------* //')

    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    bSlothRecursNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    bSlothRecursDir = eyeDir+eyeOutDir
    os.makedirs(bSlothRecursDir, exist_ok=True)

    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat / 3)) #2 images for 2 frames
    #xfadeFrames = int(np.ceil(eyeClks.framesPerBeat)) #2 images for 2 frames
    xfadeFrames = framesPerBeat
    #xfadeFrames = xLength

    sLength = xLength

    #inOrOut = 1     # telescope direction: 0 = in, 1 = out

    eyeu.odmkBSlothRecurs(imgSrcArray, sLength, framesPerSec, xfadeFrames, bSlothRecursDir, imgOutNm=bSlothRecursNm)

    print('\nProcessed images output to the following directory:')
    print(bSlothRecursDir)

    # print('\nrepeatDir function output => Created python lists:')
    # print('<<<xfadeRepeatA>>>   (ndimage objects)')
    # print('<<<xfadeRepeatNmA>>> (img names)')

    # print('\noutput processed img to the following directory:')
    # print(eyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')







if cntrlEYE == 'xodMskDualV':
    
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---:: XODMKEYE - EYE xodMskDualESP ::---*')
    print('// *--------------------------------------------------------------* //')


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
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


    # srcXfadeDir = eyeDir+'eyeSrcExp23/'    # defined above
    #eyeOutFileName = 'myOutputFileName'    # defined above
    fxVideoGoreNm = eyeOutFileName
    #eyeOutDir = 'myOutputDirName'    # defined above
    fxVideoGoreDir = eyeDir+eyeOutDir
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
    # print(eyeDir+'eyeXfadeRepeat')

    print('// *--------------------------------------------------------------* //')







# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : img pre-processing
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


if preProcess == 2:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::Scale All images in SRC Directory::---*')
    print('// *--------------------------------------------------------------* //')

    ctrl = high

    imgSrcArray = eyeDir+scaleSrcDir
    
    sclSzX = SzX
    sclSzY = SzY
    
    # define output directory for scaled img
    # Dir path must end with backslash /
    processScaleDir = eyeDir+scaleOutDirName
    os.makedirs(processScaleDir, exist_ok=True)
    
    # individual file root name
    outNameRoot = scaleFileName    
    

    eyeutil.odmkScaleAll(imgSrcArray, sclSzX, sclSzY, processScaleDir, high=ctrl, outName=outNameRoot)


    print('Saved Scaled images to the following location:')
    print(processScaleDir)
    print('\n')



elif preProcess == 3:

    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::Convert All images in SRC Directory to bmp::---*')
    print('// *--------------------------------------------------------------* //')


    #imgSrcDir = eyeDir+jpgSrcDir
    
    
    # define output directory for scaled img
    # Dir path must end with backslash /
    imgOutDir = eyeDir+bmpOutDirName
    os.makedirs(imgOutDir, exist_ok=True)
    
    # individual file root name
    outNameRoot = bmpOutFileName    
    

    eyeutil.convertJPGtoBMP(imgSrcDir, imgOutDir, reName=outNameRoot)


    print('Saved converted images to the following location:')
    print(imgOutDir)
    print('\n')



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
    repeatSrcDir = eyeDir+srcDir

    # eyeOutFileName = 'myOutputFileName'    # defined above
    repeatNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    repeatDir = eyeDir+eyeOutDir
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
    repeatSrcDir = eyeDir+srcDir

    # eyeOutFileName = 'myOutputFileName'    # defined above
    repeatRevNm = eyeOutFileName
    # output dir where processed img files are stored:
    # eyeOutDir = 'myOutputDirName'    # defined above
    repeatRevDir = eyeDir+eyeOutDir
    # If Dir does not exist, makedir:
    os.makedirs( repeatRevDir, exist_ok=True)


    eyeutil.repeatReverseAllImg(repeatSrcDir, n, w=1, repeatReverseDir=repeatRevDir, repeatReverseName=repeatRevNm)



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


elif postProcess == 3:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::Concatenate all images in directory list::---*')
    print('// *--------------------------------------------------------------* //')

    # ex. defined above: concatDirList = [loc1, loc2, loc3, loc4, loc5, loc6, loc7, loc8]
    dirList = concatDirList
    reName = concatReName
    
    eyeConcatDir = eyeDir+concatOutDir
    os.makedirs(eyeConcatDir, exist_ok=True)
    
    
    eyeutil.concatAllDir(dirList, eyeConcatDir, reName)
    
    print('\nOutput all images to: '+eyeConcatDir)
    
    print('// *--------------------------------------------------------------* //')



# // *********************************************************************** //
# // *********************************************************************** //
# // *********************************************************************** //


elif postProcess == 4:
    print('\n')
    print('// *--------------------------------------------------------------* //')
    print('// *---::ODMKEYE - mirrorHV4 list of files in directory::---*')
    print('// *--------------------------------------------------------------* //')


    srcDir = eyeDir+mirrorHV4SrcDir   
    
    mirrorHV4Nm = mirrorHV4ReName
    
    mirrorHV4Dir = eyeDir+mirrorHV4OutDir
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


    srcDir = eyeDir+mirrorTemporalHV4SrcDir   
    
    mirrorTemporalHV4Nm = mirrorTemporalHV4ReName
    
    mirrorTemporalHV4Dir = eyeDir+mirrorTemporalHV4OutDir
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


    srcDir1 = eyeDir+imgXfadeSrcDir1
    srcDir2 = eyeDir+imgXfadeSrcDir2
    
    XfadeNm = imgXfadeReName
    
    imgXfadeDir = eyeDir+imgXfadeOutDir
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
    print('// *---::ODMKEYE - Render Video::---*')
    print('// *--------------------------------------------------------------* //')

    if numDigits == 0:
        nDigits = n_digits
    else:
        nDigits = numDigits

    eyemv = xodffm.xodFFmpeg(framesPerSec) 
    eyemv(nDigits, earSrc, eyeOutDir, eyeOutMvDir)


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