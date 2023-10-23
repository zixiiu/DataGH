import sys
from tkinter import filedialog

import numpy as np
import pandas as pd
from PyQt5 import QtGui

from vispy import scene, app
from vispy.scene import visuals, PanZoomCamera
from vispy.visuals.text.text import FontManager
from vispy.visuals.transforms import TransformSystem

from Fitter import Fitter
from lasso_select import select

from multiprocessing import freeze_support

import logging

logging.basicConfig(level=logging.INFO)
# set log format to console logger as time:level:message
logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))


class VispyApp:
    def __init__(self):
        self.df = None
        self.canvas = None
        self.fitter = None
        # mouse move
        # self.pointer = None
        self.px = 0
        self.py = 0
        # s
        self.view = None
        self.transform = TransformSystem()
        self.ctr = None
        # lasso tools
        self.point_color = None
        self.data = None

        self._test_name_map = {0: 'SC: File Compression',
                               1: 'SC: Navigation',
                               2: 'SC: HTML5 Browser',
                               3: 'SC: PDF Renderer',
                               4: 'SC: Photo Library',
                               5: 'SC: CLang',
                               6: 'SC: Text Processing',
                               7: 'SC: Assert Compression',
                               8: 'SC: Object Detection',
                               9: 'SC: Background Blur',
                               10: 'SC: Horizon Detection',
                               11: 'SC: Object Remover',
                               12: 'SC: HDR',
                               13: 'SC: Photo Filter',
                               14: 'SC: Ray Tracer',
                               15: 'SC: Structure from Motion',
                               16: 'MC: File Compression',
                               17: 'MC: Navigation',
                               18: 'MC: HTML5 Browser',
                               19: 'MC: PDF Renderer',
                               20: 'MC: Photo Library',
                               21: 'MC: CLang',
                               22: 'MC: Text Processing',
                               23: 'MC: Assert Compression',
                               24: 'MC: Object Detection',
                               25: 'MC: Background Blur',
                               26: 'MC: Horizon Detection',
                               27: 'MC: Object Remover',
                               28: 'MC: HDR',
                               29: 'MC: Photo Filter',
                               30: 'MC: Ray Tracer',
                               31: 'MC: Structure from Motion'
                               }

        # graph element
        self.graph_element = []
        self.font_manager = FontManager(method='gpu')

        # Large Font Special
        self._font_size = 16 # 16 is normal
        # self._font_size = 48
        self._x_axis_font_size = 12 # 12 is normal
        # self._x_axis_font_size = 36

    def read_data(self, path='data/D9200 1920 5150.csv'):
        # self.df = pd.read_csv(path)
        self.fitter = Fitter()
        self.fitter.load_data(path)
        self.df = self.fitter.df

    def _init_canvas(self):
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor=(0.1, 0.1, 0.1, 1))
        canvas = self.canvas
        # canvas.measure_fps()
        times = self.df['Time (s)'].values
        powers = self.df['Main Avg Power (W)'].values
        data = np.column_stack([times, powers])
        self.data = data

        grid = canvas.central_widget.add_grid(margin=0)
        grid.spacing = 0

        title = scene.Label("GB6 Power Filter(ctrl+R: Remove, ctrl+A: Add, ctrl+D: Deselect, ctrl+S: Save, I: Insert Segment, O: Remove Segment)",
                            color='white', font_size=self._font_size, font_manager=self.font_manager)
        title.height_max = 40
        grid.add_widget(title, row=0, col=0, col_span=2)

        yaxis = scene.AxisWidget(orientation='right', font_size=self._x_axis_font_size)
        yaxis.width_max = 0
        grid.add_widget(yaxis, row=1, col=0)

        xaxis = scene.AxisWidget(orientation='top', font_size=self._x_axis_font_size)

        xaxis.height_max = 0
        grid.add_widget(xaxis, row=2, col=1)

        # right_padding = grid.add_widget(row=1, col=2, row_span=1)
        # right_padding.width_max = 50

        view = grid.add_view(row=1, col=1, border_color='white')

        # self.pointer = scene.visuals.Ellipse(center=(0., 0.), radius=(1, 1), color=None,
        #                                      border_width=0.2,
        #                                      border_color="white",
        #                                      num_segments=10, parent=view.scene)

        # before the scatter:
        for idx in range(32):
            start, end = self.fitter.get_seg_pair(idx)
            lr = scene.LinearRegion([self.df.iloc[start]['Time (s)'], self.df.iloc[end]['Time (s)']],
                                    [0.4, 0.4, 0.4, 0.5],
                                    vertical=True,
                                    parent=view.scene)
            self.graph_element.append([lr])

        # add data
        self.selected_mask = np.full(len(data), False)
        ## red if idx in self.fitter.rm_idx
        self.rm_mask = np.full(len(data), False)
        self.rm_mask[list(self.fitter.rm_idx)] = True
        # self.point_color = np.full((len(data), 4), (0, 0, 1, 1))
        self.scatter = visuals.Markers()
        self.reset_point_color()
        view.add(self.scatter)

        for idx in range(32):
            start, end = self.fitter.get_seg_pair(idx)
            nlevel = max(self.df.iloc[start:end]['Main Avg Power (W)'].values)
            ntext = scene.Text('%i, %s' % (idx + 1, self._test_name_map[idx]),
                               pos=(self.df.iloc[start]['Time (s)'], nlevel),
                               color='white', parent=view.scene,
                               rotation=270., anchor_x='left', anchor_y='top',
                               font_manager=self.font_manager, font_size=self._font_size)
            # ntext = None
            avg = self.fitter.seg_average[idx]
            atext = scene.Text('%.2f' % avg, pos=(self.df.iloc[end]['Time (s)'], avg), color='white', parent=view.scene,
                               anchor_x='left', anchor_y='top', font_manager=self.font_manager, font_size=self._font_size)
            # atext = None
            aline = scene.Line(
                pos=np.array([[self.df.iloc[start]['Time (s)'], avg], [self.df.iloc[end]['Time (s)'], avg]]),
                color=(0, 1, 0, 1), parent=view.scene, width=2)
            self.graph_element[idx].extend([ntext, aline, atext])

        # set camera
        view.camera = PanZoomCamera()
        view.camera.set_range((0, 350), (0, 25), margin=0)
        view.add(visuals.GridLines())

        xaxis.link_view(view)
        yaxis.link_view(view)

        # set transform
        self.view = view

        # set lasso
        self.lasso = scene.visuals.Line(pos=np.array([[0, 0], [0, 0]]), color=(1, 0, 0), parent=view.scene,
                                        width=1, antialias=True)

        @canvas.connect
        def on_key_press(event):
            modifiers = [key.name for key in event.modifiers]
            logging.debug('Key pressed - text: %r, key: %s, modifiers: %r' % (
                event.text, event.key.name, modifiers))
            # ctrl + d
            if 'Control' in modifiers and event.key.name == 'D':
                self.selected_mask = np.full(len(data), False)
                self.reset_point_color()
                self.lasso.set_data(pos=np.empty((1, 2)))
            # ctrl + r
            if 'Control' in modifiers and event.key.name == 'R':
                self.rm_mask = np.logical_or(self.selected_mask, self.rm_mask)
                logging.info('rm %d points' % np.count_nonzero(self.rm_mask))
                self.selected_mask = np.full(len(data), False)
                self.reset_point_color()
                self.lasso.set_data(pos=np.empty((1, 2)))
                self.reset_avg_bar()
            # ctrl + a
            if 'Control' in modifiers and event.key.name == 'A':
                self.rm_mask[self.selected_mask] = False
                logging.info('added %d points' % np.count_nonzero(self.rm_mask))
                self.selected_mask = np.full(len(data), False)
                self.reset_point_color()
                self.lasso.set_data(pos=np.empty((1, 2)))
                self.reset_avg_bar()
            # ctrl + s
            if 'Control' in modifiers and event.key.name == 'S':
                self.fitter.save_df_to_file()
                logging.info('saved to %s' % self.fitter.path)
            # i
            if event.key.name == 'I':
                start, end = self.selected_mask.nonzero()[0][[0, -1]]
                self.fitter.add_seg(start, end)
                self.replot_graph_element()
            # o
            if event.key.name == 'O':
                start, end = self.selected_mask.nonzero()[0][[0, -1]]
                rm_idxes = self.fitter.get_seg_idxes_by_range(start, end)
                for idx in sorted(rm_idxes, reverse=True):
                    self.fitter.rm_seg(idx)
                self.replot_graph_element()




        @canvas.connect
        def on_mouse_press(event):
            # global point_color, selected_mask

            if event.button == 3:
                # Reset lasso state.
                self.lasso.set_data(pos=np.empty((1, 2)))

                # Reset selected vertices to the filtered color, this would earn some time in case
                # scene contains a lot of vertices.
                self.point_color = np.full((len(self.data), 4), (0, 0, 1, 1))

                # scatter.set_data(pos, edge_width=0, face_color=self.print_color, size=SCATTER_SIZE)

        @canvas.connect
        def on_mouse_move(event):
            pp = event.pos
            ppx = (pp[0] - 40, pp[1] - 40)
            # Optimization: to avoid too much recalculation/update we can update scene only if the mouse
            # moved a certain amount of pixel.
            if (abs(self.px - pp[0]) > 5 or abs(self.py - pp[1]) > 5):
                # pp2 = self.view.camera.transform.imap(ppx)[:2]
                # aspect = self.view.camera.aspect
                # self.pointer.radius = (1, 1/aspect)
                # self.pointer.center = pp2
                self.px, self.py = pp
                if event.button == 3:
                    polygon_vertices = event.trail()
                    pvx = [self.view.camera.transform.imap((p[0], p[1] - 40))[:2] for p in polygon_vertices]
                    self.lasso.set_data(
                        pos=np.insert(pvx, len(pvx), pvx[0], axis=0))

        @canvas.connect
        def on_mouse_release(event):

            if event.button == 3:
                self.selected_mask = select(event.trail(), self.data, self.scatter)
                self.reset_point_color()

    def sync_rm_mask(self):
        self.fitter.rm_idx = set(np.where(self.rm_mask)[0])

    def replot_graph_element(self):
        for idx, (lr, ntext, aline, atext) in enumerate(self.graph_element):
            start, end = self.fitter.get_seg_pair(idx)
            lr.set_data(pos=np.array([self.df.iloc[start]['Time (s)'], self.df.iloc[end]['Time (s)']]))
            ntext.text = '%i, %s' % (idx + 1, self._test_name_map[idx])
            nlevel = max(self.df.iloc[start:end]['Main Avg Power (W)'].values)
            ntext.pos = (self.df.iloc[start]['Time (s)'], nlevel)
        self.reset_avg_bar()
    def reset_avg_bar(self):
        self.sync_rm_mask()
        self.fitter.recalculate_avg()
        for idx, (_, _, aline, atext) in enumerate(self.graph_element):

            avg = self.fitter.seg_average[idx]
            start, end = self.fitter.get_seg_pair(idx)
            aline.set_data(pos=np.array([[self.df.iloc[start]['Time (s)'], avg], [self.df.iloc[end]['Time (s)'], avg]]))

            atext.text = '%0.2f' % avg
            atext.pos = (self.df.iloc[end]['Time (s)'], avg)

    def reset_point_color(self):
        self.point_color = np.full((len(self.data), 4), (0, 0.6, 1, 1))  # blue
        self.point_color[self.rm_mask] = (1, 0, 0, 1)  # red
        self.point_color[self.selected_mask] = (1, 1, 0, 1)  # yellow
        self.scatter.set_data(self.data, edge_width=0, face_color=self.point_color, size=5)

    def start(self):
        self._init_canvas()
        app.run()


if __name__ == '__main__':
    freeze_support()
    vapp = VispyApp()
    file_path = filedialog.askopenfilename()
    recal_yn = input('Recalculate Segments? (y/n)')
    vapp.read_data(file_path)
    if recal_yn == 'y' or recal_yn == 'Y':
        th_lo = float(input('th_lo(1.5):') or 1.5)
        th_hi = float(input('th_hi(2.5):') or 2.5)
        avg_lo = int(input('avg_lo(200):') or 200)
        avg_hi = int(input('avg_hi(300):') or 300)
        rest_lo = float(input('rest_lo(2.0):') or 2.0)
        rest_hi = float(input('rest_hi(3.0):') or 3.0)
        vapp.fitter.det_seg(th_lo, th_hi, avg_lo, avg_hi, rest_lo, rest_hi)
    vapp.fitter.load_seg_from_df()
    vapp.start()
