from cad.dxf_reader import load_dxf
from cad.drawing_info import get_drawing_info

filepath = "test_sample.dxf"

print("Loading DXF...")

doc = load_dxf(filepath)

if doc is None:
    print("❌ Failed to load DXF.")
else:
    info = get_drawing_info(doc, filepath)

    print("\n========== PIPECHECKAI ==========")
    print(f"Filename      : {info['filename']}")
    print(f"DXF Version   : {info['dxf_version']}")
    print(f"Layer Count   : {info['layer_count']}")
    print(f"Entity Count  : {info['entity_count']}")

    print("\nLayers")
    print("-------------------------")

    for layer in info["layers"]:
        print(layer)