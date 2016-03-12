"""Load a project.
"""
from app import mongo
from app.mod_cmd.commands import status
from libs.arthur import ArthurProject, ArthurDocument
import os
from app.mod_cmd.client_instruction import ClientInstruction
from app import app
from app.mod_cmd.commands.docs.load_doc import load_doc

def run(project = None, args = [], **kwargs):
    """Load a project.

    usage: load_project name

    Args:
        name: Name of project to load.
    """
    name = args[0]
    project, instruction = load_project('default', name)
    if project is None:
        instruction = ClientInstruction({'message': "Project \"%s\" does not exist. Run 'list_projects' to view available projects." % name})
    else:
        app.session['active_doc'] = None
        app.session['active_project'] = name
        project, instruction = status.run(project)
        instruction.set_value('pass_project', True);
        instruction.set_value('page', '#doc-list');
        instruction.set_message(("Project \"%s\" loaded.\n-----------------------------\n" + instruction.get_message()) % project.name)
    return [project, instruction]

def load_project(username, project_name):
    """Load a project.

    This method is accessible from other parts of the app.

    Args:
        username: Username owning the project.
        project_name: Name of project to load.
    """
    # projection is important here to get only the projects with given name.
    user_data = mongo.db.users.find_one({'username': username, 'projects.name': project_name},
        projection=['username', 'projects.$'])

    if user_data is None:
        return (None, None)
    else:
        project_data = user_data['projects'][0]
        
        docs = []
        if 'docs' in project_data:
            for doc_data in project_data['docs']:
                docs.append(ArthurDocument(**doc_data))

        project = ArthurProject(
            name = project_data['name'],
            context = mongo.db.contexts.find_one({'_id': project_data['context_id']}),
            _id = project_data['_id'],
            docs = docs
        )

        instruction = None
        if 'active_doc' in project_data and project_data['active_doc'] is not None:
            project, instruction = load_doc(project_data['active_doc'], project=project)
        return (project, instruction)
