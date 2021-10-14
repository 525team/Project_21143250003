import sys
import csv
import numpy as np


class Employee():
    def __init__(self, EmpNo, Captain, FirstOfficer, Deadhead, Base, DutyCostPerHour, ParingCostPerHour):
        self.EmpNo = EmpNo
        self.Captain = Captain
        self.FirstOfficer = FirstOfficer
        self.Deadhead = Deadhead
        self.Base = Base
        self.DutyCostPerHour = DutyCostPerHour
        self.ParingCostPerHour = ParingCostPerHour

    def __str__(self):
        return "[" + self.EmpNo + "," + str(self.Captain) + "," + str(self.FirstOfficer) + "," + str(
            self.Deadhead) + "," + self.Base + "," + self.DutyCostPerHour + "," + self.ParingCostPerHour + "]"
    # def catch_mice(self):
    #     """抓老鼠的方法"""
    #     print('抓老鼠')
    #
    # def eat_mice(self):
    #     """吃老鼠"""
    #     print('吃老鼠')
        #
        # def eat_mice(self):
        #     """吃老鼠"""
        #     print('吃老鼠')
class cat():
    def __init__(self,EmpNo):
        self.EmpNo = EmpNo

#提供一个建立Employee类的函数
def Data_processing(DataName, DataDir):
    with open(DataDir+DataName) as f:
        data = csv.reader(f)
        header_row = next(data)
        print(header_row)
        emp = []
        for row in data:
            row[1] = 1 if row[1] == 'Y' else 0
            row[2] = 1 if row[2] == 'Y' else 0
            tmp = Employee(EmpNo=row[0], Captain=row[1], FirstOfficer=row[2], Deadhead=1, Base=row[4],
                           DutyCostPerHour=row[5], ParingCostPerHour=row[6])
            emp.append(tmp)
        # for i in emp:
        #     print(i.EmpNo)
        return emp

if __name__ == '__main__' :
    emp = Data_processing('Data A-Crew.csv', '../data/')
    print(emp[1].EmpNo)
    # with open("../data/Data A-Crew.csv") as f:
    #     data = csv.reader(f)
    #     header_row = next(data)
    #     print(header_row)
    #     emp = []
    #
    #     for row in data:
    #         row[1] = 1 if row[1] == 'Y' else 0
    #         row[2] = 1 if row[2] == 'Y' else 0
    #         tmp = Employee(EmpNo=row[0], Captain=row[1], FirstOfficer=row[2], Deadhead=1, Base=row[4],
    #                        DutyCostPerHour=row[5], ParingCostPerHour=row[6])
    #         emp.append(tmp)
    #     for i in emp:
    #         print(i.EmpNo)



    # data = open("../data/Data A-Crew.csv",'rb')
    # data_mid = np.loadtxt(data)
    # data.close()
    # data_arr = np.array(data_mid)
    #a = sizeof(data_list)
    # print('daxiao',my_matrix)
    # # for row in data_list:
    # #     for col in row:
    #
    # print("test", my_matrix[0][0])