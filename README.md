# docker-pretty-ps
Tired of that awful super wide docker ps output? I'm always resizing the text on my terminal to see what ```docker ps``` is outputting, and it's making me go blind. Try docker-pretty-ps! Just run ```docker-pretty-ps``` and get your output long, instead of wide! **Now with COLORS!**

Run with ```docker-pretty-ps``` to get all running containers or ```docker-pretty-ps a-search```

```
$ docker-pretty-ps web
Currently running containers with: web

bad-actor-services_bad-actor-services-web_1
	Status:			    Up 3 days
	Created:		    3 days ago
	Ports:			    0.0.0.0:5000->5000/tcp
			    	    0.0.0.0:5001->80/tcp
	Container ID:		47549f78a0eb
	Image ID:		    bad-actor-services_bad-actor-services-web
	Command:		    tail -f /dev/null"

tradetrack_web_1
	Status:	    		Up 5 days
	Created:	    	5 days ago
	Ports:		    	80/tcp
			        	0.0.0.0:5010->5010/tcp
	Container ID:		416948f10a42
	Image ID:		    tradetrack_web
	Command:		    "gunicorn -b 0.0.0.0…"

tradetrack_dev_web_1
	Status:		    	Up 6 days
	Created:    		6 days ago
	Container ID:		5f7ab3814051
	Image ID:	    	tradetrack_dev_web
	Command:	    	"gunicorn -b 0.0.0.0…"

Total Containers:	12
Containers in Seach:	3
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
