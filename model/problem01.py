import input
import datetime
import argparse
import random
import math
import csv
import pandas as pd

args = None

def parse_argsA() :
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

def parse_argsB() :
    parser = argparse.ArgumentParser()

    # data parameters
    parser.add_argument('--data_crew_name', type=str, default='Data B-Crew.csv', help='the name of the crew data')
    parser.add_argument('--data_flight_name', type=str, default='Data B-Flight.csv', help='the name of the flight data')
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
        employee.ArrvStn = employee.Base

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

#排序
def emp_ranking(emp):
    sorted_emp = sorted(emp, key=lambda x: x.ArrvTime, reverse=False)
    return sorted_emp

#生成只含有Num的list
def create_crew_list(list):
    num_list = []
    for num in list:
        num_list.append(list.EmpNo)
    return  num_list

def create_flight_list(list):
    num_list = []
    for num in list:
        num_list.append(list.Num)
    return  num_list

#该函数建立可执行的航班：
def feasibility_check(X,Y,flight):
    """

    :param X: 飞行员
    :param flight: 航班List
    :param Y: 副机长的list
    :return: 1/0 （Y/N）， 航班号
    """
    num = len(flight)
    peo_num = len(Y)
    for i,fly in enumerate(flight):
        if fly.DptrTimestamp > X.ArrvTime:
            #计算时间,单位换算成mins
            time_error = ((fly.DptrTimestamp - X.ArrvTime).seconds)/60
            if (X.ArrvStn == fly.DptrStn) and (time_error >= args.MinCT ):  # 满足进行飞行,将该项置顶
                 # 说明满足条件，返回，Y，航班数据
                 for j,y in enumerate(Y):
                     if fly.DptrTimestamp > y.ArrvTime:
                         time_errorY = ((fly.DptrTimestamp - y.ArrvTime).seconds) / 60
                         if (y.ArrvStn == fly.DptrStn) and (time_errorY >= args.MinCT ):  # 满足进行飞行,将该项置顶
                             # print("我是满足条件的Y：", y, j)
                             return 1, [y,j], [fly,i]
                             break
                         else:
                             if j == peo_num - 1:  #如果遍历完副机长都不行
                                 return 0, None, None
                             else:
                                 continue
                     else:
                         if j == peo_num - 1:
                             return 0, None, None
                         else:
                             continue
            else:
                if i == num -1:
                    return 0, None, None
                else:
                    continue
        else:  #起飞时间都不满足
            if i == num - 1:
                return 0, None, None
            else:
                continue

#匹配航班：
def feasibility_check_fli(xy,flight):
    num = len(flight)
    X = xy[0]
    for i,fly in enumerate(flight):
        time_error = ((fly.DptrTimestamp - X.ArrvTime).seconds) / 60
        if fly.DptrTimestamp > X.ArrvTime and  (X.ArrvStn == fly.DptrStn) and (time_error >= args.MinCT ):
            #计算时间,单位换算成mins
            return 1, xy, [fly,i]
            break
        else:  #起飞时间都不满足
            if i == num - 1:  # 如果是最后一个航班，那么就说明XY组合不适合，没有能飞的航班了
                return 0, None, None
                break
            else:
                continue  # 否则就继续看有无航班

#判断是否有人可以继续执飞：
def judge_fly(x,y,z):
    if (len(x) + len(z) >=1) and (len(y) + len(z) >=1) and (len(x) + len(y) + len(z) >=2):
        return 1
    else:
        return 0

#DeadHeading 当日和昨日的DH处理
def DeadHeading(fei, people, arranged_flight):
    fei_num = len(fei)
    Arrfli_num = len(arranged_flight)
    #先对rest_people 进行分类和排序
    Record = []
    Yesterday_DH = []
    #遍历一下fei
    for i, fei_fli in enumerate(fei):
        print("废掉的航班：",fei_fli)
        for j,arr_fli in enumerate(arranged_flight):
            if arr_fli !=0:
                if arr_fli.ArrvStn == fei_fli.DptrStn and (judge_fly(rest_X,rest_Y,rest_Z) == 1): #当天有闲人并且废掉的航班在当天有飞机飞过去
                    #判断是否有人匹配航班
                    for jx_num, jx in enumerate(rest_X):
                        if jx != 0:
                            if (jx.ArrvStn == arr_fli.DptrStn) and ((((arr_fli.ArrvTimestamp - fei_fli.DptrTimestamp ).seconds)/60)>=40):
                                # JX_flag, Ylist, JX_flight = feasibility_check(jx,rest_Y,arranged_flight)
                                # if JX_flag == 1:
                                #     print("找到人了：",Ylist)
                                for jxy_num,jxy in enumerate(rest_Y):
                                    if jxy!=0:
                                        if (jxy.ArrvStn == arr_fli.DptrStn) :
                                            print("此处找到人了")
                                            Record.append([jx,jxy,[arr_fli,j],[fei_fli,i]])
                                            fei[i] = 0
                                            print("看看fei:", fei)
                                            rest_X[jx_num] = 0
                                            rest_Y[jxy_num] = 0
                                            break
                                    else:
                                        continue
                else:
                    if j == Arrfli_num - 1:
                        print("今天没有航班匹配：")
                        Yesterday_DH.append(fei_fli)
                        print("启动昨日匹配")
                    else:
                        # arranged_flight[j] = 0
                        print("看看今天其他班次吧")
    # print("我是Record：", Record)
    return Record

def new_DeadHeading(fei, DH_XY, arranged_flight):
    """

    :param fei: 单个废掉的航班
    :param XY:  XY列表
    :param arranged_flight:  fli列表
    :return: XY 和 fli
    """
    Arrfli_num = len(arranged_flight)
    Yesterday_DH = []
    peo_num = len(DH_XY)
    #遍历一下fei
    # for dh_xy in DH_XY:
    #      print("检查一个人还是两个人：",DH_XY)
    if(len(DH_XY)!=0):  #有救星
        for arr_num, arr_fli in enumerate(arranged_flight):
            if arr_fli.ArrvTimestamp < fei.DptrTimestamp :  #要保证时间
                if (fei.DptrStn ==  arr_fli.ArrvStn ) and (((( fei.DptrTimestamp  - arr_fli.ArrvTimestamp ).seconds)/60)>=40):
                    # 时间和地点符合的话,找人
                    for jx_num, jx in enumerate(DH_XY):
                        jx_x = jx[0]
                        if (jx_x.ArrvStn == arr_fli.DptrStn) : #救星的基地在抵达航班的出发地
                            # print("找到救星，即可安排!")
                            return jx,arr_fli
                        else:
                            if jx_num == peo_num -1:
                                #说明人员列表到底，这个fei没救了
                                print("启动昨日：")
                                return 1
                            else:
                                #可以找其他人
                                continue
                else:  #没有满足的航班
                    if arr_num == Arrfli_num - 1:
                        print("今天没有航班匹配：")
                        Yesterday_DH.append(fei)
                        print("启动昨日匹配")
                        return 1
                    else:
                        # print("看看今天其他班次吧")
                        continue
        else:
            print("启动昨日匹配")
            return 1
    else:
        return 0


#全局更新参数:
def update_emp(emp, num,ArrvTime, ArrvStn, Task):
    emp[num].ArrvTime = ArrvTime
    emp[num].ArrvStn = ArrvStn
    emp[num].Task = Task
#从航班List里面删除某个航班：
def deleFlight(Flight_list,fli):
    for dele_num, a_fli in enumerate(Flight_list):
        if a_fli.Num == fli.Num:
            print("开始删除")
            del Flight_list[dele_num]
    return Flight_list

def problity_choice(x,y,P):
    a = random.uniform(0, 1)
    if a <= P:
        return x
    else:
        return y

#检查xy的起飞地点是否一致
def y_choice(x,y):
    if x.ArrvStn == y.ArrvStn:
        return 1
    else:
        return 0

#选出新的机组C和F
def pair_CF(captain_sortedlist,FirstOficer_sortedlist,all2_sortedlist, P):
    cap_num = len(captain_sortedlist)
    FO_num = len(FirstOficer_sortedlist)
    all_num = len(all2_sortedlist)
    pair = 0 #配对数
    new_caplist = []
    new_FOlist = []
    pair_xy = []
    if FO_num == cap_num :  #人数相等的话，偶数平分，奇数是最后一个替补休息
        # if (all_num%2) == 0:  #是偶数
        cut_num = math.floor(all_num/2)
        pair = FO_num +cut_num
        # 候选列表
        while (len(new_caplist)<cap_num+cut_num):
            if len(captain_sortedlist) == 0:
                # 说明x选完了，要把Z全加上去
                for z in all2_sortedlist:
                    new_caplist.append(z)
            elif len(all2_sortedlist) == 0:
                # 说明z选完了。要把X全加上去
                for x in captain_sortedlist:
                    new_caplist.append(x)
            else:
                new_one = problity_choice(captain_sortedlist[0], all2_sortedlist[0], P)
                # print("look look type:")
                if new_one == captain_sortedlist[0]:
                    del captain_sortedlist[0]
                else:
                    del all2_sortedlist[0]
                new_caplist.append(new_one)
        for y in FirstOficer_sortedlist:
            new_FOlist.append(y)
        for z in all2_sortedlist:
            new_FOlist.append(z)

    elif FO_num > cap_num:     #副机长人数多，正机长少
        error = FO_num -cap_num
        if cap_num + all_num <= FO_num: #差距过大的话，全给cap
            pair = cap_num + all_num
            if len(captain_sortedlist) == 0:
                # 说明x选完了，要把Z全加上去
                for z in all2_sortedlist:
                    new_caplist.append(z)
            elif len(all2_sortedlist) == 0:
                # 说明z选完了。要把X全加上去
                for x in captain_sortedlist:
                    new_caplist.append(x)
            else:
                new_one = problity_choice(captain_sortedlist[0], all2_sortedlist[0], P)
                # print("look look type:")
                if new_one == captain_sortedlist[0]:
                    del captain_sortedlist[0]
                else:
                    del all2_sortedlist[0]
                new_caplist.append(new_one)
            new_FOlist = FirstOficer_sortedlist
        else:
            #cap要得到(error+all_num)/2个名额,然后,相差不大

            reference = math.floor(cap_num + (error+all_num)/2)
            pair = reference
            print("队伍总数：", reference)
            while (len(new_caplist) < reference):
                if len(captain_sortedlist) == 0:
                    #说明x选完了，要把Z全加上去
                    print("xm没人了")
                    for z in all2_sortedlist:
                        new_caplist.append(z)
                        # print("new_cap的数量：", len(new_caplist))
                elif len(all2_sortedlist) == 0:
                    #说明z选完了。要把X全加上去
                    print("z选完了")
                    for x in captain_sortedlist:
                        new_caplist.append(x)
                else:
                    new_one = problity_choice(captain_sortedlist[0], all2_sortedlist[0], P)
                    # print("look look type:")
                    if new_one == captain_sortedlist[0]:
                        del captain_sortedlist[0]
                    else:
                        del all2_sortedlist[0]
                    new_caplist.append(new_one)
                # new_caplist.append(random.choices([captain_sortedlist[0], all2_sortedlist[0]], P))
                # for ii in new_caplist:
                #     print("我是概率选取的人：", ii)
            for y in FirstOficer_sortedlist:
                new_FOlist.append(y)
            for z in all2_sortedlist:
                new_FOlist.append(z)
    cap_copy = new_caplist
    FO_copy = new_FOlist
    return cap_copy,FO_copy, pair

def pair_CF1(captain_sortedlist,FirstOficer_sortedlist,all2_sortedlist, P):
    # 1. 循环生成当日所有配对机组，while 循环，因为我们不知道可以生成多少对（还能产生正机长 且 还能产生副机长）
    # 1. 1 每次循环以概率产生一个正机长，产生一个随机数，如果小于等于 P， 从X中产生正机长，如果大于P，从Z中产生正机长
    # 1. 2 产生正机长后，根据地点去匹配一个副机长， 从Y中找到的第一个就是副机长，如果Y中没有找到，去Z中找，如果没有，这个正机长就是废的
    # 1. 3 如果上述代码成功，现在已经得到一对 （X,Y），然后从copy中删除这俩人， 重新进入while 循环
    # 1. 4 最后的结果是匹配好的机长对
    cap_x = make_copy(captain_sortedlist)
    fo_y = make_copy(FirstOficer_sortedlist)
    fo_y.reverse()
    all_z = make_copy(all2_sortedlist)
    cp_XY = []
    X_temp = []
    cap_flag = 0
    while(judge_fly(cap_x, fo_y, all_z)):
        # 产生正机长
        prob = random.uniform(0,1)
        if (len(cap_x) != 0) and (len(all_z) != 0):
            cap_flag = 1
            # print('可以用概率选择：',cap_flag)
            if prob <= P:
               X_temp = cap_x[0]
               cap_x.remove(X_temp)
            else:
                X_temp = all_z[0]
                all_z.remove(X_temp)

        elif (len(cap_x) == 0) and (len(all_z) != 0):
            # x 用完了
            cap_flag = 1
            X_temp = all_z[0]
            # print('x用完了：',X_temp)
            all_z.remove(X_temp)
        elif (len(cap_x) != 0) and (len(all_z) == 0):
            cap_flag = 1
            X_temp = cap_x[0]
            # print('z用完了：',X_temp)
            cap_x.remove(X_temp)
        else:
            # 没有正机长了
            cap_flag = 0
            print("没有机长了")
            break

        # 匹配副机长
        pair_flag = 0
        if(cap_flag!=0) and (len(fo_y)!=0):
            for yi in range(len(fo_y)-1,-1,-1):
                if (y_choice(X_temp,fo_y[yi]) == 1):
                    # 说明匹配成功
                    pair_flag = 1
                    Y_temp = fo_y[yi]
                    cp_XY.append([X_temp,Y_temp])
                    del fo_y[yi]
                    break
                else:
                    pair_flag = 0
            if (pair_flag == 0) and (len(all_z)!=0):
                for zi in range(len(all_z) - 1, -1, -1):
                    if (y_choice(X_temp, all_z[zi]) == 1):
                        # 说明匹配成功
                        pair_flag = 1
                        Y_temp = all_z[zi]
                        cp_XY.append([X_temp, Y_temp])
                        del fo_y[zi]
                        break
                    else:
                        pair_flag = 0
    return  cp_XY

# 将C和F配对成机组
def pairXY(new_caplist,new_FOlist,pair):
    pair_xy = []
    pair_xy_num = []
    while(len(pair_xy)<pair):
        for i,ix in enumerate(new_caplist):
            if ix!=0:
                for j,iy in enumerate(new_FOlist):
                    if iy!=0:
                        if y_choice(ix,iy) == 1:
                            # print("成对：",len(pair_xy))
                            pair_xy.append([ix,iy])
                            ix_num = ix.No
                            iy_num = iy.No
                            # pair_xy_num.append([ix_num,iy_num])
                            # print("成对：",len(pair_xy))
                            new_caplist[i] = 0
                            new_FOlist[j] = 0
                            break
            if len(pair_xy) == pair:
                break
    # for i in pair_xy:
    #     print("pair:",i[0],i[1])
    return pair_xy, pair_xy_num

# def emp2num(emp):
#     num = []
#     for em in emp:
#         num.append(emp.No)
#     return num

def make_copy(a):
    b = []
    for i in a:
        b.append(i)
    return b


def AorB (decision):
    if decision == "A":
        date_start = datetime.datetime.strptime("2021-08-11","%Y-%m-%d")
        date_end = datetime.datetime.strptime("2021-08-25","%Y-%m-%d")
        initial_arrvtime = datetime.datetime.strptime("2021-08-10 00:00","%Y-%m-%d %H:%M")
        args = parse_argsA()
    elif decision == "B":
        date_start = datetime.datetime.strptime("2019-08-01", "%Y-%m-%d")
        date_end = datetime.datetime.strptime("2019-08-31", "%Y-%m-%d")
        initial_arrvtime = datetime.datetime.strptime("2019-08-01 00:00", "%Y-%m-%d %H:%M")
        args = parse_argsB()
    else:
        print("我散步了！")
    return  date_start,date_end,initial_arrvtime,args

def save_csv(name, data, path):
    test = pd.DataFrame(columns=name, data = data)  # 数据有三列，列名分别为one,two,three
    print(test)
    test.to_csv(path, encoding='gbk')


# 记录数据使用
UncoversdFlight_name = ['DptrDate','DptrTime','DptrStn','ArrvStn','FltNum','Comp']
CrewRosters_name = ['Crew','Date','FlightOrder','FltNum','DptrDate','DptrStn','ArrvDate','ArrvStn','TsakProp']

if __name__ == '__main__':
    date_start, date_end, initial_arrvtime, args = AorB("B")

    #1.读取数据
    emp = input.Read_crew(DataName=args.data_crew_name)
    fli = input.Read_flight(DataName=args.data_flight_name)
    print(fli)

    initial_ArrvTime(emp,initial_arrvtime)     # 对所有的飞行员ArrvTime进行初始化，因为类型相同才方便排序

    # 2.机长分组
    emp_group = emp_grouping(emp)

    data = []
    date_rank = [date_start]
    delta = (date_end-date_start).days

    # 生成一个日期排序
    for day in range(1,delta+1):
        date_rank.append(date_start+datetime.timedelta(days=day))
    print("这个数据的天数", len(date_rank))

    # 4.提取每日航班
    flight_day = {}
    flight_day_num = {}  #记录航班编号
    sortedFlight = sorted(fli, key=lambda x: x.DptrTimestamp, reverse=False)
    for flight in sortedFlight:
        # print("flight", flight,num)
        flight_date = flight.DptrDate.date()
        flight_num = flight.Num
        if flight_date in flight_day:
            flight_day[flight_date].append(flight)
            flight_day_num[flight_date].append(flight_num)
        else:
            flight_day[flight_date] = []
            flight_day[flight_date].append(flight)
            flight_day_num[flight_date] = []
            flight_day_num[flight_date].append(flight_num)


    #5.安排飞行员
    emp_arrange = {}
    days = len(flight_day)
    Capnum = 0
    FistOfficernum = 0
    num = 0
    abnormal_flight = []

    flight_copy = make_copy(flight_day)#对航班分组进行备份
    dissatisfaction_flight = []
    emp_copy = make_copy(emp_group)
    Arranged_record = {}  # 记录所有安排好的航班 # 记录所有安排好的人
    #每天处理航班, A15 days, B 31 days
    for i in date_rank:
        #print("coming:", flight_day[i.date()])
        F_day = make_copy(flight_day[i.date()])  # 该天的航班序列
        F_num = make_copy(flight_day_num[i.date()])  # 该天的航班序列
        Fei_fli = []  #记录当天废掉的航班
        Arranged_fli = []  #记录当天安排好的航班
        Arranged_emp = []  #记录当天安排好的人
        emp_arrange = {}
        Arranged_record [i] = []
        print("***************************************************今天是第",i, "*******************************************************")
        # 机长资格check,需要重新排序
        xy_list= pair_CF1(emp_ranking(emp_group[0]),emp_ranking(emp_group[1]),emp_ranking(emp_group[2]), 0)
        # new_xlist, new_ylist, pair_num = pair_CF1(emp_ranking(emp_group[0]), emp_ranking(emp_group[1]),
        #                                           emp_ranking(emp_group[2]), 0.65)
        # print("........",new_xlist)
        # X_list = make_copy(new_xlist)  # 机长
        # Y_list = make_copy(new_ylist)   # 副机长

        # print("新的机长列表：", new_xlist, new_ylist)
        # new_xy,new_xy_num = pairXY(new_xlist,new_ylist,pair_num)
        new_xy = make_copy(xy_list)
        #备份用，一旦用过就删除，剩下的就是闲人
        Emp_rest = make_copy(emp)
        new_xy_copy =make_copy(new_xy)
        Capnum = 0
        XY = new_xy[Capnum]
        rest_XY =make_copy(new_xy)
        task = None
        order = 0
        while (len(F_day)!=0):
            # 资格测试
            # flag_feasibility, y_list, fly_list = feasibility_check(X, Y_list, F_day)
            flag_feasibility, xy, fly_list = feasibility_check_fli(XY, F_day)
            # print("rest_XY:",rest_XY)
            if flag_feasibility == 1:   #存在这样的航班
                #飞行 -> 记录 -> 删除
                if xy in rest_XY:
                    rest_XY.remove(xy)
                order = order +1
                xy_num = [xy[0].No, xy[1].No]
                X = xy[0]
                Y = xy[1]
                fly = fly_list[0]
                fly_num = fly_list[1]
                # print("现在是", X.EmpNo,Y.EmpNo, "在执行飞行", fly.FltNum)
                Arranged_fli.append(fly)
                update_emp(emp, X.No, fly.ArrvTimestamp, fly.ArrvStn, Task=0)
                update_emp(emp, Y.No, fly.ArrvTimestamp, fly.ArrvStn, Task=1)
                # record_information = [xy, i,order,fly.FltNum,fly.DptrTimestamp, fly.DptrStn, fly.ArrvTimestamp,fly.ArrvStn,[X.Task,Y.Task],]
                # Arranged_record[i].append()
                if X in emp_arrange:
                    emp_arrange[X].append([fly, order, X.Task])
                    X.ArrvTime = fly.ArrvTimestamp
                    X.ArrvStn = fly.ArrvStn
                    X.State = 0
                else:
                    emp_arrange[X] = []
                    emp_arrange[X].append([fly, order,X.Task])
                    X.ArrvTime = fly.ArrvTimestamp
                    X.ArrvStn = fly.ArrvStn
                    X.State = 0
                if Y in emp_arrange:
                    emp_arrange[Y].append([fly, order, Y.Task])
                    Y.ArrvTime = fly.ArrvTimestamp
                    Y.ArrvStn = fly.ArrvStn
                    Y.State = 1
                else:
                    emp_arrange[Y] = []
                    emp_arrange[Y].append([fly, order, Y.Task])
                    Y.ArrvTime = fly.ArrvTimestamp
                    Y.ArrvStn = fly.ArrvStn
                    Y.State = 0
                if X not in Arranged_emp:
                    Arranged_emp.append(X)
                    Arranged_emp.append(Y)

                del F_day[fly_num]
            elif (len(new_xy)!=0): #机组还有剩余
                order = 0
                # print("这组人下班,剩余", len(new_xy),"人",Capnum)
                new_xy[0][0].State = 3
                new_xy[0][1].State = 3
                # print("Capnum:", new_xy[Capnum][0], new_xy[Capnum][1])
                del new_xy[0]
                # print("Capnum:",new_xy[Capnum][0],new_xy[Capnum][1])
                if (len(new_xy)!=0):
                    XY = new_xy[Capnum]  # 机长
            else:
                print("oh,no,处理不了了！")
                for leave in F_day:
                    # dissatisfaction_flight.append(leave)
                    Fei_fli.append(leave)
                # print("F_day的数量:",F_day)
                # print("剩下的人：",rest_XY)
                F_day = []

# for empe in emp:
#     print("最终的到达机场：", empe.ArrvTime)
        if (len(Fei_fli)!=0):
            # print("剩下的人：", rest_XY)
            for fei in Fei_fli:
                order = 0
                Record_information = new_DeadHeading(fei, rest_XY, Arranged_fli)
                # print("record_information:", Record_information)
                if Record_information == 0: #无人可救
                    dissatisfaction_flight.append(fei)
                    Fei_fli.remove(fei)

                elif Record_information == 1:   #昨日匹配
                    dissatisfaction_flight.append(fei)
                    Fei_fli.remove(fei)
                else:
                    XY = Record_information[0]  # 机长
                    X = XY[0]
                    Y = XY[1]
                    jx_fli = Record_information[1] #救星航班
                    order = order + 1
                    fly = fei
                    # print("现在是", X.EmpNo, Y.EmpNo, "在执行拯救飞行", fei.FltNum)
                    Arranged_fli.append(fly)

                    # 记录下乘机任务
                    update_emp(emp, X.No, jx_fli.ArrvTimestamp, jx_fli.ArrvStn ,Task=3)
                    update_emp(emp, Y.No, jx_fli.ArrvTimestamp, jx_fli.ArrvStn, Task=3)
                    if X in emp_arrange:
                        emp_arrange[X].append([jx_fli, order, X.Task])
                        X.ArrvTime = jx_fli.ArrvTimestamp
                        X.ArrvStn = jx_fli.ArrvStn
                        X.State = 2
                    else:
                        emp_arrange[X] = []
                        emp_arrange[X].append([jx_fli, order, X.Task])
                        X.ArrvTime = fly.ArrvTimestamp
                        X.ArrvStn = fly.ArrvStn
                        X.State = 2

                    if Y in emp_arrange:
                        emp_arrange[Y].append([jx_fli, order, Y.Task])
                        Y.ArrvTime = fly.ArrvTimestamp
                        Y.ArrvStn = fly.ArrvStn
                        Y.State = 1
                    else:
                        emp_arrange[Y] = []
                        emp_arrange[Y].append([jx_fli, order, Y.Task])
                        Y.ArrvTime = fly.ArrvTimestamp
                        Y.ArrvStn = fly.ArrvStn
                        Y.State = 0
                    if X not in Arranged_emp:
                        Arranged_emp.append(X)
                        Arranged_emp.append(Y)

                    # 记录下执行fei航班信息
                    update_emp(emp, X.No, fly.ArrvTimestamp, fly.ArrvStn ,Task=0)
                    update_emp(emp, Y.No, fly.ArrvTimestamp, fly.ArrvStn, Task=1)

                    if X in emp_arrange:
                        emp_arrange[X].append([fly, order, X.Task])
                        X.ArrvTime = fly.ArrvTimestamp
                        X.ArrvStn = fly.ArrvStn
                        X.State = 0
                    else:
                        emp_arrange[X] = []
                        emp_arrange[X].append([fly, order, X.Task])
                        X.ArrvTime = fly.ArrvTimestamp
                        X.ArrvStn = fly.ArrvStn
                        X.State = 0
                    if Y in emp_arrange:
                        emp_arrange[Y].append([fly, order, Y.Task])
                        Y.ArrvTime = fly.ArrvTimestamp
                        Y.ArrvStn = fly.ArrvStn
                        Y.State = 1
                    else:
                        emp_arrange[Y] = []
                        emp_arrange[Y].append([fly, order, Y.Task])
                        Y.ArrvTime = fly.ArrvTimestamp
                        Y.ArrvStn = fly.ArrvStn
                        Y.State = 1
                    if X not in Arranged_emp:
                        Arranged_emp.append(X)
                        Arranged_emp.append(Y)
                    if XY in rest_XY:
                        # print("rest_xy_information:",XY)
                        rest_XY.remove(XY)
        for xx in emp_arrange:
            for record_x in emp_arrange[xx]:
                flii = record_x[0]
                flii_order = record_x[1]
                xx_Task = record_x[2]
                record_information = [xx.EmpNo, i.date(), flii_order, flii.FltNum, flii.DptrTimestamp, flii.DptrStn,
                                      flii.ArrvTimestamp, flii.ArrvStn, xx_Task]
                Arranged_record[i].append(record_information)
                print("看看是谁被记下了：", xx.EmpNo, flii.FltNum)

# 记录不行的航班

# UncoversdFlight_data = []
# fli_Temp = []
# for i in dissatisfaction_flight:
#      fli_Temp = (i.DptrDate, i.DptrTime,i.DptrStn,i.ArrvStn,i.FltNum,i.Comp)
#      UncoversdFlight_data.append(fli_Temp)
# save_csv(UncoversdFlight_name,UncoversdFlight_data,path='D:/Desktop/2021 Fall/competition/Project_21143250003/output/test.csv')

# # test = pd.DataFrame(columns=UncoversdFlight_name,data=UncoversdFlight_data)
# # test.to_csv('D:/Desktop/2021 Fall/competition/Project_21143250003/output/UncoverdFlights_1_a_B.csv')
# print("我输出了鸭")

# 记录安排好的航班
# CrewRosters_data = []
# print("看看长度：",Arranged_record)
# for iii in date_rank:
#     for inf in Arranged_record[iii]:
#          # print("我怎么了", inf)
#          CrewRosters_data.append(inf)
# save_csv(CrewRosters_name,CrewRosters_data,path='D:/Desktop/2021 Fall/competition/Project_21143250003/output/CrewRosters_1_b_B.csv')
# print("我输出了鸭")

print("不满足机组配置航班数：", len(dissatisfaction_flight))
print("满足机组配置航班数：", len(fli) - len(dissatisfaction_flight))