import random
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
#the robot should suite a maze constructed form 16*16 cell
# each cell of width 16.8 cm and with walls of 5cm high
ren .gitignore.txt .gitignore

class MicroMouse():
    def __init__(self,x,y,mass,velocity,acceleration):
        self.x=x
        self.y=y
        self.velocity=velocity
        self.acceleration=acceleration
        self.mass = mass 
class Cell:
    def __init__(self):
        self.visited=False
        #Dictionary
        self.walls = {"N":True,"S":True,"E":True,"W":True}
class Maze():
    cell_num_x=16
    cell_num_y=16
    def __init__(self):
        self.grid = [[Cell() for i in range(self.cell_num_y)] for i in range(self.cell_num_x)] #column, row outer loop is x and inner loop is y so [x][y]
    def recursiveBacktrack(self,x,y):
            start = self.grid[x][y]
            start.visited = True
            directions = ["N","S","E","W"]
            opposites = {"N":"S","S":"N","E":"W","W":"E"}
            random.shuffle(directions)
            for direction in directions: 
                temp_x = x
                temp_y = y
                if(direction == "W"): #Couldve used dictionary here
                    temp_x=temp_x-1 #Top left is 0,0
                if(direction == "E"):
                    temp_x=temp_x+1
                if(direction == "S"):
                    temp_y=temp_y+1 
                if(direction == "N"):
                    temp_y=temp_y-1
                if(self.isInBounds(temp_x,temp_y) and not self.grid[temp_x][temp_y].visited):
                    self.grid[x][y].walls[direction] = False
                    self.grid[temp_x][temp_y].walls[opposites[direction]] = False
                    self.recursiveBacktrack(temp_x,temp_y)
    def draw(self): #AI function
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        
        # Invert Y-axis so (0,0) is visually top-left
        ax.invert_yaxis()

        for x in range(self.cell_num_x):
            for y in range(self.cell_num_y):
                cell = self.grid[x][y]
                
                # Cell corners
                x_left, x_right = x, x + 1
                y_top, y_bottom = y, y + 1

                # Draw walls if True
                if cell.walls["N"]:
                    ax.plot([x_left, x_right], [y_top, y_top], color="black", lw=2)
                if cell.walls["S"]:
                    ax.plot([x_left, x_right], [y_bottom, y_bottom], color="black", lw=2)
                if cell.walls["E"]:
                    ax.plot([x_right, x_right], [y_top, y_bottom], color="black", lw=2)
                if cell.walls["W"]:
                    ax.plot([x_left, x_left], [y_top, y_bottom], color="black", lw=2)

        # Highlight Start (0,0) and Center Goal (7,7 to 8,8 for 16x16 Micromouse)
        ax.add_patch(patches.Rectangle((0, 0), 1, 1, color="green", alpha=0.3, label="Start (0,0)"))
        ax.add_patch(patches.Rectangle((7, 7), 2, 2, color="red", alpha=0.3, label="Goal Center"))

        plt.title("16x16 Micromouse Maze (Recursive Backtracker)")
        plt.xlabel("X (Columns)")
        plt.ylabel("Y (Rows)")
        plt.legend(loc="upper right")
        plt.grid(False)
        plt.show()
        
    def isInBounds(self,x,y):
        if(0<=x<self.cell_num_x and 0<=y<self.cell_num_y):
            return True
        return False
    
maze = Maze()
maze.recursiveBacktrack(0, 0)  # Start generating from top-left (0,0)
maze.draw()