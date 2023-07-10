### pymupdf tutorial

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
