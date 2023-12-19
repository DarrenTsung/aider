import subprocess
from .base_agent import Agent, AgentConfigError
from aider import prompts


class FixAgent(Agent):
    @classmethod
    def type(self):
        return "fix"

    @classmethod
    def required_config_keys(self):
        return {"command"}

    @classmethod
    def optional_config_keys(self):
        # IMPROVEMENT: allow FixAgent to call commands from a whitelisted list of commands
        # provided via `additional_allowed_commands`.
        return {"context", "max_output_lines", "add_files_mentioned_in_command_output"}

    def __init__(self, agent_name, config):
        self.agent_name = agent_name
        self.command = self.read_required_config_value(
            config, key="command", expected_type=str
        )

        self.context = self.read_config_value(
            config, key="context", expected_type=str, default=None
        )
        self.max_output_lines = self.read_config_value(
            config, key="max_output_lines", expected_type=int, default=50
        )
        self.add_files_mentioned_in_command_output = self.read_config_value(
            config, key="add_files_mentioned_in_command_output", expected_type=bool, default=True
        )

    def run(self, coder):
        coder.verbosely_list_files_in_context = True
        coder.add_line_numbers_to_content = True

        first_run = True
        while True:
            try:
                result = None
                try:
                    result = subprocess.run(
                        self.command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        shell=True,
                    )
                except Exception as e:
                    coder.io.tool_error(f"Error running command: {e}")
                    return

                # Check if the command was successful
                if result.returncode == 0:
                    coder.io.tool_output(
                        f"Command '{self.command}' executed successfully, {self.agent_name} is finished."
                    )
                    break

                command_output = "\n".join(
                    result.stdout.split("\n")[: self.max_output_lines]
                )

                # Remove files not mentioned in the output from the context every iteration of fixing.
                # This improves fix accuracy because the context gets cluttered quickly for common
                # tasks like fixing lint errors which are scattered across multiple files.
                #
                # I tried to get the LLM to drop the files from the context once it was
                # done with them, but it didn't request for any dropped files.
                dropped_files = None
                if len(coder.abs_fnames) > 0:
                    mentioned_files = set()
                    for fname in coder.abs_fnames:
                        rel_fname = coder.get_rel_fname(fname)
                        if rel_fname in command_output:
                            mentioned_files.add(fname)
                    dropped_files = [
                        coder.get_rel_fname(fname)
                        for fname in set(coder.abs_fnames) - mentioned_files
                    ]
                    coder.abs_fnames = mentioned_files
                    coder.abs_fnames_to_ranges = {fname: ranges for fname, ranges in coder.abs_fnames_to_ranges.items() if fname in coder.abs_fnames}

                if first_run:
                    new_user_message = prompts.fix_agent_initial_run_output.format(
                        command=self.command,
                        context=self.context if self.context is not None else "",
                        output=command_output,
                    )
                    first_run = False
                else:
                    new_user_message = prompts.run_output.format(
                        command=self.command,
                        output=command_output,
                    )

                if dropped_files:
                    dropped_files_joined = ", ".join(dropped_files)
                    new_user_message += f"\nI dropped these *read-write* files from the context: {dropped_files_joined}, please re-request *read-write* access for these files if you need them."

                coder.io.user_input(new_user_message, log_only=False)

                if self.add_files_mentioned_in_command_output:
                    coder.io.tool_output("\n")
                    added_files_message = coder.check_for_file_mentions(command_output, find_mentions_for_partial_files_in_chat=True)
                    if added_files_message:
                        added_files_message = f"\n{added_files_message}"
                        coder.io.user_input(added_files_message, log_only=False)
                        new_user_message += added_files_message

                while new_user_message:
                    new_user_message = coder.send_new_user_message(new_user_message)
            except KeyboardInterrupt:
                coder.io.tool_error("\n\n^C Exiting due to keyboard interrupt.")
                return
            except EOFError:
                return
