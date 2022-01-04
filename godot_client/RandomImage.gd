extends TextureRect

var image_url = "http://127.0.0.1:8000/files/out_00000"
func _ready():
	var request = HTTPRequest.new()
	add_child(request)
	request.connect("request_completed", self, "_http_request_completed")
	var error = request.request(image_url, ["x-api-key: BABABBABABBALLLALLLEER"])
	if error != OK:
		push_error("An error occured in the HTTP request.")
		
func _http_request_completed(result, response_code, headers, body):
	var image = Image.new()
	var image_error = image.load_png_from_buffer(body)
	if image_error != OK:
		print("An error occurred while trying to display the image.")
	var new_texture = ImageTexture.new()
	new_texture.create_from_image(image)
	self.texture = new_texture
