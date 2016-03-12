# Commands

This package contains all commands available for arthur app. Use following template to add more commands (like, the absolute minimum for a command):

```
def run(project = None, args = []):
    """The docstring here will be displayed when `help` command is run.

    And the docstring down here will be displayed with `help [command]` command.
    """
    return [project, instruction]
```