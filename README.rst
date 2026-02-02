getmarcapi
==========

Config File
-----------

This application requires a configuration file to run. It should be in INI format
and contain the following sections and options:

.. code-block:: ini

    [ALMA_API]
    API_DOMAIN=
    API_KEY=


Using the Docker Image
----------------------

This Docker image requires a config file (see Config File section above) to be
mounted into the container in order to function properly. By default, the
container will look for the config file at inside the container at
`/app/settings.cfg` but this can be changed by running the container with the
GETMARCAPI_SETTINGS environment variable set to another path.

Port 5000 inside the container is used for the web server, so this port should
be forwarded to the host machine.

For example, you can run the container like this:

.. code-block:: sh

    docker run -d -p 5000:5000 -v /path/to/your/settings.cfg:/app/settings.cfg:ro --name getmarc getmarcapi