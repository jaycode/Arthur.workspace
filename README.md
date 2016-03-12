# Development Notes

## Building The App for The First Time

Arthur runs on Docker. To build it, run the following:

docker build -t jaycode/arthur .

## Running The App

Arthur application is comprised of three servers:
- The main app and workspace app, both are located in the same docker as below:
  ```
  docker run -dit -v /c/path_to_project/:/media/disk -p 8000:8000 -p 8888:8888 -p 6006:6006 -p 49152:49152 --name arthur jaycode/arthur
  ```
  In this case `/c/path_to_project/` is the directory that contains '/Arthur/', the main directory of this application. It is important to follow this similar structure (i.e. app's root dir's parent virtually linked with container) to ensure external libraries are running without issues.
- A Redis server for session sharing between main and workspace apps. Run the following docker command to set it up:
  ```docker run -dit -v /c/path_to_project/Arthur/dev/redis.conf:/usr/local/etc/redis/redis.conf -p 6379:6379 redis redis-server /usr/local/etc/redis/redis.conf
  ```
  To display errors from running that code:
  ```
  docker logs $ID
  ```

  To store session in persistent data, run this instead (not needed but good for debugging session values):
  ```
  ID=$(docker run --name arthur-redis -d -v /c/path_to_project/Arthur/redis_data:/data -v /c/path_to_project/Arthur/dev/redis.conf:/usr/local/etc/redis/redis.conf -p 6379:6379 redis redis-server /usr/local/etc/redis/redis.conf --appendonly yes)
  ```
  session:eyJhY3RpdmVfcHJvamVjdCI6InJpc2t5In0.CT36Hg.vX7ffotqpm1y6bMXgN3K3YisTiQ

Port information:
- 8000: Arthur main app.
- 8888: iPython notebook.
- 6006: Theano's Tensorboard.
- 49152: Arthur workspace app.
- 6379: Redis (used in second docker above)


To access a docker container, run the following:
```
docker exec -ti arthur bash
```

Before actually running the server, make sure mongodb server is up and running. In localhost
this is done by simply running command `mongod`.

And finally, run the server by going to `/media/disk/Arthur` and running:
```
python server.py
```

And create another instance to run:
```
python server-workspace.py
```


## How to update styles / javascript

Grunt is used to allow compass to update scss as well as uglifying javascript files.
First `cd` to root directory (the same directory that contains
this readme file, then install grunt with `npm install grunt`. Other npm modules will then be 
asked to be installed (such as `grunt-sass` and `grunt-contrib-watch`).

When all npm modules have been installed, grunt watcher can be run by command `grunt`
inside root directory which will detect updates to scss and javascript files then compile them 
into css file readily used in app.

All scss and javascript files are editable from directory `dev/front_end`.


## How to add new modules

When adding new modules, vendor all the pip *.tar.gz into `vendor/` with following command:


```
pip install --download vendor -r requirements.txt
```

## How to test your code

ipython notebook documents in `/test` are there to systematically test and document your tests.

To test out library code at its lowest level, run the code directly e.g.

```
python libs\arthur\document.py > result.txt
```

`result.txt` will then contain output of your test.

## Database Stuff (MongoDB)

### MongoDB server

Current recommendation is to run database server outside of docker. To have MongoDB database server
up and running, do the following for Windows dev machine (assuming docker vm is running):

1. Open "Network Connections".
2. Find "VirtualBox Host-Only Network Status".
3. Click "Details..." and take note on IPv4 Address.
4. Enter this ip address as mongodb config (e.g. D:\mongodb\config.txt file), under the setting `net.bindIp`.
   Enter this next to local IP e.g. "127.0.0.1,192.168.56.1".
5. From inside docker, it should now be possible to connect with command `mongo 192.168.56.1`.

### Installation

Run the following script for installation (make sure to turn the database server on first).
```
python dev/install.py
```

## Clean code with pylint

Run `pylint [path] > pylint.txt` from root directory to check code cleanliness at given path. 

## Documentation

Arthur uses Sphinx to write documentation. All documentation files are located in `docs/` directory. Sphinx
will automatically searches for docstrings within the code and compile them into documentation. To compile the files,
run `make html` from within `docs/` directory.