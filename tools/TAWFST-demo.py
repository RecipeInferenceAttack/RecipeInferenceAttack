import configparser
import csv
import math
import os
from datetime import time
from pathlib import Path
import random
import numpy as np
import logging


class Device:
    def __init__(self, name):
        # 设备名称
        self.name = name
        # 触发器数量
        self.triggerNum = 0
        # 动作数量
        self.actionNum = 0
        # 触发器列表
        self.trigger = []
        # 动作列表
        self.action = []

    def addTrigger(self, trigger):
        self.trigger.append(trigger)
        self.triggerNum += 1

    def addAction(self, action):
        self.action.append(action)
        self.actionNum += 1

    def getTrigger(self):
        return self.trigger

    def getAction(self):
        return self.action

    def getTriggerNum(self):
        return self.triggerNum

    def getActionNum(self):
        return self.actionNum

    def getName(self):
        return self.name


class Action:
    def __init__(self, name):
        # 动作名称
        self.name = name
        # 触发器数量
        self.triggerNum = 0
        # 触发器列表
        self.trigger = []

    def addTrigger(self, trigger):
        self.trigger.append(trigger)
        self.triggerNum += 1

    def getTrigger(self):
        return self.trigger

    def getTriggerNum(self):
        return self.triggerNum

    def getName(self):
        return self.name


class Event:
    def __init__(self, name, deviceName, type):
        # 事件名称
        self.name = name
        # 设备名称
        self.deviceName = deviceName
        # 事件类型 0:触发器 1:动作
        self.type = type
        # 边数量
        self.edgeNum = 0
        # 边列表
        self.edge = []

    def addEdge(self, edge):
        self.edge.append(edge)
        self.edgeNum += 1

    def getEdge(self):
        return self.edge

    def getEdgeNum(self):
        return self.edgeNum

    def getName(self):
        return self.name

    def getDeviceName(self):
        return self.deviceName

    def getType(self):
        return self.type


class Edge:
    def __init__(self, start, end, weight, type, name):
        # 起始节点
        self.start = start
        # 终止节点
        self.end = end
        # 权重
        self.weight = weight
        # 边类型 0:触发器-动作 1:动作-触发器
        self.type = type
        # 边执行次数
        self.executeNum = 0
        # 边名称
        self.name = name
        # 最终权重
        self.maxWeight = 0

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getWeight(self):
        return self.weight

    def getType(self):
        return self.type

    def getExecuteNum(self):
        return self.executeNum

    def addExecuteNum(self, num):
        # 更新权重
        self.executeNum += num
        if self.type == 0:
            self.maxWeight = self.weight * self.executeNum
        else:
            self.maxWeight = 0

    def getmaxWeight(self):
        return self.maxWeight

    def getName(self):
        return self.name


def writeTxt(list, name, runNum):
    path = 'demo/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'demo/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    filename = open('demo/' + str(runNum) + '/' + name + '.txt', 'w')
    for value in list:
        filename.write(str(value))
        filename.write('\n')
    filename.close()
    list = np.array(list)
    np.save('demo/' + str(runNum) + '/npy/' + name + '.npy', list)


def initlogging(logfile):
    # debug, info, warning, error, critical
    # set up logging to file
    logging.shutdown()

    logger = logging.getLogger()
    logger.handlers = []

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=logfile,
                        filemode='w')

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    # add formatter to ch
    ch.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(ch)


def currentDir():
    return os.path.dirname(os.path.realpath(__file__))


def parentDir(mydir):
    return str(Path(mydir).parent.absolute())


def readConfigFile(configfile):
    parameters = {}
    # read parameters from config file
    config = configparser.ConfigParser()
    config.read(configfile)

    p_default = config['DEFAULT']
    parameters['DeviceListName'] = p_default['DeviceListName']
    parameters['DeviceNumber'] = p_default.getint('DeviceNumber')
    parameters['RulesNumber'] = p_default.getint('RulesNumber')
    parameters['KnownDevicesNumber'] = p_default.getint('KnownDevicesNumber')
    parameters['DatasetLength'] = p_default.getint('DatasetLength')
    parameters['topK'] = p_default.getfloat('topK')
    logfile = p_default['LogFile']
    index = logfile.rfind('.')
    if index != -1:
        logfile = logfile[:index] + "_" + time.strftime("%Y%m%d%H%M%S") + logfile[index:]
    else:
        logfile = logfile + "_" + time.strftime("%Y%m%d%H%M%S") + ".log"

    parameters['logpath'] = currentDir() + os.sep + "log" + os.sep + logfile

    return parameters


def rename_duplicate(list, print_result=False):
    new_list = [v + str(list[:i].count(v) + 1) if list.count(v) > 1 else v for i, v in enumerate(list)]
    if print_result:
        print("Renamed list:", new_list)
    return new_list


def clean_duplicate(list, print_result=False):
    no_duplicate_list = []
    duplicate_list = []
    duplicate_dict = {}
    for ele in list:
        duplicate_list.append(ele)
        if ele not in no_duplicate_list:
            no_duplicate_list.append(ele)
        else:
            ind = len(duplicate_list) - 1
            duplicate_dict[ele] = duplicate_dict.get(ele, [list.index(ele)])
            duplicate_dict[ele].append(ind)
    if print_result:
        print('Origin list:', duplicate_list, '\nNew list:', no_duplicate_list, '\nDuplicate dict:', duplicate_dict)
    return duplicate_list, no_duplicate_list, duplicate_dict


def main(runNum):
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('runNum: %d', runNum)
    # read parameters from config file  读取配置文件
    DeviceListName = 'deviceList2.npy'
    DeviceNumber = 12
    RulesNumber = 10
    knowDevicesNumber = 6
    DatasetLength = 100
    topK = 0.1

    # init logging 初始化日志
    logging.critical('DeviceNumber: %d', DeviceNumber)
    logging.critical('RulesNumber: %d', RulesNumber)
    logging.critical('knowDevicesNumber: %d', knowDevicesNumber)
    logging.critical('DatasetLength: %d', DatasetLength)

    # get device list 获取设备列表
    deviceList = np.load(DeviceListName)
    deviceList = deviceList.tolist()

    # get random device list 获取随机设备列表
    randomDeviceList = random.sample(deviceList, DeviceNumber)
    RulesList = []

    # get rules list 获取popular规则列表
    for i in randomDeviceList:
        csvName = i + '.csv'
        csvPath = os.path.join(currentDir(), '../Applets', csvName)
        with open(csvPath, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == 'applet_name':
                    continue
                if row in RulesList:
                    continue
                if row[4] == 'None' or row[5] == 'None':
                    row[4] = i
                    row[5] = i
                    RulesList.append(row)
                elif row[4].split('/')[1] in randomDeviceList and row[5].split('/')[1] in randomDeviceList:
                    row[4] = row[4].split('/')[1]
                    row[5] = row[5].split('/')[1]
                    RulesList.append(row)
    writeTxt(RulesList, 'RulesList', runNum)

    # get random rules list 获取随机规则列表
    randomRulesList = random.sample(RulesList, RulesNumber)
    writeTxt(randomRulesList, 'randomRulesList', runNum)

    # get known devices list 获取已知设备列表
    knowDevicesList = random.sample(randomDeviceList, knowDevicesNumber)
    writeTxt(knowDevicesList, 'knowDevicesList', runNum)

    # init devices 初始化设备对象列表
    deviceObjDict = {}
    for i in randomDeviceList:
        deviceObjDict[i] = Device(i)
        devicePath = os.path.join(currentDir(), '../TA_ALL', i)
        # init trigger  初始化触发器
        with open(devicePath + '/Trigger.csv') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] == 'trigger':
                    continue
                else:
                    deviceObjDict[i].addTrigger(row[0])
        # init action 初始化动作
        with open(devicePath + '/Action.csv') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] == 'action':
                    continue
                else:
                    deviceObjDict[i].addAction(Action(row[0]))
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
                deviceObjDict[i].getAction()[actionNum].addTrigger(tmpTrigger)

    # get rules dataset 获取规则数据集
    RulesDataset = []
    for i in range(DatasetLength):
        RulesDataset.append(random.choice(randomRulesList))
    writeTxt(RulesDataset, 'RulesDataset', runNum)

    # Attack 1: generate event list 生成事件列表
    eventsDict = {}
    edgeDict = {}
    for i in randomDeviceList:
        for j in range(deviceObjDict[i].getTriggerNum()):
            eventsDict[i + '/' + deviceObjDict[i].getTrigger()[j]] = Event(deviceObjDict[i].getTrigger()[j], i, 0)
        for j in range(deviceObjDict[i].getActionNum()):
            actionEvent = Event(deviceObjDict[i].getAction()[j].getName(), i, 1)
            triggeerNum = deviceObjDict[i].getAction()[j].getTriggerNum()
            aName = deviceObjDict[i].getAction()[j].getName()
            for k in range(triggeerNum):
                # actionEvent.addTrigger(deviceObjDict[i].getAction()[j].getTrigger()[k])
                tName = deviceObjDict[i].getAction()[j].getTrigger()[k]
                tEage = Edge(i + '/' + aName, i + '/' + tName, 1, 1, i + '/' + aName + '/' + tName)
                edgeDict[i + '/' + aName + '/' + tName] = tEage
                actionEvent.addEdge(tEage)
            eventsDict[i + '/' + deviceObjDict[i].getAction()[j].getName()] = actionEvent
    writeTxt(eventsDict, 'eventsDict', runNum)

    # Attack 2: generate edge list 生成边列表
    for i in RulesList:
        try:
            startEvent = eventsDict[i[4] + '/' + i[2]]
            endEvent = eventsDict[i[5] + '/' + i[3]]
        except:
            try:
                startEvent = eventsDict[i[5] + '/' + i[2]]
                endEvent = eventsDict[i[4] + '/' + i[3]]
            except:
                print(i)
                continue
        # 自触发权重为1
        if i[6] == '':
            weight = 1
        else:
            # sigmoid*2
            if i[6].find('k') != -1:
                popular = int(i[6].replace('k', '00').replace('.', ''))
            else:
                popular = int(i[6])
            weight = 2 / (1 + math.exp(-popular))
        edgeDict[i[0]] = Edge(startEvent, endEvent, weight, 0, i[0])
    writeTxt(edgeDict, 'edgeDict', runNum)

    # Attack 3: update edge weight 更新边权重
    for i in RulesDataset:
        if i[4] in knowDevicesList:
            if i[5] in knowDevicesList:
                # both known
                flag = 0
                for j in edgeDict.values():
                    if j.getType() == 1:
                        continue
                    if j.getStart().getDeviceName() == i[4] and j.getStart().getName() == i[2] \
                            and j.getEnd().getDeviceName() == i[5] and j.getEnd().getName() == i[3]:
                        j.addExecuteNum(1)
                        flag = 1
                        break

                if flag == 0:
                    try:
                        startEvent = eventsDict[i[4] + '/' + i[2]]
                        endEvent = eventsDict[i[5] + '/' + i[3]]
                    except:
                        try:
                            startEvent = eventsDict[i[5] + '/' + i[2]]
                            endEvent = eventsDict[i[4] + '/' + i[3]]
                        except:
                            print('error Rule')
                            print(i)
                            continue
                    if i[6] == '':
                        weight = 1
                    else:
                        if i[6].find('k') != -1:
                            popular = int(i[6].replace('k', '00').replace('.', ''))
                        else:
                            popular = int(i[6])
                        weight = 2 / (1 + math.exp(-popular))
                    edgeDict[i[4] + '/' + i[2] + '/' + i[5] + '/' + i[3]] = Edge(startEvent, endEvent, weight, 0, i[0])
                    edgeDict[i[4] + '/' + i[2] + '/' + i[5] + '/' + i[3]].addExecuteNum(1)
            else:
                # trigger known
                tmpEdge = []
                for j in edgeDict.values():
                    if j.getType() == 1:
                        continue
                    if j.getStart().getDeviceName() == i[4] and j.getStart().getName() == i[2]:
                        tmpEdge.append(j)
                jNum = len(tmpEdge)
                for j in tmpEdge:
                    j.addExecuteNum(1 / jNum)
        else:
            if i[5] in knowDevicesList:
                # action known
                tmpEdge = []
                for j in edgeDict.values():
                    if j.getType() == 1:
                        continue
                    if j.getEnd().getDeviceName() == i[5] and j.getEnd().getName() == i[3]:
                        tmpEdge.append(j)
                jNum = len(tmpEdge)
                for j in tmpEdge:
                    j.addExecuteNum(1 / jNum)
            else:
                # both unknown
                continue
    writeTxt(edgeDict, 'edgeDictUpdate', runNum)

    # Attack 4: output top-k edge list 输出边列表
    topkEdgeDict = {}
    maxweight = 0
    for k, v in edgeDict.items():
        if v.getmaxWeight() > maxweight:
            maxweight = v.getmaxWeight()



    for k, v in edgeDict.items():
        if v.getmaxWeight() > maxweight * topK:
            topkEdgeDict[k] = v

    topkEdgeList = []
    topkEdgeList2 = []
    for v in topkEdgeDict.values():
        topkEdgeList.append(v.getName())
        topkEdgeList2.append(v.getName() + '/' + str(v.getmaxWeight()))
    writeTxt(topkEdgeList2, 'topkEdgeList', runNum)

    # Attack 5: output accuracy 输出准确率
    randomRulesNameList = []
    for i in randomRulesList:
        randomRulesNameList.append(i[0])
    randomRuleLen = len(randomRulesList)
    tp = 0
    fp = 0
    for i in topkEdgeList:
        if i in randomRulesNameList:
            tp += 1
        else:
            fp += 1
    accuracy = tp / randomRuleLen
    topkAccuracy = tp / (tp + fp)
    logging.critical('accuracy: ' + str(accuracy * 100) + '%')
    logging.critical('topkAccuracy: ' + str(topkAccuracy * 100) + '%')
    return accuracy, topkAccuracy


if __name__ == '__main__':
    logpath = os.path.join(currentDir(), '../log', 'demo.txt')
    initlogging(logpath)
    runNum = 100
    finalAccuracy = 0
    finalTopkAccuracy = 0
    for i in range(runNum):
        a, ta = main(i)
        finalAccuracy += a
        finalTopkAccuracy += ta
    finalAccuracy /= runNum
    finalTopkAccuracy /= runNum
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('finalAccuracy: ' + str(finalAccuracy * 100) + '%')
    logging.critical('finalTopkAccuracy: ' + str(finalTopkAccuracy * 100) + '%')
