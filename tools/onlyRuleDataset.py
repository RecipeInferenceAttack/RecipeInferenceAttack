import csv
import random


def onlyRuleDataset(num):
    with open('./DatasetOutPut/onlyrule_' + str(num) + '.csv', 'w', newline='') as csvfile:
        # 构建字段名称，也就是key
        fieldnames = ['index', 'nuki', 'hue1', 'date_and_time', 'wemo_switch', 'mycurtains', 'hue2', 'arlo1', 'weather', 'tado_air_conditioning', 'nest_protect', 'arlo2', 'location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 写入字段名，当做表头
        writer.writeheader()
        for i in range(num):
            lc = random.randint(0, 2)
            li = random.randint(0, 1)
            ti = random.randint(0, 1440)
            sw = random.randint(0, 1)
            cu = random.randint(0, 2)
            li2 = random.randint(0, 1)
            mv = random.randint(0, 1)
            te = random.randint(-10, 50)
            fa = random.randint(0, 1)
            wa = random.randint(0, 1)
            so = random.randint(0, 1)
            trigger = 0
            # 应用规则
            if lc == 1:
                li = 1
                trigger = 1
            if 540 >= ti >= 480 and lc == 2:
                sw = 1
                cu = 1
                li = 0
                trigger = 1
            if ((0 <= ti <= 420) or (1140 <= ti <= 1440)) and mv == 1:
                li2 = 1
                trigger = 1
            if ti == 1140:
                cu = 2
                trigger = 1
            if te > 27 and mv == 1:
                fa = 1
                trigger = 1
            if wa == 1:
                so = 1
                trigger = 1
            # 单行写入
            if trigger == 1:
                writer.writerow({'index': str(i + 1), 'lc': str(lc), 'li': str(li), 'ti': str(ti), 'sw': str(sw),
                                 'cu': str(cu), 'li2': str(li2), 'mv': str(mv), 'te': str(te), 'fa': str(fa),
                                 'wa': str(wa),
                                 'so': str(so), })
            else:
                i -= 1


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    onlyRuleDataset(2000)
