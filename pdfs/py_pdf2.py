from colorama import Fore, Style
from pathlib import Path
import random
import sys
import PyPDF2
from PyPDF2.generic import DictionaryObject, NameObject, ArrayObject, StreamObject, NumberObject, TextStringObject
#form PyPDF2 import Ue

"""
Not supported: AnnotRichMedia, Annot3D, Catalog
Catalog: The Catalog plug-in (and the catalog object) is available only in Acrobat Pro.
"""

def print_debug(data):
    print(f"{Fore.GREEN}[DEBUG] {data} {Style.RESET_ALL}")

def print_error(data):
    print(f"{Fore.RED}[ERROR] {data} {Style.RESET_ALL}")

def print_warning(data):
    print(f"{Fore.MAGENTA}[WARNING] {data} {Style.RESET_ALL}")

def print_info(data):
    print(f"{Fore.CYAN}[INFO] {data} {Style.RESET_ALL}")

def is_file(filename: Path):
    """ Check if file is present and type of  `filename` is file
    """
    if not isinstance(type(filename), Path):
        filename = Path(filename)
    
    # check `filename` exists
    if not filename.exists():
        print_error(f"{filename} doesn't exists")
        return False
    
    # check if `filename` is a file
    if not filename.is_file():
        print_error(f"{filename} is not a file")
        return False
    
    return True

### Copy pasted: https://github.com/c0ll3cti0n/exploitpack/blob/46bdf121a0e22473690417a823b6fc757cef7f34/exploits/code/Adobe-Acrobat-and-Reader.py
class PDF:
      
    def __init__(self):
        self.xrefs = []
        self.eol = '\x0a'
        self.content = ''
        self.xrefs_offset = 0
         
    def header(self):
        self.content += '%PDF-1.6' + self.eol
         
    def obj(self, obj_num, data,flag):
        self.xrefs.append(len(self.content))
        self.content += '%d 0 obj' % obj_num
        if flag == 1:
            self.content += self.eol + '<< ' + data + ' >>' + self.eol
        else:
            self.content += self.eol + data + self.eol
        self.content += 'endobj' + self.eol
 
    def obj_SWFStream(self, obj_num, data, stream):
        self.xrefs.append(len(self.content))
        self.content += '%d 0 obj' % obj_num
        self.content += self.eol + '<< ' + data + '/Params << /Size %d >> /DL %d /Length %d' %(len(stream),len(stream),len(stream))
        self.content += ' >>' + self.eol
        self.content += 'stream' + self.eol + stream + self.eol + 'endstream' + self.eol
        self.content += 'endobj' + self.eol
     
    def obj_Stream(self, obj_num, data, stream):
        self.xrefs.append(len(self.content))
        self.content += '%d 0 obj' % obj_num
        self.content += self.eol + '<< ' + data + '/Length %d' %len(stream)
        self.content += ' >>' + self.eol
        self.content += 'stream' + self.eol + stream + self.eol + 'endstream' + self.eol
        self.content += 'endobj' + self.eol
         
    def ref(self, ref_num):
        return '%d 0 R' % ref_num
         
    def xref(self):
        self.xrefs_offset = len(self.content)
        self.content += 'xref' + self.eol
        self.content += '0 %d' % (len(self.xrefs) + 1)
        self.content += self.eol
        self.content += '0000000000 65535 f' + self.eol
        for i in self.xrefs:
            self.content += '%010d 00000 n' % i
            self.content += self.eol
     
    def trailer(self):
        self.content += 'trailer' + self.eol
        self.content += '<< /Size %d' % (len(self.xrefs) + 1)
        self.content += ' /Root ' + self.ref(1) + ' >> ' + self.eol
        self.content += 'startxref' + self.eol
        self.content += '%d' % self.xrefs_offset
        self.content += self.eol
        self.content += '%%EOF'
         
    def generate(self):
        return self.content


class py_pdf2():
    def __init__(self, infile, outfile=None):
        self.blank = False
        self.infile =  infile if self.file_exists(infile) else self._blank_pdf(infile)
        self.reader = PyPDF2.PdfReader(self.infile)

        # add `MediaBox`
        if self.blank:
            self.pdf_initialize()

        self.outfile = outfile if outfile else self.infile

        self.writer = PyPDF2.PdfWriter()


    def file_exists(self, filename):
        """ check `filename` exists
        """
        if not Path(filename).exists():
            return False
        else:
            return True

    def _blank_pdf(self, filename):
        """ if pdf foesn't exist, create a pdf contains a blank page
        """
        #check the flag
        self.blank=True
        writer = PyPDF2.PdfWriter()

        writer.add_blank_page(200,300)

        with open(filename, "wb") as fp:
            writer.write(fp)

        print_info(f"created a blank file: {filename}")
        return filename
    
    def pdf_initialize(self):
        """ add `MediaBox`, Annots
        """
        page = self.reader.pages[0]

        page[NameObject("/MediaBox")] = ArrayObject((NumberObject(0),NumberObject(0),NumberObject(600),NumberObject(800)))
        page[NameObject('/Annots')] = ArrayObject([DictionaryObject()])

    def get_random_page(self):
        """ return a random page from the reader
        """
        return random.choices(self.reader.pages)
       

    def add_rich_media(self, page=None, buffer=b"\xFF\XFE\FDAAAAAAAAAAAAA", swffilename="filename.txt", x1=random.randrange(0,100),y1=random.randrange(100,200),x2=random.randrange(100,200),y2=random.randrange(200,300)):
       """copy pasted from here:
            https://github.com/berez23/canvas/blob/cb306a9d8b1d8a743049a29164e6d324f8dabbfa/exploits/clientside/windows/acrobat_flash/acrobat_flash.py#L182
       """
       page = page if page else self.reader.pages[0]
       annot=DictionaryObject()
       appearance=DictionaryObject()
       appearance[NameObject("/Subtype")]=NameObject("/Form")
       appearance[NameObject("/Matrix")]=ArrayObject([NumberObject("1"), NumberObject("0"), NumberObject("0"), NumberObject("1"), NumberObject("0"), NumberObject("0")])
       appearance[NameObject("/BBox")]=ArrayObject([NumberObject("0"), NumberObject("0"), NumberObject("30"), NumberObject("30")])
       annot[NameObject('/Type')]=NameObject("/Annot")
       annot[NameObject('/Subtype')]=NameObject("/RichMedia")
       annot[NameObject('/NM')]=TextStringObject(swffilename)
       annot[NameObject('/AP')]=DictionaryObject( { NameObject("/N") : appearance } )
       annot[NameObject('/F')]=NumberObject(68)
       annot[NameObject('/Rect')]=ArrayObject([NumberObject(x1), NumberObject(y1), NumberObject(x2), NumberObject(y2)])
       data=StreamObject()
       data._data=buffer
       data[NameObject("/DL")]=NumberObject(len(buffer))
       data[NameObject("/Params")]=DictionaryObject( { NameObject("/Size"):NumberObject(len(buffer)) } )
       filespec=DictionaryObject( { NameObject("/Type"):NameObject("/Filespec"), \
                                    NameObject("/F"):TextStringObject(swffilename), \
                                    NameObject("/UF"):TextStringObject(swffilename), \
                                    NameObject("/EF"):DictionaryObject( { NameObject("/F"):data } ) } )
       #config the player
       config = DictionaryObject()
       config[NameObject("/Type")]=NameObject("/RichMediaConfiguration")
       config[NameObject("/Subtype")]=NameObject("/Flash")
       config[NameObject("/Instances")]=ArrayObject()
       instance=DictionaryObject()
       instance[NameObject("/Params")]=DictionaryObject( { NameObject("/Binding"):TextStringObject("Background") } )
       instance[NameObject("/Asset")]=filespec
       config["/Instances"].append(instance)
       #activate as soon as any part of the page that contains the annotation becomes visible, deactivate at user request
       activation = DictionaryObject( { NameObject("/Condition") : NameObject("/PO"),\
                                        NameObject("/Type") : NameObject("/RichMediaActivation"),\
                                        NameObject("/Configuration") : config } )
       deactivation = DictionaryObject( { NameObject("/Condition") : NameObject("/PC"),\
                                          NameObject("/Type") : NameObject("/RichMediaDeactivation") } )
       annot[NameObject('/RichMediaSettings')]=DictionaryObject( { NameObject("/Activation"):activation,\
                                                                              NameObject("/Deactivation"):deactivation,\
                                                                                         NameObject("/Configuration"):config } )
       annot[NameObject('/RichMediaContent')]=DictionaryObject( { NameObject("/Configurations"):ArrayObject( [ config ] ),\
                                                                  NameObject("/Assets"):\
                                                                  DictionaryObject( { \
                                                                      NameObject("/Names"):\
                                                                      ArrayObject( [ TextStringObject(swffilename), filespec ] ) \
                                                                  } ) } )
       print_info(annot)
       page['/Annots'].append(annot)
       return True
    
    def add_u3d_annot(self, u3dStr=b"\xFF\xFFu3dStr", page=None):
        """https://github.com/berez23/canvas/blob/cb306a9d8b1d8a743049a29164e6d324f8dabbfa/exploits/clientside/windows/acrobat_u3d_mesh/acrobat_u3d_mesh.py#L321
        """
        page = page if page else self.reader.pages[0]

        appearance=DictionaryObject()
        appearance[NameObject("/Subtype")]=NameObject("/Form")
        appearance[NameObject("/Matrix")]=ArrayObject([NumberObject("1"), NumberObject("0"), NumberObject("0"), NumberObject("1"), NumberObject("0"), NumberObject("0")])
        appearance[NameObject("/BBox")]=ArrayObject([NumberObject("0"), NumberObject("0"), NumberObject("800"), NumberObject("600")])

        page[NameObject('/Annots')]=ArrayObject([DictionaryObject()])
        annot = DictionaryObject()
        annot[NameObject('/Subtype')] = NameObject("/3D")
        annot[NameObject('/F')]       = NumberObject(68)
        annot[NameObject('/Rect')]    = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(800), NumberObject(600)])
        annot[NameObject('/Type')]    = NameObject("/Annot")
        annot[NameObject('/AP')]      = DictionaryObject( { NameObject("/N") : appearance } )

        data=StreamObject()
        data._data=u3dStr
        annot[NameObject('/3DD')]=data.flate_encode()
        annot['/3DD'][NameObject('/Type')]=NameObject("/3D")
        annot['/3DD'][NameObject('/Subtype')]=NameObject("/U3D")    
        annot[NameObject('/3DA')]=DictionaryObject( { NameObject("/DIS"):NameObject("/I"), NameObject("/A"):NameObject("/PO"), NameObject("/D"):NameObject("/XD") } )


        page['/Annots'].append(annot)

    def add_object(self):
        pageobj = self.reader.get_object(1)
        print_debug(f"pageobj= {pageobj}")

        xref = self.reader.xref

        print(self.reader.xref)
    
    def save(self):
        """ save reader pages to writer and write to `self.outfile`
        """
        for page in self.reader.pages:
            self.writer.add_page(page)
            
        with open(self.outfile, "wb") as fp:
            self.writer.write_stream(fp)
            print_info(f"Created the file: {self.outfile}")


def main(filename: Path):
    print_info(f"use filename that doesn't exists.It may overwrite the file ({filename}).")
    # create `pdfobj` object
    # `filename` should not exists
    pdfobj = py_pdf2(filename)

    #u3d_bytes = Path("./sample.u3d").read_bytes()
    #pdfobj.add_u3d_annot(u3d_bytes)
    pdfobj.add_rich_media()
    #pdfobj.add_object()

    # save the file
    pdfobj.save()
    print_info(f"Created the file: {pdfobj.outfile}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_error("[-] Incorrect usage")
        print_error(f"[-] {__file__} pdf_file_name")
        exit(1)
    main(Path(sys.argv[1]))
