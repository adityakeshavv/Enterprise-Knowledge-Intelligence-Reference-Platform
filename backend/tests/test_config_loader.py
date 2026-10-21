import pytest
from app.core.config_loader import ConfigurationLoader

def test_config_loader_discovers_industries():
    loader = ConfigurationLoader()
    industries = loader.list_available_industries()
    assert len(industries) >= 2
    
    industry_ids = [ind["id"] for ind in industries]
    assert "manufacturing" in industry_ids
    assert "retail_cpg" in industry_ids

def test_manufacturing_config_content():
    loader = ConfigurationLoader()
    loader.set_active_industry("manufacturing")
    active = loader.get_active_industry()
    
    assert active["id"] == "manufacturing"
    assert "OEE" in active["terminology"]
    assert "MTBF" in active["terminology"]
    assert len(active["scenarios"]) >= 3
    assert active["scenarios"][0]["id"] == "mfg-downtime-factors"

def test_dynamic_industry_switch():
    loader = ConfigurationLoader()
    assert loader.set_active_industry("retail_cpg") is True
    assert loader.active_industry_id == "retail_cpg"
    
    active = loader.get_active_industry()
    assert active["id"] == "retail_cpg"
    assert "SKU" in active["terminology"]
    
    # Switching back to manufacturing
    assert loader.set_active_industry("manufacturing") is True
    assert loader.active_industry_id == "manufacturing"

def test_invalid_industry_switch():
    loader = ConfigurationLoader()
    assert loader.set_active_industry("non_existent_sector") is False
