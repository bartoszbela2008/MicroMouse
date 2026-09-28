import random
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
import matplotlib.animation as animation
#the robot should suite a maze constructed form 16*16 cell
# each cell of width 16.8 cm and with walls of 5cm high
#MAKE IT SO WHEN BEST HAS BEEN VISITED ITS OK!
cell_num_x=30
cell_num_y=30

class MicroMouse():
    def __init__(self,x,y,mass,velocity,acceleration):
        self.x=x
        self.y=y
        self.velocity=velocity
        self.acceleration=acceleration
        self.mass = mass 
        self.grid = [[Cell(999999,x,y) for y in range(cell_num_y)] for x in range(cell_num_x)]
    def updateWalls(self,maze):
        directions = ["N","S","E","W"]
        opposites = {"N":"S","S":"N","E":"W","W":"E"}
        for direction in directions:
            cell = self.grid[self.x][self.y]
            if self.grid[self.x][self.y].detected_walls[direction] != maze.grid[self.x][self.y].walls[direction]:
                self.grid[self.x][self.y].detected_walls[direction] = maze.grid[self.x][self.y].walls[direction]
                increment = {"N":(cell.x,cell.y-1), "S":(cell.x, cell.y+1),"E":(cell.x+1,cell.y),"W":(cell.x-1,cell.y)}
                position = increment[direction]
                if(maze.isInBounds(position[0],position[1])):
                    self.grid[position[0]][position[1]].detected_walls[opposites[direction]] = cell.detected_walls[direction]
    def floodFill(self,maze,target_cells):
        queue = []
        for x in range(cell_num_x):
            for y in range(cell_num_y):
                self.grid[x][y].distance = 999999
        for cell in target_cells:
            queue.append(cell)
            cell.distance = 0
        while len(queue) != 0:
            currentCell = queue.pop(0)
            neighbors = maze.findNeighbors(currentCell,self)
            for neighbor in neighbors:
                if neighbor.distance > currentCell.distance + 1:
                    neighbor.distance = currentCell.distance + 1
                    queue.append(neighbor)
    def move(self,maze):
        currentCell = self.grid[self.x][self.y]
        currentCell.visited = True
        neighbors= maze.findNeighbors(currentCell,self)
        min_distance = min(cell.distance for cell in neighbors)
        best_cells = [cell for cell in neighbors if cell.distance == min_distance]
        for cell in best_cells:
            if(len(best_cells) !=0 and not cell.visited):
                newCell = cell
            else:
                newCell = cell
        self.x = newCell.x
        self.y = newCell.y
        

class Cell:
    def __init__(self,distance,x,y):
        self.x = x
        self.y = y
        self.visited=False
        self.distance = distance
        #Dictionary
        self.walls = {"N":True,"S":True,"E":True,"W":True}  
        self.detected_walls = {"N":False,"S":False,"E":False,"W":False}  

class Maze():
    def __init__(self):
        self.grid = [[Cell(-1,x,y) for y in range(cell_num_y)] for x in range(cell_num_x)] #column, row outer loop is x and inner loop is y so [x][y]
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
    def findNeighbors(self,cell,mouse):
        neighbors =[]
        directions = ["N","S","E","W"]
        increment = {"N":(cell.x,cell.y-1), "S":(cell.x, cell.y+1),"E":(cell.x+1,cell.y),"W":(cell.x-1,cell.y)}
        for direction in directions: 
            position = increment[direction]
            if self.isInBounds(position[0],position[1]) and not cell.detected_walls[direction]:
                neighbors.append(mouse.grid[position[0]][position[1]])
        return neighbors
    def draw(self): #AI function
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        
        # Invert Y-axis so (0,0) is visually top-left
        ax.invert_yaxis()

        for x in range(cell_num_x):
            for y in range(cell_num_y):
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
        if(0<=x<cell_num_x and 0<=y<cell_num_y):
            return True
        return False
def animate_mouse(maze, mouse, target_cells, steps=50):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.invert_yaxis()

    # Draw maze walls
    for x in range(cell_num_x):
        for y in range(cell_num_y):
            cell = maze.grid[x][y]
            x_left, x_right = x, x + 1
            y_top, y_bottom = y, y + 1

            if cell.walls["N"]:
                ax.plot([x_left, x_right], [y_top, y_top], color="black", lw=2)
            if cell.walls["S"]:
                ax.plot([x_left, x_right], [y_bottom, y_bottom], color="black", lw=2)
            if cell.walls["E"]:
                ax.plot([x_right, x_right], [y_top, y_bottom], color="black", lw=2)
            if cell.walls["W"]:
                ax.plot([x_left, x_left], [y_top, y_bottom], color="black", lw=2)

    ax.add_patch(patches.Rectangle((0, 0), 1, 1, color="green", alpha=0.3, label="Start"))
    ax.add_patch(patches.Rectangle((7, 7), 2, 2, color="red", alpha=0.3, label="Goal"))

    # Blue square patch representing the mouse
    mouse_patch = patches.Rectangle((mouse.x + 0.2, mouse.y + 0.2), 0.6, 0.6, color="blue", label="MicroMouse")
    ax.add_patch(mouse_patch)

    plt.title("MicroMouse Live Simulation")
    plt.xlabel("X (Columns)")
    plt.ylabel("Y (Rows)")
    plt.legend(loc="upper right")
    def update(frame):
            # Stop moving if goal reached
        #if (mouse.x, mouse.y) in [(7, 7), (8, 7), (7, 8), (8, 8)]:
          #  return mouse_patch,

        mouse.updateWalls(maze)
        mouse.floodFill(maze, target_cells)
        mouse.updateWalls(maze)
        
        mouse.move(maze)
        mouse.updateWalls(maze)
        debug_step(mouse,maze,frame+1)
            
            # Update square position
        mouse_patch.set_xy((mouse.x + 0.2, mouse.y + 0.2))
        return mouse_patch,

    anim = animation.FuncAnimation(fig, update, frames=steps, interval=300, repeat=False)
    plt.show()
def debug_step(mouse, maze, frame_num=None):
    """Prints mouse position, real walls vs detected walls, neighbor distances, and full grid."""
    header = f"--- Step {frame_num} ---" if frame_num is not None else "--- Debug Info ---"
    print(f"\n{header}")
    print(f"Mouse Location: ({mouse.x}, {mouse.y}) | Current Cell Distance: {mouse.grid[mouse.x][mouse.y].distance}")
    
    real_walls = maze.grid[mouse.x][mouse.y].walls
    sensed_walls = mouse.grid[mouse.x][mouse.y].detected_walls
    
    print("\n[WALL SENSING STATUS]")
    print(f"  North (N): Real Wall = {real_walls['N']}  | Sensed = {sensed_walls['N']}")
    print(f"  South (S): Real Wall = {real_walls['S']}  | Sensed = {sensed_walls['S']}")
    print(f"  East  (E): Real Wall = {real_walls['E']}  | Sensed = {sensed_walls['E']}")
    print(f"  West  (W): Real Wall = {real_walls['W']}  | Sensed = {sensed_walls['W']}")

    # Check available paths and neighbor distances
    current_cell = mouse.grid[mouse.x][mouse.y]
    neighbors = maze.findNeighbors(current_cell, mouse)
    print("\n[ACCESSIBLE NEIGHBORS & DISTANCES]")
    for n in neighbors:
        print(f"  -> Neighbor Cell ({n.x}, {n.y}) | Distance to Goal: {n.distance}")

    print("\n[16x16 DISTANCE MAP]")
    mouse.print_distances()  # Uses your original print_distances() function
    print("=" * 45)

mouse = MicroMouse(0,0,0.5,0,0)
maze = Maze()
maze.recursiveBacktrack(0, 0)
target_cells ={mouse.grid[29][29]}

# Launch live animated window
animate_mouse(maze, mouse, target_cells, steps=2000)