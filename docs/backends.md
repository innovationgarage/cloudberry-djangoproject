A Cloudberry backend definition consists of

* a JSON schema
* A transform
* A reference to a lower backend

The schema specifies how configuration for that backend should look,
and is used to generate a user interface for editing the configuration.

The transform specifies how to extract configuration for a specific device and convert it from the schema of
the backend to the schema of the lower level backend.

# Backend schemas
Backend schemas are normal JSON schemas, with the addition of a way to reference foreign django model objects.

Example JSON schema for configuring a set of devices with an ip number and port:

    {
        "properties": {
            "servers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "host": {"$ref": "#/definitions/fk__cloudberry_app_Device"},
                        "ip": {"type": "string"},
                        "port": {"type": "integer"}
                    }
                }
            }
        }
    }

Example configuration that a user can generate using the configuration editor and a backend with the above schema:

    {
        "servers": [
            {
                "host": "fk://cloudberry_app.Device/e19d0072-daae-4e0b-8514-47d73f522bc1",
                "ip": "192.168.0.1",
                "port": 4711
            },
            {
                "host": "fk://cloudberry_app.Device/4e4a5c64-a84a-4abe-91c8-74d8496a8c1d",
                "ip": "10.0.0.1",
                "port": 4712
            }
        ]
    }

# Backend transforms
Transforms are written in the
[SakForm](https://innovationgarage.github.io/sakstig/) templating language
(which uses [ObjectPath](http://objectpath.org/) expressions to extract values).

## Path context

Template [ObjectPath](http://objectpath.org/) expressions have the following available to them:

* @ the current path object, e.g. the object selected by the preceding fragment of the SakStig expression.
* $.config the configuration to be transformed. This configuration matches the schema of the backend the
  transform belongs to.
* @template() the current template object, e.g. the object selected by the path of the closest surrounding template.
* $.context.fk foreign key model loader, see below.

# Foreign keys
Foreign keys to django models are represented in JSON as strings on the form 'fk://cloudberry_app.Device/4711'.
They should however be considered opaque values save for the fk:// prefix.

## Schema specification
Foreign keys can be specified in the JSON schema as a reference to a schema definition with a special name:

    {"$ref": "#/definitions/fk__cloudberry_app_Device"}

The definition itself is a string enum of all possible foreign keys, and will produce a drop-down list in the configuration
editor, with the usual add/edit django admin buttons next to it.

## Lookups
SakForm templates can load a django models by their JSON foreign key representation. This is done using the `$.context.fk`
context variable:

    $.context.fk['fk://cloudberry_app.Device/4711'].some_device_attribute_name
