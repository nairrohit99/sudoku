from flask import Flask, render_template, request, redirect, url_for, flash
from gurobipy import Model, GRB, quicksum
import numpy as np
import os

os.environ['GRB_LICENSE_FILE'] = r'gurobi\gurobi.lic'


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

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
        return solution.tolist()  # Convert to list for JSON/templating compatibility
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Build the grid from the submitted form data.
        grid = []
        try:
            for i in range(9):
                # Expecting numbers separated by spaces; empty cells can be left blank or as 0
                row_str = request.form.get(f"row{i}", "")
                # Convert each row into a list of integers (0 represents an empty cell)
                row = [int(num) if num.strip() != "" else 0 for num in row_str.split()]
                if len(row) != 9:
                    flash("Each row must contain 9 numbers separated by spaces.")
                    return redirect(url_for("index"))
                grid.append(row)
        except Exception as e:
            flash("Invalid input detected. Please enter valid numbers.")
            return redirect(url_for("index"))
        
        solution = solve_sudoku(grid)
        if solution is None:
            flash("No solution found. Please check your input puzzle.")
            return redirect(url_for("index"))
        else:
            return render_template("index.html", grid=grid, solution=solution)
    # GET request: show the form
    return render_template("index.html", grid=None, solution=None)

if __name__ == "__main__":
    app()
