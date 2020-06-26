import cv2
import time
from cv import *
import uiautomator2 as u2


class Automator:
    def __init__(self, auto_task=False, auto_policy=True,
                 auto_goods=False, speedup=True):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.d = u2.connect()
        self.dWidth, self.dHeight = self.d.window_size()
        self.appRunning = False

    def get_button_state(self, screenshot, template_paths, threshold=0.84):
        # 此函数输入要判断的图片path,屏幕截图, 阈值,   返回大于阈值的path,坐标字典,
        self.dWidth, self.dHeight = self.d.window_size()
        return_dic = {}
        centers, max_vals = UIMatcher.find_pic(screenshot, template_paths=template_paths)
        for i, name in enumerate(template_paths):
            print(name + '--' + str(round(max_vals[i], 3)), end=' ')
            if max_vals[i] > threshold:
                return_dic[name] = (centers[i][0] * self.dWidth, centers[i][1] * self.dHeight)
        print('')
        return return_dic

    def find_and_click(self, screenshot, template_paths, threshold=0.84, suiji=True):
        """
        输入截图, 模板列表, 点击第一个找到的模板
        :param screenshot:
        :param template_paths:
        :param threshold:
        :param suiji:  suiji标号置True, 表示未找到时将点击左上角, 置False则不点击
        :return: 是否成功点击
        """
        self.dWidth, self.dHeight = self.d.window_size()
        centers, max_vals = UIMatcher.find_pic(screenshot, template_paths=template_paths)
        for i, name in enumerate(template_paths):
            if max_vals[i] > threshold:
                print("找到并点击", name)
                x, y = centers[i][0] * self.dWidth, centers[i][1] * self.dHeight
                self.d.click(x, y)
                return True
        if suiji:
            print('未找到所需的按钮,将点击左上角')
            self.d.click(0.1 * self.dWidth, 0.1 * self.dHeight)
            time.sleep(0.1)
            return False
        else:
            print('未找到所需的按钮,无动作')
            return False

    def get_screen_state(self, screen):
        """
        判断当前界面是否为[战斗中，初始化结束，宝石已抽完，引导模式]中的一个
        :param screen:
        :return:
        """
        self.dWidth, self.dHeight = self.d.window_size()
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        ret, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        num_of_white = len(np.argwhere(binary == 255))
        active_path = self.get_button_state(screen, ['img/kuaijin.jpg', 'img/shouye.jpg', 'img/baoshigoumai.jpg',
                                                     'img/kuaijin_1.jpg'])

        if 'img/baoshigoumai.jpg' in active_path:
            return 'baoshigoumai'

        if 'img/shouye.jpg' in active_path:
            return 'shouye'

        if 'img/kuaijin.jpg' in active_path or 'img/kuaijin_1.jpg' in active_path:
            return 'fight'

        if num_of_white < 50000:
            return 'dark'
        else:
            return 0

    def start(self):
        """
        启动脚本，请确保已进入游戏页面。
        """
        while True:
            # 判断pcr进程是否在前台, 最多等待20秒，否则唤醒到前台
            if self.d.app_wait("com.bilibili.priconne", front=True, timeout=1):
                if not self.appRunning:
                    # 从后台换到前台，留一点反应时间
                    time.sleep(1)
                self.appRunning = True
                break
            else:
                self.app = self.d.session("com.bilibili.priconne")
                self.appRunning = False
                continue

    def login(self, ac, pwd):
        while True:
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").exists(timeout=0.1):
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").click(timeout=0.1)
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").exists(timeout=0.1):
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click(timeout=0.1)
                break
            else:
                self.d.click(self.dWidth * 0.965, self.dHeight * 0.029)
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click()
        self.d.clear_text()
        self.d.send_keys(str(ac))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_password_login").click()
        self.d.clear_text()
        self.d.send_keys(str(pwd))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_buttonLogin").click()
        time.sleep(5)
        if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").exists(timeout=0.1):
            return 1  # 说明要进行认证
        else:
            return 0  # 正常

    def auth(self, auth_name, auth_id):
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_name))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_id))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
        self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()

    def follow_guide(self, screenshot):
        x, y = UIMatcher.find_highlight(screenshot)
        try:
            self.d.click(x * self.dWidth, y * self.dHeight + 20)
        except:
            pass

    def fight(self):
        # 此函数在进入战斗后调用, 会一直运行直到战斗结束.
        # print('尝试跳过战斗')
        # screenshot = self.d.screenshot(format="opencv")
        # self.find_and_click(screenshot, ['img/caidan.jpg'])
        # time.sleep(0.5)
        # screenshot = self.d.screenshot(format="opencv")
        # active_path = self.get_button_state(screenshot,
        #                                    ['img/caidan_tiaoguo.jpg', 'img/zhandou_fanhui.jpg', 'img/ok.jpg'])
        # if 'img/ok.jpg' in active_path:
        #     x, y = active_path['img/ok.jpg']
        #     print('可以跳过')
        #     self.d.click(x, y)
        # elif 'img/zhandou_fanhui.jpg' in active_path:
        #     x, y = active_path['img/zhandou_fanhui.jpg']
        #     print('无法跳过,确认进入战斗模式,将进入战斗循环')
        #     self.d.click(x, y)
        while True:
            time.sleep(0.5)
            screenshot = self.d.screenshot(format="opencv")
            active_path = self.get_button_state(screenshot, ['img/wanjiadengji.jpg', 'img/kuaijin.jpg'])
            if 'img/kuaijin.jpg' in active_path:
                x, y = active_path['img/kuaijin.jpg']
                self.d.click(x, y)
            if 'img/wanjiadengji.jpg' in active_path:
                print('战斗应该结束了. 跳出战斗循环')
                break

    def find_next_fight(self):
        """
        进入下一关的战斗页面
        需要在没有干扰的主界面执行
        :return:
        """
        print("正在寻找下一关")
        screenshot = self.d.screenshot(format="opencv")
        if not self.find_and_click(screenshot, ['img/maoxian.jpg'], suiji=False):
            print("adventure is not clickable")
            return False
        time.sleep(2)
        screenshot = self.d.screenshot(format="opencv")
        if not self.find_and_click(screenshot, ['img/zhuxianguanqia.jpg'], suiji=False):
            print("main line is not clickable")
            return False
        time.sleep(1)
        screenshot = self.d.screenshot(format="opencv")
        center_dic = self.get_button_state(screenshot, ['img/NEXT.jpg'])
        while 'img/NEXT.jpg' not in center_dic:
            self.d.click(0.955, 0.53)
            time.sleep(1)
            screenshot = self.d.screenshot(format="opencv")
            center_dic = self.get_button_state(screenshot, ['img/NEXT.jpg'])
        x, y = center_dic['img/NEXT.jpg'][0], center_dic['img/NEXT.jpg'][1] + 100
        self.d.click(x, y)
        return True


if __name__ == '__main__':
    a = Automator()
    a.find_next_fight()
