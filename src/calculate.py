import datetime
import json

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
            team_exist1 = team_exist.deepcopy(config)
            team_exist1 = team_exist1.add_hero(candidate, config)
            # to Prune
            if team_exist1.evaluate > int(len(team_exist1.team)/2-1):
                dfs(config, teams, team_exist1, team_number)


def main():
    # data_processing()
    start = datetime.datetime.now()
    heroes, classes, origins = data_read()
    config = Config(heroes, classes, origins)
    teams = []
    team_exist = TeamExist(config, set())
    dfs(config, teams, team_exist, 5)
    teams.sort(key=lambda x: x.evaluate, reverse=True)
    teams_json = []
    for team in teams:
        teams_json.append(team.to_json())
    file = '../res/result_prune.json'
    write_to_json(file, teams_json)
    end = datetime.datetime.now()
    print(end - start)


if __name__ == '__main__':
    main()
