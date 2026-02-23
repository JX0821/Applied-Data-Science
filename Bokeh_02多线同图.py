from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool

output_file("multi_line.html")

source = ColumnDataSource(data = dict(
    epoch=[1,2,3,4],
    model_A=[0.6,0.7,0.75,0.8],
    model_B=[0.5,0.55,0.6,0.65]
))

p = figure(title='Model Accuracy Over Epoch',
           x_axis_label="Epoch",
           y_axis_label="Accuracy",
           width=700,
           height=400)

lineA = p.line('epoch', 'model_A', source=source,
               color='blue', line_width=2, legend_label='Model A')

lineB = p.line('epoch', 'model_B', source=source, 
               color='red', line_width=2, legend_label='Model B')

hover = HoverTool(
    renderers=[lineA, lineB],
    tooltips=[
              ('epoch', '@epoch'),
              ('model_A', '@model_A'),
              ('model_B', '@model_B')
              ]
)

p.add_tools(hover)
p.legend.location='top_left' #legend 是图例
show(p)