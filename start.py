# -*- coding: utf-8 -*-

# 使用说明
# python 3
# 下载谷歌浏览器
# 下载谷歌浏览器驱动，放入path路径下（注意给执行权限）
# 安装包 pip install selenium
# 命令行运行 python index.py
# 命令框输入验证码

from idle import Idle

name = ""
pwd = ""
idle = Idle(name, pwd)
idle.start()
idle.character()

while True:
    print("========== 功能列表 ==========")
    print("==========1.开始秘本==========")
    print("==========2.一键卖物==========")
    print("==========3.更换角色==========")
    print("==========4.退出程序==========")

    number = input("选择功能：")
    if "1" == number :
        try:
            idle.mystery()
        except Exception as e:
            print(e)
            continue

    elif "2" == number :
        idle.sell()

    elif "3" == number :
        idle.character()

    elif "4" == number :
        idle.quit()
        break

    else:
        print("未知的指令，重新输入...\n")









