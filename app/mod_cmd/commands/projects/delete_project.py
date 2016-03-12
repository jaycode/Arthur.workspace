"""Delete a project
"""
def run(project = None, args = [], **kwargs):
    """Delete a project. Default project (risky) can't be deleted.

    delete_project [name]

    Args:
        name: Name of project to be deleted.
    """

    _delete_project(name)
    return [project, instruction]

def _delete_project(name):
    pass