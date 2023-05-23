import time
import requests
import selenium.webdriver.common.by
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import json
import csv

opt = Options()
# 不自动关闭浏览器
opt.add_experimental_option('detach', True)
web = Chrome(options=opt)

# 用户登录
web.get("https://ifttt.com/login?wp_=1")
web.find_element(By.XPATH, '//*[@id="user_username"]').send_keys("928150677")
web.find_element(By.XPATH, '//*[@id="user_password"]').send_keys("zyk220184457", Keys.ENTER)

# 防止广告出现？
time.sleep(2)
ActionChains(web).move_by_offset(0, 0).click().perform()
web.find_element(By.XPATH, '/html/body/header/div/section[2]/a[1]').click()  # 进入到了my applets界面

# 对每一个applets进行日志统计,得到当前正在使用applets总数量
time.sleep(3)
appletsTotalNum = web.find_element(By.XPATH, '/html/body/main/div/div[2]/span[1]').text.split("(")[1].split(")")[0]

# 在activity栏目对信息进行提取统计（暂未点入详细界面）

# 爬取信息写入csv文件中
data_file = open("./resources/data.csv","w",newline='')
header = ["applet name","applet creator","applet status","applet user number","device list","description","applet's log"]
writer = csv.DictWriter(data_file,header)
writer.writeheader()

for x in range(int(appletsTotalNum)):
    applet_list = web.find_elements(By.XPATH, '/html/body/main/div/section/div/ul/li')
    applet = applet_list[x]
    applet_name = applet.find_element(By.XPATH, './a/div/span/span/div/div').text

    try:
        applet.find_element(By.XPATH, './a/div/div/img')
        applet_creator = applet.find_element(By.XPATH, './a/div/div/span').text
    except exceptions.NoSuchElementException:
        applet_creator = applet.find_element(By.XPATH, './a/div/div/span/span[2]').text

    applet_status = applet.find_element(By.XPATH, './a/div[2]/div/div/div[2]/div/span/div/div').text

    try:
        applet_user = applet.find_element(By.XPATH, './a/div[3]/div/span[2]').text
    except exceptions.NoSuchElementException:
        applet_user = "none"

    if applet_status == "Connected":
        applet_device_list = applet.find_elements(By.XPATH, './a/div[3]/div[2]/ul/li')
    else:
        applet_device_list = applet.find_elements(By.XPATH, './a/div[3]/div/ul/li')

    print("applet name: " + applet_name)
    print("applet creator: " + applet_creator)
    print("applet status: " + applet_status)
    print("applet user number: " + applet_user)
    print("device list: ", end="")
    device_result = []
    for device in applet_device_list:
        device_name = device.find_element(By.XPATH, './img').get_attribute("title")
        print(device_name+", ", end=" ")
        device_result.append(device_name)
    print()

    # 开始爬取每一个applet的详细日志信息
    applet.find_element(By.XPATH, './a/div/span/span/div/div').click()
    time.sleep(3)
    # 记得爬完了页面得还回去

    #connected和connect两种情况
    if applet_status == "Connected":
        web.find_element(By.XPATH, '//*[@id="card"]/div/div[6]/div[1]/a').click()
    else:
        web.find_element(By.XPATH, '//*[@id="card"]/div/div[4]/div[1]/a').click()

    time.sleep(3)

    # 判断当前页面是否为不存在activities的页面
    try:
        web.find_element(By.XPATH, '/html/body/main/section/ul/li')
    except exceptions.NoSuchElementException:
        print("There's no activity in your feed yet. Please check back soon.")
        web.find_element(By.XPATH, '/html/body/header/button').click()
        time.sleep(2)
        web.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/button/span').click()
        time.sleep(2)
        print("###############################################")
        print(x)

        # 写入文件
        writer.writerow({"applet name":applet_name,"applet creator":applet_creator,"applet status":applet_status,"applet user number":applet_user,
                         "device list":device_result,"description":"N/A","applet's log":"There's no activity in your feed yet. Please check back soon."})
        continue

    # 判断日志是否全部刷新出来(点击所有的more)
    while True:
        try:
            web.find_element(By.XPATH,'//*[@id="more"]').click()
        except (exceptions.ElementClickInterceptedException,exceptions.NoSuchElementException,exceptions.StaleElementReferenceException):
            break
    time.sleep(3)


    # 对trigger和action的内容描述

    #这个getAttritube有跨越li段的特性？
    dict_json = web.find_element(By.XPATH,'/html/body/main/section/ul/li/div[2]').get_attribute("data-react-props")
    dict = json.loads(dict_json)

    description_result = []
    for description in dict["applet"]["permissions"]:
        print(description["description"],end=" ")
        description_result.append(description["description"])   # 将从json中拿取到的数据输出之外再加入数组中存入csv文件

    print()
    print()
    cards_list = web.find_elements(By.XPATH,'/html/body/main/section/ul/li')
    print("This applet's log: ")
    applet_log = []
    for card in cards_list:
        log_status = card.find_element(By.XPATH,'./div/div/div/h3/span').text
        log_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(card.find_element(By.XPATH,'./div/div/div/span/span').get_attribute("data-time"))))
        print(log_status,log_time)
        applet_log.append(log_status)
        applet_log.append(log_time)

        try:
            log_data_json = card.find_element(By.XPATH, './div[2]').get_attribute("data-react-props")
        except exceptions.NoSuchElementException:
            continue
        log_data_dict = json.loads(log_data_json)
        for data in log_data_dict["runDetails"]:
            if data["message"] == None:
                message = "none"
            else:
                message = data["message"]
            if data["outcome"] == None:
                outcome = "none"
            else:
                outcome = data["outcome"]
            print("Trigger/Action message: "+message)
            applet_log.append("Trigger/Action message: "+message)
            print("Trigger/Action outcome: "+outcome)
            applet_log.append("Trigger/Action outcome: "+outcome)
        print()

        # 写入文件
    writer.writerow({"applet name": applet_name, "applet creator": applet_creator, "applet status": applet_status,
                     "applet user number": applet_user,
                     "device list": device_result, "description": description_result,
                     "applet's log":applet_log})

    # 先挺住，一会儿切换回去去处理其他applets
    web.find_element(By.XPATH,'/html/body/header/button/span').click()
    time.sleep(2)
    web.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/button/span').click()
    time.sleep(2)
    print("###############################################")
    print(x)

