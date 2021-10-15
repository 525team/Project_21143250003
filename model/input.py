import sys
import csv
import numpy as np
import datetime

class Employee():
    def __init__(self, EmpNo, Captain, FirstOfficer, Deadhead, Base, DutyCostPerHour, ParingCostPerHour, CapType, ArrvTime=None, ArrvStn=None):
        self.EmpNo = EmpNo
        self.Captain = Captain
        self.FirstOfficer = FirstOfficer
        self.Deadhead = Deadhead
        self.Base = Base
        self.DutyCostPerHour = DutyCostPerHour
        self.ParingCostPerHour = ParingCostPerHour
        self.CapType = CapType
        self.ArrvTime = ArrvTime
        self.ArrvStn = ArrvStn

    def __str__(self):
        return "[" + self.EmpNo + "," + str(self.Captain) + "," + str(self.FirstOfficer) + "," + str(
            self.Deadhead) + "," + self.Base + "," + self.DutyCostPerHour + "," + self.ParingCostPerHour + "," + str(self.CapType) + "]"

class Flight():
    def __init__(self, Num, FltNum, DptrDate, DptrTime, DptrStn, ArrvDate, ArrvTime, ArrvStn,Comp, CompCaptain,CompFirstOfficer, DptrTimestamp ,ArrvTimestamp):
        self.Num = Num
        self.FltNum = FltNum
        self.DptrDate = DptrDate
        self.DptrTime = DptrTime
        self.DptrStn = DptrStn
        self.ArrvDate = ArrvDate
        self.ArrvTime = ArrvTime
        self.ArrvStn = ArrvStn
        self.Comp = Comp
        self.CompCaptain = CompCaptain
        self.CompFirstOfficer = CompFirstOfficer
        self.DptrTimestamp = DptrTimestamp
        self.ArrvTimestamp = ArrvTimestamp

    def __str__(self):
        return "[" + str(self.Num) + "," + self.FltNum + "," + str(self.DptrDate) + "," + str(self.DptrTime) + "," + str(
            self.DptrStn) + "," + str(self.DptrStn) + "," + str(self.ArrvDate) + "," + str(self.ArrvTime) + "," + str(self.Comp) + "," + str(self.DptrTimestamp) + "," + str(self.ArrvTimestamp)+ "]"



#读取Employee数据，并且提供一个建立Employee类的函数
def Read_crew(DataName, DataDir="../data/"):
    """
    :param DataName: 文件名称，，需要带引号，eg. 'Data A-Flight.csv'
    :param DataDir: 默认路径为这个
    :return: emp 是一个list，调用时emp[i] 表示第i个人的信号，eg.  emp[10].EmpNo = A0000
    """
    with open(DataDir+DataName) as f:
        data = csv.reader(f)
        header_row = next(data)
        #print(header_row)
        emp = []
        for row in data:
            row[1] = 1 if row[1] == 'Y' else 0
            row[2] = 1 if row[2] == 'Y' else 0
            if row[1] == 1 and row[2] == 0:
                CapType = 0
            elif row[1] == 0 and row[2] == 1:
                CapType = 1
            else:
                CapType = 2
            tmp = Employee(EmpNo=row[0], Captain=row[1], FirstOfficer=row[2], Deadhead=1, Base=row[4],
                           DutyCostPerHour=row[5], ParingCostPerHour=row[6],CapType=CapType)
            emp.append(tmp)
        # for i in emp:
        #     print(i.EmpNo)
        return emp

#读取航班数据，并且建立一个Flight的类
def Read_flight(DataName, DataDir="../data/"):
    with open(DataDir+DataName) as f:
        data = csv.reader(f)
        header_row = next(data)
        # print(header_row)
        fli = []
        num = 0
        for row in data:
            # row[1] = 1 if row[1] == 'Y' else 0
            if row[7] =='C1F1':
                CompCaptain = 1
                CompFirstOfficer = 1
            elif row[7] == "C1F2":
                CompCaptain = 1
                CompFirstOfficer = 2
            Dptr_time = row[1] + ' ' + row[2]  #将日期和时间组合在一起
            Arrv_time = row[4] + ' ' + row[5]  # 将日期和时间组合在一起
            row[1] = datetime.datetime.strptime(row[1], "%m/%d/%Y")
            Dptr_time = datetime.datetime.strptime(Dptr_time, "%m/%d/%Y %H:%M")
            Arrv_time = datetime.datetime.strptime(Arrv_time, "%m/%d/%Y %H:%M")
            tmp = Flight(Num=num,FltNum=row[0], DptrDate=row[1], DptrTime=row[2], DptrStn=row[3], ArrvDate=row[4],
                         ArrvTime=row[5], ArrvStn=row[6], Comp=row[7], CompCaptain=CompCaptain, CompFirstOfficer=CompFirstOfficer, ArrvTimestamp=Arrv_time,DptrTimestamp=Dptr_time)
            fli.append(tmp)
            num = num +1
        return fli


if __name__ == '__main__' :
    fli = Read_flight(DataName='Data A-Flight.csv')
    emp = Read_crew('Data A-Crew.csv')
    #costtime = fli[0].DptrTime - fli[0].ArrvTime
    #print(costtime)
    print("origin:", emp[1].ArrvStn)


