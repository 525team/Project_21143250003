import input
import datetime
import argparse


args = None

def parse_args() :
    parser = argparse.ArgumentParser()

    # data parameters
    parser.add_argument('--data_crew_name', type=str, default='Data A-Crew.csv', help='the name of the crew data')
    parser.add_argument('--data_flight_name', type=str, default='Data A-Flight.csv', help='the name of the flight data')
    parser.add_argument('--data_dir', type=str, default='', help='the directory of the data')

    # input parameters
    parser.add_argument('--MinCT', type=int, default=40, help='the minimum connected time')
    parser.add_argument('--MaxBLk', type=int, default=600, help='the maximum of the flight time during a duty')
    parser.add_argument('--MaxDP', type=int, default=720, help='the maximum of the time during a duty')
    parser.add_argument('--MinRest', type=int, default=660, help='the minimum of the rest time between two adjacent duty')
    parser.add_argument('--MaxDH', type=int, default=5, help='the maximum of the people deadheading')
    parser.add_argument('--MaxTAFB', type=int, default=14400, help='the maximum of the total time of the pairing')
    parser.add_argument('--MaxSuccOn', type=int, default=4, help='the maximum of the succeed on duty days')
    parser.add_argument('--MinVacDay', type=int, default=2, help='the minimum vacation days between two adjacent pairings')

    # model parameters
    parser.add_argument('--kState', type=int, default=2, help='the state of the pilot participate in the flight')

    args = parser.parse_args()
    return args

#初始化机组到达时间
def initial_ArrvTime(emp, ArrvTime):
    for employee in emp:
        employee.ArrvTime = ArrvTime

#对机长按照时间排序和分组
def emp_grouping(emp):
    emp_group = {}
    sorted_emp = sorted(emp, key=lambda x: x.ArrvTime, reverse=False)
    for employee in sorted_emp:
        #print("flight", flight,num)
        type = employee.CapType
        if type in emp_group:
            emp_group[type].append(employee)
        else:
            emp_group[type] = []
            emp_group[type].append(employee)
    return emp_group

if __name__ == '__main__':
    args = parse_args()

    #1.读取数据
    emp = input.Read_crew(DataName=args.data_crew_name)
    fli = input.Read_flight(DataName=args.data_flight_name)
    print(fli)


    # emp_group = {}
    # for employee in emp:
    #     #print("flight", flight,num)
    #     type = employee.CapType
    #     if type in emp_group:
    #         emp_group[type].append(employee)
    #     else:
    #         emp_group[type] = []
    #         emp_group[type].append(employee)

    #3.先进行排序
    date_start = datetime.datetime.strptime("2021-08-11","%Y-%m-%d")
    date_end = datetime.datetime.strptime("2021-08-25","%Y-%m-%d")
    initial_arrvtime = datetime.datetime.strptime("2021-08-11 00:00","%Y-%m-%d %H:%M")
    initial_ArrvTime(emp,initial_arrvtime)     #对所有的飞行员ArrvTime进行初始化，因为类型相同才方便排序
    #2.机长分组
    emp_group = emp_grouping(emp)

    data = []
    date_rank = [date_start]
    delta = (date_end-date_start).days
    #生成一个日期排序
    for day in range(1,delta+1):
        date_rank.append(date_start+datetime.timedelta(days=day))
    print(date_rank)

    #testing: 飞行员状态更新 successful
    # emp_group[0][0].ArrvTime = datetime.datetime.strptime("2021-08-11 08:00", "%Y-%m-%d %H:%M")
    # emp_group[0][1].ArrvTime = datetime.datetime.strptime("2021-08-11 09:00", "%Y-%m-%d %H:%M")
    # emp_group_sorted = emp_grouping(emp)



    # 4.提取每日航班
    flight_day = {}
    sortedFlight = sorted(fli, key=lambda x: x.DptrTimestamp, reverse=False)
    for i in sortedFlight:
        print("排序航班:", i)
    for flight in sortedFlight:
        # print("flight", flight,num)
        flight_date = flight.DptrDate.date()
        if flight_date in flight_day:
            flight_day[flight_date].append(flight)
        else:
            flight_day[flight_date] = []
            flight_day[flight_date].append(flight)
    # day =0
    # for i in date_rank:
    #     for flight in fli:
    #         if flight.DptrDate == i :
    #             data.append(flight)
    #     day = day +1
    #
    # for j in data:
    #     print(j)


    #5.安排飞行员
    emp_arrange = {}
    #print("test:", flight_day[datetime.datetime.strptime("2021-8-11", "%Y-%m-%d").date()])
    days = len(flight_day)
    Capnum = 0
    FistOfficernum = 0
    num = 0
    abnormal_flight = []

    #每天处理航班,15 days
    for i in date_rank:
        X = emp_group[0][Capnum]  #机长
        Y = emp_group[1][FistOfficernum]     #副机长
        #print("coming:", flight_day[i.date()])
        while (all(flight_day[i.date()])!=0):
            FirstFlight = flight_day[i.date()][0]
            #分配机长并且同时记录ArrvTime和ArrvStn（到达机场），这里需要加个判断机长是不是用完了？动用type = 3 全能机长
            if X in emp_arrange:
                emp_arrange[X].append(FirstFlight)
                X.ArrvTime = FirstFlight.ArrvTimestamp
                X.ArrvStn = FirstFlight.ArrvStn
            else:
                emp_arrange[X] = []
                emp_arrange[X].append(FirstFlight)
                X.ArrvTime = FirstFlight.ArrvTimestamp
                X.ArrvStn = FirstFlight.ArrvStn
            #分配一名副机长，同时记录ArrvTime和ArrvStn（到达机场）
            if Y in emp_arrange:
                emp_arrange[Y].append(FirstFlight)
                Y.ArrvTime = FirstFlight.ArrvTimestamp
                Y.ArrvStn = FirstFlight.ArrvStn
            else:
                emp_arrange[Y] = []
                emp_arrange[Y].append(FirstFlight)
                Y.ArrvTime = FirstFlight.ArrvTimestamp
                Y.ArrvStn = FirstFlight.ArrvStn
            #记录完信息，从列表李删除该航班信息
            print("删除列表：", flight_day[i.date()][0])
            del flight_day[i.date()][0]

            #检测剩余航班有满足继续飞行的要求：
            for j,flight in enumerate(flight_day[i.date()]):
                #满足飞行条件的话，继续执飞，否则就跳过
                if flight.DptrTimestamp > X.ArrvTime:
                    time_error = (flight.DptrTimestamp - X.ArrvTime).seconds
                    print("时间差：", time_error)
                    if (X.ArrvStn == flight.DptrStn) and (time_error >= args.MinCT * 60):  # 满足进行飞行,将该项置顶
                        #flight_day[i.date()].insert(0, flight)
                        #break
                        # 更新机长和副机长的航班信息
                        emp_arrange[X].append(flight)
                        X.ArrvTime = flight.ArrvTimestamp
                        X.ArrvStn = flight.ArrvStn

                        emp_arrange[Y].append(FirstFlight)
                        Y.ArrvTime = FirstFlight.ArrvTimestamp
                        Y.ArrvStn = FirstFlight.ArrvStn

                        # 删除信息
                        print("删除航班号码", flight.FltNum)
                        flight_day[i.date()][j] = 0
                        for flig in flight_day[i.date()]:
                             print("剩余航班号码", flig)
                        continue
                    else:
                        # Capnum = Capnum +1
                        # FistOfficernum = FistOfficernum +1
                        # del X
                        # del emp_group[1]
                        print("时间差：", time_error)
                        print("no")
                else:
                    if j == len(flight_day[i.date()])-1:
                        print("今天这位飞行员已经上不了了！！！！")
                        #安排下一位
                        Capnum = Capnum +1
                        FistOfficernum = FistOfficernum + 1
                        break
                    else:
                        continue
                    # print((X.ArrvStn == flight.DptrStn))
                a = flight.Num
                b = flight.FltNum
                print("时间1：", a)
                # print("时间2：", X.ArrvTime)
                  #单位是：s

        break

    #print("the 1st assignment:",emp_arrange)
