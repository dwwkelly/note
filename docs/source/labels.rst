Labels
-------

Notes may be refered to by their ID (an integer) or a label (a text 
string without spaces).  Labels are optional, a note does not need a label.

Implementation
^^^^^^^^^^^^^^

Labels shall be implemented in in data structures separate from note structures.
For example, if the note backend is SQL then there shall be a table 'label' 
like this:

=====  =====
name   ID
=====  =====
abc     23
xyz     45
=====  =====

If the note backed is MongoDB the documements in the label collection shall 
be structured like this:

``{"name": "some_label", "ID": 23}``
