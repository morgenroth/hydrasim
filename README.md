# Hydra Simulator #

This project has been superseded by the Hydra emulation framework:

 * Server component - https://github.com/morgenroth/hydra-webmanager
 * Slave component - https://github.com/morgenroth/hydra-slave
 * Node daemon - https://github.com/morgenroth/hydra-node

--

Hydra is a virtualized testbed for realistic large-scale network simulations. While classic simulation tools only provide approximations of the protocol stack, Hydra virtualizes nodes running a complete Linux system. Mobility models and connection management integrated into Hydra allow for the simulation of various wireless networking scenarios. Our distributed virtualization approach achieves excellent scalability and the automated node setup makes it easy to deploy large setups with hundreds of nodes. Hardware-in-the-loop simulations are possible, using Hydra to augment a testbed of real devices. The ability to boot a Hydra node completely from an USB flash drive enables the user to convert temporarily unused computer resources into a testbed without the need for any complex setup.

## Getting started ##

You need:
 * At least one x86 PC capable of booting from USB
 * An USB stick with the Hydra Slave environmnt (todo: show how to make your own)
 * The current Hydra codebase
 
 ## Configuration ##
 
The whole setup of Hydra is explained on this page. For most of the cases you only need to copy the directory "data/setup/default" to a new directory in "data/setups" and modify the files to you needs.

### Individual Setup ###

Folders:
 * mnt
 * overlay
 * packages

Files:
 * config.properties
 * modify_image_base.sh
 * modify_image_node.sh
 * packages.install
 
