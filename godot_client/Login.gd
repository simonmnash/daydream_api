extends Panel

const client = preload("res://HTTPClientExample/Client.tscn")
const websocket_client = preload("res://WebSocketClientExample/WebSocketClient.tscn")
func _ready():
	pass # Replace with function body.



func _on_Connect_pressed():
	var host = $CenterContainer/VBoxContainer/Host/Host.text
	var port = $CenterContainer/VBoxContainer/Port/Port.text
	var key = $CenterContainer/VBoxContainer/Key/Key.text
	var new_client = client.instance()
	new_client.hostname = host
	new_client.port = port
	new_client.api_key = key
	$CenterContainer.hide()
	self.add_child(new_client)
	
