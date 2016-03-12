"""List all projects.
"""
from app.mod_cmd.client_instruction import ClientInstruction
from app import app, mongo

def run(project = None, args = [], **kwargs):
    """List all projects you own.
    """
    projects = mongo.db.users.find_one({'username': app.session['active_user']}, projection=['projects.name'])['projects']
    message = "List of projects (load a project with 'load_project [name] command'):"
    for prj in projects:
        message += "\n%s" % prj['name']
    instruction = ClientInstruction({'message': message})
    return [project, instruction]