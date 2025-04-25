# Isesjøen Depth Map

An interactive visualization tool for displaying the depth contours of Isesjøen lake and marking fishing spots.

## Features
- Displays depth contours with a color-coded visualization
- Allows marking and labeling of fishing spots
- Interactive map with zoom and pan capabilities
- Easy-to-use coordinate input system

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd isesjo-map
```

2. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install geopandas matplotlib numpy shapely
```

## Usage

### Running the Map
1. Run the main script:
```bash
python main.py
```

### Adding Fishing Spots
1. Open `coordinates.txt`
2. Add your fishing spots in the following format:
```
LocationName: DD°MM'SS.S"N DD°MM'SS.S"E
```
Example:
```
StorJævel: 59°17'20.3"N 11°16'12.4"E
grytekanten: 59°16'57.8"N 11°14'10.7"E
```

## File Structure
- `main.py` - Main script for generating the map
- `coordinates.txt` - File for storing fishing spot coordinates
- `isesjo_kart.geojson` - GeoJSON file containing lake depth data

## Notes
- The map uses a color gradient to represent different depths
- Fishing spots are marked with red dots and labeled
- Labels maintain consistent positioning during zoom/pan operations

## Contributing
Feel free to submit issues and enhancement requests! 