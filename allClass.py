import configparser
import csv
import logging
import os
import pickle
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split


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
        # 状态值
        self.stateNum = 0

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

    def getStateNum(self):
        return self.stateNum

    def setStateNum(self, stateNum):
        self.stateNum = stateNum

    def getTriggerState(self, triggerName):
        for i in self.trigger:
            if i.getName() == triggerName:
                return i.getStateNum()
        return -1

    def getActionState(self, actionName):
        for i in self.action:
            if i.getName() == actionName:
                return i.getStateNum()
        return -1


class Trigger:
    def __init__(self, name, stateNum=-1):
        # 触发器名称
        self.name = name
        # 状态值
        self.stateNum = stateNum

    def getName(self):
        return self.name

    def getStateNum(self):
        return self.stateNum

    def setStateNum(self, stateNum):
        self.stateNum = stateNum


class Action:
    def __init__(self, name, stateNum=-1):
        # 动作名称
        self.name = name
        # 触发器数量
        self.triggerNum = 0
        # 触发器列表
        self.trigger = []
        # 状态值
        self.stateNum = stateNum

    def addTrigger(self, trigger):
        self.trigger.append(trigger)
        self.triggerNum += 1

    def getTrigger(self):
        return self.trigger

    def getTriggerNum(self):
        return self.triggerNum

    def getName(self):
        return self.name

    def getStateNum(self):
        return self.stateNum


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
    def __init__(self, start, end, weight, type, name, condition=None):
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
        # 条件
        self.condition = condition

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

    def setmaxWeight(self, maxWeight):
        self.maxWeight = maxWeight

    def getName(self):
        return self.name

    def getCondition(self):
        return self.condition


def currentDir():
    return os.path.dirname(os.path.realpath(__file__))


def parentDir(mydir):
    return str(Path(mydir).parent.absolute())


def readConfigFile(configfile):
    parameters = {}
    # read parameters from config file
    config = configparser.ConfigParser()
    config.read(configfile, encoding='utf-8')

    p_default = config['INIT']
    parameters['DeviceListName'] = p_default['DeviceListName']
    parameters['DeviceNumber'] = p_default.getint('DeviceNumber')
    parameters['RulesNumber'] = p_default.getint('RulesNumber')
    parameters['KnownDevicesNumber'] = p_default.getint('KnownDevicesNumber')
    parameters['DatasetLength'] = p_default.getint('DatasetLength')
    parameters['MLRuleNum'] = p_default.getint('MLRuleNum')
    parameters['localDeviceNum'] = p_default.getint('localDeviceNum')
    logfile = p_default['LogFile']
    parameters['modelNum'] = p_default.getint('modelNum')

    p_default = config['ATTACK']
    parameters['topK'] = p_default.getfloat('topK')
    parameters['runNum'] = p_default.getint('runNum')
    parameters['recoverNum'] = p_default.getint('recoverNum')
    parameters['maxDepth'] = p_default.getint('maxDepth')
    parameters['topkPath'] = p_default.getint('topkPath')
    parameters['ATWeight'] = p_default.getint('ATWeight')
    parameters['defaultWeight'] = p_default.getint('defaultWeight')

    index = logfile.rfind('.')
    if index != -1:
        logfile = logfile[:index] + "_" + time.strftime("%Y%m%d%H%M%S") + logfile[index:]
    else:
        logfile = logfile + "_" + time.strftime("%Y%m%d%H%M%S") + ".log"
    path = currentDir() + os.sep + "log"
    if not os.path.exists(path):
        os.makedirs(path)
    parameters['logpath'] = currentDir() + os.sep + "log" + os.sep + logfile

    return parameters


def initlogging(logfile):
    # debug, info, warning, error, critical
    # set up logging to file
    logging.shutdown()

    logger = logging.getLogger()
    logger.handlers = []

    logging.basicConfig(level=logging.CRITICAL,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=logfile,
                        filemode='w',
                        encoding='utf-8')

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    # add formatter to ch
    ch.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(ch)


def writeAttackPkl(list, name, runNum):
    path = 'Attack/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Attack/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    filename = open('Attack/' + str(runNum) + '/' + name + '.txt', 'w', encoding='utf-8')
    for value in list:
        filename.write(str(value))
        filename.write('\n')
    filename.close()

    with open('Attack/' + str(runNum) + '/npy/' + name + '.pkl', 'wb') as f:
        pickle.dump(list, f)


def writeAttackTxt(list, name, runNum):
    path = 'Attack/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Attack/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    filename = open('Attack/' + str(runNum) + '/' + name + '.txt', 'w', encoding='utf-8')
    for value in list:
        filename.write(str(value))
        filename.write('\n')
    filename.close()


def writeAttackNpy(list, name, runNum):
    path = 'Attack/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Attack/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    list = np.array(list)
    np.save('Attack/' + str(runNum) + '/npy/' + name + '.npy', list)


def writeEnvironmentTxtAndNpy(list, name, runNum):
    path = 'Environment/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Environment/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    filename = open('Environment/' + str(runNum) + '/' + name + '.txt', 'w', encoding='utf-8')
    for value in list:
        filename.write(str(value))
        filename.write('\n')
    filename.close()
    try:
        list = np.array(list)
        np.save('Environment/' + str(runNum) + '/npy/' + name + '.npy', list)
    except:
        print('npy error:' + str(runNum))


def writeEnvironmentNpy(list, name, runNum):
    path = 'Environment/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Environment/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    list = np.array(list)
    np.save('Environment/' + str(runNum) + '/npy/' + name + '.npy', list)


def writeEnvironmentTxtAndPkl(list, name, runNum):
    path = 'Environment/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Environment/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    filename = open('Environment/' + str(runNum) + '/' + name + '.txt', 'w', encoding='utf-8')
    for value in list:
        filename.write(str(value))
        filename.write('\n')
    filename.close()

    with open('Environment/' + str(runNum) + '/npy/' + name + '.pkl', 'wb') as f:
        pickle.dump(list, f)


def writeEnvironmentCSV(list, name, runNum):
    path = 'Environment/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Environment/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)
    with open('Environment/' + str(runNum) + '/' + name + '.csv', 'w',newline='', encoding='utf-8') as f:
        expwriter = csv.writer(f)
        for value in list:
            expwriter.writerow(value)


def writeEnvironmentPkl(list, name, runNum):
    path = 'Environment/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    path = 'Environment/' + str(runNum) + '/npy'
    if not os.path.exists(path):
        os.makedirs(path)

    with open('Environment/' + str(runNum) + '/npy/' + name + '.pkl', 'wb') as f:
        pickle.dump(list, f)


def writeAttackModel(model, name, runNum):
    path = 'Model/' + str(runNum)
    if not os.path.exists(path):
        os.makedirs(path)
    with open('Model/' + str(runNum) + '/' + name + '.pkl', 'wb') as f:
        pickle.dump(model, f)


def datasetLoad(runNum, pathNum, test_size):
    # load data
    if pathNum == 0:
        logging.critical('ML Dataset Load')
        npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        with open(npyfilepath + 'MLDataset.pkl', 'rb') as f:
            data = pickle.load(f)
    else:
        logging.critical('ML Recover Dataset Load')
        npyfilepath = currentDir() + os.sep + "Attack" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        data = np.load(npyfilepath + 'MLRecoverDataset.npy', allow_pickle=True).tolist()
    data = np.array(data)
    X = data[1:, 0:-1]
    y = data[1:, -1]
    # split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=0)
    # return
    return X_train, y_train, X_test, y_test

def datasetLoadV2(runNum, pathNum, test_size):
    # load data
    if pathNum == 0:
        logging.critical('ML Dataset Load')
        npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        with open(npyfilepath + 'MLDataset.pkl', 'rb') as f:
            data = pickle.load(f)
    else:
        logging.critical('ML Recover Dataset Load')
        npyfilepath = currentDir() + os.sep + "Attack" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        data = np.load(npyfilepath + 'MLRecoverDataset.npy', allow_pickle=True).tolist()
    data = np.array(data)
    return data
