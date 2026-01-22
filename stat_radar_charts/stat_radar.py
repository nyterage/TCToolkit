import plotly.graph_objects as go
import os
import sys

# Sets the color of the chart data
wow_class = "death_knight"
# Only used for file name outputs, makes it easier to find the output later
specilization = "frost"

# Circular and Linear are the only two options for shape
shape='linear'

# Set your ratings here
crit_rating = 17278
haste_rating = 19522
mastery_rating = 20994
vers_rating = 0

# Set the background color of the chart, wowhead grey is #242424
background_color = '#181818'
font_size = 36
graph_width = 1150
graph_height = 1000

class_colors = {
    "death_knight": "#C41E3A",
    "druid": "#FF7C0A",
    "demon_hunter": "#A330C9",
    "evoker": "#33937F",
    "hunter": "#AAD372",
    "mage": "#3FC7EB",
    "monk": "#00FF98",
    "paladin": "#F58CBA",
    "priest": "#FFFFFF",
    "rogue": "#FFF468",
    "shaman": "#0070DE",
    "warlock": "#8788EE",
    "warrior": "#C69B6D"
}

default = "#000000"
class_color = class_colors.get(wow_class, default)

fig = go.Figure(data=go.Scatterpolar(
  r=[crit_rating,haste_rating,mastery_rating,vers_rating],
  theta=['Critical Strike','Haste','Mastery','Versatility'],
  fill='toself',
  marker_color=class_color,
  opacity=0.8,
))

fig.update_layout(
  plot_bgcolor=background_color,
  paper_bgcolor=background_color,
  width=graph_width,
  height=graph_height,
  margin=dict(
    l=150,
    r=200,
    b=75,
    t=75
  ),
  polar=dict(
    radialaxis=dict(
      visible=True,
      tickfont=dict(
        color='white',
        size=font_size * 0.5
      ),
    ),
    angularaxis=dict(
      visible=True,
      rotation=90,
      tickfont=dict(
        color='white',
        size=font_size,
      )
    ),
    bgcolor='rgba(255,255,255,0.2)',
    gridshape=shape,
  ),
  showlegend=False
)

chart_output_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "chart_output")
fig.write_image(os.path.join(chart_output_dir,f'{wow_class}_{specilization}_stat_radar.png'))
fig.show()