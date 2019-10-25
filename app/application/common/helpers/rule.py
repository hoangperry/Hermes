import yaml
import glob
import os


def load_from_yaml(yaml_file):
    """
    Load all rules in directory
    All rules will be read by recursive walks
    :return: list of dictionary rules
    """
    with open(yaml_file, 'r') as stream:
        return yaml.safe_load(stream)


def load_from_db_config():
    raise NotImplementedError("This method will be implemented later")


def load_from_yaml_dir(directory):
    dict_rule = dict()
    for file in glob.glob(os.path.join(directory, "/**")):
        dict_rule[os.path.splitext(os.path.basename(file))[0]] = load_from_yaml(file)

    return dict_rule
