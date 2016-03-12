"""Module containing Learnable class.
"""
import numpy as np

class Learnable():
    """Inheritable class to add features and targets to another class.

    These features and targets may then be extracted and used in learning algorithms.

    Starting from empty features then builds up from there.
    >>> object = HasFeatures([], {
            'feature1': {'type': str, 'default': 0.0, 'is_detail': True},
            'feature2': {'type': float, 'default': 0, 'is_detail': False},
            'feature3': {'type': int, 'default': 0, 'is_detail': False},
            'feature4': {'type': int, 'default': 0, 'is_detail': True},
            'target1': {'type': float, 'default': None, 'is_target': True},
            'target2': {'type': float, 'default': None, 'is_target': True}
        })
    >>> print(object.get_feature_names(with_details=True))
    ['feature1', 'feature4', 'feature2', 'feature3']

    Append features by passing in numpy array. Note that the ordering needs to match
    :func:`get_feature_names`.
    >>> features = [
    >>>     ['id_1', 1, 0.2893, 12],
    >>>     ['id_2', 2, 0.2293, 30],
    >>>     ['id_3', 3, 0.1427, 19],
    >>>     ['id_4', 4, 0.3001, 14]
    >>> ]
    >>> features_np = np.array(features)
    >>> object.append_features(features_np)

    Making sure the features are properly entered.
    >>> features = object.get_features()
    >>> print(features)
    [[0.2893, 12], [0.2293, 30], ...]

    Now we want to manually label some of the data. In reality (at least in Arthur's case),
    this will happen iteratively as each concept is being processed.
    >>> object.apply_label()

    Args:
        __data: Numpy array of features + targets.
                To get these features, use method :func:`get_block_features`.
                To check if a document / block / word is labeled, use method
                :func:`has_label`. Non-existant targets are denoted with the value None.
    """

    __data = None
    __field_details = {}

    def __init__(self, data=[], field_details = {}):
        """Initializes object.

        Args:
            data(list|numpy.array): Initial features to store. Remember to store the complete details, including
                                    informational data like doc_name or block_id (i.e. not directly used in learning
                                    algorithm).
        """
        self.__data = np.array(data)
        self.__field_details = field_details


    def get_feature_id():
        """Get feature id given name.

        Shorthand method for `ArthurDocument.get_feature_names().index(feature_name)`.
        """
        return ArthurDocument.get_feature_names().index(feature_name)

    def get_feature_names(self, with_details=False):
        """Returns all feature names.

        Alias for :func:`get_field_names(features_only=True)`.
        """
        return self.get_field_names(with_details=with_details, features_only=True)

    def get_field_names(self, with_details=False, features_only=False):
        """Returns all field names.

        Convenience method to get the sorted keys from
        :func:`_field_details`. This is how the features in :func:`get_features`
        are sorted by.

        Proof of concept:
        >>> dic = {'c': {'top': False}, 'a': {'top': False}, 'b': {'top': True}}

        We want to order first by 'top' then key:
        >>> sorted(dic.items(), key=lambda d: (-d[1]['top'], d[0]))
        [('b', {'top': True}), ('a', {'top': False}), ('c', {'top': False})]

        Args:
            with_details(bool): When True, include features with `is_detail == True`.
                                Defaults to False. 

        Returns:
            list: List of (sorted) feature names.
        """
        if features_only:
            field_details = filter(lambda d: 'is_target' not in d[1] or -d[1]['is_target'], self.get_field_details().items())
        else:
            field_details = self.get_field_details().items()

        if with_details:
            sorted_details = sorted(field_details, key=lambda d: ('is_detail' not in d[1] or -d[1]['is_detail'], d[0]))
        else:
            filtered = filter(lambda d: d[1]['is_detail']==False, field_details)
            sorted_details = sorted(filtered, key=lambda d: ('is_detail' not in d[1] or -d[1]['is_detail'], d[0]))
        return map(lambda d: d[0], sorted_details)

    def get_field_details(self):
        """Details of fields used by data.

        Returns:
            dict: A dictionary of all field details:
                  `{'field_name': {'type': float, 'default': 0.0, 'is_detail': False, 'is_target': False}}`
                  in here, when `is_detail` or `is_target` is True (`is_detail` MUST be specified unless `is_target` exists),
                  it is not included when getting features for learning with :func:`get_features()` method.
        """
        return self.__field_details

    def set_field_details(self, key_or_data, data=None):
        """Setting field details with given dict
        """
        if data is None:
            self.__field_details = key_or_data
        else:
            self.__field_details[key] = data

    def get_feature_dtypes():
        """Override this
        """
        return {}
    
    def get_data(self, doc_name=None, with_details=False, features_only=False):
        """Gets all stored features for use in learning or display.

        Args:
            with_details: By default, features can be used directly for learning. However, should developer needs
                          to get reference to other details (e.g. doc_name and block_id), this option can be
                          set to True.
        """
        if with_details:
            return self.__data
        else:
            return self.__data

    def append_data(self, data):
        """Append more records to stored data.
        """
        pass

    def to_dict(self):
        """Convert stored data to dictionary.
        """
        return {
            'field_names': self.get_field_names(with_details=True, features_only=False),
            'data': list(self.get_data(with_details=True, features_only=False))
        }

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
                )[0]

            )
        )
    )
    doctest.testmod()