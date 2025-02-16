# receipt-processor

## Docker Instructions

### Build the Docker Image

Open a terminal in the project root (where the Dockerfile is located) and run:

```bash
docker build -t receipt-processor .
```

Now run the docker image

```bash
docker run -d -p 8080:8080 receipt-processor
```
