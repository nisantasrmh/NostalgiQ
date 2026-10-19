"""Tests for Qloo client abstraction and factory switching."""

import pytest
from backend.qloo.base import BaseQlooClient
from backend.qloo.client import QlooClient
from backend.qloo.factory import get_qloo_client
from backend.qloo.mock_client import MockQlooClient


@pytest.mark.asyncio
async def test_mock_client_implements_base_interface():
    """Verify that MockQlooClient inherits from BaseQlooClient."""
    client = MockQlooClient()
    assert isinstance(client, BaseQlooClient)


@pytest.mark.asyncio
async def test_mock_client_search_entity():
    """Verify entity search returns results with 'source': 'MOCK'."""
    client = MockQlooClient()
    results = await client.search_entity("Bhimsen Joshi", domain="music")
    assert len(results) > 0
    for item in results:
        assert item["source"] == "MOCK"
        assert "title" in item
        assert "domain" in item


@pytest.mark.asyncio
async def test_mock_client_get_recommendations():
    """Verify recommendations return properly tagged items across domains."""
    client = MockQlooClient()
    seeds = ["seed_bhimsen_joshi", "seed_pune_1960s"]

    # Test music domain
    music_recs = await client.get_recommendations(
        seed_entity_ids=seeds,
        target_domain="music",
        era="1960s",
        region="Maharashtra",
        limit=3,
    )
    assert len(music_recs) > 0
    for rec in music_recs:
        assert rec["source"] == "MOCK"
        assert rec["domain"] == "music"

    # Test dining domain
    dining_recs = await client.get_recommendations(
        seed_entity_ids=seeds,
        target_domain="dining",
        region="Maharashtra",
        limit=3,
    )
    assert len(dining_recs) > 0
    for rec in dining_recs:
        assert rec["source"] == "MOCK"


def test_factory_switches_correctly():
    """Verify that get_qloo_client respects the use_mock flag."""
    mock_instance = get_qloo_client(use_mock=True)
    assert isinstance(mock_instance, MockQlooClient)

    real_instance = get_qloo_client(use_mock=False)
    assert isinstance(real_instance, QlooClient)
