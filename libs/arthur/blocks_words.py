"""
Classes to extract and write features from multiple documents.
"""

from learnable import Learnable

class ArthurBlocks(Learnable):
    """Class to manage blocks.

    Extract block features from a document.
    >>> features = blocks_manager.extract_features(document)

    Save extracted features.
    >>> blocks_manager.append_features(features)

    Get features of blocks
    >>> blocks_manager.get_features

    Get features of one document (convenience method, you could 
    also get this by doing np.which to result of :func:`get_features()`).
    >>> blocks_manager.get_features(doc_name='348418.pdf')

    Labeling a block.
    >>> blocks_manager.apply_label(doc_name, block_id, concept_id)
    """
    def extract_features(self, document=None):
        """Method to extract block features from a document.
        """
        features = document.get_features()
        return features

    def count_labels(self, doc_name=None):
        """Counts labeled blocks or words.

        Args:
            doc_name: Document name. If None, count all labeled blocks and words from all documents.
            type: 0 for blocks, 1 for words.
        """
        return 0


class ArthurWords(Learnable):
    def extract_features(self, document=None):
        """Method to extract word features from a document.
        """
        features = document.get_features()
        return features

    def count_labels(self, doc_name=None):
        """Counts labeled blocks or words.

        Args:
            doc_name: Document name. If None, count all labeled blocks and words from all documents.
            type: 0 for blocks, 1 for words.
        """
        return 0
