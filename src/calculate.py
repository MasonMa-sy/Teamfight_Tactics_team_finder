import datetime
import json
import threading
import multiprocessing

import numpy as np

from src.TeamExist import TeamExist


class Config:
    """
    heroes {'@name': {'class':'@*', 'origin': '@*', 'second_class': '@*', 'second_origin': '@*'}}
    classes and origins {'@name': [@num, @num]}
    classes_to_heroes {@name':set{@hero, @hero}}
    """
    def __init__(self, heroes_dict, classes_dict, origins_dict):
        self.heroes_dict = heroes_dict
        self.classes_dict = classes_dict
        self.origins_dict = origins_dict
        self.class_to_hero = {}
        self.class_to_hero.update(classes_dict)
        self.find_hero('class')
        self.origin_to_hero = {}
        self.origin_to_hero.update(origins_dict)
        self.find_hero('origin')

    def find_hero(self, type_str):
        if type_str == 'class':
            self.to_set(self.class_to_hero)
            for hero in self.heroes_dict.keys():
                self.class_to_hero[self.heroes_dict[hero]['class']].add(hero)
                if 'second_class' in self.heroes_dict[hero].keys():
                    self.class_to_hero[self.heroes_dict[hero]['second_class']].add(hero)
        if type_str == 'origin':
            self.to_set(self.origin_to_hero)
            for hero in self.heroes_dict.keys():
                self.origin_to_hero[self.heroes_dict[hero]['origin']].add(hero)
                if 'second_origin' in self.heroes_dict[hero].keys():
                    self.origin_to_hero[self.heroes_dict[hero]['second_origin']].add(hero)

    def to_set(self, dict_a):
        for a in dict_a.keys():
            dict_a[a] = set()


class BFSThread(threading.Thread):
    def __init__(self, candidates, team_temp, queue, config):
        threading.Thread.__init__(self)
        self.candidates = candidates
        self.team_temp = team_temp
        self.queue = queue
        self.config = config

    def run(self):
        for candidate in self.candidates:
            print('%s    %d\n%s  %d' % (self.team_temp.team, len(self.queue), candidate, len(self.team_temp.team)))
            team_temp2 = self.team_temp.deepcopy(self.config)
            team_temp2.add_hero(candidate, self.config)
            # to prune
            if team_temp2.evaluate > int(len(team_temp2.team) / 2 - 1):
                if team_temp2 not in self.queue:
                    self.queue.append(team_temp2)


def read_from_json(file):
    f = open(file, encoding='utf-8')
    data = json.load(f)
    f.close()
    return data


def write_to_json(file, data):
    f = open(file, 'w', encoding='utf-8')
    json.dump(data, f, indent=4, separators=(', ', ': '))
    f.close()


def data_processing():
    """
    According data.json to get origin and class
    This is not used in follow code.
    :rtype: object
    """
    file = '../res/data.json'
    data = read_from_json(file)
    f = open('../res/data_indent.json', 'w', encoding='utf-8')
    json.dump(data, f, indent=1)
    f.close()
    heroes = data.get('teamfighttactics')
    class1_temp = {}
    origin_temp = {}
    class1 = []
    origin = []
    id_class = id_origin = 1
    for hero in heroes:
        print(hero.keys())
        if not (hero['class'] in class1_temp):
            class1_temp[hero['class']] = ''
            class1.append({'id': id_class, 'class': hero['class']})
            id_class += 1
        if not (hero['origin'] in origin_temp):
            origin_temp[hero['origin']] = ''
            origin.append({'id': id_origin, 'origin': hero['origin']})
            id_origin += 1
    print(len(class1), len(origin))
    f = open('../res/class.json', 'w', encoding='utf-8')
    json.dump(class1, f, indent=1)
    f.close()
    f = open('../res/origin.json', 'w', encoding='utf-8')
    json.dump(origin, f, indent=1)
    f.close()


def dict_to_dict_hero(dicts):
    lists = {}
    dicts = dicts['teamfighttactics']
    for dict_a in dicts:
        dict_b = dict()
        dict_b['class'] = dict_a['class']
        dict_b['origin'] = dict_a['origin']
        if 'second_class' in dict_a.keys():
            dict_b['second_class'] = dict_a['second_class']
        if 'second_origin' in dict_a.keys():
            dict_b['second_origin'] = dict_a['second_origin']
        lists[dict_a['name']] = dict_b
    return lists


def dict_to_dict_class_or_origin(dicts, type_co):
    lists = {}
    for dict_a in dicts:
        lists[dict_a[type_co]] = list(map(int, dict_a['number'].split('/')))
    return lists


def data_read():
    file = '../res/hero_f.json'
    heroes_dict = read_from_json(file)
    file = '../res/class_f.json'
    classes_dict = read_from_json(file)
    file = '../res/origin_f.json'
    origins_dict = read_from_json(file)
    return dict_to_dict_hero(heroes_dict), dict_to_dict_class_or_origin(
        classes_dict, 'class'), dict_to_dict_class_or_origin(origins_dict, 'origin')


def dfs(config, teams, team_exist, team_number=9):
    if len(team_exist.team) >= team_number:
        if team_exist not in teams:
            # team_exist.evaluate_association(config)
            # team_exist.evaluate_team()
            if team_exist.evaluate > 0:
                teams.append(team_exist)
        return
    elif len(team_exist.team) == 0:
        for hero in config.heroes_dict.keys():
            team_exist1 = team_exist.deepcopy(config)
            team_exist1 = team_exist1.add_hero(hero, config)
            dfs(config, teams, team_exist1, team_number)
    else:
        candidates = team_exist.find_candidate(config)
        for candidate in candidates:
            print('%s\n%s  %d' % (team_exist.team, candidate, len(team_exist.team)))
            team_exist1 = team_exist.deepcopy(config)
            team_exist1 = team_exist1.add_hero(candidate, config)
            # to Prune
            if team_exist1.evaluate > int(len(team_exist1.team)/2-1):
                dfs(config, teams, team_exist1, team_number)


def bfs(config, teams, team_exist, prune, team_number=9):
    queue = []
    if len(team_exist.team) == 0:
        for hero in config.heroes_dict.keys():
            team_temp = TeamExist(config, set())
            team_temp.add_hero(hero, config)
            queue.append(team_temp)
        delete_team_len = 1
    else:
        delete_team_len = len(team_exist.team)
        queue.append(team_exist)
    index_now = 0
    while index_now < len(queue):
        print("%d   %d" % (index_now, delete_team_len))
        team_temp = queue[index_now].deepcopy(config)
        if len(team_temp.team) > delete_team_len:
            delete_team_len += 1
            queue = queue[index_now:]
            index_now = 0
        if len(team_temp.team) == team_number:
            teams.append(team_temp)
            index_now += 1
            continue
        candidates = team_temp.find_candidate(config)
        for candidate in candidates:
            print('%s    %d\n%s  %d' % (team_temp.team, len(queue), candidate, len(team_temp.team)))
            team_temp2 = team_temp.deepcopy(config)
            team_temp2.add_hero(candidate, config)
            # to prune-1
            if prune == 'prune-1':
                if team_temp2.evaluate > int(len(team_temp2.team) / 2 - 1):
                    if team_temp2 not in queue:
                        queue.append(team_temp2)
            if prune == 'prune-2':
                if team_temp2.evaluate >= int(len(team_temp2.team)):
                    if team_temp2 not in queue:
                        queue.append(team_temp2)
        index_now += 1


def bfs_parallel(config, teams, team_exist, team_number=9):
    """
    cpython can not parallel because of GIL.
    The time cost is not reduce.
    :param config:
    :param teams:
    :param team_exist:
    :param team_number:
    :return:
    """
    queue = []
    if len(team_exist.team) == 0:
        for hero in config.heroes_dict.keys():
            team_temp = TeamExist(config, set())
            team_temp.add_hero(hero, config)
            queue.append(team_temp)
        delete_team_len = 1
    else:
        delete_team_len = len(team_exist.team)
        queue.append(team_exist)
    index_now = 0
    while index_now < len(queue):
        print("%d   %d" % (index_now, delete_team_len))
        team_temp = queue[index_now].deepcopy(config)
        if len(team_temp.team) > delete_team_len:
            delete_team_len += 1
            queue = queue[index_now:]
            index_now = 0
        if len(team_temp.team) == team_number:
            teams.append(team_temp)
            index_now += 1
            continue
        candidates = team_temp.find_candidate(config)
        candidates = list(candidates)
        bfs_thread1 = BFSThread(candidates[:int(len(candidates)/2)], team_temp, queue, config)
        bfs_thread2 = BFSThread(candidates[int(len(candidates)/2):], team_temp, queue, config)
        bfs_thread1.start()
        bfs_thread2.start()
        bfs_thread1.join()
        bfs_thread2.join()
        index_now += 1


def dp_k(config, team_number=9, team_count=100):
    """
    from: https://blog.csdn.net/creat2012/article/details/9469873
    It could not find the best solution. This question can not be divided into sub-questions.
    """
    dp = np.zeros([team_number+1, team_count+1])
    teams = [[TeamExist(config, set()) for col in range(team_count+1)] for row in range(team_number+1)]
    a = np.zeros([team_count+2])
    b = np.zeros([team_count+2])
    team_temp_a = [d for d in range(0, team_count + 2)]
    team_temp_b = [d for d in range(0, team_count + 2)]
    for i in config.heroes_dict.keys():
        for j in range(team_number, 0, -1):
            for d in range(1, team_count+1):
                team_temp = teams[j-1][d].deepcopy(config)
                team_temp.add_hero(i, config)
                team_temp_a[d] = team_temp
                a[d] = dp[j-1][d] + team_temp.evaluate
                team_temp = teams[j][d].deepcopy(config)
                team_temp_b[d] = team_temp
                team_temp_b[d].evaluate_association(config)
                team_temp_b[d].evaluate_team()
                b[d] = dp[j][d]
            a[team_count+1] = b[team_count+1] = -1
            x = y = z = 1
            while z <= team_count and (x <= team_count or y <= team_count):
                if a[x] > b[y]:
                    dp[j][z] = a[x]
                    teams[j][z] = team_temp_a[x]
                    x += 1
                else:
                    dp[j][z] = b[y]
                    teams[j][z] = team_temp_b[y]
                    y += 1
                if dp[j][z] != dp[j][z-1]:
                    z += 1
    print(dp)
    return teams[team_number]


def dp_best(config, team_number=9):
    dp = np.zeros([len(config.heroes_dict.keys()), team_number+1])
    teams = [[TeamExist(config, set()) for col in range(team_number+1)] for row in range(len(
        config.heroes_dict.keys())+1)]
    for i in range(0, len(config.heroes_dict.keys())):
        for j in range(team_number, 0, -1):
            team_temp = teams[i-1][j-1].deepcopy(config)
            team_temp.add_hero(list(config.heroes_dict.keys())[i], config)
            if dp[i-1][j] > dp[i-1][j-1] + team_temp.evaluate:
                dp[i][j] = dp[i-1][j]
                teams[i][j] = teams[i-1][j].deepcopy(config)
                teams[i][j].evaluate_association(config)
                teams[i][j].evaluate_team()
            else:
                dp[i][j] = dp[i-1][j-1] + team_temp.evaluate
                teams[i][j] = team_temp
    print(dp[len(config.heroes_dict.keys())-1])
    return teams[len(config.heroes_dict.keys())-1]


def main():
    # data_processing()
    method = 'bfs'
    team_number = 5
    prune = 'prune-2'
    start = datetime.datetime.now()
    heroes, classes, origins = data_read()
    config = Config(heroes, classes, origins)
    if method == 'dfs' or method == 'bfs' or 'bfs_parallel':
        teams = []
        team_exist = TeamExist(config, set())
        if method == 'dfs':
            dfs(config, teams, team_exist, team_number)
        if method == 'bfs':
            bfs(config, teams, team_exist, prune, team_number)
        if method == 'bfs_parallel':
            bfs_parallel(config, teams, team_exist, team_number)
        teams.sort(key=lambda x: x.evaluate, reverse=True)
    if method == 'dp_k':
        team_count = 100
        teams = dp_k(config, team_number, team_count)
    if method == 'dp_best':
        teams = dp_best(config, 4)
    teams_json = []
    for team in teams:
        teams_json.append(team.to_json())
    file = '../result/result_%s_%d_%s.json' % (method, team_number, prune)
    write_to_json(file, teams_json)
    end = datetime.datetime.now()
    print(end - start)


if __name__ == '__main__':
    main()
