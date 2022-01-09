extends Node2D


const image_scene = preload("res://WebSocketClientExample/Image.tscn")
var current_image = null

signal image_selected(image)

func _ready():
	add_new_image("Night Sky")
	add_new_image("Ocean Blue")
	add_new_image("Radient Forest")
	current_image = self.get_child(0)
	

func add_new_image(prompt: String):
	var new_image = image_scene.instance()
	new_image.prompt = prompt
	new_image.connect("selected", self, "_image_selected")
	new_image.position = Vector2(rand_range(-500, 500), rand_range(-300, 300))
	add_child(new_image)

func _image_selected(image):
	current_image = image
	emit_signal("image_selected", image)

