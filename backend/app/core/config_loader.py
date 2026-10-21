import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

class ConfigurationLoader:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or settings.CONFIG_DIR)
        self.active_industry_id = settings.DEFAULT_INDUSTRY
        self._cached_industries: Dict[str, Dict[str, Any]] = {}
        self.reload_all()

    def reload_all(self) -> None:
        """Scan directory and reload all industry configurations into memory."""
        self._cached_industries.clear()
        if not self.config_dir.exists():
            return

        for industry_folder in self.config_dir.iterdir():
            if industry_folder.is_dir():
                industry_id = industry_folder.name
                config_data = self._load_industry_folder(industry_folder)
                if config_data:
                    self._cached_industries[industry_id] = config_data

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}

    def _load_industry_folder(self, folder: Path) -> Dict[str, Any]:
        industry_meta = self._load_yaml(folder / "industry.yaml")
        terminology = self._load_yaml(folder / "terminology.yaml")
        sources = self._load_yaml(folder / "sources.yaml")
        scenarios = self._load_yaml(folder / "scenarios.yaml")
        prompts = self._load_yaml(folder / "prompts.yaml")

        industry_id = industry_meta.get("id", folder.name)
        return {
            "id": industry_id,
            "metadata": industry_meta,
            "terminology": terminology.get("terms", {}),
            "sources": sources.get("sources", {}),
            "scenarios": scenarios.get("scenarios", []),
            "prompts": prompts.get("system_prompts", {})
        }

    def list_available_industries(self) -> List[Dict[str, Any]]:
        results = []
        for ind_id, ind_data in self._cached_industries.items():
            meta = ind_data.get("metadata", {})
            results.append({
                "id": ind_id,
                "name": meta.get("name", ind_id.title()),
                "description": meta.get("description", ""),
                "version": meta.get("version", "1.0.0"),
                "scenario_count": len(ind_data.get("scenarios", [])),
                "is_active": (ind_id == self.active_industry_id)
            })
        return results

    def get_active_industry(self) -> Dict[str, Any]:
        if self.active_industry_id not in self._cached_industries:
            # Fallback to first available if default not found
            if self._cached_industries:
                self.active_industry_id = next(iter(self._cached_industries.keys()))
            else:
                return {"id": "none", "metadata": {}, "terminology": {}, "sources": {}, "scenarios": [], "prompts": {}}
        return self._cached_industries[self.active_industry_id]

    def set_active_industry(self, industry_id: str) -> bool:
        if industry_id in self._cached_industries:
            self.active_industry_id = industry_id
            return True
        return False

# Global singleton configuration loader
config_loader = ConfigurationLoader()
