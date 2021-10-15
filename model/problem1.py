# -*- coding: utf-8 -*-
import argparse
import gurobipy as gp
from gurobipy import GRB
import input

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

    emp = input.Read_crew(args.data_crew_name)
    fli = input.Read_flight(args.data_flight_name)
    print(fli[1].CompCaptain)
    print(40)

    try:
        problem1 = gp.models()

        # Create variables
        x = problem1.addVars(emp.__len__(), fli.__len__(), args.kState, vtype=GRB.BINARY, name='x')

        # Add Constraints
        # Composition constraints
        problem1.addConstrs(gp.quicksum(x[i, j, 0] for i in range(emp.__len__())) >= fli[j].CompCaptain for j in range(fli.__len__()))
        problem1.addConstrs(gp.quicksum(x[i, j, 1] for i in range(emp.__len__())) >= fli[j].CompFirstOfficer for j in range(fli.__len__()))
        problem1.addConstrs()

        # Set objective
        problem1.setObjective(0, GRB.MINIMIZE)

        problem1.optimize()

        for v in problem1.getVars():
            print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % problem1.objVal)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')























