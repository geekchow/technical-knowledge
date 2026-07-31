## Mock Question

> **Solve this question on instance:** `ssh ckad9044`

During a quarterly audit, the Security team of **department Luna** discovered that a legacy service needs to be containerized. The application files and build context are located at `/opt/course/14/image`. The container runs a **Python** application that listens on port **8080**.

**NOTE:** Run all commands as user `candidate`. For docker use `sudo docker`.

1. **Modify the Dockerfile.** Add an environment variable `LUNA_APP_ENV` hardcoded to the value `production-9f3a-4471-bc12-8e0dacf71230`. Also ensure the container **exposes port 8080**.

2. **Build the image using Docker**, named `registry.killer.sh:5000/luna-app`, tagged as both `stable` and `v2-docker`. Push both tags to the registry.

3. **Build the image using Podman**, named `registry.killer.sh:5000/luna-app`, tagged as `v2-podman`. Push it to the registry.

4. **Run a Podman container** in the background named `luna-app`, using image `registry.killer.sh:5000/luna-app:v2-podman`, and **map host port 8080 to container port 8080**. The container must be started from `candidate@ckad9044`, not `root@ckad9044`.

5. **Inspect the running container** `luna-app` and write its **IP address** into `/opt/course/14/ip`. Then write all **container image digests** currently stored in Podman's local storage into `/opt/course/14/digests` on `ckad9044`.

---
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Step 1: Add this env var
ENV LUNA_APP_ENV=production-9f3a-4471-bc12-8e0dacf71230

# Step 1: Expose the port
EXPOSE 8080

CMD ["python", "app.py"]
```

---

**Answer to Mock Question**

```bash
ssh ckad9044

# Step 1: Edit Dockerfile
cd /opt/course/14/image
vi Dockerfile
# Add/modify:
# ENV LUNA_APP_ENV=production-9f3a-4471-bc12-8e0dacf71230
# EXPOSE 8080

# Step 2: Docker build + push both tags
sudo docker build \
  -t registry.killer.sh:5000/luna-app:stable \
  -t registry.killer.sh:5000/luna-app:v2-docker .

sudo docker push registry.killer.sh:5000/luna-app:stable
sudo docker push registry.killer.sh:5000/luna-app:v2-docker

# Step 3: Podman build + push
podman build -t registry.killer.sh:5000/luna-app:v2-podman .
podman push registry.killer.sh:5000/luna-app:v2-podman

# Step 4: Run rootless Podman container with port mapping
podman run -d --name luna-app \
  -p 8080:8080 \
  registry.killer.sh:5000/luna-app:v2-podman

# Step 5: Get IP and image digests
podman inspect luna-app \
  --format '{{.NetworkSettings.IPAddress}}' \
  > /opt/course/14/ip

podman images --digests > /opt/course/14/digests
```

export app log to host path
```bash
# Create the host directory first (recommended to avoid permission issues)
mkdir -p ~/container-logs/myapp

docker run -d \
  --name my-container \
  -v ~/container-logs/myapp:/app/logs \          # ← host path : container path
  my-image:latest
```

The mock question adds complexity around **port mapping**, **EXPOSE** directives, **container inspection**, and **image digest** listing — all common CKAD exam patterns.
