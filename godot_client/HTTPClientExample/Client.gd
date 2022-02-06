extends Panel

export var api_key: String
export var hostname: String
export var port: String
export var use_ssl: bool
var full_hostname = ""
var i = 0
var generate_embeddings_endpoint = ""
var generate_images_endpoint = ""

func _http_request_completed(result, response_code, headers, body):
	var response = body.get_string_from_utf8()
	#queue_new_image_generation()

func _images_generated(result, response_code, headers, body):
	var RandomImageScene = load("res://HTTPClientExample/RandomImage.tscn")
	if $MarginContainer/VBoxContainer/HBoxContainer.get_child_count() < 9:
		var new_scene = RandomImageScene.instance()
		new_scene.controller = self
		$MarginContainer/VBoxContainer/HBoxContainer.add_child(new_scene)
		queue_new_image_generation()
	else:
		queue_new_image_generation()
		$MarginContainer/VBoxContainer/HBoxContainer.get_child(i).refresh_image()
		i = (i+1) % 9

func _ready():
	if hostname == "http://127.0.0.1":
		self.use_ssl = false
	else:
		self.use_ssl = true
	if port != "":
		self.full_hostname = hostname + ":" + port
	else:
		self.full_hostname = hostname
	self.generate_embeddings_endpoint = full_hostname + "/generate_embeddings"
	self.generate_images_endpoint = full_hostname + "/generate_images"

func _on_GenerateEmbeddings_pressed():
	var request = HTTPRequest.new()
	var query = JSON.print({"prompt": $MarginContainer/VBoxContainer/EmbeddingGeneration/Prompt.text,
							"start": $MarginContainer/VBoxContainer/EmbeddingGeneration/Start.text,
							"end": $MarginContainer/VBoxContainer/EmbeddingGeneration/More.text})
	add_child(request)
	request.connect("request_completed", self, "_http_request_completed")
	print(self.generate_embeddings_endpoint)
	var error = request.request(self.generate_embeddings_endpoint, ["Content-Type: application/json", "x-api-key: " + api_key], self.use_ssl, HTTPClient.METHOD_POST, query)
	if error != OK:
		push_error("An error occured in the HTTP request.")

func queue_new_image_generation():
	var request = HTTPRequest.new()
	var query = JSON.print({"iterations": 15, "start_from_best": true})
	add_child(request)
	request.connect("request_completed", self, "_images_generated")
	var error = request.request(self.generate_images_endpoint, ["Content-Type: application/json", "x-api-key: " + api_key], self.use_ssl, HTTPClient.METHOD_POST, query)
	if error != OK:
		push_error("An error occured in the HTTP request.")


func _on_Canvas_fireaway(buffer, position):
	var RandomImageScene = load("res://HTTPClientExample/RandomImage.tscn")
	var new_scene = RandomImageScene.instance()
	new_scene.controller = self
	var image = Image.new()
	image.load_png_from_buffer(buffer)
	var imagetexture = ImageTexture.new()
	imagetexture.create_from_image(image, 0)
	new_scene.texture = imagetexture
	new_scene.position = position + Vector2(64, 64)
	print(new_scene.position)
	$Group.add_child(new_scene)
	
