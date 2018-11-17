# docker-pretty-ps
Tired of that awful super wide docker ps output? I'm always resizing the text on my terminal to see what ```docker ps``` is outputting, and it's making me go blind. Try docker-pretty-ps! Just run ```docker-pretty-ps``` and get your output long, instead of wide!

```
$ ./docker-pretty-ps
Running docker containers

Name:         cool-freaking-container
Container ID: 1a685dd9d351
Image ID:     28bbeb325405
Created:      9 days ago
Status:       Up 43 minutes
Command:      "tail -f /dev/null"

Name:         some-postgres
Container ID: 0370c73b4951
Image ID:     postgres:alpine
Created:      9 days ago
Status:       Up 43 minutes
Command:      "/bin/sh -c 'while t..."
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
* Add colors!
* Better install instructions.. probably
* Ordering options
* Support docker ps -a (to get all running and stopped containers on the host)
