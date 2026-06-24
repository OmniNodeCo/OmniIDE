"""Extension manager — downloads VSIX from VS Code Marketplace."""

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

    def _load_installed(self):
        manifest = os.path.join(EXTENSIONS_DIR, "installed.json")
        if os.path.exists(manifest):
            try:
                with open(manifest, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_installed(self):
        manifest = os.path.join(EXTENSIONS_DIR, "installed.json")
        try:
            with open(manifest, "w") as f:
                json.dump(self.installed, f, indent=2)
        except Exception:
            pass

    def search(self, query, callback, page_size=15):
        def _do():
            try:
                results = self._query(query, page_size)
                # Use QTimer for thread safety
                from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
                self.app.statusbar.set_text(f"Found {len(results)} extensions")
                callback(results, None)
            except Exception as e:
                callback([], str(e))

        threading.Thread(target=_do, daemon=True).start()

    def _query(self, query, page_size=15):
        payload = {
            "filters": [{
                "criteria": [
                    {"filterType": 8, "value": "Microsoft.VisualStudio.Code"},
                    {"filterType": 10, "value": query},
                ],
                "pageNumber": 1,
                "pageSize": page_size,
                "sortBy": 0,
                "sortOrder": 0,
            }],
            "assetTypes": [],
            "flags": 950,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": f"application/json;api-version={VSCODE_MARKETPLACE_VERSION}",
            "User-Agent": "OmniIDE/1.0.4",
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(VSCODE_MARKETPLACE_URL, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        results = []
        try:
            extensions = body["results"][0]["extensions"]
        except (KeyError, IndexError):
            return results

        for ext in extensions:
            info = self._parse(ext)
            if info:
                results.append(info)
        return results

    def _parse(self, ext):
        try:
            name = ext.get("extensionName", "")
            publisher = ext.get("publisher", {}).get("publisherName", "")
            display = ext.get("displayName", name)
            desc = ext.get("shortDescription", "")

            versions = ext.get("versions", [])
            version = versions[0].get("version", "0.0.0") if versions else "0.0.0"

            stats = ext.get("statistics", [])
            installs = 0
            for s in stats:
                if s.get("statisticName") == "install":
                    installs = int(s.get("value", 0))

            # VSIX download URL
            vsix_url = ""
            if versions:
                for f in versions[0].get("files", []):
                    if f.get("assetType") == "Microsoft.VisualStudio.Services.VSIXPackage":
                        vsix_url = f.get("source", "")
                        break

            full_id = f"{publisher}.{name}"
            is_installed = any(e.get("id") == full_id for e in self.installed)

            return {
                "id": full_id,
                "name": display,
                "publisher": publisher,
                "description": desc,
                "version": version,
                "installs": installs,
                "vsix_url": vsix_url,
                "installed": is_installed,
            }
        except Exception:
            return None

    def install_extension(self, ext_info, callback):
        def _do():
            try:
                vsix_url = ext_info.get("vsix_url", "")
                if not vsix_url:
                    callback(False, "No download URL")
                    return

                ext_id = ext_info["id"]
                ext_dir = os.path.join(EXTENSIONS_DIR, ext_id)
                os.makedirs(ext_dir, exist_ok=True)

                # Download VSIX
                req = urllib.request.Request(vsix_url, headers={"User-Agent": "OmniIDE/1.0.4"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    vsix_data = resp.read()

                # Extract — VSIX is a zip
                with zipfile.ZipFile(io.BytesIO(vsix_data)) as zf:
                    zf.extractall(ext_dir)

                # Read package.json from the extension
                pkg_json = None
                for root, dirs, files in os.walk(ext_dir):
                    if "package.json" in files:
                        pkg_path = os.path.join(root, "package.json")
                        try:
                            with open(pkg_path, "r", encoding="utf-8") as f:
                                pkg_json = json.load(f)
                        except Exception:
                            pass
                        break

                # Save metadata
                meta = {
                    "id": ext_id,
                    "name": ext_info["name"],
                    "publisher": ext_info["publisher"],
                    "version": ext_info["version"],
                    "description": ext_info.get("description", ""),
                    "dir": ext_dir,
                }

                if pkg_json:
                    meta["contributes"] = pkg_json.get("contributes", {})
                    meta["engines"] = pkg_json.get("engines", {})

                meta_path = os.path.join(ext_dir, "omniide_meta.json")
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)

                if not any(e["id"] == ext_id for e in self.installed):
                    self.installed.append(meta)
                    self._save_installed()

                callback(True, f"Installed {ext_info['name']} v{ext_info['version']}")

            except Exception as e:
                callback(False, f"Install failed: {e}")

        threading.Thread(target=_do, daemon=True).start()

    def uninstall_extension(self, ext_id):
        ext_dir = os.path.join(EXTENSIONS_DIR, ext_id)
        try:
            if os.path.isdir(ext_dir):
                shutil.rmtree(ext_dir)
            self.installed = [e for e in self.installed if e.get("id") != ext_id]
            self._save_installed()
            return True, f"Uninstalled {ext_id}"
        except Exception as e:
            return False, str(e)

    def get_installed(self):
        return self.installed.copy()

    def get_extension_contributes(self, ext_id):
        """Get what an installed extension contributes (themes, languages, snippets)."""
        ext_dir = os.path.join(EXTENSIONS_DIR, ext_id)
        meta_path = os.path.join(ext_dir, "omniide_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
                return meta.get("contributes", {})
            except Exception:
                pass
        return {}

    @staticmethod
    def format_installs(count):
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)

    @staticmethod
    def format_rating(rating):
        return f"{rating}"