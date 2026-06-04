"""Centralized modern styling — round buttons with proper hover fix."""

import ttkbootstrap as ttk


def apply_global_styles(app):
    """Apply modern round-button styles globally."""
    style = ttk.Style()
    c = app.colors

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

    style.configure(
        "RoundSm.TButton",
        font=("Segoe UI", 9),
        padding=(10, 5),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    style.configure(
        "RoundIcon.TButton",
        font=("Segoe UI", 9),
        padding=(6, 5),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    style.configure(
        "SidebarHeader.TLabel",
        font=("Segoe UI", 9, "bold"),
        padding=(4, 2),
    )

    style.configure(
        "Status.TLabel",
        background=c["bg_tertiary"],
        foreground=c["fg_secondary"],
        font=("Segoe UI", 9),
        padding=(4, 2),
    )

    style.configure("Sidebar.TFrame", background=c["sidebar_bg"])
    style.configure("Editor.TFrame", background=c["editor_bg"])

    style.configure(
        "Section.TLabelframe",
        font=("Segoe UI", 9, "bold"),
        padding=6,
    )


def make_round_btn(parent, text, icon, command, style_name="info", icon_refs=None):
    """
    Create a round-styled button with icon and PROPER hover effect.
    Highlight only while hovering — resets on leave.
    """
    outline_style = f"{style_name}-outline"

    btn = ttk.Button(
        parent,
        text=f"  {text}" if text else "",
        image=icon,
        compound="left" if text else "image",
        command=command,
        bootstyle=outline_style,
        padding=(12, 6) if text else (7, 6),
        cursor="hand2",
    )

    if icon_refs is not None and icon:
        icon_refs.append(icon)

    # Store the base style so we always know what to revert to
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

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)

    # Safety: also reset on FocusOut and ButtonRelease
    def _on_reset(event):
        if not btn._is_hovering:
            try:
                btn.configure(bootstyle=btn._base_style)
            except Exception:
                pass

    btn.bind("<FocusOut>", _on_reset)
    btn.bind("<ButtonRelease-1>", lambda e: btn.after(50, lambda: _on_reset(e)))

    return btn


def make_icon_btn(parent, icon, command, style_name="secondary", icon_refs=None):
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

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)

    def _on_reset(event):
        if not btn._is_hovering:
            try:
                btn.configure(bootstyle=btn._base_style)
            except Exception:
                pass

    btn.bind("<FocusOut>", _on_reset)
    btn.bind("<ButtonRelease-1>", lambda e: btn.after(50, lambda: _on_reset(e)))

    return btn