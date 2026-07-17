"""
PipeCheckAI
Drawing Information Module
"""

from pathlib import Path


def get_drawing_info(doc, filepath):
    """
    Extract basic information from a DXF drawing.

    Parameters
    ----------
    doc
        ezdxf Drawing object.

    filepath : str
        Path to the DXF file.

    Returns
    -------
    dict
        Dictionary containing basic drawing information.
    """

    modelspace = doc.modelspace()

    layers = [layer.dxf.name for layer in doc.layers]

    return {
        "filename": Path(filepath).name,
        "dxf_version": doc.dxfversion,
        "layer_count": len(layers),
        "layers": layers,
        "entity_count": len(modelspace),
    }