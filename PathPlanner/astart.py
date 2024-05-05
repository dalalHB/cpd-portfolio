import math
import heapq
# This file contains the path planning function that will be called by the GUI.
    
# The main path planning function. Additional functions, classes, 
# variables, libraries, etc. can be added to the file, but this
# function must always be defined with these arguments and must 
# return an array ('list') of coordinates (col,row).
#DO NOT EDIT THIS FUNCTION DECLARATION
   
def do_a_star(grid, start, end, display_message):
    # Class to represent a node in the A* algorithm
    class Node:
        # Node constructor
        '''Each node has a parent node, 
        a position, and g, h, and f values.
        The g value is the cost of the path from the start node to the current node.
        The h value is the heuristic value (Euclidean distance) from the current node to the end node.
        The f value is the sum of the g and h values.'''
        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position = position
            self.g = 0
            self.h = 0
            self.f = 0

        # Overload the less than and equal to operators to allow for comparison of nodes
        def __lt__(self, other):
            return self.f < other.f

        # Overload the equal to operator to allow for comparison of nodes
        def __eq__(self, other):
            return self.position == other.position
        
        # Overload the hash function to allow for comparison of nodes
        def __hash__(self):
            return hash(self.position)

    # Function to calculate the heuristic value (Euclidean distance)
    def calculate_h_value(position, end_position):
        # x = position[0] , y = position[1]
        return math.sqrt((position[0] - end_position[0]) ** 2 + (position[1] - end_position[1]) ** 2)

    # Initialize the start and end nodes
    start_node = Node(None, start)
    end_node = Node(None, end)
    # Initialize the h and f values of the start node
    start_node.h = calculate_h_value(start_node.position, end_node.position)
    start_node.f = start_node.g + start_node.h

    # Initialize the open list and closed set (using a set for faster lookup)
    # The open list is a list of tuples containing the f value and the node
    # The open list is a priority queue (heap) to allow for efficient retrieval of the node with the lowest f value
    open_list = []
    heapq.heappush(open_list, (start_node.f, start_node)) # Push the start node onto the open list
    closed_set = set()

    # Main loop of the A* algorithm
    '''The A* algorithm works as follows:
    1. Pop the node with the lowest f value from the open list
    2. Add the current node to the closed set
    3. Check if the current node is the end node
        - If it is, reconstruct the path and return it
    4. Check the adjacent nodes
        5. For each adjacent node:
            - Skip if the node is out of bounds
            - Skip if the node is an obstacle
            - Create a new node
            - Calculate the new node's g, h, and f values
            - If the new node is already in the closed set, skip it
            - If the new node is not in the open list, add it to the open list and continue
            - If the new node is in the open list and the new node's g value is greater than or equal to the existing node's g value, skip it
    6. Repeat the loop until the open list is empty or the end node is reached    
    If the open list is empty and the end node has not been reached, return an empty path'''

    while open_list:
        current_f, current_node = heapq.heappop(open_list) # heapq.heappop returns the node with the lowest f value
        closed_set.add(current_node)

        # Check if the current node is the end node
        if current_node == end_node:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        # Check the adjacent nodes
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Skip if the node is out of bounds
            if node_position[0] > len(grid) - 1 or node_position[0] < 0 or node_position[1] > len(grid[0]) - 1 or node_position[1] < 0:
                continue

            # Skip if the node is an obstacle (obstacle = 0)
            if grid[node_position[0]][node_position[1]] == 0:
                continue

            # Create a new node
            new_node = Node(current_node, node_position)
            if new_node in closed_set:
                continue
            
            # Calculate the new node's g, h, and f values
            new_node.g = current_node.g + 1
            new_node.h = calculate_h_value(new_node.position, end_node.position)
            new_node.f = new_node.g + new_node.h

            # if the new node is not in the open list, add it to the open list and continue
            # if the new node is in the open list and the new node's g value is greater than or equal to the existing node's g value, skip it
            if not any(node for _, node in open_list if new_node == node and new_node.g >= node.g):
                heapq.heappush(open_list, (new_node.f, new_node))

  
     # Display the start and end locations
    display_message("Start location is " + str(start))
    display_message("End location is " + str(end))

    # If no path was found, display a message
    if not path:
        display_message("No path found")
    else:
        # If a path was found, display a message
        display_message("Shortest path found")
    
    # Return the path (or an empty list if no path was found)
    return []
#end of files