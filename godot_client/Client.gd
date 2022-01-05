extends Panel


var headers = [{"x-api-key": "BABABBABABBALLLALLLEER"}]
var start_from_best = false
var i = 0
func _http_request_completed(result, response_code, headers, body):
	var response = body.get_string_from_utf8()
	queue_new_image_generation()

func _images_generated(result, response_code, headers, body):
	var RandomImageScene = load("RandomImage.tscn")
	if $MarginContainer/VBoxContainer/HBoxContainer.get_child_count() < 9:
		var new_scene = RandomImageScene.instance()
		new_scene.controller = self
		$MarginContainer/VBoxContainer/HBoxContainer.add_child(new_scene)
		queue_new_image_generation()
	else:
		queue_new_image_generation()
		$MarginContainer/VBoxContainer/HBoxContainer.get_child(i).refresh_image()
		i = (i+1) % 9



func _on_GenerateEmbeddings_pressed():
	var request = HTTPRequest.new()
	var query = JSON.print({"prompt": "Rose"})
	add_child(request)
	request.connect("request_completed", self, "_http_request_completed")
	var error = request.request("http://127.0.0.1:8000/generate_embeddings", ["Content-Type: application/json", "x-api-key: BABABBABABBALLLALLLEER"], false, HTTPClient.METHOD_POST, query)
	if error != OK:
		push_error("An error occured in the HTTP request.")

func queue_new_image_generation():
	var request = HTTPRequest.new()
	var query = JSON.print({"iterations": 15, "start_from_best": self.start_from_best})
	add_child(request)
	request.connect("request_completed", self, "_images_generated")
	var error = request.request("http://127.0.0.1:8000/generate_images", ["Content-Type: application/json", "x-api-key: BABABBABABBALLLALLLEER"], false, HTTPClient.METHOD_POST, query)
	if error != OK:
		push_error("An error occured in the HTTP request.")
