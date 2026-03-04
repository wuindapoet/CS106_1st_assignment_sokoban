## Introduction:
- Assignment 1: DFS/BFS/UCS for Sokoban
- Author: Quynh Vo Thi Xuan
- Course: CS106 - Artificial Intelligence
- Class: CS106.Q23 - Second Semester of 2025-2026 school year
- From: University of Information Technology, VNU-HCM
---

## Project Discription:
- This project implements classical search algorithms **DFS (Depth-First Search)**, **BFS (Breadth-First Search)**, and **UCS (Uniform Cost Search)** to solve the Sokoban game.

- Sokoban is a puzzle game where a player pushes boxes to designated target positions within a warehouse maze. The challenge lies in finding a valid sequence of moves that places all boxes on goal tiles.

**Deadline:** 11/03/2026 – 11:59 PM  

### Implementation Requirement:
1. Implement:
    - `breadthFirstSearch(gameState)` in `solver.py`
    - `uniformCostSearch(gameState)` in `solver.py`

2. A DFS template is already provided in `solver.py`.   BFS and UCS can be implemented similarly or in your own approach.

3. To change the algorithm: Comment/uncomment corresponding lines in the `auto_move()` function inside `game.py`.

4. For UCS:
    - Use the provided `cost()` function.
    - `cost(node_action[1:])` calculates path cost as the number of steps **excluding box pushes**.

### Submission Requirements:
- Submit 2 files:
    - Source code (.zip): A file named **BT1_MSSV.zip** which contains full project source code having fully commented implementation requirements. Each line must clearly explain the *purpose, data structured used* & *algorithm logic*.
    - Report (.pdf): A file named **BT1_MSSV.pdf** which includes the explanation of *DFS, BFS, UCS implementation, Sokoban modeling, state representation, successor function, experimental comparison table, algorithm evaluation* and *discussion*. 
    - ***Note***: 
        - Non-PDF report files will lose 10/100 points.  
        - The report must be written carefully, clearly, and coherently. It should not be longer than 10 pages.  
        - Any plagiarism will receive 0 points
---

### How to run:
```bash
python3 Sokoban.py
```
---

### Demo: 
- **[First Assignment: DFS/BFS/UCS for Sokoban - Modeling Search Problem | CS106.Q23](link)**
---


