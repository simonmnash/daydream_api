extends Node2D


const image_scene = preload("res://WebSocketClientExample/Image.tscn")
var current_image = null
var last_image = null
var switch = false
signal image_selected(image)

func _ready():
	pass

func add_new_image(prompt: String):
	var new_image = image_scene.instance()
	new_image.prompt = prompt
	new_image.connect("selected", self, "_image_selected")
	new_image.position = Vector2(rand_range(0, 600), rand_range(0, 450))
	add_child(new_image)
	return new_image

func _image_selected(image):
	current_image = image
	emit_signal("image_selected", image)
