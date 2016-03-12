"""Upload zip command.
"""
from app.mod_cmd.client_instruction import ClientInstruction
def run(project = None, args = [], **kwargs):
    """(todo) Show upload zip panel.

    upload_zip [name]

    Args:
        name: Upload zip file and rename it with [name]. Omit the '.zip' extension.
    """
    instruction = ClientInstruction({
        'action': 'showUploadWindow()'
    })
    return [project, instruction]