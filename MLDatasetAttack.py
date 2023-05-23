import copy
import random

from allClass import *
import numpy as np


def random_weight(AD, A, AW):
    total = 0  # 权重求和
    for i in AW:
        total += int(float(i))
    ra = random.uniform(0, total)  # 在0与权重和之前获取一个随机数
    curr_sum = 0
    ret = None
    for k in range(len(AW)):
        curr_sum += int(float(AW[k]))  # 在遍历中，累加当前权重值
        if ra <= curr_sum:  # 当随机数<=当前权重和时，返回权重key
            ret = [AD[k], A[k]]
            break
    return ret


def attackMLDataset(runNum, recoverNum):
    #logging.critical('ML Dataset Attack runNum: %d', runNum)
    #print('ML Dataset Attack runNum: %d' % runNum)
    npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    MLLabel = np.load(npyfilepath + 'MLLabel.npy', allow_pickle=True).tolist()
    if MLLabel[0] == 'error':
        return -1
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    TriggerDeviceList = np.load(npyfilepath + 'TriggerDeviceList.npy', allow_pickle=True).tolist()
    knowDeviceList = np.load(npyfilepath + 'knowDevicesList.npy', allow_pickle=True).tolist()
    with open(npyfilepath + 'MLAttackDataset.pkl', 'rb') as f:
        MLAttackDataset = pickle.load(f)
    attackFilePath = currentDir() + os.sep + "Attack" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    with open(attackFilePath + 'AttackEventList.pkl', 'rb') as f:
        AttackEventList = pickle.load(f)
    labelName = MLLabel[0]
    MLRecoverDataset = []
    title = copy.deepcopy(TriggerDeviceList)
    title.append(labelName)
    MLRecoverDataset.append(title)

    for r in range(recoverNum):
        for i in MLAttackDataset:
            if i[-1] == labelName:
                continue
            recoverData = {}
            count = 0
            for j in knowDeviceList:
                if j == labelName:
                    continue
                recoverData[j] = i[count]
                count += 1
            recoverData[labelName] = i[-1]
            for j in TriggerDeviceList:
                if j in knowDeviceList:
                    continue
                recoverData[j] = -2
            # add unknown device state 添加未知设备状态
            random.shuffle(AttackEventList)
            for j in AttackEventList:
                PE = len(j)
                if PE == 1:
                    continue
                else:
                    TD = j[0].split('/')[0]
                    T = j[0].split('/')[1]
                    TS = deviceObjDict[TD].getTriggerState(T)
                    if TD == labelName:
                        continue
                    if TS == recoverData[TD]:
                        AD = []
                        A = []
                        AW = []
                        for k in range(1, PE):
                            A.append(j[k].split('/')[0])
                            AD.append(j[k].split('/')[1])
                            AW.append(j[k].split('/')[2])
                        ret = random_weight(AD, A, AW)
                        if ret[0] == labelName or ret[0] in knowDeviceList:
                            continue
                        AS = deviceObjDict[ret[0]].getTriggerState(ret[1])
                        if AS == -1:
                            AS = deviceObjDict[ret[0]].getActionState(ret[1])
                        recoverData[ret[0]] = AS

            for j in recoverData.keys():
                if recoverData[j] == -2:
                    sn = deviceObjDict[j].getStateNum()
                    recoverData[j] = random.randint(-1, sn - 1)
            #添加上标签
            recoverData2 = []
            for j in TriggerDeviceList:
                recoverData2.append(recoverData[j])
            recoverData2.append(recoverData[labelName])
            MLRecoverDataset.append(recoverData2)

    writeAttackTxt(MLRecoverDataset, 'MLRecoverDataset', runNum)
    writeAttackNpy(MLRecoverDataset, 'MLRecoverDataset', runNum)
    return 0


if __name__ == '__main__':
    for i in range(0, 1):
        attackMLDataset(i, 1)
