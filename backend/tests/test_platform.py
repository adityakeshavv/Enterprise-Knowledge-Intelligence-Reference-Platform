import pytest
import asyncio
from pathlib import Path
from app.config_loader.loader import IndustryConfigLoader
from app.db.session import SafeDatabaseManager
from app.db.seed_mfg import seed_manufacturing_database
from app.core.security import create_access_token, decode_access_token, DEMO_USERS
from app.agents.router import QueryRouterAgent
from app.agents.data_agent import StructuredDataAgent
from app.agents.doc_agent import DocumentIntelligenceAgent
from app.agents.validation_agent import EvidenceValidationAgent
from app.agents.synthesis_agent import SynthesisAgent

@pytest.fixture(scope="module")
def setup_db(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("db")
    db_file = temp_dir / "test_mfg.db"
    seed_manufacturing_database(db_file)
    manager = SafeDatabaseManager(db_file)
    return manager

def test_industry_config_loading():
    """Verify both manufacturing and retail industry packs load cleanly."""
    loader = IndustryConfigLoader()
    ids = loader.get_industry_ids()
    assert "manufacturing" in ids
    assert "retail_cpg" in ids
    
    mfg_pack = loader.get_industry_pack("manufacturing")
    assert mfg_pack is not None
    assert mfg_pack["industry"]["name"] == "Industrial & Advanced Manufacturing"
    assert len(mfg_pack["scenarios"]["scenarios"]) >= 4

def test_safe_sql_ast_validator(setup_db):
    """Verify SQL AST validator strictly enforces read-only operations."""
    mgr = setup_db
    
    # Valid SELECT
    valid_sql = "SELECT line_id, actual_oee FROM production_lines WHERE plant_id = 'PLANT-A';"
    is_valid, _ = mgr.validate_sql_readonly(valid_sql)
    assert is_valid is True
    
    res = mgr.execute_query(valid_sql)
    assert res["success"] is True
    assert res["row_count"] > 0
    assert "line_id" in res["columns"]

    # Blocked DROP TABLE
    drop_sql = "DROP TABLE production_lines;"
    is_valid, msg = mgr.validate_sql_readonly(drop_sql)
    assert is_valid is False
    assert "Blocked" in msg

    # Blocked UPDATE
    update_sql = "UPDATE production_lines SET actual_oee = 1.0 WHERE line_id = 'LINE-01';"
    is_valid, msg = mgr.validate_sql_readonly(update_sql)
    assert is_valid is False
    assert "Blocked" in msg

    # Blocked INSERT
    insert_sql = "INSERT INTO production_lines VALUES ('X', 'Y', 'Z', 1.0, 1.0, 2026, 'OP');"
    is_valid, msg = mgr.validate_sql_readonly(insert_sql)
    assert is_valid is False
    assert "Blocked" in msg

def test_auth_and_token():
    """Verify JWT token encoding, decoding, and user payload."""
    user = DEMO_USERS["executive"]
    token = create_access_token(data={"sub": user["user_id"], "role": user["role"]})
    payload = decode_access_token(token)
    assert payload["sub"] == "usr_exec_01"
    assert payload["role"] == "Executive"

@pytest.mark.asyncio
async def test_multi_agent_pipeline():
    """Verify multi-agent flow: Router -> Data & Doc Agents -> Validation -> Synthesis."""
    seed_manufacturing_database()
    loader = IndustryConfigLoader()
    pack = loader.get_industry_pack("manufacturing")

    query = "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?"
    
    context = {
        "query": query,
        "industry_pack": pack,
        "user": DEMO_USERS["executive"]
    }

    # 1. Router
    router = QueryRouterAgent()
    r_res = await router.process(context)
    assert "StructuredDataAgent" in r_res["plan"]["agents_to_invoke"]
    assert "DocumentAgent" in r_res["plan"]["agents_to_invoke"]

    # 2. Data & Doc Agents
    data_agent = StructuredDataAgent()
    d_res = await data_agent.process(context)
    context["structured_data"] = d_res["structured_data"]
    context["sql_executed"] = d_res["sql_executed"]
    assert d_res["structured_data"]["success"] is True

    doc_agent = DocumentIntelligenceAgent()
    doc_res = await doc_agent.process(context)
    context["passages"] = doc_res["passages"]
    assert len(doc_res["passages"]) > 0

    # 3. Validation Agent (Should detect intentional Plant A root cause conflict)
    val_agent = EvidenceValidationAgent()
    val_res = await val_agent.process(context)
    assert val_res["grounding_score"] >= 0.8
    assert len(val_res["citations"]) >= 2
    assert len(val_res["conflicts"]) == 1
    assert val_res["conflicts"][0]["conflict_id"] == "cnf_line2_root_cause"

    # 4. Synthesis Agent
    synth_agent = SynthesisAgent()
    context["validation"] = val_res
    synth_res = await synth_agent.process(context)
    assert "Plant A" in synth_res["executive_summary"]
    assert len(synth_res["key_findings"]) >= 3
    assert len(synth_res["metrics_table"]["rows"]) > 0
