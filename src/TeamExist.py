

class TeamExist:
    def __init__(self, config, team, i_or_c='init'):
        """

        :param config:
        :param team:
        :param type: 'init' or 'copy'
        """
        self.classes = {}
        self.origins = {}
        self.eva_classes = {}
        self.eva_origins = {}
        self.team = set()
        self.evaluate = 0
        if i_or_c == 'init':
            self.classes.update(config.classes_dict)
            self.origins.update(config.origins_dict)
            self.eva_classes.update(config.classes_dict)
            self.eva_origins.update(config.origins_dict)
            self.to0(self.classes)
            self.to0(self.origins)
            self.to0(self.eva_classes)
            self.to0(self.eva_origins)
            self.team.update(team)
            if len(team) > 0:
                self.get_full_association(config)
                # no need to evaluate team
                # self.evaluate_association()
                # self.evaluate_team()

    def __eq__(self, other):
        if len(self.team) != len(other.team):
            return False
        if len(self.team.symmetric_difference(other.team)) > 0:
            return False
        return True

    def to0(self, dict_a):
        for a in dict_a.keys():
            dict_a[a] = 0

    def evaluate_team(self):
        """
        get team score
        :return:
        """
        eva_temp = 0
        for eva in self.eva_classes.keys():
            eva_temp += self.eva_classes[eva]
        for eva in self.eva_origins.keys():
            eva_temp += self.eva_origins[eva]
        self.evaluate = eva_temp
        return eva_temp

    def get_full_association(self, config):
        """
        set team actually association
        :return:
        """
        for hero in self.team:
            self.classes[config.heroes_dict[hero]['class']] += 1
            self.origins[config.heroes_dict[hero]['origin']] += 1
            if 'second_class' in config.heroes_dict[hero].keys():
                self.classes[config.heroes_dict[hero]['second_class']] += 1
            if 'second_origin' in config.heroes_dict[hero].keys():
                self.origins[config.heroes_dict[hero]['second_origin']] += 1

    def evaluate_association(self, config):
        """
        set team trigger association
        :return:
        """
        for association in self.classes.keys():
            for num in config.classes_dict[association]:
                if self.classes[association] >= num:
                    self.eva_classes[association] = num
        for association in self.origins.keys():
            for num in config.origins_dict[association]:
                if self.origins[association] >= num:
                    self.eva_origins[association] = num

    def add_hero(self, hero, config):
        self.team.add(hero)
        self.classes[config.heroes_dict[hero]['class']] += 1
        self.origins[config.heroes_dict[hero]['origin']] += 1
        if 'second_class' in config.heroes_dict[hero].keys():
            self.classes[config.heroes_dict[hero]['second_class']] += 1
        if 'second_origin' in config.heroes_dict[hero].keys():
            self.origins[config.heroes_dict[hero]['second_origin']] += 1
        # to Prune
        self.evaluate_association(config)
        self.evaluate_team()
        return self

    def find_candidate(self, config):
        """
        according to self.team to find candidate heroes
        :return: heroes{string}
        """
        candidates = set()
        for class1 in self.classes.keys():
            if self.classes[class1] > 0:
                candidates.update(config.class_to_hero[class1])
        for origin in self.origins.keys():
            if self.origins[origin] > 0:
                candidates.update(config.origin_to_hero[origin])
        return candidates.difference(self.team)

    def deepcopy(self, config):
        team_exist = TeamExist(config, self.team, 'copy')
        team_exist.classes.update(self.classes)
        team_exist.origins.update(self.origins)
        team_exist.eva_classes.update(self.eva_classes)
        team_exist.eva_origins.update(self.eva_origins)
        team_exist.team.update(self.team)
        team_exist.evaluate = self.evaluate
        return team_exist

    def __str__(self):
        strr = '%s\t%d\n' % (self.team, self.evaluate_team())
        for class1 in self.eva_classes.keys():
            if self.eva_classes[class1] > 0:
                strr += '%s %d   ' % (class1, self.eva_classes[class1])
        strr += '\n'
        for origin in self.eva_origins.keys():
            if self.eva_origins[origin] > 0:
                strr += '%s %d   ' % (origin, self.eva_origins[origin])
        strr += '\n'
        return strr

    def to_json(self):
        strr = dict()
        strr['team'] = list(self.team)
        strr['score'] = self.evaluate
        classes = dict()
        for class1 in self.eva_classes.keys():
            if self.eva_classes[class1] > 0:
                classes[class1] = self.eva_classes[class1]
        strr['class'] = classes
        origins = dict()
        for origin in self.eva_origins.keys():
            if self.eva_origins[origin] > 0:
                origins[origin] = self.eva_origins[origin]
        strr['origin'] = origins
        return strr
