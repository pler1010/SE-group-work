from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction
from gesture_detect.gesture_handler import detect_gesture_from_filelike
def detect_gesture(video):
    '''
    需要做的事情：
    把video中2.5、7.5、12.5（2.5+5n）位置的图像取出来，并且识别对应位置的手势，同时记录日志。
    '''
    '''
    返回值：
    手势有且只有以下几种类型
    none（没有识别到手势）
    up（向上）
    left（向左）
    right（向右）
    fist（握拳）
    palm（手张开/摆手）
    thumb（大拇指，点赞手势，确认警告）
    '''
<<<<<<< HEAD
    # 已按照注释内容实现
    return detect_gesture_from_filelike(video)
=======
    res = detect_gesture_from_filelike(video)
    print(res)
    return res
>>>>>>> 67613f0 (Complete the final modifications and upload the complete code)
