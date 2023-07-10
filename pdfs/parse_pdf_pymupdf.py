from colorama import Fore, Style
from pathlib import Path
import fitz
import sys

"""
documents method: https://pymupdf.readthedocs.io/en/latest/document.html#Document.pages

Document.xref_get_keys() returns the PDF keys of the object at `xref`  to get the value of key `MediaBox` => ` doc.xref_get_key(page.xref, "MediaBox")`


"""
def print_debug(data):
    print(f"{Fore.GREEN}[DEBUG] {data} {Style.RESET_ALL}")

def print_error(data):
    print(f"{Fore.MAGENTA}[Error] {data} {Style.RESET_ALL}")

def print_info(data):
    print(f"{Fore.CYAN}[INFO] {data} {Style.RESET_ALL}")

def access_content(doc):
    """ https://pymupdf.readthedocs.io/en/latest/recipes-low-level-interfaces.html
        content objects are stream object describing what apperars
        where and how on  a page (like text and image)
    """
    print_info("in access_content")
    page_count = doc.page_count
    contents = []
    for idx in range(page_count):
        page = doc[idx]
        # extract concatenated contents
        content = page.read_contents()
        contents.append(content)
        print_info(content)
    return contents

def access_catalog(doc):
    # get object num of catalog
    print_debug("in access_catalog")
    xref_num = doc.pdf_catalog()
    catalog = doc.xref_object(xref_num)
    print_info(f"catalog={catalog}")
    return catalog

def access_file_trailer(doc):
    # access the last object
    trailer = doc.pdf_trailer()
    # or
    # trailer = doc.xref_object(-1)
    print_info(f"trailer={trailer}")
    return trailer

def access_xml_metadata(doc):
    xmlmetadata = doc.get_xml_metadata()
    print_info(f"xmlmetadata={xmlmetadata}")
    # write back modified XML metadata:
    # doc.set_xml_metadata(xmlmetadata)
    # XML metadata can be deleted like this:
    # doc.del_xml_metadata()
    return xmlmetadata

def access_link(doc):
    """ Access all links on document
    """
    links = []
    for page in doc.pages():
        for link in page.links():
            links.append(link)
        
    return links

def access_annot(doc):
    """ Access all annots on the document
    """
    annots = []
    for page in doc.pages():
        for annot  in page.annots():
            # have to save page, otherwise `annot` will get 
            # destroy after loop and will show the error: 
            # `orphaned object: parent is None`
            annots.append((annot, page))
    #print(annots)
    return annots


def access_widgets(doc):
    """ Access all widgets on the document
    """
    widgets = []
    for page in doc.pages():
        for widget  in page.widgets():
            # have to save page, otherwise `widget` will get 
            # destroy after loop and will show the error: 
            # `weakly-referenced object no longer exists`
            widgets.append((widget, page))

    return widgets
            



def parse_xref(doc):
    """ Uses xref to iterate over each object of a `doc`
    """
    # get length of object table
    xreflen = doc.xref_length()

    # object 0 is reserved and not used in pdf
    for xref in range(1, xreflen):
        # get object from `xref``
        object_data = doc.xref_object(xref, compressed=False)

        # not interested in `object_data` whne it's value is `null`
        if object_data != "null":
            print_info(f"object: {xref} (stream: {doc.xref_is_stream(xref)})")
            print_info(object_data)
            # Get `stream` if stream is present in the object
            if stream := doc.xref_stream(xref):
                print_debug(f"stream={stream}")
                # can update stream using `update_stream`
                # doc.update_stream(xref, stream)


def parse_pdf(filename):
    print_info(f"Parsing file: {filename}")

    doc = fitz.open(filename)

    # get metdata of the file
    metdata = doc.metadata 

    #parse_xref(doc)
    access_content(doc)
    access_catalog(doc)
    access_file_trailer(doc)
    links = access_link(doc)
    print_debug(f"link = {links}")

    annots = access_annot(doc)
    print_debug(f"annots = {annots}")

    widgets = access_widgets(doc)
    print_debug(f"widgets = {widgets}")


    doc.close()


def main(filename: Path):
    # check `filename` exists
    if not filename.exists():
        print_error(f"{filename} doesn't exists")
        exit(1)
    
    # check if `filename` is a file
    if not filename.is_file():
        print_error(f"{filename} is not a file")
        exit()
    
    parse_pdf(filename)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_error("Incorrect usage")
        print_error(f"{__file__} pdf_file_name")
        exit(1)
    main(Path(sys.argv[1]))
