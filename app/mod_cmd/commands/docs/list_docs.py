"""List documents in current ArthurProject
"""
import os, sys, inspect
# This needs to be included here to ensure path is loaded from app main directory.
base_path = os.path.realpath(
    os.path.abspath(
        os.path.join(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()
                )
            )[0],
            '..',
            '..',
            '..',
            '..'
        )
    )
)
print base_path
sys.path.append(base_path)

from app.mod_cmd.client_instruction import ClientInstruction
from app.helpers import docs_path, save_project
from zipfile import ZipFile
from app import mongo
from libs.arthur.clusterer.dumb_clusterer import DumbClusterer

def run(project = None, args = [], **kwargs):
    """List all documents in this project.

    usage: list_docs option

    Args:
        option: Type of documents to display: "all"(default), "corrected", "guessed", "unprocessed".
    """
    project, instruction = list_docs(project)
    return [project, instruction]

def list_docs(project):
    """List all documents in a project

    Attr:
        project: Project to get list of documents from
    """
    if project == None:
        instruction = ClientInstruction({
            'pass_project': False,
            'pass_docs': False,
            'message': "Please load a project first with command `load_project [project name]`"
        })
    else:
        path = docs_path()
        del project.active_doc
        project.active_doc = None
        save_project(project)

        with ZipFile(path, 'r') as zipfile:
            instruction = ClientInstruction({
                'pass_project': True,
                'pass_docs': True,
                'docs': get_doc_infos(project, zipfile),
                'project': project.to_dict(),
                'page': '#doc-list',
                'message': "Listing documents of project %s" % project.name
            })
    return [project, instruction]

def get_doc_infos(project, zipfile):
    """Gets all information of documents inside given zip file.

    Make sure that the zipfile is already opened before passing it here.
    One way to call this, for example:
    >>> from libs.arthur.project import ArthurProject
    >>> project = ArthurProject()
    >>> filepath = ''
    >>> with ZipFile(filepath, 'r') as zipfile:
    ...     get_doc_infos(zipfile)

    Attr:
        project: Arthur project.
        zipfile: Zip file handler.

    Returns:
        list: A list of dictionary with following information:
              - name: Name of document file.
              - size: Filesize of that document file.
              - num_data_fields_labeled: Number of data fields labeled.
              - num_data_fields_total: Total number of data fields.
    """
    docinfos = []
    for zipinfo in zipfile.infolist():
        num_data_fields_labeled = 0
        num_data_fields_total = 0
        found_docs = filter(lambda d: d.name == zipinfo.filename, project.docs)

        if len(found_docs) > 0:
            num_data_fields_labeled = mongo.db.data_fields.count({'project_id': project._id, 'doc_id': found_docs[0]._id})
            num_data_fields_total = found_docs[0].num_data_fields
        docinfos.append({
            'name': zipinfo.filename,
            'size': zipinfo.file_size,
            'blocks': [],
            'num_data_fields_labeled': num_data_fields_labeled,
            'num_data_fields_total': num_data_fields_total
        })
    return docinfos

if __name__ == '__main__':
    import doctest
    import pdb
    doctest.testmod()