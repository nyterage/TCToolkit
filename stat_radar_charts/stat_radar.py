import plotly.graph_objects as go
import os
import sys

# Sets the color of the chart data
wow_class = "death_knight"
# Only used for file name outputs, makes it easier to find the output later
specilization = "unholy"

# Circular and Linear are the only two options for shape
shape='circular'

# Set your ratings here
crit_rating = 1586
haste_rating = 21666
mastery_rating = 23076
vers_rating = 699

# Set the background color of the chart, wowhead grey is #242424
background_color = '#242424'
font_size = 50
graph_width = 2300
graph_height = 2000

# Create the variable with a sensable default value so even if the class is not found, it will still work
class_color = '#C41E3A'

match( wow_class ):
  case "death_knight":
    class_color = '#C41E3A'
  case "druid":
    class_color = '#FF7C0A'
  case "demon_hunter":
    class_color = '#A330C9'
  case "evoker":
    class_color = '#33937F'
  case "hunter":
    class_color = '#AAD372'
  case "mage":
    class_color = '#3FC7EB'
  case "monk":
    class_color = '#00FF98'
  case "paladin":
    class_color = '#F58CBA'
  case "priest":
    class_color = '#FFFFFF'
  case "rogue":
    class_color = '#FFF468'
  case "shaman":
    class_color = '#0070DE'
  case "warlock":
    class_color = '#8788EE'
  case "warrior":
    class_color = '#C69B6D'

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
    l=200,
    r=200,
    b=200,
    t=200
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
      tickfont=dict(
        color='white',
        size=font_size
      )
    ),
    bgcolor='rgba(255,255,255,0.2)',
    gridshape=shape
  ),
  showlegend=False
)

chart_output_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "chart_output")
fig.write_image(os.path.join(chart_output_dir,f'{wow_class}_{specilization}_stat_radar.png'))
fig.show()