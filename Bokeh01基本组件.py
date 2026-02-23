# Step 1: basic concept 
# (1) Figure
from bokeh.plotting import figure

p = figure(title = "My First Plot",
           x_axis_label = "X",
           y_axis_label = "Y",
           width = 600,
           height = 400
           )

# line
# p.line([1,2,3], [4,5,6], line_width=3, color="blue", legend_label = "My line")

x = [1,2,3]
y = [4,5,6]

# Scatter
# p.scatter(x, y, size=8, color="red")

# Show:
from bokeh.plotting import show, output_file
# output_file("plot.html")
# show(p) # output_file("plot.html") 必须在 show(p) 之前，否则 show() 不会输出到那个 html

#(5) Column Data Scource
from bokeh.models import ColumnDataSource

source = ColumnDataSource( data=dict(x=x,
                                        y=y,
                                        label = ["A", "B", "C"]
                                        ))


p.line('x', 'y', source = source)

#Hover Tool 鼠标悬停显示数据
from bokeh.models import HoverTool

hover = HoverTool(tooltips=[
    ('X value', '@x'),
    ('Y value', '@y')
])

p.add_tools(hover)

output_file("plot.html")
show(p) # output_file("plot.html") 必须在 show(p) 之前，否则 show() 不会输出到那个 html
