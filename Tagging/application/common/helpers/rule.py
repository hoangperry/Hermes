import application.common.helpers.logger as logger
import os
import re
import ast

class RuleLoader:
    """
    Load all rule in config path
    Each page has config rule file with .rule extension
    """
    def __init__(self, rule_path):
        self.rule_path = rule_path

    @staticmethod
    def read_rule(file_name):
        """
        Read rule from file.rule
        Each rule written in line, separated by =>
        Ex: RULE => div.h1
        Any invalid format can be use as comment
        :param file_name:
        :return: Dictionary of rules as { rule_name : rule }
        """
        # read all lines in file
        all_lines = open(file_name).readlines()

        # result stored in dictionary
        result_dict = dict()

        # read rules
        for line in all_lines:
            try:
                splited_values = line.split("=>")

                # get key, value and check
                key = splited_values[0].strip()
                value = splited_values[1].strip()

                if value == 'null' and re.match(r'pre_.*', value):
                    value = ''

                if key == 'use_selenium':
                    value = ast.literal_eval(value)

                # if invalid line format, skip this lines
                result_dict[key] = value
            except Exception as ex:
                pass

        return result_dict

    def load(self):
        """
        Load all rules in directory
        All rules will be read by recursive walks
        :return: list of dictionary rules
        """
        all_rules = dict()

        # recursive walks in directory and find all files end with .rule
        for root, dirs, files in os.walk(self.rule_path):
            for file in files:
                if file.endswith(".rule"):
                    file_name = os.path.join(root, file)
                    rule = RuleLoader.read_rule(file_name)
                    all_rules[rule['domain']] = RuleLoader.read_rule(file_name)

        return all_rules
