extends Sprite

export var prompt: String = "Night Sky"
signal selected(image_selected)
func _ready():
	pass

func _on_Area2D_input_event(viewport, event, shape_idx):
	if (event is InputEventMouseButton && event.pressed):
		self.emit_signal("selected", self)
