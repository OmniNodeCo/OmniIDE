"""Extensions panel — VS Code style browse and install."""

import tkinter as tk
import tkinter.ttk as tkttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn
from src.core.extension_manager import ExtensionManager


class ExtensionsPanel:
    """Extensions browser panel."""

    def __init__(self, parent, app):
        self.app = app
        self.ext_manager = ExtensionManager(app)
        self.icon_mgr = IconManager()
        self._icon_refs = []
        self.result_widgets = []

        self.frame = ttk.Frame(parent)
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self.frame, padding=(10, 6, 10, 4))
        header.pack(fill=X)

        ext_icon = self.icon_mgr.get("settings", 14)
        self._icon_refs.append(ext_icon)

        ttk.Label(
            header,
            text=" EXTENSIONS",
            image=ext_icon,
            compound=LEFT,
            font=("Segoe UI", 9, "bold"),
            foreground="#a6adc8",
        ).pack(side=LEFT)

        # Search
        search_frame = ttk.Frame(self.frame, padding=(8, 4, 8, 4))
        search_frame.pack(fill=X)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 4))
        self.search_entry.insert(0, "Search extensions...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._set_placeholder)
        self.search_entry.bind("<Return>", self._on_search)

        search_icon = self.icon_mgr.get("search", 14)
        self._icon_refs.append(search_icon)

        search_btn = make_round_btn(
            search_frame, "", search_icon,
            self._on_search, "info",
            self._icon_refs, size="small",
        )
        search_btn.pack(side=RIGHT)

        # Loading label
        self.loading_label = ttk.Label(
            self.frame, text="",
            font=("Segoe UI", 9),
            padding=(10, 2),
        )
        self.loading_label.pack(fill=X)

        # Tabs: Marketplace | Installed
        tab_frame = ttk.Frame(self.frame, padding=(8, 2, 8, 4))
        tab_frame.pack(fill=X)

        self.tab_var = tk.StringVar(value="marketplace")

        ttk.Radiobutton(
            tab_frame, text="Marketplace",
            variable=self.tab_var, value="marketplace",
            bootstyle="info-outline-toolbutton",
            command=self._on_tab_change,
        ).pack(side=LEFT, fill=X, expand=True, padx=(0, 2))

        ttk.Radiobutton(
            tab_frame, text="Installed",
            variable=self.tab_var, value="installed",
            bootstyle="success-outline-toolbutton",
            command=self._on_tab_change,
        ).pack(side=LEFT, fill=X, expand=True, padx=(2, 0))

        # Results (scrollable)
        results_container = ttk.Frame(self.frame)
        results_container.pack(fill=BOTH, expand=True, padx=2)

        self.results_canvas = tk.Canvas(
            results_container,
            highlightthickness=0, bd=0,
            bg=self.app.colors["sidebar_bg"],
        )

        self.results_scrollbar = tkttk.Scrollbar(
            results_container, orient=tk.VERTICAL,
            command=self.results_canvas.yview,
        )

        self.results_frame = ttk.Frame(self.results_canvas)
        self.results_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")
            ),
        )

        self.canvas_window = self.results_canvas.create_window(
            (0, 0), window=self.results_frame, anchor="nw",
        )

        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)
        self.results_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.results_scrollbar.pack(side=RIGHT, fill=tk.Y)

        self.results_canvas.bind("<Enter>", self._bind_mousewheel)
        self.results_canvas.bind("<Leave>", self._unbind_mousewheel)

        self.results_canvas.bind(
            "<Configure>",
            lambda e: self.results_canvas.itemconfig(
                self.canvas_window, width=e.width
            ),
        )

        self._show_installed()

    def _clear_placeholder(self, event=None):
        if self.search_entry.get() == "Search extensions...":
            self.search_entry.delete(0, "end")

    def _set_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search extensions...")

    def _bind_mousewheel(self, event=None):
        self.results_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.results_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.results_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        self.results_canvas.unbind_all("<MouseWheel>")
        self.results_canvas.unbind_all("<Button-4>")
        self.results_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.results_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.results_canvas.yview_scroll(1, "units")
        else:
            self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_tab_change(self):
        if self.tab_var.get() == "installed":
            self._show_installed()
        else:
            self._clear_results()
            self.loading_label.configure(text="Search for extensions above")

    def _on_search(self, event=None):
        query = self.search_var.get().strip()
        if not query or query == "Search extensions...":
            return

        self.tab_var.set("marketplace")
        self._clear_results()
        self.loading_label.configure(text="Searching...")
        self.app.set_status(f"Searching extensions: {query}")

        self.ext_manager.search(query, self._on_search_results)

    def _on_search_results(self, results, error):
        self._clear_results()

        if error:
            self.loading_label.configure(text=f"Error: {error}")
            return

        if not results:
            self.loading_label.configure(text="No extensions found.")
            return

        self.loading_label.configure(text=f"{len(results)} found")
        self.app.set_status(f"Found {len(results)} extensions")

        for ext_info in results:
            self._add_card(ext_info, mode="marketplace")

    def _show_installed(self):
        self._clear_results()
        installed = self.ext_manager.get_installed()

        if not installed:
            self.loading_label.configure(text="No extensions installed.")
            return

        self.loading_label.configure(text=f"{len(installed)} installed")

        for ext_info in installed:
            self._add_card(ext_info, mode="installed")

    def _add_card(self, ext_info, mode="marketplace"):
        """Add a VS Code style extension card."""
        c = self.app.colors

        card = ttk.Frame(self.results_frame, padding=(10, 8))
        card.pack(fill=X, padx=2, pady=1)

        # Top: name + version
        top = ttk.Frame(card)
        top.pack(fill=X)

        name = ext_info.get("name", ext_info.get("id", "Unknown"))
        version = ext_info.get("version", "")

        ttk.Label(
            top, text=name,
            font=("Segoe UI", 10, "bold"),
            wraplength=210,
        ).pack(side=LEFT, anchor="w")

        ttk.Label(
            top, text=f"v{version}",
            font=("Segoe UI", 8),
            foreground=c.get("fg_secondary", "#888"),
        ).pack(side=RIGHT)

        # Publisher
        publisher = ext_info.get("publisher", "")
        if publisher:
            ttk.Label(
                card, text=publisher,
                font=("Segoe UI", 8),
                foreground=c.get("accent", "#89b4fa"),
            ).pack(anchor="w")

        # Description
        desc = ext_info.get("description", "")
        if desc:
            ttk.Label(
                card, text=desc[:100] + ("..." if len(desc) > 100 else ""),
                font=("Segoe UI", 9),
                wraplength=220,
                foreground=c.get("fg_secondary", "#a6adc8"),
            ).pack(anchor="w", pady=(2, 0))

        # Stats
        if mode == "marketplace":
            stats = ttk.Frame(card)
            stats.pack(fill=X, pady=(4, 0))

            installs = ext_info.get("installs", 0)
            rating = ext_info.get("rating", 0)

            ttk.Label(
                stats,
                text=f"Downloads: {ExtensionManager.format_installs(installs)}",
                font=("Segoe UI", 8),
                foreground=c.get("fg_secondary", "#888"),
            ).pack(side=LEFT)

            if rating > 0:
                ttk.Label(
                    stats,
                    text=f"  Rating: {rating}",
                    font=("Segoe UI", 8),
                    foreground=c.get("warning", "#fab387"),
                ).pack(side=LEFT, padx=(8, 0))

        # Action button
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill=X, pady=(6, 0))

        if mode == "marketplace":
            is_installed = ext_info.get("installed", False)
            if is_installed:
                ttk.Label(
                    btn_frame, text="Installed",
                    font=("Segoe UI", 9, "bold"),
                    foreground=c.get("success", "#a6e3a1"),
                ).pack(side=LEFT)
            else:
                make_round_btn(
                    btn_frame, "Install",
                    self.icon_mgr.get("success", 12),
                    lambda ei=ext_info: self._install(ei),
                    "success", self._icon_refs, "small",
                ).pack(side=LEFT)
        elif mode == "installed":
            make_round_btn(
                btn_frame, "Uninstall",
                self.icon_mgr.get("close", 12),
                lambda ei=ext_info: self._uninstall(ei),
                "danger", self._icon_refs, "small",
            ).pack(side=LEFT)

        ttk.Separator(self.results_frame).pack(fill=X, padx=8, pady=1)
        self.result_widgets.append(card)

    def _install(self, ext_info):
        name = ext_info.get("name", "extension")
        self.loading_label.configure(text=f"Installing {name}...")
        self.app.set_status(f"Installing {name}...")

        def _on_done(success, message):
            self.loading_label.configure(text=message)
            self.app.set_status(message)
            if success:
                messagebox.showinfo("Installed", message)
                query = self.search_var.get().strip()
                if query and query != "Search extensions...":
                    self._on_search()
            else:
                messagebox.showerror("Install Failed", message)

        self.ext_manager.install_extension(ext_info, _on_done)

    def _uninstall(self, ext_info):
        ext_id = ext_info.get("id", "")
        name = ext_info.get("name", ext_id)

        if not messagebox.askyesno("Uninstall", f"Uninstall {name}?"):
            return

        ok, msg = self.ext_manager.uninstall_extension(ext_id)
        if ok:
            self.app.set_status(msg)
            self._show_installed()
        else:
            messagebox.showerror("Uninstall Failed", msg)

    def _clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.result_widgets.clear()