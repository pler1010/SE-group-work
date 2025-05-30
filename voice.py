from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction

def detect_gesture(video):
    '''
    需要做的事情：
    把0-5s，5-10s，10-15s...的语音转为文字，同时记录日志
    '''
    '''
    返回值，一个列表，包好每段语音对应的文字：
    '''