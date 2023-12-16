# flake8: noqa: E501


# COMMIT
commit_system = """You are an expert software engineer.
Review the provided context and diffs which are about to be committed to a git repo.
Generate a *SHORT* 1 line, 1 sentence commit message that describes the purpose of the changes.
The commit message MUST be in the past tense.
It must describe the changes *which have been made* in the diffs!
Reply with JUST the commit message, without quotes, comments, questions, etc!
"""

# COMMANDS
undo_command_reply = "I did `git reset --hard HEAD~1` to discard the last edits."

added_files = "I added these *read-write* files: {fnames}"


run_output = """I ran this command:

{command}

And got this output:

{output}
"""

fix_agent_initial_run_output = """I am trying to fix the errors I'm getting from this command:
`{command}`

I will run this command repeatedly and provide the output each time, so break down the problem into
small chunks if possible and work incrementally instead of trying to fix all the errors at once. This
process works better if you are reading the smallest set of files possible, so only add the files
you need to work on the current chunk of work!

{context}

I ran this command:

{command}

And got this output:

{output}
"""

# CHAT HISTORY
summarize = """*Briefly* summarize this partial conversation about programming.
Include less detail about older parts and more detail about the most recent messages.
Start a new paragraph every time the topic changes!

This is only part of a longer conversation so *DO NOT* conclude the summary with language like "Finally, ...". Because the conversation continues after the summary.
The summary *MUST* include the function names, libraries, packages that are being discussed.
The summary *MUST* include the filenames that are being referenced by the assistant inside the ```...``` fenced code blocks!
The summaries *MUST NOT* include ```...``` fenced code blocks!

Phrase the summary with the USER in first person, telling the ASSISTANT about the conversation.
Write *as* the user.
The user should refer to the assistant as *you*.
Start the summary with "I asked you...".
"""

summary_prefix = "I spoke to you previously about a number of things.\n"
