param NUM_ROWS integer, >= 1, default 8;  # Number of rows in the chessboard
param NUM_COLS integer, >= 1, default 8;  # Number of columns in the chessboard

set Rows = 1..NUM_ROWS;  # Set of row indexes
set Cols = 1..NUM_COLS;  # Set of column indexes

set CELL = {Rows, Cols};  # Set of chessboard cells

param VALUE{CELL} >= 0, integer, default 1;    # Cells values (in the classical problem they are all 1, where the aim is maximizing the "number" of queens disposed)

var x{CELL} binary; # we introduce a binary variable for every cell (1 if there is a queen, 0 otherwise)

# Objective function definition
maximize MaxVal:
         sum{(i,j) in CELL} VALUE[i,j] * x[i,j];

# first constraints family: there is at maximum one queen for every row
subject to maxOneQueenForRow{i in Rows}:
        sum{j in Cols} x[i,j] <= 1;

# second constraints family: there is at maximum one queen for every column
subject to maxOneQueenForColumn{j in Cols}:
        sum{i in Rows} x[i,j] <= 1;

# third constraints family: diagonals:
#set RminusC = (1-NUM_COLS)..(NUM_ROWS-1);
subject to maxOneOnDiag{d in (1-NUM_COLS)..(NUM_ROWS-1)}:
        sum{(i,j) in CELL : i-j = d} x[i,j] <= 1;

# fourth constraints family: anti-diagonals:
#set RplusC = 2..NUM_ROWS+NUM_COLS;
subject to maxOneOnAntiDiag{d in 2..NUM_ROWS+NUM_COLS}:
        sum{(i,j) in CELL : i+j = d} x[i,j] <= 1;
