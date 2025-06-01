#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import copy
import csv
import cv2 as cv
import numpy as np
import mediapipe as mp

from model import KeyPointClassifier

# 初始化 Mediapipe 组件
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 配置路径
VIDEO_PATH = 'gesture_detect/video/test.mp4'
SAVE_ROOT = 'gesture_detect/img'
LOCAL_DIR = os.path.join(SAVE_ROOT, 'local')
EXTERNAL_DIR = os.path.join(SAVE_ROOT, 'external')
os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(EXTERNAL_DIR, exist_ok=True)

FRAME_INTERVAL_SEC = 5.0
START_TIME_SEC = 2.5


def run_gesture_detection(cap, save_dir):
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    keypoint_classifier = KeyPointClassifier()

    with open('gesture_detect/model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
        keypoint_classifier_labels = [row[0] for row in csv.reader(f)]

    fps = cap.get(cv.CAP_PROP_FPS)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    results_list = []
    log_lines = []

    current_time = START_TIME_SEC
    frame_idx = 0

    while current_time * fps < total_frames:
        cap.set(cv.CAP_PROP_POS_MSEC, current_time * 1000)
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv.flip(frame, 1)
        debug_image = copy.deepcopy(frame)

        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        label = "None"
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                pre_processed = pre_process_landmark(landmark_list)
                hand_sign_id = keypoint_classifier(pre_processed)
                label = keypoint_classifier_labels[hand_sign_id]

                mp_drawing.draw_landmarks(debug_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 保存图像与日志
        raw_path = os.path.join(save_dir, f'frame_{frame_idx}_raw.jpg')
        annotated_path = os.path.join(save_dir, f'frame_{frame_idx}_label_{label}.jpg')
        cv.imwrite(raw_path, frame)
        cv.imwrite(annotated_path, debug_image)

        results_list.append(label)
        log_line = f'Time: {current_time:.1f}s, Label: {label}'
        log_lines.append(log_line)
        print(log_line)

        current_time += FRAME_INTERVAL_SEC
        frame_idx += 1

    cap.release()

    # 保存日志
    with open(os.path.join(save_dir, 'log.txt'), 'w', encoding='utf-8') as f:
        for line in log_lines:
            f.write(line + '\n')

    return results_list


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    return [[int(landmark.x * image_width), int(landmark.y * image_height)] for landmark in landmarks.landmark]


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
    base_x, base_y = temp_landmark_list[0]
    for i in range(len(temp_landmark_list)):
        temp_landmark_list[i][0] -= base_x
        temp_landmark_list[i][1] -= base_y
    flat_list = list(np.array(temp_landmark_list).flatten())
    max_value = max(map(abs, flat_list)) or 1
    return [x / max_value for x in flat_list]


# 本地视频处理
def main():
    cap = cv.VideoCapture(VIDEO_PATH)
    results = run_gesture_detection(cap, LOCAL_DIR)
    print("识别结果数组：", results)


# 外部调用接口：传入 file-like 对象（如 Flask 的 request.files['video']）
def detect_gesture_from_filelike(video_file):
    # 转为 OpenCV 可读取的 VideoCapture
    temp_video_path = os.path.join(EXTERNAL_DIR, 'temp_input.mp4')
    with open(temp_video_path, 'wb') as f:
        f.write(video_file.read())

    cap = cv.VideoCapture(temp_video_path)
    results = run_gesture_detection(cap, EXTERNAL_DIR)

    return results


if __name__ == '__main__':
    main()
