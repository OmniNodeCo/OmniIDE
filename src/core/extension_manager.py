"""VS Code Marketplace extension browser and installer."""

import json
import os
import threading
import urllib.request
import urllib.error
import zipfile
import io
import shutil

from src.config import (
    VSCODE_MARKETPLACE_URL,
    VSCODE_MARKETPLACE_VERSION,
    EXTENSIONS_DIR,
)


class ExtensionManager:
    """Search, download, and manage VS Code extensions."""

    def __init__(self, app):
        self.app = app
        self.installed = self._load_installed()
        self.search_results = []
        self._callbacks = {}

    def _load_installed(self):
        """Load list of installed extensions."""
        manifest_path = os.path.join(EXTENSIONS_DIR, "installed.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_installed(self):
        """Save installed extensions list."""
        manifest_path = os.path.join(EXTENSIONS_DIR, "installed.json")
        try:
            with open(manifest_path, "w") as f:
                json.dump(self.installed, f, indent=2)
        except Exception:
            pass

    def search(self, query, callback, page_size=15):
        """
        Search VS Code Marketplace.
        callback(results, error) called on main thread.
        """
        def _do_search():
            try:
                results = self._query_marketplace(query, page_size)
                self.app.root.after(0, callback, results, None)
            except Exception as e:
                self.app.root.after(0, callback, [], str(e))

        threading.Thread(target=_do_search, daemon=True).start()

    def _query_marketplace(self, query, page_size=15):
        """Query the VS Code Marketplace API."""
        payload = {
            "filters": [
                {
                    "criteria": [
                        {"filterType": 8, "value": "Microsoft.VisualStudio.Code"},
                        {"filterType": 10, "value": query},
                    ],
                    "pageNumber": 1,
                    "pageSize": page_size,
                    "sortBy": 0,
                    "sortOrder": 0,
                }
            ],
            "assetTypes": [],
            "flags": 950,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": f"application/json;api-version={VSCODE_MARKETPLACE_VERSION}",
            "User-Agent": "OmniIDE/1.0.1",
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            VSCODE_MARKETPLACE_URL,
            data=data,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        results = []
        try:
            extensions = body["results"][0]["extensions"]
        except (KeyError, IndexError):
            return results

        for ext in extensions:
            info = self._parse_extension(ext)
            if info:
                results.append(info)

        return results

    def _parse_extension(self, ext):
        """Parse extension data from API response."""
        try:
            name = ext.get("extensionName", "")
            publisher = ext.get("publisher", {}).get("publisherName", "")
            display_name = ext.get("displayName", name)
            short_desc = ext.get("shortDescription", "")
            ext_id = ext.get("extensionId", "")

            # Get version info
            versions = ext.get("versions", [])
            version = versions[0].get("version", "0.0.0") if versions else "0.0.0"

            # Get install count and rating
            stats = ext.get("statistics", [])
            installs = 0
            rating = 0
            for stat in stats:
                if stat.get("statisticName") == "install":
                    installs = int(stat.get("value", 0))
                elif stat.get("statisticName") == "averagerating":
                    rating = round(float(stat.get("value", 0)), 1)

            # Get icon URL
            icon_url = ""
            if versions:
                for file_info in versions[0].get("files", []):
                    if file_info.get("assetType") == "Microsoft.VisualStudio.Services.Icons.Default":
                        icon_url = file_info.get("source", "")
                        break

            # Get VSIX download URL
            vsix_url = ""
            if versions:
                for file_info in versions[0].get("files", []):
                    if file_info.get("assetType") == "Microsoft.VisualStudio.Services.VSIXPackage":
                        vsix_url = file_info.get("source", "")
                        break

            # Check if installed
            full_id = f"{publisher}.{name}"
            is_installed = any(
                e.get("id") == full_id for e in self.installed
            )

            return {
                "id": full_id,
                "name": display_name,
                "publisher": publisher,
                "description": short_desc,
                "version": version,
                "installs": installs,
                "rating": rating,
                "icon_url": icon_url,
                "vsix_url": vsix_url,
                "installed": is_installed,
                "extension_id": ext_id,
            }
        except Exception:
            return None

    def install_extension(self, ext_info, callback):
        """
        Download and install a VSIX extension.
        callback(success, message) called on main thread.
        """
        def _do_install():
            try:
                vsix_url = ext_info.get("vsix_url", "")
                if not vsix_url:
                    self.app.root.after(
                        0, callback, False, "No download URL available."
                    )
                    return

                ext_id = ext_info["id"]
                ext_dir = os.path.join(EXTENSIONS_DIR, ext_id)
                os.makedirs(ext_dir, exist_ok=True)

                # Download VSIX
                req = urllib.request.Request(
                    vsix_url,
                    headers={"User-Agent": "OmniIDE/1.0.1"},
                )

                with urllib.request.urlopen(req, timeout=60) as resp:
                    vsix_data = resp.read()

                # VSIX is a zip file — extract it
                with zipfile.ZipFile(io.BytesIO(vsix_data)) as zf:
                    zf.extractall(ext_dir)

                # Save metadata
                meta = {
                    "id": ext_id,
                    "name": ext_info["name"],
                    "publisher": ext_info["publisher"],
                    "version": ext_info["version"],
                    "description": ext_info["description"],
                }

                meta_path = os.path.join(ext_dir, "omniide_meta.json")
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)

                # Add to installed list
                if not any(e["id"] == ext_id for e in self.installed):
                    self.installed.append(meta)
                    self._save_installed()

                self.app.root.after(
                    0, callback, True,
                    f"Installed {ext_info['name']} v{ext_info['version']}"
                )

            except urllib.error.URLError as e:
                self.app.root.after(
                    0, callback, False, f"Network error: {e}"
                )
            except Exception as e:
                self.app.root.after(
                    0, callback, False, f"Install failed: {e}"
                )

        threading.Thread(target=_do_install, daemon=True).start()

    def uninstall_extension(self, ext_id):
        """Remove an installed extension."""
        ext_dir = os.path.join(EXTENSIONS_DIR, ext_id)
        try:
            if os.path.isdir(ext_dir):
                shutil.rmtree(ext_dir)

            self.installed = [
                e for e in self.installed if e.get("id") != ext_id
            ]
            self._save_installed()
            return True, f"Uninstalled {ext_id}"
        except Exception as e:
            return False, str(e)

    def get_installed(self):
        """Return list of installed extensions."""
        return self.installed.copy()

    @staticmethod
    def format_installs(count):
        """Format install count for display."""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)

    @staticmethod
    def format_rating(rating):
        """Format rating as stars."""
        full = int(rating)
        stars = "*" * full
        empty = "*" * (5 - full)
        return f"[{stars}{'.' * (5 - full)}] {rating}"