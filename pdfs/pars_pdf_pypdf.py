from colorama import Fore, Style

from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import DictionaryObject, ArrayObject, IndirectObject, DecodedStreamObject, NameObject
import sys
import PyPDF2  

def print_debug(data):
    print(f"{Fore.GREEN} {data} {Style.RESET_ALL}")

def print_rm(data):
    print(f"{Fore.MAGENTA} {data} {Style.RESET_ALL}")

def print_info(data):
    print(f"{Fore.CYAN} {data} {Style.RESET_ALL}")


def get_annots2(filename: Path):
    print_debug("In get_annots2")

    reader = PyPDF2.PdfReader(filename)

    annot_obj = []
    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                annot_obj.append(obj)

                print_rm(f'{obj["/Subtype"]} {obj["/T"] if "/T" in obj else "None"}')

    print(len(annot_obj))
    


def get_annots(reader: PdfReader):
    print_debug("In get_annots")
    annots_array = []

    # iterate through all pages to get /Annots object
    for page in reader.pages:
        annots = page.get("/Annots")
        print_debug(f"annots: {annots}")

        if annots:
            for annot in annots:
                if isinstance(annot, IndirectObject):
                    subtype =  reader.get_object(annot.idnum).get("/Subtype")
                else:
                    subtype = annot.get("/Subtype")
                annots_array.append(subtype)
                print_rm(subtype)
    
    print_info(f"annots_array len: {len(annots_array)}")


def pdf_reader(reader: PdfReader):

    objects = {}
    # iterate through pages
    for page in reader.pages:
        print_debug(f"page contains {page}")
        for key in page:
            print(key, "==>",  page[key], "==>", page.get(key))
            if isinstance(page.get(key), IndirectObject):
                object_value = reader.get_object(page.get(key).idnum)
                print_debug(object_value)
        break
        objects.update(page)
    
    print(objects)


def main(filename: Path):
    # check `filename` exists
    if not filename.exists():
        print(f"{filename} doesn't exists")
        exit(1)
    
    # check if `filename` is a file
    if not filename.is_file():
        print(f"{filename} is not a file")
        exit()
    
    reader = PdfReader(filename)
    get_annots2(filename)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[-] Incorrect usage")
        print(f"__file__ pdf_file_name")
    main(Path(sys.argv[1]))
