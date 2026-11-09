
#the robot should suite a maze constructed form 16*16 cell
# each cell of width 16.8 cm and with walls of 5cm high

#LIST OF THINGS I NEED
#RECEIVE SPIN/M data or whatever and convert to velocity
#Use a filter
#Use a PID to find error between target cell and current position and find velocity needed (outer)
#Use an inner PID to find error between velocity on wheels and veclotiy needed. (inner)
#SOLVE DIFFERENTIAL EQUATION TO GET KP AND KD
#ADD STEERING
cell_num_x=16
cell_num_y=16
wall_sense_distance = 100 #mm assumes hull is 100x100mm
sensors = []
sensor_readings = []
class MicroMouse():
    def __init__(self,x,y,mass,velocity,lateral_velocity,acceleration,orientation):
        self.x=x
        self.y=y
        self.velocity=velocity
        self.lateral_velocity = lateral_velocity
        self.acceleration=acceleration
        self.mass = mass 
        self.grid = [[Cell(999999,x,y) for y in range(cell_num_y)] for x in range(cell_num_x)]
        self.current_cell = self.grid[self.x][self.y]
        self.orientation = orientation
    def updateVelocity(self):
        #Using moving average filter
        sample_window = 5
        velocities = self.sampleVelocity(sample_window)
        self.velocity = sum(velocities)/sample_window
    def sampleVelocity(self,sample_window):
        return [110,120,100] #PLACEHOLDER!!!!
    def PID_pos(self,next_cell): #For straights
        #Placeholder values
        MAX_INTEGRAL = 2 
        dt = 0.01
        Kp_pos = 100 
        Kd_pos = 10
        Ki_pos = 1
        Kp_steer = 100 
        Kd_steer = 10
        Ki_steer = 1
        alpha = 0.3
        steer_error =min(next_cell.x-self.x,next_cell.y-self.y)
        pos_error = max(next_cell.x-self.x,next_cell.y-self.y)
        self.updateVelocity()
        steer_integral_error = 0
        steer_integral_error += steer_error*dt
        if (steer_integral_error > MAX_INTEGRAL): steer_integral_error = MAX_INTEGRAL #ANTI SUPER BUILD UP
        if (steer_integral_error < -MAX_INTEGRAL): steer_integral_error = -MAX_INTEGRAL
        pos_integral_error = 0
        pos_integral_error += pos_error*dt
        if (pos_integral_error > MAX_INTEGRAL): pos_integral_error = MAX_INTEGRAL #ANTI SUPER BUILD UP
        if (pos_integral_error < -MAX_INTEGRAL): pos_integral_error = -MAX_INTEGRAL
        velocity_throttle = Kp_pos*pos_error-Kd_pos*self.velocity + Ki_pos*pos_integral_error
        velocity_steer = Kp_steer*steer_error-Kd_steer*self.lateral_velocity + Ki_steer*steer_integral_error
        target_voltage = alpha*(velocity_throttle+velocity_steer) #placeholder equation
    def PID_wheel_speed(self,next_cell):
        pass
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
