"""List all uploaded zip files.
"""
from app import app, mongo
from app.helpers import user_logged_in, user_path, uploaded_path
from app.mod_cmd.client_instruction import ClientInstruction
import os
import glob

def run(project = None, args = [], **kwargs):
    """List all uploaded zip files.
    """
    
    if user_logged_in():
        path = os.path.join(uploaded_path(), '*.zip')
        filenames = []
        for filepath in glob.iglob(path):
            filenames.append(os.path.basename(filepath))
        instruction = ClientInstruction({'message': "\n".join(filenames)})
    else:
        instruction = ClientInstruction({'message': 'Please login first'})

    return [project, instruction]