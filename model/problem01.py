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


if __name__ == '__main__':
    args = parse_args()

    #1.读取数据
    emp = input.Read_crew(DataName=args.data_crew_name)
    fli = input.Read_flight(DataName=args.data_flight_name)
    print(fli)

    #2.机长分组
    emp_group = {}
    for employee in emp:
        #print("flight", flight,num)
        type = employee.CapType
        if type in emp_group:
            emp_group[type].append(employee)
        else:
            emp_group[type] = []
            emp_group[type].append(employee)

    #3.先进行排序
    data_start = datetime.datetime.strptime("2021-08-11","%Y-%m-%d")
    data_end = datetime.datetime.strptime("2021-08-25","%Y-%m-%d")
    #sortedFlight = sorted(fli,key=lambda x: fli.DptrDate,reverse=True)  #ranking
    #print(sortedFlight)
    data = []
    data_rank = [data_start]
    delta = (data_end-data_start).days
    #生成一个日期排序
    for day in range(1,delta+1):
        data_rank.append(data_start+datetime.timedelta(days=day))
    print(data_rank)


    # 4.提取每日航班
    flight_day = {}
    for flight in fli:
        # print("flight", flight,num)
        flight_date = flight.DptrDate.date()
        if flight_date in flight_day:
            flight_day[flight_date].append(flight)
        else:
            flight_day[flight_date] = []
            flight_day[flight_date].append(flight)
    # day =0
    # for i in data_rank:
    #     for flight in fli:
    #         if flight.DptrDate == i :
    #             data.append(flight)
    #     day = day +1
    #
    # for j in data:
    #     print(j)


    #5.安排飞行员
    emp_arrange = {}
    ArrvImf = {}
    print("test:", flight_day[datetime.datetime.strptime("2021-8-11", "%Y-%m-%d").date()])
    days = len(flight_day)
    Capnum = 0
    FistOfficernum = 0
    num = 0

    for i in data_rank:
        print("coming:", flight_day[i.date()])
        while (len(flight_day[i.date()])!=0):
            FirstFlight = flight_day[i.date()][0]
            #分配机长并且同时记录ArrvTime和ArrvStn（到达机场），这里需要加个判断机长是不是用完了？动用type = 3 全能机长
            if emp_group[0][Capnum] in emp_arrange:
                emp_arrange[emp_group[0][Capnum]].append(FirstFlight)
                emp_group[0][Capnum].ArrvTime = FirstFlight.ArrvTime
                emp_group[0][Capnum].ArrvStn = FirstFlight.ArrvStn
            else:
                emp_arrange[emp_group[0][Capnum]] = []
                emp_arrange[emp_group[0][Capnum]].append(FirstFlight)
                emp_group[0][Capnum].ArrvTime = FirstFlight.ArrvTime
                emp_group[0][Capnum].ArrvStn = FirstFlight.ArrvStn
            #分配一名副机长，同时记录ArrvTime和ArrvStn（到达机场）
            if emp_group[1][FistOfficernum] in emp_arrange:
                emp_arrange[emp_group[1][FistOfficernum]].append(FirstFlight)
                emp_group[1][FistOfficernum].ArrvTime = FirstFlight.ArrvTime
                emp_group[1][FistOfficernum].ArrvStn = FirstFlight.ArrvStn
            else:
                emp_arrange[emp_group[1][FistOfficernum]] = []
                emp_arrange[emp_group[1][FistOfficernum]].append(FirstFlight)
                emp_group[1][FistOfficernum].ArrvTime = FirstFlight.ArrvTime
                emp_group[1][FistOfficernum].ArrvStn = FirstFlight.ArrvStn
            #记录完信息，从列表李删除该航班信息
            del flight_day[i.date()][0]
            print("hello",emp_group[0][Capnum].ArrvStn)

            #检测剩余航班有满足继续飞行的要求：
            for flight in flight_day[i.date()]:
                print((emp_group[0][Capnum].ArrvStn == flight.DptrStn))
                time_error = (flight.DptrTimestamp - emp_group[0][Capnum].ArrvTime).seconds
                print("时间差：", time_error)
                # if (emp_group[0][Capnum].ArrvStn == flight.DptrStn) and (flight.DptrTimestamp - emp_group[0][Capnum].ArrvTime >= args.MinCT):  #满足进行飞行
                #     print("find")
                # else:
                #     print("no")


    #print("the 1st assignment:",emp_arrange)
