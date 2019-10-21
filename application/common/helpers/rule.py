import yaml


class RuleLoaderV2:
    """
    Load all rule in config path
    Each page has config rule file with .rule extension
    """

    def __init__(self, rule_file):
        self.rule_file = rule_file

    def load_from_yaml(self):
        """
        Load all rules in directory
        All rules will be read by recursive walks
        :return: list of dictionary rules
        """
        with open(self.rule_file, 'r') as stream:
            return yaml.safe_load(stream)

    def load_from_db_config(self):
        raise NotImplementedError("This method will be implemented later")
