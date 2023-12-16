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

    @abstractmethod
    def __init__(self, agent_name, config):
        pass

    @abstractmethod
    def run(self, coder):
        pass
