# install using > python3 -m pip install pyyaml
# good ref : https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started

from yaml import load, FullLoader


class YamlConfig:
    # install using > python3 -m pip install pyyaml
    # good ref : https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started
    def load_yaml(yaml_file_path):
        with open(yaml_file_path,"r") as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            ldap_config = load(file, Loader=FullLoader)
            return ldap_config

