import input
import datetime

#1.读取数据
emp = input.Read_crew(DataName='Data A-Crew.csv')
fli = input.Read_flight(DataName='Data A-Flight.csv')
print(fli)

#2.先进行排序
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
    data.append("day"+str(day))
print(data)

#data_rank = range(data_end-data_start)
#3.提取每日航班
# for i in range(1,delta+1):
#     for flight in fli:
#         if flight.DptrDate == data_rank[i] :
#             data.append(flight)
#
#
# for j in range(1,delta+1):
#     print(data[j])
day =0
for i in data_rank:
    for flight in fli:
        if flight.DptrDate == i :
            data.append(flight)
    day = day +1

for j in data:
    print(j)
