from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction
from visual_detect.main_detect import detect_fatigue_from_video_cap

def detect_visual(video):
    info = detect_fatigue_from_video_cap(video)
    return info