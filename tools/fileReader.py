import os

import numpy as np

from Init import parentDir, currentDir
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


npyfilepath = currentDir()+os.sep + "environment" + os.sep + '0' + os.sep + "npy" + os.sep
deviceObjDict = np.load(npyfilepath+'deviceObjDict.npy',allow_pickle=True).item()

print('done')
