"""
CLIPBOARD LAN - Device Panel
Liste des appareils — pastille de statut, IDs en mono, actions discrètes

CHEMIN: windows/ui/device_panel.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, font
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, font


class DeviceRow(ctk.CTkFrame):
    """Une ligne d'appareil dans la liste — pas une card isolée avec ombre."""

    def __init__(self, master, device_id: str, device_name: str,
                 is_connected: bool = False, is_trusted: bool = False,
                 last_seen: str = "", on_approve=None, on_remove=None):
        super().__init__(master, fg_color="transparent")

        self.device_id = device_id

        self.grid_columnconfigure(2, weight=1)

        dot_color = COLORS["success"] if is_connected else COLORS["offline"]
        dot = ctk.CTkLabel(self, text="●", font=("Segoe UI", 10), text_color=dot_color, width=16)
        dot.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, SPACING["sm"]))

        name = ctk.CTkLabel(
            self, text=device_name, font=font("base", "bold"),
            text_color=COLORS["text_primary"], anchor="w"
        )
        name.grid(row=0, column=1, columnspan=2, sticky="w")

        trust_text = "de confiance" if is_trusted else "en attente d'approbation"
        trust_color = COLORS["text_secondary"] if is_trusted else COLORS["warning"]
        meta = ctk.CTkLabel(
            self, text=f"{device_id}  ·  {trust_text}  ·  {last_seen}",
            font=font("xs", mono=True), text_color=trust_color, anchor="w"
        )
        meta.grid(row=1, column=1, columnspan=2, sticky="w")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=3, rowspan=2, sticky="e", padx=(SPACING["md"], 0))

        if not is_trusted and on_approve:
            approve_btn = ctk.CTkButton(
                actions, text="Approuver", width=88, height=26,
                fg_color="transparent", hover_color=COLORS["surface_hover"],
                border_width=1, border_color=COLORS["accent_dim"],
                text_color=COLORS["accent"], font=font("xs"),
                corner_radius=RADIUS["sm"],
                command=lambda: on_approve(device_id)
            )
            approve_btn.pack(side="left", padx=(0, SPACING["xs"]))

        if on_remove:
            remove_btn = ctk.CTkButton(
                actions, text="Retirer", width=64, height=26,
                fg_color="transparent", hover_color=COLORS["surface_hover"],
                text_color=COLORS["text_dim"], font=font("xs"),
                corner_radius=RADIUS["sm"],
                command=lambda: on_remove(device_id)
            )
            remove_btn.pack(side="left")

        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(SPACING["sm"], 0))


class DevicePanel(ctk.CTkFrame):
    """Panel affichant la liste des appareils connus/connectés."""

    def __init__(self, master, device_manager=None):
        super().__init__(master, fg_color="transparent")

        self.device_manager = device_manager
        self._on_approve_callback = None
        self._on_remove_callback = None

        self._create_header()
        self._create_list_container()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(SPACING["md"], SPACING["md"]))

        title = ctk.CTkLabel(
            header, text="Appareils", font=font("xl", "bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")

        self.count_label = ctk.CTkLabel(
            header, text="0 appareils", font=font("xs", mono=True),
            text_color=COLORS["text_dim"]
        )
        self.count_label.pack(side="right")

    def _create_list_container(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"],
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="both", expand=True)

        self.device_list_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.device_list_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        self._show_empty_state()

    def _show_empty_state(self):
        empty_label = ctk.CTkLabel(
            self.device_list_frame,
            text="Aucun appareil connecté.\nOuvrez l'app Android sur le même réseau pour l'associer.",
            font=font("sm"), text_color=COLORS["text_dim"], justify="center"
        )
        empty_label.pack(pady=SPACING["2xl"])

    def refresh_devices(self, devices: list):
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        self.count_label.configure(text=f"{len(devices)} appareils")

        if not devices:
            self._show_empty_state()
            return

        for device in devices:
            row = DeviceRow(
                self.device_list_frame,
                device_id=device.get("device_id", ""),
                device_name=device.get("device_name", "Appareil inconnu"),
                is_connected=device.get("is_connected", True),
                is_trusted=device.get("is_trusted", False),
                last_seen=device.get("last_seen", "à l'instant"),
                on_approve=self._on_approve_callback,
                on_remove=self._on_remove_callback
            )
            row.pack(fill="x", pady=(0, SPACING["sm"]))

    def on_approve_device(self, callback):
        self._on_approve_callback = callback

    def on_remove_device(self, callback):
        self._on_remove_callback = callback


if __name__ == "__main__":
    print("✅ Device Panel v2 ready")