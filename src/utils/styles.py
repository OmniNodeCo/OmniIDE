"""Centralized modern styling — VS Code inspired round buttons, consistent spacing."""

import ttkbootstrap as ttk


def apply_global_styles(app):
    """Apply modern VS Code-inspired styles globally."""
    style = ttk.Style()
    c = app.colors

    # Round button base
    style.configure(
        "Round.TButton",
        font=("Segoe UI", 10),
        padding=(14, 7),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )
    style.map("Round.TButton",
        relief=[("pressed", "flat"), ("active", "flat")],
    )

    # Small round button
    style.configure(
        "RoundSm.TButton",
        font=("Segoe UI", 9),
        padding=(10, 5),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    # Icon-only round button
    style.configure(
        "RoundIcon.TButton",
        font=("Segoe UI", 9),
        padding=(6, 5),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    # Sidebar header label
    style.configure(
        "SidebarHeader.TLabel",
        font=("Segoe UI", 9, "bold"),
        padding=(4, 2),
    )

    # Status bar
    style.configure(
        "Status.TLabel",
        background=c["bg_tertiary"],
        foreground=c["fg_secondary"],
        font=("Segoe UI", 9),
        padding=(4, 2),
    )

    # Frame backgrounds
    style.configure("Sidebar.TFrame", background=c["sidebar_bg"])
    style.configure("Editor.TFrame", background=c["editor_bg"])
    style.configure("Dark.TFrame", background=c["bg_primary"])
    style.configure("Card.TFrame", background=c["bg_secondary"])

    # Section label frame
    style.configure(
        "Section.TLabelframe",
        font=("Segoe UI", 9, "bold"),
        padding=6,
    )

    # Modern Notebook (tabs)
    style.configure(
        "TNotebook",
        background=c["bg_primary"],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        padding=(12, 6),
        font=("Segoe UI", 9),
    )

    # Treeview
    style.configure(
        "Treeview",
        background=c["sidebar_bg"],
        foreground=c["fg_primary"],
        fieldbackground=c["sidebar_bg"],
        borderwidth=0,
        font=("Segoe UI", 10),
        rowheight=26,
    )
    style.map("Treeview",
        background=[("selected", c["selection"])],
        foreground=[("selected", c["fg_primary"])],
    )

    # Combobox
    style.configure(
        "TCombobox",
        font=("Segoe UI", 10),
        padding=(8, 4),
    )

    # Entry
    style.configure(
        "TEntry",
        font=("Segoe UI", 10),
        padding=(8, 6),
    )

    # Separator
    style.configure(
        "TSeparator",
        background=c["border"],
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=c["bg_tertiary"],
        troughcolor=c["bg_secondary"],
        borderwidth=0,
        arrowsize=0,
    )

    # Checkbutton toggle
    style.configure(
        "Switch.TCheckbutton",
        font=("Segoe UI", 10),
    )


def make_round_btn(parent, text, icon, command, style_name="info", icon_refs=None, size="normal"):
    """Create a round-styled button with icon and proper hover effect."""
    outline_style = f"{style_name}-outline"

    if size == "small":
        pad = (8, 4)
        txt = f" {text}" if text else ""
    elif size == "large":
        pad = (16, 8)
        txt = f"  {text}" if text else ""
    else:
        pad = (12, 6)
        txt = f"  {text}" if text else ""

    btn = ttk.Button(
        parent,
        text=txt,
        image=icon,
        compound="left" if text else "image",
        command=command,
        bootstyle=outline_style,
        padding=pad,
        cursor="hand2",
    )

    if icon_refs is not None and icon:
        icon_refs.append(icon)

    btn._base_style = outline_style
    btn._hover_style = style_name
    btn._is_hovering = False

    def _on_enter(event):
        btn._is_hovering = True
        try:
            btn.configure(bootstyle=btn._hover_style)
        except Exception:
            pass

    def _on_leave(event):
        btn._is_hovering = False
        try:
            btn.configure(bootstyle=btn._base_style)
        except Exception:
            pass

    def _on_reset(event):
        if not btn._is_hovering:
            try:
                btn.configure(bootstyle=btn._base_style)
            except Exception:
                pass

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    btn.bind("<FocusOut>", _on_reset)
    btn.bind("<ButtonRelease-1>", lambda e: btn.after(50, lambda: _on_reset(e)))

    return btn


def make_icon_btn(parent, icon, command, style_name="secondary", icon_refs=None, tooltip=None):
    """Create a small icon-only round button with proper hover."""
    link_style = f"{style_name}-link"

    btn = ttk.Button(
        parent,
        image=icon,
        command=command,
        bootstyle=link_style,
        padding=(4, 4),
        cursor="hand2",
    )

    if icon_refs is not None and icon:
        icon_refs.append(icon)

    btn._base_style = link_style
    btn._hover_style = style_name
    btn._is_hovering = False

    def _on_enter(event):
        btn._is_hovering = True
        try:
            btn.configure(bootstyle=btn._hover_style)
        except Exception:
            pass

    def _on_leave(event):
        btn._is_hovering = False
        try:
            btn.configure(bootstyle=btn._base_style)
        except Exception:
            pass

    def _on_reset(event):
        if not btn._is_hovering:
            try:
                btn.configure(bootstyle=btn._base_style)
            except Exception:
                pass

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    btn.bind("<FocusOut>", _on_reset)
    btn.bind("<ButtonRelease-1>", lambda e: btn.after(50, lambda: _on_reset(e)))

    return btn


def make_action_row(parent, icon, text, description, command, style_name="info", icon_refs=None):
    """Create a VS Code style action row — icon + text + description + hover."""
    row = ttk.Frame(parent, padding=(4, 3))

    btn = ttk.Button(
        row,
        text=f"  {text}",
        image=icon,
        compound="left",
        command=command,
        bootstyle=f"{style_name}-outline",
        padding=(10, 5),
        cursor="hand2",
    )
    btn.pack(fill="x")

    if icon_refs is not None and icon:
        icon_refs.append(icon)

    btn._base_style = f"{style_name}-outline"
    btn._hover_style = style_name
    btn._is_hovering = False

    def _on_enter(e):
        btn._is_hovering = True
        try:
            btn.configure(bootstyle=btn._hover_style)
        except Exception:
            pass

    def _on_leave(e):
        btn._is_hovering = False
        try:
            btn.configure(bootstyle=btn._base_style)
        except Exception:
            pass

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    btn.bind("<FocusOut>", lambda e: _on_leave(e))
    btn.bind("<ButtonRelease-1>", lambda e: btn.after(50, lambda: _on_leave(e)))

    return row