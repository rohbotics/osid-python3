# Open Source Image Duplicator - Python3

OSID offers a UI (in the form of a webpage) to assist in duplicating SD cards from a Raspberry Pi.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Hardware

- Raspberry Pi 2
- 32 GB SD Card
- Official Raspberry Pi Touch Display
- Monoprice powered USB hubs (7 ports) (4 total)
- Monoprice SD card readers (26 total, rpi2 will stall on any more)

### Prerequisites

What things you need to install the software and how to install them

```
Python3
Pip3
cherrypy (through pip)
```

### Installing

Instructions is for Raspbian since this is designed to be ran on a Raspberry Pi.

Make sure you have python3 and pip3.

```
sudo apt-get install python3 python3-pip
```

and the CherryPy library.

```
sudo pip3 install cherrypy
```

Or

```
sudo pip3 install -r requirements.txt
```

To Do: Create an installation script to do it all.


## Deployment

Add the command to start when boot takes place

```
sudo python3 server.py
```

To Do: Elaborate and include in installation script.

## Built With

* [Skeleton](https://github.com/dhg/Skeleton) - CSS framework used to structure Web UI
* [CherryPy](http://docs.cherrypy.org/en/latest/) - API Library for Python used to manage all actions
* [rockandscissor/OSID](https://github.com/rockandscissor/osid) - Base Project originally written in PHP and Bash

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Aaron Nguyen** - [aaronnguyen](https://github.com/aaronnguyen)

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks [PurpleBooth](https://gist.github.com/PurpleBooth) for the [Readme Template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
