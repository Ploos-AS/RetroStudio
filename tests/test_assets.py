from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from retrostudio.assets import (
    ASSET_KINDS,
    Asset,
    ContentCache,
    ConversionRequest,
    ResourceUsage,
    budget_diagnostics,
    hash_bytes,
    hash_file,
)


class AssetPipelineTests(unittest.TestCase):
    def test_baseline_asset_kinds(self) -> None:
        self.assertEqual(ASSET_KINDS, {"image", "palette", "tilemap", "audio"})

    def test_asset_validation(self) -> None:
        self.assertEqual(Asset("hero", "image", "assets/hero.png").validate(), [])
        diagnostics = Asset("bad", "video", "assets/intro.mp4").validate()
        self.assertEqual([item.code for item in diagnostics], ["asset.kind_unknown"])

    def test_hash_bytes_and_file_match(self) -> None:
        payload = b"RetroStudio M3\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "asset.bin"
            path.write_bytes(payload)
            self.assertEqual(hash_bytes(payload), hash_file(path))

    def test_conversion_cache_key_is_deterministic_and_backend_sensitive(self) -> None:
        asset = Asset("hero", "image", "assets/hero.png", {"role": "sprite"})
        request_a = ConversionRequest(asset, "machine-a", options={"bpp": 4, "dither": False})
        request_b = ConversionRequest(asset, "machine-a", options={"dither": False, "bpp": 4})
        digest = hash_bytes(b"source")
        key_a = request_a.cache_key(digest, "dummy", "1")
        key_b = request_b.cache_key(digest, "dummy", "1")
        self.assertEqual(key_a, key_b)
        self.assertNotEqual(key_a, request_a.cache_key(digest, "dummy", "2"))

    def test_content_cache_round_trip(self) -> None:
        key = hash_bytes(b"converted")
        with tempfile.TemporaryDirectory() as tmp:
            cache = ContentCache(tmp)
            self.assertFalse(cache.contains(key))
            cache.put(key, b"converted")
            self.assertTrue(cache.contains(key))
            self.assertEqual(cache.get(key), b"converted")

    def test_content_cache_rejects_invalid_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache = ContentCache(tmp)
            with self.assertRaises(ValueError):
                cache.get("not-a-sha256")

    def test_budget_diagnostics(self) -> None:
        usages = [
            ResourceUsage("graphics-memory", 1024, 2048),
            ResourceUsage("audio-memory", 4096, 2048, path="assets/music.mod"),
        ]
        diagnostics = budget_diagnostics(usages)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].code, "budget.exceeded")
        self.assertEqual(diagnostics[0].path, "assets/music.mod")


if __name__ == "__main__":
    unittest.main()
