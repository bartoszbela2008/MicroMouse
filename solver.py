
#the robot should suite a maze constructed form 16*16 cell
# each cell of width 16.8 cm and with walls of 5cm high

cell_num_x=16
cell_num_y=16
wall_sense_distance = 100 #mm assumes hull is 100x100mm
sensors = []
sensor_readings = []
class MicroMouse():
    def __init__(self,x,y,mass,velocity,acceleration,orientation):
        self.x=x
        self.y=y
        self.velocity=velocity
        self.acceleration=acceleration
        self.mass = mass 
        self.grid = [[Cell(999999,x,y) for y in range(cell_num_y)] for x in range(cell_num_x)]
        self.current_cell = self.grid[self.x][self.y]
        self.orientation = orientation
    def findNeighbors(self,cell):
            neighbors =[]
            directions = ["N","S","E","W"]
            increment = {"N":(cell.x,cell.y-1), "S":(cell.x, cell.y+1),"E":(cell.x+1,cell.y),"W":(cell.x-1,cell.y)}
            for direction in directions: 
                position = increment[direction]
                if self.isInBounds(position[0],position[1]) and not cell.detected_walls[direction]:
                    neighbors.append(self.grid[position[0]][position[1]])
            return neighbors     
    def isInBounds(self,x,y):
        if(0<=x<cell_num_x and 0<=y<cell_num_y):
            return True
    def updateWalls(self):
        directions = ["N","S","E","W"]
        opposites = {"N":"S","S":"N","E":"W","W":"E"}
        for sensor in sensors:
            if sensor.reading<= wall_sense_distance:
                self.current_cell.detected_walls[sensor.direction] = True
                increment = {"N":(self.current_cell.x,self.current_cell.y-1), "S":(self.current_cell.x, self.current_cell.y+1),"E":(self.current_cell.x+1,self.current_cell.y),"W":(self.current_cell.x-1,self.current_cell.y)}
                position = increment[sensor.direction] # of cell in sensor direction
                if(self.isInBounds(position[0],position[1])):
                    self.grid[position[0]][position[1]].detected_walls[opposites[sensor.direction]] = self.current_cell.detected_walls[sensor.direction]
    def floodFill(self,target_cells):
        queue = []
        for x in range(cell_num_x):
            for y in range(cell_num_y):
                self.grid[x][y].distance = 999999
        for cell in target_cells:
            queue.append(cell)
            cell.distance = 0
        while len(queue) != 0:
            currentCell = queue.pop(0)
            neighbors = self.findNeighbors(currentCell)
            for neighbor in neighbors:
                if neighbor.distance > currentCell.distance + 1:
                    neighbor.distance = currentCell.distance + 1
                    queue.append(neighbor)
    def selectCell(self):
        self.current_cell.visited = True
        neighbors= self.findNeighbors(self.current_cell)
        min_distance = min(cell.distance for cell in neighbors)
        best_cells = [cell for cell in neighbors if cell.distance == min_distance]
        for cell in best_cells:
            if(len(best_cells) != 1 and not cell.visited):
                newCell = cell
            elif(len(best_cells)==1):
                newCell=cell
    def move(self,target):
        direction = self.targetDirection(target)
        if(self.orientation!=direction):
               self.turn(direction)
        
    def targetDirection(self,target):
        directions = ["N","S","E","W"]
        if(self.current_cell.x == target.x):
            # check north south
            if(self.current_cell.y < target.y):
                direction = "S"
            else:
                direction = "N"
        elif(self.current_cell.x == target.y):
            if(self.current_cell.x == target.x):
                # check east west
                if(self.current_cell.x < target.x):
                    direction = "E"
                else:
                    direction = "W"
        return direction
    def turn(self,direction):
        pass
class Cell:
    def __init__(self,distance,x,y):
        self.x = x
        self.y = y
        self.visited=False
        self.distance = distance
        #Dictionary
        self.walls = {"N":True,"S":True,"E":True,"W":True}  
        self.detected_walls = {"N":False,"S":False,"E":False,"W":False}  
