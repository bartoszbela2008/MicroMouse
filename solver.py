
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
    def __init__(self,x,y,mass,velocity,lateral_velocity,acceleration,orientation,motor_R,motor_L):
        self.x=x
        self.y=y
        self.velocity=velocity
        self.lateral_velocity = lateral_velocity
        self.acceleration=acceleration
        self.mass = mass 
        self.grid = [[Cell(999999,x,y) for y in range(cell_num_y)] for x in range(cell_num_x)]
        self.current_cell = self.grid[self.x][self.y]
        self.orientation = orientation
        self.pos_integral_error = 0
        self.steer_integral_error = 0
        self.motor_R = motor_R
        self.motor_L = motor_L
        self.velocity_integral_error = 0
    def updateVelocity(self):
        #Using moving average filter
        sample_window = 5
        velocities = self.sampleVelocity(sample_window)
        self.velocity = sum(velocities)/sample_window
    def sampleVelocity(self,sample_window):
        return [110,120,100] #PLACEHOLDER!!!!
    def getThrottleDirection(self,current,target): #Right and down is forward, left and up is backward
        if(current<target):
            return "F"
        if(current>target):
            return "B"
    def getLateralDirection(self,current,target): #These must be ones stored on miromouse not the ones in the cells
        if(self.orientation == "N" or self.orientation == "E"): #North and East directions
            if(target<current):
                return "L"
            else:
                return "R"
        elif(self.orientation == "S" or self.orientation == "W"): #South and west directions
            if(target<current):
                return "R"
            else:
                return "L"
    def PID_pos(self,next_cell,dt): #For straights
        
        #Placeholder values
        MAX_INTEGRAL = 2 
        Kp_pos = 100 
        Kd_pos = 10
        Ki_pos = 1
        Kp_steer = 100 
        Kd_steer = 10
        Ki_steer = 1
        alpha = 0.3
        
        x_diff = abs(next_cell.x-self.x)
        y_diff = abs(next_cell.y-self.y)
        steer_error =min(x_diff,y_diff)
        pos_error = max(x_diff,y_diff)
        self.steer_integral_error += steer_error*dt
        if (self.steer_integral_error > MAX_INTEGRAL): self.steer_integral_error = MAX_INTEGRAL #ANTI SUPER BUILD UP
        if (self.steer_integral_error < -MAX_INTEGRAL): self.steer_integral_error = -MAX_INTEGRAL
        self.pos_integral_error += pos_error*dt
        if (self.pos_integral_error > MAX_INTEGRAL): self.pos_integral_error = MAX_INTEGRAL #ANTI SUPER BUILD UP
        if (self.pos_integral_error < -MAX_INTEGRAL): self.pos_integral_error = -MAX_INTEGRAL
        self.updateVelocity()
        velocity_throttle = Kp_pos*pos_error-Kd_pos*self.velocity + Ki_pos*self.pos_integral_error
        velocity_steer = Kp_steer*steer_error-Kd_steer*self.lateral_velocity + Ki_steer*self.steer_integral_error
        if x_diff < y_diff:
            current = self.x
            target = next_cell.x #problem with conversion vs micromouse position and cell
        else:
            current = self.y
            target = next_cell.y
        turn_direction = self.getLateralDirection(current,target)
        if(turn_direction == "R"):
            target_velocity_R = velocity_throttle-velocity_steer
            target_velocity_L = velocity_throttle+velocity_steer 
        else:
            target_velocity_R = velocity_throttle+velocity_steer
            target_velocity_L = velocity_throttle-velocity_steer
        return (target_velocity_R,target_velocity_L)
    def PID_wheel_speed(self,target_velocity,dt):
        MAX_INTEGRAL = 2 
        Kp_vel = 100 
        Kd_vel = 10
        Ki_vel = 1
        Kv = 100 # Determined by motors KV rating and resistance
        self.updateVelocity()
        velocity_error = target_velocity-self.velocity
        self.velocity_integral_error += velocity_error*dt
        if (self.velocity_integral_error > MAX_INTEGRAL): self.velocity_integral_error = MAX_INTEGRAL #ANTI SUPER BUILD UP
        if (self.velocity_integral_error < -MAX_INTEGRAL): self.velocity_integral_error = -MAX_INTEGRAL
        pid_out = Kp_vel*velocity_error - Kd_vel*self.acceleration + Ki_vel*self.velocity_integral_error
        voltage = Kv*target_velocity+ pid_out
        MAX_PWM = 255
        if voltage > MAX_PWM:
            voltage = MAX_PWM
        elif voltage < -MAX_PWM:
            voltage = -MAX_PWM
            
        return int(voltage) # This integer goes directly to your motor driver PWM pin! idk what this means yet but ill figure it out
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
