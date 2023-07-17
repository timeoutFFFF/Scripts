### pymupdf tutorial


###### create a blank pdf

```python
def create_a_pdf():
    doc = fitz.open()
    # add a page to doc
    page= doc.new_page()

    output_file = "example.pdf"
    doc.save(output_file)
    doc.close()
```

###### add js object to pdf:
```python
# https://github.com/pymupdf/PyMuPDF/discussions/2157
def add_js_object(doc, js="app.alert('hello')"):
    xref = doc.get_new_xref()
    objsource = f"<</Type/Action/S/JavaScript/JS({js})>>"
    doc.update_object(xref, objsource)

    #update cataloge
    cat = doc.pdf_catalog()
    doc.xref_set_key(cat, "OpenAction", f"{xref} 0 R")
```

###### iterate through  all objects of a pdf
```python
#  doc = fitz.open(source_file)
xreflen = doc.xref_length()
for xref in range(1, xreflen):
    # get the object
    object_data = doc.xref_object(xref, compressed=False)
    if doc.xref_is_stream(xref):
        # get the stream
        stream_raw = doc.xref_stream_raw(xref)          
```

###### Update an object and a stream
```python
"""
xref_num is 56 here
56 0
obj
endob
"""
dest_doc.update_object(xref_num, updated_obj_data)
dest_doc.update_stream(xref_num, stream_data, False, compress=False) # compress set to true to compress the stream 
```
