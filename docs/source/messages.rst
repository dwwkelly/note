Messages
========

Client-Server
-------------

For every Client-Server interaction the client shall send a message with only
``"object"`` and ``"type"`` as keys, ``"object"`` must point to a ``dict``
and ``"type"`` must point to a string.  For Example:

.. code-block:: javascript

    {"object": {"some": "object"},
     "type": "some type"}

The server will always reply with with a message that ``"object"``,
``"type"`` and ``"status"`` as keys, ``"object"`` must point to a ``dict``,
``"type"`` must point to a string and ``"status"`` must point to a string 
that will be either ``"OK"`` or ``"ERROR"``.

.. code-block:: javascript

    {"object": {"some": "object"},
     "type": "some type"
     "status": "some status"}


Get
^^^^

Get showing done To-Dos

.. code-block:: javascript

    {"object": {"type": "done", "done": True},
     "type": "Get"}

Get showing undone To-Dos

.. code-block:: javascript

    {"object": {"type": "done", "done": False},
     "type": "Get"}

Get by ID

.. code-block:: javascript

    {"object": {"type": "ID", "id": 1},
     "type": "Get"}

Get by Label

.. code-block:: javascript

    {"object": {"type": "label", "name": "some label"},
     "type": "Get"}

Reply - OK

.. code-block:: javascript

    {"status": "OK",
     "object": {"note": "some note",
                "ID": 1,
                "tags": ["tag1"],
                "timestamps": [1417326762.795402]},
     "type": "Get"}

Reply - ERROR

.. code-block:: javascript

    {"status": "ERROR",
     "type": "Get",
     "object": {"msg": "Item does not exist",
                "ID": 1}}



New Note
^^^^^^^^

Message to add a new note

.. code-block:: javascript

    {
     "type": "Note"
     "object": {"note": "some note",
                "tags": ["tag1", "tag2"],
                "ID": 1
               }
    }

**NOTE** The ID is optional


Reply - OK

.. code-block:: javascript

    {"status": "OK",
     "type": "Note",
     "object": {
               "received note": "some note text",
               "received tags": ["tag1", "tag2"],
               "ID": 1}
    }

Reply - Error



Delete
^^^^^^

Message to delete a note

.. code-block:: javascript

    {
     "type": "Delete"
     "object": {"ID": 1},
    }

Reply - OK

.. code-block:: javascript

    {
     "status": "OK",
     "type": "Delete",
     "object": 1
    }


Reply - Error

.. code-block:: javascript

    {
     "status": "ERROR",
     "type": "Delete",
     "object": {"msg": "Note Does not exist"}
    }


Search
^^^^^^

.. code-block:: javascript

    {
     "object": {"searchTerm": "some search query"},
     "type": "Search"
    }


Reply - OK

.. code-block:: javascript

    {"status": "OK",
     "object": {"received search": "query", 
                "results": [{"score": 1.5,
                             "obj": {"note": "some note",
                                     "tags": ["tag1"],
                                     "ID": 1,
                                     "timestamps": [1417326762.795402]},
                             "itemType": "notes"}]}
     "type": "Search"}

Reply - Error

.. code-block:: javascript

    {
     "status": "ERROR",
     "type": "search",
     "object": {"received search": "original search query",
                "results": results}
    }

Set Label
^^^^^^^^^

.. code-block:: javascript

    {"object": {"name": "some label", "id": 23},
     "type": "label"}



Server-Server
-------------
