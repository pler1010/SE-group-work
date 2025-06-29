# SE-group-work

## 分心&疲劳检测

模块在文件夹 `visual_detect` 中，调用关系为 `visual.py` 调用 `main_detect.py` 进行分析，`main_detect.py` 中的参数可更改，`visual.py` 的返回值的类型如下：

| 状态字符串    | 说明                 |
| ------------- | -------------------- |
| `"phone"`     | 玩手机               |
| `"smoking"`   | 抽烟                 |
| `"drink"`     | 喝水                 |
| `"tired"`     | 疲劳驾驶（轻度疲劳） |
| `"sleepy"`    | 梦游驾驶（高度疲劳） |
| `"none"`      | 清醒状态             |
| `"no_driver"` | 未识别到面部         |

模型文件夹下的 `test.py` 可使用设备摄像头事实识别分析，运行模型文件夹下的 `ui_test.py` 可进行附带ui界面的实时识别分析(供调试使用，可删除)，模型参考了[KyrieIrv11ng/Yolov5-driving-detection: 疲劳检测-危险驾驶检测](https://github.com/KyrieIrv11ng/Yolov5-driving-detection)。


TODO:`visual.py` 的返回值并非每5秒返回一次，而是和视频的帧率有关，若检测到分心行为会立刻写入info中，每40帧会计算一次疲劳指数并将疲劳程度写入info，如果只是每5秒读取一次图片进行检测会导致眨眼也会被检测为疲劳，可以考虑将系统的疲劳检测和其他功能分开，因为疲劳检测和分心检测需要实时进行，或者增加一个可视化疲劳检测的系统功能。


## 手势识别
模块在文件夹 `gesture_detect` 中，接口文件为 `gesture_handler.py`，测试文件为 `gesture_test.py`，返回值类型如下：

| 返回值 | 含义                        |
|--------|-----------------------------|
| none   | 未检测到手部（如手放在方向盘时） |
| up     | 手势向上                    |
| left   | 手势向左                    |
| right  | 手势向右                    |
| fist   | 握拳                        |
| palm   | 手掌张开 / 摆手            |
| thumb  | 大拇指（点赞手势）          |
 
实现方式为把video中2.5、7.5、12.5（2.5+5n）位置的图像取出来，并且识别对应位置的手势，日志记录在文件夹 `gesture_detect/img/external` 中，直接运行文件 `gesture_detect/gesture_handler.py` 会使用 `gesture_detect/video/test.mp4` 进行测试，并把日志记录在 `gesture_detect/img/local` 内。直接运行文件 `gesture_detect/gesture_test.py` 可使用摄像头进行在线的手势识别。

本手势识别系统基于开源项目 [hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe) 实现，
所用训练数据集为作者自行采集的手部图像，训练过程及模型参数均由作者独立完成。
该方法保证了模型在特定任务场景下的适用性和准确性。