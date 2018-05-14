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

# Backend transforms
Transforms are written in the
[SakForm](https://github.com/innovationgarage/sakstig) templating language (which uses SakStig/Objectpath path expressions).

## Path context

Template SakStig expressions have the following available to them:

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
