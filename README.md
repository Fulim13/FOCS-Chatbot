This is a ChatBot about FOCS

# Prerequisite

1. [Install Docker](https://www.docker.com/products/docker-desktop/)
2. Create a .env file in `/api/backend`
3. Add the following to the .env file

```
MISTRAL_API_KEY=xxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="xxxxxxxxxxx"
LANGCHAIN_PROJECT="project-xxxxxxxxxxx"
```

# Run Locally

```
cd FOCS
```

```
docker-compose up
```

# Deployment

1. SSH into the server
2. Clone the repository
3. `cd` to the repository
4. Run `sudo apt update`
5. Run `sudo apt install docker.io nodejs npm -y`
6. Run `sudo systemctl start docker`
7. Run `sudo systemctl enable docker`
8. Install docker compose

```
sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

9. Run `sudo chmod +x /usr/local/bin/docker-compose`
10. Run `docker-compose --version`
11. Add. env file to `/api/backend`
12. Run `docker-compose up -d`

# References to dockerize django and react project

https://dev.to/anjalbam/dockerize-a-django-react-and-postgres-application-with-docker-and-docker-compose-by-anjal-bam-e0a
