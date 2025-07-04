# ImageModerator
A simple server that accepts an image and sends it to a free moderation service to see if there is unwanted content on it. A test assignment from the company BKH Ekom LLC.

## Description
A server (FastAPI) that allows you to evaluate an image for NSFW content. The [Clarify](https://clarifai.com/clarifai/main/models/nsfw-recognition) service is used for evaluation.

## Installation
Docker is used to build the project. You must create a file before building it.env by example .env.example in the root of the project. 
Next, the assembly and launch is carried out using the ```docker compose up --build``` command.

## Endpoints

- **POST /moderate/** - Check the image for NSFW.
- **GET /moderation_result/{moderation_request_id}** - Check the moderation status. If it takes a long time to send an image 
via the endpoint (the service is slow or there are too many requests), the endpoint will return the request id. You can use this id to find out the moderation status later.
- **GET /health/** - Healthcheck

More detailed documentation is available in Swagger (http://localhost:8000/docs)

## Technologies
- HTTPX
- Redis
- FastAPI
- Docker