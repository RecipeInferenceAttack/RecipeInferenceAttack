# Recipe Inference Attack
## 运行方式
运行main.py  
## 运行后文件架构
### ***Environment/npy***文件夹内 
1.*AttackDataset.pkl*是基于rule的攻击数据集,基于*cascadeRules.pkl*生成，只包含*knowDevicesList.npy*中的设备数据，用于构建WFST  
2.*cascadeRules.pkl*是基于*randomRulesList.npy*的级联规则集  
3.*deviceObjDict.npy*是包含TA关系的设备字典  
4.*easyRulesDataset.npy*是基于rule的攻击数据集,基于*randomRulesList.npy*生成，只包含*knowDevicesList.npy*中的设备数据，用于构建WFST  
5.*knowDevicesList.npy*是已知设备列表  
6.*knowEvent.npy*是所有已知设备的Trigger和Action  
7.*knowDevicesList.npy*是所有抽取的设备列表  
8.*randomRulesList.npy*是所有抽取的规则列表  
9.*RulesDataset2.pkl*是基于rule的攻击数据集,基于*cascadeRules.pkl*生成，包含所有设备数据，**用于检索原始数据**  
10.*RulesList.npy*是所有抽取设备的可能规则，**用于检索原始数据**  
11.*MLRules,pkl*是基于TA的规则集  
12.*MLDataset.pkl*是基于TA的数据集，基于*MLRules,pkl*生成，用于构建ML模型  
13.*MLlabel.pkl*是ML模型中的label名称  
14.*MLAttackRules.pkl*是基于TA的攻击规则集，只包含*knowDevicesList.npy*内的设备  
15.*MLAttackDataset.pkl*是基于TA的数据集，基于*MLAttackRules,pkl*生成，用于构建ML攻击模型  
### ***Attack/npy***文件夹内
1.*edgeDict.npy*是利用popular值构建的基础WFST边字典  
2.*edgeDictUpdate.npy*是利用*AttackDataset.pkl*更新权重后的WFST边字典  
3.*edgeDictCut.npy*是按照topK值去除低权重边后的WFST边字典  
4.*eventsDict.npy*是按照ATLIST设置的映射规则，**用于检索原始数据**  
### ***log***文件夹内
包含了每次攻击的日志数据
