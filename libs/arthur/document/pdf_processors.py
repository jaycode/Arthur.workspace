"""A module containing all pdf processors required for ArthurDocument.
"""

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFConverter
from pdfminer.pdfpage import PDFPage

from pdfminer.layout import LTPage, LTContainer, LTAnno
from pdfminer.layout import LTImage, LTChar
from pdfminer.layout import LTTextBox

from pdfminer.image import ImageWriter

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def process_pdf(outfp, text):
    """Process PDF document.

    Args:
        outfp: Basically an object that has `write` method, like ArthurDocument or sys.stdout.
    """

    rsrcmgr = PDFResourceManager(caching=True)
    codec = 'utf-8'
    imagewriter = ImageWriter('images')

    laparams = LAParams()
    device = ArthurPDFConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                                imagewriter=imagewriter)
    interpreter = ArthurPDFPageInterpreter(rsrcmgr, device)
    interpreter.debug = False

    pagenos = set()
    text_io = StringIO(text)

    max_width = ArthurPDFPage.get_max_width(text_io, pagenos)

    for page in ArthurPDFPage.get_pages(text_io, pagenos):
        interpreter.process_page(page, max_width)
    device.close()


class ArthurPDFPage(PDFPage):
    @classmethod
    def get_max_width(cls, text_io, pagenos = None):
        max_width = 0
        for page in cls.get_pages(text_io, pagenos):
            (x0, y0, x1, y1) = page.mediabox
            width = x1 - x0
            if width > max_width:
                max_width = width
        return max_width

class ArthurPDFPageInterpreter(PDFPageInterpreter):
    def process_page(self, page, max_width):
        """Adds max_width to page processing method.
        """
        if 1 <= self.debug:
            print >>sys.stderr, 'Processing page: %r' % page
        (x0, y0, x1, y1) = page.mediabox
        if page.rotate == 90:
            ctm = (0, -1, 1, 0, -y0, x1)
        elif page.rotate == 180:
            ctm = (-1, 0, 0, -1, x1, y1)
        elif page.rotate == 270:
            ctm = (0, 1, -1, 0, y1, -x0)
        else:
            ctm = (1, 0, 0, 1, -x0, -y0)
        self.device.begin_page(page, ctm)
        self.render_contents(page.resources, page.contents, ctm=ctm)
        self.device.end_page(page, max_width)
        return

class ArthurPDFConverter(PDFConverter):
    """Write pdf into Arthur documents. This is useful to get the words as features.

    If stdout is given as outfp, should show features of characters gathered:
    - char
    - x
    - y
    - textbox_id

    >>> outfp = sys.stdout
    >>> imagewriter = ImageWriter('images')
    >>> rsrcmgr = PDFResourceManager(caching=True)
    >>> laparams = LAParams()
    >>> device = ArthurPDFConverter(rsrcmgr, outfp, laparams=laparams, imagewriter=imagewriter)
    >>> interpreter = ArthurPDFPageInterpreter(rsrcmgr, device)

    >>> pagenos = set()
    >>> pdf_path = base_path + '/test/test.pdf'
    >>> f = open(pdf_path, 'rb')
    >>> text = f.read()

    When get_pages is run, :func:`ArthurPDFConverter.receive_layout` is executed for each element.
    >>> text_io = StringIO(text)
    >>> max_width = ArthurPDFPage.get_max_width(text_io, pagenos)
    >>> pages = PDFPage.get_pages(text_io, pagenos)
    >>> page = pages.next()

    By doing the above preparation, when we process the page,
    we get each character with their features. We will then use these features
    in a Supervised Learning algorithm to let Arthur finds out how to group the information.

    >>> interpreter.process_page(page, max_width) # doctest:+ELLIPSIS
    <BLANKLINE>
    "3" x: 53.999978, y: 13.020312, x1: 59.999976, y1: 23.928307, img_width: -1.000000, img_height: -1.000000, textbox_id: 0, textline_id: 0, page: 1
    ...

    >>> page = pages.next()
    >>> interpreter.process_page(page, max_width) # doctest:+ELLIPSIS
    <BLANKLINE>
    "3" x: 53.999978, y: 805.020312, x1: 59.999976, y1: 815.928307, img_width: -1.000000, img_height: -1.000000, textbox_id: 0, textline_id: 0, page: 2
    ...

    """
    current_value = ''

    def end_page(self, page, max_width):
        """Adds max_width to the original method.
        """
        assert not self._stack
        assert isinstance(self.cur_item, LTPage)
        if self.laparams is not None:
            self.cur_item.analyze(self.laparams)
        self.pageno += 1
        self.receive_layout(self.cur_item, max_width)
        return

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None,
                 showpageno=False, imagewriter=None):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno, laparams=laparams)
        self.showpageno = showpageno
        self.imagewriter = imagewriter
        self.current_total_height = 0
        return

    def write(self, element=None, page_info=None):
        """Write into ArthurDocument

        If outfp is ArthurDocumentElement, pass coordinates as parameters, otherwise pass
        them as text, so we can inspect in other output buffers.

        Args:
            element: ArthurDocumentElement instance containing text and features.
            page_info: ArthurDocumentPageInfo instance containing page information. Will only be added to 
                       document's page_infos when page number does not already exist.
        """

        from document import ArthurDocumentPageInfo, ArthurDocumentElement

        # Somehow isinstance(self.outfp, ArthurDocument) is not working here, maybe caused by dynamic import.
        if type(self.outfp).__name__ == 'ArthurDocument':
            if isinstance(element, ArthurDocumentElement):
                self.outfp.write(element)
            if isinstance(page_info, ArthurDocumentPageInfo):
                self.outfp.write_page_info(page_info) 
        else:
            if element is not None:
                if isinstance(element, str):
                    self.outfp.write(element)
                elif element.features is None:
                    self.outfp.write(element.text)
                else:
                    self.outfp.write("\"%s\" x: %f, y: %f, x1: %f, y1: %f, img_width: %f, "
                                     "img_height: %f, textbox_id: %i, textline_id: %i, page: %i\n" %
                                     (
                                         element.text,
                                         element.features['x'],
                                         element.features['y'],
                                         element.features['x1'],
                                         element.features['y1'],
                                         element.features['img_width'],
                                         element.features['img_height'],
                                         element.features['textbox_id'],
                                         element.features['textline_id'],
                                         element.features['page']
                                     )
                                    )
        return

    def receive_layout(self, ltpage, max_width):
        """Stuff to do when layout received.

        Inherited from :class:`pdfminer.converter.PDFConverter`.

        Args:
            ltpage: :class:`pdfminer.layout.LTPage` object.
            max_width: numeric, Max width of all pages.
        """
        def render(item, page, page_width, max_width, current_total_height):
            """What to do when rendering certain :class:`pdfminer.layout.LT.*` objects.
            
            item.bbox has a set of (x0, y0, x1, y1)
            which we will store as part of our features.

            Important notes on features:
            - In pdf, (0,0) coordinate is positioned at bottom left, and each page has its own
              coordinates. To make it easier for learning and users to label, we combine all the
              pages into one huge, continuous plane, with position (0,0) on top left. This way
              users don't have to specify page number to create blocks, and learner can learn contents
              that span across multiple pages i.e. large paragraph of texts.

            Facts about LTTextBox:
            - It contains list of texts contained in LTTextLine... object,
              instead of single characters. Values of texts can be gathered with
              object.current_value. LTTextLine... contains LTChar.
            - LTTextLineHorizontal, LTTextLineVertical, or any child of LTTextBox does
              not have index, but we create our own index on the go (textline_id), so later
              we can trace back which LTText does an LTChar belong to.
            - LTTextBox does not seem to contain another LTTextBox, nor does it
              contain characters directly (at least in the examples so far).
            - Index can be gained from property `index` e.g. `item.index` (we will
              think about how to get this element from index later).

            Facts about LTImage:
            - object.srcsize are different from width and height calculated from bbox.
            - Belongs to no textbox.
            """
            from document import ArthurDocumentPageInfo, ArthurDocumentElement
            if isinstance(item, LTPage):
                page = ltpage.pageid
                page_info = ArthurDocumentPageInfo(
                    number=page,
                    height=item.height,
                    width=item.width
                )
                self.write(page_info=page_info)                
            if isinstance(item, LTContainer):
                for child in item:
                    render(child, page, page_width, max_width, current_total_height)
            elif isinstance(item, LTAnno):
                self.write(item.get_text().encode(self.codec, 'ignore')) # important to avoid unicode error.
            if isinstance(item, LTTextBox):
                for textline_id, textline in enumerate(item):
                    for char in textline:
                        if isinstance(char, LTChar):
                            x = (max_width/2 - page_width/2) + char.bbox[0]
                            y = current_total_height - char.bbox[1]
                            chartext = char.get_text().encode(self.codec, 'ignore')
                            element = ArthurDocumentElement(chartext,
                                {
                                    'x': x,
                                    'y': y,
                                    'x1': x + char.bbox[2] - char.bbox[0],
                                    'y1': y + char.bbox[3] - char.bbox[1],
                                    'textbox_id': int(item.index),
                                    'textline_id': textline_id,
                                    'page': page,
                                    'size': char.size
                                }
                            )
                            self.write(element)
                        elif isinstance(char, LTAnno):
                            self.write(item.get_text().encode(self.codec, 'ignore'))
                            pass
            elif isinstance(item, LTImage):
                x = (max_width/2 - page_width/2) + item.bbox[0]
                y = current_total_height - item.bbox[1]
                element = ArthurDocumentElement(item.name+'<image>',
                    {
                        'x': x,
                        'y': y,
                        'x1': x + item.bbox[2] - item.bbox[0],
                        'y1': y + item.bbox[3] - item.bbox[1],
                        'img_width': item.srcsize[0],
                        'img_height': item.srcsize[1],
                        'page': page
                    }
                )
                self.write(element)

                if self.imagewriter is not None:
                    self.imagewriter.export_image(item)

        self.current_total_height += ltpage.height
        render(ltpage, ltpage.pageid, ltpage.width, max_width, self.current_total_height)
        return

    def render_image(self, name, stream):
        """
        Some dummy functions to save memory/CPU when all that is wanted
        is text.  This stops all the image and drawing output from being
        recorded and taking up RAM.
        """
        if self.imagewriter is None:
            return
        PDFConverter.render_image(self, name, stream)
        return

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
