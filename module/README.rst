etunexus
========

Etunexus is an GPL-licensed SDK encapsulating the API to interact with
`etunexus online service <https://www.etunexus.com/>`__.

It supports API of Etu Management Center (EMC) v2, Etu Recommender (ER)
v3, and Etu Insight (EI) v3.

Features
--------

-  Simplify the single-signon process with a simple login() call.
-  Encapsulate the protocol detail into easy-of-use objects, but still
   keep the flexibility for adjustment.

Quick start
-----------

Etuneuxs online service provides a rich and full-featured API entries
for every client supporting RESTful programming model to manipulate the
data and settings. It also provides a single-sign-on (SSO) service that
multiple applications can share the same user login authentication.

However, for a Python programmer, it is still complicated to code the
SSO process with involving two stages communication between SSO server
and application server from the ground. The SDK wraps it as a simple
login() call as:

.. code-block:: pycon

    >>> from etunexus.cas import *
    >>> from etunexus.emc import *
    >>>
    >>> cas = CAS([user_group], [user_name], [password])
    >>> # It is optional to make SSO login first.
    >>> cas.login()
    >>>
    >>> # Login application
    >>> emc2 = EMC2(cas)
    >>> emc2.login()

The subsequent API call is also trivial with the methods of the
application object. For example, it is easy to get the group list and
the user list in a group (of course, for an authorized account only)
with:

.. code-block:: pycon

    >>> # Get all groups, and then find a specific group.
    >>> groups=emc2.get_groups()
    >>> workshop_group = filter(lambda x: x['name']=='workshop', groups)[0]
    >>>
    >>> # Get all users, and then find a specific user
    >>> workshop_users = emc2.get_users(workshop_group)
    >>> workshop_user = filter(lambda x: x['name']=='workshop_user', workshop_users)[0]

It is worthy noticed that the data returned are wrapped into
objects/classes:

.. code-block:: pycon

    >>> type(workshop_group)
    <class 'etunexus.emc.Group'>
    >>> type(workshop_user)
    <class 'etunexus.emc.User'>

To manipulate the data, for example, add a user to the group. First,
create an object as the data with the constructor already properly
designed:

.. code-block:: pycon

    >>> new_user=User('new_workshop_user', 'New workshop user', 'password')
    >>> emc2.add_user(workshop_group, new_user)

And, it is easy to update the data with:

.. code-block:: pycon

    >>> update_user = filter(lambda x: x['name']=='new_workshop_user', workshop_users)[0]
    >>>
    >>> from etunexus.enum import *
    >>> update_user['roles']=[UserRole(AppRoleName.VIEWER, AppId.ER), UserRole(AppRoleName.VIEWER, AppId.EI)]
    >>>
    >>> emc2.update_user(update_user)

Similar programming model for other applications (ER and EI). Please
refer to pydoc for detail. There are also samples in `GitHub
repository <https://github.com/etusolution/etunexus_api.git>`__.

Installation
------------

Etunexus is in PyPI. It can be installed easily directly with:

.. code-block:: bash

    $ pip install etunexus

Or, from Github:

.. code-block:: bash

    $ git clone https://github.com/etusolution/etunexus_api.git
    $ cd etunexus_api/module
    $ python setup.py install

Documents generation
--------------------

After installed the SDK, the document of modules can be viewed with
following:

.. code-block:: bash

    $ pydoc etunexus.emc
    $ pydoc etunexus.er
    $ pydoc etunexus.ei
    $ pydoc etunexus.enum

Or, you can generate the HTML edition with "pydoc -w". For example,
following line generate an etunexus.emc.html.

.. code-block:: bash

    $ pydoc -w etunexus.emc

Resources
---------

-  `GitHub
   repository <https://github.com/etusolution/etunexus_api.git>`__