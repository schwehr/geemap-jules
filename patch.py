with open("geemap/foliumap.py", "r") as f:
    content = f.read()

content = content.replace("from . import basemaps\nbasemaps = box.Box(basemaps.xyz_to_folium(), frozen_box=True)", """from .basemaps import xyz_to_folium\nbasemaps = box.Box(xyz_to_folium(), frozen_box=True)""")

with open("geemap/foliumap.py", "w") as f:
    f.write(content)
