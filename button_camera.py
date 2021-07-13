#!/usr/bin/env python3
# -*- coding: utf-8 -*-:q

import picamera
import picamera.array
import numpy as np
from time import sleep

def capture_raw(bayer=False, type=16, outpath=None, preview_time=5):
    '''
    Capturing Raw Image
    This function works only with pi (noir) camera version 2

    Parameters
    ----------
    bayer : boolean default False
        If True, returns Bayer (before-demosaic) image. Otherwise returns demosaiced image.
    outpath : str default None
        If not None, save result in the path.
    type : str default "uint8"
        uint8 or uint16. If uint8, convert results to np.uint8. If uint16, return 10bit data (as np.uint16).
    preview_time : int default 5
        Preview time in seconds
    '''
    with picamera.PiCamera() as camera:
        if preview_time > 0:
            camera.start_preview()
            sleep(preview_time)
            camera.stop_preview()
        with picamera.array.PiBayerArray(camera) as stream:
            camera.capture(stream, 'jpeg', bayer=True)
            # Demosaic data and write to output (just use stream.array if you
            # want to skip the demosaic step)
            if bayer:
                out = stream.array
                if type == "uint8":
                    out = (out >> 2).astype(np.uint8)
            else:
                out = stream.demosaic()
                if type == "uint8":
                    out = (out >> 2).astype(np.uint8)
            if outpath != None:
                with open(outpath, 'wb') as f:
                    out.tofile(f)
            return out

import argparse
from time import sleep
import datetime as dt
from RPi import GPIO
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='argparse sample.')
    # Basic arguments
    parser.add_argument("-o", "--out", type=str, \
        help="Output directory", required=True)
    parser.add_argument("-g", "--gpio", type=int, \
        help="GPIO number connected to the shutter bottun", \
            required=True)
    # Optional arguments
    parser.add_argument("-b", "--bayer", action="store_true", \
        default=False, help="Return Bayer array (Default: Return demosaiced array)")
    parser.add_argument("-t", "--type", type=str, default="uint8", \
        help="Data type of the result. uint8 or uint16. If uint16, 10bit raw data will returned as np.uint16 array.")
    parser.add_argument("-p", "--preview", type=int, default=0, \
        help="Preview time in seconds. If 0, preview will not be activated.")
    
    args = parser.parse_args()

    GPIO.setmode(GPIO.BCM) # GPIO番号で指定
    GPIO.setup(args.gpio, GPIO.IN) # GPIO 27にボタンの出力をつなぐ
    while True:
        if GPIO.input(args.gpio) == GPIO.HIGH:
            now = dt.datetime.now()
            now = now.strftime("%Y%m%d_%H%M_%S")
            # save the audio frames as .wav file
            out_path = args.out + "/" + now + ".data"
            out_image_path = args.out + "/" + now + ".png"
            out = capture_raw(bayer=args.bayer, type=args.type, preview_time=args.preview, outpath=out_path)
            cv2.imwrite(out_image_path, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
            print("Finished capturing. Wrote " + out_path)
            sleep(2)
        else:
            sleep(2)
