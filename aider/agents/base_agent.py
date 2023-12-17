from abc import ABC, abstractmethod


class AgentUnexpectedError(ValueError):
    pass


class AgentConfigError(ValueError):
    pass


class Agent(ABC):
    @classmethod
    @abstractmethod
    def type(self):
        pass

    @classmethod
    @abstractmethod
    def required_config_keys(self):
        pass

    @classmethod
    @abstractmethod
    def optional_config_keys(self):
        pass

    def read_required_config_value(self, config, key, expected_type):
        if key not in config:
            raise AgentConfigError(
                f"'{self.agent_name}' is missing required key '{key}'."
            )

        value = config[key]
        if not isinstance(value, expected_type):
            raise AgentConfigError(
                f"FixAgent '{self.agent_name}' has an invalid '{key}' value. It must be a {expected_type.__name__}."
            )
        return value

    def read_config_value(self, config, key, expected_type, default):
        value = default
        if key in config:
            value = self.read_required_config_value(config, key, expected_type)
        return value

    @abstractmethod
    def __init__(self, agent_name, config):
        self.agent_name = agent_name
        pass

    @abstractmethod
    def run(self, coder):
        pass
