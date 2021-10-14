# -*- coding: utf-8 -*-
import argparse
import gurobipy as gp
from gurobipy import GRB

args = None

def parse_args():
    parser = argparse.ArgumentParser()

    # data parameters
    parser.add_argument('--data_name', type=str, default='', help='the name of the data')
    parser.add_argument('--data_dir', type=str, default='', help='the directory of the data')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    try:
        problem1 = gp.models()

        # Create variables
        x = problem1.addVars()

        # Add Constraints
        problem1.addConstrs()

        # Set objective
        problem1.setObjective(0, GRB.MINIMIZE)

        problem1.optimize()

        for v in problem1.getVars():
            print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % m.objVal)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')























