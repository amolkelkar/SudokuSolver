import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Using the relative import we fixed earlier
from .new_solver_copy import SudoKuSolver 

app = FastAPI()

initial_board = [
    [4, 0, 6, 5, 0, 0, 2, 0, 3],
    [2, 0, 3, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0, 0, 0, 4],
    [0, 0, 7, 4, 0, 0, 0, 0, 2],
    [0, 0, 1, 7, 0, 0, 9, 0, 5],
    [0, 0, 0, 0, 0, 0, 6, 7, 0],
    [0, 0, 0, 8, 0, 1, 0, 0, 6],
    [0, 0, 5, 0, 0, 4, 0, 9, 0],
    [0, 2, 0, 0, 5, 9, 0, 0, 0]
]

# The full HTML and JavaScript payload
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Sudoku Solver</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #1a1a1a; color: white; }
        .grid { display: grid; grid-template-columns: repeat(9, 40px); gap: 1px; width: 368px; margin: 20px auto; background: #444; border: 3px solid #fff; }
        .cell { width: 40px; height: 40px; background: #2b2b2b; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold; }
        .cell.changed { color: #00ffcc; background: #223333; }
        .cell.empty { color: transparent; }
        button { padding: 10px 20px; font-size: 1rem; cursor: pointer; background: #00ffcc; border: none; border-radius: 4px; font-weight: bold; color: #1a1a1a; margin-bottom: 20px; }
        button:hover { background: #00ccaa; }
    </style>
</head>
<body>
    <h1>Real-time Sudoku Solver</h1>
    <button onclick="startSolving()">Start Solver</button>
    <div class="grid" id="sudoku-grid"></div>

    <script>
        const gridDiv = document.getElementById('sudoku-grid');
        let ws;

        // Initialize empty board UI
        for (let i = 0; i < 81; i++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            gridDiv.appendChild(cell);
        }

        function startSolving() {
            // Prevent multiple clicks opening multiple connections
            if (ws && ws.readyState === WebSocket.OPEN) return;
            
            ws = new WebSocket("ws://localhost:8000/ws");
            
            ws.onmessage = function(event) {
                const board = JSON.parse(event.data);
                const cells = gridDiv.children;
                
                let idx = 0;
                for (let r = 0; r < 9; r++) {
                    for (let c = 0; c < 9; c++) {
                        const val = board[r][c];
                        cells[idx].textContent = val !== 0 ? val : "";
                        cells[idx].className = val === 0 ? 'cell empty' : 'cell changed';
                        idx++;
                    }
                }
            };
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize your custom solver
    solver = SudoKuSolver(initial_board)
    solver.first_call = False 
    
    try:
        # Loop over your generator
        for current_board_state in solver.solve_generator():
            
            # Send the board over the WebSocket
            await websocket.send_text(json.dumps(current_board_state))
            
            # Delay to visualize the backtracking
            await asyncio.sleep(0)
            
    except Exception as e:
        print(f"Connection closed or error: {e}")
    finally:
        await websocket.close()