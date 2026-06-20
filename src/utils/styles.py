"""Centralized modern styling — VS Code inspired round buttons."""

import ttkbootstrap as ttk


def _safe_configure(style, name, **kwargs):
    """Configure a style, ignoring duplicate element errors."""
    try:
        style.configure(name, **kwargs)
    except Exception as e:
        if "duplicate" in str(e).lower() or "Duplicate" in str(e):
            pass  # Already configured — safe to ignore
        else:
            raise


def apply_global_styles(app):
    """Apply modern VS Code-inspired styles globally."""
    style = ttk.Style()
    c = app.colors

    _safe_configure(style, "Round.TButton",
        font=("Segoe UI", 10), padding=(14, 7),
        borderwidth=0, focusthickness=0, relief="flat",
    )
    style.map("Round.TButton",
        relief=[("pressed", "flat"), ("active", "flat")],
    )

    _safe_configure(style, "RoundSm.TButton",
        font=("Segoe UI", 9), padding=(10, 5),
        borderwidth=0, focusthickness=0, relief="flat",
    )

    _safe_configure(style, "RoundIcon.TButton",
        font=("Segoe UI", 9), padding=(6, 5),
        borderwidth=0, focusthickness=0, relief="flat",
    )

    _safe_configure(style, "SidebarHeader.TLabel",
        font=("Segoe UI", 9, "bold"), padding=(4, 2),
    )

    _safe_configure(style, "Status.TLabel",
        background=c["bg_tertiary"],
        foreground=c["fg_secondary"],
        font=("Segoe UI", 9),
        padding=(4, 2),
    )

    _safe_configure(style, "Sidebar.TFrame", background=c["sidebar_bg"])
    _safe_configure(style, "Editor.TFrame", background=c["editor_bg"])
    _safe_configure(style, "Dark.TFrame", background=c["bg_primary"])
    _safe_configure(style, "Card.TFrame", background=c["bg_secondary"])

    _safe_configure(style, "Section.TLabelframe",
        font=("Segoe UI", 9, "bold"), padding=6,
    )

    _safe_configure(style, "TNotebook",
        background=c["bg_primary"], borderwidth=0,
    )
    _safe_configure(style, "TNotebook.Tab",
        padding=(12, 6), font=("Segoe UI", 9),
    )

    _safe_configure(style, "Treeview",
        background=c["sidebar_bg"],
        foreground=c["fg_primary"],
        fieldbackground=c["sidebar_bg"],
        borderwidth=0,
        font=("Segoe UI", 10),
        rowheight=26,
    )
    try:
        style.map("Treeview",
            background=[("selected", c["selection"])],
            foreground=[("selected", c["fg_primary"])],
        )
    except Exception:
        pass

    _safe_configure(style, "TCombobox",
        font=("Segoe UI", 10), padding=(8, 4),
    )

    _safe_configure(style, "TEntry",
        font=("Segoe UI", 10), padding=(8, 6),
    )

    _safe_configure(style, "Switch.TCheckbutton",
        font=("Segoe UI", 10),
    )

    # TSeparator — most likely to cause duplicate element errors
    try:
        style.configure("TSeparator", background=c["border"])
    except Exception:
        pass


def make_round_btn(parent, text, icon, command, style_name="info", icon_refs=None, size="normal"):
    """Create a round-styled button with proper hover effect."""
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
    """Create a VS Code style action row."""
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