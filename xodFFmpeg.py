# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

# __::((xodFFmpeg.py))::__

# Python ODMK img processing research
# ffmpeg experimental

# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os
#from math import ceil
#import numpy as np

# from subprocess import check_output, check_call
from subprocess import check_call


# temp python debugger - use >>>pdb.set_trace() to set break
#import pdb


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class xodFFmpeg:
    """ # Python ffmpeg video generator
        --earSrc: path to .wav file
        --eyeSrc: path to img frame folder
        --xLength: length of output video/audio file
        --framesPerSec: video frames per second
        >>tbFFmpeg = eyeInst.xodFFmpeg('myWavPath', 'myImgSrcPath', 93)
    """

    def __init__(self, framesPerSec=30.0):

        # *---set primary parameters from inputs---*
        self.xLength = 0
        
        self.imgFormat = 'fjpg'    # imgFormat => { fbmp, fjpg }

        self.framesPerSec = framesPerSec
        
        self.overwrite = True
        self.n_interpolation_frames = 1
        self.frame_rate = 30
        self.bitrate = '5000k'
        self.codec = 'h264'

    def __call__(self, n_digits, earSrc, eyeSrcDir, mvDir, mvName='auto'):
        
        # // *-------------------------------------------------------------* //
        # // *---::Search for .jpg images in eyeSrcDir directory::---*')
        # // *-------------------------------------------------------------* //

        os.makedirs(mvDir, exist_ok=True)

        # generate list all files in a directory
        imgSrcList = []
        
        try:
            print('\nFFmpeg Source Directory: '+eyeSrcDir)
            for filename in os.listdir(eyeSrcDir):
                if self.imgFormat == 'fjpg':
                    if filename.endswith('.jpg'):
                        imgSrcList.append(filename)
                elif self.imgFormat == 'fbmp':
                    if filename.endswith('.bmp'):
                        imgSrcList.append(filename)

            if not imgSrcList:
                print('\nError: No .jpg files found in directory\n')
                return
            else:
                imgCount = len(imgSrcList)
                print('\nFound '+str(imgCount)+' images in the eyeSrcDir directory!')
                if mvName == 'auto':
                    eye_name = imgSrcList[0]
                    eye_name = eye_name.split("00")[0]
                else:
                    eye_name = mvName
                # print('\nSet eye_name = "'+eye_name+'"')
        except OSError:
            print('\nError: directory:\n'+eyeSrcDir+'\ncannot be found\n')

        # // *-------------------------------------------------------------* //

        if self.imgFormat == 'fjpg':
            self.fmt_str = eye_name+'%'+str(n_digits)+'d.jpg'
        elif self.imgFormat == 'fbmp':
            self.fmt_str = eye_name+'%'+str(n_digits)+'d.bmp'
        print('\nfmt_str... '+self.fmt_str)
        src_name = os.path.join(eyeSrcDir, self.fmt_str)
        movie_name = os.path.join(mvDir, eye_name+'.mp4')
        print('\nMovie output path = '+mvDir)
        print('\nSet movie_name = '+eye_name+'.mp4')
        print('\nRunning ffmpeg... ')

        # movie_cmd = ["ffmpeg",
        #             '-r',  '%d' % frame_rate,
        #             '-i', os.path.join(eyeSrcDir, fmt_str),
        #             '-i', earSrc,
        #             '-shortest',
        #             '-y' if overwrite else '-n',
        #             # '-vcodec', codec,
        #             '-b:v', bitrate,
        #             movie_name]

        # ffmpeg -i input -c:v libx265 -preset medium -crf 28 -c:a aac -b:a 128k output.mp4

        # # *** works ***
        # movie_cmd = ["ffmpeg",
        #              # '-framerate', 30
        #              '-framerate', '%d' % self.framesPerSec,
        #              '-i', src_name,
        #              '-i', earSrc,
        #              '-c:v', 'libx264',
        #              # '-c:a aac',
        #              # '-b:a 256k',
        #              '-preset', 'medium',
        #              '-crf', '15',
        #              '-r', '%d' % self.framesPerSec,
        #              #'-r', '30',
        #              #'-shortest',
        #              #'-fflags', '+shortest',
        #              #'-max_interleave_delta', '500M',
        #              '-y' if self.overwrite else '-n',
        #              movie_name]

        # *** experimental ?? ***
        # ffmpeg -i input_file -c:v libx264 -profile:v baseline -level:v 3.0 -c:a aac -b:a 128k output.mp4
        movie_cmd = ["ffmpeg",
                     '-i', src_name,
                     '-i', earSrc,
                     '-c:v', 'libx264',
                     '-c:a', 'aac',
                     '-b:a', '256k',
                     '-profile:v', 'baseline',
                     '-level:v', '3.0',
                     '-r', '%d' % self.framesPerSec,
                     '-shortest',
                     # '-max_interleave_delta', '500M',
                     '-y' if self.overwrite else '-n',
                     movie_name]

        print("ffmpeg cmd: %s" % movie_cmd)
        rc = check_call(movie_cmd)
        if rc:
            raise Exception("ffmpeg failed")

        # /////////////////////////////////////////////////////////////////////
        # #####################################################################
        # end : eye generator - ffmpeg function calls
        # #####################################################################
        # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
