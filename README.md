# docker-pretty-ps (v.0.0.1a72)
Tired of that awful super wide ```docker ps``` output? I'm always resizing the text on my terminal to see what ```docker ps``` is outputting, and it's making me go blind. Try docker-pretty-ps! Just run ```docker-pretty-ps``` and get your output long, instead of wide! **Now with COLORS!**

Run with ```docker-pretty-ps``` to get all running containers.
You can also search containers, containing a search phrase, such as ```docker-pretty-ps webserver```

## Example: Most Basic
run ```docker-pretty-ps``` to get output of all currently running containers, or inlcude an optional argument to search containers who's name match a phrase. Need to collect containers with multiple different phrases? Just comma sepperate them (```docker-pretty-ps web,mail```)
```
$ docker-pretty-ps web
Currently running containers with: web

bad-actor-services_bad-actor-services-web_1
    Status:                Up 3 days
    Created:               3 days ago
    Ports:                 0.0.0.0:5000->5000/tcp
                           0.0.0.0:5001->80/tcp
    Container ID:          47549f78a0eb
    Image ID:              bad-actor-services_bad-actor-services-web
    Command:               tail -f /dev/null"

tradetrack_web_1
    Status:                 Up 5 days
    Created:                5 days ago
    Ports:                  80/tcp
                            0.0.0.0:5010->5010/tcp
    Container ID:           416948f10a42
    Image ID:               tradetrack_web
    Command:                "gunicorn -b 0.0.0.0…"

tradetrack_dev_web_1
    Status:                 Up 6 days
    Created:                6 days ago
    Ports:
    Container ID:           5f7ab3814051
    Image ID:               tradetrack_dev_web
    Command:                "gunicorn -b 0.0.0.0…"

Total Containers:   12
Containers in Search:   3
```

## Example: Slim output --slim, (-s) mode
Typical docker-prettty-ps too long for ya? Don't fert! ```docker-pretty-ps```` has an answer to that, use ```-s``` or ```--slim``` cli argument to get a slim output.
```
$ docker-pretty-ps -s
All currently running docker containers

nginx-proxy
some-postgres
carpetbag_carpetbag_1
badactorservices_bad-actor-services_1
badactorservices_bad-actor-services-data_1

Total containers:   21
Total running:      5
```

## Example --slim (-s) mode with just a pinch more data: --inlcude (-i)
Sure, thats nice to know all containers on a host, but you also need to know what ports and the creation date, (for example).
Well then just the ```--include``` or ```-i``` cli arg.

Get current running containers wiwth just the **c**reation time and the **port** configuration. Use the command ```docker-pretty-ps -s -i=cp```
```
$ docker-pretty-ps -s -i=cp
All currently running docker containers

carpetbag_carpetbag_1
    Created:              42 minutes ago
    Ports:

some-postgres
    Created:              5 months ago
    Ports:                10.138.44.203:5432->5432/tcp

nginx-proxy
    Created:              5 days ago
    Ports:                0.0.0.0:80->80/tcp
                          0.0.0.0:443->443/tcp

Total containers:   5
Total running:      3
```
### Other available arguments to --inlcude (-i):
- **n** - Co(**n**)tainer ID
- **i** - Container (**i**)mage ID
- **m** - Container co(**m**)mand
- **c** - Container (**c**)reation Date
- **s** - Container (**s**)tatus
- **p** - Container (**p**)orts

## Example: All containers on system, on or off --all (-a)
Run ```docker-pretty-ps -all``` against all containers running or not on your system.
```
$ docker-pretty-ps -a
All docker containers

tradetrack_api_1
    Container ID:         d7755eeda676
    Image ID:             tradetrack_api
    Command:              gunicorn -b 0.0.0.0…
    Created:              3 months ago
    Status:               Exited (0) 8 weeks ago
    State:                [OFF]
    Ports:

bad-actor-services_bad-actor-services-web_1
    Status:             Up 3 days
    Created:            3 days ago
    Ports:              0.0.0.0:5000->5000/tcp
                        0.0.0.0:5001->80/tcp
    Container ID:           47549f78a0eb
    Image ID:           bad-actor-services_bad-actor-services-web
    Command:            tail -f /dev/null"

tradetrack_web_1
    Status:                 Up 5 days
    Created:                    5 days ago
    Ports:                  80/tcp
                        0.0.0.0:5010->5010/tcp
    Container ID:           416948f10a42
    Image ID:           tradetrack_web
    Command:            "gunicorn -b 0.0.0.0…"

tradetrack_dev_web_1
    Status:                 Up 6 days
    Created:                6 days ago
    Ports:
    Container ID:           5f7ab3814051
    Image ID:               tradetrack_dev_web
    Command:                "gunicorn -b 0.0.0.0…"

Total containers:   4
Total running:      3
```
## Full CLI Usage
```
usage: docker-pretty-ps [-h] [-a] [-s] [-i INCLUDE] [-o [ORDER]] [-r] [-v]
                        [search]

positional arguments:
  search                Phrase to search containers, comma separate multiples.

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Selects against all rnning and stopped containers
  -s, --slim            Shows a slim minimal output.
  -i INCLUDE, --include INCLUDE
                        Data points to add to display, (c)reated, (p)orts,
                        (i)mage_id, co(m)mand
  -o [ORDER], --order [ORDER]
                        Order by, defaults to container start, allows
                        'container', 'image'.
  -r, --reverse         Reverses the display order.
  -v, --version         Reverses the display order.
```

# Install
**Step 1:** *git* the repo
```
git clone https://github.com/politeauthority/docker-pretty-ps.git
```

**Step 2:** move the docker-pretty-ps executable somewhere within your path, this may change depending on OS and setups, for most my systems this works.
```
cp docker-pretty-ps/docker-pretty-ps /bin
```

# Future
* Add unit tests!
* Add optional json output to file.
* Create more python native usage.
