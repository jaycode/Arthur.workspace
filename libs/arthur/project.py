"""
This module contains ArthurProject that stores all
the important details needed from Arthur system, in addition
to other classes and functions that may be required.
"""

from helpers import format_size
import numpy as np
from blocks_words import ArthurBlocks, ArthurWords
import shutil

class ArthurProject():
    """Object that wraps up an Arthur project.

    This is the server counterpart of js model's Project (and other
    models contained by it respectively e.g. ActiveDoc for this object's
    :attr:`active_doc` attribute, which is an instance of ArthurDocument).
    """

    def __init__(self, name='', active_doc=None, context=None, _id=None, docs=[]):
        """Initializes ArthurProject instance.

        Args:
            name: Name of project.
            active_doc(ArthurDocument): Currently active document.
            context(str): Context associated with this project.
            _id(ObjectId): ID of this project (for database keeping).
            # docs: List of ArthurDocuments.
        """
        self._id = _id
        self.name = name
        self.active_doc = active_doc
        self.context = context
        self.docs = docs

    def to_dict(self):
        """Serializes this object to a python dictionary.
        """
        active_doc = None
        if self.active_doc is not None:
            active_doc = self.active_doc.to_dict(raw=False, with_details=True)

        doclist = []
        for doc in self.docs:
            doclist.append(doc.to_dict(raw=False, with_details=False))

        obj = {
            'name': self.name,
            'active_doc': active_doc,
            'docs': doclist
        }
        return obj

    def get_doc_infos(self, zipfile):
        """Gets all informations of documents inside given zip file.

        Make sure that the zipfile is already opened before passing it here.
        One way to call this, for example:
        >>> with ZipFile(filepath, 'r') as zipfile:
        >>>     arthurProject.get_doc_infos(zipfile)

        Attr:
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
            found_docs = filter(lambda d: d.name == zipinfo.filename, self.docs)
            if len(found_docs) > 0:
                num_data_fields_total = found_docs[0].num_blocks
            docinfos.append({
                'name': zipinfo.filename,
                'size': zipinfo.file_size,
                'num_data_fields_labeled': num_data_fields_labeled,
                'num_data_fields_total': num_data_fields_total
            })
        return docinfos

    def nuke_docs(self, corpus_dir=None):
        """Remove all docs from this project.
        """
        del self.docs[:]
        if corpus_dir is not None and os.path.isdir(corpus_dir):
            shutil.rmtree(corpus_dir)