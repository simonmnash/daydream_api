extends TextureButton

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
	self.texture_normal = new_texture


func _on_RandomImage_pressed():
	var image = self.texture_normal.get_data()
	image.convert(Image.FORMAT_RGBA8)
	image.save_png("test.png")
	
	
	var file = File.new()
	file.open('res://test.png', File.READ)
	var file_content = file.get_buffer(file.get_len())

	var body = PoolByteArray()
	body.append_array("\r\n--WebKitFormBoundaryePkpFF7tjBAqx29L\r\n".to_utf8())
	body.append_array("Content-Disposition: form-data; name=\"file\"; filename=\"test.png\"\r\n".to_utf8())
	body.append_array("Content-Type: image/png\r\n\r\n".to_utf8())
	body.append_array(file_content)
	body.append_array("\r\n--WebKitFormBoundaryePkpFF7tjBAqx29L--\r\n".to_utf8())

	var headers = [
		"Content-Type: multipart/form-data;boundary=\"WebKitFormBoundaryePkpFF7tjBAqx29L\"",
		"x-api-key: BABABBABABBALLLALLLEER"
	]
	var http = HTTPClient.new()
	http.connect_to_host("http://127.0.0.1", 8000, false)

	while http.get_status() == HTTPClient.STATUS_CONNECTING or http.get_status() == HTTPClient.STATUS_RESOLVING:
		http.poll()
		OS.delay_msec(500)
	assert(http.get_status() == HTTPClient.STATUS_CONNECTED) # Could not connect
	var err = http.request_raw(HTTPClient.METHOD_POST, "/uploadfile" , headers, body)
	assert(err == OK) # Make sure all is OK.
	while http.get_status() == HTTPClient.STATUS_REQUESTING:
		# Keep polling for as long as the request is being processed.
		http.poll()

