import yaml
from .fix_agent import FixAgent


class AgentConfig:
    def __init__(self, config_texts):
        self.agents = {}
        merged_agents_config = {}

        for config_text in config_texts:
            if config_text:
                parsed_config = yaml.safe_load(config_text)
                for key in parsed_config:
                    if key in merged_agents_config:
                        raise ValueError(
                            f"Duplicate key '{key}' found in agent configurations."
                        )
                    merged_agents_config[key] = parsed_config[key]

        for agent_name, config in merged_agents_config.items():
            if "type" not in config:
                raise ValueError(
                    f"Agent '{agent_name}' is missing required 'type' key."
                )

            if not isinstance(config["type"], str):
                raise ValueError(
                    f"Agent '{agent_name}' has an invalid 'type' value. It must be a string."
                )

            agent_type = config["type"]
            del config["type"]

            agent_class = None
            for curr_agent_class in [FixAgent]:
                if agent_type != curr_agent_class.type():
                    continue

                self.agents[agent_name] = curr_agent_class(agent_name, config)
                agent_class = curr_agent_class

            if not agent_class:
                raise ValueError(
                    f"Unknown agent type '{agent_type}' for agent '{agent_name}'."
                )

            required_keys = agent_class.required_config_keys()
            optional_keys = agent_class.optional_config_keys()
            all_keys = required_keys | optional_keys

            missing_keys = required_keys - config.keys()
            if missing_keys:
                raise ValueError(
                    f"Agent '{agent_name}' is missing required keys: {missing_keys}."
                )

            unknown_keys = config.keys() - all_keys
            if unknown_keys:
                raise ValueError(
                    f"Agent '{agent_name}' has unknown keys: {unknown_keys}."
                )

    def is_agent(self, agent_name):
        return agent_name in self.agents

    def run_agent(self, agent_name, coder):
        agent = self.agents[agent_name]
        if not agent:
            # Assume checked by `is_agent()` beforehand.
            raise ValueError(
                f"run_agent() reached with missing agent '{agent_name}', programmer error!"
            )

        agent.run(coder)
