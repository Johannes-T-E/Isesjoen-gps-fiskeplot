import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
import matplotlib.patheffects as path_effects
from shapely.geometry import LineString, Polygon
import re
from pathlib import Path

def dms_to_decimal(degrees, minutes, seconds, direction):
    """Convert coordinates from degrees-minutes-seconds to decimal degrees"""
    decimal = float(degrees) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_coordinates(line):
    """Parse a line containing a label and coordinates in DMS format"""
    try:
        # Split label and coordinates
        label, coords = line.strip().split(': ', 1)
        
        # Parse coordinates using regex
        pattern = r"(\d+)°(\d+)'([\d.]+)\"([NS])\s+(\d+)°(\d+)'([\d.]+)\"([EW])"
        match = re.search(pattern, coords)
        
        if not match:
            print(f"Warning: Could not parse coordinates in line: {line}")
            return None
            
        # Extract all components
        lat_deg, lat_min, lat_sec, lat_dir = match.group(1, 2, 3, 4)
        lon_deg, lon_min, lon_sec, lon_dir = match.group(5, 6, 7, 8)
        
        # Convert to decimal degrees
        lat = dms_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
        lon = dms_to_decimal(lon_deg, lon_min, lon_sec, lon_dir)
        
        return (label, lat, lon)
    except Exception as e:
        print(f"Error parsing line: {line}")
        print(f"Error details: {str(e)}")
        return None

def read_coordinates_file(file_path):
    """Read and parse all coordinates from the file"""
    coordinates = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    result = parse_coordinates(line)
                    if result:
                        coordinates.append(result)
    except FileNotFoundError:
        print(f"Warning: Coordinates file {file_path} not found.")
    except Exception as e:
        print(f"Error reading coordinates file: {str(e)}")
    
    return coordinates

def create_map(coordinates):
    """Create the map with depth contours and marked locations"""
    # Load the GeoJSON file
    print("Loading GeoJSON file: isesjo_kart.geojson")
    gdf = gpd.read_file("isesjo_kart.geojson")

    # Create a figure with a larger size
    fig, ax = plt.subplots(figsize=(15, 15))

    # Set background color to a nice forest green
    background_color = '#90A955'  # Light forest green
    ax.set_facecolor(background_color)
    fig.patch.set_facecolor(background_color)

    # Define specific depth values and their corresponding colors
    depth_values = [3, 8, 13, 18, 23]  # Specific depth values in meters
    colors = [(0.7, 0.9, 1.0),   # Color for 3m
             (0.6, 0.8, 1.0),   # Color for 8m
             (0.5, 0.7, 0.9),    # Color for 13m
             (0.3, 0.5, 0.8),    # Color for 18m
             (0.1, 0.2, 0.5)]    # Color for 23m

    # Create a discrete colormap
    custom_cmap = ListedColormap(colors)
    bounds = depth_values + [depth_values[-1] + 5]
    norm = BoundaryNorm(bounds, custom_cmap.N)

    # First: Create the shoreline polygon
    main_shoreline = gdf[(gdf['dybde_m'] == 0) & (gdf['objektType'] == 'InnsjoKant')]
    if len(main_shoreline) > 0:
        for _, row in main_shoreline.iterrows():
            if row.geometry.geom_type == 'MultiLineString':
                part0_coords = list(row.geometry.geoms[0].coords)
                part1_coords = list(row.geometry.geoms[1].coords)
                all_coords = part0_coords + part1_coords + [part0_coords[0]]
                shore_polygon = Polygon(all_coords)
                x, y = shore_polygon.exterior.xy
                ax.fill(x, y, facecolor=colors[0], alpha=1)
                ax.plot(x, y, color='black', linewidth=0.5)

    # Second: Plot depth contours
    depth_contours = gdf[gdf['dybde_m'] > 0].sort_values('dybde_m', ascending=True)
    for i, (_, row) in enumerate(depth_contours.iterrows()):
        depth = row['dybde_m']
        closest_depth_idx = min(range(len(depth_values)), 
                              key=lambda i: abs(depth_values[i] - depth))
        color = colors[closest_depth_idx]
        gdf.iloc[[gdf.index.get_loc(row.name)]].plot(ax=ax, facecolor=color, 
                                                    edgecolor=color, linewidth=1, alpha=1)

    # Last: Plot island borders
    island_borders = gdf[(gdf['dybde_m'] == 0) & (gdf['objektType'] == 'ØyInnsjøGrense')]
    if len(island_borders) > 0:
        island_borders.plot(ax=ax, color='black', linewidth=0.5, facecolor=background_color)

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, boundaries=bounds, ticks=depth_values)
    cbar.ax.set_yticklabels([f'{depth}m' for depth in depth_values])
    cbar.ax.set_ylabel('Depth', fontsize=10)

    # Plot coordinates from file with mellow red color and black outline
    mellow_red = '#D35F5F'  # Mellow red color
    for label, lat, lon in coordinates:
        # Plot the marker
        point = ax.plot(lon, lat, 'o', color=mellow_red, markeredgecolor='black', 
                markeredgewidth=1, markersize=6)[0]
        
        # Add annotation attached to the point
        ax.annotate(label,
                   xy=(lon, lat),  # Point to annotate
                   xytext=(0, 10),  # Offset in pixels
                   textcoords='offset points',  # Offset units
                   ha='center',
                   va='bottom',
                   color='white',
                   path_effects=[path_effects.withStroke(linewidth=2, foreground='black')],
                   bbox=dict(facecolor='none', edgecolor='none', pad=2))

    # Set title and labels
    plt.title("Isesjøen - Water Depth Contours")
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, linestyle='--', alpha=0.3)

    return fig, ax

def main():
    # Read coordinates from file
    coordinates_file = Path("coordinates.txt")
    coordinates = read_coordinates_file(coordinates_file)
    
    if coordinates:
        print(f"Found {len(coordinates)} locations in coordinates file")
        
        # Create and display the map
        fig, ax = create_map(coordinates)
        plt.show()
    else:
        print("No valid coordinates found in coordinates file")

if __name__ == "__main__":
    main() 