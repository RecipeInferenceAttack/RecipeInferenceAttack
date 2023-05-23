import copy
import csv
import random
from allClass import *


def generateMLDataset(DatasetLength, runNum, MLRuleNum, DeviceListName):
    # logging.critical('ML Dataset runNum: %d', runNum)
    npyfilepath = currentDir() + os.sep + "environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    randomDeviceList = np.load(npyfilepath + 'randomDeviceList.npy', allow_pickle=True).tolist()
    knowDeviceList = np.load(npyfilepath + 'knowDevicesList.npy', allow_pickle=True).tolist()
    randomRulesList = np.load(npyfilepath + 'randomRulesList.npy', allow_pickle=True).tolist()

    TriggerDeviceList = copy.deepcopy(knowDeviceList)
    count = 0
    while True:
        # label设备选取
        count += 1
        labelname = random.choice(knowDeviceList)
        label = deviceObjDict[labelname]
        labelActionNum = label.getActionNum()
        if labelActionNum != 0:
            break
        if count > 100:
            labelname = 'error'
            labellist = [labelname]
            writeEnvironmentTxtAndNpy(labellist, 'MLLabel', runNum)
            return

    labellist = [labelname]
    writeEnvironmentNpy(labellist, 'MLLabel', runNum)

    for i in randomDeviceList:
        if i not in TriggerDeviceList:
            TriggerDeviceList.append(i)
    TriggerDeviceList.remove(labelname)

    # localList = []
    # for i in range(localDeviceNum):
    #     count = 0
    #     while True:
    #         count += 1
    #         # local设备选取
    #         localname = random.choice(deviceList)
    #         if localname in randomDeviceList:
    #             continue
    #         devicePath = os.path.join(currentDir(), 'TA', localname)
    #         deviceObjDict[localname]=Device(localname)
    #         local = deviceObjDict[localname]
    #         with open(devicePath + '/Trigger.csv') as csv_file:
    #             reader = csv.reader(csv_file)
    #             for row in reader:
    #                 if row[0] == 'trigger':
    #                     continue
    #                 else:
    #                     local.addTrigger(Trigger(row[0]))
    #         with open(devicePath + '/Action.csv') as csv_file:
    #             reader = csv.reader(csv_file)
    #             stateNum = 0
    #             for row in reader:
    #                 if row[0] == 'action':
    #                     continue
    #                 else:
    #                     local.addAction(Action(row[0], stateNum))
    #                     stateNum += 1
    #         config = configparser.ConfigParser()
    #         config.read(devicePath + "/State.ini")
    #         ATlist = config['DEFAULT']['ATlist']
    #         ATlist = ATlist.replace('],[', '/').replace('[', '').replace(']', '').replace(' ', '').split('/')
    #         for j in ATlist:
    #             j = j.split(',')
    #             for k in j:
    #                 if k == j[0]:
    #                     continue
    #                 actionNum = int(j[0]) - 2
    #                 triggerNum = int(k) - 2
    #                 tmpTrigger = local.getTrigger()[triggerNum]
    #                 tmpAction = local.getAction()[actionNum]
    #                 tmpAction.addTrigger(tmpTrigger)
    #                 tmpTrigger.setStateNum(tmpAction.getStateNum())
    #         stateNum = local.getActionNum()
    #         for j in local.getTrigger():
    #             if j.getStateNum() == -1:
    #                 j.setStateNum(stateNum)
    #                 stateNum += 1
    #         local.setStateNum(stateNum)
    #         localTriggerNum = local.getTriggerNum()
    #         if localTriggerNum != 0:
    #             localList.append(local)
    #             TriggerDeviceList.append(localname)
    #             break
    #         if count > 100:
    #             labelname = 'error'
    #             labellist = [labelname]
    #             writeEnvironmentTxtAndNpy(labellist, 'MLLabel', runNum)
    #             break

    # writeEnvironmentTxtAndNpy(localList, 'MLLocal', runNum)
    # writeEnvironmentNpy(deviceObjDict, 'deviceObjDict', runNum)

    writeEnvironmentNpy(TriggerDeviceList, 'TriggerDeviceList', runNum)

    random.shuffle(randomRulesList)
    # 生成ML规则
    MLRules = []
    MLAttackRules = []
    count = 0
    while True:
        count += 1
        tmpDeviceList = copy.deepcopy(random.sample(TriggerDeviceList, random.randint(1, len(TriggerDeviceList))))
        tmpRule = {}
        for j in tmpDeviceList:
            if deviceObjDict[j].getTriggerNum() == 0:
                continue
            triggerNum = random.randint(-1, deviceObjDict[j].getTriggerNum() - 1)
            tmpRule[j] = deviceObjDict[j].getTrigger()[triggerNum].getStateNum()
        if tmpRule != {}:
            tmpRule[labelname] = random.randint(-1, label.getActionNum() - 1)
            rule = tmpRule
            for j in randomRulesList:
                trigger = j[2]
                triggerDevice = j[4]
                jTstateNum = -1
                if triggerDevice in rule.keys():
                    stateNum = int(rule[triggerDevice])
                else:
                    continue
                for k in deviceObjDict[triggerDevice].getTrigger():
                    if k.getName() == trigger:
                        jTstateNum = k.getStateNum()
                        break
                if stateNum == jTstateNum:
                    for k in deviceObjDict[j[5]].getAction():
                        if k.getName() == j[3]:
                            rule[j[5]] = k.getStateNum()
                            break
            MLRules.append(rule)
        else:
            continue
        newRule = {}
        for j in tmpRule.keys():
            if j in knowDeviceList:
                newRule[j] = tmpRule[j]
        MLAttackRules.append(newRule)
        if len(MLRules) == MLRuleNum:
            break
        if count > MLRuleNum * 10:
            labelname = 'error'
            labellist = [labelname]
            writeEnvironmentTxtAndNpy(labellist, 'MLLabel', runNum)
            return
    writeEnvironmentTxtAndPkl(MLRules, 'MLRules', runNum)
    # writeEnvironmentPkl(MLAttackRules, 'MLAttackRules', runNum)

    # 生成ML数据集
    MLDataset = []
    for i in range(DatasetLength):
        # 选取ML规则
        rule = random.choice(MLRules)
        # 随机填充空白状态
        for j in TriggerDeviceList:
            if j not in rule.keys():
                rule[j] = random.randint(-1, deviceObjDict[j].getStateNum() - 1)
        MLDataset.append(rule)
    title = copy.deepcopy(TriggerDeviceList)
    title.append(labelname)
    MLDataset2 = [title]
    for i in MLDataset:
        data = []
        for j in TriggerDeviceList:
            data.append(i[j])
        data.append(i[labelname])
        MLDataset2.append(data)

    MLAttackDataset2 = []
    title = copy.deepcopy(knowDeviceList)
    title.remove(labelname)
    title.append(labelname)
    MLAttackDataset2.append(title)
    for i in MLDataset:
        data = []
        for j in knowDeviceList:
            if j != labelname:
                data.append(i[j])
        data.append(i[labelname])
        MLAttackDataset2.append(data)

    writeEnvironmentPkl(MLDataset2, 'MLDataset', runNum)
    #writeEnvironmentCSV(MLDataset2, 'MLDataset', runNum)
    writeEnvironmentPkl(MLAttackDataset2, 'MLAttackDataset', runNum)

    # print('done')


if __name__ == '__main__':
    for i in range(100):
        generateMLDataset(10000, i, 40, 'popularDeviceList.npy')
