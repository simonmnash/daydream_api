extends Node

const client = preload("res://HTTPClientExample/Client.tscn")
const websocket_client = preload("res://HTTPClientExample/Client.tscn")
export var default_host: String
export var default_port: int

func _ready():
	pass # Replace with function body.

func _on_Connect_pressed():
	var host = $CenterContainer/VBoxContainer/Host/Host.text
	var port = $CenterContainer/VBoxContainer/Port/Port.text
	var key = $CenterContainer/VBoxContainer/Key/Key.text
	var new_client = websocket_client.instance()
	new_client.hostname = host
	new_client.port = port
	new_client.api_key = key
	$CenterContainer.hide()
	self.add_child(new_client)


func _on_Webconnect_pressed():
	var new_client = websocket_client.instance()
	new_client.hostname = default_host
	new_client.port = default_port
	new_client.api_key = $CenterContainer/VBoxContainer3/LineEdit.text
	$CenterContainer.hide()
	self.add_child(new_client)
