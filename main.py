import time
from automator import *
from utils import *
from cv import *

plt.ion()
fig, ax = plt.subplots()
plt.show()

a = Automator()
a.start()


def login_auth(ac, pwd):
    need_auth = a.login(ac=ac, pwd=pwd)
    if need_auth:
        auth_name, auth_id = random_name(), CreatIDnum()
        a.auth(auth_name=auth_name, auth_id=auth_id)


def init_acc():
    while True:

        screenshot = a.d.screenshot(format="opencv")
        state_flag = a.get_screen_state(screenshot)

        if state_flag == 'dark':
            print('画面变暗,尝试进入引导模式点击')
            screenshot = a.d.screenshot(format="opencv")
            a.follow_guide(screenshot)

        elif state_flag == 'fight':
            print('侦测到加速按钮, 进入战斗模式')
            a.fight()
        elif state_flag == 'shouye':
            print('恭喜完成所有教学内容, 跳出循环')
            break
        else:
            template_paths = ['img/tiaoguo.jpg', 'img/ok.jpg', 'img/xiayibu.jpg', 'img/caidan.jpg',
                              'img/caidan_yuan.jpg',
                              'img/caidan_tiaoguo.jpg', 'img/dengji.jpg', 'img/tongyi.jpg', 'img/niudan_jiasu.jpg']
            a.find_and_click(screenshot, template_paths)


def clear_3_1():
    while True:
        screenshot = a.d.screenshot(format="opencv")
        state_flag = a.get_screen_state(screenshot)
        if state_flag == "dark":
            print('画面变暗,尝试进入引导模式点击')
            time.sleep(1)
            a.follow_guide(screenshot)
            time.sleep(1)
        elif state_flag == 'fight':
            print('现在是战斗模式')
            a.fight()
        elif not a.get_button_state(screenshot, ['img/maoxian.jpg']):
            a.find_and_click(screenshot, ['img/guanbi.jpg', 'img/caidan_tiaoguo.jpg', 'img/guanbi.jpg',
                                          'img/ok.jpg', 'img/zhandou_ok.jpg', 'img/quxiao.jpg', 'img/xiayibu.jpg',
                                          'img/tongyi.jpg', 'img/niudan_jiasu.jpg'])
            time.sleep(1)
        else:
            if not a.find_next_fight():
                continue
            while True:
                screenshot = a.d.screenshot(format="opencv")
                if a.get_button_state(screenshot, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) == {}:
                    a.d.click(0.877, 0.845)
                else:
                    break


def shou_qu():
    active_list = ['img/guanbi.jpg', 'img/liwu.jpg', 'img/quanbushouqu.jpg',
                   'img/ok.jpg', 'img/zhandou_ok.jpg', 'img/quxiao.jpg']
    for active in active_list:
        screen_shot = a.d.screenshot(format="opencv")
        a.find_and_click(screen_shot, [active], suiji=0)
        time.sleep(1)


def niu_dan():
    a.d.click(751, 505)
    time.sleep(1)
    while True:
        time.sleep(1)
        active_list = ['img/ok.jpg', 'img/niudan_jiasu.jpg', 'img/zaicichouqu.jpg', 'img/shilian.jpg']
        screen_shot = a.d.screenshot(format="opencv")
        a.find_and_click(screen_shot, active_list, suiji=1)
        screen_shot_ = a.d.screenshot(format="opencv")
        state_flag = a.get_screen_state(screen_shot_)
        if state_flag == 'baoshigoumai':
            print('没钱了, 关闭')
            a.d.click(373, 370)
            break


def write_log(account, pwd):
    time.sleep(1)
    a.d.click(209, 519)
    time.sleep(2)
    a.d.click(659, 30)
    time.sleep(2)
    a.d.click(728, 142)
    time.sleep(2)
    a.d.click(588, 481)
    time.sleep(2)

    base_path = 'img/touxiang/'
    touxiang_path_list = []
    for touxiang_path in os.listdir(base_path):
        touxiang_path_list.append(base_path + touxiang_path)
    screen_shot = a.d.screenshot(format="opencv")
    exist_list = a.get_button_state(screen_shot, touxiang_path_list)
    print(exist_list)
    st = ''
    for i in exist_list:
        st = st + str(os.path.basename(i).split('.')[0]) + ','
    with open('jieguo.txt', 'a') as f:
        f.write(account + '\t' + pwd + '\t' + st + '\n')


def logout():
    time.sleep(1)
    a.d.click(871, 513)
    time.sleep(2)
    a.d.click(165, 411)
    time.sleep(2)
    a.d.click(591, 369)
    time.sleep(2)


account_dic = {}

with open('zhanghao.txt', 'r') as f:
    for i, line in enumerate(f):
        # if i<47:
        #     continue
        account, password = line.split('\t')[0:2]
        account_dic[account] = password.strip()

for account in account_dic:
    print(account, account_dic[account])
    # login_auth(account, account_dic[account])
    clear_3_1()
    # init_acc()
    # shou_qu()
    # niu_dan()
    # write_log(account, account_dic[account])
    logout()

# 若无账号密码, 注释掉上面的for循环后, 用下面的替换
# init_acc()
# shou_qu()
# niu_dan()
# write_log(account, account_dic[account])
