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
    ''' # Python ffmpeg video generator
        --earSrc: path to .wav file
        --eyeSrc: path to img frame folder
        --xLength: length of output video/audio file
        --framesPerSec: video frames per second
        >>tbFFmpeg = eyeInst.xodFFmpeg('myWavPath', 'myImgSrcPath', 93)
    '''

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

        #self.eyeDir = rootDir+'eye/eyeSrc/'
        #os.makedirs(self.eyeDir, exist_ok=True)
        
        
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
                if self.imgFormat=='fjpg':        
                    if filename.endswith('.jpg'):
                        imgSrcList.append(filename)
                elif self.imgFormat=='fbmp':
                    if filename.endswith('.bmp'):
                        imgSrcList.append(filename)
        
        
            if imgSrcList == []:
                print('\nError: No .jpg files found in directory\n')
                return
            else:
                imgCount = len(imgSrcList)
                print('\nFound '+str(imgCount)+' images in the eyeSrcDir directory!')
                if mvName=='auto':
                    eye_name = imgSrcList[0]
                    eye_name = eye_name.split("00")[0]
                else:
                    eye_name = mvName
                #print('\nSet eye_name = "'+eye_name+'"')
        except OSError:
            print('\nError: directory:\n'+eyeSrcDir+'\ncannot be found\n')

        # // *-------------------------------------------------------------* //

        if self.imgFormat=='fjpg':
            self.fmt_str = eye_name+'%'+str(n_digits)+'d.jpg'
        elif self.imgFormat=='fbmp':   
            self.fmt_str = eye_name+'%'+str(n_digits)+'d.bmp'
        print('\nfmt_str... '+self.fmt_str)
        src_name = os.path.join(eyeSrcDir, self.fmt_str)
        
        
        #movie_name = eye_name+'.mpg'
        movie_name = os.path.join(mvDir, eye_name+'.mp4')
        print('\nMovie output path = '+mvDir)
        print('\nSet movie_name = '+eye_name+'.mp4')
        print('\nRunning ffmpeg... ')

        
        #movie_cmd = ["ffmpeg",
        #             '-an',  # no sound!
        #             '-r',  '%d' % frame_rate,
        #             '-i', os.path.join(eyeSrcDir, fmt_str),
        #             '-y' if overwrite else '-n',
        #             # '-vcodec', codec,
        #             '-b:v', bitrate,
        #             movie_name]
                     
        #movie_cmd = ["ffmpeg",
        #             '-r',  '%d' % frame_rate,
        #             '-i', os.path.join(eyeSrcDir, fmt_str),
        #             '-i', earSrc,
        #             '-shortest',
        #             '-y' if overwrite else '-n',
        #             # '-vcodec', codec,
        #             '-b:v', bitrate,
        #             movie_name]
        
        
        #ffmpeg -i input -c:v libx264 -preset slow -crf 22 -c:a copy output.mkv
        #ffmpeg -i input -c:v libx265 -preset medium -crf 28 -c:a aac -b:a 128k output.mp4
        movie_cmd = ["ffmpeg",
                     #'-i', os.path.join(eyeSrcDir, self.fmt_str),
                     '-i', src_name,
                     '-i', earSrc,
                     '-c:v', 'libx264',
                     #'-c:a aac',
                     #'-b:a 3500k',
                     '-preset', 'medium',
                     '-crf', '15',
                     '-r', '%d' % self.framesPerSec,
                     #'-r', '30',
                     '-shortest',
                     '-fflags', '+shortest',
                     #'-max_interleave_delta', '500M',
                     '-y' if self.overwrite else '-n',
                     movie_name]
        
        #check_call(movie_cmd)
        
        print("ffmpeg cmd: %s" % movie_cmd)
        rc = check_call(movie_cmd)
        if rc:
            raise Exception("ffmpeg failed")




        # /////////////////////////////////////////////////////////////////////
        # #####################################################################
        # end : eye generator - ffmpeg function calls
        # #####################################################################
        # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


        print('\n')
        print('// *------------------------------------------------------* //')
        print('// *---::done::---*')
        print('// *------------------------------------------------------* //')
        
        


# // *---------------------------------------------------------------------* //


# video frame-grabbing
# ffmpeg -i file.mp4 -r 1/1 $filename%06d.jpg
#ffmpeg -i test.mov -ss 00:00:09 -t 00:00:03 $filename%06d.jpg


#ffmpeg -i inputMov.whatever -ss starttime -t duration outputMov.whatever
#ffmpeg -i test.mov -ss 00:00:09 -t 00:00:03 test-out.mov

# example:
# ffmpeg -i olly2017.mp4 -ss 00:02:03 -t 00:00:27 moshOlly%06d.bmp



# mp3 encoding
# ffmpeg -i oto.wav -ab 320k -f mp3 newfile.mp3

# flac encoding
# ffmpeg -i oto.wav newfile.flac


# Extracting audio from video (MOV)
# ffmpeg -i IMG_0141.MOV -vn -acodec copy IMG_0141_audio.mp4

# ** note, ffmpeg -i my_video.MOV(.AVI) 
# - above will just show format details of input source file



# Create Music Video with Still image for -t seconds
#ffmpeg -loop 1 -i subnoxious13300563.jpg -i fangorela.wav -t 00:03:45 -c:v libx264 -r 30 -pix_fmt yuv420p fangorela.mp4


# *** verify needed ***
# create music video with n frame per second..

#ffmpeg -loop 1 -i image.jpg -i carbonprimate2019radio.wav -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest out.mp4

#ffmpeg -framerate 24 -i Project%03d.png Project.mp4


#ffmpeg -framerate 1 -pattern_type glob -i '*.png' \
#  -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4



#Caption length text: 2,200 characters Max
#Video aspect ratio: Landscape (1.91:1), Square (1:1), Vertical (4:5)
#Minimum resolution: 600 x 315 pixels (1.91:1 landscape) / 600 x 600 pixels (1:1 square) / 600 x 750 pixels (4:5 vertical)
#Minimum length: No minimum
#Maximum length: 60 seconds
#File type: Full list of supported file formats
#Supported video codecs: H.264, VP8
#Supported audio codecs: AAC, Vorbis
#Maximum size: 4GB
#Frame rate: 30fps max


# cropping a video
#ffmpeg -i in.mp4 -filter:v "crop=out_w:out_h:x:y" out.mp4

#out_w is the width of the output rectangle
#out_h is the height of the output rectangle
#x and y specify the top left corner of the output rectangle


# scaling video

#ffmpeg scaling all images in folder
# *** assumes ffmpeg installed in bash shell

#for f in *.png; do ffmpeg -i "$f" -vf scale=1200:900 "../another-folder/${f%%.png}.png"; done


# Twitter Video Resolution
# Maximum resolution: 1920 x 1200 (and 1200 x 1900)
# Aspect ratios: 1:2.39 - 2.39:1 range (inclusive)



