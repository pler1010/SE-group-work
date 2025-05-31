import cv2
import os
import argparse
import myframe

# 命令行参数解析
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--mode", type=str, default="camera", choices=["camera", "video"],
                help="选择运行模式: camera=摄像头，video=视频文件夹")
ap.add_argument("-a", "--alarm", help="报警音文件路径", default="phone.wav")
ap.add_argument("-v", "--video_path", type=str, default="video",
                help="视频文件夹路径，仅视频模式下使用")
ap.add_argument("-w", "--webcam_index", type=int, default=0,
                help="摄像头索引，仅摄像头模式下使用")
args = ap.parse_args()

ALARM_ON = False

# 初始化全局计数变量
phone_num = 0
drink_num = 0
smok_num = 0

EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3

MAR_THRESH = 0.8
MOUTH_AR_CONSEC_FRAMES = 3

COUNTER = 0
TOTAL = 0
mCOUNTER = 0
mTOTAL = 0
ActionCOUNTER = 0

Roll = 0
Rolleye = 0
Rollmouth = 0

def process_frame(frame):
    global COUNTER, TOTAL, mCOUNTER, mTOTAL, ActionCOUNTER
    global phone_num, drink_num, smok_num
    global ALARM_ON
    global Roll, Rolleye, Rollmouth

    ret, frame = myframe.frametest(frame)
    lab, eye, mouth = ret

    if len(lab) > 0:
        ActionCOUNTER += 1

        for i in lab:
            if i == "phone":
                phone_num += 1
                if phone_num % 20 == 0:
                    print("[警告] 检测到使用手机！请注意驾驶安全！")
                    ALARM_ON = True
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                    phone_num += 20
            elif i == "smoke":
                smok_num += 1
                if smok_num % 20 == 0:
                    print("[警告] 检测到抽烟！请注意驾驶安全！")
                    ALARM_ON = True
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                    smok_num += 20
            elif i == "drink":
                drink_num += 1
                if drink_num % 20 == 0:
                    print("[警告] 检测到喝水！请注意驾驶安全！")
                    ALARM_ON = True
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                    drink_num += 20
            else:
                ALARM_ON = False

        if ActionCOUNTER == 50:
            print("[提示] 目前无分心行为")
            ActionCOUNTER = 0

        # 眨眼判断
        if eye < EYE_AR_THRESH:
            COUNTER += 1
            Rolleye += 1
        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
                print(f"[信息] 眨眼次数: {TOTAL}")
            COUNTER = 0

        # 哈欠判断
        if mouth > MAR_THRESH:
            mCOUNTER += 1
            Rollmouth += 1
        else:
            if mCOUNTER >= MOUTH_AR_CONSEC_FRAMES:
                mTOTAL += 1
                print(f"[信息] 哈欠次数: {mTOTAL}")
            mCOUNTER = 0

        # 疲劳提醒
        if mTOTAL != 0 and mTOTAL % 5 == 0:
            print("[疲劳提醒] 有疲劳风险，注意休息！")
            ALARM_ON = True
            if ActionCOUNTER > 0:
                ActionCOUNTER -= 1
            mTOTAL += 1
        else:
            ALARM_ON = False

        # 疲劳模型计算
        Roll += 1
        if Roll == 40:
            perclos = Rolleye / Roll
            print(f"[疲劳模型] 过去40帧Perclos得分: {perclos:.3f}")
            if 0.12 < perclos < 0.6:
                print("[疲劳状态] 当前处于疲劳驾驶状态！")
                ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
            elif perclos >= 0.6:
                print("[危险状态] 当前处于梦游驾驶状态！")
                ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
            else:
                print("[状态] 当前处于清醒状态")

            # 重置计数
            Roll = 0
            Rolleye = 0
            Rollmouth = 0
            print("[信息] 重新开始疲劳检测循环...")

    else:
        # 无人驾驶状态重置
        TOTAL = 0
        ActionCOUNTER = 0
        mTOTAL = 0
        print("[状态] 无人驾驶状态...")

def run_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print("打开摄像头失败")
        return

    print("摄像头打开成功，开始检测...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("摄像头读取失败")
            break
        process_frame(frame)

    cap.release()
    cv2.destroyAllWindows()

def run_videos(video_folder):
    files = [f for f in os.listdir(video_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if not files:
        print(f"{video_folder} 中没有找到视频文件")
        return

    for filename in files:
        path = os.path.join(video_folder, filename)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"打开视频文件失败: {filename}")
            continue

        print(f"开始处理视频文件: {filename}")
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"视频文件 {filename} 播放完毕")
                break
            process_frame(frame)

        cap.release()

if __name__ == "__main__":
    if args.mode == "camera":
        run_camera(args.webcam_index)
    else:
        run_videos(args.video_path)
