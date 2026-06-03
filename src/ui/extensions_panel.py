"""Extensions panel — browse and install VS Code extensions."""

import tkinter as tk
import tkinter.ttk as tkttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

from src.utils.icon_manager import IconManager
from src.utils.styles import make_round_btn, make_icon_btn
from src.core.extension_manager import ExtensionManager


class ExtensionsPanel:
    """Extensions browser panel for the sidebar."""

    def __init__(self, parent, app):
        self.app = app
        self.ext_manager = ExtensionManager(app)
        self.icon_mgr = IconManager()
        self._icon_refs = []
        self.result_widgets = []

        self.frame = ttk.Frame(parent)
        self._build_ui()

    def _build_ui(self):
        """Build the extensions panel UI."""
        # ── Search bar ──
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=X, padx=6, pady=(6, 4))

        search_icon = self.icon_mgr.get("search", 14)
        self._icon_refs.append(search_icon)

        ttk.Label(
            search_frame, image=search_icon,
        ).pack(side=LEFT, padx=(0, 4))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True)
        self.search_entry.insert(0, "Search extensions...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._set_placeholder)
        self.search_entry.bind("<Return>", self._on_search)

        search_btn = make_round_btn(
            search_frame,
            text="",
            icon=search_icon,
            command=self._on_search,
            style_name="info",
            icon_refs=self._icon_refs,
        )
        search_btn.pack(side=RIGHT, padx=(4, 0))

        # ── Loading label ──
        self.loading_label = ttk.Label(
            self.frame, text="",
            font=("Segoe UI", 9),
        )
        self.loading_label.pack(fill=X, padx=8)

        # ── Tab selector: Marketplace | Installed ──
        tab_frame = ttk.Frame(self.frame)
        tab_frame.pack(fill=X, padx=6, pady=(2, 4))

        self.tab_var = tk.StringVar(value="marketplace")

        ttk.Radiobutton(
            tab_frame, text="Marketplace",
            variable=self.tab_var, value="marketplace",
            bootstyle="info-outline-toolbutton",
            command=self._on_tab_change,
        ).pack(side=LEFT, padx=(0, 2), fill=X, expand=True)

        ttk.Radiobutton(
            tab_frame, text="Installed",
            variable=self.tab_var, value="installed",
            bootstyle="success-outline-toolbutton",
            command=self._on_tab_change,
        ).pack(side=LEFT, padx=(2, 0), fill=X, expand=True)

        # ── Results area (scrollable) ──
        results_container = ttk.Frame(self.frame)
        results_container.pack(fill=BOTH, expand=True, padx=2)

        self.results_canvas = tk.Canvas(
            results_container,
            highlightthickness=0,
            bd=0,
            bg=self.app.colors["sidebar_bg"],
        )

        self.results_scrollbar = tkttk.Scrollbar(
            results_container,
            orient=tk.VERTICAL,
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

        # Bind mouse wheel
        self.results_canvas.bind("<Enter>", self._bind_mousewheel)
        self.results_canvas.bind("<Leave>", self._unbind_mousewheel)

        # Make results frame fill canvas width
        self.results_canvas.bind(
            "<Configure>",
            lambda e: self.results_canvas.itemconfig(
                self.canvas_window, width=e.width
            ),
        )

        # Show installed by default
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
            self.results_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units"
            )

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
        """Handle search results on main thread."""
        self._clear_results()

        if error:
            self.loading_label.configure(text=f"Error: {error}")
            return

        if not results:
            self.loading_label.configure(text="No extensions found.")
            return

        self.loading_label.configure(text=f"{len(results)} extensions found")
        self.app.set_status(f"Found {len(results)} extensions")

        for ext_info in results:
            self._add_extension_card(ext_info, mode="marketplace")

    def _show_installed(self):
        """Show installed extensions."""
        self._clear_results()
        installed = self.ext_manager.get_installed()

        if not installed:
            self.loading_label.configure(text="No extensions installed.")
            return

        self.loading_label.configure(text=f"{len(installed)} installed")

        for ext_info in installed:
            self._add_extension_card(ext_info, mode="installed")

    def _add_extension_card(self, ext_info, mode="marketplace"):
        """Add an extension card to the results."""
        card = ttk.Frame(
            self.results_frame,
            padding=(8, 6),
        )
        card.pack(fill=X, padx=4, pady=2)

        # Top row: name + version
        top = ttk.Frame(card)
        top.pack(fill=X)

        name = ext_info.get("name", ext_info.get("id", "Unknown"))
        version = ext_info.get("version", "")

        ttk.Label(
            top, text=name,
            font=("Segoe UI", 10, "bold"),
            wraplength=200,
        ).pack(side=LEFT, anchor="w")

        ttk.Label(
            top, text=f"v{version}",
            font=("Segoe UI", 8),
            foreground=self.app.colors.get("fg_secondary", "#888"),
        ).pack(side=RIGHT)

        # Publisher
        publisher = ext_info.get("publisher", "")
        if publisher:
            ttk.Label(
                card, text=publisher,
                font=("Segoe UI", 8),
                foreground=self.app.colors.get("accent", "#89b4fa"),
            ).pack(anchor="w")

        # Description
        desc = ext_info.get("description", "")
        if desc:
            ttk.Label(
                card, text=desc[:120] + ("..." if len(desc) > 120 else ""),
                font=("Segoe UI", 9),
                wraplength=220,
            ).pack(anchor="w", pady=(2, 0))

        # Stats row
        if mode == "marketplace":
            stats_frame = ttk.Frame(card)
            stats_frame.pack(fill=X, pady=(4, 0))

            installs = ext_info.get("installs", 0)
            rating = ext_info.get("rating", 0)

            ttk.Label(
                stats_frame,
                text=f"Downloads: {ExtensionManager.format_installs(installs)}",
                font=("Segoe UI", 8),
                foreground=self.app.colors.get("fg_secondary", "#888"),
            ).pack(side=LEFT)

            if rating > 0:
                stars = "*" * int(rating) + "." * (5 - int(rating))
                ttk.Label(
                    stats_frame,
                    text=f"  [{stars}] {rating}",
                    font=("Consolas", 8),
                    foreground=self.app.colors.get("warning", "#fab387"),
                ).pack(side=LEFT, padx=(8, 0))

        # Action button
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill=X, pady=(4, 0))

        if mode == "marketplace":
            is_installed = ext_info.get("installed", False)
            if is_installed:
                ttk.Label(
                    btn_frame, text="Installed",
                    font=("Segoe UI", 9, "bold"),
                    foreground=self.app.colors.get("success", "#a6e3a1"),
                ).pack(side=LEFT)
            else:
                install_btn = make_round_btn(
                    btn_frame,
                    text="Install",
                    icon=self.icon_mgr.get("success", 12),
                    command=lambda ei=ext_info: self._install(ei),
                    style_name="success",
                    icon_refs=self._icon_refs,
                )
                install_btn.pack(side=LEFT)

        elif mode == "installed":
            uninstall_btn = make_round_btn(
                btn_frame,
                text="Uninstall",
                icon=self.icon_mgr.get("close", 12),
                command=lambda ei=ext_info: self._uninstall(ei),
                style_name="danger",
                icon_refs=self._icon_refs,
            )
            uninstall_btn.pack(side=LEFT)

        # Separator
        ttk.Separator(self.results_frame).pack(fill=X, padx=8, pady=1)

        self.result_widgets.append(card)

    def _install(self, ext_info):
        """Install an extension."""
        name = ext_info.get("name", "extension")
        self.loading_label.configure(text=f"Installing {name}...")
        self.app.set_status(f"Installing {name}...")

        def _on_done(success, message):
            self.loading_label.configure(text=message)
            self.app.set_status(message)
            if success:
                messagebox.showinfo("Installed", message)
                # Refresh the results to show updated install status
                query = self.search_var.get().strip()
                if query and query != "Search extensions...":
                    self._on_search()
            else:
                messagebox.showerror("Install Failed", message)

        self.ext_manager.install_extension(ext_info, _on_done)

    def _uninstall(self, ext_info):
        """Uninstall an extension."""
        ext_id = ext_info.get("id", "")
        name = ext_info.get("name", ext_id)

        confirm = messagebox.askyesno(
            "Uninstall",
            f"Uninstall {name}?",
        )
        if not confirm:
            return

        ok, msg = self.ext_manager.uninstall_extension(ext_id)
        if ok:
            self.app.set_status(msg)
            self._show_installed()
        else:
            messagebox.showerror("Uninstall Failed", msg)

    def _clear_results(self):
        """Clear all result widgets."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.result_widgets.clear()