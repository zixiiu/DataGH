import numpy as np
import pandas as pd
from vispy import scene
from vispy.scene import visuals, AxisWidget, cameras
import consts


class CustomPanZoomCamera(cameras.PanZoomCamera):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._box = None

    def _on_mouse_move(self, event):
        if event.button == 1:  # Left button
            if self._box is None:
                self._box = visuals.Rectangle(center=event.pos, color=(1, 0, 0, 0.5))
                self.view.add(self._box)
            self._box.center = event.pos
        elif event.button == 2:  # Middle button
            super()._on_mouse_move(event)

    def _on_mouse_press(self, event):
        if event.button == 1:
            if self._box:
                self.view.remove(self._box)
                self._box = None
        elif event.button == 2:
            super()._on_mouse_press(event)

# Load the CSV
df = pd.read_csv('data/D9200 1918 5143.csv')

# Extract the data
times = df[consts.time_col_name].values
powers = df[consts.power_col_name].values

canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='white')
view = canvas.central_widget.add_view()

data = np.column_stack([times, powers])

# Create a scatter plot
scatter = visuals.Markers()
scatter.set_data(data, face_color=(0, 0, 1, 0.8), edge_width=0, size=5)
view.add(scatter)

# Configure the view
# view.camera = 'panzoom'
# view.camera.aspect_ratio = 1
view.camera = CustomPanZoomCamera()
view.camera.set_range()

# Show the canvas
canvas.app.run()
