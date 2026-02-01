# Smart Ambulance Corridor Simulation

A Smart City simulation built with **Eclipse SUMO** and **Python** that optimizes emergency vehicle routing in dense urban traffic. This project implements a dynamic **"Green Wave" algorithm** and an **autonomous obstacle clearing mechanism** to ensure zero-wait times for ambulances.

## Features

* **Intelligent Green Wave:** Detects the ambulance's path and proactively turns traffic lights Green (creating a "Green Bubble") while releasing distant signals back to normal flow.
* **Anti-Gridlock System:** Automatically detects and clears vehicles blocking the immediate path of the ambulance to prevent simulation deadlocks.
* **Realistic Traffic Generation:** Uses Python scripts to generate uniform, heavy traffic coverage across every street in the map, simulating real-world peak hour congestion.
* **Rolling Window Logic:** Optimizes only the immediate and next intersection, ensuring the rest of the city traffic flows normally.

## Prerequisites

-  **Python 3.x**
-  **Eclipse SUMO**

## Installation

-  **Clone the repository:**
    
-  **Install dependencies:**
    ```
    pip install traci
    ```

## How to Run

### 1. Generate Traffic (One-Time Setup)
```
python generate_chaos.py
```

### 2. Run app
```
python run.py
```