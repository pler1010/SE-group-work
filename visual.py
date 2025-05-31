from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction
from visual_detect.main_detect import detect_fatigue, video_convert2_images

def detect_visual(video):
    video_convert2_images(video, r'./visual_detect/images/run/{}.jpg')
    info = detect_fatigue(r'./visual_detect/run/1', r'./visual_detect/images/run_result')
    return info