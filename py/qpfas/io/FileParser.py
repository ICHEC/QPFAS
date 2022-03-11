from pathlib import Path

xyz = ""
if type(data) is str:
    if os.path.exists(data): # If string path to data file
        xyz = Path(data).read_text()
    else: # If explicit XYZ
        xyz = data
else: # If Path to data file
    xyz = data.read_text()