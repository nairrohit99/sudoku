import streamlit as st
from gurobipy import Model, GRB, quicksum
import numpy as np
import os

# Set path to your Gurobi license file
os.environ['GRB_LICENSE_FILE'] = r'gurobi\gurobi.lic'

def solve_sudoku(grid):
    model = Model("Sudoku")
    # Decision variables: x[i, j, k] is 1 if digit (k+1) is in cell (i, j)
    x = model.addVars(9, 9, 9, vtype=GRB.BINARY, name="x")
    
    # If a cell is pre-filled, fix its value
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                model.addConstr(x[i, j, grid[i][j] - 1] == 1)
    
    # Each cell must contain exactly one number
    for i in range(9):
        for j in range(9):
            model.addConstr(quicksum(x[i, j, k] for k in range(9)) == 1)
    
    # Each number must appear exactly once in each row
    for i in range(9):
        for k in range(9):
            model.addConstr(quicksum(x[i, j, k] for j in range(9)) == 1)
    
    # Each number must appear exactly once in each column
    for j in range(9):
        for k in range(9):
            model.addConstr(quicksum(x[i, j, k] for i in range(9)) == 1)
    
    # Each number appears exactly once in each 3x3 subgrid
    for bi in range(3):
        for bj in range(3):
            for k in range(9):
                model.addConstr(
                    quicksum(
                        x[3 * bi + di, 3 * bj + dj, k]
                        for di in range(3) for dj in range(3)
                    ) == 1
                )
    
    # Solve the model
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        solution = np.zeros((9, 9), dtype=int)
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    if x[i, j, k].x > 0.5:
                        solution[i][j] = k + 1
        return solution.tolist()  # Convert to list for Streamlit display
    else:
        return None

# --- Streamlit Interface ---

st.title("Sudoku Solver using Gurobi and Streamlit")
st.write(
    "Enter your Sudoku puzzle below. Each row should contain 9 numbers separated by spaces. "
    "Use 0 or leave blank for empty cells."
)

# Create text input for each row
row_inputs = []
for i in range(9):
    row_input = st.text_input(f"Row {i+1}", value="")
    row_inputs.append(row_input)

if st.button("Solve Sudoku"):
    try:
        puzzle = []
        for row_str in row_inputs:
            # Convert each row string to a list of integers
            row = [int(num) if num.strip() != "" else 0 for num in row_str.split()]
            if len(row) != 9:
                st.error("Each row must contain exactly 9 numbers separated by spaces.")
                st.stop()
            puzzle.append(row)
        # Call the solver
        solution = solve_sudoku(puzzle)
        if solution is None:
            st.error("No solution found. Please check your input puzzle.")
        else:
            st.success("Sudoku solved!")
            st.subheader("Input Puzzle")
            st.table(puzzle)
            st.subheader("Solution")
            st.table(solution)
    except Exception as e:
        st.error("Invalid input detected. Please enter valid numbers.")
