# Collin's Aerospace Performance Simulation

_This project is created with censored data procured with the permission of Collin's Aerospace associates._

Collin's Aerospace produces a multitude of aerospace parts and systems for both the flight and defense industry. The production of these parts require long and complex production processes that are prone to incident and delay.

In this project, we are taking a specific look at the landing gear production at the Collin's Aerospace Oakville plant to determine where bottlenecks may lie and get a better understanding of how parts move through the production line.

## Simulation
To start our investigation, we've pulled data from their production line for 4 types of landing gear being produced. The data holds thousands of records of part production including information such as when they first start in production, the different processes they've went through (e.g. machining, refining, inspection, etc.), how much time they spent at that process, and when they've been completed. With that information, we build out a simulation of the production line.

We represent each of the production processes as a node (FIFO_Node.py) and build out of network of these nodes to model the production line. Then feed each of the parts at an exponentially distributed rate into the assembly line. Each of the nodes will keep track of their processing history during the simulation
 - Number of parts serviced
 - Busy time (Time spent servicing)
 - Response time (How long a part has to wait in line before it can get serviced)

We can then run the simulation for a set amount of time—for instance, a month—and then analyze the average service time, response time, as well as the utilization of each process.

---

## Sheridan PGDAP Reviewer Considerations

### Involvement

This is a team project consisting of me and 2 other members. My role in the project was strictly writing the simulation using extracted data provided by a team member in filtered.csv. Therefore, all code used to build the simulation is written by me and relevant for review.

### Code Highlights

The project is a series of Python scripts used in the simulation as well as the calculation of results. Below I've highlighted core sections of the code along with some context.
#### Simulation Code
- **sim.py**
  - Runs the simulation
  - A significant amount of scraping through the csv data is done in order to determine how many processes there are, the exact processing order for each type of part, as well as the service times for a given part at a given process.
- **Jobs/**
  - This directory contain the 4 types of landing gear parts (Arbitrarily named A,B,C,D) represented as a child class of Job.py
- **FIFO_Node.py**
  - This node (First-In-Last-Out) represents a production process in the aerospace assembly line
  - Only needs to be instantiated with a name
  - Contains a queue the can hold any number of jobs and will process that job in a given time based on the type of job it is (the job itself has this information)
#### Non-Simulation Files (Teamwork)
- **Classed_Net.py & ExtractData.py**
  - ExtractData.Py acts as an independent run of the simulation for 2 years with its results then fed into Classed_Net
  - Classed_Net uses Jacksonian Networks to attain the overall response times and utilization for each process
- **Collin's_Performance_Analysis.pdf**
  - A final report of our whole project and findings

