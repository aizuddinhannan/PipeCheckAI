"""
DXF/DWG drawing reader powered by ezdxf.

Extracts layer and entity statistics from readable CAD files.
"""

from dataclasses import dataclass, field
from pathlib import Path

import ezdxf
from ezdxf import recover

# Entity types counted for the Drawing Information panel.
ENTITY_TYPES = (
    "LINE",
    "LWPOLYLINE",
    "POLYLINE",
    "TEXT",
    "MTEXT",
    "INSERT",
)

DWG_CONVERSION_MESSAGE = (
    "DWG support will require conversion to DXF or ODA File Converter."
)


@dataclass
class DrawingInfo:
    """Structured metadata extracted from a CAD drawing file."""

    drawing_name: str = ""
    file_size: str = ""
    layer_count: int = 0
    line_count: int = 0
    lwpolyline_count: int = 0
    polyline_count: int = 0
    text_count: int = 0
    mtext_count: int = 0
    insert_count: int = 0
    layer_names: list[str] = field(default_factory=list)
    readable: bool = False
    message: str = ""


class DrawingReader:
    """Reads DXF files and attempts to read DWG files via ezdxf."""

    @staticmethod
    def _count_entities(doc: ezdxf.document.Drawing) -> dict[str, int]:
        """
        Count selected entity types in the model space layout.

        Args:
            doc: Loaded ezdxf drawing document.

        Returns:
            Mapping of DXF entity type name to occurrence count.
        """
        counts = {entity_type: 0 for entity_type in ENTITY_TYPES}
        msp = doc.modelspace()

        for entity in msp:
            dxftype = entity.dxftype()
            if dxftype in counts:
                counts[dxftype] += 1

        return counts

    @staticmethod
    def _get_layer_names(doc: ezdxf.document.Drawing) -> list[str]:
        """
        Collect sorted layer names from the drawing tables section.

        Args:
            doc: Loaded ezdxf drawing document.

        Returns:
            Alphabetically sorted list of layer names.
        """
        return sorted(layer.dxf.name for layer in doc.layers)

    @staticmethod
    def _get_drawing_name(filepath: Path, doc: ezdxf.document.Drawing) -> str:
        """
        Resolve a display name from the DXF header or fall back to the filename.

        Args:
            filepath: Path to the source file on disk.
            doc: Loaded ezdxf drawing document.

        Returns:
            Human-readable drawing name.
        """
        title = doc.header.get("$TITLE", "").strip()
        if title:
            return title
        return filepath.stem

    @classmethod
    def _load_document(cls, filepath: Path) -> ezdxf.document.Drawing:
        """
        Load a drawing file, using recover mode for slightly damaged DXF files.

        Args:
            filepath: Path to the DXF or DWG file.

        Returns:
            Loaded ezdxf document.

        Raises:
            Exception: If the file cannot be parsed by ezdxf.
        """
        try:
            doc, _auditor = recover.readfile(str(filepath))
            return doc
        except recover.DXFStructureError:
            return ezdxf.readfile(str(filepath))

    @classmethod
    def read_dxf(cls, filepath: str, file_size: str) -> DrawingInfo:
        """
        Read a DXF file and extract drawing statistics.

        Args:
            filepath: Path to the DXF file.
            file_size: Pre-formatted human-readable file size string.

        Returns:
            DrawingInfo populated with layer and entity counts.
        """
        path = Path(filepath)

        try:
            doc = cls._load_document(path)
        except Exception as exc:
            return DrawingInfo(
                drawing_name=path.stem,
                file_size=file_size,
                readable=False,
                message=f"Unable to read DXF file: {exc}",
            )

        counts = cls._count_entities(doc)
        layer_names = cls._get_layer_names(doc)

        return DrawingInfo(
            drawing_name=cls._get_drawing_name(path, doc),
            file_size=file_size,
            layer_count=len(layer_names),
            line_count=counts["LINE"],
            lwpolyline_count=counts["LWPOLYLINE"],
            polyline_count=counts["POLYLINE"],
            text_count=counts["TEXT"],
            mtext_count=counts["MTEXT"],
            insert_count=counts["INSERT"],
            layer_names=layer_names,
            readable=True,
            message="Drawing loaded successfully.",
        )

    @classmethod
    def read_dwg(cls, filepath: str, file_size: str) -> DrawingInfo:
        """
        Attempt to read a DWG file directly; otherwise return a conversion hint.

        ezdxf can only read native DWG when ODA File Converter is installed.
        This method tries a direct read first and reports a friendly message
        when the file cannot be opened.

        Args:
            filepath: Path to the DWG file.
            file_size: Pre-formatted human-readable file size string.

        Returns:
            DrawingInfo with statistics on success, or a conversion message.
        """
        path = Path(filepath)

        try:
            doc = cls._load_document(path)
        except Exception:
            return DrawingInfo(
                drawing_name=path.stem,
                file_size=file_size,
                readable=False,
                message=DWG_CONVERSION_MESSAGE,
            )

        counts = cls._count_entities(doc)
        layer_names = cls._get_layer_names(doc)

        return DrawingInfo(
            drawing_name=cls._get_drawing_name(path, doc),
            file_size=file_size,
            layer_count=len(layer_names),
            line_count=counts["LINE"],
            lwpolyline_count=counts["LWPOLYLINE"],
            polyline_count=counts["POLYLINE"],
            text_count=counts["TEXT"],
            mtext_count=counts["MTEXT"],
            insert_count=counts["INSERT"],
            layer_names=layer_names,
            readable=True,
            message="Drawing loaded successfully.",
        )

    @classmethod
    def read_drawing(cls, filepath: str, file_size: str) -> DrawingInfo | None:
        """
        Route a file to the appropriate reader based on its extension.

        Args:
            filepath: Path to the uploaded drawing file.
            file_size: Pre-formatted human-readable file size string.

        Returns:
            DrawingInfo for DXF/DWG files, or None for non-CAD formats.
        """
        extension = Path(filepath).suffix.lower()

        if extension == ".dxf":
            return cls.read_dxf(filepath, file_size)
        if extension == ".dwg":
            return cls.read_dwg(filepath, file_size)
        return None
