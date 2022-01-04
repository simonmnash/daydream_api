extends Panel


var headers = [{"x-api-key": "BABABBABABBALLLALLLEER"}]


func _http_request_completed(result, response_code, headers, body):
	var response = body.get_string_from_utf8()
	queue_new_image_generation()

func _images_generated(result, response_code, headers, body):
	var RandomImageScene = load("RandomImage.tscn")
	$VBoxContainer/HBoxContainer.add_child(RandomImageScene.instance())
	if $VBoxContainer/HBoxContainer.get_child_count() < 6:
		queue_new_image_generation()



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
	var query = JSON.print({"iterations": 10})
	add_child(request)
	request.connect("request_completed", self, "_images_generated")
	var error = request.request("http://127.0.0.1:8000/generate_images", ["Content-Type: application/json", "x-api-key: BABABBABABBALLLALLLEER"], false, HTTPClient.METHOD_POST, query)
	if error != OK:
		push_error("An error occured in the HTTP request.")
