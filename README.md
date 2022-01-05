# Daydream
## A python server for interacting with CLIP models
### (and some example clients for that server)

Daydream is a FastAPI server that wraps https://github.com/crowsonkb/v-diffusion-pytorch in some quality of life methods to make it easier to build human in the loop systems for playing with text to image models.

Currently there are three things in this repo:

1) A FastAPI server, designed to serve CLIP results to single clients.

2) A minimal example Godot client (generates embeddings for a single given phrase, then runs 6 super-short generation processes using those embeddings).

3) A not-quite-working-yet Krita plugin client.

Daydream is built with the assumption that the server is being operated by the same person using the client, and that only one client will be using the server.


### Godot client after starting, and generating 128x128 images in ~30 iterations:
![Godot client on starting](https://github.com/simonmnash/daydream_api/blob/8f34ff5a1b4c8a9b0501c9f16a4240c85d5c9ec3/examples/early_screenshot.png)

### Godot client after several rounds of the user picking a favorite 128x128 image to start from, and running ~30 iterations per round.
![Godot client after picking lots of favorite candidates](https://github.com/simonmnash/daydream_api/blob/8f34ff5a1b4c8a9b0501c9f16a4240c85d5c9ec3/examples/late_screenshot.png)
