from yaml import load, FullLoader
import os
# install using > python3 -m pip install pyyaml
# good ref : https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started


class YamlConfig:
    # install using > python3 -m pip install pyyaml
    # good ref : https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started
    def load_yaml(yaml_file_path):
        with open(yaml_file_path, "r") as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            ldap_config = load(file, Loader=FullLoader)
            return ldap_config

    @staticmethod
    def get_config():
        yaml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../resources/config.yaml')
        print("yaml_file_path=" + yaml_file_path)
        config_dict = YamlConfig.load_yaml(yaml_file_path)
        return config_dict
