"""Professional Reference Import System — V1.6."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.ziwei.reference.metadata import sample_template
from app.ziwei.reference.validator import validate_sample

DEFAULT_SAMPLES_DIR = Path(__file__).resolve().parent / "samples"


class ReferenceImporter:
    def __init__(self, samples_dir: Path | None = None) -> None:
        self.samples_dir = samples_dir or DEFAULT_SAMPLES_DIR
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, sample_id: str) -> Path:
        return self.samples_dir / f"{sample_id}.json"

    def load(self, sample_id: str) -> dict[str, Any]:
        path = self.path_for(sample_id)
        if not path.exists():
            raise FileNotFoundError(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, sample: dict[str, Any], *, overwrite: bool = True) -> Path:
        sid = sample.get("id")
        if not sid:
            raise ValueError("sample.id required")
        v = validate_sample(sample)
        if sample.get("verification_level") == "verified_professional" and not v["ok"]:
            raise ValueError(f"invalid professional sample: {v['errors']}")
        path = self.path_for(sid)
        if path.exists() and not overwrite:
            raise FileExistsError(path)
        path.write_text(json.dumps(sample, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._upsert_index(sample)
        return path

    def import_dict(self, payload: dict[str, Any]) -> dict[str, Any]:
        """导入并校验，返回 {path, validation, sample}。"""
        sample = dict(payload)
        sample.setdefault("verification_level", "pending")
        sample.setdefault("settings", {"calendar": "solar", "school": "sanhe", "tianfu_rule": "traditional"})
        validation = validate_sample(sample)
        path = self.save(sample) if validation["ok"] or sample.get("verification_level") == "pending" else None
        if path is None and not validation["ok"]:
            raise ValueError(validation["errors"])
        if path is None:
            path = self.save(sample)
        return {"path": str(path), "validation": validation, "sample": sample}

    def list_samples(
        self,
        *,
        level: str | None = None,
        professional_only: bool = False,
    ) -> list[dict[str, Any]]:
        index_path = self.samples_dir / "index.json"
        if index_path.exists():
            rows = json.loads(index_path.read_text(encoding="utf-8")).get("cases", [])
            ids = [r["id"] for r in rows]
        else:
            ids = sorted(p.stem for p in self.samples_dir.glob("SC-P*.json"))
        out = []
        for sid in ids:
            try:
                s = self.load(sid)
            except FileNotFoundError:
                continue
            lv = s.get("verification_level") or "pending"
            if professional_only and lv != "verified_professional":
                continue
            if level and lv != level:
                continue
            out.append(s)
        return out

    def create_pending_slot(self, sample_id: str, **birth_kwargs: Any) -> dict[str, Any]:
        sample = sample_template(sample_id, **birth_kwargs)
        self.save(sample)
        return sample

    def _upsert_index(self, sample: dict[str, Any]) -> None:
        index_path = self.samples_dir / "index.json"
        if index_path.exists():
            index = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            index = {"version": "1.6", "description": "Professional wenmo reference samples", "cases": []}
        entry = {
            "id": sample["id"],
            "source": sample.get("source"),
            "verification_level": sample.get("verification_level", "pending"),
            "birth": sample.get("birth"),
            "file": f"{sample['id']}.json",
        }
        cases = index.setdefault("cases", [])
        for i, row in enumerate(cases):
            if row.get("id") == sample["id"]:
                cases[i] = entry
                break
        else:
            cases.append(entry)
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
