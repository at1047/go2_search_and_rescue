---
layout: page
title: Resources
permalink: /resources/
icon: fas fa-book
order: 5
---


# Conclusion

This project aimed to develop an autonomous exploration system for the Unitree Go2 quadruped capable of mapping, exploring, and navigating an unknown indoor environment. Experimental results show that the final system largely met the original design criteria.

Key outcomes:

* Successful autonomous navigation through a maze environment using Nav2-generated paths  
* Construction of an occupancy grid map from collected LiDAR data  
* Effective frontier-based exploration directing the quadruped to unexplored areas of the maze  
* Safe operation enabled by costmap inflation, which assigns high cost to regions near obstacles and allows Nav2 to reject infeasible frontiers  
* Full integration of sensing, planning, and actuation on the Go2 platform

These results demonstrate that the perception-planning-actuation pipeline functioned as intended, allowing the robot to autonomously explore and map an unknown environment without prior knowledge. Overall, the system provided reliable autonomous performance and validated the core design choices made for this project.

## Additional materials

* Github link
* Videos
