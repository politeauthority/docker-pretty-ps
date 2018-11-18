# docker-pretty-ps
Tired of that awful super wide docker ps output? I'm always resizing the text on my terminal to see what ```docker ps``` is outputting, and it's making me go blind. Try docker-pretty-ps! Just run ```docker-pretty-ps``` and get your output long, instead of wide! **Now with COLORS!**

```
$ ./docker-pretty-ps
Currently running docker containers

some-postgres
    Status:         Up About an hour
    Created:        4 weeks ago
    Container ID:   294843cd3eab
    Image ID:       postgres:alpine
    Command:        "docker-entrypoint.s…"

some-python
    Status:         Up About an hour
    Created:        3 months ago
    Container ID:   0370c73b4951
    Image ID:       some-python
    Command:        "/bin/sh -c 'while t…"
```

# Install
**Step 1:** *git* the repo
```
git clone https://github.com/politeauthority/docker-pretty-ps.git
```

**Step 2:** move the docker-pretty-ps executable somewhere within your path, this may change depending on OS and setups, for most my systems this works.
```
cp docker-pretty-ps/docker-pretty-ps ~/bin
```

# Future
* Add unit tests
* Better install instructions.. probably
* Ordering options
* Support docker ps -a (to get all running and stopped containers on the host)
