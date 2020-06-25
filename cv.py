import cv2
import uiautomator2 as u2
import numpy as np
import matplotlib.pylab as plt
import os


def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img


class UIMatcher:

    @staticmethod
    def Rotate(img):
        """
        counter clock wise 90 degrees
        """
        trans_img = cv2.transpose(img)
        new_img = cv2.flip(trans_img, 0)
        return new_img

    @staticmethod
    def find_pic(screen, template_paths=['img/tiaoguo.jpg']):
        # 返回相对坐标
        """
        检测图片是否出现
        @return: 中心坐标lists, 对应的可信度list
        """
        centers = []
        max_vals = []
        # 增加判断screen方向
        if screen.shape[0] > screen.shape[1]:
            screen = UIMatcher.Rotate(screen)
        screen_show = screen.copy()
        # screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        # plt.imshow(screen)
        # plt.show()
        for template_path in template_paths:
            template = cv_imread(template_path)
            # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)cv_imread
            h, w = template.shape[:2]  # rows->h, cols->w
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            x = (max_loc[0] + w // 2) / screen.shape[1]
            y = (max_loc[1] + h // 2) / screen.shape[0]
            centers.append([x, y])
            max_vals.append(max_val)
            if max_val > 0.8:
                cv2.rectangle(screen_show, (int(max_loc[0]), int(max_loc[1])),
                              (int(max_loc[0] + w), int(max_loc[1] + h)), (0, 0, 255), 2)
                cv2.putText(screen_show, str(round(max_val, 3)) + os.path.basename(template_path),
                            (int(max_loc[0]), int(max_loc[1]) - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        # cv2.rectangle(screen, (0, 0), (10, 10), (0, 0, 255), 2)
        plt.cla()
        img4 = cv2.cvtColor(screen_show, cv2.COLOR_BGR2RGB)
        plt.imshow(img4)
        plt.pause(0.01)
        # if max_val>yuzhi:
        #     match_flag = 1
        # else:
        #     match_flag = 0
        # ax.hist(res.reshape(-1,1), 100, facecolor='b', alpha=0.5, label="rand_mat")
        # plt.show()
        return centers, max_vals

    @staticmethod
    def find_highlight(screen):
        """
        检测高亮位置(忽略了上板边,防止成就栏弹出遮挡)
        @return: 高亮中心相对坐标[x,y]
        """
        if screen.shape[0] > screen.shape[1]:
            screen = UIMatcher.Rotate(screen)
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        ret, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        index_1 = np.mean(np.argwhere(binary[63:, :] == 255), axis=0).astype(int)

        screen = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        cv2.circle(screen, (index_1[1], index_1[0] + 63), 10, (255, 0, 0), -1)

        plt.cla()
        plt.imshow(screen)
        plt.pause(0.01)
        print("暗点像素个数：", len(np.argwhere(binary == 255)), "亮点像素个数：", len(np.argwhere(binary == 0)))
        return index_1[1] / screen.shape[1], (index_1[0] + 63) / screen.shape[0]


if __name__ == '__main__':
    d = u2.connect()
    screen = d.screenshot(format="opencv")
    # screen = cv_imread('test.jpg')
    UIMatcher.find_highlight(screen)
    plt.show()
