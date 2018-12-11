
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 16:50:38 2017

@author: alice
"""

# Solve the diet problem

from gurobipy import Model, GRB, multidict

# Model
m = Model("diet")

# Sets and parameters
categories, minNutrition, maxNutrition = multidict({
  'calories': [2000, GRB.INFINITY],
  'protein':  [50, GRB.INFINITY],
  'calcium':  [700, GRB.INFINITY]})

foods, cost, maxPortions = multidict({
  'bread':  [3, 4],
  'milk':   [2, 7],
  'eggs':   [3, 2],
  'meat':   [19, 3],
  'sweets': [15, 2]})

# Nutrition values for the foods
nutritionValues = {
  ('bread', 'calories'): 150,
  ('bread', 'protein'): 4,
  ('bread', 'calcium'): 2,
  ('milk', 'calories'): 120,
  ('milk', 'protein'): 8,
  ('milk', 'calcium'): 285,
  ('eggs', 'calories'): 160,
  ('eggs', 'protein'): 15,
  ('eggs', 'calcium'): 54,
  ('meat', 'calories'): 230,
  ('meat', 'protein'): 14,
  ('meat', 'calcium'): 4,
  ('sweets', 'calories'): 450,
  ('sweets', 'protein'): 4,
  ('sweets', 'calcium'): 22}


# Using Python looping constructs and m.addVar() to create decision variables:
buy = {}
for f in foods:
    buy[f] = m.addVar(0.0, maxPortions[f], name=f)

# The objective is to minimize the costs, using looping constructs:
m.setObjective(sum(buy[f]*cost[f] for f in foods), GRB.MINIMIZE)

# Nutrition constraints to respect minimum daily necessities:
for c in categories:
    m.addRange(
            sum(nutritionValues[f,c] * buy[f] for f in foods), minNutrition[c], maxNutrition[c], c)

def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nCost: %g' % m.objVal)
        print('\nBuy:')
        buyx = m.getAttr('x', buy)
        for f in foods:
            if buy[f].x > 0.0001:
                print('%s %g' % (f, buyx[f]))
    else:
        print('No solution')

# Solve
m.optimize()
printSolution()

print('\nAdding constraint: at most 6 servings of milk and eggs')
m.addConstr(buy['milk'] + buy['eggs'] <= 6, "limit_milk_eggs")

# Solve
m.optimize()
printSolution()