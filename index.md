---
layout: default
title: Introduction
---

[Home](index.md) | [Design](design.md) | [Implementation](implementation.md) | [Results](results.md) | [Conclusion](conclusion.md)

---

# **1.Introduction** {#1.introduction}

Autonomous Exploration and Navigation for Quadruped Robots in Search and Rescue

The challenge of autonomous robotic operation in hazardous, unknown environments is critical, particularly within the Search and Rescue (SAR) sector, a global market projected to reach $15.7 billion by 2031 [\[1\]](https://www.6wresearch.com/market-takeaways-view/how-big-is-the-search-and-rescue-market). Developing reliable autonomous systems is essential for improving human safety and mission efficiency in disaster zones.

*Project Goal*

The core goal is to develop and open-source a robust, autonomous exploration framework for the Unitree Go2 quadruped robot. This system must be capable of collision-free traversal and real-time environment mapping in unstructured, debris-filled spaces, integrating onboard odometry, the Navigation2 stack, and a custom frontier-based planning algorithm.

*Project Significance and Technical Problems*

This project fuses complex legged mobility with real-time autonomy over three-dimensional obstacles common in disaster sites. Success requires solving three specific technical challenges:

1. Achieving precise, real-time environment awareness by converting the local LiDAR point cloud stream into a highly accurate 2D occupancy grid using only the robot's onboard sensors and odometry.  
     
2. Designing a dynamic costmap that accurately processes the 2D occupancy grid data to penalize non-traversable (high-cost) debris, achieving reliable navigation.

3. Implementing a utility-based exploration function that intelligently balances travel cost against directional progress toward the mission goal, ensuring efficient and complete area coverage without prior global knowledge.

*Real-World Robotics Applications*

The resulting framework is directly transferable to high-value robotics applications beyond SAR, including:

* Industrial Inspection and Monitoring in hazardous facilities (e.g., nuclear power plants).  
* Underground and Subterranean Exploration (caves, mines).  
* Planetary and Scientific Exploration on extraterrestrial bodies.

Crucially, this work contributes an open-source, documented approach to Unitree Go2 LiDAR integration and navigation, facilitating future SAR and general robotics research on this platform.

# **6\. Team** {#6.-team}

Jason:  
*Bio:*  
Jason is a Mechanical Engineering graduate student specializing in Robotics, with experience in advanced motion control systems for quadruped robots.

*Major Contributions:*

Denae:  
*Bio:*  
Denae is a PhD student in the EECS department, whose current project focuses on simulating a frontier-based exploration strategy for a quadruped robot.

*Major Contributions:*

Kabir:  
*Bio:*  
Kabir is an EECS undergrad student. He has worked on some projects involving autonomous vehicles and distributed ML systems.

*Major Contributions:*

Andrew:  
*Bio:*  
Andrew is a Mechanical Engineering graduate student specializing in Robotics with industry software engineering experience.

*Major Contributions:*

# 

# **7\. Additional materials** {#7.-additional-materials}

Github link

Videos 
