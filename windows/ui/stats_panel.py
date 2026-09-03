"""
CLIPBOARD LAN - Stats Panel
Flux de synchronisation en vedette + colonne de lecture compacte

CHEMIN: windows/ui/stats_panel.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, font
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, font


class FeedRow(ctk.CTkFrame):
    """Une ligne du flux de synchronisation — style journal technique."""

    def __init__(self, master, timestamp: str, source: str, content_preview: str, size_label: str):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(2, weight=1)

        ts = ctk.CTkLabel(
            self, text=timestamp, font=font("xs", mono=True),
            text_color=COLORS["text_dim"], width=56, anchor="w"
        )
        ts.grid(row=0, column=0, sticky="w", padx=(0, SPACING["md"]))

        src = ctk.CTkLabel(
            self, text=source.upper(), font=font("xs", "bold", mono=True),
            text_color=COLORS["accent"], width=64, anchor="w"
        )
        src.grid(row=0, column=1, sticky="w", padx=(0, SPACING["md"]))

        content = ctk.CTkLabel(
            self, text=content_preview, font=font("sm"),
            text_color=COLORS["text_primary"], anchor="w"
        )
        content.grid(row=0, column=2, sticky="w")

        size = ctk.CTkLabel(
            self, text=size_label, font=font("xs", mono=True),
            text_color=COLORS["text_dim"], anchor="e"
        )
        size.grid(row=0, column=3, sticky="e", padx=(SPACING["md"], 0))


class ReadoutRow(ctk.CTkFrame):
    """Une ligne de lecture chiffrée compacte (label + valeur alignée à droite)."""

    def __init__(self, master, label: str, value: str, value_color: str = None):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(
            self, text=label, font=font("xs"),
            text_color=COLORS["text_secondary"], anchor="w"
        )
        lbl.grid(row=0, column=0, sticky="w")

        val = ctk.CTkLabel(
            self, text=value, font=font("base", "bold", mono=True),
            text_color=value_color or COLORS["text_primary"], anchor="e"
        )
        val.grid(row=0, column=1, sticky="e")


class StatsPanel(ctk.CTkFrame):
    """
    Panel principal: flux de sync en vedette (large) + colonne de lecture
    (uptime, débit, taux de réussite) — pas une grille de cards identiques.
    """

    def __init__(self, master, sync_manager=None):
        super().__init__(master, fg_color="transparent")

        self.sync_manager = sync_manager

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, pady=(SPACING["md"], 0))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._create_feed(body)
        self._create_readouts(body)

    def _create_feed(self, parent):
        feed_frame = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"],
            border_width=1, border_color=COLORS["border"]
        )
        feed_frame.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["md"]))

        header = ctk.CTkLabel(
            feed_frame, text="FLUX DE SYNCHRONISATION",
            font=font("xs", "bold", mono=True), text_color=COLORS["text_dim"], anchor="w"
        )
        header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        self.feed_list = ctk.CTkScrollableFrame(feed_frame, fg_color="transparent")
        self.feed_list.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))

        self._show_feed_empty()

    def _show_feed_empty(self):
        empty = ctk.CTkLabel(
            self.feed_list, text="En attente de la première synchronisation…",
            font=font("sm"), text_color=COLORS["text_dim"]
        )
        empty.pack(pady=SPACING["xl"])

    def _create_readouts(self, parent):
        col = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"],
            border_width=1, border_color=COLORS["border"]
        )
        col.grid(row=0, column=1, sticky="nsew")

        header = ctk.CTkLabel(
            col, text="ÉTAT", font=font("xs", "bold", mono=True),
            text_color=COLORS["text_dim"], anchor="w"
        )
        header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        self.readout_devices = ReadoutRow(col, "Appareils connectés", "0")
        self.readout_devices.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        self.readout_syncs = ReadoutRow(col, "Syncs aujourd'hui", "0")
        self.readout_syncs.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        self.readout_success = ReadoutRow(col, "Taux de réussite", "—", COLORS["accent"])
        self.readout_success.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        self.readout_data = ReadoutRow(col, "Données transférées", "0 KB")
        self.readout_data.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        sep = ctk.CTkFrame(col, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])

        self.readout_uptime = ReadoutRow(col, "Uptime", "00:00:00")
        self.readout_uptime.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

    def add_activity_item(self, source: str, content_preview: str, timestamp: str, size_label: str = ""):
        """Ajoute une ligne au flux de synchronisation (retire l'état vide au premier ajout)."""
        children = self.feed_list.winfo_children()
        if len(children) == 1 and isinstance(children[0], ctk.CTkLabel):
            children[0].destroy()

        row = FeedRow(self.feed_list, timestamp, source, content_preview, size_label)
        row.pack(fill="x", pady=SPACING["xs"])

    def update_readouts(self, devices: int = None, syncs: int = None,
                         success_rate: str = None, data_transferred: str = None,
                         uptime: str = None):
        """Met à jour les valeurs de la colonne d'état."""
        if devices is not None:
            self.readout_devices.grid_slaves(row=0, column=1)[0].configure(text=str(devices))
        if syncs is not None:
            self.readout_syncs.grid_slaves(row=0, column=1)[0].configure(text=str(syncs))
        if success_rate is not None:
            self.readout_success.grid_slaves(row=0, column=1)[0].configure(text=success_rate)
        if data_transferred is not None:
            self.readout_data.grid_slaves(row=0, column=1)[0].configure(text=data_transferred)
        if uptime is not None:
            self.readout_uptime.grid_slaves(row=0, column=1)[0].configure(text=uptime)

    def refresh(self, status: dict):
        """Rafraîchit à partir du statut renvoyé par SyncManager.get_status()."""
        connected = status.get("connected_devices", 0)
        self.update_readouts(devices=connected)


if __name__ == "__main__":
    print("✅ Stats Panel v2 ready")