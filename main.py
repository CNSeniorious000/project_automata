from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from alive_progress import alive_it
from functools import wraps
from secret import Zyh, Lx
from random import randint
from rich import print

magic_words = "main/article"
chrome, edge = 0, 1
browser = chrome
tracing = False
driver = None
timeout = 2
user = Zyh

if browser == edge:
    options = webdriver.EdgeOptions()
    options.add_argument("headless")
else:
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=720,960')
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")


def stoppable(func):

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print(f"[bright_yellow]interrupted during [r]{func.__name__}")
            exit()

    return inner


@stoppable
def restart():
    global driver
    print("[r]RESTARTING")
    if browser == chrome:
        driver = webdriver.Chrome(options=options)
    elif browser == edge:
        driver = webdriver.Edge(options=options)
    else:
        raise NotImplementedError(browser)
    driver.implicitly_wait(timeout)


restart()


@stoppable
def login():
    driver.get("https://xgfx.bnuz.edu.cn/xsdtfw/sys/emapfunauth/pages/welcome.do#/")

    click_by_xpaths("/html/body/div[1]/div/div/div/div/button[2]")
    driver.find_element(
        By.XPATH,
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[1]/div/div[1]/div/input'
    ).send_keys(user.username)
    driver.find_element(
        By.XPATH,
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[2]/div/div[1]/div/input'
    ).send_keys(user.password)


def click_by_xpaths(*xpaths):
    for xpath in xpaths:
        driver.find_element(By.XPATH, xpath).click()


def send_by_xpath(xpath, text, select=False):
    box = driver.find_element(By.XPATH, xpath)
    if select:
        box.send_keys(Keys.CONTROL + "A")
    box.send_keys(text)


@stoppable
def input_temperature():
    ans = randint(363, 371) / 10
    print(f"today's body temperature is {ans}℃")
    send_by_xpath(
        f'/html/body/{magic_words}/section/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/input',
        str(ans)
    )


@stoppable
def choose_false():
    driver.execute_script('window.scrollBy(0,1000)')
    for i in range(5):
        click_by_xpaths(
            f'/html/body/{magic_words}/section/div[2]/div[2]/div/div[2]/div[2]/div[{6 + 2 * i}]/div/div/div[2]',
            f'/html/body/div[{24 + tracing * 5 + 2 * i}]/div/div/div/div[2]/div/div[3]'
        )


@stoppable
def fill_all():
    print("[green][r]接下来填写时间")
    input_temperature()
    print("[cyan][r]接下来填否")
    choose_false()
    print("[green][r]接下来按按钮")
    click_by_xpaths('//*[@id="save"]')


@stoppable
def get_before(n):
    from datetime import date, timedelta
    return f"{date.today() - timedelta(n):%Y-%m-%d}"


@stoppable
def get_text(date):
    # return "测试"
    import arrow
    now = arrow.now()
    return f"""\
现在是：{now.ctime}，正在填写{date}即{arrow.get(date).humanize()}的健康打卡
我终于发现了！不停报ElementClickInterceptedException的原因只是我打太多字了，元素定位变了
所以只要headless模式又会出问题 总之selenium坑还真不少😥
2022年3月15日14点45分改：增加了自动滚动屏幕和屏幕大小限制，现在没问题了
源码链接
https://github.com/CNSeniorious000/project_automata
"""


@stoppable
def trace(past):
    global magic_words, tracing
    magic_words = "div[11]/div/div[1]"
    tracing = True
    for i in alive_it(past):
        date = get_before(i)
        print(date)
        try:
            click_by_xpaths('//*[@id="mrbpaxz-bl"]')  # 补录
            text = get_text(date)
            if text:
                input_bonus(text)
            send_by_xpath(
                '/html/body/div[11]/div/div[1]/section/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div/div[2]/input',
                date + "\n", select=True
            )
            fill_all()
        except WebDriverException as ex:
            print(f"[r]{type(ex).__name__}")
            return i


@stoppable
def prepare():
    login()
    page = driver.current_window_handle
    click_by_xpaths(
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[3]/div/button/span',  # 登录
        '/html/body/main/article/section[1]/div/div/div/div[1]/div/div[2]/span',  # 疫情返校
        '/html/body/main/article/section[1]/div/div/div/div[2]/div[2]/div/div[2]',  # 疫情自查上报
    )
    driver.switch_to.window(
        [handle for handle in driver.window_handles if handle != page][0])


@stoppable
def robust_trace_range(start, end, step=1):
    i = start
    prepare()
    while True:
        try:
            i = trace(range(i, end, step)) + step
            print(f"[r]{i = }")
        except TypeError:
            return
        try:
            # click_by_xpaths(
            #     '/html/body/div[39]/div[1]/div[1]/div[2]/div[2]/a',
            #     '/html/body/main/article/h2'
            # )
            print("[cyan]进行刷新")
            driver.refresh()
        except WebDriverException as ex:
            print(f"[r]{ex}")
            restart()
            prepare()


@stoppable
def daily():
    prepare()
    fill_all()


@stoppable
def input_bonus(text):
    send_by_xpath(
        f'/html/body/{magic_words}/section/div[2]/div[1]/div/div[1]/div[2]/div[25]/div/div/div[2]/div/textarea',
        text, select=True
    )


if __name__ == '__main__':
    import sys

    print(sys.argv[1:])
    if "lx" in sys.argv:
        user = Lx
    if "daily" in sys.argv:
        sys.exit(daily())
    else:
        robust_trace_range(*map(int, sys.argv[1:4]))
