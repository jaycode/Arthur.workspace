#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""Load zip file into current ArthurProject
"""
if __name__ == '__main__':
    # Needed up here for unit testing. This code piece basically
    # sets base_path to Arthur app's root directory.
    import doctest
    import os, sys, inspect
    import pdb
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
    sys.path.append(base_path)

from zipfile import ZipFile
from app.mod_cmd.client_instruction import ClientInstruction
from app import app, mongo
from app.helpers import user_path, uploaded_path, docs_path, save_project
from app.mod_cmd.commands.help import get_docs
import os
from libs.arthur import ArthurDocument
import numpy as np
import sockjs.tornado
from bson.objectid import ObjectId
from argparse import ArgumentParser
from libs.arthur.reader import create_corpus, read

def run(project = None, args = [], **kwargs):
    """Load all documents inside a zip file in server into currently active project. Runs 'upload_zip' instead if file does not exist.

    usage: load_zip [--keep] [--nuke] name

    Args:
        name: Zip file to load.

    Optional arguments:
      --keep, -k               By default, load_zip will remove uploaded zip file. Add this option to keep that file.
      --nuke, -n               ☠ Destroy all previous documents in this project and recreate them. ☠
      --overwrite_corpus, -o   Overwrite corpus as they are created.

    """
    
    if project is None:
        instruction = ClientInstruction({'message': 'Please load a project.'})
    else:
        if len(args) == 0:
            docs = get_docs('load_zip')
            instruction = ClientInstruction({
                'message': "\n".join(docs)
            })
        else:
            parser = ArgumentParser(add_help=False)
            parser.add_argument('name')
            parser.add_argument('--keep', '-k', action='store_true')
            parser.add_argument('--nuke', '-n', action='store_true')
            parser.add_argument('--overwrite_corpus', '-o', action='store_true')
            parsed_args = parser.parse_args(args)

            name = parsed_args.name
            keep = parsed_args.keep
            nuke = parsed_args.nuke
            frompath = os.path.join(uploaded_path(), name)
            project, instruction = load_zip(project, docs_path(), frompath, keep=keep, nuke=nuke, connection=kwargs['connection'], mongo=mongo)
            save_project(project)

    return [project, instruction]

def load_zip(project, docs_path, zip_path, keep=False, nuke=False, connection=None, mongo=None):
    """Loads documents from zip_path into project.

    Args:
        project: ArthurProject object documents will be loaded into.
        docs_path: Path to docs.zip of a project.
        zip_path: Path to zip file containing documents to load.
        keep: By default, load_zip will remove uploaded zip file. Set this to True to keep that file.
        connection: Pass a sockjs.tornado.SockJSConnection object to update progress dynamically,
                    otherwise print will be used.

    While loading each document, its content will be clustered into several data_fields which will
    then be used for learning algorithms.
    >>> from libs.arthur import ArthurProject
    >>> docs_path = os.path.join(base_path, 'test', 'unit', 'test_project', 'docs.zip')
    >>> project = ArthurProject('test_project')
    >>> zip_path = os.path.join(base_path, 'test', 'unit', 'test.zip')
    >>> project, instruction = load_zip(project, docs_path, zip_path, keep=True)
    Found document "11758.docx". Created 0 data_fields (not entered into database).
    Found document "348418.pdf". Created 50 data_fields (not entered into database).
    Found document "348608.pdf". Created 53 data_fields (not entered into database).

    >>> print(instruction.get_value('message')) # doctest:+ELLIPSIS
    Loaded ...

    Data fields should then be available for all documents.

    Args:
        project: ArthurProject instance to be updated.
        zip_path (str): Path to zip file containing documents to be loaded.
        keep (bool): If True, keep loaded zip file, otherwise delete it after all documents
                     loaded into project. Defaults to False.
        mongo (MongoClient): If not empty, will store blocks into mongodb database.

    Returns:
        list: [ArthurProject instance, ClientInstruction instance]
    """
    found = []
    added = []
    try:
        fromzip = ZipFile(zip_path, 'r')
        try:
            topath = docs_path
            mode = 'a'

            if nuke:
                mode = 'w'
                project.nuke_docs(corpus_dir=corpus_path())
                project.active_doc = None
                message = "☠ - Nuked project's documents - No Survivor!"
                if isinstance(connection, sockjs.tornado.SockJSConnection):
                    connection.send(message)
                else:
                    print(message)
                if mongo:
                    mongo.db.data_fields.delete_many({'project_id': project._id})

            # Create corpus
            send(connection, "Attempt to create corpus...")
            create_corpus(fromzip, corpus_path(), stdout=connection, overwrite=overwrite_corpus)

            tozip = ZipFile(topath, mode)

            for docname in fromzip.namelist():
                content = fromzip.read(docname)
                try:
                    tozip.getinfo(docname)
                    found.append(docname)
                    message = "Found document \"%s\"." % docname
                except:
                    # Add to project's list of documents
                    tozip.writestr(docname, content)
                    added.append(docname)
                    message = "Loaded document \"%s\"." % docname
                # Checks if data fields have been created for this document, add if they haven't.
                documents = filter(lambda d: d.name == docname, project.docs)
                new_data_fields = []
                if len(documents) == 0:
                    document = ArthurDocument(content, name=docname, project_id=project._id, _id=ObjectId())
                    project.docs.append(document)
                    if mongo is not None:
                        # Todo: Use transaction and save in bulk instead.
                        save_project(project)
                    have_data_fields = False
                else:
                    document = documents[0]
                    have_data_fields = True
                    if document.num_data_fields == 0:
                        have_data_fields = False

                if have_data_fields:
                    message += " Already has %i data fields." % document.num_blocks 
                else:
                    new_data_fields = read(document, project_id=project._id)
                    if mongo is not None:
                        if len(new_data_fields) == 0:
                            total_inserted_data_fields = 0
                        else:
                            total_inserted_data_fields = len(mongo.db.data_fields.insert_many(new_data_fields).inserted_ids)
                            save_project(project)
                        message += " Created %i data fields and entered them into database." % (total_inserted_data_fields)
                    else:
                        message += " Created %i data fields (not entered into database)." % (len(new_data_fields))

                send(connection, message)

        except KeyError as e:
            instruction = ClientInstruction({'message': e[1]})
            return (project, instruction)
    except OSError as e:
        if e.errno == errno.EEXIST:
            instruction = ClientInstruction({'message': "File %s does not exist." % name})
            return (project, instruction)
        else:
            instruction = ClientInstruction({'message': e[1]})
            return (project, instruction)
    except IOError as e:
        instruction = ClientInstruction({'message': e[1]})
        return (project, instruction)

    fromzip.close()
    tozip.close()
    del_msg = ''
    if not keep:
        os.remove(zip_path)
        del_msg = " Zip file \"%s\" deleted." % name

    instruction = ClientInstruction({
        'detail': {'found': found, 'added': added},
        'message': "Loaded %i files. %i files already found in storage.%s" % (len(added), len(found), del_msg)
    })
    return [project, instruction]

def send(connection, message):
    if isinstance(connection, sockjs.tornado.SockJSConnection):
        connection.send(message)
    else:
        print(message)

if __name__ == '__main__':
    doctest.testmod()