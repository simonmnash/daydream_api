extends Node2D


const image_scene = preload("res://WebSocketClientExample/Image.tscn")
var current_image = null

func _ready():
	add_new_image("Night Sky")
	add_new_image("Ocean Blue")
	add_new_image("Radient Forest")
	current_image = self.get_child(0)
	

func add_new_image(prompt: String):
	var new_image = image_scene.instance()
	new_image.prompt = prompt
	new_image.connect("selected", self, "_image_selected")
	new_image.position = Vector2(rand_range(-256, 256), rand_range(-256, 256))
	add_child(new_image)
	
func _image_selected(image):
	current_image = image
