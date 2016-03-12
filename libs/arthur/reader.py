"""Contain functions to read ArthurDocument objects

This includes clustering the boxes by textbox ids, then split the paragraphs within.

corpus is created as reading takes place.
"""

if __name__ == '__main__':
    # Needed up here for unit testing. This code piece basically
    # sets base_path to arthur library's directory.
    import os, sys, inspect
    base_path = os.path.realpath(
        os.path.abspath(
            os.path.join(
                os.path.split(
                    inspect.getfile(
                        inspect.currentframe()
                    )
                )[0]
            )
        )
    )
    sys.path.append(base_path)

from document import ArthurDocument
from zipfile import ZipFile
from errors import BatchReadingError
from scipy.spatial import cKDTree
from helpers import unique_rows
import numpy as np
import os

def read(document, clusterer, project_id=None):
    """Reads a document, returning (unscored) data fields.
    ## How to use:

    First, make sure that corpus is created and updated by running :func:`create_corpus` method
    below. Note that `sys.stdout` can be replaced with any object containing `write` method.
    >>> zip_path = os.path.join(base_path, 'test/test.zip')
    >>> corpus_dir = os.path.join(base_path, 'test/corpus')
    >>> try:
    ...     create_corpus(zip_path, corpus_dir, stdout=sys.stdout, overwrite=True) # doctest:+ELLIPSIS
    ... except BatchReadingError as e:
    ...     print(e.msg)
    ...     print('last batch was: %i' % e.last_batch)
    ... except Exception as e:
    ...     print(e.message)
    processing 10091948.pdf (1/7)
    processing 11758.docx (2/7)
        empty text! moving on...

    Then read a document to extract its data fields:
    >>> from document import ArthurDocument
    >>> pdf_path = base_path + '/test/test.pdf'
    >>> with open(pdf_path, 'rb') as f:
    ...     document = ArthurDocument(f.read(), doctype='pdf', name='test.pdf')
    >>> from clusterer.dumb_clusterer import DumbClusterer
    >>> clusterer = DumbClusterer(corpus_dir)
    >>> data_fields = read(document, clusterer)
    >>> len(data_fields) > 0
    True

    One of the data fields must contain a now correctly separated "Property Type":
    >>> "Property Type" in map(lambda df: df['text'], data_fields)
    True

    Args:
        document: ArthurDocument to apply the algorithm to.

    Returns:
        list: Data fields
    """
    textboxes = __extract_textboxes(document)
    data_fields = []
    counter = 0
    for textbox_id, textbox in enumerate(textboxes):
        counter += 1
        remove = __find_duplicates(textbox)
        ctextbox = np.delete(textbox, remove, axis=0)
        for exp in clusterer.extract_expressions(document, ctextbox):
            data_fields.append({
                'id': counter,
                'project_id': str(project_id),
                'doc_id': document._id,
                'page': ctextbox[0][document.get_feature_id('page')],
                'text': exp['text'],
                'x': exp['x'],
                'x1': exp['x1'],
                'y': exp['y'],
                'y1': exp['y1']
            })

    return data_fields

def create_corpus(zip_path, corpus_dir, batch_size=100, start_batch=0, stdout=None, overwrite=False):
    """Create corpus from zip file. A corpus is basically just a list of text files.
    Args:
        zip_path(str):    Path of zip file to load.
        corpus_dir(str):  Path to corpus dir where the files will be written into.
        batch_size(int):  Size of batch to be processed. If we have one million documents,
                          we'd want to process them in batches. Defaults to 100.
        start_batch(int): When an error happens in batch processing, reader will return
                          index of the last batch processed. enter that index value to
                          start processing from that batch index. Defaults to 0.
        stdout(Object):   Pass sys.stdout to print progress, or pass any object with `write`
                          method to pass printed progress to it.
        overwrite(bool):  Overwrite files as they are created?
    """
    zipfile = ZipFile(zip_path, 'r')
    namelist = zipfile.namelist()
    jobs_total = len(namelist)
    jobs_left = jobs_total - start_batch*batch_size
    
    def process_batch(zipfile, corpus_dir, batch, total, counter=0):
        for docname in batch:
            counter += 1
            if not os.path.exists(corpus_dir):
                os.makedirs(corpus_dir)
            filename = os.path.join(corpus_dir, docname+'.txt')
            if os.path.isfile(filename) and not overwrite:
                if stdout is not None:
                    stdout.write("%s already exists (%i/%i)\n" % (docname, counter, total))
            else:
                content = zipfile.read(docname)
                if stdout is not None:
                    stdout.write("processing %s (%i/%i)\n" % (docname, counter, total))
                document = ArthurDocument(content, name=docname)

                textboxes = __extract_textboxes(document)

                texts = []
                for idx, textbox in enumerate(textboxes):
                    remove = __find_duplicates(textbox)
                    ctextbox = np.delete(textbox, remove, axis=0)
                    texts.append(document.get_text(ctextbox))

                if len(texts) > 0:
                    if not os.path.isdir(corpus_dir):
                        os.mkdir(corpus_dir)

                    with open(filename,'w') as fout:
                        for text in texts:
                            print>>fout, text
                else:
                    if stdout is not None:
                        stdout.write("    empty text! moving on...\n")

    while jobs_left > 0:
        job_start = jobs_total - jobs_left
        job_end = job_start + batch_size
        batch = namelist[job_start:job_end]
        process_batch(zipfile, corpus_dir, batch, jobs_total, job_start)
        jobs_left -= batch_size

    zipfile.close()

def __extract_textboxes(document):
    """Extract textboxes from document.

    It is kept here instead of document since ArthurDocument does not need to know the concept of a textbox.
    In ArthurDocument a textbox is just a set of features happen to have the same textbox_id. Different document
    type may have different configurations and approaches to this.

    Args:
        document(ArthurDocument): ArthurDocument instance textboxes will be extracted from.

    Returns:
        list: List of textboxes i.e. grouped features from document.
    """
    features = document.get_features()
    page_feature_id = ArthurDocument.get_feature_id('page')
    textbox_feature_id = ArthurDocument.get_feature_id('textbox_id')

    page_textbox_pairs = features[:, [page_feature_id, textbox_feature_id]]
    unique_page_textbox_pairs = unique_rows(page_textbox_pairs)
    textboxes = []
    for page, textbox_id in unique_page_textbox_pairs:
        textbox = features[np.where(
            (features[:, page_feature_id]==page) * 
            (features[:, textbox_feature_id]==textbox_id)
        )]
        textboxes.append(textbox)
    return textboxes

def __find_duplicates(features):
    """Finds duplicates of a set of features.
    
    Example of usage
    >>> pdf_path = os.path.join(base_path, 'test', 'test.pdf')
    >>> f = open(pdf_path, 'rb')
    >>> document = ArthurDocument(f.read(), doctype='pdf')
    >>> textboxes = __extract_textboxes(document)
    >>> print(document.get_text(textboxes[11]))
    Property TypeProperty Type Property TypeProperty Type Single Family

    >>> remove_indexes = __find_duplicates(textboxes[11])
    >>> cfeatures = np.delete(textboxes[11], remove_indexes, axis=0)
    >>> print(document.get_text(cfeatures))
    Property Type Single Family

    Args:
        features(np.array): List of features to find duplicates of.

    Returns:
        list: Returns a tuple of corrected block and removed indexes.
    """
    fxid = ArthurDocument.get_feature_id('x')
    fyid = ArthurDocument.get_feature_id('y')
    positions = features[:,[fxid,fyid]]
    tree = cKDTree(positions)

    # Removes duplicate elements that are close together
    radius = 0.4
    neighbors = tree.query_ball_point(positions, radius)
    neighbors = np.unique(neighbors)
    # This returns numpy array like:
    # [[0, 13, 26, 39] [1, 14, 27, 40] [5, 31, 44, 18] [11, 24, 37, 50]
    # [16, 29, 42, 3] [17, 30, 43, 4] [21, 8, 34, 47] [22, 35, 48, 9]
    # [32, 45, 19, 6] [36, 23, 10, 49] [38, 12, 25, 51] [41, 28, 2, 15]
    # [46, 33, 7, 20] [52] [53] [54] [55] [56] [57] [58] [59] [60] [61] [62]
    # [63] [64]]
    #
    # Which we will then remove duplicates e.g. remove index 13, 26, 39, 14, 27, etc.
    removed = []
    for n in neighbors:
        removed.extend(np.sort(n)[1:])
    
    # Removes image elements
    removed.extend(np.where(features[:,ArthurDocument.get_feature_id('img_width')] != -1)[0].tolist())

    return removed
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
