import csv
import random
import numpy as np
from allClass import *


def random_weight(weight_data):
    total = 0  # 权重求和
    for i in weight_data:
        total += int(i[6])
    ra = random.uniform(0, total)  # 在0与权重和之前获取一个随机数
    curr_sum = 0
    ret = None
    for k in weight_data:
        curr_sum += int(k[6])  # 在遍历中，累加当前权重值
        if ra <= curr_sum:  # 当随机数<=当前权重和时，返回权重key
            ret = k
            break
    return ret


def init(runNum, DeviceListName, DeviceNumber, RulesNumber, KnownDevicesNumber, DatasetLength):
    #logging.critical('INIT runNum: %d', runNum)

    # get device list 获取设备列表
    deviceList = np.load(DeviceListName)
    deviceList = deviceList.tolist()
    RulesList = []

    # get random devices 获取随机设备
    randomDeviceList = random.sample(deviceList, DeviceNumber)
    writeEnvironmentNpy(randomDeviceList, 'randomDeviceList', runNum)

    # get rules list 获取规则列表
    for i in randomDeviceList:
        csvName = i + '.csv'
        csvPath = os.path.join(currentDir(), 'Applets', csvName)
        with open(csvPath, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == 'applet_name' or row[2] == 'None' or row[3] == 'None' \
                        or row[2] == 'Query' or row[3] == 'Query':
                    continue
                if row in RulesList:
                    continue
                if row[4] == 'None' or row[5] == 'None':
                    row[4] = i
                    row[5] = i
                    row[1] = '0'
                    RulesList.append(row)
                elif row[4].split('/')[1] in randomDeviceList and row[5].split('/')[1] in randomDeviceList:
                    row[4] = row[4].split('/')[1]
                    row[5] = row[5].split('/')[1]
                    row[1] = '0'
                    RulesList.append(row)
    writeEnvironmentNpy(RulesList, 'RulesList', runNum)

    for i in RulesList:
        if i[6].find('k') != -1:
            i[6] = i[6].replace('k', '00').replace('.', '')
        elif i[6] == '':
            i[6] = 0

    # get random rules list 获取随机规则列表
    randomRulesList = []
    RuleCount = 0
    while True:
        tmpRule = random_weight(RulesList)
        if tmpRule not in randomRulesList:
            randomRulesList.append(tmpRule)
            RuleCount += 1
        if RuleCount == RulesNumber:
            break
    # randomRulesList = random.sample(RulesList, RulesNumber)
    writeEnvironmentNpy(randomRulesList, 'randomRulesList', runNum)

    # get known devices list 获取已知设备列表
    knowDevicesList = random.sample(randomDeviceList, KnownDevicesNumber)
    writeEnvironmentNpy(knowDevicesList, 'knowDevicesList', runNum)

    # init devices 初始化设备对象列表
    deviceObjDict = {}
    for i in randomDeviceList:
        deviceObjDict[i] = Device(i)
        devicePath = os.path.join(currentDir(), 'TA', i)
        # init trigger  初始化触发器
        with open(devicePath + '/Trigger.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] == 'trigger':
                    continue
                else:
                    deviceObjDict[i].addTrigger(Trigger(row[0]))
        # init action 初始化动作
        with open(devicePath + '/Action.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            stateNum = 0
            for row in reader:
                if row[0] == 'action':
                    continue
                else:
                    deviceObjDict[i].addAction(Action(row[0], stateNum))
                    stateNum += 1
        # init state 初始化AT状态列表
        config = configparser.ConfigParser()
        config.read(devicePath + "/State.ini")
        ATlist = config['DEFAULT']['ATlist']
        ATlist = ATlist.replace('],[', '/').replace('[', '').replace(']', '').replace(' ', '').split('/')
        for j in ATlist:
            j = j.split(',')
            for k in j:
                if k == j[0]:
                    continue
                actionNum = int(j[0]) - 2
                triggerNum = int(k) - 2
                tmpTrigger = deviceObjDict[i].getTrigger()[triggerNum]
                tmpAction = deviceObjDict[i].getAction()[actionNum]
                tmpAction.addTrigger(tmpTrigger)
                tmpTrigger.setStateNum(tmpAction.getStateNum())
        stateNum = deviceObjDict[i].getActionNum()
        for j in deviceObjDict[i].getTrigger():
            if j.getStateNum() == -1:
                j.setStateNum(stateNum)
                stateNum += 1
        deviceObjDict[i].setStateNum(stateNum)
    writeEnvironmentNpy(deviceObjDict, 'deviceObjDict', runNum)

    # get rules dataset 生成简单规则数据集
    # RulesDataset = []
    # for i in range(DatasetLength):
    #     RulesDataset.append(random.choice(randomRulesList))
    #writeEnvironmentNpy(RulesDataset, 'easyRulesDataset', runNum)

    # get rules dataset 生成实时事件数据集
    knowEvent = []
    for i in knowDevicesList:
        j = deviceObjDict[i]
        for k in j.getTrigger():
            knowEvent.append(j.getName() + '/' + k.getName())
        for k in j.getAction():
            knowEvent.append(j.getName() + '/' + k.getName())
    writeEnvironmentNpy(knowEvent, 'knowEvent', runNum)


if __name__ == '__main__':
    # read parameters from config file  读取配置文件
    configfile = 'TAWFST.ini'
    parameters = readConfigFile(configfile)
    DeviceListName = parameters['DeviceListName']
    DeviceNumber = parameters['DeviceNumber']
    RulesNumber = parameters['RulesNumber']
    KnownDevicesNumber = parameters['KnownDevicesNumber']
    DatasetLength = parameters['DatasetLength']
    topK = parameters['topK']
    RealTimeEventNum = parameters['RealTimeEventDatasetLength']

    runNum = 100
    for i in range(runNum):
        init(i, DeviceListName, DeviceNumber, RulesNumber, KnownDevicesNumber, DatasetLength, RealTimeEventNum)
