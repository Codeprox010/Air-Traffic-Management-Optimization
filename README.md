# Air-Traffic-Management-Optimization
These are the codes for optimizing the landing times and reducing net carbon emissions by implementing specific runway management techniques.

The repository contains the following files:
1) A320.py - finding the emissions for A320 aircraft with phase inputs for a flight from Mumbai to Chennai
2) B737-800.py - finding the emissions for Boeing 737 aircraft for a flight from Vishakapatnam to Chennai
3) path_planner_redefined.py - it minimizes the emissions for an aircraft while undergoing descent phase by specifying all the parameters given.
4) Controller.py - it controls all the scripts and gives the net reduction observed when implementing the technique. In addition, it also allows the implementation of said method only when the landing times between two aircrafts are within a particular range.(If the time is lower, the technique gets applied slowing down the entire aircraft and if its high enough, the method gets skipped as both the aircrafts' landing times are not clashing)
5)log.py - It checks the number of successfully implemented cases/skipped caases of the methodology.
