import os

import cv2
import myframe



# 定义三个变量，分别用来控制识别的结果
phone_num = 0
drink_num = 0
smok_num = 0

# 眼睛闭合判断
EYE_AR_THRESH = 0.2        # 眼睛长宽比
EYE_AR_CONSEC_FRAMES = 3    # 闪烁阈值

#嘴巴开合判断
MAR_THRESH = 0.8           # 打哈欠长宽比
MOUTH_AR_CONSEC_FRAMES = 3  # 闪烁阈值

# 定义检测变量，并初始化
COUNTER = 0                 #眨眼帧计数器
TOTAL = 0                   #眨眼总数
mCOUNTER = 0                #打哈欠帧计数器
mTOTAL = 0                  #打哈欠总数
ActionCOUNTER = 0           #分心行为计数器器

# 疲劳判断变量
Roll = 0                    #整个循环内的帧
Rolleye = 0                 #循环内闭眼帧数
Rollmouth = 0               #循环内打哈欠数


text = []
flag = True

#视频转换为图像
def video_convert2_images(video,convert_image):

    vc = cv2.VideoCapture(video)  # 读入视频文件，命名cv
    n = 1  # 计数

    if vc.isOpened():  # 判断是否正常打开
        rval, frame = vc.read()
    else:
        rval = False


    timeF = 2  # 视频帧计数间隔频率

    i = 0
    while rval:  # 循环读取视频帧
        rval, frame = vc.read()
        if (n % timeF == 0):  # 每隔timeF帧进行存储操作
            i += 1
            print(i)
            cv2.imwrite(convert_image.format(i), frame)  # 存储为图像
        n = n + 1
        # cv2.imshow("1",frame)
        # cv2.waitKey(0)
    vc.release()




#读取文件夹下图像
def read_directory(directory_name):
    array_of_img = []
    # this loop is for read each image in this foder,directory_name is the foder name with images.
    img_name_list = os.listdir(directory_name)
    img_name_list.sort(key=lambda x: int(x[:-4]))  # 将'.jpg'左边的字符转换成整数型进行排序

    for filename in img_name_list:
        #print(filename) #just for test
        if(filename.endswith(".jpg") or filename.endswith(".png")):

            #img is used to store the image data
            img = cv2.imread(directory_name + "/" + filename)
            array_of_img.append(img)
            #print(img)
            # print(array_of_img)
    return array_of_img

def log_info(message):
    global text
    text.append(message)          # 追加到显示列表
    print(message.strip())        # 同时打印到控制台（去掉多余换行）


def show_pic(frame, info=[]):
    global EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES, MAR_THRESH, MOUTH_AR_CONSEC_FRAMES
    global COUNTER, TOTAL, mCOUNTER, mTOTAL, ActionCOUNTER
    global phone_num, drink_num, smok_num
    global ALARM_ON
    global Roll, Rolleye, Rollmouth
    global text, flag



    def log_info(message):
        global text
        text.append(message)
        print(message.strip())

    # 调用检测函数
    ret, frame = myframe.frametest(frame)
    lab, eye, mouth = ret

    if len(lab) > 0:
        current_state = "none"  # 默认清醒状态

        ActionCOUNTER += 1

        # 分心行为检测优先级 phone > smoke > drink
        if "phone" in lab:
            phone_num += 1
            if phone_num % 20 == 0:
                log_info("正在玩手机...\n")
                info.append("phone")
                current_state = "phone"
                if not ALARM_ON:
                    ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
                phone_num += 20

        elif "smoke" in lab:
            smok_num += 1
            if smok_num % 20 == 0:
                log_info("正在抽烟...\n")
                info.append("smoking")
                current_state = "smoke"
                if not ALARM_ON:
                    ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
                smok_num += 20

        elif "drink" in lab:
            drink_num += 1
            if drink_num % 20 == 0:
                log_info("正在喝水...\n")
                info.append("drink")
                current_state = "drink"
                if not ALARM_ON:
                    ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
                drink_num += 20
        else:
            ALARM_ON = False

        # 眨眼判断
        if eye == 0:
            log_info("cant detect eyes")
        elif eye < EYE_AR_THRESH:
            log_info("eyes closing")
            COUNTER += 1
            Rolleye += 1
        else:
            log_info("eyes opening")
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
                log_info("第" + str(TOTAL) + '次眨眼\n')
            COUNTER = 0

        # 哈欠判断
        if mouth == 0:
            log_info("cant detect mouth")
        elif mouth > MAR_THRESH:
            log_info("yawning")
            mCOUNTER += 1
            Rollmouth += 1
        else:
            log_info("not yawn")
            if mCOUNTER >= MOUTH_AR_CONSEC_FRAMES:
                mTOTAL += 1
                log_info("第" + str(mTOTAL) + '次打哈欠\n')
                mCOUNTER = 0
                flag = True

        # 疲劳提醒
        if mTOTAL != 0 and mTOTAL % 5 == 0 and flag:
            log_info("打哈欠已经{}次了，有疲劳的风险存在...\n".format(mTOTAL))
            flag = False
            if not ALARM_ON:
                ALARM_ON = True
            if ActionCOUNTER > 0:
                ActionCOUNTER -= 1
            info.append("tired")
            current_state = "tired"

        # 疲劳模型
        Roll += 1
        if Roll == 40:
            perclos = (Rolleye / Roll)
            log_info("过去40帧中，Perclos得分为" + str(round(perclos, 3)) + '\n')

            if 0.12 < perclos < 0.6:
                log_info("当前处于疲劳驾驶状态\n")
                info.append("tired")
                current_state = "tired"
                if not ALARM_ON:
                    ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
            elif perclos >= 0.6:
                log_info("当前处于梦游驾驶状态\n")
                current_state = "sleepy"
                info.append("sleepy")
                if not ALARM_ON:
                    ALARM_ON = True
                if ActionCOUNTER > 0:
                    ActionCOUNTER -= 1
            else:
                log_info("当前处于清醒状态\n")
                if current_state not in ["phone", "smoke", "drink", "tired", "sleepy"]:
                    current_state = "none"
                    info.append("none")

            # 计数器归零，重新开始
            Roll = 0
            Rolleye = 0
            Rollmouth = 0
            log_info("重新开始执行疲劳检测...\n")

    else:
        TOTAL = 0
        ActionCOUNTER = 0
        mTOTAL = 0
        log_info("无人驾驶状态...\n")
        current_state = "no_driver"

    # 把info和text中的检测状态写到frame上
    y0, dy = 40, 20
    i = 0
    for txt in info:
        y = y0 + i * dy
        i += 1
        cv2.putText(frame, txt, (10, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 0, 255), 1)

    # 额外写入text里最近几条信息
    for j, line in enumerate(text[-6:]):
        y = y0 + (i + j) * dy
        cv2.putText(frame, line.strip(), (10, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (0, 0, 255), 1)

    # 写当前状态
    cv2.putText(frame, "当前状态: " + current_state, (10, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    return frame, info


#检测疲劳
def detect_fatigue(input_dir,output_dir, info=[]):


    # 读取需要检测的文件夹
    img_list = read_directory(input_dir)
    index = 0
    for img in img_list:
        index = index + 1
        # 检测
        img_detect, info = show_pic(img, info)
        #输出检测结果
        output_filename = os.path.join(output_dir,'{}.jpg'.format(index))
        cv2.imwrite(output_filename,img_detect)

        # cv2.imshow("1",img_detect)
        # cv2.waitKey(0)

    # 将所有帧检测结果输出到result.txt文本
    output_result_filename = os.path.join(output_dir,'detect_result.txt')


    file = open(output_result_filename, 'w')
    file.write("".join(text))
    file.close()
    return info




def main():
    #视频转换为图像
    video_convert2_images(r'./visual_detect/video/1.mp4',r'./visual_detect/images/1/{}.jpg')

    # (需要检测的图像文件夹路径,检测结果文件夹路径)
    # detect_fatigue(r'./images/resolution_augment',r'./images/detect_after_resolution_augment')
    info = detect_fatigue(r'./visual_detect/images/1', r'./visual_detect/images/result1')

    print(info)

if __name__ == "__main__":
    main()


