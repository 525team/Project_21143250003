import input
import datetime
import argparse
import random
import math


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
    if (len(x) + len(x) >=1) and (len(y) + len(z) >=1) and (len(x) + len(y) + len(Z_list) >=2):
        return 1
    else:
        return 0

#DeadHeading 当日和昨日的DH处理
def DeadHeading(fei, people, arranged_flight):
    fei_num = len(fei)
    Arrfli_num = len(arranged_flight)
    #先对rest_people 进行分类和排序
    rest_people = emp_grouping(people)
    rest_X = rest_people[0]
    rest_Y = rest_people[1]
    rest_Z = rest_people[2]
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

#配对机制
def assign_cap_fistofficer(feasible_group):
    pass

#全局更新参数:
def update_emp(emp,num,ArrvTime,ArrvStn):
    emp[num].ArrvTime = ArrvTime
    emp[num].ArrvStn = ArrvStn

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
                print("look look type:")
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
                print("look look type:")
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
                        print("new_cap的数量：", len(new_caplist))
                elif len(all2_sortedlist) == 0:
                    #说明z选完了。要把X全加上去
                    print("z选完了")
                    for x in captain_sortedlist:
                        new_caplist.append(x)
                else:
                    new_one = problity_choice(captain_sortedlist[0], all2_sortedlist[0], P)
                    print("look look type:")
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

#将C和F配对成机组
def pairXY(new_caplist,new_FOlist,pair):
    pair_xy = []
    while(len(pair_xy)<pair):
        for i,ix in enumerate(new_caplist):
            if ix!=0:
                for j,iy in enumerate(new_FOlist):
                    if iy!=0:
                        if y_choice(ix,iy) == 1:
                            print("成对：",len(pair_xy))
                            pair_xy.append([ix,iy])
                            # print("成对：",len(pair_xy))
                            new_caplist[i] = 0
                            new_FOlist[j] = 0
                            break
            if len(pair_xy) == pair:
                break
    for i in pair_xy:
        print("pair:",i[0],i[1])
    return pair_xy


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
    # A
    date_start = datetime.datetime.strptime("2021-08-11","%Y-%m-%d")
    date_end = datetime.datetime.strptime("2021-08-25","%Y-%m-%d")
    initial_arrvtime = datetime.datetime.strptime("2021-08-10 00:00","%Y-%m-%d %H:%M")

    # B
    # date_start = datetime.datetime.strptime("2019-08-01","%Y-%m-%d")
    # date_end = datetime.datetime.strptime("2019-08-31","%Y-%m-%d")
    # initial_arrvtime = datetime.datetime.strptime("2019-08-01 00:00","%Y-%m-%d %H:%M")

    initial_ArrvTime(emp,initial_arrvtime)     #对所有的飞行员ArrvTime进行初始化，因为类型相同才方便排序
    #2.机长分组
    emp_group = emp_grouping(emp)

    data = []
    date_rank = [date_start]
    delta = (date_end-date_start).days
    #生成一个日期排序
    for day in range(1,delta+1):
        date_rank.append(date_start+datetime.timedelta(days=day))
    print("这个数据的天数", len(date_rank))

    #testing: 飞行员状态更新 successful
    # emp_group[0][0].ArrvTime = datetime.datetime.strptime("2021-08-11 08:00", "%Y-%m-%d %H:%M")
    # emp_group[0][1].ArrvTime = datetime.datetime.strptime("2021-08-11 09:00", "%Y-%m-%d %H:%M")
    # emp_group_sorted = emp_grouping(emp)



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
    # print("checj:",flight_day_num)
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

    flight_copy = flight_day   #对航班分组进行备份
    dissatisfaction_flight = []
    emp_copy = emp_group
    #每天处理航班, A15 days, B 31 days
    for i in date_rank:
        #print("coming:", flight_day[i.date()])
        F_day = flight_day[i.date()]  # 该天的航班序列
        F_num = flight_day_num[i.date()]  # 该天的航班序列
        Fei_fli = []  #记录当天废掉的航班
        Arranged_fli = []  #记录当天安排好的航班
        Arranged_emp = []  #记录当天安排好的人

        print("***************************************************今天是第",i, "*******************************************************")

        # 机长资格check,需要重新排序

        new_xlist,new_ylist, pair_num = pair_CF(emp_ranking(emp_group[0]),emp_ranking(emp_group[1]),emp_ranking(emp_group[2]),0.65)
        X_list = new_xlist  # 机长
        Y_list = new_ylist   # 副机长

        print("新的机长列表：", new_xlist, new_ylist)
        new_xy = pairXY(new_xlist,new_ylist,pair_num)
        #备份用，一旦用过就删除，剩下的就是闲人
        Emp_rest = emp
        new_xy_copy =new_xy
        Capnum = 0
        XY = new_xy[Capnum]
        rest_XY = new_xy



        while (len(F_day)!=0):
            # 资格测试
            print("feasibility_check:")
            # flag_feasibility, y_list, fly_list = feasibility_check(X, Y_list, F_day)
            flag_feasibility, xy, fly_list = feasibility_check_fli(XY, F_day)

            if flag_feasibility == 1:   #存在这样的航班
                #飞行 -> 记录 -> 删除
                X = xy[0]
                Y = xy[1]
                fly = fly_list[0]
                fly_num = fly_list[1]
                print("现在是", X.EmpNo,Y.EmpNo, "在执行飞行", fly)
                Arranged_fli.append(fly)
                update_emp(emp,X.No,fly.ArrvTimestamp,fly.ArrvStn)
                update_emp(emp,Y.No,fly.ArrvTimestamp,fly.ArrvStn)
                if X in emp_arrange:
                    emp_arrange[X].append(fly)
                    X.ArrvTime = fly.ArrvTimestamp
                    X.ArrvStn = fly.ArrvStn
                    X.State = 0
                else:
                    emp_arrange[X] = []
                    emp_arrange[X].append(fly)
                    X.ArrvTime = fly.ArrvTimestamp
                    X.ArrvStn = fly.ArrvStn
                    X.State = 0
                if Y in emp_arrange:
                    emp_arrange[Y].append(fly)
                    Y.ArrvTime = fly.ArrvTimestamp
                    Y.ArrvStn = fly.ArrvStn
                    Y.State = 1
                else:
                    emp_arrange[Y] = []
                    emp_arrange[Y].append(fly)
                    Y.ArrvTime = fly.ArrvTimestamp
                    Y.ArrvStn = fly.ArrvStn
                    Y.State = 0
                if X not in Arranged_emp:
                    Arranged_emp.append(X)
                    Arranged_emp.append(Y)
                if xy in rest_XY:
                    rest_XY.remove(xy)
                    # for xxyy in rest_XY:
                    #      print("剩下的机组：",xxyy)
                del F_day[fly_num]
            elif (len(new_xy)!=0): #机组还有剩余
                print("这组人下班,剩余", len(new_xy),"人",Capnum)
                new_xy[0][0].State = 3
                new_xy[0][1].State = 3
                print("Capnum:", new_xy[Capnum][0], new_xy[Capnum][1])
                del new_xy[0]
                # print("Capnum:",new_xy[Capnum][0],new_xy[Capnum][1])
                if (len(new_xy)!=0):
                    XY = new_xy[Capnum]  # 机长
                # else
                # del emp_group[0][Capnum]
                # new_xy[Capnum][0].State = 3
                # new_xy[Capnum][1].State = 3
                # del new_xy[Capnum]
                #     del X_list[Capnum]
                # if (len(X_list) == 0 ) and (len(Z_list)!= 0):  #剩余没机长了
                #     print("我来借人")
                #     X_list.append(Z_list[0])
                #     del Z_list[0]
                # else:
                #     print("此人不符合条件，换下一个人:", X_list[Capnum])
                #     X_list[Capnum].State = 3
                #     del X_list[Capnum]
                #
                #     print("Y:,", Y)
                #     # Y_num = None表示没有用上副机长，正机长自身不符合条件
                #     if  Y != None:
                #         # 表示Y用完了。
                #         # print("Y用完了：",Y_num)
                #         print("删除了Y：",Y_list[Y_num])
                #         Y_list[Y_num] = 3
                #         del Y_list[Y_num]
                #         #del Y_list[Y_num]
                #     if len(X_list) == 0:
                #         print("X没人了:")
                #         continue
                #     else:
                #         print("X还有人在，顶上去：",X_list[0])
                #         X = X_list[0]
                # if Capnum < len(emp_group[0])-1:
                #     Capnum = Capnum + 1
                #     print("Capnum:",emp_group[0][Capnum])
                #     X = emp_group[0][Capnum]  # 机长
                # else
               # del emp_group[0][Capnum]
            else:
                print("oh,no,处理不了了！")
                for leave in F_day:
                    dissatisfaction_flight.append(leave)
                    Fei_fli.append(leave)
                print("F_day的数量:",F_day)
                F_day = []
# for empe in emp:
#     print("最终的到达机场：", empe.ArrvTime)

        print("已经安排好的航班：",len(Arranged_fli))
        if (len(Fei_fli)!=0):
            print("Looking:", Fei_fli)
            Arrfli_num = len(Arranged_fli)
            # 先对rest_people 进行分类和排序
            rest_people = emp_grouping(Emp_rest)
            rest_X = rest_people[0]
            rest_Y = rest_people[1]
            rest_Z = rest_people[2]
            Record = []
            Yesterday_DH = []
            # 遍历一下fei
            for i, fei_fli in enumerate(Fei_fli):
                print("废掉的航班：", fei_fli)
                for j, arr_fli in enumerate(Arranged_fli):
                    if arr_fli.ArrvStn == fei_fli.DptrStn and (judge_fly(rest_X, rest_Y, rest_Z) == 1) and (((( fei_fli.DptrTimestamp - arr_fli.ArrvTimestamp).seconds) / 60) >= 40):  # 当天有闲人并且废掉的航班在当天有飞机飞过去
                        # 1.JX航班到达机场 = Miss机场的出发机场 & 有闲人 & Miss航班出发时间要比JX航班到达时间要多40分钟
                        print("可以飞，接下来是找人")
                        for jx_num, jx in enumerate(rest_X):
                            if jx != 0:
                                if (jx.ArrvStn == arr_fli.DptrStn):
                                    #找到人了
                                    print("找到X了：",jx)
                                    update_emp(emp, jx.No, fei_fli.ArrvTimestamp, fei_fli.ArrvStn)
                                    X = jx
                                    Saved_fli = fei_fli
                                    if X in emp_arrange:
                                        emp_arrange[X].append(Saved_fli)
                                        X.ArrvTime = Saved_fli.ArrvTimestamp
                                        X.ArrvStn = Saved_fli.ArrvStn
                                        X.State = 0
                                    else:
                                        emp_arrange[X] = []
                                        emp_arrange[X].append(Saved_fli)
                                        X.ArrvTime = Saved_fli.ArrvTimestamp
                                        X.ArrvStn = Saved_fli.ArrvStn
                                        X.State = 0
                                    rest_X[jx_num] = 0
                                    break
                                else:
                                    #没有X
                                    print("这个人不行：", jx)
                        for jxy_num, jxy in enumerate(rest_Y):
                            if jxy !=0 :
                                if (jxy.ArrvStn == arr_fli.DptrStn):
                                    # 找到人了
                                    print("找到Y了：", jxy)
                                    update_emp(emp, jxy.No, fei_fli.ArrvTimestamp, fei_fli.ArrvStn)
                                    Y = jxy
                                    Saved_fli = fei_fli
                                    if Y in emp_arrange:
                                        emp_arrange[Y].append(Saved_fli)
                                        Y.ArrvTime = Saved_fli.ArrvTimestamp
                                        Y.ArrvStn = Saved_fli.ArrvStn
                                        Y.State = 1
                                    else:
                                        emp_arrange[Y] = []
                                        emp_arrange[Y].append(Saved_fli)
                                        Y.ArrvTime = Saved_fli.ArrvTimestamp
                                        Y.ArrvStn = Saved_fli.ArrvStn
                                        Y.State = 1
                                    rest_Y[jxy_num] = 0
                                    Arranged_fli.append(fei_fli)
                                    break
                                else:
                                    print("这个人不行：", jxy)
            dissatisfaction_flight = deleFlight(dissatisfaction_flight, Saved_fli)
            Fei_fli[i] = 0
            '''         
            for i, fei_fli in enumerate(Fei_fli[0]):
                print("废掉的航班：", fei_fli)
                for j, arr_fli in enumerate(arranged_flight):
                    if arr_fli != 0:
                        if arr_fli.ArrvStn == fei_fli.DptrStn and (
                                judge_fly(rest_X, rest_Y, rest_Z) == 1):  # 当天有闲人并且废掉的航班在当天有飞机飞过去
                            # 判断是否有人匹配航班
                            for jx_num, jx in enumerate(rest_X):
                                if jx != 0:
                                    if (jx.ArrvStn == arr_fli.DptrStn) and (
                                            (((arr_fli.ArrvTimestamp - fei_fli.DptrTimestamp).seconds) / 60) >= 40):
                                        # JX_flag, Ylist, JX_flight = feasibility_check(jx,rest_Y,arranged_flight)
                                        # if JX_flag == 1:
                                        #     print("找到人了：",Ylist)
                                        for jxy_num, jxy in enumerate(rest_Y):
                                            if jxy != 0:
                                                if (jxy.ArrvStn == arr_fli.DptrStn):
                                                    print("此处找到人了")
                                                    Record.append([jx, jxy, [arr_fli, j], [fei_fli, i]])
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

            '''
            '''
            param = DeadHeading(Fei_fli[0],people=Emp_rest,arranged_flight=Arranged_fli)
            for par in param:
                X = par[0]
                Y = par[1]
                JX_fli = par[2][0]
                Saved_fli = par[3][0]
                Saved_fli_num = par[3][1]
                print("checking:", Saved_fli)
                print("现在是", X.EmpNo, Y.EmpNo, "在", JX_fli, "上DeadHeading")
                Arranged_fli.append(Saved_fli)
                update_emp(emp, X.No, Saved_fli.ArrvTimestamp, Saved_fli.ArrvStn)
                update_emp(emp, Y.No, Saved_fli.ArrvTimestamp, Saved_fli.ArrvStn)
                if X in emp_arrange:
                    emp_arrange[X].append(Saved_fli)
                    X.ArrvTime = Saved_fli.ArrvTimestamp
                    X.ArrvStn = Saved_fli.ArrvStn
                    X.State = 0
                else:
                    emp_arrange[X] = []
                    emp_arrange[X].append(Saved_fli)
                    X.ArrvTime = Saved_fli.ArrvTimestamp
                    X.ArrvStn = Saved_fli.ArrvStn
                    X.State = 0
                if Y in emp_arrange:
                    emp_arrange[Y].append(Saved_fli)
                    Y.ArrvTime = Saved_fli.ArrvTimestamp
                    Y.ArrvStn = Saved_fli.ArrvStn
                    Y.State = 1
                else:
                    emp_arrange[Y] = []
                    emp_arrange[Y].append(Saved_fli)
                    Y.ArrvTime = Saved_fli.ArrvTimestamp
                    Y.ArrvStn = Saved_fli.ArrvStn
                    Y.State = 1
                if X not in Arranged_emp:
                    Arranged_emp.append(X)
                    Arranged_emp.append(Y)
                print("Saved_fli:", Saved_fli.FltNum, "JX_fli:", Fei_fli[Saved_fli_num], "全体有错航班：", dissatisfaction_flight)
                dissatisfaction_flight = deleFlight(dissatisfaction_flight,Saved_fli)
                Fei_fli[Saved_fli_num] = 0
                '''
for i in dissatisfaction_flight:
        print("处理不了航班：", i)
        print("...")


'''
            if X.Base == F_day[0].DptrStn:
                # 分配机长并且同时记录ArrvTime和ArrvStn（到达机场），这里需要加个判断机长是不是用完了？动用type = 3 全能机长
                if X in emp_arrange:
                    emp_arrange[X].append(F_day[0])
                    X.ArrvTime = F_day[0].ArrvTimestamp
                    X.ArrvStn = F_day[0].ArrvStn
                else:
                    emp_arrange[X] = []
                    emp_arrange[X].append(F_day[0])
                    X.ArrvTime = F_day[0].ArrvTimestamp
                    X.ArrvStn = F_day[0].ArrvStn
            else:
                Capnum = Capnum +1
            if Y.Base == F_day[0].DptrStn:
                # 分配一名副机长，同时记录ArrvTime和ArrvStn（到达机场）
                if Y in emp_arrange:
                    emp_arrange[Y].append(F_day[0])
                    Y.ArrvTime = F_day[0].ArrvTimestamp
                    Y.ArrvStn = F_day[0].ArrvStn
                else:
                    emp_arrange[Y] = []
                    emp_arrange[Y].append(F_day[0])
                    Y.ArrvTime = F_day[0].ArrvTimestamp
                    Y.ArrvStn = F_day[0].ArrvStn
            else:
                FistOfficernum = FistOfficernum + 1
            #记录完信息，从列表李删除该航班信息
            print("删除列表：", F_day[0])
            del F_day[0]
            #del F_num[0]

            #检测剩余航班有满足继续飞行的要求：

            for j,flight in enumerate(F_day):
                #满足飞行条件的话，继续执飞，否则就跳过
                if flight.DptrTimestamp > X.ArrvTime:
                    time_error = (flight.DptrTimestamp - X.ArrvTime).seconds
                    print("时间差：", time_error)
                    if (X.ArrvStn == flight.DptrStn) and (time_error >= args.MinCT * 60):  # 满足进行飞行,将该项置顶
                        # 更新机长和副机长的航班信息
                        emp_arrange[X].append(flight)
                        X.ArrvTime = flight.ArrvTimestamp
                        X.ArrvStn = flight.ArrvStn

                        emp_arrange[Y].append(flight)
                        Y.ArrvTime = flight.ArrvTimestamp
                        Y.ArrvStn = flight.ArrvStn

                        # 删除信息
                        print("删除航班号码", flight.FltNum)
                        # del F_num[j]
                        del F_day[j]
                        # for flig in F_day:
                        #      print("剩余航班号码", flig)
                        # continue
                    else:
                        # del X
                        # del Y
                        print("时间差：", time_error)
                        a = len(F_day)
                        print("no",a)
                else:
                    if flight == F_day[-1]:
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
'''