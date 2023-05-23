import csv
import os
import numpy as np
import requests
from bs4 import BeautifulSoup


# 获取所有的TA
def iftttGetTA(url, csvwriter, csvwriter2):
    print('TA:' + url)
    # 请求的首部信息
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.146 Safari/537.36 '
    }
    # 利用requests对象的get方法，对指定的url发起请求
    # 该方法会返回一个Response对象
    res = requests.get(url, headers=headers)
    # 通过Response对象的text方法获取网页的文本信息
    soup = BeautifulSoup(res.text, 'lxml')
    # 通过BeautifulSoup对象的select方法获取指定的元素
    TA = soup.find_all('ul', {'class': 'web-applet-cards tqa discover_service_view__tqa-list___-B15q'})
    count = 0
    trigger = []
    action = []
    trigger_description = []
    action_description = []
    triggerNum = -1
    actionNum = -1
    name = soup.find_all('div', {'class': 'discover_service_view__header___yBMPF'})
    for i in name:
        if i.find('h3').get_text().strip() == 'Triggers':
            triggerNum = count
        elif i.find('h3').get_text().strip() == 'Actions':
            actionNum = count
        count += 1
    count = 0
    for i in TA:
        try:
            TAS = i.find_all('div', {'class': 'content tqa'})
            for j in TAS:
                title = j.find('span', {'class': 'discover_service_view__title___Iffhh'}).get_text().strip()
                description = j.find('span', {'class': 'discover_service_view__description___kRvgq'}).get_text().strip()
                if count == triggerNum:
                    row = []
                    trigger.append(title)
                    row.append(title)
                    trigger_description.append(description)
                    row.append(description)
                    csvwriter.writerow(row)
                elif count == actionNum:
                    row = []
                    action.append(title)
                    row.append(title)
                    action_description.append(description)
                    row.append(description)
                    csvwriter2.writerow(row)
            count += 1
        except:
            count += 1
            pass
    return trigger, action, trigger_description, action_description


def iftttGetApplets(url, csvwriter, appletNum=0):
    print('Applets:'+url)
    # 请求的首部信息
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.146 Safari/537.36 '
    }
    # 利用requests对象的get方法，对指定的url发起请求
    # 该方法会返回一个Response对象
    res = requests.get(url, headers=headers)
    # 通过Response对象的text方法获取网页的文本信息
    soup = BeautifulSoup(res.text, 'lxml')
    applets = soup.find_all('li', {'class': 'my-web-applet-card web-applet-card'})
    applet_name = []
    applet_description = []
    applet_TA = []
    count = 0
    for i in applets:
        count += 1
        if appletNum != 0 and count < appletNum:
            continue
        if appletNum != 0 and count > appletNum:
            break
        name = i.find('span', {'class': 'title'}).get_text().strip()
        applet_name.append(name)
        try:
            applet_number = i.find('div', {'class': 'meta'}).get_text().strip()
        except:
            applet_number = '0'
        applet_url = "https://ifttt.com" + i.find('a', {'class': 'small_applet_card__applet-card-body___483yP'}).get(
            'href')
        res2= requests.get(applet_url, headers=headers)
        # browser = webdriver.Chrome()
        # browser.get(applet_url)
        # time.sleep(1)
        # try:
        #     browser.find_element(By.CLASS_NAME, "txt-body-3").click()
        # except:
        #     pass

        applet_soup = BeautifulSoup(res2.text, 'lxml')
        description = applet_soup.find('p', {'class': 'txt-body-2'}).get_text().strip()
        applet_description.append(description)
        try:
            applet_TD = applet_soup.find('div', {'class': 'step'}).find('div',{'class':'icon'}).find('a').get('href')
            applet_AD = applet_soup.find('div', {'class': 'step final'}).find('div',{'class':'icon'}).find('a').get('href')
        except:
            applet_TD = 'None'
            applet_AD = 'None'
        try:
            applet_Trigger = applet_soup.find('div', {'class': 'step'}).find('h5',{'class': 'service-name'}).get_text().strip()
            applet_Action = applet_soup.find('div', {'class': 'step final'}).find('h5', {
                'class': 'service-name'}).get_text().strip()
        except:
            applet_Trigger = 'None'
            applet_Action = 'None'
        applet_TA.append([applet_Trigger, applet_Action, applet_TD, applet_AD, applet_number])
        # browser.close()
        row = [name, description, applet_Trigger, applet_Action, applet_TD, applet_AD, applet_number]
        csvwriter.writerow(row)
    res.close()
    return applet_name, applet_description, applet_TA


# choice=1:只获取applets，choice=2:只获取TA，choice=3:获取applets和TA
def getAppletsAndTA(device, choice, appletNum=0):
    url = 'https://ifttt.com/'
    if choice % 2 == 1 and not os.path.exists('./Applets/' + device + '.csv'):
        csvfile = open('./Applets/' + device + '.csv', 'w', newline='',encoding='utf-8')
        csv_writer = csv.writer(csvfile)
        header = ['applet_name', 'applet_description', 'applet_Trigger', 'applet_Action', 'applet_TD', 'applet_AD',
                  'applet_number']
        csv_writer.writerow(header)
        iftttGetApplets(url + device, csv_writer, appletNum)

    if choice > 1 and not os.path.exists('./TA/' + device):
        path = './TA/' + device
        if not os.path.exists(path):
            os.makedirs(path)
        csvfile2 = open(path + '/Trigger.csv', 'w', newline='', encoding='utf-8')
        csv_writer2 = csv.writer(csvfile2)
        csvfile3 = open(path + '/Action.csv', 'w', newline='', encoding='utf-8')
        csv_writer3 = csv.writer(csvfile3)
        header2 = ['trigger', 'trigger_description']
        csv_writer2.writerow(header2)
        header3 = ['action', 'action_description']
        csv_writer3.writerow(header3)
        iftttGetTA(url + device + "/details", csv_writer2, csv_writer3)


def getDevicesList():
    url = 'https://ifttt.com/explore/services'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/100.0.3325.146 Safari/537.36 '
    }
    # 利用requests对象的get方法，对指定的url发起请求
    # 该方法会返回一个Response对象
    res = requests.get(url, headers=headers)
    # 通过Response对象的text方法获取网页的文本信息
    soup = BeautifulSoup(res.text, 'lxml')
    print(soup)
    div = soup.find('div', {'class','web-services-container'})
    card = div.find('ul', {'class', 'web-service-cards'})
    services = card.find_all('li', {'class': 'web-service-card'})
    deviceList = []
    for i in services:
        device = i.find('a', {'class': 'service_card__service-card___Xp4nE'}).get('href').split('/')[1]
        deviceList.append(device)

    filename = open('tools/deviceList.txt', 'w')
    for value in deviceList:
        filename.write(str(value))
        filename.write(',')
    filename.close()

    deviceList = np.array(deviceList)
    np.save('DeviceList.npy', deviceList)  # 保存为.npy格式


#chatwork之后为utf-8
if __name__ == '__main__':

    getDevicesList()

    a = np.load('DeviceList.npy')
    deviceList = a.tolist()
    # num=deviceList.index('weather')
    # del deviceList[0:num]
    print(deviceList)
    for device in deviceList:
        getAppletsAndTA(device, 2)
        #time.sleep(1)


    # device = 'amazon_alexa'
    # choice = 1
    # applets = 0
    # getAppletsAndTA(device, choice, applets)
