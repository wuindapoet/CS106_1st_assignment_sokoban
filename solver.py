import sys
import collections
import numpy as np
import heapq
import time
import numpy as np
global posWalls, posGoals
class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0
        self.len = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

"""Load puzzles and define the rules of sokoban"""

def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n','') for x in layout]
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ': layout[irow][icol] = 0   # free space
            elif layout[irow][icol] == '#': layout[irow][icol] = 1 # wall
            elif layout[irow][icol] == '&': layout[irow][icol] = 2 # player
            elif layout[irow][icol] == 'B': layout[irow][icol] = 3 # box
            elif layout[irow][icol] == '.': layout[irow][icol] = 4 # goal
            elif layout[irow][icol] == 'X': layout[irow][icol] = 5 # box on goal
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)]) 

    # print(layout)
    return np.array(layout)
def transferToGameState2(layout, player_pos):
    """Transfer the layout of initial puzzle"""
    maxColsNum = max([len(x) for x in layout])
    temp = np.ones((len(layout), maxColsNum))
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]

    temp[player_pos[1]][player_pos[0]] = 2
    return temp

def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0]) # e.g. (2, 2)

def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5))) # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))

def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1)) # e.g. like those above

def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5))) # e.g. like those above

def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)

def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper(): # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls

def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox: # the move was a push
            action.pop(2) # drop the little letter
        else:
            action.pop(3) # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else: 
            continue     

    return tuple(tuple(x) for x in legalActions) # e.g. ((0, -1, 'l'), (0, 1, 'R'))

def updateState(posPlayer, posBox, action):
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer # the previous position of player
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]] # the current position of player
    posBox = [list(x) for x in posBox]
    if action[-1].isupper(): # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox

def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                    [2,5,8,1,4,7,0,3,6],
                    [0,1,2,3,4,5,6,7,8][::-1],
                    [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6][::-1],
                    [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False

"""Implement all approcahes"""
def depthFirstSearch(gameState):
    """Implement depthFirstSearch approach"""
    """## ORIGINAL CODE
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])
    exploredSet = set()
    actions = [[0]] 
    temp = []
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])
    return temp
    """
    # Lấy vị trí ban đầu của các box trong game và của player
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    # Tạo state ban đầu gồm vị trí player và vị trí các box
    startState = (beginPlayer, beginBox)

    # parent: dictionary lưu thông tin state cha
    # key: state hiện tại
    # value: (state cha, action dẫn tới state hiện tại), đồng thời parent cũng đóng vai trò là visited set
    parent = {startState: (None, None)}

    # frontier: stack với mỗi phần tử là một state
    frontier = collections.deque([startState])

    # Lặp cho đến khi frontier rỗng
    while frontier:
        # Lấy state ở cuối stack
        state = frontier.pop()
        # Tách state thành vị trí player và vị trí các box
        posPlayer, boxState = state
        #Kiểm tra xem các box đã ở vị trí goal chưa
        if isEndState(boxState):
            # Danh sách lưu các action từ start đến goal
            actions = []
            curr = state
            # Lần ngược lại các state cha để reconstruct đường đi
            while parent[curr][1] is not None:
                actions.append(parent[curr][1])
                curr = parent[curr][0]
            # Đảo ngược lại để được thứ tự từ start đến goal
            return actions[::-1]

        # Lấy danh sách các action hợp lệ từ state hiện tại
        legal = legalActions(posPlayer, boxState)

        # Sắp xếp action: ưu tiên push box (chữ hoa) trước move thường (chữ thường)
        legal = sorted(legal, key=lambda a: a[-1].islower(), reverse=True)

        # Duyệt qua từng action hợp lệ
        for action in legal:
            # Tính toán state mới sau khi thực hiện action
            newPosPlayer, newPosBox = updateState(posPlayer, boxState, action)
            # Nếu state box mới rơi vào deadlock thì bỏ qua
            if isFailed(newPosBox):
                continue
            #Tạo state mới từ vị trí player và box sau khi cập nhật
            newState = (newPosPlayer, newPosBox)
            # Nếu state này chưa được thăm (chưa có trong parent)
            if newState not in parent:
                # Lưu lại state cha và action dẫn tới state này
                parent[newState] = (state, action[-1])
                # Đưa state mới vào stack để tiếp tục DFS
                frontier.append(newState)
    #trả về danh sách rỗng nếu không có solution
    return []

def breadthFirstSearch(gameState):
    """Implement breadthFirstSearch approach"""

    # lấy vị trí ban đầu của các box và của player
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    
    # trạng thái ban đầu gồm vị trí player và vị trí các box
    startState = (beginPlayer, beginBox)

    # frontier: hàng đợi (queue) dùng cho BFS
    # mỗi phần tử gồm (state, danh sách hành động đã thực hiện)
    frontier = collections.deque([(startState, [])])

    # tập các trạng thái đã duyệt để tránh lặp lại
    exploredSet = set()
    
    # Lặp cho đến khi frontier rỗng
    while frontier:
        # lấy phần tử đầu hàng đợi (FIFO)
        state, actions = frontier.popleft()
        # tách vị trí player và box từ state
        posPlayer, posBox = state
        # kiểm tra nếu tất cả box đã vào goal
        if isEndState(posBox):
            # nếu đạt goal thì trả về danh sách actions
            return actions
        # nếu trạng thái này đã được duyệt trước đó thì bỏ qua
        if state in exploredSet:
            continue
        #thêm trạng thái vào tập explored
        exploredSet.add(state)
        
        # duyệt tất cả các hành động hợp lệ từ trạng thái hiện tại
        for action in legalActions(posPlayer, posBox):
            # cập nhật vị trí mới của player và box sau khi thực hiện action
            newPosPlayer, newPosBox = updateState(posPlayer, posBox, action)
            # nếu trạng thái mới là trạng thái thất bại (deadlock) thì bỏ qua
            if isFailed(newPosBox):
                continue
            # tạo trạng thái mới
            newState = (newPosPlayer, newPosBox)
            # cập nhật danh sách hành động, action[-1] lấy ký tự cuối (u,d,l,r,U,D,L,R)
            newActions = actions + [action[-1]]
            # thêm trạng thái mới vào hàng đợi frontier
            frontier.append((newState, newActions))
    # trả về danh sách rỗng nếu không có solution
    return []

def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])

def uniformCostSearch(gameState):
    """Implement uniformCostSearch approach"""

    # Lấy vị trí ban đầu của các box và của player
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    # trạng thái ban đầu gồm vị trí player và vị trí các box
    startState = (beginPlayer, beginBox)

    # frontier: hàng đợi ưu tiên (priority queue)
    # UCS sẽ luôn lấy trạng thái có chi phí nhỏ nhất để mở rộng
    frontier = PriorityQueue()

    # Đưa trạng thái ban đầu vào frontier với cost = 0
    frontier.push((startState, []), 0)

    # tập các trạng thái đã duyệt để tránh lặp lại
    exploredSet = set()

    # lặp cho đến khi frontier rỗng
    while not frontier.isEmpty():
        # lấy trạng thái có chi phí nhỏ nhất ra khỏi frontier
        state, actions = frontier.pop()
        # tách vị trí player và box
        posPlayer, posBox = state
        # nếu trạng thái đã được duyệt trước đó thì bỏ qua
        if state in exploredSet:
            continue
        # đánh dấu trạng thái đã được duyệt
        exploredSet.add(state)
        # kiểm tra nếu tất cả box đã vào goal
        if isEndState(posBox):
            # trả về danh sách hành động tìm được
            return actions
        # duyệt tất cả các hành động hợp lệ từ trạng thái hiện tại
        for action in legalActions(posPlayer, posBox):
            # cập nhật vị trí mới của player và box sau khi thực hiện action
            newPosPlayer, newPosBox = updateState(posPlayer, posBox, action)
            # nếu trạng thái mới là deadlock thì bỏ qua
            if isFailed(newPosBox):
                continue
            # tạo trạng thái mới
            newState = (newPosPlayer, newPosBox)
            # chỉ thêm vào frontier nếu trạng thái chưa được duyệt
            if newState not in exploredSet:
                # cập nhật danh sách hành động
                newActions = actions + [action[-1]]
                # tính chi phí của đường đi mới
                newCost = cost(newActions)
                # thêm trạng thái mới vào frontier với độ ưu tiên là chi phí
                frontier.push((newState, newActions), newCost)
    # no solution = danh sách rỗng
    return []

"""Read command"""
def readCommand(argv):
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('assets/levels/' + options.sokobanLevels,"r") as f: 
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    return args

def get_move(layout, player_pos, method):
    time_start = time.time()
    global posWalls, posGoals
    # layout, method = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState2(layout, player_pos)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)
    
    if method == 'dfs':
        result = depthFirstSearch(gameState)
    elif method == 'bfs':        
        result = breadthFirstSearch(gameState)
    elif method == 'ucs':
        result = uniformCostSearch(gameState)
    else:
        raise ValueError('Invalid method.')
    time_end=time.time()
    print(result)
    print('Runtime of %s: %.2f second.' %(method, time_end-time_start))
    return result