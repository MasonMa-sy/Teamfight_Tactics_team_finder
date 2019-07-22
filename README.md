### TFT_team_finder

Using dfs to find teams that use classes and origins as much as possible.  
The time cost is too high, need more optimization. 

#### DFS
1.Add a hero to team from all hero list.   
2.According to the class and origin of the hero, get a candidate hero list.  
3.Add a hero to team from candidate hero list.  
4.Until len(team) >= team_size, to 3. find another hero.  
5.Until candidate list is all used, to 1. find another hero.  

First pruning, if team.evaluate <= int(len(team_exist1.team)/2-1),  
not dfs() this team.

#### Time and Memory used
4 no prune, mem 20+MB, evaluate 8.  
4 first prune, time 1:19, mem 24.51M, evaluate 8.  
5 first prune, time , mem 96.46M, evaluate .a


