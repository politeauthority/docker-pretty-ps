# docker-pretty-ps (v.1.0.1)
Tired of that awful super wide ```docker ps``` output? I'm always shrinking my terminal output just to see what ```docker ps``` is trying saying... and it's making me go blind. If you commiserate, try `docker-pretty-ps`! Just run ```docker-pretty-ps``` and get your output long, instead of wide and with **COLORS!**

Use ```docker-pretty-ps``` to get all running containers, stopped containers, search for containers. You can do all this in a beautiful, colored, long output with only the data you requested.
Narrow your request with a search against containers with a name matching a search phrase; such as ```docker-pretty-ps webserver```.

### Why docker-pretty-ps though? (or TLDR)
- `docker ps` output is awful. Very wide output, yet not very helpful.
- `docker-pretty-ps` uses no 3rd party python packages, so it will run on any system that can run python, and Docker.
- You're a Docker wizard and need just a little bit more.

## Basic Example
Run ```docker-pretty-ps``` to get output of all currently running containers, or include an optional argument to search containers who's name match a phrase. Need to collect containers with multiple different phrases? Just comma separate them, like so ```docker-pretty-ps web,mail```
```bash
$ docker-pretty-ps web
Currently running containers with: web, mail
tradetrack_web_1
    Status:                 Up 5 days
    Created:                5 days ago
    Ports:                  80/tcp
                            0.0.0.0:5010->5010/tcp
    Container ID:           416948f10a42
    Image ID:               tradetrack_web
    Command:                "gunicorn -b 0.0.0.0…"

smpt-mail
    Container ID:         10d861029eae
    Image ID:             tvial/docker-mailserver:latest
    Command:              supervisord -c /etc…
    Created:              12 days ago
    Status:               Up 12 days
    Ports:                0.0.0.0:25->25/tcp
                          110/tcp
                          0.0.0.0:143->143/tcp
                          0.0.0.0:587->587/tcp
                          465/tcp
                          995/tcp
                          0.0.0.0:993->993/tcp
                          4190/tcp

Total containers:      14
Total running:         5
Containers in search:  2
```
# Install
### Over pip
```bash
pip install docker-pretty-ps
```

### Build and install
```bash
git clone https://github.com/politeauthority/docker-pretty-ps.git
cd docker-pretty-ps
python3 setup.py build
python3 setup install

```
Then you should be able to run the command ```docker-pretty-ps``` any where on your system.

# Other Example Usages
### Example Slim Output --slim, (-s) Mode
Typical docker-prettty-ps too long for ya? Don't fret! ```docker-pretty-ps``` has an answer to that. Use ```-s``` or ```--slim``` cli argument to get a slim output.
```bash
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

### Example --slim (-s) Mode with Just a Pinch More Data --inlcude (-i)
Sure, thats nice to know all containers on a host, but you also need to know what ports and the creation date, (for example).
Well then just the ```--include``` or ```-i``` cli arg.

Get current running containers with just the **c**reation time and the **p**ort configuration. Use the command ```docker-pretty-ps -s -i=cp```
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
### The other --inlcude (-i) argument options
The `-i` argument allows a user to specify the columns they want to receive back.
```
$ docker-pretty-ps -i ns
```
This will return just the container ID and the container status, like the following.
```
All currently running docker containers

bad-actor-services_bad-actor-services-web_1
    Container ID:         85cc746f77a4
    Status:               Up 3 hours

Total containers:   14
Total running:      1
```
#### --include column namespaces
- **n** - Co(**n**)tainer ID
- **i** - Container (**i**)mage ID
- **m** - Container co(**m**)mand
- **c** - Container (**c**)reation Date
- **s** - Container (**s**)tatus
- **p** - Container (**p**)orts

### Example all containers on system, on or off --all (-a)
Run ```docker-pretty-ps --all``` against all containers running or not on your system.
```
$ docker-pretty-ps -a
All docker containers

determined_goldstine
  Container ID:         51ab96c96896
  Image ID:             39e12b5ef620
  Command:              /bin/sh -c 'apk add…
  Created:              13 days ago
  Status:               Exited (1) 13 days ago
  State:                [OFF]
  Ports:

alpine-sshd
  Container ID:         23a8d9762781
  Image ID:             danielguerra/alpine-sshd
  Command:              docker-entrypoint.s…
  Created:              6 months ago
  Status:               Up 4 months
  State:                [ON]
  Ports:                0.0.0.0:4848->22/tcp

Total containers:   4
Total running:      2
```
## Full CLI Usage
```
usage: docker-pretty-ps [-h] [-a] [-s] [-i INCLUDE] [-o [ORDER]] [-r] [-j]
                        [-v]
                        [search]

positional arguments:
  search                Phrase to search containers, comma separate multiple.

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Selects against all rnning and stopped containers
  -s, --slim            Shows a slim minimal output.
  -i INCLUDE, --include INCLUDE
                        Data points to add to display, (c)reated, (p)orts,
                        (i)mage_id, co(m)mand
  -r, --reverse         Reverses the display order.
  -j, --json            Instead of printing, creates a json response of the
                        container data.
  -v, --version         Reverses the display order.
```

# Future
* Crush dem bugs.
* Create more python native usage.
* More testing.
