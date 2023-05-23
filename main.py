import csv

import Init
import AttackRule
import MLAttackStates
import MLDatasetAttack
import EventAttack
import RuleDatasetGenerator
import MLDatasetGenerator
import MLTraining
from allClass import *
from sklearnex import patch_sklearn
patch_sklearn()


def main(kdn,expwriter):
    # read parameters from config file  读取配置文件
    configfile = 'TAWFST.ini'
    parameters = readConfigFile(configfile)
    DeviceListName = parameters['DeviceListName']
    DeviceNumber = parameters['DeviceNumber']
    RulesNumber = parameters['RulesNumber']
    #KnownDevicesNumber = parameters['KnownDevicesNumber']
    KnownDevicesNumber = kdn
    DatasetLength = parameters['DatasetLength']
    topK = parameters['topK']
    logpath = parameters['logpath']
    MLRuleNum = parameters['MLRuleNum']
    runNum = parameters['runNum']
    recoverNum = parameters['recoverNum']
    maxDepth = parameters['maxDepth']
    topkPath = parameters['topkPath']
    ATWeight = parameters['ATWeight']
    defaultWeight = parameters['defaultWeight']
    modelNum = parameters['modelNum']
    row = [KnownDevicesNumber]

    initlogging(logpath)

    # init device list 初始化设备列表
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START Rule ATTACK')
    logging.critical('DeviceNumber: %d', DeviceNumber)
    logging.critical('RulesNumber: %d', RulesNumber)
    logging.critical('knowDevicesNumber: %d', KnownDevicesNumber)
    logging.critical('DatasetLength: %d', DatasetLength)
    logging.critical('topK: %f', topK)
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START INIT')
    for i in range(runNum):
        Init.init(i, DeviceListName, DeviceNumber, RulesNumber, KnownDevicesNumber, DatasetLength)

    # init attack rule 初始化攻击规则
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START DATASET GENERATION')
    for i in range(runNum):
        RuleDatasetGenerator.generateRuleDataset(DatasetLength, i)
        MLDatasetGenerator.generateMLDataset(DatasetLength, i, MLRuleNum, DeviceListName)


    # attack rule 攻击规则
    finalAccuracy = 0
    finalTopkAccuracy = 0
    for i in range(runNum):
        # a, ta = AttackRule.attackEasyRule(i)
        a, ta = AttackRule.attackRuleC(i, topK, maxDepth, topkPath, ATWeight, defaultWeight)
        finalAccuracy += a
        finalTopkAccuracy += ta
    finalAccuracy /= runNum
    finalTopkAccuracy /= runNum
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('Attack Rules Done!!!')
    logging.critical('Final Recall: ' + str(finalAccuracy * 100) + '%')
    logging.critical('Final Precision: ' + str(finalTopkAccuracy * 100) + '%')
    row.append(finalAccuracy)
    row.append(finalTopkAccuracy)

    # attack event 攻击事件
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START Event ATTACK')
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    for i in range(runNum):
        EventAttack.AttackEvent(i)
    logging.critical('Event ATTACK Done!!!')

    # attack MLDataset 攻击机器学习数据集
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START MLDataset ATTACK')
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    errorList = []
    for i in range(runNum):
        state = MLDatasetAttack.attackMLDataset(i, recoverNum)
        if state == -1:
            errorList.append(i)
    logging.critical('MLDataset ATTACK Done!!!')

    # MLTrain 机器学习训练
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START MLTrain')
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    scoreList = [0 for i in range(modelNum)]
    scoreList_A = [0 for i in range(modelNum)]
    realRunNum = runNum - len(errorList)
    alltargetlist = []
    for i in range(runNum):
        if i in errorList:
            continue
        dttarget=MLTraining.ML(i, scoreList, scoreList_A)
        alltargetlist.append(dttarget)
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('Attack Rules Done!!!')
    for i in range(modelNum):
        if realRunNum!=0:
            scoreList[i] /= realRunNum
            scoreList_A[i] /= realRunNum
        else:
            scoreList[i] = 0
            scoreList_A[i] = 0
        logging.critical('model:' + str(i) + ' finalScore: %f', scoreList[i])
        row.append(scoreList[i])
        logging.critical('model:' + str(i) + ' finalScore_A: %f', scoreList_A[i])
        row.append(scoreList_A[i])

    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('START State Attack')
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    scoreList_S = [0 for i in range(modelNum+1)]
    for i in range(runNum):
        if i in errorList:
            continue
        MLAttackStates.AttackStatesWithTarget(i, DatasetLength, scoreList_S, KnownDevicesNumber,alltargetlist[i])
        #MLAttackStates.AttackStates(i, DatasetLength, scoreList_S, KnownDevicesNumber)
    for i in range(modelNum+1):
        scoreList_S[i] /= realRunNum
        logging.critical('model:' + str(i) + ' finalScore_S: %f', scoreList_S[i])
        row.append(scoreList_S[i])
    expwriter.writerow(row)


if __name__ == '__main__':
    with open('experiment.csv', 'w',newline='', encoding='utf-8') as f:
        expwriter = csv.writer(f)
        expwriter.writerow(['kdn', 'recall', 'precision', 'DT score', 'DT score_A', 'RF score', 'RF score_A',
                            'ADA score', 'ADA score_A', 'MLP score', 'MLP score_A', 'DT Attack score', 'RF Attack score'
                               , 'ADA Attack score', 'MLP Attack score'])
        for kdn in range(10, 11):
            main(kdn, expwriter)

