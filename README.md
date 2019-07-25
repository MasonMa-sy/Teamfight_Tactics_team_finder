### TFT_team_finder

Using dfs to find teams that use classes and origins as much as possible.  
The time cost is too high, need more optimization. 

#### DFS
1.Add a hero to team from all hero list.   
2.According to the class and origin of the hero, get a candidate hero list.  
3.Add a hero to team from candidate hero list.  
4.Until len(team) >= team_size, to 3. find another hero.  
5.Until candidate list is all used, to 1. find another hero.  
#### BFS
Using a List to record all history searched team. This removes duplicate teams.  
need more memory, less time.   
BFS-parallel: Because of GIL, the parallel of thread is not fast.  
multiprocessing.Queue can not be traversed. The parallel of process is not suitable.

#### Prune
pruning-1, team.evaluate > int(len(team_exist1.team)/2-1),  
prune-2, team.evaluate >= len(team_exist1.team),  

#### Time and Memory used
##### dfs
4 no prune, mem 20+MB, evaluate 8.  
4 first prune, time 1:19, mem 24.51M, evaluate 8.  
5 first prune, time 3:43:48, mem 96.46M, evaluate 10.  

##### bfs
5 first prune, time , mem , evaluate  
5 first prune, time 39:42, mem 136.24 , evaluate 10, get_team 36666  
5 prune-2, time 2:44, mem 68.06, evaluate 10(10 same, 9 290-278, 8 1272-1148), get_team 12315  
#### Thanks
Thanks to LNTech, I got hero data from
(https://github.com/LNTech/TeamfightTactics_Simulator).


