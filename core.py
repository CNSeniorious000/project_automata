import numpy as np
from cv2 import cv2
import ddddocr; ocr = ddddocr.DdddOcr(show_ad=False)
import easyocr; reader = easyocr.Reader(["ch_sim", "en"])
from matplotlib import pyplot as plt
from mss.windows import MSS; sct = MSS()
import ctypes, win32api, win32gui
from loguru import logger
from thefuzz import process
from functools import cached_property, cache
import pyautogui
from pymouse import PyMouse; m = PyMouse()
from pykeyboard import PyKeyboard; k = PyKeyboard()
ctypes.windll.user32.SetProcessDPIAware(2)
scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
monitor = sct.monitors[0]
x, y = map(win32api.GetSystemMetrics, (0,1))
assert monitor['width'] == x and monitor['height'] == y
assert m.screen_size() == (x, y)


class about_ocr:
    def __init__(self):
        self.image = None

    def delete_cache(self, attribute):
        if attribute in self.__dict__:
            logger.info(f"{attribute = } deleted")
            del self.__dict__[attribute]

    def clear(self):
        self.delete_cache("result_e")
        self.delete_cache("result_d")
        self.delete_cache("reversed_dict")

    def show_plt(self):
        plt.imshow(self.image)
        plt.show()

    def show_cv2(self, title=None):
        cv2.imshow(str(self.image.shape) if title is None else title, self.image[...,::-1])
        cv2.waitKey()

    def load_pic(self, path="image.png"):
        self.image = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        self.clear()

    def full_screen(self):
        self.image = np.frombuffer(sct.grab(monitor).rgb, np.uint8).reshape(y, x, 3)
        self.clear()

    def modify(self):
        cv2.normalize(self.image, self.image, 0, 255, cv2.NORM_MINMAX)

    @staticmethod
    def read(img:np.ndarray):
        return ocr.classification(cv2.imencode(".bmp", img)[1].tobytes())

    def show_e(self, color=(255, 0, 0), save_to=None):
        color = np.array(color, np.uint8)
        img = self.image.copy()
        for i in self.result_e:
            c = color * i[2]
            A, B, C, D = [(round(j[0]), round(j[1])) for j in i[0]]
            cv2.line(img, A, B, c)
            cv2.line(img, B, C, c)
            cv2.line(img, C, D, c)
            cv2.line(img, D, A, c)

        else:
            plt.imshow(img)
            plt.show()
            cv2.imwrite(save_to, img[...,::-1]) if save_to is not None else None

        return img

    def show_d(self, save_to=None):
        green = np.array((0,255,0), np.uint8)
        blue = np.array((0,0,255), np.uint8)
        img = self.image.copy()

        for i, j in enumerate(self.result_d):
            opposite, string, weight = j
            c = green * weight if string == self.result_e[i][1] else blue * weight
            cv2.rectangle(img, *opposite, c)
        else:
            plt.imshow(img)
            plt.show()
            cv2.imwrite(save_to, img[..., ::-1]) if save_to is not None else None

        return img

    @cached_property
    def result_e(self):
        logger.info(f"start reading self.image @ shape {self.image.shape} using easyocr")
        _ = reader.readtext(self.image, min_size=1)
        logger.success(f"got {len(_)} blocks from self.image")
        return _

    @cached_property
    def result_d(self):
        result = []
        for box, text, weight in self.result_e:
            x1 = round(min(map(lambda p: p[0], box)))
            x2 = round(max(map(lambda p: p[0], box))) + 1
            y1 = round(min(map(lambda p: p[1], box)))
            y2 = round(max(map(lambda p: p[1], box))) + 1

            string = self.read(self.image[y1:y2, x1:x2])

            result.append((((x1, y1), (x2, y2)), string, weight))

        return result

    @cached_property
    def reversed_dict(self):
        ans = {}
        for i, j in enumerate(self.result_e):
            box, text, weight = j
            try:
                ans[text].append(i)
            except KeyError:
                ans[text] = [i]

        return ans

    def get_top(self, string:str, num=5):
        if _ := [
            self.result_e[  self.reversed_dict[ i[0] ][0]  ][1:]
            for i in process.extractBests(string, self.reversed_dict.keys(), limit=num)
            if i[1] > 0
        ]:
            logger.success(f"got {string} for {len(_) = } from easyocr")
            return _
        elif _ := [
            self.result_d[  self.reversed_dict[ i[0] ][0]  ][1:]
            for i in process.extractBests(string, self.reversed_dict.keys(), limit=num)
            if i[1] > 0
        ]:
            logger.success(f"got {string} for {len(_) = } from ddddocr")
            return _
        else:
            logger.critical(f"both attempts on {string} had failed")

    def match(self, string):
        """return the bbox of the given string"""
        """仍然是以easyocr的结果为主, 以ddddocr的结果为辅"""
        top5 = self.get_top(string, 5)
        logger.debug(f"{top5 = }")
        try:
            return top5[0][0]
        except TypeError:
            pass

class about_autogui:
    pass

class about_win32:
    def __init__(self):
        handle_root = win32gui.FindWindow(None, None)
        left, top, right, bottom = win32gui.GetWindowRect(handle_root)

    @staticmethod
    def get_opposite(handle):
        """获取对角线"""
        left, top, right, bottom = win32gui.GetWindowRect(handle)
        return (left, top), (right, bottom)


if __name__ == '__main__':
    self = a = about_ocr()
