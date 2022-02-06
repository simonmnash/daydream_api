extends Sprite

var image_url = "http://127.0.0.1:8000/files/out_00000"
var controller = null
var scene_index = null

func refresh_image():
	var request = HTTPRequest.new()
	add_child(request)
	request.connect("request_completed", self, "_http_request_completed")
	var error = request.request(image_url, ["x-api-key: " + self.controller.api_key])
	if error != OK:
		push_error("An error occured in the HTTP request.")

func _ready():
	#image_url = self.controller.full_hostname + "/files/out_00000"
	pass

func _image_refreshed(result, response_code, headers, body):
	print(result)

func _http_request_completed(result, response_code, headers, body):
	var image = Image.new()
	var image_error = image.load_png_from_buffer(body)
	if image_error != OK:
		print("An error occurred while trying to display the image.")
	var new_texture = ImageTexture.new()
	new_texture.create_from_image(image)
	self.texture_normal = new_texture


func send_to_server():
	print("begin")
	var image = self.texture.get_data()
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
		"x-api-key: " + self.controller.api_key
	]
	var http = HTTPClient.new()
	print(self.controller.hostname)
	print(self.controller.port)
	http.connect_to_host(self.controller.hostname, -1, self.controller.use_ssl)

	while http.get_status() == HTTPClient.STATUS_CONNECTING or http.get_status() == HTTPClient.STATUS_RESOLVING:
		http.poll()
		OS.delay_msec(500)
	assert(http.get_status() == HTTPClient.STATUS_CONNECTED) # Could not connect
	var err = http.request_raw(HTTPClient.METHOD_POST, "/refreshimage" , headers, body)
	assert(err == OK) # Make sure all is OK.
	while http.get_status() == HTTPClient.STATUS_REQUESTING:
		# Keep polling for as long as the request is being processed.
		http.poll()
		
	if http.has_response():
		# If there is a response...

		headers = http.get_response_headers_as_dictionary() # Get response headers.
		print("code: ", http.get_response_code()) # Show response code.
		print("**headers:\\n", headers) # Show headers.
		if http.is_response_chunked():
			print("Response is Chunked!")
		else:
			# Or just plain Content-Length
			var bl = http.get_response_body_length()
			print("Response Length: ", bl)
			# This method works for both anyway
		var rb = PoolByteArray() # Array that will hold the data.
		while http.get_status() == HTTPClient.STATUS_BODY:
			# While there is body left to be read
			http.poll()
			# Get a chunk.
			var chunk = http.read_response_body_chunk()
			if chunk.size() == 0:
				if not OS.has_feature("web"):
					# Got nothing, wait for buffers to fill a bit.
					OS.delay_usec(1000)
				else:
					yield(Engine.get_main_loop(), "idle_frame")
			else:
				rb = rb + chunk # Append to read buffer.

		print("bytes got: ", rb.size())
		var data = rb.get_string_from_utf8()
		data = Marshalls.base64_to_raw(data)
		var new_image = Image.new()
		#var decoded_image = Marshalls.base64_to_raw(data)
		var image_error = image.load_png_from_buffer(data)
		if image_error != OK:
			print("An error occurred while trying to display the image.")
		var new_texture = ImageTexture.new()
		new_texture.create_from_image(image)
		self.texture = new_texture
	else:
		print("no response")


func _on_Timer_timeout():
	send_to_server()
