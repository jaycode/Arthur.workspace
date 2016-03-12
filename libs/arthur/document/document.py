"""
This module contains classes related to a document object used
by Arthur, namely ArthurDocument, along with its elements.
"""

from pdfminer.pdfparser import PDFStreamParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

from pdf_processors import process_pdf

import numpy as np
from collections import namedtuple

class ArthurDocument(object):
    """An object used in Arthur for various document related functions.

    Here is an example of using ArthurPDFConverter to convert a pdf
    document into an ArthurDocument.

    >>> pdf_path = base_path + '/test/test.pdf'
    >>> f = open(pdf_path, 'rb')
    >>> document = ArthurDocument(f.read(), doctype='pdf', name='testname')
    >>> features = document.get_features()
    >>> print features # doctest:+ELLIPSIS
    [[ -1.00000000e+00  -1.00000000e+00   1.00000000e+00 ...,   5.99999760e+01
    ...

    How to get name:
    >>> document.name
    'testname'

    >>> ArthurDocument.get_feature_names()
    ['img_height', 'img_width', 'page', 'size', 'textbox_id', 'textline_id', 'x', 'x1', 'y', 'y1']

    Reconstruct text from a single feature:
    >>> print document.get_text(features[58])
    1

    Reconstruct text from multiple features:
    >>> selected = features[np.where(
    ... (features[:,ArthurDocument.get_feature_id('textbox_id')] == 1) *
    ... (features[:,ArthurDocument.get_feature_id('page')] == 1))]
    >>> print document.get_text(selected)
    Page 1 of 3

    Setting :attr:`_others_attr`.
    >>> document.set_other_attr('arbitrary', 'arbitrary_value')
    >>> print(document.get_other_attr('arbitrary'))
    arbitrary_value

    Sample usage of :func:`to_dict`.
    >>> doc_dict = document.to_dict(with_details=True)
    >>> print(isinstance(doc_dict, dict) and 
    ...     'text' in doc_dict['elements'][0] and
    ...     'features' in doc_dict['elements'][0] and
    ...     'name' in doc_dict and
    ...     'page_infos' in doc_dict
    ... )
    True

    Getting page information
    >>> print(len(document._page_infos))
    3

    >>> print(document._page_infos[0])
    ArthurDocumentPageInfo(number=1, width=612, height=792)

    Sorting features
    >>> fsort = np.array([[1,2,3,4,5,6,7,8, 9,10],
    ...                   [0,1,2,3,4,5,6,7, 8, 9],
    ...                   [2,3,4,5,6,7,8,9,10,11]])
    >>> ArthurDocument.sort_features(fsort, ['page', 'textbox_id'])
    array([[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
           [ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10],
           [ 2,  3,  4,  5,  6,  7,  8,  9, 10, 11]])

    Attributes:
        num_data_fields Number of data fields.

        raw: Raw text.
        _elements: (read-only) List of ArthurDocumentElement instances. Edit via method :func:`write`.
                   Elements differ from features in that they store a text.
        
        _page_infos: (read-only) List of ArthurDocumentPageInfo instances detailing page info
                     (width and height, page number, and maybe other features we may later need
                     for learning). Edit via method :func:`write_page_info`.
        
        _data: (read-only) Numpy array gathered from self._elements. This array contains id (to
               lookup for elements in :func:`get_text`). To get only the features, use method
               :func:`get_features`.
        
        _others: (read-only) Other attributes of this document that will be outputted with
                 :func:`to_dict()` method.
                 They are also retrieve / updateable by function :func:`get_other_attr(key)` and
                 :func:`set_other_attr(key)`.
        
        __page_numbers: (private) A list of registered page numbers, so we don't have to search through all page_infos
                        to find out if a page exists in document.
    """

    def __init__(self, text=None, doctype=None, num_data_fields=0, _id=None, name=None, **kwargs):
        """Initializes ArthurDocument instance.

        Args:
            text: Text gathered from a read file. Currently supports only pdf,
                  but should later be expanded to others. Optional. When empty,
                  no need to read text during object creation.
            doctype: Type of given text. If doctype is not given, try one by one:
                     pdf, docx, etc.
            kwargs: Other keyword arguments. Can be used to store arbitrary values
                    during document creation (will be returned by to_dict() method).

        """
        self.num_data_fields= num_data_fields
        self.raw = ''
        self.name = name

        self._id = _id
        self._elements = []
        self._page_infos = []
        self._data = None
        self._others = kwargs

        self.__page_numbers = []

        if text is not None:
            if doctype == 'pdf':
                parser = PDFStreamParser(text)
                document = PDFDocument(parser)
            else:
                try:
                    self.raw = text
                    parser = PDFStreamParser(text)
                    document = PDFDocument(parser)
                    doctype = 'pdf'
                except PDFSyntaxError:
                    doctype = 'text'

            if doctype == 'pdf':
                if not document.is_extractable:
                    raise PDFTextExtractionNotAllowed
                process_pdf(self, text)

    def write(self, element=None):
        """Writes an ArthurDocumentElement to this document for
        further processing.

        Args:
            element: ArthurDocumentElement object.
        """
        self._elements.append(element)

    def write_page_info(self, page_info):
        """Writes into page_infos.

        This method will add an ArthurDocumentPageInfo instance into self._page_infos
        if given `page_info` argument has a page number (key `number`) not already exist.

        Args:
            page_info: Dictionary with keys `number`, `width`, `height`, and later probably other
                       features needed for learning.
        """
        if not self.page_number_exists(page_info.number):
            self._page_infos.append(page_info)
            self.__page_numbers.append(page_info.number)

    def page_number_exists(self, number):
        """Checks if a page_info with given number exists.
        """
        return(number in self.__page_numbers)

    def remove_page_info(self, number=None):
        """Removes a page_info.
        """
        if number is None:
            del self._page_infos[:]
            del self.__page_numbers[:]
        else:
            for idx, page_info in enumerate(self._page_infos):
                if page_info.number == number:
                    del self._page_infos[idx]
            del self.__page_numbers[number]

    def get_features(self, with_id=False, force_recreate=False):
        """Gets all stored ArthurDocumentElements as numpy array
        features for use in data analysis and machine learning.

        To get only one column of features:
        `features[:,ArthurDocument.get_feature_id('field_name')]`

        Args:
            force_recreate: Force recreates :attr:`_data` attribute.
            with_id: Defaults to False. When True, include id as first attribute's value.
                     This id can be used to get element (`self._elements[id]`).
        
        Returns:
            numpy.array: Numpy array of features
        """
        if self._data is None or force_recreate:
            self._recreate_features()
        if with_id:
            return self._data
        else:
            return np.nan_to_num(self._data[:,1:])

    def to_dict(self, raw=False, with_details=False):
        """Returns dictionary representation of this object.

        Args:
            raw(bool): If True, returns raw data as well. Defaults to False.
            with_details(bool): If True, includes detailed data like page infos,
                                elements, and data fields. Generally this should be set
                                to False when listing documents, and True for viewing
                                a document in detail. Defaults to False.

        Returns:
            dict: This object, serialized as dictionary.
        """

        obj = {
            '_id': str(self._id),
            'name': self.name,
            'num_data_fields': self.num_data_fields
        }

        raw_data = None
        if raw:
            raw_data = self.raw
            obj_add = {
                'raw': raw_data
            }
            obj.update(obj_add)

        dict_elements = None
        page_infos = None
        if with_details:
            dict_elements = []
            for element in self._elements:
                dict_elements.append(element.to_dict())
            page_infos = []
            for page_info in self._page_infos:
                page_infos.append(page_info.to_dict())

            obj_add = {
                'elements': dict_elements,
                'page_infos': page_infos
            }
            obj.update(obj_add)

        # Combine both dictionaries.
        combined = obj.copy()
        if 'project_id' in self._others:
            self._others['project_id'] = str(self._others['project_id'])
        combined.update(self._others)
        
        return combined

    def set_other_attr(self, key, value):
        self._others[key] = value

    def get_other_attr(self, key, default=None):
        """Get other attributes.

        Attr:
            key (string): Key of attribute to get.
            default: Returned value if key not found.
        """

        if key not in self._others:
            return default
        else:
            return self._others[key]

    @classmethod
    def sort_features(cls, features, sort_by_names, axis=0, **kwargs):
        """Sort features by names.

        Simply pass in list of names to sort features
        """
        ids = []
        total_names = len(cls.get_feature_names())
        # Todo: this +x thing is really ugly. Currently needed since features
        #       may include id or not, but this code could be better.
        x = 0
        if np.shape(features)[1] > total_names:
            x = np.shape(features)[1] - total_names
        for name in sort_by_names:
            idx = 'f%i' % (cls.get_feature_id(name) + x)
            ids.append(idx)
        dtype = ','.join(['f4']*total_names)
        features.view(dtype).sort(order=ids, axis=axis, **kwargs)
        return features

    @classmethod
    def get_feature_names(cls):
        """Static function to return all feature names.

        This is a convenience method to get the sorted keys from
        :func:`get_default_features`. This is how the features in :func:`get_features`
        are sorted by.

        Returns:
            list: List of (sorted) feature names.
        """
        return sorted(cls.get_default_features())

    @classmethod
    def get_feature_id(cls, feature_name):
        """Get feature id given name.

        Shorthand method for `ArthurDocument.get_feature_names().index(feature_name)`.
        """
        return ArthurDocument.get_feature_names().index(feature_name)

    @classmethod
    def get_default_features(cls):
        """Static function to return default features.

        This function returns an unsorted dictionary, don't use this to export
        directly to numpy array, instead run :func:`sorted` on its key prior to
        do so.

        To get sorted names used in :func:`get_features`, use :func:`get_feature_names`.

        Returns:
            dict: A dict object of default features.
        """

        return {
            'x': 0.,
            'y': 0.,
            'x1': 0.,
            'y1': 0.,
            'img_width': -1.,
            'img_height': -1.,
            'textbox_id': -1,
            'textline_id': -1,
            'page': 0,
            'size': 10
        }

    # @classmethod
    # def get_feature_dtypes(cls):
    #     types = {
    #         'x': float,
    #         'y': float,
    #         'x1': float,
    #         'y1': float,
    #         'img_width': float,
    #         'img_height': float,
    #         'textbox_id': int,
    #         'textline_id': int,
    #         'page': int,
    #         'size': float
    #     }
    #     dtypes = []
    #     for f in cls.get_feature_names():
    #         dtypes.append((f, types[f]))
    #     return dtypes

    def get_text(self, features):
        """Returns text from given features.

        Args:
            features: Numpy array of features.

        Returns:
            string: A string containing reconstructed text from features.
        """
        text = ''
        if len(np.shape(features)) == 1:
            features = [features]

        last_y = None
        for f in features:
            rows = self._data[np.where(
                # The following combines 3 where conditions with '*'.
                # Needs +1 since _data contains id at its first column.
                (self._data[:,ArthurDocument.get_feature_id('x')+1] == f[ArthurDocument.get_feature_id('x')]) * 
                (self._data[:,ArthurDocument.get_feature_id('y')+1] == f[ArthurDocument.get_feature_id('y')]) *
                (self._data[:,ArthurDocument.get_feature_id('page')+1] == f[ArthurDocument.get_feature_id('page')])
            )]
            for r in rows:
                y = r[ArthurDocument.get_feature_id('y')+1]
                if last_y != y and last_y is not None:
                    # Todo: Move this to reader.correct_block().
                    text += ' '
                last_y = y
                text += self._elements[int(r[0])].text
        return text

    def _recreate_features(self):
        """Recreate :self._data: from :self._elements:.

        No need to return anything since this is a protected method.

        Note: This will create a numpy array with first column being id. This id is used to get
              characters in :func:`get_text` method. Numeric id instead of char is used here to
              avoid numpy behavior that converts all values into string when one value turned into string.
        """

        self._data = np.zeros([len(self._elements), len(ArthurDocument.get_feature_names())+1])
        for i, val in enumerate(self._elements):
            self._data[i,0] = i
            for j, k in enumerate(ArthurDocument.get_feature_names()):
                self._data[i, j+1] = val.features[k]
        self._data = np.nan_to_num(self._data)

class ArthurDocumentPageInfo(namedtuple('ArthurDocumentPageInfo', ['number', 'width', 'height'])):
    """A single page information object.
    
    Information contained in this page is useful to restructure the document in UI.

    Attr:
        number: Page number.
        width: Width of this page.
        height: Height of this page.
    """
    def to_dict(self):
        """Returns dictionary representation of this object.
        """
        obj = {
            'number': self.number,
            'width': self.width,
            'height': self.height
        }
        return obj



class ArthurDocumentElement(namedtuple('ArthurDocumentElement', ['text', 'features'])):
    """Represents the smallest unit in an Arthur document.

    Smallest unit could either be an image or a character. In this case we only work with
    texts.

    Attr:
        text: Character contained in this element.
        features: Other features this element may have (see :func:`ArthurPDFConverter.write` and 
                  :func:`ArthurPDFConverter.receive_layout` for places to edit these).
    """
    def to_dict(self):
        """Returns dictionary representation of this object.
        """
        obj = {
            'text': self.text,
            'features': self.features
        }
        return obj

    def __new__(cls, text, features=None):
        """Initializes ArthurDocumentElement with default features.

        Args:
            text: String to keep (usually a character).
            features: Dict of features to keep.
        """
        default_features = ArthurDocument.get_default_features()
        if features is not None:
            default_features.update(features)
        # This looks weird but this is actually how to override immutable objects like namedtuple.
        return super(cls, cls).__new__(cls, text, default_features)

if __name__ == '__main__':
    import doctest
    import os, sys, inspect
    import pdb
    # This needs to be included here to ensure path loaded from arthur library directory.
    base_path = os.path.realpath(
        os.path.abspath(
            os.path.join(
                os.path.split(
                    inspect.getfile(
                        inspect.currentframe()
                    )
                )[0],
                '..'
            )
        )
    )
    doctest.testmod()