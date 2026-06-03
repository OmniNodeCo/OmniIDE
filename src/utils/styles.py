"""Centralized modern styling — round buttons, consistent spacing."""

import ttkbootstrap as ttk


def apply_global_styles(app):
    """Apply modern round-button styles globally."""
    style = ttk.Style()
    c = app.colors

    # ── Round button base ──
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

    # ── Small round button ──
    style.configure(
        "RoundSm.TButton",
        font=("Segoe UI", 9),
        padding=(10, 5),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    # ── Icon-only round button ──
    style.configure(
        "RoundIcon.TButton",
        font=("Segoe UI", 9),
        padding=(6, 5),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    # ── Sidebar section header ──
    style.configure(
        "SidebarHeader.TLabel",
        font=("Segoe UI", 9, "bold"),
        padding=(4, 2),
    )

    # ── Status bar ──
    style.configure(
        "Status.TLabel",
        background=c["bg_tertiary"],
        foreground=c["fg_secondary"],
        font=("Segoe UI", 9),
        padding=(4, 2),
    )

    # ── Sidebar frame ──
    style.configure("Sidebar.TFrame", background=c["sidebar_bg"])
    style.configure("Editor.TFrame", background=c["editor_bg"])

    # ── Section frame with subtle border ──
    style.configure(
        "Section.TLabelframe",
        font=("Segoe UI", 9, "bold"),
        padding=6,
    )


def make_round_btn(parent, text, icon, command, style_name="info", icon_refs=None):
    """
    Create a round-styled button with icon, hover effect.
    Returns the button widget.
    """
    btn = ttk.Button(
        parent,
        text=f"  {text}" if text else "",
        image=icon,
        compound="left" if text else "image",
        command=command,
        bootstyle=f"{style_name}-outline",
        padding=(12, 6) if text else (7, 6),
        cursor="hand2",
    )

    # Keep icon reference alive
    if icon_refs is not None and icon:
        icon_refs.append(icon)

    # Hover animation
    original = f"{style_name}-outline"
    hover = style_name

    btn.bind("<Enter>", lambda e, b=btn, s=hover: b.configure(bootstyle=s))
    btn.bind("<Leave>", lambda e, b=btn, s=original: b.configure(bootstyle=s))

    return btn


def make_icon_btn(parent, icon, command, style_name="secondary", icon_refs=None):
    """Create a small icon-only round button."""
    btn = ttk.Button(
        parent,
        image=icon,
        command=command,
        bootstyle=f"{style_name}-link",
        padding=(4, 4),
        cursor="hand2",
    )

    if icon_refs is not None and icon:
        icon_refs.append(icon)

    return btn