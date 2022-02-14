# Daydream
## A python server for interacting with CLIP models
### (and some example clients for that server)

![Godot client after a whole lot of CLIP](https://github.com/simonmnash/daydream_api/blob/main/examples/512.jpg)

Daydream is a FastAPI server that wraps https://github.com/crowsonkb/v-diffusion-pytorch to make it easier to build human in the loop systems for playing with text to image models.

Currently there are three things in this repo:

1) A FastAPI server, designed to serve CLIP results to single clients. 

2) A minimal example Godot client, where clicking on a canvas of shifting colors sends an image chunk to the server, does some clip guided diffusion, and sends the result back to superimpose over the canvas.

3) A not-quite-working-yet Krita plugin client.

Daydream is built with the assumption that the server is being operated by the same person using the client, and that only one client will be using the server.

![Result from a Krita Client](https://github.com/simonmnash/daydream_api/blob/main/examples/carefreedragonintheskyabovethemossystoneroccoco.png)

A result from the krita client that didn't invove any human interaction except prompting. Still working on getting some human interacting into the krita client.
