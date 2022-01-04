# Daydream
## A python Server for Interacting With CLIP Models

Daydream is a FastAPI server that wraps https://github.com/crowsonkb/v-diffusion-pytorch in some quality of life methods to make it easier to build human in the loop systems for playing with image generating models.

Currently there are three things in this repo:

1) A FastAPI server, designed to serve CLIP results to single clients.

2) A minimal working Godot client.

3) A not-quite-working-yet Krita plugin client.

Daydream is built with the assumption that the server is being operated by the same person using the client, and that only one client will be using the server.
