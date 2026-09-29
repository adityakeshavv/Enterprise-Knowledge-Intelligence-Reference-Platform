from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from app.core.config import settings
from app.core.logging import logger

class IndustryConfigLoader:
    """Dynamic, generic YAML loader for Industry Configuration Packs."""

    def __init__(self, config_root: Optional[Path] = None):
        self.config_root = config_root or settings.CONFIG_DIR
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.reload_all()

    def reload_all(self):
        self._cache.clear()
        if not self.config_root.exists():
            logger.warning(f"Config root does not exist: {self.config_root}")
            return
            
        for industry_dir in self.config_root.iterdir():
            if industry_dir.is_dir():
                industry_id = industry_dir.name
                self._cache[industry_id] = self._load_single_pack(industry_dir)
                logger.info(f"Loaded industry pack: {industry_id}")

    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content or {}
        except Exception as e:
            logger.error(f"Error loading YAML from {path}: {e}")
            return {}

    def _load_single_pack(self, industry_dir: Path) -> Dict[str, Any]:
        pack = {
            "id": industry_dir.name,
            "industry": self._load_yaml_file(industry_dir / "industry.yaml"),
            "terminology": self._load_yaml_file(industry_dir / "terminology.yaml"),
            "sources": self._load_yaml_file(industry_dir / "sources.yaml"),
            "prompts": self._load_yaml_file(industry_dir / "prompts.yaml"),
            "scenarios": self._load_yaml_file(industry_dir / "scenarios.yaml"),
            "evaluation": self._load_yaml_file(industry_dir / "evaluation.yaml"),
        }
        return pack

    def get_industry_ids(self) -> List[str]:
        return list(self._cache.keys())

    def get_industry_pack(self, industry_id: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(industry_id)

    def list_industries_summary(self) -> List[Dict[str, Any]]:
        summaries = []
        for ind_id, pack in self._cache.items():
            ind_info = pack.get("industry", {})
            scenarios = pack.get("scenarios", {}).get("scenarios", [])
            summaries.append({
                "id": ind_id,
                "name": ind_info.get("name", ind_id.title()),
                "tagline": ind_info.get("tagline", ""),
                "badge_color": ind_info.get("badge_color", "blue"),
                "icon": ind_info.get("icon", "briefcase"),
                "version": ind_info.get("version", "1.0.0"),
                "kpis": ind_info.get("kpis", []),
                "scenarios_count": len(scenarios)
            })
        return summaries

config_loader = IndustryConfigLoader()
