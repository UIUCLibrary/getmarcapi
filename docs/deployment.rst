=========================
Installing and Deployment
=========================

This section provides instructions for deploying the application in a production environment.

In order to use the application, you need to create a configuration file as described below.

.. _configuration-file:

Configuration File
==================

The application requires a configuration file in INI format. The configuration file should contain the following sections and options:

.. code-block:: ini

    [ALMA_API]
    API_DOMAIN=      ;url to ALMA's API endpoint
    API_KEY=         ;API key for accessing ALMA's API

Using Docker Image for Deployment
=================================

If a Docker image is available, you can deploy the application using Docker. And if not, you can build the Docker image
locally using the provided `Dockerfile`. :ref:`See the Development section for instructions on building the Docker image.<dockerizing>`

If a docker image has been created locally, use the following command, ensuring to mount your configuration file and
expose the necessary port:

.. code-block:: console

    $ docker run -d -p 5000:5000 -v /path/to/your/settings.cfg:/app/settings.cfg:ro --name getmarc getmarcapi

By default, the container looks for the config file at `/app/settings.cfg` inside the container, but this can be
changed by setting the `GETMARCAPI_SETTINGS` environment variable to another path.

The default port 5000 inside the container is used for the web server, so ensure this port is forwarded to the host
machine.
