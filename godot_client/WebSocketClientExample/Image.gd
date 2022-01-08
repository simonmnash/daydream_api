extends Sprite

export var prompt: String = "Night Sky"
signal selected(image_selected)

var can_grab = false
var grabbed_offset = Vector2()


func _ready():
	pass

func _on_Area2D_input_event(viewport, event, shape_idx):
	if event is InputEventMouseButton:
		can_grab = event.pressed
		grabbed_offset = position - get_global_mouse_position()
		if event.pressed:
			self.emit_signal("selected", self)


func _process(delta):
	if Input.is_mouse_button_pressed(BUTTON_LEFT) and can_grab:
		position = get_global_mouse_position() + grabbed_offset
