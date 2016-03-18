"""This module is useful to allow user finds out current state of their work.
"""
from app.mod_cmd.client_instruction import ClientInstruction
from app.helpers import docs_path
from zipfile import ZipFile
import app

def run(project = None, args = [], **kwargs):
    """Show status of current project. Keep checking this often!

    status [item]

    Args:
        item: Item from the project you wish to view in more detail. Possible values:
              - docs: View all docs currently being worked on. Shorthand of `list_docs` command.
              - context: View the detail of context currently used in the project.
    """
    if project is None:
        message = ""
    else:
        active_doc = ''
        if 'last_loaded_doc' in app.session:
            active_doc = app.session['last_loaded_doc']
        
        path = docs_path()
        with ZipFile(path, 'r') as zipfile:
            docs = len(zipfile.namelist())
        current_context = project.context['name']
        dfcount = mongo.db.data_fields.count({'project_id': project._id})

        message = \
        "Project name: %s\n" \
        "Last loaded document: %s\n" \
        "Total documents: %d\n" \
        "# data fields: %d\n" \
        "Context: %s" \
        % (project.name, active_doc, docs, dfcount, current_context)
    instruction = ClientInstruction({
        'message': message
    })
    return [project, instruction]