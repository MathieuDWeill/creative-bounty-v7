"""Contract tests for our expectations of the Genblaze result surface.

They do not call any provider and therefore cost nothing.
"""
from types import SimpleNamespace
from creative_bounty.provenance import summarize_genblaze_result


class FakeManifest:
    canonical_hash = "a" * 64
    def verify(self):
        return True


def test_provenance_contract_uses_canonical_manifest_hash_and_verify():
    asset=SimpleNamespace(url="b2://bucket/object.png", sha256="b"*64)
    run=SimpleNamespace(steps=[SimpleNamespace(assets=[asset])])
    result=SimpleNamespace(manifest=FakeManifest(), run=run)
    proof=summarize_genblaze_result(result)
    assert proof["canonical_manifest_hash"] == "a" * 64
    assert proof["manifest_verified"] is True
    assert proof["provider_url"] == "b2://bucket/object.png"
    assert proof["asset_sha256"] == "b" * 64
