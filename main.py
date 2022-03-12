from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from secret import username, password
from alive_progress import alive_it
from random import randint
from rich import print

# options = EdgeOptions()
# options.add_argument("headless")
options = webdriver.ChromeOptions()
options.add_argument("-headless")

# driver = webdriver.Edge(options=options)
driver = webdriver.Chrome(options=options)
print(driver)
driver.implicitly_wait(10)

magic_words = "main/article"
tracing = False


def restart():
    global driver
    print("[r]RESTARTING")
    # driver = webdriver.Edge(options=options)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)


def login():
    driver.get("https://xgfx.bnuz.edu.cn/xsdtfw/sys/emapfunauth/pages/welcome.do#/")

    click_by_xpaths("/html/body/div[1]/div/div/div/div/button[2]")
    driver.find_element(
        By.XPATH,
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[1]/div/div[1]/div/input'
    ).send_keys(username)
    driver.find_element(
        By.XPATH,
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[2]/div/div[1]/div/input'
    ).send_keys(password)


def click_by_xpaths(*xpaths):
    for xpath in xpaths:
        driver.find_element(By.XPATH, xpath).click()


def input_temperature():
    ans = randint(365, 370) / 10
    print(f"today's body temperature is {ans}℃")
    driver.find_element(
        By.XPATH,
        f'/html/body/{magic_words}/section/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/input'
    ).send_keys(f"{ans}")


def choose_false(n):
    for n in range(n):
        click_by_xpaths(
            f'/html/body/{magic_words}/section/div[2]/div[2]/div/div[2]/div[2]/div[{6 + 2 * n}]/div/div/div[2]/div/div/div[1]',
            f'/html/body/div[{24 + tracing * 5 + 2 * n}]/div/div/div/div[2]/div/div[3]/span'
        )


def fill_all():
    input_temperature()
    choose_false(5)
    click_by_xpaths('//*[@id="save"]')


def get_before(n):
    from datetime import date, timedelta
    return f"{date.today() - timedelta(n):%Y-%m-%d}"


def trace(past):
    global magic_words, tracing
    magic_words = "div[11]/div/div[1]"
    tracing = True
    for i in alive_it(past):
        print(get_before(i))
        try:
            click_by_xpaths('//*[@id="mrbpaxz-bl"]')  # 补录
            box = driver.find_element(
                By.XPATH,
                '/html/body/div[11]/div/div[1]/section/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div/div[2]/input'
            )
            box.send_keys(Keys.CONTROL + "A")
            box.send_keys(get_before(i) + "\n")
            fill_all()
        except BaseException as ex:
            print(f"[r]{ex}")
            return i


def prepare():
    login()
    page = driver.current_window_handle
    click_by_xpaths(
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[3]/div/button/span',  # 登录
        '/html/body/main/article/section[1]/div/div/div/div[1]/div/div[2]/span',  # 疫情返校
        '/html/body/main/article/section[1]/div/div/div/div[2]/div[2]/div/div[2]',  # 疫情自查上报
    )
    driver.switch_to.window([handle for handle in driver.window_handles if handle != page][0])


def robust_trace_range(start, end, step=1):
    i = start
    while True:
        prepare()
        i = trace(range(i, end, step)) + step
        if i is None:
            return
        else:
            restart()


if __name__ == '__main__':
    import sys
    print(sys.argv[1:])
    robust_trace_range(*map(int, sys.argv[1:]))
