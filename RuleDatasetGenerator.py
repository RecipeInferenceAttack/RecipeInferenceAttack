import copy
import random
from allClass import *


def getNewRulesDataset(i, deviceObjDict, randomRulesList, cascadeRules, oldrow, init, ):
    row = copy.deepcopy(oldrow)
    actionName = i[3]
    actionDevice = i[5]
    if init == 1:
        row.append(1)
        # TriggerName
        row.append(i[2])
        # TriggerDevice
        row.append(i[4])
        # ActionName
        row.append(actionName)
        # ActionDevice
        row.append(actionDevice)
    else:
        row[0] += 1
        row.append(actionName)
        row.append(actionDevice)

    aNum = deviceObjDict[actionDevice].getActionNum()
    tNum = 0
    for j in range(aNum):
        if actionName == deviceObjDict[actionDevice].getAction()[j].getName():
            tNum = deviceObjDict[actionDevice].getAction()[j].getTriggerNum()
            aNum = j
            break

    # 定位action的event
    action = deviceObjDict[actionDevice].getAction()[aNum]
    flag = 0
    for j in range(tNum):
        for k in randomRulesList:
            if k[2] == action.getTrigger()[j].getName() and k[4] == i[5]:
                kactionName = k[3]
                kactionDevice = k[5]
                if kactionName in row and kactionDevice in row:
                    continue
                getNewRulesDataset(k, deviceObjDict, randomRulesList, cascadeRules, row, 0)
                flag = 1
    if flag == 0:
        cascadeRules.append(row)
        del row


def generateRuleDataset(DatasetLength, runNum):
    #logging.critical('Dataset runNum: %d', runNum)
    npyfilepath = currentDir() + os.sep + "environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    knowDevicesList = np.load(npyfilepath + 'knowDevicesList.npy', allow_pickle=True).tolist()
    randomRulesList = np.load(npyfilepath + 'randomRulesList.npy', allow_pickle=True)

    cascadeRules = []
    for i in randomRulesList:
        row = []
        getNewRulesDataset(i, deviceObjDict, randomRulesList, cascadeRules, row, 1)

    writeEnvironmentTxtAndPkl(cascadeRules, 'cascadeRules', runNum)

    RulesDataset = []
    AttackDataset = []
    for i in range(DatasetLength):
        tmpRule = copy.deepcopy(random.choice(cascadeRules))
        RulesDataset.append(tmpRule)
        j = 0
        tmpRuleLen = tmpRule[0]*2
        while j < tmpRuleLen:
            if j % 2 == 0:
                j += 1
                continue
            name = tmpRule[j]
            device = tmpRule[j + 1]
            if device not in knowDevicesList:
                tmpRule[0] = int(tmpRule[0])
                tmpRule[0] -= 1
                tmpRule.remove(name)
                tmpRule.remove(device)
                tmpRuleLen = len(tmpRule) - 2
                continue
            j += 2
        if tmpRule[0] == -1:
            continue
        else:
            AttackDataset.append(tmpRule)

    writeEnvironmentPkl(AttackDataset, 'AttackDataset', runNum)

    writeEnvironmentPkl(RulesDataset, 'RulesDataset', runNum)


if __name__ == '__main__':
    for DatasetNum in range(10):
        generateRuleDataset(100, DatasetNum)
        print("DatasetNum:"+str(DatasetNum))
    # generateRuleDataset(100, 30)

