"""
PipeCheckAI
DXF Reader Module

This module loads DXF drawings using the ezdxf library.
"""

import ezdxf


def load_dxf(filepath):
    """
    Load a DXF drawing.

    Parameters
    ----------
    filepath : str
        Path to the DXF file.

    Returns
    -------
    ezdxf.document.Drawing | None
        Loaded drawing object, or None if loading fails.
    """

    try:
        document = ezdxf.readfile(filepath)
        return document

    except Exception as error:
        print(f"[ERROR] Unable to load DXF: {error}")
        return None