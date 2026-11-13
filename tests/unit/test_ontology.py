"""Process ontology (frontier-process): seed from the blueprint, Fabric ontology (preview) rules, Turtle export,
design documents, the grounding in the Common Data Model, the semantic data layer, data products, the blueprint's
Ontology page data and workshop verdicts."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

SK = "plugin/skills/frontier-process"
lib = load(f"{SK}/scripts/ontology_lib.py", "on_lib")
seed = load(f"{SK}/scripts/seed_ontology.py", "on_seed")
build = load(f"{SK}/scripts/build_ontology.py", "on_build")
apply_ = load(f"{SK}/scripts/apply_ontology.py", "on_apply")
merge = load(f"{SK}/scripts/merge_ontology_feedback.py", "on_merge")
bpbuild = load("plugin/skills/frontier-blueprint/scripts/build_blueprint.py", "on_bpbuild")
BLUEPRINT = ROOT / "plugin/skills/frontier-blueprint/examples/caldova-blueprint.json"
EXAMPLE = ROOT / SK / "examples/caldova-ontology.json"


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = fn(*a)
    return code, out.getvalue()


def normalized_blueprint(tmp: Path) -> Path:
    quiet(bpbuild.main, ["--data", str(BLUEPRINT), "--out", str(tmp / "bp.html"), "--save-normalized", str(tmp / "bp.json")])
    return tmp / "bp.json"


def mini():
    return {"meta": {"short": "Acme"}, "namespaces": [{"id": "core"}, {"id": "svc", "journey": "D1"}],
            "entity_types": [
                {"id": "Asset", "namespace": "core", "key": ["assetId"], "properties": [{"name": "assetId", "type": "string"}, {"name": "status", "type": "string"}],
                 "timeseries": [{"name": "temperature", "type": "double", "unit": "C"}], "source": "s-fs"},
                {"id": "WorkOrder", "name": "Work order", "namespace": "svc", "key": ["workOrderId"], "synonyms": ["Job"],
                 "properties": [{"name": "workOrderId", "type": "string"}, {"name": "status", "type": "string"}, {"name": "cost", "type": "decimal"}], "source": "s-fs"}],
            "relationship_types": [{"name": "concerns", "from": "WorkOrder", "to": "Asset", "cardinality": "n:1"}],
            "sources": [{"id": "s-fs", "name": "Field Service", "path": "shortcut"}],
            "rules": ["A work order is closed only after the technician confirms it."],
            "data_agents": [{"name": "Service data agent", "entities": ["WorkOrder", "Asset"], "questions": ["Which work orders are open?"]}]}


class Rules(unittest.TestCase):
    def test_normalize_completes_and_counts(self):
        rep = lib.Rep()
        o = lib.normalize(mini(), None, rep)
        self.assertEqual(rep.errors, [])
        self.assertEqual(o["relationship_types"][0]["id"], "WorkOrder_concerns_Asset")
        self.assertEqual(o["entity_types"][1]["properties"][2]["type"], "double", "decimal maps to double")
        self.assertEqual(o["sources"][0]["item"], "lakehouse", "a shortcut lands in a lakehouse")
        self.assertEqual(o["data_agents"][0]["sources"], ["ontology"])
        self.assertEqual(o["rules"][0]["id"], "RU-01")
        self.assertEqual(o["stats"]["timeseries"], 1)
        self.assertTrue(o["readiness"] and o["risks"] and o["sources_doc"], "canon blocks added")

    def test_fabric_rules_are_enforced(self):
        bad = mini()
        bad["entity_types"][0]["key"] = ["temperature"]
        bad["entity_types"][1]["properties"].append({"name": "assetId", "type": "integer"})
        bad["entity_types"].append({"id": "2Bad", "properties": []})
        bad["relationship_types"].append({"name": "x", "from": "WorkOrder", "to": "Nope"})
        bad["data_agents"][0]["sources"] = ["ontology", "a", "b", "c", "d", "e"]
        rep = lib.Rep()
        lib.normalize(bad, None, rep)
        text = " | ".join(rep.errors)
        for part in ("key Asset.temperature is not a static property", "property name 'assetId' is string", "'2Bad' must start with a letter",
                     "connects unknown entity types", "has 6 sources: a Fabric data agent uses up to 5"):
            self.assertIn(part, text)

    def test_semantic_model_binding_warns_for_agents(self):
        o = mini()
        o["sources"].append({"id": "s-sm", "name": "Service KPIs", "path": "semantic model"})
        o["entity_types"][1]["source"] = "s-sm"
        rep = lib.Rep()
        lib.normalize(o, None, rep)
        self.assertTrue(any("known issue" in w for w in rep.warnings))


class Turtle(unittest.TestCase):
    def test_owl_subset_for_the_fabric_import(self):
        o = lib.normalize(mini())
        ttl = lib.to_turtle(o)
        self.assertIn("@prefix owl: <http://www.w3.org/2002/07/owl#> .", ttl)
        self.assertIn(":WorkOrder a owl:Class ;", ttl)
        self.assertIn('skos:altLabel "Job"', ttl)
        self.assertIn(":WorkOrder_workOrderId a owl:DatatypeProperty ;\n  rdfs:label \"workOrderId\" ;\n  rdfs:domain :WorkOrder ;\n  rdfs:range xsd:string", ttl)
        self.assertIn(":WorkOrder_concerns_Asset a owl:ObjectProperty ;", ttl)
        self.assertIn("rdfs:range xsd:double", ttl)
        self.assertIn("Time series (C)", ttl)
        # every statement ends with " ." and strings are balanced
        stmts = [s for s in re.split(r"\n(?=:|<)", ttl.split("\n\n", 1)[1]) if s.strip() and not s.startswith("#")]
        for st in stmts:
            self.assertTrue(st.rstrip().endswith("."), st[:60])
            self.assertEqual(st.count('"') % 2, 0, st[:60])

    def test_escaping_and_namespace(self):
        o = mini()
        o["entity_types"][1]["description"] = 'Line one\nwith "quotes" and \\ backslash'
        o["meta"]["namespace_uri"] = "https://caldova.example/onto#"
        ttl = lib.to_turtle(lib.normalize(o))
        self.assertIn('rdfs:comment "Line one\\nwith \\"quotes\\" and \\\\ backslash Key: workOrderId. Dataverse, Dynamics 365 Field Service: Work Order (msdyn_workorder)."', ttl)
        self.assertIn("@prefix : <https://caldova.example/onto#> .", ttl)


class Caldova(unittest.TestCase):
    def test_seed_from_the_blueprint(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            bp = normalized_blueprint(t)
            code, out = quiet(seed.main, ["--blueprint", str(bp), "--out", str(t / "o.json")])
            self.assertEqual(code, 0, out)
            res = json.loads(out)
            o = json.loads((t / "o.json").read_text(encoding="utf-8"))
        self.assertEqual(res["patterns"], {"commercial": "lead-to-order", "procurement": "source-to-pay", "service": "request-to-resolution", "finance": "record-to-report"})
        ids = {e["id"] for e in o["entity_types"]}
        self.assertTrue({"Customer", "Opportunity", "Quote", "SalesOrder", "Supplier", "PurchaseOrder", "WorkOrder", "AlarmEvent", "LedgerAccount"} <= ids)
        sap = next(s for s in o["sources"] if s["id"] == "src-sap-s-4hana")
        self.assertEqual((sap["path"], sap["item"]), ("mirroring", "mirrored database"))
        self.assertIn("FI/CO", sap["system"])
        iot = next(s for s in o["sources"] if s["id"] == "src-iot-platform")
        self.assertEqual(iot["item"], "eventhouse")
        self.assertFalse(any("sharepoint" in s["id"] for s in o["sources"]), "documents stay with Foundry IQ")
        asset = next(e for e in o["entity_types"] if e["id"] == "Asset")
        self.assertEqual(asset["source"], "src-dynamics-365-field-service", "static data first")
        self.assertIn("src-iot-platform", asset["secondary"], "time series from the eventhouse")
        self.assertEqual(next(e for e in o["entity_types"] if e["id"] == "AlarmEvent")["source"], "src-iot-platform")
        das = {a["journey"]: a for a in o["data_agents"]}
        self.assertEqual(das["D3"]["name"], "Service Data Agent")
        self.assertEqual({p["name"]: p["note"] for p in das["D3"]["products"]}["Knowledge articles"], "documents: Foundry IQ")
        self.assertEqual(len(o["operations_agents"]), 1)
        self.assertEqual(o["operations_agents"][0]["actions"][0]["approver"], "Planner")
        self.assertIn("E05", next(e for e in o["entity_types"] if e["id"] == "Asset")["src"])

    def test_example_builds_and_applies(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            bp = normalized_blueprint(t)
            code, out = quiet(build.main, ["--ontology", str(EXAMPLE), "--blueprint", str(bp), "--out-dir", str(t / "out")])
            self.assertEqual(code, 0, out)
            res = json.loads(out)
            self.assertEqual(res["stats"]["entity_types"], 27)
            self.assertEqual(res["warnings"], ["entity type Employee has no data binding yet"])
            md = (t / "out/ontology.md").read_text(encoding="utf-8")
            kit = (t / "out/data-agents.md").read_text(encoding="utf-8")
            ttl = (t / "out/ontology.ttl").read_text(encoding="utf-8")
            self.assertEqual(ttl.count(" a owl:Class"), 27)
            self.assertEqual(ttl.count(" a owl:ObjectProperty"), 33)
            for part in ("## 4 Grounding in the Common Data Model", "## 6 Semantic data layer", "## 7 Data products", "```mermaid", "erDiagram",
                         "## 11 Build it in Fabric IQ", "learn.microsoft.com/en-us/fabric/iq/ontology/overview", "learn.microsoft.com/en-us/common-data-model/"):
                self.assertIn(part, md)
            self.assertIn("## DA-03 · Service Data Agent", kit)
            self.assertIn("Support group by in GQL.", kit)
            code, out = quiet(apply_.main, ["--blueprint", str(bp), "--ontology", str(t / "out/ontology.normalized.json"), "--out", str(t / "bp2.json")])
            self.assertEqual(code, 0, out)
            b2 = json.loads((t / "bp2.json").read_text(encoding="utf-8"))
        onto = b2["ontology"]
        self.assertNotIn("ttl", onto, "the page writes the Turtle itself")
        self.assertNotIn("kit", onto)
        self.assertTrue(all(a.get("instructions") or a.get("instructions_default") for a in onto["data_agents"]))
        group = next(g for g in b2["it_readiness"]["groups"] if g["id"] == "fabric-iq")
        self.assertEqual(len(group["items"]), 15)
        self.assertEqual(len(onto["data_products"]), 19)
        self.assertEqual([m["name"] for m in onto["semantic_models"]], ["Commercial model", "Procurement model", "Service model", "Finance close (Power BI)"])
        svc = next(p for p in onto["process"] if p["journey"] == "D3")
        self.assertEqual([s["entities"] for s in svc["stages"]][0], ["ServiceRequest", "AlarmEvent"])

    def test_risks_and_verdicts(self):
        risks = load("plugin/skills/frontier-blueprint/scripts/risks.py", "on_risks")
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            bp = json.loads(normalized_blueprint(t).read_text(encoding="utf-8"))
            rep = lib.Rep()
            bp = apply_.apply(bp, json.loads(EXAMPLE.read_text(encoding="utf-8")), rep)
            reg = risks.fill_risks(bp)
            ont = [r for r in reg["items"] if r["origin"] == "ontology"]
            self.assertEqual(sorted(r["id"] for r in ont), ["R-ONT-1", "R-ONT-2", "R-ONT-3", "R-ONT-4", "R-ONT-5", "R-ONT-6", "R-ONT-7"])
            fb = {"type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                  "validations": {"onto:WorkOrder": {"status": "validated", "note": "Key confirmed by the service applications lead"},
                                  "onto:DA-03": {"status": "adjusted", "note": "Add parts availability"}, "onto:model": {"status": "validated"},
                                  "onto:Nope": {"status": "validated"}, "risk:R-01": {"status": "open"}}}
            (t / "fb.json").write_text(json.dumps(fb), encoding="utf-8")
            code, out = quiet(merge.main, ["--ontology", str(EXAMPLE), "--feedback", str(t / "fb.json"), "--out", str(t / "o2.json")])
            self.assertEqual(code, 0, out)
            res = json.loads(out)
            o2 = json.loads((t / "o2.json").read_text(encoding="utf-8"))
        self.assertEqual((res["changed"], res["unknown"], res["version"]), (3, ["onto:Nope"], "0.2"))
        self.assertEqual(next(e for e in o2["entity_types"] if e["id"] == "WorkOrder")["status"], "validated")
        self.assertEqual(next(a for a in o2["data_agents"] if a["id"] == "DA-03")["status"], "adjusted")
        self.assertEqual(o2["meta"]["status"], "validated")


class SemanticModel(unittest.TestCase):
    def test_tmsl_tables_relationships_and_measures(self):
        model = {"name": "Service KPIs", "model": {"tables": [
            {"name": "WorkOrders", "columns": [{"name": "WorkOrderID", "dataType": "string"}, {"name": "Hours", "dataType": "decimal"}, {"name": "AssetID", "dataType": "string"}],
             "measures": [{"name": "First Time Fix %", "expression": "DIVIDE(...)"}]},
            {"name": "Machines", "columns": [{"name": "AssetID", "dataType": "string"}, {"name": "Installed", "dataType": "dateTime"}]},
            {"name": "Date", "columns": [{"name": "Date", "dataType": "dateTime"}]}],
            "relationships": [{"fromTable": "WorkOrders", "fromColumn": "AssetID", "toTable": "Machines", "toColumn": "AssetID"}]}}
        o = {"namespaces": [{"id": "core"}], "entity_types": [], "relationship_types": [], "metrics": [], "sources": []}
        rep = lib.Rep()
        added = seed.add_semantic_model(o, model, None, rep)
        self.assertEqual(added, {"entities": 2, "merged": 0, "relationships": 1, "metrics": 1})
        ids = [e["id"] for e in o["entity_types"]]
        self.assertEqual(ids, ["WorkOrders", "Machines"], "the date table is skipped")
        self.assertEqual(o["entity_types"][1]["key"], ["assetID"])
        self.assertEqual(o["metrics"][0]["measure"], "[First Time Fix %]")
        self.assertTrue(any("known issue" in w for w in rep.warnings))
        n = lib.normalize(o, None, lib.Rep())
        self.assertEqual(n["sources"][0]["item"], "semantic model")


class SemanticAncestry(unittest.TestCase):
    def model(self):
        return {
            "entity_types": [{"id": "Fact", "source": "shared-source"},
                             {"id": "Dimension", "source": "shared-source"}],
            "sources": [{"id": "shared-source"}],
            "semantic_models": [{"id": "SM-TEST", "facts": ["Fact"], "dimensions": ["Dimension", "Date"]}],
            "data_products": [{"id": "DP-TEST", "uses": [{"use": "analytics", "via": ["SM-TEST"]}]}],
        }

    def test_semantic_fact_dimension_anchors_retain_private_ancestry_and_retirement(self):
        for field, index in (("facts", 0), ("dimensions", 1)):
            with self.subTest(field=field):
                model = self.model()
                model["entity_types"][index]["visibility"] = "internal"
                before = copy.deepcopy(model)
                anchors = lib.feedback_ancestry(model, "DP-TEST")
                keys = [(row["pool"], row["id"]) for row in anchors]
                for key in (("entity_types", "Fact"), ("entity_types", "Dimension"), ("sources", "shared-source")):
                    self.assertIn(key, keys)
                self.assertEqual(keys, sorted(set(keys)), "shared acyclic joins remain unique and canonically ordered")
                self.assertNotIn(("unresolved", "Date"), keys)
                verdict = {"id": "DP-TEST", "target_ancestry": anchors}
                self.assertEqual(lib.feedback_privacy(model, verdict), (True, []))
                self.assertEqual(model, before)
                model["data_products"] = []
                self.assertEqual(lib.feedback_privacy(model, verdict), (True, []),
                                 "retiring only the target cannot erase its private dependency ancestry")

    def test_unknown_semantic_fact_dimension_are_unresolved_but_date_remains_builtin(self):
        for field in ("facts", "dimensions"):
            with self.subTest(field=field):
                model = self.model()
                model["semantic_models"][0][field] = ["MISSING-ENTITY"] + (["Date"] if field == "dimensions" else [])
                anchors = lib.feedback_ancestry(model, "DP-TEST")
                unresolved = [row["id"] for row in anchors if row.get("unresolved")]
                self.assertEqual(unresolved, ["MISSING-ENTITY"])
                restricted, gaps = lib.feedback_privacy(model, {"id": "DP-TEST", "target_ancestry": anchors})
                self.assertTrue(restricted)
                self.assertIn("unresolved:MISSING-ENTITY", gaps)


class StrictTypedReferences(unittest.TestCase):
    def fixture(self):
        model = mini()
        model["data_agents"][0].update(id="DA-01", sources=["s-fs"],
                                       consumers=[{"kind": "copilot_studio", "agents": ["BP-AGENT"]}])
        model["operations_agents"] = [{"id": "OA-01", "entities": ["Asset"], "rules": ["Synthetic rule"]}]
        model["semantic_models"] = [{"id": "SM-01", "facts": ["WorkOrder"], "dimensions": ["Asset", "Date"]}]
        model["data_products"] = [{"id": "DP-01", "entities": ["Asset"], "agents": ["DA-01"],
                                   "uses": [{"use": "analytics", "via": ["SM-01"]}]}]
        model["metrics"] = [{"id": "M-01", "name": "Synthetic metric", "entity": "WorkOrder"}]
        bp = {"domains": [{"id": "D1", "agents": [{"id": "BP-AGENT"}]}]}
        return model, bp

    def operation(self):
        operation = getattr(lib, "strict_reference_graph", None)
        self.assertTrue(callable(operation), "an opt-in schema-specific process reference helper is required")
        return operation

    def test_strict_graph_is_pure_typed_deterministic_and_keeps_date_builtin(self):
        model, bp = self.fixture()
        before = copy.deepcopy((model, bp))
        result = self.operation()(model, bp)
        graph = result["edges"]
        self.assertIn(("blueprint.agents", "BP-AGENT"), graph[("data_agents", "DA-01")])
        self.assertIn(("sources", "s-fs"), graph[("data_agents", "DA-01")])
        self.assertIn(("entity_types", "Asset"), graph[("semantic_models", "SM-01")])
        self.assertNotIn(("entity_types", "Date"), graph[("semantic_models", "SM-01")])
        self.assertIn(("semantic_models", "SM-01"), graph[("data_products", "DP-01")])
        self.assertEqual(result, self.operation()(model, bp))
        self.assertEqual((model, bp), before)

    def test_strict_graph_rejects_wrong_pools_and_original_invalid_consumers(self):
        mutations = (
            lambda m: m["data_agents"][0]["consumers"][0].update(agents=["Asset"]),
            lambda m: m["data_agents"][0]["consumers"][0].update(kind="INVALID", agents=["NO-AGENT"]),
            lambda m: m["data_agents"][0].update(entities=["s-fs"]),
            lambda m: m["data_agents"][0].update(sources=["Asset"]),
            lambda m: m["entity_types"][0].update(source="WorkOrder"),
            lambda m: m["entity_types"][0].update(namespace="Asset"),
            lambda m: m["entity_types"][0].update(base="s-fs"),
            lambda m: m["relationship_types"][0].update(to="s-fs"),
            lambda m: m["semantic_models"][0].update(dimensions=["s-fs", "Date"]),
            lambda m: m["metrics"][0].update(entity="s-fs"),
            lambda m: m["data_products"][0].update(agents=["SM-01"]),
            lambda m: m["data_products"][0]["uses"][0].update(via=["DA-01"]),
        )
        operation = self.operation()
        for mutate in mutations:
            model, bp = self.fixture()
            mutate(model)
            before = copy.deepcopy((model, bp))
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                operation(model, bp)
            self.assertEqual((model, bp), before)

    def test_same_spelling_in_another_namespace_does_not_change_the_typed_edge(self):
        model, bp = self.fixture()
        bp["domains"][0]["agents"].append({"id": "Asset"})
        model["data_agents"][0]["consumers"][0]["agents"] = ["Asset"]
        model["data_agents"][0]["entities"] = ["WorkOrder"]
        model["semantic_models"].append({"id": "DA-01", "dimensions": ["Date"]})
        graph = self.operation()(model, bp)["edges"]
        self.assertIn(("blueprint.agents", "Asset"), graph[("data_agents", "DA-01")])
        self.assertNotIn(("entity_types", "Asset"), graph[("data_agents", "DA-01")])
        self.assertIn(("data_agents", "DA-01"), graph[("data_products", "DP-01")])
        self.assertNotIn(("semantic_models", "DA-01"), graph[("data_products", "DP-01")])

    def test_reached_blueprint_domain_node_keeps_parent_metadata_not_sibling_agents(self):
        model, bp = self.fixture()
        domain = bp["domains"][0]
        domain.update(sharingClassification="customer-specific", customer_scope="synthetic-owner-scope",
                      ownership={"source_id": "OWNER-EVIDENCE"},
                      data_agent={"id": "UNRELATED-DATA-AGENT", "internal": True})
        model["data_agents"][0]["journey"] = "D1"
        before = copy.deepcopy((model, bp))
        graph = self.operation()(model, bp)
        self.assertIn(("blueprint.domains", "D1"), graph["edges"][("data_agents", "DA-01")])
        header = graph["nodes"][("blueprint.domains", "D1")]
        self.assertEqual(header["ownership"], domain["ownership"])
        self.assertEqual(header["customer_scope"], "synthetic-owner-scope")
        for field in ("agents", "lead", "orchestrator", "data_agent"):
            self.assertNotIn(field, header, "a reached parent is not all its unrelated children")
        self.assertEqual((model, bp), before)


class Canon(unittest.TestCase):
    def test_sources_are_microsoft_learn(self):
        c = lib.load_canon()
        self.assertEqual(len(c["sources"]), 44)
        self.assertTrue(all(s["url"].startswith("https://learn.microsoft.com/en-us/fabric/") for s in c["sources"][:17]), "Fabric IQ")
        self.assertTrue(all(s["url"].startswith(("https://learn.microsoft.com/en-us/", "https://github.com/MicrosoftDocs/")) for s in c["sources"]),
                        "Microsoft Learn or Microsoft's documentation repository")
        ids = {s["id"] for s in c["sources"]}
        for block in ("readiness", "risks", "build_steps", "stack"):
            for x in c[block]:
                self.assertTrue(set(x.get("src", [])) <= ids, (block, x.get("id")))
        self.assertEqual(c["binding_sources"], ["eventhouse", "KQL database", "lakehouse", "mirrored database", "semantic model", "SQL database", "warehouse"])
        pats = lib.load_patterns()
        names = {}
        for e in pats["core"] + [e for p in pats["patterns"] for e in p["entities"]]:
            for p in e["properties"] + e.get("timeseries", []):
                self.assertEqual(names.setdefault(p["name"], p["type"]), p["type"], f"property {p['name']} has one type")


class DataAgentQuestions(unittest.TestCase):
    def test_duplicate_example_questions_merge(self):
        o = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        da = next(a for a in o["data_agents"] if a["id"] == "DA-03")
        self.assertEqual(len(da["questions"]), 6)
        q = copy.deepcopy(da["questions"][2])
        self.assertIn("query", q)
        da["questions"].insert(0, {"q": q["q"]})
        da["questions"].append({"q": "  " + q["q"].upper() + " "})
        rep = lib.Rep()
        n = lib.normalize(o, None, rep)
        qs = next(a for a in n["data_agents"] if a["id"] == "DA-03")["questions"]
        self.assertEqual(len(qs), 6)
        self.assertEqual((qs[0]["query"], qs[0]["language"]), (q["query"], q["language"]), "the query of a duplicate is kept")
        self.assertEqual(sum("duplicate example question merged" in w for w in rep.warnings), 2)


class CommonDataModel(unittest.TestCase):
    """1.9: each entity type rests on a Microsoft standard entity; silver bindings, domains, semantic models, data products."""

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as t:
            cls.bp = json.loads(normalized_blueprint(Path(t)).read_text(encoding="utf-8"))
        cls.rep = lib.Rep()
        cls.o = lib.normalize(json.loads(EXAMPLE.read_text(encoding="utf-8")), cls.bp, cls.rep)
        cls.E = {e["id"]: e for e in cls.o["entity_types"]}

    def test_the_map_covers_every_pattern_entity_type(self):
        cmap = lib.load_cdm()
        pats = lib.load_patterns()
        canon_ids = {s["id"] for s in lib.load_canon()["sources"]}
        ents = list(pats["core"]) + [e for p in pats["patterns"] + [pats["fallback"]] for e in p["entities"]]
        for e in ents:
            m = cmap["entities"].get(e["id"])
            self.assertIsNotNone(m, e["id"])
            self.assertIn(m["standard"], lib.STANDARDS)
            self.assertIn(m["match"], lib.MATCH)
            self.assertIn(m["role"], lib.ROLES)
            props = {p["name"] for p in e.get("properties", [])}
            self.assertTrue(set(m["attributes"]) <= props, (e["id"], set(m["attributes"]) - props))
            self.assertTrue(set(m["src"]) <= canon_ids, (e["id"], m["src"]))
            if m["standard"] != "custom":
                self.assertTrue(m["table"] and m["entity"], e["id"])

    def test_every_canon_reference_resolves(self):
        canon = lib.load_canon()
        ids = {s["id"] for s in canon["sources"]}
        used = set()
        for k in ("readiness", "risks", "build_steps", "stack"):
            for x in canon[k]:
                used |= set(x.get("src", []))
        for x in canon["data_architecture"]["layers"]:
            used |= set(x["src"])
        used |= set(canon["data_architecture"]["domains"]["src"]) | set(canon["data_product_standard"]["src"])
        self.assertTrue(used <= ids, used - ids)
        self.assertTrue(all(s["url"].startswith("https://") for s in canon["sources"]))

    def test_standard_entities_and_silver_bindings(self):
        self.assertEqual(self.rep.errors, [])
        cust, wo, alarm, asset = (self.E[x] for x in ("Customer", "WorkOrder", "AlarmEvent", "Asset"))
        self.assertEqual((cust["standard"]["standard"], cust["standard"]["entity"], cust["standard"]["table"]), ("cdm", "Account", "account"))
        self.assertEqual(cust["standard"]["attributes"]["customerId"], "accountnumber")
        self.assertEqual((wo["standard"]["standard"], wo["standard"]["table"], wo["standard"]["role"]), ("dataverse", "msdyn_workorder", "fact"))
        self.assertEqual(cust["binding"]["table"], "core_silver.customer")
        self.assertEqual(alarm["binding"], {"layer": "silver", "item": "eventhouse", "table": "service_events.alarm_event", "origin": "default"})
        self.assertEqual(asset["binding"]["timeseries_table"], "service_events.asset_telemetry", "time series in the eventhouse of the live journey")
        st = self.o["stats"]
        self.assertEqual((st["standard"], st["custom"], st["to_verify"], st["mapped_properties"]), (24, 3, 6, 61))
        self.assertEqual(self.E["ServiceReport"]["standard"]["match"], "custom")

    def test_domains_and_semantic_models(self):
        doms = {d["id"]: d for d in self.o["domains"]}
        self.assertEqual(doms["core"]["governance_domain"], "Data domain")
        self.assertEqual(doms["service"]["governance_domain"], "Functional unit")
        self.assertEqual((doms["service"]["silver"], doms["service"]["gold"], doms["service"]["events"]), ("service_silver", "service_gold", "service_events"))
        sm = {m["journey"]: m for m in self.o["semantic_models"]}
        self.assertEqual(sm["D3"]["facts"], ["ServiceRequest", "WorkOrder", "ServiceReport", "AlarmEvent"])
        self.assertIn("Asset", sm["D3"]["dimensions"])
        self.assertEqual(sm["D3"]["dimensions"][-1], "Date")
        self.assertEqual(sm["D4"]["name"], "Finance close (Power BI)", "an existing semantic model keeps its name")
        self.assertEqual(sm["D3"]["mode"], "Direct Lake on OneLake")

    def test_data_products_follow_the_publication_standard(self):
        dps = {d["name"]: d for d in self.o["data_products"]}
        self.assertEqual(self.o["stats"]["data_products"], 18)
        self.assertEqual(self.o["stats"]["knowledge_products"], 1)
        self.assertEqual(self.o["stats"]["data_products_ready"], 2)
        self.assertEqual(dps["Knowledge articles"]["kind"], "knowledge")
        c360 = dps["Customer 360"]
        self.assertEqual((c360["owner"], c360["gaps"], c360["sensitivity"]), ("Chief Commercial Officer", [], "confidential"))
        tele = dps["Installed base & telemetry"]
        act = [u for u in tele["uses"] if u["use"] == "actions"]
        self.assertEqual(act, [{"use": "actions", "via": ["OA-01"], "review": True}], "agent actions need a review")
        self.assertFalse(any(u["use"] == "actions" for u in dps["Installed base"]["uses"]), "only the journey's own operations agent")
        self.assertEqual(dps["Work orders"]["gaps"], ["access", "quality"])
        self.assertIn("entity types to model", dps["Spend cube"]["gaps"])

    def test_nineteen_unique_rows_are_eighteen_products_and_one_knowledge_source(self):
        received = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        expected = [(p["id"], p["name"], p["kind"]) for p in received["data_products"]]
        without_products = copy.deepcopy(received)
        without_products.pop("data_products")
        for model in (received, lib.normalize(received), lib.normalize(without_products)):
            rows = model["data_products"]
            self.assertEqual(len(rows), 19)
            self.assertEqual(len({p["id"] for p in rows}), 19)
            self.assertEqual(len({p["name"] for p in rows}), 19)
            self.assertEqual([(p["id"], p["name"], p["kind"]) for p in rows], expected)
            self.assertEqual([(p["id"], p["name"]) for p in rows if p["kind"] == "knowledge"], [("DP-13", "Knowledge articles")])
            self.assertEqual(sum(p["kind"] == "data product" for p in rows), 18)

    def test_turtle_names_the_standard_entity_and_columns(self):
        ttl = lib.to_turtle(self.o)
        self.assertIn("Common Data Model: Account (Dataverse table account).", ttl)
        self.assertIn('rdfs:comment "Standard column: accountnumber."', ttl)
        self.assertIn('skos:altLabel "Alarm", "Telemetry event", "IoT Alert" .', ttl)
        self.assertEqual(ttl.count(" a owl:Class"), 27)

    def test_documents_and_kit(self):
        md = lib.to_markdown(self.o, self.bp)
        dp = lib.data_products_md(self.o, self.bp)
        kit = lib.data_agent_kit(self.o)
        self.assertIn("| Customer | cdm | Account | account | exact | dimension | 5 of 5 | yes |", md)
        self.assertIn("| Service report | custom | Service report | custom table | custom | fact | 0 of 5 | custom |", md)
        self.assertIn("## DP-11 · Installed base & telemetry", dp)
        self.assertIn("Agent actions need an additional review", dp)
        self.assertIn("`service_silver.work_order`: Work order · Dataverse, Dynamics 365 Field Service: Work Order (msdyn_workorder)", kit)
        self.assertIn("The tables follow the Common Data Model: Customer is Account", lib.default_instructions(self.o["data_agents"][0], self.o, self.E))

    def test_authored_standards_are_checked(self):
        o = copy.deepcopy(json.loads(EXAMPLE.read_text(encoding="utf-8")))
        e = next(x for x in o["entity_types"] if x["id"] == "Lead")
        e["standard"] = {"standard": "sap", "entity": "VBAK", "attributes": {"nope": "x"}}
        e["binding"] = {"layer": "platinum", "item": "lakehouse", "table": "commercial_silver.lead"}
        rep = lib.Rep()
        n = lib.normalize(o, None, rep)
        lead = next(x for x in n["entity_types"] if x["id"] == "Lead")
        self.assertEqual((lead["standard"]["standard"], lead["binding"]["layer"]), ("custom", "silver"))
        self.assertTrue(any("standard 'sap'" in w for w in rep.warnings))
        self.assertTrue(any("unknown property 'nope'" in w for w in rep.warnings))
        self.assertTrue(any("layer 'platinum'" in w for w in rep.warnings))

    def test_data_product_verdicts_merge(self):
        o = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        o.pop("data_products", None)
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "o.json").write_text(json.dumps(o), encoding="utf-8")
            fb = {"type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                  "validations": {"onto:DP-11": {"status": "validated", "note": "Owner confirmed"}}}
            (t / "fb.json").write_text(json.dumps(fb), encoding="utf-8")
            code, out = quiet(merge.main, ["--ontology", str(t / "o.json"), "--feedback", str(t / "fb.json"), "--out", str(t / "o2.json")])
            o2 = json.loads((t / "o2.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0, out)
        dp = next(d for d in o2["data_products"] if d["id"] == "DP-11")
        self.assertEqual((dp["name"], dp["status"]), ("Installed base & telemetry", "validated"))
        self.assertNotIn("gaps", dp)


class BuildSafety(unittest.TestCase):
    def test_strict_warning_never_writes_or_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            model = tmp / "model.json"
            warning_model = mini()
            warning_model["entity_types"][0].pop("source")
            model.write_text(json.dumps(warning_model), encoding="utf-8")
            output = tmp / "output"
            code, text = quiet(build.main, ["--ontology", str(model), "--out-dir", str(output), "--strict"])
            self.assertEqual(code, 1, text)
            self.assertFalse(output.exists(), "failed strict build must not create an output directory")
            output.mkdir()
            names = ("ontology.normalized.json", "ontology.ttl", "ontology.md", "data-agents.md", "data-products.md")
            for name in names:
                (output / name).write_bytes(b"previous good output\n")
            code, text = quiet(build.main, ["--ontology", str(model), "--out-dir", str(output), "--strict"])
            self.assertEqual(code, 1, text)
            self.assertEqual(json.loads(text)["files"], {})
            for name in names:
                self.assertEqual((output / name).read_bytes(), b"previous good output\n")

    def test_error_never_creates_output(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            model = mini()
            model["entity_types"][0]["key"] = ["temperature"]
            path = tmp / "bad.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            code, text = quiet(build.main, ["--ontology", str(path), "--out-dir", str(tmp / "output")])
            self.assertEqual(code, 1, text)
            self.assertFalse((tmp / "output").exists())

    def test_repeated_build_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            args = ["--ontology", str(EXAMPLE), "--out-dir", str(tmp / "output")]
            code, text = quiet(build.main, args)
            self.assertEqual(code, 0, text)
            before = {p.name: p.read_bytes() for p in (tmp / "output").iterdir()}
            code, text = quiet(build.main, args)
            self.assertEqual(code, 0, text)
            self.assertEqual(before, {p.name: p.read_bytes() for p in (tmp / "output").iterdir()})
            self.assertTrue(all(b"\r\n" not in content for content in before.values()))


class ValidationEdges(unittest.TestCase):
    def test_invalid_root_metadata_and_mapping_shape_report_errors(self):
        cases = [[], {"meta": []}]
        malformed = mini()
        malformed["entity_types"][0]["standard"] = {"standard": "cdm", "attributes": []}
        cases.append(malformed)
        not_verified = mini()
        not_verified["entity_types"][0]["standard"] = {
            "standard": "cdm", "checked": "false", "attributes": {}}
        cases.append(not_verified)
        for model in cases:
            with self.subTest(model=model):
                rep = lib.Rep()
                lib.normalize(model, None, rep)
                self.assertTrue(rep.errors)

    def test_rdf_identifiers_do_not_collide(self):
        model = mini()
        model["entity_types"].append({
            "id": "Asset_assetId", "key": ["id"], "properties": [{"name": "id", "type": "string"}], "source": "s-fs"})
        rep = lib.Rep()
        lib.normalize(model, None, rep)
        self.assertTrue(any("RDF identifier" in error for error in rep.errors))

    def test_invalid_types_keys_relationships_and_sources_are_errors(self):
        cases = [
            ("unsupported static type", lambda o: o["entity_types"][0]["properties"][1].update(type="binary")),
            ("unsupported time-series type", lambda o: o["entity_types"][0]["timeseries"][0].update(type="binary")),
            ("duplicate key", lambda o: o["entity_types"][0].update(key=["assetId", "assetId"])),
            ("invalid relationship name", lambda o: o["relationship_types"][0].update(name="2invalid")),
            ("invalid cardinality", lambda o: o["relationship_types"][0].update(cardinality="many")),
            ("unknown secondary source", lambda o: o["entity_types"][0].update(secondary=["missing"])),
            ("unknown data agent source", lambda o: o["data_agents"][0].update(sources=["missing"])),
            ("unknown data agent entity", lambda o: o["data_agents"][0].update(entities=["missing"])),
            ("unknown inheritance", lambda o: o["entity_types"][0].update(base="missing")),
            ("inheritance cycle", lambda o: (o["entity_types"][0].update(base="WorkOrder"), o["entity_types"][1].update(base="Asset"))),
            ("unknown primary source", lambda o: o["entity_types"][0].update(source="missing")),
        ]
        for name, change in cases:
            with self.subTest(name=name):
                model = mini()
                change(model)
                rep = lib.Rep()
                lib.normalize(model, None, rep)
                self.assertTrue(rep.errors, f"{name} must not silently normalize to a publishable model")

    def test_five_sources_valid_six_sources_rejected(self):
        model = mini()
        for number in range(4):
            model["sources"].append({"id": f"extra{number}", "path": "shortcut"})
        model["data_agents"][0]["sources"] = ["ontology", "s-fs", "extra0", "extra1", "extra2"]
        rep = lib.Rep()
        lib.normalize(model, None, rep)
        self.assertEqual(rep.errors, [])
        model["data_agents"][0]["sources"].append("extra3")
        rep = lib.Rep()
        lib.normalize(model, None, rep)
        self.assertTrue(any("has 6 sources" in e for e in rep.errors))

    def test_unchecked_mapping_remains_to_verify(self):
        model = mini()
        model["entity_types"][1]["standard"] = {
            "standard": "dataverse", "entity": "Work Order", "table": "msdyn_workorder",
            "match": "exact", "checked": False, "attributes": {"workOrderId": "msdyn_workorderid"},
        }
        normalized = lib.normalize(model)
        entity = next(e for e in normalized["entity_types"] if e["id"] == "WorkOrder")
        self.assertIs(entity["standard"]["checked"], False)
        self.assertIn("to verify", lib.to_markdown(normalized))


class FeedbackEdges(unittest.TestCase):
    def test_duplicate_question_preserves_verified_query_and_provenance(self):
        model = mini()
        model["data_agents"][0]["questions"] = [
            {"q": "Open orders?", "query": "unverified query", "language": "SQL", "verified": False},
            {"q": " OPEN orders? ", "query": "verified query", "language": "GQL", "verified": True, "src": ["query-evidence"]},
        ]
        rep = lib.Rep()
        result = lib.normalize(model, None, rep)["data_agents"][0]["questions"]
        self.assertEqual(len(result), 1)
        self.assertEqual((result[0]["query"], result[0]["language"], result[0]["verified"]), ("verified query", "GQL", True))
        self.assertEqual(result[0]["src"], ["query-evidence"])
        self.assertTrue(any("duplicate example question merged" in warning for warning in rep.warnings))

    def test_derived_ids_and_repeated_feedback_are_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            model = tmp / "model.json"
            model.write_text(json.dumps(mini()), encoding="utf-8")
            feedback = tmp / "feedback.json"
            feedback.write_text(json.dumps({
                "type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                "validations": {
                    "onto:DA-01": {"status": "validated", "note": "Confirmed"},
                    "onto:WorkOrder_concerns_Asset": {"status": "adjusted", "note": "Review cardinality"},
                    "onto:Nope": {"status": "validated"},
                    "onto:DP-999": {"status": "validated"},
                },
            }), encoding="utf-8")
            output = tmp / "merged.json"
            code, text = quiet(merge.main, ["--ontology", str(model), "--feedback", str(feedback), "--out", str(output)])
            self.assertEqual(code, 0, text)
            summary = json.loads(text)
            self.assertEqual(summary["changed"], 2)
            self.assertEqual(summary["unknown"], ["onto:Nope", "onto:DP-999"])
            first = output.read_bytes()
            code, text = quiet(merge.main, ["--ontology", str(output), "--feedback", str(feedback), "--out", str(output)])
            self.assertEqual(code, 0, text)
            self.assertEqual(json.loads(text)["changed"], 0)
            self.assertEqual(output.read_bytes(), first)


class CustomerPrivacy(unittest.TestCase):
    MARKER = "SYNTHETIC_ONTOLOGY_PRIVATE_28"

    def model(self):
        model = mini()
        model["entity_types"][0]["description"] = self.MARKER + " entity"
        model["entity_types"][0]["properties"][0]["description"] = self.MARKER + " property"
        model["entity_types"][0]["binding"] = {
            "table": self.MARKER + "_table", "layer": "silver", "item": "lakehouse"}
        model["data_agents"][0]["instructions"] = self.MARKER + " instructions"
        model["data_agents"][0]["products"] = [{"name": self.MARKER + " product", "entities": ["Asset"]}]
        model["rules"] = [{"id": "RU-private", "text": self.MARKER + " rule"}]
        model["metrics"] = [{"name": self.MARKER + " metric", "entity": "Asset"}]
        model["operations_agents"] = [{
            "id": "OA-private", "name": self.MARKER + " operations", "entities": ["Asset"],
            "rules": [self.MARKER], "actions": [{"name": self.MARKER + " action"}]}]
        model["risks"] = [{"id": "R-ONT-private", "title": self.MARKER + " risk", "mitigation": self.MARKER}]
        model["readiness"] = [{"id": "ONT-private", "item": self.MARKER + " readiness", "why": self.MARKER}]
        return model

    def blueprint(self):
        bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        bp.setdefault("evidence", []).append({
            "id": "private28", "visibility": "internal", "type": "assessment",
            "title": "Synthetic private assessment", "date": "2026-11-11",
        })
        return bp

    def customer_build(self, bp, tmp):
        path = tmp / "input.json"
        path.write_text(json.dumps(bp), encoding="utf-8")
        code, text = quiet(bpbuild.main, [
            "--data", str(path), "--audience", "customer", "--out", str(tmp / "customer.html"),
            "--save-normalized", str(tmp / "customer.json"), "--no-product-icons"])
        self.assertEqual(code, 0, text)
        for name in ("customer.json", "customer.html"):
            self.assertFalse(self.MARKER in (tmp / name).read_text(encoding="utf-8"), f"private ontology content leaked into {name}")
        return json.loads((tmp / "customer.json").read_text(encoding="utf-8"))

    def test_root_privacy_before_readiness_projection(self):
        for restriction in ({"internal": True}, {"visibility": "internal"}, {"src": ["private28"]}):
            with self.subTest(restriction=restriction), tempfile.TemporaryDirectory() as directory:
                bp = self.blueprint()
                model = self.model()
                model.update(restriction)
                bp = apply_.apply(bp, model, lib.Rep())
                self.customer_build(bp, Path(directory))

    def test_internal_build_feedback_source_correction_customer_rebuild(self):
        bpmerge = load("plugin/skills/frontier-blueprint/scripts/merge_feedback.py", "on_bpmerge_privacy")
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = apply_.apply(self.blueprint(), self.model(), lib.Rep())
            source = tmp / "source.json"
            source.write_text(json.dumps(bp), encoding="utf-8")
            normalized = tmp / "internal.json"
            code, text = quiet(bpbuild.main, ["--data", str(source), "--save-normalized", str(normalized), "--no-product-icons"])
            self.assertEqual(code, 0, text)
            feedback = tmp / "feedback.json"
            feedback.write_text(json.dumps({
                "type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                "validations": {"onto:Asset": {"status": "validated", "note": self.MARKER + " workshop"}},
            }), encoding="utf-8")
            merged = tmp / "merged.json"
            code, text = quiet(bpmerge.main, ["--blueprint", str(normalized), "--feedback", str(feedback), "--out", str(merged)])
            self.assertEqual(code, 0, text)
            bp = json.loads(merged.read_text(encoding="utf-8"))
            model_path = tmp / "ontology-source.json"
            model_path.write_text(json.dumps(self.model()), encoding="utf-8")
            corrected = tmp / "ontology-merged.json"
            code, text = quiet(merge.main, ["--ontology", str(model_path), "--feedback", str(feedback), "--out", str(corrected)])
            self.assertEqual(code, 0, text)
            model = json.loads(corrected.read_text(encoding="utf-8"))
            asset = next(e for e in model["entity_types"] if e["id"] == "Asset")
            self.assertEqual(asset["status"], "validated")
            self.assertTrue(asset["workshop_notes"])
            model["src"] = ["private28"]
            bp = apply_.apply(bp, model, lib.Rep())
            self.customer_build(bp, tmp)

    def test_private_nested_binding_instructions_and_product_are_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            model = mini()
            model["entity_types"][0]["binding"] = {
                "table": self.MARKER, "layer": "silver", "item": "lakehouse", "visibility": "internal"}
            model["entity_types"][0]["properties"][1]["description"] = self.MARKER
            model["entity_types"][0]["properties"][1]["src"] = ["private28"]
            model["data_agents"][0]["instructions"] = self.MARKER
            model["data_agents"][0]["src"] = ["private28"]
            model["data_agents"][0]["products"] = [{"name": self.MARKER, "entities": ["Asset"]}]
            bp = apply_.apply(self.blueprint(), model, lib.Rep())
            self.customer_build(bp, Path(directory))

    def test_customer_ontology_exports_do_not_publish_internal_content(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            model = self.model()
            model["visibility"] = "internal"
            path = tmp / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            code, text = quiet(build.main, [
                "--ontology", str(path), "--out-dir", str(tmp / "output"), "--audience", "customer"])
            self.assertEqual(code, 1, text)
            self.assertFalse((tmp / "output").exists())


class ProcessWrapper(unittest.TestCase):
    def test_seed_retains_private_journey_provenance_for_customer_exports(self):
        wrapper = load("plugin/skills/frontier-blueprint/scripts/build_with_identity.py", "on_seed_customer_wrapper")
        for restriction in ("journey", "data agent"):
            with self.subTest(restriction=restriction), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                bp = CustomerPrivacy().blueprint()
                domain = bp["domains"][0]
                domain["src"] = ["E01"]
                if restriction == "journey":
                    domain["visibility"] = "internal"
                    domain["name"] = CustomerPrivacy.MARKER + " private journey"
                else:
                    domain["data_agent"]["visibility"] = "internal"
                domain["data_agent"]["name"] = CustomerPrivacy.MARKER + " private data agent"
                source = tmp / "blueprint.json"
                source.write_text(json.dumps(bp), encoding="utf-8")
                model = tmp / "seed.json"
                code, text = quiet(seed.main, ["--blueprint", str(source), "--out", str(model)])
                self.assertEqual(code, 0, text)
                out = tmp / "exports"
                code, text = quiet(wrapper.main, ["--data", str(source), "--ontology", str(model),
                                                  "--out-dir", str(out), "--audience", "customer", "--no-identity"])
                self.assertEqual(code, 0, text)
                leaks = [str(path.relative_to(out)) for path in out.rglob("*")
                         if path.is_file() and path.suffix in (".json", ".ttl", ".md", ".html")
                         and CustomerPrivacy.MARKER in path.read_text(encoding="utf-8")]
                self.assertEqual(leaks, [])

    def test_customer_wrapper_sanitizes_every_process_export_before_writing(self):
        wrapper = load("plugin/skills/frontier-blueprint/scripts/build_with_identity.py", "on_customer_wrapper")
        sentinel = CustomerPrivacy.MARKER
        for explicit in (True, False):
            with self.subTest(explicit=explicit), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                bp = CustomerPrivacy().blueprint()
                bp["meta"]["audience"] = "customer"
                bp["domains"][0]["internal"] = True
                bp["domains"][0]["name"] = sentinel + " private journey"
                bp["ontology_feedback"] = [{"id": "WorkOrder", "note": sentinel + " old workshop", "src": ["private28"]}]
                source = tmp / "blueprint.json"
                source.write_text(json.dumps(bp), encoding="utf-8")
                model = mini()
                model["entity_types"][0]["journeys"] = ["D1"]
                model["data_agents"][0]["journey"] = "D1"
                model["data_agents"][0]["products"] = [{"name": "Public data product", "entities": ["Asset"]}]
                model["entity_types"][0]["binding"] = {
                    "table": sentinel + "_binding", "layer": "silver", "item": "lakehouse", "visibility": "internal"}
                model["data_agents"][0]["questions"] = [{"q": sentinel + " question", "internal": True}]
                model["rules"] = [{"text": sentinel + " rule", "visibility": "internal"}]
                model["metrics"] = [{"name": sentinel + " metric", "entity": "Asset", "src": ["private28"]}]
                model["readiness"] = [{"id": "ONT-safe", "item": "Public readiness"}]
                model_path = tmp / "model.json"
                model_path.write_text(json.dumps(model), encoding="utf-8")
                out = tmp / "exports"
                args = ["--data", str(source), "--ontology", str(model_path), "--out-dir", str(out),
                        "--no-identity", "--save-normalized", str(out / "customer.json")]
                if explicit:
                    args += ["--audience", "customer"]
                code, text = quiet(wrapper.main, args)
                self.assertEqual(code, 0, text)
                leaks = [str(path.relative_to(out)) for path in out.rglob("*")
                         if path.is_file() and path.suffix in (".json", ".ttl", ".md", ".html")
                         and sentinel in path.read_text(encoding="utf-8")]
                self.assertEqual(leaks, [], f"private content leaked into {leaks}")
                self.assertEqual(len(list((out / "ontology").glob("*.md"))), 3)

    def test_process_only_wrapper_builds_without_finops(self):
        wrapper = load("plugin/skills/frontier-blueprint/scripts/build_with_identity.py", "on_wrapper")
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            code, text = quiet(wrapper.main, [
                "--data", str(BLUEPRINT), "--ontology", str(EXAMPLE), "--out-dir", str(tmp),
                "--no-identity", "--save-normalized", str(tmp / "bp.json")])
            self.assertEqual(code, 0, text)
            result = json.loads(text)
            self.assertEqual(result["ontology"]["status"], "ok")
            self.assertNotIn("value_finops", result)
            self.assertFalse((tmp / "value-finops").exists())
            bp = json.loads((tmp / "bp.json").read_text(encoding="utf-8"))
            self.assertEqual(len(bp["ontology"]["entity_types"]), 27)


class BlueprintOntologyFeedback(unittest.TestCase):
    def test_known_unknown_invalid_and_repeated_ontology_feedback(self):
        bpmerge = load("plugin/skills/frontier-blueprint/scripts/merge_feedback.py", "on_bpmerge_edges")
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = apply_.apply(json.loads(BLUEPRINT.read_text(encoding="utf-8")), mini(), lib.Rep())
            source = tmp / "source.json"
            source.write_text(json.dumps(bp), encoding="utf-8")
            feedback = tmp / "feedback.json"
            feedback.write_text(json.dumps({
                "type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                "validations": {
                    "onto:Asset": {"status": "validated", "note": "Synthetic confirmation"},
                    "onto:Nope": {"status": "validated"},
                    "onto:DP-999": {"status": "validated"},
                    "onto:DA-01": {"status": "not a verdict"},
                },
            }), encoding="utf-8")
            output = tmp / "merged.json"
            code, text = quiet(bpmerge.main, ["--blueprint", str(source), "--feedback", str(feedback), "--out", str(output), "--no-bump"])
            self.assertEqual(code, 0, text)
            result = json.loads(text)
            self.assertEqual(result["ontology_feedback"], 1)
            self.assertEqual(result["unknown"], ["onto:Nope", "onto:DP-999"])
            self.assertTrue(result["invalid"])
            first = json.loads(output.read_text(encoding="utf-8"))
            code, text = quiet(bpmerge.main, ["--blueprint", str(output), "--feedback", str(feedback), "--out", str(output), "--no-bump"])
            self.assertEqual(code, 0, text)
            second = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(first["ontology_feedback"], second["ontology_feedback"])
            self.assertEqual(first["evidence"], second["evidence"])


class ProcessSelftest(unittest.TestCase):
    def test_ontology_canon_urls_are_not_reported_as_unrendered_content(self):
        bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        bp["ontology"] = {"sources_doc": [{
            "id": "FI-01", "title": "Fabric ontology overview",
            "url": "https://learn.microsoft.com/en-us/fabric/iq/ontology/overview"}]}
        rep = bpbuild.Report()
        bpbuild.normalise(bp, rep)
        self.assertFalse(any("$.ontology.sources_doc" in warning and "contains a URL" in warning for warning in rep.warnings))

    def test_ontology_risk_requires_current_lineage_integration(self):
        risks = load("plugin/skills/frontier-blueprint/scripts/risks.py", "on_risks_dependency")
        bp = apply_.apply(CustomerPrivacy().blueprint(), CustomerPrivacy().model(), lib.Rep())
        rows = [r for r in risks.fill_risks(bp)["items"] if r.get("origin") == "ontology"]
        self.assertEqual(len(rows), 1, "bounded ontology risk derivation is a proven integration dependency")

    def test_new_selftest_checks_execute_process_behavior(self):
        selftest = load("tools/selftest.py", "on_selftest")
        results = []
        with tempfile.TemporaryDirectory() as directory:
            selftest.process_checks(Path(directory), BLUEPRINT, lambda name, condition, detail="": results.append((name, condition, detail)))
        self.assertGreaterEqual(len(results), 5)
        self.assertTrue(all(condition for _, condition, _ in results), results)

    def test_seed_date_comes_from_fixed_input_not_wall_clock(self):
        bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        bp["meta"]["date"] = "2026-11-01"
        result = seed.seed(bp, lib.load_patterns(), lib.load_canon())
        self.assertEqual(result["meta"]["date"], "2026-11-01")


class OntologyRiskLineage(unittest.TestCase):
    RID = "R-ONT-28"
    MARKER = "SYNTHETIC_ONTOLOGY_RISK_PRIVATE_28"

    def fixture(self):
        bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        # Neutral privacy fixture: isolate ontology provenance from the bundled
        # engagement's unrelated internal evidence. No source example is edited.
        for evidence in bp["evidence"]:
            evidence["visibility"] = "customer"
        bp["evidence"] += [
            {"id": "public28", "visibility": "customer", "title": "Synthetic public evidence"},
            {"id": "replacement28", "visibility": "customer", "title": "Synthetic corrected evidence"},
            {"id": "private28", "visibility": "internal", "title": "Synthetic private evidence"},
        ]
        onto = mini()
        onto["src"] = ["public28"]
        onto["risks"] = [{
            "id": self.RID, "title": self.MARKER + " risk", "mitigation": self.MARKER + " mitigation",
            "owner": "Synthetic data owner", "likelihood": 3, "impact": 4,
            "entities": ["Asset"], "sources": ["s-fs"], "src": ["public28"],
        }]
        return apply_.apply(bp, onto, lib.Rep())

    def internal_build(self, bp, tmp):
        source = tmp / "risk-source.json"
        source.write_text(json.dumps(bp), encoding="utf-8")
        output = tmp / "risk-internal.json"
        code, text = quiet(bpbuild.main, ["--data", str(source), "--save-normalized", str(output), "--no-product-icons"])
        self.assertEqual(code, 0, text)
        return json.loads(output.read_text(encoding="utf-8"))

    def promote(self, bp, tmp):
        bpmerge = load("plugin/skills/frontier-blueprint/scripts/merge_feedback.py", "on_ontology_risk_merge")
        source = tmp / "risk-promote-source.json"
        source.write_text(json.dumps(bp), encoding="utf-8")
        row = next(r for r in bp["risks"]["items"] if r["id"] == self.RID)
        feedback = tmp / "risk-feedback.json"
        feedback.write_text(json.dumps({
            "type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
            "validations": {
                f"risk:{self.RID}": {"status": "accepted", "note": self.MARKER + " workshop", "source_key": row["source_key"]},
                "risk:R-ONT-unknown": {"status": "accepted"},
            },
        }), encoding="utf-8")
        output = tmp / "risk-promoted.json"
        code, text = quiet(bpmerge.main, ["--blueprint", str(source), "--feedback", str(feedback), "--out", str(output)])
        self.assertEqual(code, 0, text)
        self.assertEqual(json.loads(text)["unknown"], ["risk:R-ONT-unknown"])
        return json.loads(output.read_text(encoding="utf-8"))

    def assert_customer_outputs(self, bp, tmp):
        source = tmp / "risk-customer-source.json"
        source.write_text(json.dumps(bp), encoding="utf-8")
        output = tmp / "customer"
        output.mkdir(exist_ok=True)
        normalized = output / "customer.json"
        code, text = quiet(bpbuild.main, ["--data", str(source), "--audience", "customer", "--no-product-icons",
                                          "--out", str(output / "customer.html"), "--save-normalized", str(normalized)])
        self.assertEqual(code, 0, text)
        scaffold = load("plugin/skills/frontier-solution-design/scripts/scaffold_design_docs.py", "on_ontology_risk_scaffold")
        code, text = quiet(scaffold.main, ["--blueprint", str(normalized), "--out-dir", str(output / "scaffold")])
        self.assertEqual(code, 0, text)
        ontology = tmp / "risk-ontology.json"
        ontology.write_text(json.dumps(bp["ontology"]), encoding="utf-8")
        code, text = quiet(build.main, ["--ontology", str(ontology), "--blueprint", str(source),
                                       "--out-dir", str(output / "ontology"), "--audience", "customer"])
        if lib.private_content(bp["ontology"], bp):
            self.assertEqual(code, 1, text)
            self.assertFalse((output / "ontology").exists())
        else:
            self.assertEqual(code, 0, text)
        leaks = [str(p.relative_to(output)) for p in output.rglob("*")
                 if p.is_file() and self.MARKER in p.read_text(encoding="utf-8")]
        self.assertEqual(leaks, [])

    def test_direct_customer_ontology_risk_entity_and_source_privacy(self):
        for restriction in ("entity flag", "entity visibility", "entity citation", "source flag", "source visibility", "binding visibility"):
            with self.subTest(restriction=restriction), tempfile.TemporaryDirectory() as directory:
                bp = self.fixture()
                entity = bp["ontology"]["entity_types"][0]
                source = bp["ontology"]["sources"][0]
                if restriction == "entity flag":
                    entity["internal"] = True
                elif restriction == "entity visibility":
                    entity["visibility"] = "internal"
                elif restriction == "entity citation":
                    entity["src"] = ["private28"]
                elif restriction == "source flag":
                    source["internal"] = True
                elif restriction == "source visibility":
                    source["visibility"] = "internal"
                else:
                    entity["binding"]["visibility"] = "internal"
                self.assert_customer_outputs(bp, Path(directory))

    def test_promoted_risk_current_citation_correction_is_preserved(self):
        risks = load("plugin/skills/frontier-blueprint/scripts/risks.py", "on_ontology_risk_citations")
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = self.promote(self.internal_build(self.fixture(), tmp), tmp)
            before = next(r for r in bp["risks"]["items"] if r["id"] == self.RID)
            key = before["source_key"]
            bp["ontology"]["risks"][0]["src"] = ["replacement28"]
            bp = self.internal_build(bp, tmp)
            row = next(r for r in bp["risks"]["items"] if r["id"] == self.RID)
            self.assertEqual((row["source_key"], row["status"], row["content_src"]), (key, "accepted", ["replacement28"]))
            self.assertTrue(any(s.startswith("W") for s in row["src"]))
            self.assertEqual(len([r for r in risks.fill_risks(bp)["items"] if r["id"] == self.RID]), 1)
            bp["ontology"]["risks"][0]["src"] = ["private28"]
            self.assert_customer_outputs(bp, tmp)

    def test_promoted_retired_risk_obeys_current_ontology_ancestry(self):
        for restriction in ("root flag", "root visibility", "root citation", "entity flag", "entity citation", "source visibility"):
            with self.subTest(restriction=restriction), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                bp = self.promote(self.internal_build(self.fixture(), tmp), tmp)
                bp["ontology"]["risks"][0]["title"] = "A corrected public title, not the old workshop risk"
                if restriction == "root flag":
                    bp["ontology"]["internal"] = True
                elif restriction == "root visibility":
                    bp["ontology"]["visibility"] = "internal"
                elif restriction == "root citation":
                    bp["ontology"]["src"] = ["private28"]
                elif restriction == "entity flag":
                    bp["ontology"]["entity_types"][0]["internal"] = True
                elif restriction == "entity citation":
                    bp["ontology"]["entity_types"][0]["src"] = ["private28"]
                else:
                    bp["ontology"]["sources"][0]["visibility"] = "internal"
                self.assert_customer_outputs(bp, tmp)

    def test_legacy_ontology_risk_ids_stay_bound_after_retirement(self):
        risks = load("plugin/skills/frontier-blueprint/scripts/risks.py", "on_ontology_risk_ids")
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = self.promote(self.internal_build(self.fixture(), tmp), tmp)
            owned = next(r for r in bp["risks"]["items"] if r["id"] == self.RID)
            original_key = owned.pop("source_key")
            owned.pop("ref")
            bp["risks"].pop("source_ids")
            bp["ontology"]["risks"][0]["title"] = "Corrected ontology risk"
            reg = risks.fill_risks(bp)
            owned = next(r for r in reg["items"] if r["id"] == self.RID)
            self.assertEqual(owned["source_key"], original_key)
            self.assertEqual(reg["source_ids"][original_key], self.RID)
            new = next(r for r in reg["items"] if r.get("origin") == "ontology" and r["id"] != self.RID)
            self.assertNotEqual(new["source_key"], original_key)
            before = [(r["id"], r.get("source_key")) for r in reg["items"]]
            self.assertEqual(before, [(r["id"], r.get("source_key")) for r in risks.fill_risks(bp)["items"]])

    def test_derived_reference_snapshot_is_not_mutated_with_the_source(self):
        risks = load("plugin/skills/frontier-blueprint/scripts/risks.py", "on_ontology_risk_snapshot")
        bp = self.fixture()
        row = next(r for r in risks.fill_risks(bp)["items"] if r["id"] == self.RID)
        bp["ontology"]["risks"][0]["entities"].clear()
        self.assertEqual(row["entities"], ["Asset"], "a retained row must retain its original entity ancestry")

    def test_retired_private_verdict_does_not_restrict_a_new_public_source(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = self.fixture()
            bp["ontology"]["risks"][0]["src"] = ["private28"]
            bp = self.promote(self.internal_build(bp, tmp), tmp)
            current = bp["ontology"]["risks"][0]
            current["title"] = "Replacement public risk"
            current["mitigation"] = "Public replacement mitigation"
            current["src"] = ["replacement28"]
            current.pop("internal", None)
            bp = self.internal_build(bp, tmp)
            self.assert_customer_outputs(bp, tmp)
            customer = json.loads((tmp / "customer/customer.json").read_text(encoding="utf-8"))
            replacement = next(r for r in customer["risks"]["items"] if r["title"] == "Replacement public risk")
            self.assertNotEqual(replacement["id"], self.RID)
            self.assertEqual(replacement["status"], "open", "the old accepted verdict must not move to the new source")


class ReviewD1Regressions(unittest.TestCase):
    MARKER = "D1REVIEWPRIVATE"

    def public_blueprint(self):
        bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        def public(value):
            if isinstance(value, dict):
                value.pop("internal", None)
                value.pop("content_src", None)
                if "visibility" in value:
                    value["visibility"] = "customer"
                for child in value.values():
                    public(child)
            elif isinstance(value, list):
                for child in value:
                    public(child)
        public(bp)
        bp["feedback_loop"]["quadrants"] = []
        bp["evidence"].append({"id": "review-private", "visibility": "internal", "title": "Synthetic private origin"})
        return bp

    def assert_no_export_marker(self, root):
        leaks = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()
                 and self.MARKER in path.read_text(encoding="utf-8").upper()]
        self.assertEqual(leaks, [])

    def child_fixture(self, kind, restriction):
        bp = self.public_blueprint()
        domain = bp["domains"][0]
        domain["src"] = ["E01"]
        privacy = {"src": ["E01"]}
        if restriction == "flag":
            privacy["internal"] = True
        elif restriction == "visibility":
            privacy["visibility"] = "internal"
        elif restriction == "citation":
            privacy["src"] = ["review-private"]
        elif restriction == "content citation":
            privacy["content_src"] = ["review-private"]
        if kind == "data agent":
            child = domain["data_agent"]
            child["name"] = self.MARKER + " data agent"
            child["products"][0] = self.MARKER + " data product"
            child.update(privacy)
        elif kind == "KPI":
            child = {"kpi": "Win rate " + self.MARKER, "definition": self.MARKER + " definition",
                     "baseline": "10%", "target": "20%", **privacy}
            domain["kpis"] = [child]
        elif kind == "seam":
            child = {"text": "The " + self.MARKER + " approves every quote", **privacy}
            domain["approval_seam"] = child
            domain["systems"].append("IoT Platform")
        else:
            child = {"text": "Live alarm modelled as " + self.MARKER + "Signal", "iq": ["fabric"], **privacy}
            bp["feedback_loop"]["quadrants"] = [{"pillar": "engage_customers", "journeys": ["D1"], "signals": [child], "src": ["E01"]}]
        return bp

    def test_each_private_seed_child_survives_roundtrip_without_customer_leaks(self):
        wrapper = load("plugin/skills/frontier-blueprint/scripts/build_with_identity.py", "review_child_wrapper")
        for kind in ("data agent", "KPI", "seam", "signal"):
            for restriction in ("flag", "visibility", "citation", "content citation"):
                with self.subTest(kind=kind, restriction=restriction), tempfile.TemporaryDirectory() as directory:
                    tmp = Path(directory)
                    bp = self.child_fixture(kind, restriction)
                    source = tmp / "blueprint.json"
                    source.write_text(json.dumps(bp), encoding="utf-8")
                    seeded = tmp / "seed.json"
                    code, text = quiet(seed.main, ["--blueprint", str(source), "--out", str(seeded)])
                    self.assertEqual(code, 0, text)
                    self.assertIn(self.MARKER, seeded.read_text(encoding="utf-8").upper(), "fixture must exercise actual derived child content")
                    feedback = tmp / "feedback.json"
                    feedback.write_text(json.dumps({"type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                        "validations": {"onto:DA-01": {"status": "validated", "note": "Synthetic workshop confirmation"}}}), encoding="utf-8")
                    merged = tmp / "merged.json"
                    code, text = quiet(merge.main, ["--ontology", str(seeded), "--feedback", str(feedback), "--out", str(merged)])
                    self.assertEqual(code, 0, text)
                    output = tmp / "customer"
                    code, text = quiet(wrapper.main, ["--data", str(source), "--ontology", str(merged), "--audience", "customer",
                                                      "--out-dir", str(output), "--no-identity", "--save-normalized", str(output / "blueprint.json")])
                    self.assertEqual(code, 0, text)
                    self.assert_no_export_marker(output)

    def test_retired_feedback_target_rebinds_former_entity_and_source_privacy(self):
        bpmerge = load("plugin/skills/frontier-blueprint/scripts/merge_feedback.py", "review_retired_feedback")
        for restriction in ("entity", "source", "all ancestry removed", "legacy no snapshot"):
            with self.subTest(restriction=restriction), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                bp = apply_.apply(self.public_blueprint(), mini(), lib.Rep())
                source = tmp / "blueprint.json"
                source.write_text(json.dumps(bp), encoding="utf-8")
                feedback = tmp / "feedback.json"
                feedback.write_text(json.dumps({"type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                    "validations": {"onto:DA-01": {"status": "validated", "note": self.MARKER + " verdict"}}}), encoding="utf-8")
                merged = tmp / "merged.json"
                code, text = quiet(bpmerge.main, ["--blueprint", str(source), "--feedback", str(feedback), "--out", str(merged)])
                self.assertEqual(code, 0, text)
                bp = json.loads(merged.read_text(encoding="utf-8"))
                bp["ontology"]["data_agents"] = []
                if restriction == "entity":
                    bp["ontology"]["entity_types"][0]["visibility"] = "internal"
                elif restriction == "source":
                    bp["ontology"]["sources"][0]["visibility"] = "internal"
                elif restriction == "all ancestry removed":
                    bp["ontology"]["entity_types"] = []
                    bp["ontology"]["sources"] = []
                    bp["ontology"]["relationship_types"] = []
                else:
                    bp["ontology_feedback"][0].pop("target_ancestry", None)
                    bp["ontology"]["entity_types"][0]["internal"] = True
                rep = bpbuild.Report()
                customer = bpbuild.customer_version(bp, rep)
                self.assertFalse(self.MARKER in json.dumps(customer).upper(), "retired ontology feedback leaked")
                if restriction in ("all ancestry removed", "legacy no snapshot"):
                    self.assertTrue(any("ancestry" in warning and "DA-01" in warning for warning in rep.warnings), rep.warnings)

    def test_public_seed_children_are_retained_in_customer_exports(self):
        wrapper = load("plugin/skills/frontier-blueprint/scripts/build_with_identity.py", "review_public_child_wrapper")
        for kind in ("data agent", "KPI", "seam", "signal"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                source = tmp / "blueprint.json"
                source.write_text(json.dumps(self.child_fixture(kind, "public")), encoding="utf-8")
                model = tmp / "seed.json"
                code, text = quiet(seed.main, ["--blueprint", str(source), "--out", str(model)])
                self.assertEqual(code, 0, text)
                output = tmp / "output"
                code, text = quiet(wrapper.main, ["--data", str(source), "--ontology", str(model), "--audience", "customer",
                                                  "--out-dir", str(output), "--no-identity"])
                self.assertEqual(code, 0, text)
                self.assertTrue(any(self.MARKER in p.read_text(encoding="utf-8").upper() for p in output.rglob("*") if p.is_file()))

    def test_public_retired_feedback_and_replay_keep_one_original_snapshot(self):
        bpmerge = load("plugin/skills/frontier-blueprint/scripts/merge_feedback.py", "review_public_snapshot")
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = apply_.apply(self.public_blueprint(), mini(), lib.Rep())
            source = tmp / "bp.json"
            source.write_text(json.dumps(bp), encoding="utf-8")
            feedback = tmp / "feedback.json"
            feedback.write_text(json.dumps({"type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
                "validations": {"onto:DA-01": {"status": "validated", "note": "Public workshop observation"}}}), encoding="utf-8")
            merged = tmp / "merged.json"
            code, text = quiet(bpmerge.main, ["--blueprint", str(source), "--feedback", str(feedback), "--out", str(merged)])
            self.assertEqual(code, 0, text)
            bp = json.loads(merged.read_text(encoding="utf-8"))
            snapshot = copy.deepcopy(bp["ontology_feedback"][0]["target_ancestry"])
            self.assertFalse(bp["ontology_feedback"][0].get("internal"))
            bp["ontology"]["entity_types"][0]["src"] = ["E03"]
            source.write_text(json.dumps(bp), encoding="utf-8")
            code, text = quiet(bpmerge.main, ["--blueprint", str(source), "--feedback", str(feedback), "--out", str(merged)])
            self.assertEqual(code, 0, text)
            bp = json.loads(merged.read_text(encoding="utf-8"))
            self.assertEqual(len(bp["ontology_feedback"]), 1)
            self.assertEqual(bp["ontology_feedback"][0]["target_ancestry"], snapshot)
            bp["ontology"]["data_agents"] = []
            rep = bpbuild.Report()
            customer = bpbuild.customer_version(bp, rep)
            self.assertIn("Public workshop observation", json.dumps(customer))
            self.assertFalse(any("ancestry unresolved" in warning for warning in rep.warnings), rep.warnings)

    def test_model_verdict_inherits_private_child_dependencies(self):
        bp = apply_.apply(self.public_blueprint(), mini(), lib.Rep())
        bp["ontology"]["entity_types"][0]["visibility"] = "internal"
        verdict = {"id": "model", "note": self.MARKER + " model workshop", "src": ["E01"],
                   "target_ancestry": lib.feedback_ancestry(bp["ontology"], "model", bp)}
        bp["ontology_feedback"] = [verdict]
        customer = bpbuild.customer_version(bp, bpbuild.Report())
        self.assertFalse(self.MARKER in json.dumps(customer).upper(), "model verdict cannot quote a private child as public")

    def test_malformed_checked_mapping_cannot_validate_or_write(self):
        for defect in ("missing entity", "missing table", "unknown source", "empty sources"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                model = mini()
                standard = copy.deepcopy(lib.load_cdm()["entities"]["Asset"])
                standard["checked"] = True
                if defect == "missing entity":
                    standard.pop("entity")
                elif defect == "missing table":
                    standard.pop("table")
                elif defect == "unknown source":
                    standard["src"] = ["NOT-A-SOURCE"]
                else:
                    standard["src"] = []
                model["entity_types"][0]["standard"] = standard
                rep = lib.Rep()
                normalized = lib.normalize(model, None, rep)
                self.assertTrue(rep.errors, defect)
                self.assertIs(normalized["entity_types"][0]["standard"]["checked"], False)
                path = tmp / "model.json"
                path.write_text(json.dumps(model), encoding="utf-8")
                code, text = quiet(build.main, ["--ontology", str(path), "--strict", "--out-dir", str(tmp / "output")])
                self.assertEqual(code, 1, text)
                self.assertFalse((tmp / "output").exists())

    def product_model(self, use="grounding", via=None):
        model = mini()
        model["data_products"] = [{"id": "DP-review", "name": "Public product", "entities": ["Asset"],
            "owner": "Synthetic owner", "purpose": "Synthetic purpose", "access": "Reviewed request", "quality": "Assessed",
            "uses": [{"use": use, "via": via or ["MISSING-AGENT"]}]}]
        return model

    def test_product_publication_rejects_unknown_and_wrong_pool_agents(self):
        for use, via in (("grounding", ["MISSING-AGENT"]), ("actions", ["DA-01"])):
            with self.subTest(use=use), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                model = self.product_model(use, via)
                rep = lib.Rep()
                normalized = lib.normalize(model, None, rep)
                self.assertEqual(normalized["stats"]["data_products_ready"], 0)
                self.assertTrue(normalized["data_products"][0]["gaps"])
                self.assertTrue(any(via[0] in message for message in rep.errors + rep.warnings))
                path = tmp / "model.json"
                path.write_text(json.dumps(model), encoding="utf-8")
                code, text = quiet(build.main, ["--ontology", str(path), "--strict", "--out-dir", str(tmp / "output")])
                self.assertEqual(code, 1, text)
                self.assertFalse((tmp / "output").exists())

    def test_product_via_private_agent_is_removed_before_customer_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            model = self.product_model(via=["DA-01"])
            model["data_products"][0]["name"] = self.MARKER + " product"
            model["data_agents"][0]["visibility"] = "internal"
            path = tmp / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            code, text = quiet(build.main, ["--ontology", str(path), "--audience", "customer", "--out-dir", str(tmp / "output")])
            self.assertEqual(code, 0, text)
            self.assert_no_export_marker(tmp / "output")
            normalized = json.loads((tmp / "output/ontology.normalized.json").read_text(encoding="utf-8"))
            self.assertFalse(any("DA-01" in json.dumps(p.get("uses")) for p in normalized["data_products"]))

    def test_product_binding_types_fail_without_rendering_or_writes(self):
        for field in ("via", "producer"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                tmp = Path(directory)
                model = self.product_model(via=["DA-01"])
                if field == "via":
                    model["data_products"][0]["uses"][0]["via"] = [{"id": "DA-01"}]
                else:
                    model["data_products"][0]["agents"] = [{"id": "DA-01"}]
                rep = lib.Rep()
                lib.normalize(model, None, rep)
                self.assertTrue(rep.errors, "malformed binding types are model errors, not publication warnings")
                path = tmp / "model.json"
                path.write_text(json.dumps(model), encoding="utf-8")
                code, text = quiet(build.main, ["--ontology", str(path), "--out-dir", str(tmp / "output")])
                self.assertEqual(code, 1, text)
                self.assertFalse((tmp / "output").exists())

    def test_product_use_pools_accept_valid_bindings_and_preserve_unknown_gaps(self):
        for use, target in (("grounding", "DA-01"), ("actions", "OA-01"), ("analytics", "SM-01")):
            with self.subTest(use=use):
                model = self.product_model(use, [target])
                model["operations_agents"] = [{"id": "OA-01", "name": "Public operations", "entities": ["Asset"], "rules": ["Public rule"]}]
                model["semantic_models"] = [{"id": "SM-01", "name": "Public model", "facts": ["WorkOrder"], "dimensions": ["Asset", "Date"]}]
                rep = lib.Rep()
                normalized = lib.normalize(model, None, rep)
                self.assertEqual(rep.errors, [])
                self.assertEqual(normalized["stats"]["data_products_ready"], 1)
                self.assertEqual(normalized["data_products"][0]["gaps"], [])
        model = self.product_model()
        normalized = lib.normalize(model)
        self.assertEqual(normalized["data_products"][0]["uses"][0]["via"], ["MISSING-AGENT"])
        self.assertTrue(any("MISSING-AGENT" in gap for gap in normalized["data_products"][0]["gaps"]))

    def test_semantic_model_tie_is_identical_across_hash_seed_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            model = mini()
            model["entity_types"][1]["journeys"] = ["D1"]
            model["metrics"] = [{"name": "Metric A", "journey": "D1", "semantic_model": "Alpha", "measure": "[A]"},
                                {"name": "Metric B", "journey": "D1", "semantic_model": "Beta", "measure": "[B]"}]
            path = tmp / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            results = []
            for hash_seed in ("1", "2", "3", "4"):
                output = tmp / ("output-" + hash_seed)
                process = subprocess.run([sys.executable, str(ROOT / SK / "scripts/build_ontology.py"), "--ontology", str(path), "--out-dir", str(output)],
                    capture_output=True, text=True, check=False, env=dict(os.environ, PYTHONHASHSEED=hash_seed))
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                results.append({p.name: p.read_bytes() for p in output.iterdir()})
            for result in results:
                self.assertTrue(result == results[0], "artifacts differ between fresh hash-seed processes")
                self.assertEqual(json.loads(result["ontology.normalized.json"])["semantic_models"][0]["name"], "Alpha")

    def test_failed_seed_does_not_overwrite_good_or_create_new_output(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            bp = tmp / "blueprint.json"
            bp.write_text(json.dumps(self.public_blueprint()), encoding="utf-8")
            patterns = lib.load_patterns()
            patterns["patterns"][0]["entities"].append({"id": "2Invalid", "name": "Invalid synthetic entity",
                                                        "key": ["id"], "properties": [{"name": "id", "type": "string"}]})
            custom = tmp / "patterns.json"
            custom.write_text(json.dumps(patterns), encoding="utf-8")
            good = tmp / "good.json"
            good.write_bytes(b"previous valid seed\n")
            code, text = quiet(seed.main, ["--blueprint", str(bp), "--patterns", str(custom), "--out", str(good)])
            self.assertEqual(code, 1, text)
            self.assertEqual(good.read_bytes(), b"previous valid seed\n")
            fresh = tmp / "new-output.json"
            code, text = quiet(seed.main, ["--blueprint", str(bp), "--patterns", str(custom), "--out", str(fresh)])
            self.assertEqual(code, 1, text)
            self.assertFalse(fresh.exists())
            missing_parent = tmp / "missing-parent" / "seed.json"
            code, text = quiet(seed.main, ["--blueprint", str(bp), "--patterns", str(custom), "--out", str(missing_parent)])
            self.assertEqual(code, 1, text)
            self.assertFalse(missing_parent.parent.exists())


if __name__ == "__main__":
    unittest.main()
