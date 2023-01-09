# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((xodEYEdata.py))::__
#
# Python XODMK img processing data basic
# Contains Dictionary definitions, Algorithm Names
# definitions for xodEYEctrl.py
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os

# bpm = 186            # 93 - 186 - 372
# bpm = 408            # 68 - 136 - 272 - 544 - (408)
# bpm = 93          # 66.5 - 99.75 - 133 - 199.5 - 266 - 399 - 532

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
            "RenameAll"         : 'xodRenameAll',
            "ResizeAll"         : 'xodResizeAll',
            "CropAll"           : 'xodCropAll',
            "ConcatAllDir"      : 'xodConcatAllDir',
            "FrameIntpLin"      : 'xodFrameIntpLin',    # ctrl 0: start[0], start[rndoffset]
            "FrameIntpCos"      : 'xodFrameIntpCos',    # ctrl 0: start[0], start[rndoffset]
            "FrameIntpStride"   : 'xodStrideIntp',
            "MirrorLR"          : 'xodMirrorLR',
            "ImgRndSel"         : 'xodImgRndSel',
            "ImgRotateSeq"      : 'xodImgRotateSeq',
            "XfadeTelescopeI"   : 'xodXfadeTelescopeI',
            "XfadeTelescopeII"  : 'xodXfadeTelescopeII',
            "InterlaceDir"      : 'imgInterlaceDir',
            "InterLaceBpmDir"   : 'imgInterLaceBpmDir',
            "JPGtoBMP"          : 'convJPGtoBMP',
            "BMPtoJPG"          : 'convBMPtoJPG',
        }

# __xodEYEu__
# 'xodFxSlothCult'       =>  [effx: 0, 1]
# 'xodFxSlothCultII'     =>  [effx: 0, 1]
# 'xodLfoParascope'      =>  FIXIT
# 'xodPxlRndRotate'      =>  FIXIT Sub-Box replace w/ rnd rotation
# 'xodMskLfoParascope'   =>  X img algorithm { lfoDepth<0:100> }
# 'xodMskDualESP'        =>  Dual Channel Mask Telescope [effx: 0, 1, 2, 3, 4]

xodEYEu_dict = {
            "FxSlothCult"       : 'xodFxSlothCult',
            "FxSlothCultII"     : 'xodFxSlothCultII',
            "LfoParascope"      : 'xodLfoParascope',
            "PxlRndRotate"      : 'xodPxlRndRotate',
            "MskLfoParascope"   : 'xodMskLfoParascope',
            "MskDualESP"        : 'xodMskDualESP'
        }

# __xodEYEv__
# 'xodImgLinSel'         =>  EYE Image Linear EFFX Algorithm {ctrl: 0 = start [0], 1 = rand offset}
# 'xodLinEFFX'           =>  EYE Image Linear EFFX Algorithm {ctrlSel: xbeat /  effx: algo (0=rand)}
# 'xodImgXfade'          =>  EYE Image Xfade img1 -> img2
# 'xodBSlothGlitch'      =>  FIXIT
# 'xodBSlothSwitch'      =>  Random Focal Frame Parascope FX
# 'xodVFrameParascope'   =>  FIXIT ???
# 'xodVLfoParascope'     =>  X video algorithm
# 'xodVideoGoreXXZ01'    =>  X video algorithm
# 'xodMskDualV'


xodEYEv_dict = {
            "ImgLinSel"         : 'xodImgLinSel',
            "LinEFFX"           : 'xodLinEFFX',         # effx (effects type): 0 = random ; 1 = fwd/rev ; 2 = solarize ;
                                                        #                      3 = div ; 4 = sobelXY ; 5 sobelZ
            "SegEFFX"           : 'xodSegmentEFFX',     # effx (effects type): 0 = random ; 1 = histSegment ;
                                                        #                      2 = histSegmentCLR
            "AutoSeq"           : 'xodAutoSeq',         # ctrl 0: start[0], start[rndoffset]
            "ChainSeq"          : 'xodChainSeq',
            "ImgXfade"          : 'xodImgXfade',
            "BSlothGlitch"      : 'xodBSlothGlitch',
            "BSlothSwitch"      : 'xodBSlothSwitch',
            "VFrameParascope"   : 'xodVFrameParascope',
            "VLfoParascope"     : 'xodVLfoParascope',
            "VideoGoreXXZ01"    : 'xodVideoGoreXXZ01',
            "MskDualV"          : 'xodMskDualV'
        }


xodLinSQFX_dict = {
            "SQFX01": 'xodLinSQFX_rev',
            "SQFX02": 'xodLinSQFX_crot',
            "SQFX03": 'xodLinSQFX_sobelxy',
            "SQFX04": 'xodLinSQFX_sobelz'
        }


xodExpFX_dict = {
            "SQFX01": 'xodLinSQFX_fwd',
            "SQFX02": 'xodLinSQFX_fwd',
            "SQFX03": 'xodLinSQFX_fwd',
            "SQFX04": 'xodLinSQFX_fwd'
        }


# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



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
# 5  => Concatenate all img in directory list       ::concatAllDir::
# 6  => 4-quadrant img mirror                       ::mirrorHV4AllImg::
# 7  => 4-quadrant temporal dly img mirror          ::mirrorTemporalHV4AllImg::
# 8  => interlace 2 directories

# // *********************************************************************** //

# // *********************************************************************** //
# // *********************************************************************** //

# MOV SRC RAW
#sourceDir = ['xodmkMvSrc/enterTheeDragon/enterTheeDragon_makerOvWorldsI/']


#sourceDir = ['1920x1080/wizardOvMirror/wizardOvMirror_xodLolthTankIIILin7/',
#             '1920x1080/wizardOvMirror/wizardOvMirror_cthulhuDeathRayLin5/']


#sourceDir = ['1920x1080/mizuguanaCn16_II/mzgnaCII_astralCryptMeatIIx1080/',
#             '1920x1080/mizuguanaCn16_II/mzgnaCII_xodLolthTankIIIx1080/',
#             '1920x1080/enterTheeDragon/enterTheeDragon_hardNeuralDemon1080/',
#             '1920x1080/enterTheeDragon/enterTheeDragon_neurohedral1080/',
#             '1920x1080/hardNeuralMizuguanaMx/']


#sourceDir = ['1920x1080/enterTheeDragon/enterTheeDragon_neurohedral1080/',
#             '1920x1080/enterTheeDragon/enterTheeDragon_hardNeuralDemon1080/',
#             '1920x1080/enterTheeDragon/enterTheeDragon_makerOvWorldsI1080/',
#             '1920x1080/enterTheeDragon/enterTheeDragon_makerOvWorldsILin3/',
#             '1920x1080/enterTheeDragon/enterTheeDragon_mescalEater1080/']


#sourceDir = ['1920x1080/ckeyInageMantra/ckeyInageMantra_astralCryptMeat1080/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_cthulhuDeathRay1080/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_xodLolthTank1080/',

#sourceDir = ['1920x1080/ckeyInageMantra/ckeyInageMantra_astralCryptMeatLin3/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_cthulhuDeathRayLin3/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_xodLolthTankLin3/']

#sourceDir = ['1920x1080/suspiriaEsp/suspiriaExp_medicineManLin3/',
#             '1920x1080/suspiriaEsp/suspiriaExp_mescalEaterLin3/',
#             '1920x1080/suspiriaEsp/suspiriaExp_mescalEaterLin5/',
#             '1920x1080/suspiriaEsp/suspiriaExp_neurohedralLin3/']

#sourceDir = ['1920x1080/redSamuraiESP/redSamurai_acidsharkLin5/',
#             '1920x1080/redSamuraiESP/redSamurai_eyespyeyeLin5/',
#             '1920x1080/redSamuraiESP/redSamurai_metasphynxKoiLin5/',
#             '1920x1080/redSamuraiESP/redSamurai_witchForestIILin5/',
#             '1920x1080/redSamuraiESP/redSamurai_wormQueenIILin5/',]


#sourceDir = ['1920x1080/redSamuraiESP/redSamurai_acidsharkLin5/',
#             '1920x1080/redSamuraiESP/redSamurai_eyespyeyeLin5/',
#             '1920x1080/redSamuraiESP/redSamurai_metasphynxKoiLin5/',
#             '1920x1080/redSamuraiESP/redSamurai_witchForestIILin5/',
#             '1920x1080/redSamuraiESP/redSamurai_wormQueenIILin5/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_astralCryptMeatLin3/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_cthulhuDeathRayLin3/',
#             '1920x1080/ckeyInageMantra/ckeyInageMantra_xodLolthTankLin3/',
#             '1920x1080/shamanDanceExp/shamanD_gholaILin3/',
#             '1920x1080/shamanDanceExp/shamanD_hardNeuralIguanaLin3/',
#             '1920x1080/humanEyeESP/humanEyeESP_pinealResonator1080/',
#             '1920x1080/suspiriaEsp/suspiriaExp_medicineManLin3/',
#             '1920x1080/suspiriaEsp/suspiriaExp_mescalEaterLin3/',
#             '1920x1080/suspiriaEsp/suspiriaExp_mescalEaterLin5/',
#             '1920x1080/suspiriaEsp/suspiriaExp_neurohedralLin3/']