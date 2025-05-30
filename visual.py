from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction

def detect_visual(video):
    '''
    需要做的事情：
    把video中2.5、7.5、12.5（2.5+5n）位置的图像取出来，并且识别对应位置的神态，同时记录日志。
    '''
    '''
    返回值，一个列表：
    神态有且只有以下几种类型
    none（没有明显异常）
    wander（用户走神了）
    tired（用户有困意）
    sleepy（用户快睡着了）
    '''