set GIFTS; # Xmas Gifts

param BUDGET integer, >= 1;  # Wallet Capacity
param VALUE{GIFTS} >= 0;    # Gifts values
param PRICE{GIFTS} >= 0;   # Price to buy each gift

var x{GIFTS} binary; # Binary variable for each track: it indicates if we choose the track (value 1) or not (value 0)

# Objective function definition: maximizing the total value
maximize GiftsTotalValue:
         sum{i in GIFTS} VALUE[i] * x[i];

# Instead if I want to minimize the unused part of the CD:
minimize BudgetLeft:
         BUDGET - sum{i in GIFTS} PRICE[i] * x[i];

# Constraint due to the limited wallet capacity
subject to LimitedBudget:
        sum{i in GIFTS} PRICE[i] * x[i] <= BUDGET;
