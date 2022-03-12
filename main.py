from selenium import webdriver
from selenium.webdriver.common.by import By
from secret import username, password
from alive_progress import alive_it

driver = webdriver.Edge()
driver.implicitly_wait(10)


def login():
    driver.get("https://xgfx.bnuz.edu.cn/xsdtfw/sys/emapfunauth/pages/welcome.do#/")
    click_by_xpaths("/html/body/div[1]/div/div/div/div/button[2]")
    driver.find_element(
        By.XPATH,
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[1]/div/div[1]/div/input'
    ).send_keys(*username)
    driver.find_element(
        By.XPATH,
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[2]/div/div[1]/div/input'
    ).send_keys(*password)


def click_by_xpaths(*xpaths):
    for xpath in alive_it(xpaths):
        driver.find_element(By.XPATH, xpath).click()


def input_temperature():
    from random import randint
    driver.find_element(
        By.XPATH,
        '/html/body/main/article/section/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/input'
    ).send_keys(f"{randint(365, 370) / 10}")


def choose_false(n):
    for n in range(n):
        click_by_xpaths(
            f'/html/body/main/article/section/div[2]/div[2]/div/div[2]/div[2]/div[{6 + 2 * n}]/div/div/div[2]/div/div/div[1]',
            f'/html/body/div[{24 + 2 * n}]/div/div/div/div[2]/div/div[3]/span'
        )


def fill_all():
    try:
        input_temperature()
        choose_false(5)
        click_by_xpaths('//*[@id="save"]')
    except BaseException as ex:
        print(ex.args)


if __name__ == '__main__':
    login()
    page = driver.current_window_handle
    click_by_xpaths(
        '//*[@id="emap-rsids-content"]/div/div[3]/div/div[3]/div/button/span',  # 登录
        '/html/body/main/article/section[1]/div/div/div/div[1]/div/div[2]/span',  # 疫情返校
        '/html/body/main/article/section[1]/div/div/div/div[2]/div[2]/div/div[2]',  # 疫情自查上报
    )
    driver.switch_to.window([handle for handle in driver.window_handles if handle != page][0])
