# -*- coding: utf-8 -*-

import time
from selenium import webdriver

class Idle():
    """定义参数"""
    def __init__(self, username, password):
        self.bossId = None
        self.skipBoss = True # 是否跳过boss
        self.username = username # 账号
        self.password = password   # 密码
        self.charList = [] # 当前账号角色列表
        self.charId = None # 当前角色id
        self.nth = None # 第几个角色
        self.checkedPublic = [] # 已经计算过的区域
        self.times = 0 # 当前秘境次数
        self.timesLimit = 1 # 设置打多少次

        self.homeUrl = "https://www.idleinfinity.cn"
        self.detailUrl = self.homeUrl + "/Character/Detail?id="
        self.mysteryUrl = self.homeUrl + "/Map/Detail?id="

        print("启动浏览器中...")
        self.driver = webdriver.Chrome()
        # self.driver.set_window_size(1000, 800)
        # self.driver.implicitly_wait(10)

    def start(self):
        self.driver.get(self.homeUrl)

        self.inputAccount()

        while True:
            code = self.driver.find_element_by_id("code")
            login = self.driver.find_element_by_class_name("btn-login")
            temp = input("手动输入验证码:")
            code.send_keys(temp)
            self.click(login, False)

            if not self.isElementExists(".img-thumbnail") :
                self.inputAccount()
                print("验证码输入错误，重新输入")
                continue

            break

        # self.driver.minimize_window()
        print("获取角色信息...")
        self.getUserList()

    # 启动浏览器 登录账号
    def inputAccount(self):
        username = self.driver.find_element_by_id("username")
        password = self.driver.find_element_by_id("password")
        username.send_keys(self.username)
        password.send_keys(self.password)

    # 获取所有角色信息
    def getUserList(self):
        jobs = self.driver.find_elements_by_class_name("col-sm-6")
        j = 1
        for i in jobs :
            temp = {}
            temp['name'] = i.find_element_by_class_name("panel-heading").text.split(' ')[0]
            temp['job'] = i.find_element_by_class_name("media-body").text.split("\n")[0]
            temp['id'] = i.find_element_by_class_name("btn-default").get_attribute("href")[48:]
            print("角色 %d：\n    id：%s\n    昵称：%s\n    职业：%s" % (j, temp['id'], temp['name'], temp['job']))
            self.charList.append(temp)
            j += 1

    # 选择角色
    def character(self):
        while True:
            self.nth = int(input("输入角色编号："))
            if self.nth == '' or int(self.nth) > len(self.charList) :
                print("错误的角色编号，重新输入")
                continue

            self.charId = self.charList[int(self.nth) - 1]['id']

            self.driver.get(self.detailUrl + str(self.charId))
            print("选择了第 %s 个角色" % (self.nth))
            break

    # 进入秘境
    def toMystery(self):
        self.driver.get(self.mysteryUrl + str(self.charId))
        time.sleep(1)

    def isMystery(self):
        text = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[1]").text.split("\n")[0]
        text = list(filter(str.isdigit, text))
        strs = ''
        for i in text:
            strs += str(i)

        if (int(strs) % 10 != 0) :
            raise Exception("当前非秘境副本！！！\n")

    # 开始秘境
    def mystery(self):
        print("秘境开始...")
        # 进入秘境
        self.toMystery()
        self.isMystery()

        self.click("/html/body/div[1]/div/div[1]/div[1]/div[1]/div/a[1]")

        while True:
            surplusMonster = int(self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[2]/p[11]/span[2]").text)
            if surplusMonster == 0:
                self.times += 1
                self.resetMystery()

            if self.times >= self.timesLimit :
                print("已经打了 %s 次" % self.timesLimit)
                return

            div = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[2]")

            # 判断是否有怪
            monster = div.find_elements_by_class_name("monster")
            # if self.skipBoss :
            #     for i in monster:
            #         if "boss" in i.get_attribute("class"):
            #             monster.remove(i)

            monsterLen = len(monster)
            if monsterLen :
                self.startPlay(monster.pop())
                continue

            # 判断空格
            public = div.find_elements_by_class_name("public")
            print("迷雾区域判断，稍后自动开始模拟点击...")
            for i in public :
                currentId = int(i.get_attribute("id"))
                currentClass = i.get_attribute("class")

                if (currentId in self.checkedPublic) or ("monster" in currentClass) :
                    continue

                if self.isCanDiv(currentId, currentClass):
                    self.click(i, False)

    # 开始战斗
    def startPlay(self, monster):
        monsterId = monster.get_attribute("id")
        self.click(monster, False)

        if self.isElementExists("#time") :
            count = int(self.driver.find_element_by_id("time").text)
            print("等待上次战斗结束 %s 秒" % (count))
            self.setTimeOut(count)

        count = (len(self.driver.find_elements_by_class_name("turn")) / 2) + 1
        # self.driver.execute_script("document.getElementsByClassName('turn')[0].style.display='block'")
        result = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[1]/div[1]").get_attribute('textContent')

        print("怪物ID：%s, 战斗时间：%s 秒，结果：%s \n" % (monsterId, count, result))
        self.setTimeOut(count)

        self.click("/html/body/div[1]/div/div/div[1]/div[1]/div/a")

    # 判断一个div是否可以点击
    def isCanDiv(self, divId, currentClass):
        self.checkedPublic.append(divId)

        if (divId % 20) != 19 :
            temp = self.driver.find_element_by_id(str(divId + 1)).get_attribute("class")
            if ("mask" in temp) and ("left" not in temp):
                return True

        if (divId % 20) != 0 :
            temp = self.driver.find_element_by_id(str(divId - 1)).get_attribute("class")
            if ("mask" in temp) and ("left" not in currentClass):
                return True

        if divId < 380:
            temp = self.driver.find_element_by_id(str(divId + 20)).get_attribute("class")
            if ("mask" in temp) and ("top" not in temp):
                return True

        if divId > 19:
            temp = self.driver.find_element_by_id(str(divId - 20)).get_attribute("class")
            if ("mask" in temp) and ("top" not in currentClass):
                return True

        return False

    # 重置秘境
    def resetMystery(self):
        print("本次秘境结束，即将重置...")
        self.checkedPublic = []
        self.click("/html/body/div[1]/div/div[1]/div/div[1]/div/a[1]")
        self.click("//*[@id=\"modalConfirm\"]/div/div/div[3]/button[1]")

    # type == True 传入的是一个字符串
    # type == False 传入的是一个对象
    def click(self, element, type = True):
        if type:
            element =  self.driver.find_element_by_xpath(element)

        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(1)

    # 出售物品
    def sell(self):
        self.driver.get("%s/Equipment/Query?id=%s" % (self.homeUrl, self.charId))

        while True:
            goodsType = int(input("选择要出售的类型：\n   0 全部 1 普通 2 魔法 3 稀有 4 套装 5 传奇 6 神奇\n输入对应数字:"))
            if goodsType > 6 or goodsType < 0:
                print("输入错误，重新输入")
                continue

            types = [
                "physical", "base", "magical", "rare", "set", "unique", "artifact"
            ]

            temp = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[1]/div/div[1]/ul").find_element_by_class_name(types[goodsType])
            self.click(temp, False)
            temp = self.driver.find_element_by_class_name("equip-sellbagallpage")
            self.click(temp, False)
            self.click("//*[@id=\"modalConfirm\"]/div/div/div[3]/button[1]")
            print("选中物品已经出售完成...\n")
            print("返回菜单...\n")
            time.sleep(1)
            break

    # 倒计时
    def setTimeOut(self, count):
        while count > 0:
            print("\r倒计时 %s 秒" % count, end="")
            count -= 1
            time.sleep(1)

        print('\r', end="")

    # 判断元素是否存在
    def isElementExists(self, element):
        try:
            self.driver.find_element_by_css_selector(element)
            return True

        except:
            return False

    # 回到主页，角色选择页面
    def home(self):
        self.click("/html/body/nav/div/div[1]/a")

    # 回到主页，角色选择页面
    def quit(self):
        self.driver.quit()

if __name__ == '__main__':
    idle = Idle()
    idle.start()
    idle.main()






