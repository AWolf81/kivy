'''
Styles
=========

.. versionadded:: 

This module implements stlyes that can be mixed with existing base widgets.
For example, if you want to add a "border" style to an `Image`, you could
do::


    class BorderImage(Image, BorderStyle):
        pass

.. note::

'''

__all__ = ('BorderStyle')

from kivy.properties import NumericProperty, ReferenceListProperty,\
    ListProperty
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from math import fabs

class BorderStyle(Widget):
    '''
    Adds a border to every Widget (e.g Button, Label, Scatter etc.)

    :Parameters:
        `border`: list
            Short form to initialize the border with the following format:
            [border_width, border_style, border_color]
        `border_width`: float
            Size of border in pixels
        `border_style`: list
            'dashed', 'dotted', 'solid' to change the look of the border
            >> only working for border_width = 1.0
               (see :class:`~kivy.graphics.Line(VertexInstruction) comment 
                on line 43)
            TODO: add option for tuple (dash_length, dash_offset)
        `border_color`: tuple
            RGBA value for the color of the border

    Use in kv with:
    <BorderButton@Button+BorderStyle>:
        borders: 10, 'solid', (1,1,1,1.)

    Negative borders are allowed. But notice the border is not with-in
    the collide_point area of the widget. It will be drawn around the widget
    and it's probably drawn below other widgets.

    if border_width = 0 no border will be drawn

    '''
    border_width = NumericProperty(1.)
    border_color = ListProperty([1,1,1,1])
    borders = ListProperty([border_width, 'solid', border_color])
    _border_origin_x = NumericProperty(0.)
    _border_origin_y = NumericProperty(0.)
    _border_origin = ReferenceListProperty(_border_origin_x, _border_origin_y)
    _border_lines = None

    _INIT_STATE = False # if False then Border not initialized yet 
    
    # Line styling attributes
    CAP = 'square'
    JOINT = 'miter'

    _dash_styles = {
        'dashed':
        {
            'dash_length': 10,
            'dash_offset': 5
        },
        'dotted':
        {
            'dash_length': 1,
            'dash_offset': 1
        },
        'solid':
        {
            'dash_length': 1,
            'dash_offset': 0
        }
    }

    def __init__(self, **kwargs):
        super(BorderStyle, self).__init__(**kwargs)
        border_width = kwargs.get('border_width')
        self.border_width = border_width if border_width else 1.
        border_style = kwargs.get('border_style')
        self.border_style = border_style if border_style else  'solid'
        self.cur_dash_style = self._dash_styles[self.border_style]
        border_color = kwargs.get('border_color')
        self.border_color = border_color if border_color else (1,1,1,1.) 

    def _draw_border(self):
        line_kwargs = {
            'rectangle': [0,0,0,0],
            'width': self.border_width,
            'cap': self.CAP,
            'joint': self.JOINT,
            'dash_length': self.cur_dash_style['dash_length'],
            'dash_offset': self.cur_dash_style['dash_offset']
        }

        with self.canvas.after:
            self._border_color = Color(*self.border_color)
            self._border_lines = Line(**line_kwargs)

    def _update_borders(self):
        width = self.border_width
        dbl_width = 2 * width

        if self._border_lines:
            self._border_lines.rectangle = [
               self._border_origin_x,
               self._border_origin_y,
               self.size[0] - dbl_width,
               self.size[1] - dbl_width
            ]

    def set_border_origin(self):
        self._border_origin_x = self.pos[0] + self.border_width
        self._border_origin_y = self.pos[1] + self.border_width

    def on__border_origin(self, instance, value):
        self._update_borders()
        if not self._INIT_STATE:
            self._INIT_STATE = True
            self._draw_border()

    def on_size(self, instance, value):
        # this is required if the element with border is resized e.g. on
        # window resize with a relative size
        self.set_border_origin()
        self.pos = self._border_origin
        
        if not self._INIT_STATE:
            self._INIT_STATE = True
            self._draw_border()

    def on_pos(self, instance, value):
        self.set_border_origin()

    def on_borders(self, instance, value):
        self.border_width, self.border_style, self.border_color = value
            
        self.cur_dash_style = self._dash_styles[self.border_style]
        self.set_border_origin()

    def on_border_width(self, instance, value):
        # print value, "Border changed"
        print self.border_width, "Border width value"
        self.set_border_origin()
        max_width = self.width / 4
        print self._border_lines, "on border"
        if self._border_lines:
            if self.border_width <= max_width:
                if self.border_width > 0:
                    self._border_lines.width = self.border_width
                else:
                    # <= 0 handle negative borders if not 0
                    # --> border is then out side of bounding box
                    if self.border_width != 0:
                        self._border_lines.width = fabs(self.border_width)
                    else:
                        # border_width = 0 --> hide rectangle
                        self._border_lines.rectangle = [0,0,0,0]
            else:
                # limit border to max. value
                self._border_lines.width = max_width
                self.border_width = max_width


if __name__ == '__main__':
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.stacklayout import StackLayout
    # from kivy.uix.image import Image

    Builder.load_string("""
<DemoRootWidget>:
    Label:
        text: 'Normal label'
        size_hint: None, None
        # pos: (100,100)
        width: 200
        height: 100
        canvas.before:
            Color:
                rgba: 0,0,1,1.
            Rectangle:
                pos: self.pos
                size: self.size
    BorderLabel:
        id: _label1
        text: 'Label1'
    BorderLabel:
        text: 'Label2'
        borders: 1, 'dotted', (1,1,1,1.)
    BorderButton:
        text: '+'
        on_press: _label1.border_width+=1
    BorderButton:
        text: '-'
        on_press: _label1.border_width-=1
    BorderLabel:
        text: 'with border_width=0'
        borders: 0, 'solid', (1,1,1,1.)

<BorderButton@Button+BorderStyle>:
    size_hint: None, None
    width: 200
    height: 100
    # border_width: 5
    borders: 5, 'solid', (1,0,0,1)

<BorderLabel@Label+BorderStyle>:
    size_hint: None, None
    borders: 2, 'solid', (1,0,0,1)
    width: 200
    height: 100
    canvas.before:
        Color:
            rgba: 0,0,1,1.
        Rectangle:
            pos: self.pos
            size: self.size
""")


    class DemoRootWidget(StackLayout):
        pass


    class DemoBorderApp(App):
        def build(self):
            return DemoRootWidget()


    DemoBorderApp().run()