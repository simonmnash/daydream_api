extends Node

# The URL we will connect to
var websocket_url = ""
export var generate_embeddings_endpoint: String
export var api_key: String
# Our WebSocketClient instance
var _client = WebSocketClient.new()

export var hostname: String
export var port: String
export var use_ssl: bool

func _ready():
	self.websocket_url = "wss://" + hostname + "/generation_stream"
	if use_ssl:
		self.generate_embeddings_endpoint = "https://" + hostname + "/generate_embeddings"
	else:
		self.generate_embeddings_endpoint = "http://" + hostname + ":" + port + "/generate_embeddings"
	# Connect base signals to get notified of connection open, close, and errors.
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	# This signal is emitted when not using the Multiplayer API every time
	# a full packet is received.
	# Alternatively, you could check get_peer(1).get_available_packets() in a loop.
	_client.connect("data_received", self, "_on_data")

	# Initiate connection to the given URL.
	var err = _client.connect_to_url(websocket_url, [], false, ["x-api-key: " + self.api_key])
	if err != OK:
		print("Unable to connect")
		set_process(false)


func _closed(was_clean = false):
	# was_clean will tell you if the disconnection was correctly notified
	# by the remote peer before closing the socket.
	print("Closed, clean: ", was_clean)
	set_process(false)

func current_texture_to_base64_packet():
	var group = $Group
	var current_image_bytes = $Group.current_image.texture.get_data().save_png_to_buffer()
	var base64 = Marshalls.raw_to_base64(current_image_bytes)
	return base64.to_utf8()

func _connected(proto = ""):
	# This is called on connection, "proto" will be the selected WebSocket
	# sub-protocol (which is optional)
	print("Connected with protocol: ", proto)
	# You MUST always use get_peer(1).put_packet to send data to server,
	# and not put_packet directly when not using the MultiplayerAPI.
	
	var current_image_bytes = $Group.current_image.texture.get_data().save_png_to_buffer()
	var base64 = Marshalls.raw_to_base64(current_image_bytes)
	_client.get_peer(1).set_write_mode(WebSocketPeer.WRITE_MODE_TEXT)
	_client.get_peer(1).put_packet(current_texture_to_base64_packet())

func _on_data():
	# Print the received packet, you MUST always use get_peer(1).get_packet
	# to receive data from server, and not get_packet directly when not
	# using the MultiplayerAPI.
	var data = _client.get_peer(1).get_packet().get_string_from_utf8()
	data = Marshalls.base64_to_raw(data)
	var image = Image.new()
	#var decoded_image = Marshalls.base64_to_raw(data)
	var image_error = image.load_png_from_buffer(data)
	if image_error != OK:
		print("An error occurred while trying to display the image.")
	var new_texture = ImageTexture.new()
	new_texture.create_from_image(image)
	if not $Group.switch:
		$Group.current_image.texture = new_texture
	_client.get_peer(1).put_packet(current_texture_to_base64_packet())
	$Group.switch = false

func _process(delta):
	# Call this in _process or _physics_process. Data transfer, and signals
	# emission will only happen when calling this function.
	_client.poll()

func _on_NewImage_pressed():
	$Group.add_new_image($Controls/NewPrompt.text)


func _on_Group_image_selected(image):
	$Controls/SavePrompt.text = image.prompt
	for child in $Group.get_children():
		child.get_node("Highlight").hide()
	image.get_node("Highlight").show()
	
	var request = HTTPRequest.new()
	var query = JSON.print({"prompt": image.prompt})
	add_child(request)
	var error = request.request(self.generate_embeddings_endpoint, ["Content-Type: application/json", "x-api-key: " + self.api_key], self.use_ssl, HTTPClient.METHOD_POST, query)
	if error != OK:
		push_error("An error occured in the HTTP request.")


func _on_Canvas_fireaway(buffer, position):
	var new_image = $Group.add_new_image("Man is in love")
	var image  = Image.new()
	image.load_png_from_buffer(buffer)
	new_image.texture = image
	new_image.position = position - Vector2(595, 456) + Vector2(64, 64)
	var last_image = $Group.current_image
	$Group.current_image = new_image
	$Group.switch = true

