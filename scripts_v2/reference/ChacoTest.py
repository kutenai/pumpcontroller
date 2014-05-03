#!/usr/bin/env python

from enthought.traits.api \
    import HasTraits, Int, Range, Array, Enum, on_trait_change
from enthought.traits.ui.api import View, Item
from enthought.chaco.chaco_plot_editor import ChacoPlotItem


class Hyetograph(HasTraits):
    """ Creates a simple hyetograph demo. """
    timeline = Array
    intensity = Array
    nrcs = Array
    duration = Int(12, desc='In Hours')
    year_storm = Enum(2, 10, 25, 100)
    county = Enum('Brazos', 'Dallas', 'El Paso', 'Harris')
    curve_number = Range(70, 100)
    plot_type = Enum('line', 'scatter')

    view1 = View(Item('plot_type'),
                 ChacoPlotItem('timeline', 'intensity',
                               type_trait='plot_type',
                               resizable=True,
                               x_label='Time (hr)',
                               y_label='Intensity (in/hr)',
                               color='blue',
                               bgcolor='white',
                               border_visible=True,
                               border_width=1,
                               padding_bg_color='lightgray'),
                 Item(name='duration'),
                 Item(name='year_storm'),
                 Item(name='county'),

                 # After infiltration using the nrcs curve number method.
                 ChacoPlotItem('timeline', 'nrcs',
                                type_trait='plot_type',
                                resizable=True,
                                x_label='Time',
                                y_label='Intensity',
                                color='blue',
                                bgcolor='white',
                                border_visible=True,
                                border_width=1,
                                padding_bg_color='lightgray'),
                Item('curve_number'),
                resizable = True,
                width=800, height=800)


    def calculate_intensity(self):
        """ The Hyetograph calculations. """
        # Assigning A, B, and C values based on year, storm, and county
        counties = {'Brazos': 0, 'Dallas': 3, 'El Paso': 6, 'Harris': 9}
        years = {
            2 : [65, 8, .806, 54, 8.3, .791, 24, 9.5, .797, 68, 7.9, .800],
            10: [80, 8.5, .763, 78, 8.7, .777, 42, 12., .795,81, 7.7, .753],
            25: [89, 8.5, .754, 90, 8.7, .774, 60, 12.,.843, 81, 7.7, .724],
            100: [96, 8., .730, 106, 8.3, .762, 65, 9.5, .825, 91, 7.9, .706]
        }
        year = years[self.year_storm]
        value = counties[self.county]
        a, b, c = year[value], year[value+1], year[value+2]

        self.timeline=range(2, self.duration + 1, 2)
        intensity=a / (self.timeline * 60 + b)**c
        cumdepth=intensity * self.timeline

        temp=cumdepth[0]
        result=[]
        for i in cumdepth[1:]:
            result.append(i-temp)
            temp=i
        result.insert(0,cumdepth[0])

        # Alternating block method implementation.
        result.reverse()
        switch = True
        o, e = [], []
        for i in result:
            if switch:
                o.append(i)
            else:
                e.append(i)
            switch = not switch
        e.reverse()
        result = o + e
        self.intensity = result


    def calculate_runoff(self):
        """ NRCS method to get run-off based on permeability of ground. """
        s = (1000 / self.curve_number) - 10
        a = self.intensity - (.2 * s)
        vr = a**2 / (self.intensity + (.8 * s))
        # There's no such thing as negative run-off.
        for i in range(0, len(a)):
            if a[i] <= 0:
                vr[i] = 0
        self.nrcs = vr


    @on_trait_change('duration, year_storm, county, curve_number')
    def _perform_calculations(self):
        self.calculate_intensity()
        self.calculate_runoff()


    def start(self):
        self._perform_calculations()
        self.configure_traits()


f=Hyetograph()
f.start()