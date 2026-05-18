*This project has been created as part of the 42 curriculum by bmoura-s.*



## Description


Fly-in is an algorithmic pathfinding and simulation project. The goal is to route a fleet of drones through a given map in the fewest possible turns. The project handles dynamic path scheduling, space-time reservation, connection capacities, and distinct movement costs for different zone types.


## Instructions


Below are the rules to run the `Makefile` commands.


### Installation


To install the dependencies, run:


  ```bash

  make install

  ```


### Execution


To run the simulation with a specific map, use the following command:


  ```bash

  make run MAP=map.txt

  ```


### Development Commands


* **`make debug`**: Runs the program with Python's debugger (`pdb`).


* **`make lint`**: Checks the codes' compliance with the rules of `flake8` and `mypy`.


* **`make lint-strict`** Checks the codes' compliance with the rules of `flake8` and `mypy` with the `--strict` flag.


* **`make clean`**: Removes caches and temporary files.


## Algorithmic Choices



* **Pathfinding Engine:** The routing system utilizes a Prioritized Space-Time A* algorithm. Drones are routed sequentially, and their planned movements are logged into a 3D Reservation Table (X, Y, Time) to guarantee collision-free transit.


* **Optimization:** To beat the Challenger map record, the algorithm utilizes a True Distance Heuristic (BFS) and a Congestion Heatmap. Drones dynamically alter their paths to avoid highly trafficked corridors, maximizing overall throughput.


* **Parser:** Built as a strict State Machine, the parser guarantees O(N) file reading while natively enforcing strict Top-to-Bottom configuration ordering.



## Visual Representation



The project includes a custom graphical visualizer built with `tkinter`.


* **Dynamic Scaling:** Automatically scales the window layout based on the map's coordinate boundaries.


* **Color Coding:** Zones are color-coded based on their parsed metadata or zone types (e.g., Priority vs. Restricted).


* **Interactivity:** Press `Spacebar` to pause/resume the simulation, and `Escape` to cleanly exit without standard X11 GUI crashing.


## Resources & AI Usage


### Resources

* **Graph Theory:** Red Blob Games - [Introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html)

* **Space-Time Pathfinding:** Cooperative Pathfinding documentation and logic structures.



### AI Usage


This project relied on AI assistance for the following tasks:


* **Concepts**: Helped understand the algorithms, heuristics and optimizations best suited for the project being built.

* **Structure**: Given the emphasis on OOP during this project, the architecture of the whole project and necessary restructurings that came with were greatly aided by AI overview.

* **Documentation**: When looking to further understand both the algorithms, and the tools used such as `tkinter`, AI aided in that research phase.

* **Debugging**: Finding errors, reviewing code, optimizing both the algorithm and the UI was the most crucial assistance by AI.
