# Build the pkg cache

First build the cache image:

```console
$ docker buildx build -t cache --platform=linux/amd64 -f docker/Dockerfile.cache .
```

Then run it from the `ecoscope-workflows` repo root to build the pkg cache:

> **Note**: This may take a fair amount of time. But ideally we don't have to do it that frequently.

```console
$ docker run -it \
-v $(pwd)/.rattler-build/artifacts:/opt/channel-mount \
-v $(pwd)/.conda-pkg-cache:/opt/pkg-cache \
--platform=linux/amd64 \
cache
```
