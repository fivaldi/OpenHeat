[![Build Status](https://api.travis-ci.org/fivaldi/OpenHeat.svg)](https://travis-ci.com/github/fivaldi/OpenHeat)

# OpenHeat
Open source advanced control of central heating system infrastructure using simple / affordable hardware.

## Features (WIP)
- Control your central heating system and its components from [one place](config.yaml.sample).
- Switch heating programs depending on weather forecast: Considers factors like cloud coverage / humidity / wind etc.
    - The are various reasons for this, e.g. to meet physiological temperature comfort requirement (subjective), heating economy / ecology (objective) and others...
- Fallback strategies in case of temporary network issues.
- Send mail notifications on various events.
- Web service providing information about programs / sensors / controllers...

## Supported Hardware

OpenHeat aims any [Raspberry PI](https://www.raspberrypi.org/) with [GPIO inputs / outputs](https://www.raspberrypi.org/documentation/usage/gpio/) (or compatible).

The prototype / development is based on Model „B“ (year ~2012) which means that any newer model would have enough resouces to run OpenHeat.

### Sensors
- 1-Wire (builtin)
- [brrr.cz/TCZUNI1](http://brrr.cz/brrr.php?runpagephp=createnavodpage&type=TCZUNI1) universal Wi-Fi sensor(s)

### Controllers
- OnOff (builtin) using Arduino 4-channel relay module
- SimplePID (builtin) based on [simple-pid](https://github.com/m-lundberg/simple-pid) with ON-OFF output (the very same relay module)

## Local Testing
```
$ docker build -t openheat-tests -f Dockerfile-tests .
$ docker run -v </path/to/my/OpenHeat.git>:/app openheat-tests
```