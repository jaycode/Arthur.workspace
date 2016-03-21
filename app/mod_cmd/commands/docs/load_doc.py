"""Load a document
"""
from zipfile import ZipFile
from app.helpers import docs_path, save_project
from libs.arthur import ArthurDocument
import os
from app.mod_cmd.client_instruction import ClientInstruction
from app import app, mongo
from bson import ObjectId

def run(project = None, args = [], **kwargs):
    """Load a document.

    load_doc [name] [type]

    Args:
        name: Name of document to load.
        type: (Optional) Type of document will be inferred from file extension, but
              you can also override it with this setting. Example: :load_doc document.xxx pdf:
              to load document.xxx with pdf reader tool.
    """
    kwargs['connection'].broadcast(kwargs['connection'].participants, "Loading document...")
    name = args[0]
    _, filetype = os.path.splitext(name)
    if len(args) > 1:
        filetype = args[1]
    project, instruction = load_doc(name, doctype=filetype, project=project)
    return [project, instruction]

def load_doc(name, doctype = None, project = None):
    """Load document

    Args:
        name: Name of document (file must exist in :/username/project/docs.zip: file).
        doctype: Type of document. 'pdf', 'docx', etc.
        project: reference to ArthurProject object.

    Returns:
        list: List of two objects, ArthurProject and ClientInstruction instance.
    """
    if project is None:
        instruction = ClientInstruction({'message': 'Please load a project.'})
    else:
        try:
            path = docs_path()
            with app.get_path(path) as path:
                with ZipFile(path, 'r') as docs:
                    text = docs.read(name)
            doc = ArthurDocument(text=text, doctype=doctype, name=name)
            project.active_doc = doc
            save_project(project)
            instruction = ClientInstruction({
                'pass_project': True,
                'data_fields': get_docblocks(project, name),
                'page': '#doc-view',
                'message': "Document \"%s\" loaded" % name
            })
        except OSError as e:
            if e.errno == errno.EEXIST:
                instruction = ClientInstruction({'message': "File %s does not exist." % name})
                return (project, instruction)
            else:
                instruction = ClientInstruction({'message': "OSError: " + e[1]})
                return (project, instruction)
        except IOError as e:
            instruction = ClientInstruction({'message': "IOError: " + e[1]})
            return (project, instruction)
        except KeyError as e:
            # Usually for when active_doc not found.
            instruction = ClientInstruction({'message': "KeyError: " + str(e)})
            return (project, instruction)
    return (project, instruction)

def get_idocblocks(project, docname):
    cursor = mongo.db.users.aggregate([
        {'$unwind': '$projects'},
        {'$unwind': '$projects.docs'},
        {'$match': {'projects._id': project._id, 'projects.docs.name': docname}},
        {'$project': {'projects.docs': 1}}
    ])
    doc_id = None
    doc = next(cursor, None)
    if doc:
        doc_id = doc['projects']['docs']['_id']
    docblocks = mongo.db.docblocks.find({
        'project_id': ObjectId(project._id),
        'doc_id': ObjectId(doc_id)
    })
    return docblocks

def get_docblocks(project, docname):
    docblocks = get_idocblocks(project, docname)
    if docblocks.count() == 0:
        return []
    else:
        blocks = []
        for docblock in docblocks:
            docblock['project_id'] = str(docblock['project_id'])
            docblock['_id'] = str(docblock['_id'])
            docblock['doc_id'] = str(docblock['doc_id'])
            blocks.append(docblock)
        return blocks
