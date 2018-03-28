# Example backends

The files in this directory come in pairs that each define a schema and a transform for a backend.
Their content can be directly pasted into the respective fields of a backend model.
They all generate output for the OpenWRT/Cloudberry backend.

# cloudberry_vpn

Lets you configure a VPN server running inside a docker container, and a set of clients running on e.g. RPi:s, each with a
lan behind it, routing traffic over OpenVPN via the docker container between the lan:s.

# cloudberry_docker

Lets you configure cloudberry-docker-manager to run cloudberry_vpn servers.
