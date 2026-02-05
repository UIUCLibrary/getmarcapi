===========
Development
===========

This section provides an overview of the development and deployment process for the project.

The application requires a configuration file in INI format. The configuration file format can be found in the
:ref:`config file section <configuration-file>`.

Build for Production
====================

.. _dockerizing:

Dockerizing the Application
---------------------------
To containerize the application using Docker, use the `Dockerfile` at the root of the project. You can build the Docker image with the following command:

.. code-block:: console

    $ docker build -t getmarcapi .


Run Locally for Development
===========================

Prerequisites
-------------
Preinstalled Development dependencies:

    * uv (manage Python e)
    * Node.js and npm (for building static assets)

.. Note::

    You should be using `uv <https://docs.astral.sh/uv/>`_ to manage your virtual environments and dependencies. These
    directions are going to assume that you have uv installed. If you do not have
    `uv` installed, you *can* use `pip` but **uv is HIGHLY RECOMMENDED**.

    `See uv installation instructions <https://docs.astral.sh/uv/getting-started/installation/>`_.

Getting Development Environment Set Up
--------------------------------------

To run the application locally for development purposes, follow these steps:

1. Clone the repository:

    .. code-block:: console

        $ git clone https://github.com/UIUCLibrary/getmarcapi.git
        Cloning into 'getmarcapi'...
        remote: Enumerating objects: 986, done.
        remote: Counting objects: 100% (364/364), done.
        remote: Compressing objects: 100% (157/157), done.
        remote: Total 986 (delta 271), reused 210 (delta 207), pack-reused 622 (from 2)
        Receiving objects: 100% (986/986), 441.69 KiB | 7.36 MiB/s, done.
        Resolving deltas: 100% (468/468), done.

        $ cd getmarcapi

2. Create and activate a Python virtual environment using uv with the development dependencies:

    On Unix Environments:

        .. code-block:: console

            $ uv sync --dev
            Resolved 119 packages in 33ms
            Audited 106 packages in 46ms

            $ source .venv/bin/activate

    On Windows Environments:

        .. code-block:: pwsh-session

            > uv sync --dev
            Resolved 119 packages in 33ms
            Audited 106 packages in 46ms

            > .venv\Scripts\activate

3. Gather and build the static assets:

    There are some nice CSS libraries used in the top-level API documentation page. During development, you will need to
    install them to getmarcapi/static.

    .. code-block:: console

        (getmarcapi) $ npm install
        (getmarcapi) $ npm run env -- webpack --output-path=./getmarcapi/static

4. Start the Flask development server:


    .. code-block:: console

        (getmarcapi) $ FLASK_APP=getmarcapi/app.py uv run flask run
         * Serving Flask app 'getmarcapi/app.py'
         * Debug mode: off
        WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
         * Running on http://127.0.0.1:5000
        Press CTRL+C to quit

    .. important::

        You need to have the api url and api key.

        For development, you can set the **ALMA_API_DOMAIN** and **API_KEY** environment variables in your shell.


Running Tests
=============

To run tests, you need to have pytest installed. If you are using the development environment, it should already be
installed. Tests are run by executing the pytest command.

.. code-block:: shell-session

    (getmarcapi) $ pytest
    ============================== test session starts ==============================
    platform darwin -- Python 3.11.10, pytest-8.4.2, pluggy-1.6.0 -- .venv/bin/python
    cachedir: .pytest_cache
    rootdir: /Users/mydev/pythonprojects/getmarcapi
    configfile: pyproject.toml
    testpaths: tests
    plugins: anyio-4.12.1, typeguard-4.4.4
    collected 27 items

    tests/test_api.py::test_root PASSED
    tests/test_api.py::test_get_record_xml PASSED
    tests/test_api.py::test_get_record_missing_param PASSED
    tests/test_api.py::test_api_documentation PASSED
    ...
    ============================== 27 passed in 0.34s ===============================