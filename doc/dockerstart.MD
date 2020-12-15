# dockerstart

If [dockertest](dockertest.MD) or [dockerdeploy](dockerdeploy.MD) is considered to slow for comfort, this convenience function spins up an fsst docker container with FlureeDB only.

It is important to note that there is no persistance with a deploy ran like this. When the
container is stopped, your database will be gone. Usually for testing and development this
is what you want.

```bash
./fsst dockerstart --tag alpha
```


