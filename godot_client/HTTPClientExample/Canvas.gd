extends Area2D

var mouse_pos = Vector2()
var dragging = false
var drag_start = Vector2.ZERO

var rectangle = Rect2()
var rectangle_size = Vector2(128, 128)
var avaliable_sizes = [Vector2(32, 32),
					   Vector2(64, 64),
					   Vector2(128, 128),
					   Vector2(256, 256),
					   Vector2(512, 512)]
var size_index = 2
var current_selection_buffer = null
export var debug = false

signal fireaway(buffer, position)

func _draw():
	draw_rect(rectangle, Color(.9,.3,.3, 1), false)


func _on_Canvas_input_event(viewport, event, shape_idx):
	if event is InputEventMouseButton:
		if event.pressed:
			if event.button_index == BUTTON_WHEEL_UP:
				pass
			#if event.button_index == BUTTON_WHEEL_UP:
			#	self.size_index += 1
			#	self.size_index = self.size_index % (len(avaliable_sizes)) 
			#	self.rectangle_size = avaliable_sizes[self.size_index]
			#elif event.button_index == BUTTON_WHEEL_DOWN:
			#	self.size_index -= 1
			#	self.size_index = self.size_index % (len(avaliable_sizes))
			#	self.rectangle_size = avaliable_sizes[self.size_index]
			else:
				var rect_pos = (get_viewport_transform() * (get_global_transform() * rectangle.position))
				rectangle = Rect2(0, 0, 0, 0)
				update()
				var img = get_viewport().get_texture().get_data()
				img.flip_y()
				current_selection_buffer = img.get_rect(Rect2(rect_pos, Vector2(128, 128))).save_png_to_buffer()
				if not debug:
					emit_signal("fireaway", current_selection_buffer, drag_start)
	
		rectangle = Rect2(drag_start- Vector2(600, 450), self.rectangle_size).abs()
		update()
			
	if event is InputEventMouseMotion:
		drag_start = event.position
		rectangle = Rect2(drag_start- Vector2(600, 450), self.rectangle_size).abs()
		update()

