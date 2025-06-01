#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import argparse
import csv
from collections import deque

import cv2 as cv
import numpy as np
import mediapipe as mp

from utils import CvFpsCalc
from model import KeyPointClassifier
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence", type=float, default=0.7)
    parser.add_argument("--min_tracking_confidence", type=float, default=0.5)
    return parser.parse_args()


def main():
    args = get_args()

    try:
        # 摄像头设置
        cap = cv.VideoCapture(args.device)
        if not cap.isOpened():
            print(f"Error: Cannot open camera device {args.device}")
            return 1
        cap.set(cv.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, args.height)

        # Mediapipe Hands 模型
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=args.use_static_image_mode,
            max_num_hands=1,
            min_detection_confidence=args.min_detection_confidence,
            min_tracking_confidence=args.min_tracking_confidence,
        )

        # 手势分类模型
        keypoint_classifier = KeyPointClassifier()

        # 标签加载
        label_path = 'gesture_detect/model/keypoint_classifier/keypoint_classifier_label.csv'
        try:
            with open(label_path, encoding='utf-8-sig') as f:
                keypoint_classifier_labels = [row[0] for row in csv.reader(f)]
        except Exception as e:
            print(f"Error loading label file '{label_path}': {e}")
            return 1

        # FPS计算器
        cvFpsCalc = CvFpsCalc(buffer_len=10)

        while True:
            fps = cvFpsCalc.get()
            key = cv.waitKey(10)
            if key == 27:  # ESC退出
                break

            ret, image = cap.read()
            if not ret:
                print("Error: Cannot read frame from camera")
                break
            image = cv.flip(image, 1)
            debug_image = copy.deepcopy(image)

            # 手部检测
            image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = hands.process(image_rgb)
            image_rgb.flags.writeable = True

            if results.multi_hand_landmarks is not None:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # 关键点处理
                    brect = calc_bounding_rect(debug_image, hand_landmarks)
                    landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                    pre_processed_landmark_list = pre_process_landmark(landmark_list)

                    # 分类预测
                    hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                    if hand_sign_id >= len(keypoint_classifier_labels):
                        print(f"Warning: hand_sign_id {hand_sign_id} out of label list range")
                        label = "Unknown"
                    else:
                        label = keypoint_classifier_labels[hand_sign_id]

                    # 可视化
                    debug_image = draw_bounding_rect(True, debug_image, brect)
                    mp_drawing.draw_landmarks(debug_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    debug_image = draw_info_text(debug_image, brect, handedness, label, "")

            debug_image = draw_info(debug_image, fps)
            cv.imshow('Hand Gesture Recognition', debug_image)

        cap.release()
        cv.destroyAllWindows()
        return 0

    except Exception as e:
        print("Exception occurred in main():", e)
        import traceback
        traceback.print_exc()
        return 1





# 以下函数保持不变或略作简化
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.array(
        [[int(landmark.x * image_width), int(landmark.y * image_height)] for landmark in landmarks.landmark])
    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]


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
    max_value = max(map(abs, flat_list))
    return [x / max_value for x in flat_list]


def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]), (0, 255, 0), 2)
    return image


def draw_landmarks(image, landmark_point):
    for landmark in landmark_point:
        cv.circle(image, tuple(landmark), 3, (255, 255, 255), -1)
        cv.circle(image, tuple(landmark), 1, (0, 0, 0), 1)
    return image


def draw_info_text(image, brect, handedness, hand_sign_text, finger_gesture_text):
    cv.putText(image, f'{hand_sign_text}', (brect[0], brect[1] - 10),
               cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv.LINE_AA)
    return image


def draw_info(image, fps):
    cv.putText(image, f'FPS:{fps:.1f}', (10, 30),
               cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv.LINE_AA)
    return image


if __name__ == '__main__':
    main()
