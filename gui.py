"""
PipeCheckAI — Main GUI module.

Builds the CustomTkinter desktop interface with sidebar navigation,
home page upload workflow, and placeholder pages for future features.
"""

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from utils.drawing_reader import DWG_CONVERSION_MESSAGE, DrawingInfo
from utils.file_handler import FileHandler


# ---------------------------------------------------------------------------
# Theme and layout constants
# ---------------------------------------------------------------------------

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

COLOR_BG_DARK = "#0f1419"
COLOR_SIDEBAR = "#161b22"
COLOR_SURFACE = "#1c2128"
COLOR_ACCENT = "#238636"
COLOR_ACCENT_HOVER = "#2ea043"
COLOR_TEXT = "#e6edf3"
COLOR_TEXT_MUTED = "#8b949e"
COLOR_BORDER = "#30363d"
COLOR_STATUS_OK = "#3fb950"

SIDEBAR_WIDTH = 240
LOGO_HEIGHT = 80

NAV_ITEMS = [
    ("Home", "home"),
    ("Upload Drawing", "upload"),
    ("Diagnosis", "diagnosis"),
    ("Reports", "reports"),
    ("Settings", "settings"),
]

FILE_DIALOG_TYPES = [
    ("Drawing Files", "*.dwg *.dxf *.pdf"),
    ("AutoCAD DWG", "*.dwg"),
    ("AutoCAD DXF", "*.dxf"),
    ("PDF Documents", "*.pdf"),
    ("All Files", "*.*"),
]


class SidebarButton(ctk.CTkButton):
    """Navigation button styled for the left sidebar."""

    def __init__(self, master, text: str, command, **kwargs) -> None:
        """
        Create a sidebar navigation button with consistent styling.

        Args:
            master: Parent widget.
            text: Label shown on the button.
            command: Callback invoked when the button is clicked.
        """
        super().__init__(
            master,
            text=text,
            command=command,
            anchor="w",
            height=44,
            corner_radius=8,
            fg_color="transparent",
            text_color=COLOR_TEXT,
            hover_color=COLOR_SURFACE,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            **kwargs,
        )
        self._active = False

    def set_active(self, active: bool) -> None:
        """
        Toggle the visual active state for the currently selected page.

        Args:
            active: True when this button represents the current page.
        """
        self._active = active
        if active:
            self.configure(
                fg_color=COLOR_SURFACE,
                text_color=COLOR_ACCENT,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=COLOR_TEXT,
                font=ctk.CTkFont(family="Segoe UI", size=14),
            )


class PipeCheckApp(ctk.CTk):
    """Root application window for PipeCheckAI."""

    def __init__(self) -> None:
        """Initialize the main window, layout regions, and default home page."""
        super().__init__()

        # Resolve project paths relative to this file's location.
        self.project_root = Path(__file__).resolve().parent
        self.drawings_dir = self.project_root / "drawings"
        self.file_handler = FileHandler(self.drawings_dir)

        # Track the most recently uploaded file metadata for display.
        self.current_file_info: dict | None = None

        # Initialize navigation state before any UI builders populate these dicts.
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: dict[str, SidebarButton] = {}

        self._configure_window()
        self._build_layout()
        self._create_pages()
        self.show_page("home")

    def _configure_window(self) -> None:
        """Apply window geometry, title, and global dark theme settings."""
        self.title("PipeCheckAI — AI Powered Underground Utility QA System")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.configure(fg_color=COLOR_BG_DARK)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def _build_layout(self) -> None:
        """Construct the top header, sidebar, and main content container."""
        # Top header bar with company logo placeholder.
        self.header = ctk.CTkFrame(self, height=LOGO_HEIGHT, fg_color=COLOR_SURFACE, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self._create_logo_placeholder()

        # Body: sidebar + main content area.
        self.body = ctk.CTkFrame(self, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.body.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(
            self.body,
            width=SIDEBAR_WIDTH,
            fg_color=COLOR_SIDEBAR,
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(self.body, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self._create_sidebar()

    def _create_logo_placeholder(self) -> None:
        """Render a company logo placeholder at the top of the window."""
        logo_frame = ctk.CTkFrame(
            self.header,
            width=200,
            height=50,
            fg_color=COLOR_BORDER,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_TEXT_MUTED,
        )
        logo_frame.pack(side="left", padx=24, pady=15)
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="COMPANY LOGO",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        ).pack(expand=True)

        ctk.CTkLabel(
            self.header,
            text="PipeCheckAI",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(side="left", padx=(8, 0))

    def _create_sidebar(self) -> None:
        """Build sidebar navigation labels and page-switch buttons."""
        ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(24, 8))

        for label, page_key in NAV_ITEMS:
            btn = SidebarButton(
                self.sidebar,
                text=f"  {label}",
                command=lambda key=page_key: self.show_page(key),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[page_key] = btn

        # Version footer at the bottom of the sidebar.
        ctk.CTkLabel(
            self.sidebar,
            text="v0.2.0",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_MUTED,
        ).pack(side="bottom", pady=16)

    def _create_pages(self) -> None:
        """Instantiate all application pages inside the content area."""
        self._create_home_page()
        self._create_upload_page()
        self._create_placeholder_page("diagnosis", "Diagnosis", "AI-powered pipe defect analysis will appear here.")
        self._create_placeholder_page("reports", "Reports", "Generated QA reports will be listed here.")
        self._create_placeholder_page("settings", "Settings", "Application preferences and configuration.")

    def _create_page_frame(self, page_key: str) -> ctk.CTkFrame:
        """
        Create an empty page frame registered in the pages dictionary.

        Args:
            page_key: Unique identifier used for navigation.

        Returns:
            The newly created frame widget.
        """
        frame = ctk.CTkFrame(self.content, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.pages[page_key] = frame
        return frame

    def _create_home_page(self) -> None:
        """Build the home page with title, upload button, and file info panel."""
        page = self._create_page_frame("home")

        # Center column for hero content.
        center = ctk.CTkFrame(page, fg_color="transparent")
        center.place(relx=0.5, rely=0.42, anchor="center")

        ctk.CTkLabel(
            center,
            text="PipeCheckAI",
            font=ctk.CTkFont(family="Segoe UI", size=52, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            center,
            text="AI Powered Underground Utility QA System",
            font=ctk.CTkFont(family="Segoe UI", size=20),
            text_color=COLOR_TEXT_MUTED,
        ).pack(pady=(0, 48))

        ctk.CTkButton(
            center,
            text="UPLOAD DWG",
            width=320,
            height=64,
            corner_radius=12,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            command=self.open_file_dialog,
        ).pack(pady=(0, 40))

        # File information panel (hidden until a file is uploaded).
        self.home_info_panel = self._build_file_info_panel(center)
        self.home_drawing_panel = self._build_drawing_info_panel(center)

    def _create_upload_page(self) -> None:
        """Build the dedicated Upload Drawing page with the same upload workflow."""
        page = self._create_page_frame("upload")

        wrapper = ctk.CTkFrame(page, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=48, pady=48)

        ctk.CTkLabel(
            wrapper,
            text="Upload Drawing",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            wrapper,
            text="Select a DWG, DXF, or PDF file to load into the system.",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 32))

        upload_card = ctk.CTkFrame(
            wrapper,
            fg_color=COLOR_SURFACE,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        upload_card.pack(fill="x", pady=(0, 24))

        card_inner = ctk.CTkFrame(upload_card, fg_color="transparent")
        card_inner.pack(padx=40, pady=40)

        ctk.CTkLabel(
            card_inner,
            text="Supported formats:  .dwg  ·  .dxf  ·  .pdf",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLOR_TEXT_MUTED,
        ).pack(pady=(0, 24))

        ctk.CTkButton(
            card_inner,
            text="BROWSE FILES",
            width=240,
            height=52,
            corner_radius=10,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            command=self.open_file_dialog,
        ).pack()

        self.upload_info_panel = self._build_file_info_panel(wrapper)
        self.upload_drawing_panel = self._build_drawing_info_panel(wrapper)

    def _build_file_info_panel(self, parent) -> ctk.CTkFrame:
        """
        Create a reusable panel that displays uploaded file metadata.

        Args:
            parent: Widget that will contain the panel.

        Returns:
            The panel frame (initially hidden).
        """
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )

        ctk.CTkLabel(
            panel,
            text="File Details",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=24, pady=(20, 12))

        # Grid of label/value pairs.
        grid = ctk.CTkFrame(panel, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=(0, 20))

        fields = ["Filename", "File size", "Date", "Status"]
        labels: dict[str, ctk.CTkLabel] = {}

        for row, field_name in enumerate(fields):
            ctk.CTkLabel(
                grid,
                text=f"{field_name}:",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLOR_TEXT_MUTED,
                width=100,
                anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=6)

            value_label = ctk.CTkLabel(
                grid,
                text="—",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLOR_TEXT,
                anchor="w",
            )
            value_label.grid(row=row, column=1, sticky="w", padx=(16, 0), pady=6)
            labels[field_name.lower().replace(" ", "_")] = value_label

        panel.field_labels = labels  # type: ignore[attr-defined]
        return panel

    def _build_drawing_info_panel(self, parent) -> ctk.CTkFrame:
        """
        Create a panel that displays CAD drawing statistics from ezdxf.

        Args:
            parent: Widget that will contain the panel.

        Returns:
            The panel frame (initially hidden).
        """
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )

        ctk.CTkLabel(
            panel,
            text="Drawing Information",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=24, pady=(20, 12))

        grid = ctk.CTkFrame(panel, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=(0, 12))

        stat_fields = [
            ("drawing_name", "Drawing Name"),
            ("file_size", "File Size"),
            ("layer_count", "Number of Layers"),
            ("line_count", "Number of LINE entities"),
            ("lwpolyline_count", "Number of LWPOLYLINE entities"),
            ("polyline_count", "Number of POLYLINE entities"),
            ("text_count", "Number of TEXT entities"),
            ("mtext_count", "Number of MTEXT entities"),
            ("insert_count", "Number of INSERT (blocks)"),
        ]

        labels: dict[str, ctk.CTkLabel] = {}

        for row, (field_key, field_name) in enumerate(stat_fields):
            ctk.CTkLabel(
                grid,
                text=f"{field_name}:",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLOR_TEXT_MUTED,
                width=280,
                anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=4)

            value_label = ctk.CTkLabel(
                grid,
                text="—",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLOR_TEXT,
                anchor="w",
            )
            value_label.grid(row=row, column=1, sticky="w", padx=(16, 0), pady=4)
            labels[field_key] = value_label

        ctk.CTkLabel(
            panel,
            text="Layer Names:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", padx=24, pady=(8, 4))

        layer_box = ctk.CTkTextbox(
            panel,
            height=120,
            fg_color=COLOR_BG_DARK,
            text_color=COLOR_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            activate_scrollbars=True,
            wrap="word",
        )
        layer_box.pack(fill="x", padx=24, pady=(0, 20))
        layer_box.configure(state="disabled")

        panel.field_labels = labels  # type: ignore[attr-defined]
        panel.layer_box = layer_box  # type: ignore[attr-defined]
        return panel

    def _create_placeholder_page(self, page_key: str, title: str, description: str) -> None:
        """
        Create a placeholder page for features not yet implemented.

        Args:
            page_key: Navigation key for the page.
            title: Heading displayed at the top of the page.
            description: Short explanatory text for the user.
        """
        page = self._create_page_frame(page_key)

        ctk.CTkLabel(
            page,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLOR_TEXT,
        ).place(relx=0.08, rely=0.12, anchor="nw")

        ctk.CTkLabel(
            page,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=COLOR_TEXT_MUTED,
        ).place(relx=0.08, rely=0.20, anchor="nw")

        ctk.CTkLabel(
            page,
            text="Coming Soon",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_ACCENT,
        ).place(relx=0.08, rely=0.26, anchor="nw")

    def show_page(self, page_key: str) -> None:
        """
        Switch the visible content page and update sidebar button states.

        Args:
            page_key: Identifier matching a key in self.pages.
        """
        for key, frame in self.pages.items():
            frame.pack_forget()

        if page_key in self.pages:
            self.pages[page_key].pack(fill="both", expand=True)

        for key, btn in self.nav_buttons.items():
            btn.set_active(key == page_key)

    def open_file_dialog(self) -> None:
        """Open a native file browser filtered to DWG, DXF, and PDF files."""
        initial_dir = str(self.drawings_dir)
        filepath = filedialog.askopenfilename(
            title="Select Drawing File",
            initialdir=initial_dir,
            filetypes=FILE_DIALOG_TYPES,
        )

        if filepath:
            self.process_upload(filepath)

    def process_upload(self, filepath: str) -> None:
        """
        Validate, store, and display metadata for an uploaded drawing file.

        Args:
            filepath: Path returned by the file dialog.
        """
        metadata = self.file_handler.save_drawing(filepath)

        if metadata is None:
            self._show_error("Invalid file type. Please select a DWG, DXF, or PDF file.")
            return

        self.current_file_info = metadata
        self._update_file_info_panels(metadata)

        drawing_info = metadata.get("drawing_info")
        if drawing_info and not drawing_info.readable:
            if drawing_info.message == DWG_CONVERSION_MESSAGE:
                self._show_error(drawing_info.message)
            elif drawing_info.message:
                self._show_error(drawing_info.message)

    def _update_file_info_panels(self, metadata: dict) -> None:
        """
        Refresh all file info panels with the latest upload metadata.

        Args:
            metadata: Dictionary produced by FileHandler.save_drawing().
        """
        for panel in (self.home_info_panel, self.upload_info_panel):
            self._populate_info_panel(panel, metadata)

        for panel in (self.home_drawing_panel, self.upload_drawing_panel):
            self._populate_drawing_info_panel(panel, metadata)

    def _populate_info_panel(self, panel: ctk.CTkFrame, metadata: dict) -> None:
        """
        Fill a single info panel with file metadata and make it visible.

        Args:
            panel: The file details panel widget.
            metadata: Upload metadata dictionary.
        """
        labels = panel.field_labels  # type: ignore[attr-defined]

        labels["filename"].configure(text=metadata["filename"])
        labels["file_size"].configure(text=metadata["file_size"])
        labels["date"].configure(text=metadata["date"])
        labels["status"].configure(text=metadata["status"], text_color=COLOR_STATUS_OK)

        panel.pack(fill="x", pady=(16, 0))

    def _populate_drawing_info_panel(self, panel: ctk.CTkFrame, metadata: dict) -> None:
        """
        Fill a drawing information panel with ezdxf statistics.

        Args:
            panel: The drawing information panel widget.
            metadata: Upload metadata dictionary including optional drawing_info.
        """
        drawing_info: DrawingInfo | None = metadata.get("drawing_info")
        labels = panel.field_labels  # type: ignore[attr-defined]
        layer_box = panel.layer_box  # type: ignore[attr-defined]

        if drawing_info is None:
            panel.pack_forget()
            return

        placeholder = "—" if not drawing_info.readable else "0"

        labels["drawing_name"].configure(text=drawing_info.drawing_name or metadata["filename"])
        labels["file_size"].configure(text=drawing_info.file_size or metadata["file_size"])

        if drawing_info.readable:
            labels["layer_count"].configure(text=str(drawing_info.layer_count))
            labels["line_count"].configure(text=str(drawing_info.line_count))
            labels["lwpolyline_count"].configure(text=str(drawing_info.lwpolyline_count))
            labels["polyline_count"].configure(text=str(drawing_info.polyline_count))
            labels["text_count"].configure(text=str(drawing_info.text_count))
            labels["mtext_count"].configure(text=str(drawing_info.mtext_count))
            labels["insert_count"].configure(text=str(drawing_info.insert_count))

            layer_text = "\n".join(drawing_info.layer_names) if drawing_info.layer_names else "No layers found"
        else:
            for key in (
                "layer_count",
                "line_count",
                "lwpolyline_count",
                "polyline_count",
                "text_count",
                "mtext_count",
                "insert_count",
            ):
                labels[key].configure(text=placeholder)

            layer_text = drawing_info.message or "Unable to read drawing data."

        layer_box.configure(state="normal")
        layer_box.delete("1.0", "end")
        layer_box.insert("1.0", layer_text)
        layer_box.configure(state="disabled")

        panel.pack(fill="x", pady=(16, 0))

    def _show_error(self, message: str) -> None:
        """
        Display a simple error dialog to the user.

        Args:
            message: Error description to show.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Upload Error")
        dialog.geometry("420x160")
        dialog.configure(fg_color=COLOR_SURFACE)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLOR_TEXT,
            wraplength=360,
        ).pack(expand=True, padx=24, pady=24)

        ctk.CTkButton(
            dialog,
            text="OK",
            width=100,
            command=dialog.destroy,
        ).pack(pady=(0, 20))


def run_app() -> None:
    """Create the application instance and start the Tkinter event loop."""
    app = PipeCheckApp()
    app.mainloop()
