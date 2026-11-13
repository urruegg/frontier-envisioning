(function(){
"use strict";

/* ===================================================================
   Frontier Company Blueprint renderer
   Data: <script type="application/json" id="bp-data"> (blueprint JSON)
   Built by the Frontier Envisioning plugin (build_blueprint.py)
   Renderer code: Copyright (c) 2026 Urs Rüegg · SPDX-License-Identifier: MIT
   =================================================================== */

var RAW = document.getElementById("bp-data");
var BP = null;
try { BP = JSON.parse(RAW ? RAW.textContent : "null"); } catch (e) { BP = null; }

var NS = "http://www.w3.org/2000/svg";
var TBC = "To be confirmed";

/* ---------------- helpers ---------------- */
function h(tag, attrs){
  var n = document.createElement(tag);
  setAttrs(n, attrs);
  for (var i = 2; i < arguments.length; i++) add(n, arguments[i]);
  return n;
}
function s(tag, attrs){
  var n = document.createElementNS(NS, tag);
  setAttrs(n, attrs);
  for (var i = 2; i < arguments.length; i++) add(n, arguments[i]);
  return n;
}
function setAttrs(n, attrs){
  if (!attrs) return;
  Object.keys(attrs).forEach(function(k){
    var v = attrs[k];
    if (v === undefined || v === null || v === false) return;
    if (k.slice(0,2) === "on" && typeof v === "function") n.addEventListener(k.slice(2), v);
    else if (k === "text") n.textContent = v;
    else n.setAttribute(k, v === true ? "" : String(v));
  });
}
function add(n, kid){
  if (kid === undefined || kid === null || kid === false) return;
  if (Array.isArray(kid)) { kid.forEach(function(k){ add(n, k); }); return; }
  if (typeof kid === "string" || typeof kid === "number") n.appendChild(document.createTextNode(String(kid)));
  else n.appendChild(kid);
}
function arr(x){ return Array.isArray(x) ? x : (x === undefined || x === null || x === "" ? [] : [x]); }
function has(x){ return !(x === undefined || x === null || x === "" || (Array.isArray(x) && !x.length) || (typeof x === "object" && !Array.isArray(x) && !Object.keys(x).length)); }
function txt(v){ return has(v) ? String(v) : null; }
function val(v){ return has(v) ? (Array.isArray(v) ? v.join(" · ") : String(v)) : h("span",{class:"tbc"},TBC); }
function ul(a){ a = arr(a); return a.length ? h("ul",{class:"clean"}, a.map(function(x){ return h("li",null, itemText(x)); })) : h("span",{class:"tbc"},TBC); }
function itemText(x){
  if (x && typeof x === "object" && !Array.isArray(x)) return [x.text || x.name || x.q || "", x.src ? evPills(x.src) : null, x.status ? statusPill(x.status) : null];
  if (Array.isArray(x)) return x.join(" · ");
  return String(x);
}
function initials(sv){
  sv = String(sv || "").replace(/\(.*?\)/g, "").replace(/ Agent$/i, "").trim();
  var w = sv.split(/[\s\/&\-·]+/).filter(function(z){ return /^[A-Za-z0-9ÄÖÜäöüÉéÈèÀà]/.test(z); });
  if (!w.length) return "?";
  if (w.length === 1) return w[0].slice(0,2).toUpperCase();
  return (w[0][0] + w[1][0]).toUpperCase();
}
function shortName(a){ return a.short || String(a.name || "").replace(/ Agent$/i, ""); }
/* agent identity (frontier-agent-identity kit): icon and display names, when present */
var ICON_OK = /^data:image\/(svg\+xml|png);base64,[A-Za-z0-9+\/=]+$/;
function idIcon(a, cls){
  var i = a && a.identity, src = i && i.icon;
  if (!src || !ICON_OK.test(src)) return null;
  return h("img",{class:cls || "aicon", src:src, alt:"", "aria-hidden":"true"});
}
function idName(a){ return a && a.identity && a.identity.display_name ? String(a.identity.display_name) : null; }
function idNames(a){
  var n = a && a.identity && a.identity.names;
  return n ? Object.keys(n).map(function(k){ return n[k]; }).join(" \u00b7 ") : null;
}
function nameOf(a){ return idName(a) || (a && a.name) || ""; }
function shortOf(a){ return idName(a) || shortName(a); }
function idTok(a){ var t = a && a.identity && a.identity.tokens; return t && typeof t === "object" ? t : null; }
/* org-chart label: lead agents show their display name, specialists the domain (and scope) part of it */
function orgLabel(a){
  var t = idTok(a);
  if (!t || !idName(a)) return a.alias || shortName(a);
  if (a.role === "lead") return idName(a);
  return [t.domain, t.scope].filter(function(x){ return x; }).join(" ") || idName(a);
}
function idSrc(a, env){
  var i = a && a.identity; if (!i) return null;
  var src = i.icons && typeof i.icons === "object" ? i.icons[env] : null;
  if (!src && (!env || env === prodEnv())) src = i.icon;
  return src && ICON_OK.test(src) ? src : null;
}
function idEnvIcon(a, env, cls){ var src = idSrc(a, env); return src ? h("img",{class:cls || "aicon", src:src, alt:"", "aria-hidden":"true"}) : null; }
function isMvp(a){ return !!(a && (a.mvp || (a.identity && a.identity.status_class === "mvp"))); }
function hex(c, fallback){ return /^#[0-9A-Fa-f]{6}$/.test(c || "") ? c : fallback; }
/* Black or white, whichever has the higher WCAG contrast on this opaque sRGB fill.
   The crossover is sqrt(.05 * 1.05) - .05; do not round ratios to pass AA. */
function onColor(c){
  c = hex(c, "#0F6CBD");
  var rgb = [1,3,5].map(function(i){
    var v = parseInt(c.slice(i, i + 2), 16) / 255;
    return v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4);
  });
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722 > .1791287847 ? "#000000" : "#FFFFFF";
}
function filled(c){ c = hex(c, ACCENT); return "background:" + c + ";color:" + onColor(c); }
function domainStyle(c){ c = hex(c, ACCENT); return "--d:" + c + ";--d-on:" + onColor(c); }
function soft(c, a){ c = hex(c, "#0F6CBD"); var r = parseInt(c.slice(1,3),16), g = parseInt(c.slice(3,5),16), b = parseInt(c.slice(5,7),16); return "rgba(" + r + "," + g + "," + b + "," + a + ")"; }
var DARK = !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
function wrapWords(t, max, lines){
  var words = String(t).split(/\s+/), out = [], cur = "";
  words.forEach(function(w){
    if (!cur) cur = w;
    else if ((cur + " " + w).length <= max) cur += " " + w;
    else { out.push(cur); cur = w; }
  });
  if (cur) out.push(cur);
  if (out.length > lines){ out = out.slice(0, lines); out[lines-1] = out[lines-1].replace(/.{0,2}$/, "") + "…"; }
  return out.map(function(l){ return l.length > max + 2 ? l.slice(0, max) + "…" : l; });
}

/* ---------------- vocabularies ---------------- */
var STATUS = {
  hypothesis:{label:"Hypothesis", cls:"hyp"},
  validated:{label:"Validated", cls:"val"},
  adjusted:{label:"Adjust", cls:"adj"},
  adjust:{label:"Adjust", cls:"adj"},
  rejected:{label:"Rejected", cls:"rej"},
  open:{label:"Open", cls:"open"},
  partial:{label:"Partly answered", cls:"adj"},
  answered:{label:"Answered", cls:"val"}
};
function statusPill(st){ var k = String(st || "hypothesis").toLowerCase(); var m = STATUS[k] || {label: st, cls:""}; return h("span",{class:"pill " + m.cls}, m.label); }
var AUTONOMY = [
  {n:1, label:"Assist", meaning:"Answers, drafts and suggests; a person decides and acts"},
  {n:2, label:"Act with approval", meaning:"Prepares and executes once a person approves at the seam"},
  {n:3, label:"Act within guardrails", meaning:"Executes within a mandate; people handle exceptions and audit"}
];
function autonomyOf(a){
  if (a && a.autonomy_level >= 1 && a.autonomy_level <= 3) return AUTONOMY[a.autonomy_level - 1];
  var t = String((a && a.autonomy) || "").toLowerCase();
  if (!t) return null;
  if (/approv|semi/.test(t)) return AUTONOMY[1];
  if (/guardrail|autonom|mandate|budget/.test(t)) return AUTONOMY[2];
  return AUTONOMY[0];
}
var EVT = { transcript:"Transcript", meeting:"Meeting", email:"Email", chat:"Teams chat", file:"Document", web:"Public web", workshop:"Workshop", hypothesis:"Microsoft hypothesis", note:"Note", crm:"CRM record" };
var DECL = [
  ["write_envelope","Write envelope","Which systems and fields it may change, and under which conditions"],
  ["refusal_set","Refusal set","When it stops, and how it records why"],
  ["escalation_path","Escalation path","The named person it hands over to, and how"],
  ["grounding_sources","Grounding sources","What it may read and cite"],
  ["data_classification","Data classification","The sensitivity of the data it touches"],
  ["people_decisions","People-decision surface","Whether its output shapes decisions about people, and who decides"],
  ["measurement","Measurement","How success, quality and cost are measured"]
];
var PROFILE = [
  ["Starting point & contribution", [["starting_point","Starting point"],["contribution","Contribution"],["impact","Impact"]]],
  ["Mission & output", [["mission","Mission"],["trigger","Trigger"],["input","Input"],["output","Output"]]],
  ["Tasks", [["tasks","Tasks"]]],
  ["Team & leadership", [["reports_to","Reports to"],["works_with","Works with"],["hands_off_to","Hands off to"]]],
  ["Interaction & autonomy", [["autonomous","Autonomous"],["approval","Approval"],["escalation","Escalation"]]],
  ["Knowledge, rules & limits", [["knowledge","Knowledge"],["rules","Rules"],["not_allowed","Not allowed"]]],
  ["Systems & channels", [["systems","Systems"],["channels","Channels"]]],
  ["Communication & personality", [["tone","Tone"],["language","Language"]]],
  ["Success & measurement", [["kpis","KPIs"]]]
];

/* ---------------- empty template ---------------- */
if (!BP || typeof BP !== "object" || Array.isArray(BP)){
  var v0 = document.getElementById("view");
  v0.appendChild(h("div",{class:"empty"},
    h("h2",null,"Frontier Company Blueprint template"),
    h("p",null,"This template has no blueprint data yet."),
    h("p",null,"Build it with the Frontier Envisioning plugin: ask Copilot Cowork to \u201cbuild the Frontier blueprint for <customer>\u201d, or run build_blueprint.py with a blueprint JSON file.")));
  document.getElementById("rail").classList.add("hidden");
  return;
}

/* ---------------- normalise ---------------- */
var M = BP.meta || {};
var D = arr(BP.domains);
var ACCENT = hex(M.accent, "#0F6CBD");
document.documentElement.style.setProperty("--accent", ACCENT);
document.documentElement.style.setProperty("--accent-on", onColor(ACCENT));
document.documentElement.style.setProperty("--accent-soft", DARK ? soft(ACCENT, .18) : soft(ACCENT, .09));
document.documentElement.style.setProperty("--accent-line", soft(ACCENT, .45));
document.title = (M.title || ((M.customer || "Customer") + " \u00b7 Frontier Company Blueprint"));

var AG = {};            // id -> agent
var ALL = [];           // flat list of agents
var UCS = [];           // all use cases
var EV = {};            // evidence by id
var USED = {};          // evidence id -> list of labels
D.forEach(function(d, di){
  d.id = d.id || ("D" + (di + 1));
  d.color = hex(d.color, ["#0F6CBD","#C239B3","#107C41","#CA5010","#5C2E91","#038387","#986F0B","#4F6BED"][di % 8]);
  d.agents = arr(d.agents);
  if (d.orchestrator){
    var o = d.orchestrator;
    o.id = o.id || (d.id + "-LEAD");
    o.role = "lead";
    o._d = d;
    if (!o.capability) o.capability = o.mission;
    AG[o.id] = o; ALL.push(o);
  }
  d.agents.forEach(function(a, ai){
    a.id = a.id || (d.id + "-A" + String(ai + 1).padStart(2, "0"));
    a.role = a.role || "specialist";
    a._d = d;
    AG[a.id] = a; ALL.push(a);
  });
  arr(d.use_cases).forEach(function(u){ u.domain = u.domain || d.id; UCS.push(u); });
});
arr(BP.use_cases).forEach(function(u){ UCS.push(u); });
UCS.forEach(function(u, i){ u.id = u.id || ("UC" + String(i + 1).padStart(2, "0")); });
arr(BP.evidence).forEach(function(e, i){ e.id = e.id || ("E" + String(i + 1).padStart(2, "0")); EV[e.id] = e; });
/* agent identity: top-level block written by the identity kit (apply_identity.py) */
var IDN = BP.identity && typeof BP.identity === "object" && !Array.isArray(BP.identity) ? BP.identity : null;
function idTeam(){
  var out = [];
  D.forEach(function(d){
    (d.orchestrator ? [d.orchestrator] : []).concat(d.agents, d.data_agent && typeof d.data_agent === "object" ? [d.data_agent] : []).forEach(function(a){ if (a && a.identity) out.push({a:a, d:d}); });
  });
  return out;
}
function hasIdentity(){ return !!IDN || idTeam().length > 0; }
function idEnvList(){ return IDN ? arr(IDN.environments).filter(function(x){ return x && x.name; }) : []; }
function idEnvs(){
  var e = idEnvList();
  if (e.length) return e;
  var t = idTeam().filter(function(x){ return x.a.identity.names; })[0];
  return t ? Object.keys(t.a.identity.names).map(function(n){ return {name:n}; }) : [];
}
function prodEnv(){
  var e = idEnvList(), p = e.filter(function(x){ return x.production; })[0];
  return p ? p.name : (e.length ? e[e.length - 1].name : "PROD");
}
function envOrder(){ var p = prodEnv(); return [p].concat(idEnvs().map(function(e){ return e.name; }).filter(function(n){ return n !== p; }).reverse()); }
/* ---------------- product icons (Microsoft and GitHub; see logos_note) ---------------- */
var LOGO = BP.logos && typeof BP.logos === "object" && !Array.isArray(BP.logos) ? BP.logos : {};
var IMG_OK = /^data:image\/(svg\+xml|png|jpeg|gif|webp);base64,[A-Za-z0-9+\/=]+$/;
var LOGO_RULES = [];
arr(BP.logo_rules).forEach(function(r){ try { if (Array.isArray(r) && LOGO[r[1]]) LOGO_RULES.push([new RegExp(r[0], "i"), r[1]]); } catch (e) {} });
function logo(key, size, white){
  var L = LOGO[key]; if (!L) return null;
  var src = white && L.uri_white ? L.uri_white : L.uri;
  if (!IMG_OK.test(src || "")) return null;
  var z = String(size || 20);
  return h("img",{class:"mslogo", src:src, alt:"", title:L.name || key, width:z, height:z});
}
function logosFor(text, size, max){
  var t = String(text || ""), out = [], seen = {};
  for (var i = 0; i < LOGO_RULES.length && out.length < (max || 3); i++){
    var r = LOGO_RULES[i];
    if (!seen[r[1]] && r[0].test(t)){ var im = logo(r[1], size || 18); if (im){ out.push(im); seen[r[1]] = 1; } }
  }
  return out.length ? h("span",{class:"logos"}, out) : null;
}
function logoRow(keys, size){ var l = arr(keys).map(function(k){ return logo(k, size || 22); }).filter(Boolean); return l.length ? h("span",{class:"logos"}, l) : null; }
function ulLogos(a){
  a = arr(a);
  return a.length ? h("ul",{class:"clean lgl"}, a.map(function(x){ return h("li",null, logosFor(typeof x === "string" ? x : (x && (x.text || x.name)) || "", 16, 2), itemText(x)); })) : h("span",{class:"tbc"},TBC);
}
/* ---------------- Agent Factory journey ---------------- */
var FAC = BP.factory && typeof BP.factory === "object" && !Array.isArray(BP.factory) ? BP.factory : null;
function isFactory(d){ return !!d && (d.kind === "factory" || (!!FAC && FAC.journey === d.id)); }
function facDom(){ return D.filter(isFactory)[0] || null; }
/* business value and FinOps: blocks written by frontier-value-case (apply_value.py) and frontier-finops (apply_finops.py) */
var VC = BP.value_case && typeof BP.value_case === "object" && !Array.isArray(BP.value_case) ? BP.value_case : null;
var FO = BP.finops && typeof BP.finops === "object" && !Array.isArray(BP.finops) ? BP.finops : null;
var ONT = BP.ontology && typeof BP.ontology === "object" && !Array.isArray(BP.ontology) ? BP.ontology : null;
var FINOPS_NOTICE = "Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.";
/* Viewer awareness only, scoped to this document instance. Artifact metadata is neither
   human approval nor encryption/access control. Never read or save consent in NOTES. */
var previewAcknowledged = false;
/* Successor DTO boundary only. Projection, Decimal arithmetic, lineage/scope and
   exact-target review validation belong to the offline producer, not this UI.
   Never select a last revision or silently fall back to legacy cost caches. */
function baselineObject(v){ return !!v && typeof v === "object" && !Array.isArray(v); }
var AF_PRESENT = Object.prototype.hasOwnProperty.call(BP,"agent_finops");
var AF = resolveAgentFinops();
function resolveAgentFinops(){
  var v = BP.agent_finops, seen = Object.create(null);
  if (!AF_PRESENT) return {records:[],error:null};
  var error = "Financial data incomplete: unsupported, malformed or conflicting FinOps derivative. Rebuild from authoritative sources, date, audience/scope and external review; do not reuse cached reports.";
  if (Object.prototype.hasOwnProperty.call(BP,"finops") || !baselineObject(v) ||
      v.schema !== "frontier-agent-finops-view/1.0" || v.maturity !== "Preview" ||
      v.financial_permission !== false || !/^\d{4}-\d{2}-\d{2}$/.test(v.as_of || "") ||
      ["internal","customer"].indexOf(v.audience) < 0 || !Array.isArray(v.records) ||
      typeof v.notice !== "string" || typeof v.limitations !== "string") return {records:[],error:error};
  function decimals(value){
    if (!value || typeof value !== "object") return true;
    if (Object.prototype.hasOwnProperty.call(value,"amount") &&
        value.amount !== null && (typeof value.amount !== "string" || !/^-?\d+(?:\.\d+)?$/.test(value.amount))) return false;
    return Object.keys(value).every(function(k){ return decimals(value[k]); });
  }
  var valid = v.records.every(function(r){
    if (!baselineObject(r) || r.schema !== "frontier-agent-finops-report/1.0" ||
        r.maturity !== "Preview" || r.financial_permission !== false ||
        r.as_of !== v.as_of || r.audience !== v.audience ||
        typeof r.notice !== "string" || typeof r.limitations !== "string" ||
        !baselineObject(r.profile) || !baselineObject(r.context) || !baselineObject(r.formulas) ||
        !baselineObject(r.scenarios) || !Array.isArray(r.scenario_inputs) ||
        !baselineObject(r.evidence) || !Array.isArray(r.gaps) || !baselineObject(r.handover) ||
        !decimals(r.scenarios)) return false;
    /* Only typed financial locations, not arbitrary source annotations with an
       authored key called amount. Rate records are not result-money objects. */
    if (r.evidence.rates !== undefined && (!Array.isArray(r.evidence.rates) ||
        !r.evidence.rates.every(function(rate){
          return baselineObject(rate) && (rate.amount === undefined || rate.amount === null ||
            (typeof rate.amount === "string" && /^-?\d+(?:\.\d+)?$/.test(rate.amount)));
        }))) return false;
    if (r.agent_id === null) return r.status === "withheld" && r.baseline === null && r.currency === null;
    if (typeof r.agent_id !== "string" || !AG[r.agent_id] || seen[r.agent_id] ||
        !baselineObject(r.baseline) || (r.currency !== null && typeof r.currency !== "string")) return false;
    seen[r.agent_id] = true;
    return ["low","expected","high"].every(function(id){
      var sc = r.scenarios[id];
      return !sc || (baselineObject(sc) && Array.isArray(sc.months) &&
        Array.isArray(sc.one_time_lines) && baselineObject(sc.unit_metrics));
    });
  });
  return valid ? {records:v.records,error:null} : {records:[],error:error};
}
function baselineFor(a){ return AF.records.filter(function(r){ return r.agent_id === a.id; })[0] || null; }
function financialEvidence(a){
  var r = baselineFor(a), g = r && r.handover, review = g && g.owner_review;
  function synthetic(v){
    return !!(v && typeof v === "object" && (v.synthetic === true ||
      ["type","status","validationStatus","mode"].some(function(k){ return v[k] === "synthetic"; }) ||
      Object.keys(v).some(function(k){ return synthetic(v[k]); })));
  }
  function available(m){
    return baselineObject(m) && m.status === "available" && typeof m.amount === "string" && m.currency === r.currency;
  }
  function units(v){
    return baselineObject(v) && ["per_run","per_success","per_outcome"].every(function(k){
      var m = v[k];
      return available(m) && typeof m.denominator === "string" && /^\d+(?:\.\d+)?$/.test(m.denominator) && !/^0+(?:\.0+)?$/.test(m.denominator);
    });
  }
  function completeScenario(sc){
    return baselineObject(sc) && ["annual_recurring","one_time","first_year"].every(function(k){ return available(sc[k]); }) &&
      Array.isArray(sc.months) && sc.months.length === 12 &&
      sc.months.every(function(m){ return baselineObject(m) && available(m.total) && units(m); }) &&
      baselineObject(sc.unit_metrics) && units(sc.unit_metrics.annual_recurring) && units(sc.unit_metrics.first_year);
  }
  /* Consume the dated generated decision, not raw authored status, local NOTES,
     a technical fixture flag or client-side revalidation of financial inputs.
     Customer projection intentionally omits technical target hashes. */
  return !!(!AF.error && r && r.mode === "planning" && r.status === "planning-ready" &&
    g.schema === "frontier-finops-handover/1.0" && g.as_of === r.as_of &&
    g.financial_permission === false && g.ready === true && g.status === "planning-ready" &&
    g.structural_validation === "valid" && g.pricing_completeness === "evidenced" &&
    Array.isArray(g.gaps) && !g.gaps.length && !r.gaps.length && !synthetic(r) &&
    ["low","expected","high"].every(function(k){ return completeScenario(r.scenarios[k]); }) &&
    baselineObject(review) && review.schema === "frontier-finops-owner-review/1.0" &&
    review.decision === "approve" && review.mode === "planning" && review.synthetic !== true &&
    review.assertion === "externally-asserted-not-authenticated" &&
    review.baseline_id === r.baseline.id && review.version === r.baseline.version &&
    (r.audience === "customer" || (baselineObject(g.target) && g.target.baseline_id === r.baseline.id &&
      g.target.version === r.baseline.version && typeof g.target.material_hash === "string" && g.target.material_hash.length > 0 &&
      review.material_hash === g.target.material_hash)));
}
function financialSummary(a){
  var r = baselineFor(a), ready = financialEvidence(a);
  return h("div",{class:"financial-summary callout","data-agent":a.id,"data-financial-ready":String(ready)},
    h("b",null, ready ? "Financial handover planning evidence" : "Financial handover gap"),
    h("p",null, ready ? "Generated planning evidence as of " + r.as_of + "; external review is not authenticated. Not budget, purchase, build or deployment permission."
      : (AF.error ? AF.error : r ? "Dated financial evidence is blocked, incomplete, withheld, provisional or synthetic. Rebuild and obtain external exact-target review."
        : "Supply an authoritative per-agent baseline, validate and price every in-scope driver, freeze the target and obtain external finance-owner review.")),
    h("p",{class:"note"},"Required at build handover only. Core drafts and workshops continue with gaps. Notes cannot approve; renew from authoritative sources for changed inputs or dates."),
    AF_PRESENT ? h("button",{type:"button",class:"btn",onclick:function(){ go("finops"); }},"Review FinOps evidence") : null);
}
function previewDerived(value){
  return !!(value && (Object.prototype.hasOwnProperty.call(value,"finops_preview") || value.finops));
}
var VALUE_FINANCIAL_FIELDS = ["npv","npv_budget","roi","payback_months","cost_year","build","pv_cost","break_even","scenarios","rank","swing_npv"];
/* One resolver for the supported flat / results shape. The selected result is
   authoritative for financial fields: missing/redacted nested amounts must not
   fall back to an old outer cache. Keep independent outer values and metadata,
   while collecting ancestry and assumption links from both layers. Never walk
   opaque notes or recursively discover alternative financial objects. */
function caseValueSource(u){
  var outer = u && u.business_value;
  if (!outer || typeof outer !== "object" || Array.isArray(outer)) return null;
  var nested = outer.results && typeof outer.results === "object" && !Array.isArray(outer.results) ? outer.results : null;
  var result = nested || outer, value = Object.create(null);
  Object.keys(outer).forEach(function(k){
    if (k !== "results" && k !== "internal_notes" && (!nested || VALUE_FINANCIAL_FIELDS.indexOf(k) < 0)) value[k] = outer[k];
  });
  if (nested) Object.keys(result).forEach(function(k){
    if (k !== "results" && k !== "internal_notes") value[k] = result[k];
  });
  return {value:value,ancestry:nested ? [outer,result] : [outer],
    assumptions:arr(outer.assumptions).concat(nested ? arr(result.assumptions) : [])};
}
function casePreview(u){
  var source = caseValueSource(u);
  return !!FO || previewDerived(VC) || !!(source && (source.ancestry.some(previewDerived) ||
    source.assumptions.some(function(id){ return assumptionPreview(ASSM[id]); })));
}
/* Aggregate provenance is the union of the actual contributing cases, not only
   the wrapper's marker. Do not spread a sibling's provenance to a public case,
   or recompute a public-only subset and label it as the full portfolio. */
function portfolioPreview(){
  return !!FO || previewDerived(VC) || previewDerived(VC && VC.totals) ||
    UCS.some(function(u){ return u.business_value && casePreview(u); }) ||
    arr(VC && VC.assumptions).some(assumptionPreview);
}
function previewPresent(){ return AF_PRESENT || portfolioPreview() || Object.keys(ASSM).some(function(id){ return assumptionPreview(ASSM[id]); }); }
function previewNotice(){
  return h("aside",{class:"preview-notice",role:"note","aria-label":"FinOps Preview notice"},
    h("p",null, FINOPS_NOTICE),
    h("p",null, previewAcknowledged ? "Provisional comparisons, not recommendations. Source restrictions still apply; acknowledgement is not budget approval." : "Preview-derived figures are withheld. Script/caller metadata does not acknowledge this viewer."),
    previewAcknowledged ? null : h("button",{id:"finops-preview-ack",type:"button",class:"btn",onclick:function(){
      previewAcknowledged = true; render(); document.getElementById("view").focus({preventScroll:true});
    }},"I acknowledge Preview estimates for this blueprint"));
}
function presentedValue(value, inheritedPreview){
  if (!value || previewAcknowledged || !(inheritedPreview || previewDerived(value))) return value;
  var out = Object.create(null);
  Object.keys(value).forEach(function(k){
    if (VALUE_FINANCIAL_FIELDS.indexOf(k) < 0 && k !== "results" && k !== "internal_notes") out[k] = value[k];
  });
  return out;
}
var ASSM = {};
arr(VC && VC.assumptions).concat(arr(FO && FO.assumptions)).forEach(function(a){ if (a && a.id && !ASSM[a.id]) ASSM[a.id] = a; });
/* Source membership is provenance even when the value register also has a copy
   of this ID. Do not infer consent from any marker, maturity or acknowledgement. */
var FO_ASSUMPTIONS = {};
arr(FO && FO.assumptions).forEach(function(a){ if (a && a.id) FO_ASSUMPTIONS[a.id] = true; });
function assumptionPreview(a){ return !!(a && (FO_ASSUMPTIONS[a.id] || previewDerived(a))); }
function assumptionWithheld(a){ return !previewAcknowledged && assumptionPreview(a); }
function presentedAssumption(a){
  if (!assumptionWithheld(a)) return a;
  /* Do not merely blank the numeric cells: model statements/questions/notes can
     themselves contain rates or cost figures. Keep identity/source constraints. */
  return {id:a.id,statement:"FinOps Preview assumption \u2014 figures withheld until viewer acknowledgement",
    status:a.status,src:a.src,source_type:a.source_type,confidence:a.confidence,owner:a.owner,
    use_cases:a.use_cases,internal:a.internal,customer_facing:a.customer_facing};
}
function presentedAssumptionVerdict(a, verdict){
  if (!assumptionWithheld(a)) return verdict;
  var out = {};
  Object.keys(verdict).forEach(function(k){ if (k !== "value") out[k] = verdict[k]; });
  return out;
}
function withheldAssumptionValue(){ return h("span",{class:"note"},"Numeric value withheld (FinOps Preview)"); }
function num(x){ return typeof x === "number" && isFinite(x); }
function grp(n, dec){ if (!num(n)) return TBC; var p = Math.abs(n).toFixed(dec || 0).split("."); p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ","); return (n < 0 ? "\u2212" : "") + p.join("."); }
function curr(){ return (VC && VC.currency) || (FO && FO.currency) || "CHF"; }
function chf(x, short){
  if (!num(x)) return TBC;
  var a = Math.abs(x);
  if (short && a >= 1e6) return curr() + " " + (x / 1e6).toFixed(a >= 1e7 ? 1 : 2) + "M";
  if (short && a >= 1e4) return curr() + " " + grp(Math.round(x / 1e3)) + "k";
  return curr() + " " + grp(x, a < 100 && x % 1 ? 2 : 0);
}
function pct(x, dec){ return num(x) ? (x * 100).toFixed(dec === undefined ? 0 : dec) + "%" : TBC; }
function fmtA(v, unit){
  if (!num(v)) return h("span",{class:"tbc"},"to collect");
  if (unit === "share") return pct(v, Math.abs(v * 100 - Math.round(v * 100)) > 1e-9 ? 1 : 0);
  return grp(v, v % 1 ? 2 : 0) + (unit ? " " + unit : "");
}
function valueOf(u){ var source = caseValueSource(u); return source ? presentedValue(source.value, casePreview(u)) : null; }
function mvpAgents(m){
  var opt = String(m.option || "").replace(/[^A-Za-z0-9]/g, "").toUpperCase();
  var pool = ALL.filter(function(a){ return isMvp(a) && (!m.domain || (a._d && a._d.id === m.domain)); });
  var exact = pool.filter(function(a){
    var lbl = String(typeof a.mvp === "string" ? a.mvp : ((a.identity && a.identity.status) || "")).trim().toUpperCase();
    return opt && new RegExp("(^|\\W)" + opt + "$").test(lbl);
  });
  return exact.length ? exact : pool;
}
function domById(id){ for (var i = 0; i < D.length; i++) if (D[i].id === id) return D[i]; return null; }
function agentByName(name){
  if (!name) return null;
  var n = String(name).toLowerCase();
  for (var i = 0; i < ALL.length; i++) if (String(ALL[i].name).toLowerCase() === n || ALL[i].id.toLowerCase() === n) return ALL[i];
  return null;
}
function ucById(id){ for (var i = 0; i < UCS.length; i++) if (UCS[i].id === id) return UCS[i]; return null; }
function srcList(src){ if (!has(src)) return []; return (Array.isArray(src) ? src : String(src).split(/[,\s]+/)).filter(Boolean); }
/* index evidence usage */
function scanUse(obj, label){
  if (!obj || typeof obj !== "object") return;
  if (Array.isArray(obj)) { obj.forEach(function(x){ scanUse(x, label); }); return; }
  Object.keys(obj).forEach(function(k){
    if (k === "_d") return;
    if (k === "src") srcList(obj[k]).forEach(function(id){ (USED[id] = USED[id] || []); if (USED[id].indexOf(label) < 0) USED[id].push(label); });
    else if (obj[k] && typeof obj[k] === "object") scanUse(obj[k], label);
  });
}
D.forEach(function(d){
  if (d.orchestrator) scanUse(d.orchestrator, d.orchestrator.name);
  d.agents.forEach(function(a){ scanUse(a, a.name); });
  scanUse({stages:d.stages, personas:d.personas, kpis:d.kpis, discovery:d.discovery, outcomes:d.outcomes, vision:d.vision_src}, d.name);
});
UCS.forEach(function(u){ scanUse(u, u.id + " " + u.name); });
scanUse({m:BP.mission, o:BP.outcomes, f:BP.frontier}, "Vision");
scanUse(BP.architecture, "Target architecture");
scanUse(BP.next_steps, "Next steps");

/* ---------------- local workshop notes ---------------- */
var KEY = "fbp:" + (M.id || M.customer || "blueprint") + ":" + (M.version || "0");
var NOTES = {};
try { NOTES = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { NOTES = {}; }
function saveNotes(){ try { localStorage.setItem(KEY, JSON.stringify(NOTES)); } catch (e) {} }
function note(k){ return NOTES[k] || {}; }
function setNote(k, patch){ var n = NOTES[k] || {}; Object.keys(patch).forEach(function(p){ n[p] = patch[p]; }); n.at = new Date().toISOString(); NOTES[k] = n; saveNotes(); }

/* ---------------- evidence pills ---------------- */
function evPills(src){
  var ids = srcList(src);
  if (!ids.length) return null;
  return h("span",{style:"display:inline-flex;gap:4px;flex-wrap:wrap;margin-inline-start:6px;vertical-align:middle"}, ids.map(function(id){
    var e = EV[id];
    var t = e ? (EVT[e.type] || e.type || "Source") + " \u00b7 " + (e.title || id) : id;
    return h("button",{type:"button",class:"pill ev",title:t,"aria-label":"Evidence " + id + ": " + t,onclick:function(ev){ ev.stopPropagation(); openEvidence(id); }}, id);
  }));
}

/* ---------------- icons ---------------- */
var ICON = {
  overview:'<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
  org:'<circle cx="12" cy="12" r="2.5"/><circle cx="12" cy="12" r="6.5"/><circle cx="12" cy="12" r="10"/><circle cx="18.5" cy="12" r="1.2"/><circle cx="5.5" cy="12" r="1.2"/>',
  blueprint:'<rect x="3" y="3" width="18" height="5" rx="1"/><rect x="3" y="10" width="8" height="11" rx="1"/><rect x="13" y="10" width="8" height="5" rx="1"/><rect x="13" y="17" width="8" height="4" rx="1"/>',
  journeys:'<circle cx="5" cy="17" r="2"/><circle cx="19" cy="7" r="2"/><path d="M7 17h6a3 3 0 0 0 0-6h-2a3 3 0 0 1 0-6h6"/>',
  agents:'<rect x="4" y="7" width="16" height="12" rx="3"/><path d="M12 7V4"/><circle cx="9" cy="13" r="1.3"/><circle cx="15" cy="13" r="1.3"/><path d="M2 12v3M22 12v3"/>',
  architecture:'<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5"/><path d="M3 16.5L12 21l9-4.5"/>',
  usecases:'<path d="M4 20V4"/><path d="M4 20h16"/><circle cx="9" cy="14" r="2"/><circle cx="15" cy="8" r="2.5"/><circle cx="16" cy="15" r="1.5"/>',
  discovery:'<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/><path d="M11 8.5v3l2 1"/>',
  roadmap:'<path d="M3 6h7M3 12h12M3 18h18"/><circle cx="12" cy="6" r="1.6"/><circle cx="17" cy="12" r="1.6"/>',
  evidence:'<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6M10 17h6"/>',
  finops:'<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6v4c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V6"/><path d="M5 10v4c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6v-4"/><path d="M5 14v4c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6v-4"/>',
  attendees:'<circle cx="8" cy="9" r="3"/><circle cx="16.5" cy="10" r="2.5"/><path d="M2.5 19c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5"/><path d="M13.5 16.2c.8-1.2 1.9-1.8 3-1.8 2 0 3.6 1.3 4.2 3.6"/>',
  readiness:'<rect x="4" y="3.5" width="16" height="17" rx="2"/><path d="M8 9l1.6 1.6L13 7.2"/><path d="M8 15l1.6 1.6L13 13.2"/><path d="M15 9.5h2.5M15 15.5h2.5"/>',
  identity:'<rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16.2c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4"/><path d="M14.5 10h4M14.5 13.5h4"/>'
};
ICON.prd = ICON.evidence;
ICON.plan = ICON.blueprint;
ICON.ontology = '<circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="12" cy="18" r="3"/><path d="M8 8l3 7M16 8l-3 7M9 6h6"/>';
ICON.risks = '<path d="M12 3L2 21h20zM12 9v5M12 17v1"/>';
function icon(k){ var sp = document.createElement("span"); sp.className = "ic-wrap"; sp.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (ICON[k] || "") + '</svg>'; return sp; }

/* ---------------- views and state ---------------- */
var VIEWS = [
  {id:"overview", label:"Overview", part:"Vision"},
  {id:"org", label:"Org model", part:"Vision"},
  {id:"blueprint", label:"Blueprint", part:"Vision"},
  {id:"journeys", label:"Journeys", part:"Vision"},
  {id:"usecases", label:"Use cases", part:"Vision", need:function(){ return UCS.length > 0; }},
  {id:"prd", label:"PRD", part:"Vision", need:function(){ return !!(BP.prd && typeof BP.prd === "object" && !Array.isArray(BP.prd)); }},
  {id:"agents", label:"Agents", part:"Design"},
  {id:"identity", label:"Agent identity", part:"Design", need:function(){ return hasIdentity(); }},
  {id:"architecture", label:"Target architecture", part:"Design", need:function(){ return has(BP.architecture); }},
  {id:"ontology", label:"Ontology", part:"Design", need:function(){ return ontEnts().length > 0; }},
  {id:"readiness", label:"IT readiness", part:"Design", need:function(){ return !!(BP.it_readiness && typeof BP.it_readiness === "object"); }},
  {id:"roadmap", label:"Roadmap", part:"Build", need:function(){ return has(BP.next_steps) || has(BP.mvp_options) || D.some(function(d){ return has(d.horizon_plan); }); }},
  {id:"plan", label:"Plan", part:"Build", need:function(){ return ALL.length > 0; }},
  {id:"finops", label:"FinOps", part:"Build", need:function(){ return AF_PRESENT || !!FO; }},
  {id:"attendees", label:"Attendees", part:"Workshop", need:function(){ return has(BP.attendees && BP.attendees.people); }},
  {id:"discovery", label:"Discovery", part:"Workshop", need:function(){ return D.some(function(d){ return has(d.discovery); }); }},
  {id:"risks", label:"Risks", part:"Workshop", need:function(){ return has(BP.risks && BP.risks.items); }},
  {id:"evidence", label:"Evidence", part:"Workshop", need:function(){ return has(BP.evidence); }}
];
var PART_DEF = {
  Vision:{key:"vision",label:"Part 1 \u00b7 Vision",desc:"Envisioning: from the hypothesis to the solution envisioning, the use cases and their business value"},
  Design:{key:"design",label:"Part 2 \u00b7 Design",desc:"From the solution envisioning to the architecture design"},
  Build:{key:"build",label:"Part 3 \u00b7 Build",desc:"From the approved design and scope to the build with the Agent Factory"},
  Workshop:{key:"workshops",label:"Part 4 \u00b7 Workshops",desc:"Who took part and contributed what, open questions, risks and the evidence"}
};
var PARTS = {};
Object.keys(PART_DEF).forEach(function(k){
  var d = PART_DEF[k], o = BP.parts && (BP.parts[d.key] || BP.parts[k]) || {};
  PARTS[k] = {label:o.label || d.label, desc:o.desc || d.desc};
});
var ORDER = VIEWS.filter(function(v){ return !v.need || v.need(); }).map(function(v){ return v.id; });
function viewMeta(id){ for (var i = 0; i < VIEWS.length; i++) if (VIEWS[i].id === id) return VIEWS[i]; return VIEWS[0]; }
var state = { view:"overview", flq:null, flPause:false, flPlay:false, d:0, agent:null, uc:null, archTab:null, lz:"P", lzLens:null, fstep:0, adrFilter:"all", adr:null, orgStage:3, orgDomain:null, labels:true, badges:true, discFilter:"all", planLane:"all", planMvp:false, riskSel:null, riskCat:"all", riskStatus:"active" };
var DOMAIN_VIEWS = ["blueprint","journeys","agents","discovery"];

function readHash(){
  var p = (location.hash || "").replace(/^#\/?/, "").split("/");
  if (p[0] && ORDER.indexOf(p[0]) >= 0) state.view = p[0];
  if (p[1]){
    if (state.view === "usecases") { state.uc = decodeURIComponent(p[1]); }
    else if (state.view === "agents" && AG[decodeURIComponent(p[1])]) { state.agent = decodeURIComponent(p[1]); var dd = AG[state.agent]._d; state.d = Math.max(0, D.indexOf(dd)); }
    else { var di = D.findIndex(function(d){ return d.id === decodeURIComponent(p[1]); }); if (di >= 0) state.d = di; }
  }
}
function writeHash(){
  var tail = "";
  if (state.view === "agents" && state.agent) tail = "/" + encodeURIComponent(state.agent);
  else if (state.view === "usecases" && state.uc) tail = "/" + encodeURIComponent(state.uc);
  else if (DOMAIN_VIEWS.indexOf(state.view) >= 0 && D[state.d]) tail = "/" + encodeURIComponent(D[state.d].id);
  try { history.replaceState(null, "", "#/" + state.view + tail); } catch (e) {}
}
function go(v, opts){
  state.view = v;
  if (opts && opts.d !== undefined) state.d = opts.d;
  if (opts && opts.agent !== undefined) state.agent = opts.agent;
  render(true);
}
function dom(){ return D[state.d] || D[0] || {agents:[]}; }
function setDomainColor(c){
  var st = document.documentElement.style;
  c = hex(c, ACCENT);
  st.setProperty("--domain", c);
  st.setProperty("--domain-on", onColor(c));
  /* Keep muted text readable even for white journeys and nested soft pills. */
  st.setProperty("--domain-soft", soft(c, .1));
}

/* ---------------- chrome ---------------- */
function renderRail(){
  var r = document.getElementById("rail");
  r.replaceChildren();
  var lastPart = null;
  ORDER.forEach(function(id){
    var vm = viewMeta(id);
    if (vm.part !== lastPart){ r.appendChild(h("div",{class:"grp",title:PARTS[vm.part].desc}, PARTS[vm.part].label)); lastPart = vm.part; }
    r.appendChild(h("button",{type:"button","data-view":id,"aria-current": state.view === id ? "page" : null, onclick:function(){ go(id); }}, icon(id), h("span",null, vm.label)));
  });
}
function renderHeader(){
  var t = document.getElementById("top");
  t.replaceChildren();
  var logo = h("div",{class:"logo","aria-hidden":"true"});
  if (M.logo_data_uri && /^data:image\/(png|jpeg|gif|webp);base64,/.test(M.logo_data_uri)) logo.appendChild(h("img",{src:M.logo_data_uri, alt:""}));
  else logo.textContent = initials(M.short || M.customer || "FC");
  t.appendChild(logo);
  t.appendChild(h("div",{class:"vdiv"}));
  t.appendChild(h("div",{class:"ttl"},
    h("div",{class:"eyebrow"}, M.eyebrow || "Frontier Company Blueprint"),
    h("h1",null, M.headline || ((M.customer || "Customer") + " \u2014 hybrid organisation")),
    h("p",null, M.subtitle || "Human-led, agent-operated: a hypothesis for solution envisioning")));
  t.appendChild(h("div",{class:"cobrand"},
    h("b",null, M.prepared_by || "Microsoft Innovation Hub"),
    M.engagement || "Solution envisioning", M.presenter ? h("br") : null, M.presenter || null));
}
function renderBanner(){
  var b = document.getElementById("banner");
  b.replaceChildren();
  var st = String(M.status || "hypothesis").toLowerCase();
  var n = arr(BP.evidence).length;
  b.className = "banner" + (st === "validated" ? " validated" : "");
  if (st === "validated") b.appendChild(h("span",null, h("b",null,"Validated blueprint \u00b7 "), M.status_note || ("Reviewed with " + (M.customer || "the customer") + (M.workshop_date ? " on " + M.workshop_date : "") + ".")));
  else b.appendChild(h("span",null, h("b",null,"Hypothesis \u00b7 "), M.status_note || ("Prepared by Microsoft from " + n + " source" + (n === 1 ? "" : "s") + " for validation with " + (M.customer || "the customer") + (M.workshop_date ? " in the workshop on " + M.workshop_date : "") + ".")));
  if (String(M.audience || "").toLowerCase() === "internal") b.appendChild(h("span",{class:"pill int"},"Internal \u2014 contains Microsoft-internal context; do not share externally"));
  else if (M.audience) b.appendChild(h("span",{class:"pill val"},"Customer-ready version"));
  if (M.version) b.appendChild(h("span",{class:"pill"}, "v" + M.version + (M.date ? " \u00b7 " + M.date : "")));
}
function renderCrumb(){
  var c = document.getElementById("crumb");
  var vm = viewMeta(state.view), i = ORDER.indexOf(state.view);
  c.replaceChildren(h("span",{title:PARTS[vm.part].desc}, PARTS[vm.part].label), h("span",{"aria-hidden":"true"},"\u203a"), h("b",null, vm.label), h("span",{class:"note"}, "(" + (i + 1) + " of " + ORDER.length + " \u00b7 arrow keys to move)"), h("span",{class:"partdesc"}, PARTS[vm.part].desc));
}
function renderSubnav(){
  var t = document.getElementById("subnav");
  t.replaceChildren();
  if (DOMAIN_VIEWS.indexOf(state.view) < 0 || D.length < 1) return;
  t.appendChild(h("span",{class:"lbl"}, M.domain_label || "Journey"));
  D.forEach(function(d, i){
    t.appendChild(h("button",{type:"button",id:"journey-tab-" + i,role:"tab",class:"tab",style:domainStyle(d.color),
      "aria-controls":"journey-panel","aria-selected": i === state.d ? "true" : "false",tabindex:i === state.d ? "0" : "-1",
      onclick:function(){ activateTab("journey-tab-" + i,function(){ state.d = i; if (state.view === "agents") state.agent = null; }); }},
      h("span",{class:"num",style:filled(d.color)}, String(i + 1)), d.name));
  });
}
function pager(){
  var i = ORDER.indexOf(state.view), prev = ORDER[i-1], next = ORDER[i+1];
  return h("div",{class:"pager"},
    prev ? h("button",{type:"button",class:"btn",onclick:function(){ go(prev); }}, "\u2190 " + viewMeta(prev).label) : h("span"),
    next ? h("button",{type:"button",class:"btn primary",onclick:function(){ go(next); }}, viewMeta(next).label + " \u2192") : h("span"));
}

/* ---------------- drawer ---------------- */
var drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim"), lastFocus = null, drawerTimer = null;
var drawerBackground = [];
function canFocus(node){
  if (!node || !node.isConnected || typeof node.focus !== "function" ||
      node.matches(":disabled") || node.closest("[hidden],[inert]") || !node.getClientRects().length) return false;
  var visibility = window.getComputedStyle(node).visibility;
  return visibility !== "hidden" && visibility !== "collapse";
}
function drawerStops(){
  return Array.from(drawer.querySelectorAll("a[href],button,input,select,textarea,summary,[tabindex]")).filter(function(node){
    return node.tabIndex >= 0 && canFocus(node);
  });
}
function hideClosedDrawer(){
  drawerTimer = null;
  if (!drawer.classList.contains("open")) drawer.hidden = true;
}
function openDrawer(title, sub, body){
  clearTimeout(drawerTimer); drawerTimer = null;
  // Replacing a role card or opening its evidence keeps the original page trigger.
  if (!drawer.classList.contains("open")){
    lastFocus = document.activeElement;
    drawerBackground = Array.from(document.querySelectorAll(".page,.rail,.skip")).map(function(node){
      var saved = {node:node, inert:node.inert};
      node.inert = true;
      return saved;
    });
  }
  document.getElementById("drawer-title").textContent = title || "";
  document.getElementById("drawer-sub").textContent = sub || "";
  var b = document.getElementById("drawer-body");
  b.replaceChildren(); add(b, body);
  b.scrollTop = 0;
  drawer.hidden = false; drawer.inert = false; drawer.setAttribute("aria-hidden","false");
  drawer.classList.add("open"); scrim.classList.add("open");
  document.getElementById("drawer-close").focus();
}
function closeDrawer(){
  if (!drawer.classList.contains("open")) return;
  drawer.classList.remove("open"); scrim.classList.remove("open");
  drawer.inert = true;
  drawerBackground.forEach(function(saved){ saved.node.inert = saved.inert; });
  drawerBackground = [];
  if (canFocus(lastFocus)) lastFocus.focus({preventScroll:true});
  if (document.activeElement !== lastFocus) document.getElementById("view").focus({preventScroll:true});
  lastFocus = null;
  drawer.setAttribute("aria-hidden","true");
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) hideClosedDrawer();
  else drawerTimer = setTimeout(hideClosedDrawer, 200);
}
function containDrawerTab(event){
  if (event.key !== "Tab" || !drawer.classList.contains("open")) return false;
  var stops = drawerStops(), first = stops[0], last = stops[stops.length - 1];
  var index = stops.indexOf(document.activeElement);
  if (!first){
    event.preventDefault(); document.getElementById("drawer-close").focus();
  } else if (event.shiftKey && index <= 0){
    event.preventDefault(); last.focus();
  } else if (!event.shiftKey && (index < 0 || document.activeElement === last)){
    event.preventDefault(); first.focus();
  }
  return true;
}
document.getElementById("drawer-close").addEventListener("click", closeDrawer);
scrim.addEventListener("click", closeDrawer);
function activateTab(id, update){
  update();
  render();
  document.getElementById(id).focus();
}
function navigateTabs(event){
  var tab = event.target && event.target.closest ? event.target.closest('[role="tab"]') : null;
  var list = tab && tab.closest('[role="tablist"]');
  if (!list) return false;
  var tabs = Array.from(list.querySelectorAll('[role="tab"]')).filter(function(node){
    return node.closest('[role="tablist"]') === list;
  });
  var index = tabs.indexOf(tab), next = index;
  if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
  else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
  else if (event.key === "Home") next = 0;
  else if (event.key === "End") next = tabs.length - 1;
  else return false;
  event.preventDefault(); event.stopPropagation();
  tabs[next].click();
  return true;
}
document.addEventListener("keydown", function(e){
  if (containDrawerTab(e)) return;
  if (e.key === "Escape" && drawer.classList.contains("open")) { e.preventDefault(); closeDrawer(); return; }
  var tg = e.target && e.target.tagName;
  if (tg === "INPUT" || tg === "TEXTAREA" || tg === "SELECT" || drawer.classList.contains("open")) return;
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  if (navigateTabs(e)) return;
  var i = ORDER.indexOf(state.view);
  if (e.key === "ArrowRight" && ORDER[i+1]) go(ORDER[i+1]);
  if (e.key === "ArrowLeft" && ORDER[i-1]) go(ORDER[i-1]);
});

function openEvidence(id){
  var e = EV[id];
  if (!e){ openDrawer(id, "Evidence", h("p",{class:"tbc"},"This source is not listed in the evidence register.")); return; }
  openDrawer(e.title || id, (EVT[e.type] || e.type || "Source") + (e.date ? " \u00b7 " + e.date : ""), [
    h("dl",{class:"kv"},
      h("dt",null,"ID"), h("dd",null, e.id),
      h("dt",null,"Type"), h("dd",null, EVT[e.type] || e.type || TBC),
      h("dt",null,"Date"), h("dd",null, val(e.date)),
      h("dt",null,"Source"), h("dd",null, val(e.source || e.system)),
      h("dt",null,"Participants"), h("dd",null, val(e.participants)),
      h("dt",null,"Visibility"), h("dd",null, String(e.visibility || "").toLowerCase() === "internal" ? h("span",{class:"pill int"},"Microsoft internal") : h("span",{class:"pill"},"Shareable with the customer")),
      h("dt",null,"Summary"), h("dd",null, val(e.summary)),
      e.quote ? h("dt",null,"Key quote") : null, e.quote ? h("dd",null, h("q",null, e.quote)) : null,
      h("dt",null,"Informs"), h("dd",null, ul(USED[e.id] || [])))
  ]);
}

/* ---------------- agent drawer (role card + role profile) ---------------- */
function agentPills(a){
  var au = autonomyOf(a);
  return h("span",{style:"display:inline-flex;gap:5px;flex-wrap:wrap"},
    h("span",{class:"pill d"}, a.role === "lead" ? "Lead agent" : (a.role === "data" ? "Data agent" : "Specialist agent")),
    a.mvp ? h("span",{class:"pill acc"}, a.mvp === true ? "MVP candidate" : String(a.mvp)) : null,
    idName(a) && a.name && a.name !== idName(a) ? h("span",{class:"pill",title:"Working name in the blueprint"}, a.name) : null,
    au ? h("span",{class:"pill",title:au.meaning}, "Autonomy " + au.n + " \u00b7 " + au.label) : null,
    a.horizon ? h("span",{class:"pill"}, a.horizon) : null,
    statusPill(note("val|agent|" + a.id).status || a.status));
}
function roleCard(a){
  var d = a._d || {};
  var au = autonomyOf(a);
  return h("div",null,
    h("div",{class:"rolecard"},
      h("dl",{class:"kv"},
        idName(a) ? h("dt",null,"Display name") : null, idName(a) ? h("dd",null, idName(a)) : null,
        idNames(a) ? h("dt",null,"Per environment") : null, idNames(a) ? h("dd",null, idNames(a)) : null,
        idName(a) && a.name && a.name !== idName(a) ? [h("dt",null,"Working name"), h("dd",null, a.name)] : null,
        a.identity && a.identity.schema ? [h("dt",null,"Schema name"), h("dd",null, h("code",null, String(a.identity.schema)))] : null,
        h("dt",null,"Department"), h("dd",null, d.name || TBC),
        h("dt",null,"Org role"), h("dd",null, a.role === "lead" ? "Lead agent (orchestrator)" : "Specialist agent"),
        h("dt",null,"Team"), h("dd",null, d.journey_name || d.name || TBC),
        h("dt",null,"Agent boss"), h("dd",null, val(a.owner || (d.orchestrator && d.orchestrator.owner))),
        h("dt",null,"Lifecycle"), h("dd",null, val(a.lifecycle || "Planned")),
        h("dt",null,"Autonomy"), h("dd",null, au ? au.label + " \u2014 " + au.meaning : h("span",{class:"tbc"},TBC)),
        h("dt",null,"Channels"), h("dd",null, logosFor(arr(a.channels || (d.channels && d.channels.people)).join(" "), 18), val(a.channels || (d.channels && d.channels.people))),
        h("dt",null,"Technology"), h("dd",null, logosFor(a.technology, 18), val(a.technology)),
        h("dt",null,"Horizon"), h("dd",null, val(a.horizon))),
      idIcon(a, "avatar idicon") || h("div",{class:"avatar",style:filled(d.color)}, initials(orgLabel(a)))),
    h("div",{class:"small-lbl"},"Responsibility"),
    h("p",{style:"margin:0"}, a.capability || a.mission || TBC, evPills(a.src)),
    h("div",{class:"btnrow"},
      h("button",{type:"button",class:"btn",onclick:function(){ openProfile(a); }}, "Open role profile"),
      a.identity ? h("button",{type:"button",class:"btn",onclick:function(){ openIdentity(a, d); }}, "Agent identity") : null,
      h("button",{type:"button",class:"btn primary",onclick:function(){ closeDrawer(); go("agents",{d:D.indexOf(d), agent:a.id}); }}, "Open agent canvas")));
}
function openAgent(id){
  var a = AG[id]; if (!a) return;
  openDrawer(nameOf(a) + (a.alias && !idName(a) ? " \u00b7 " + a.alias : ""), a.role === "lead" ? (a.mission || "Lead agent") : (a._d ? a._d.name : ""), [agentPills(a), h("div",{style:"height:10px"}), roleCard(a)]);
}
function profileOf(a){
  var p = a.profile || {}, d = a._d || {}, c = a.canvas || {};
  var team = a.role === "lead" ? d.agents.map(function(x){ return nameOf(x); }) : (d.orchestrator ? [nameOf(d.orchestrator)] : []);
  return {
    starting_point: p.starting_point, contribution: p.contribution || a.capability, impact: p.impact || a.outcome,
    mission: p.mission || a.mission || a.capability, trigger: p.trigger || c.trigger || a.trigger, input: p.input || c.data_sources, output: p.output || c.outcome || a.outcome,
    tasks: p.tasks || c.plan, reports_to: p.reports_to || a.owner || (a.role === "lead" ? null : (d.orchestrator ? nameOf(d.orchestrator) : null)), works_with: p.works_with || team, hands_off_to: p.hands_off_to,
    autonomous: p.autonomous, approval: p.approval || c.approval, escalation: p.escalation || (a.declarations && a.declarations.escalation_path),
    knowledge: p.knowledge || (a.declarations && a.declarations.grounding_sources), rules: p.rules, not_allowed: p.not_allowed || (a.declarations && a.declarations.refusal_set),
    systems: p.systems || c.connectors, channels: p.channels || a.channels,
    tone: p.tone, language: p.language,
    kpis: p.kpis || (a.declarations && a.declarations.measurement)
  };
}
function profileSections(a){
  var pr = profileOf(a);
  return PROFILE.map(function(sec, i){
    var filled = sec[1].some(function(f){ return has(pr[f[0]]); });
    return h("details",{class:"acc", open: i < 2 ? true : null},
      h("summary",null, h("span",{class:"n"}, String(i + 1).padStart(2,"0")), sec[0], filled ? null : h("span",{class:"pill open",style:"margin-inline-start:auto"},"To define")),
      h("div",{class:"bd"}, h("dl",{class:"kv"}, sec[1].map(function(f){
        var v = pr[f[0]];
        return [h("dt",null, f[1]), h("dd",null, Array.isArray(v) ? ul(v) : val(v))];
      }))));
  });
}
function openProfile(a){
  openDrawer(nameOf(a) + " \u00b7 role profile", (a._d ? a._d.name + " \u00b7 " : "") + (a.role === "lead" ? "Lead agent" : "Specialist agent"), [
    h("p",{class:"note",style:"margin-top:0"},"The role profile is the agent\u2019s job description: it becomes its versioned instructions and is maintained in the agent record across the lifecycle."),
    profileSections(a),
    h("div",{class:"btnrow"}, h("button",{type:"button",class:"btn",onclick:function(){ openAgent(a.id); }}, "\u2190 Back to role card"))
  ]);
}
function openLeader(L){
  var doms = D.filter(function(d){ return arr(L.accountable_for).indexOf(d.id) >= 0 || d.leader === L.id; });
  openDrawer(L.name || L.role, L.name && L.role ? L.role : "Human-led", [
    h("dl",{class:"kv"},
      h("dt",null,"Role"), h("dd",null, val(L.role)),
      h("dt",null,"Directs"), h("dd",null, val(L.direction)),
      h("dt",null,"Decides"), h("dd",null, val(L.decides)),
      h("dt",null,"Agent boss for"), h("dd",null, doms.length ? ul(doms.map(function(d){ return (d.orchestrator ? nameOf(d.orchestrator) + " \u2014 " : "") + d.name; })) : h("span",{class:"tbc"},TBC))),
    h("p",{class:"note"},"Human-led: people set direction, own every agent, judge the cases policy did not foresee and keep the relationships.")
  ]);
}

/* ---------------- overview ---------------- */
var PHASES = [
  {n:1, label:"Human with assistant", text:"Every employee has an AI assistant that helps them work better and faster."},
  {n:2, label:"Human-agent teams", text:"Agents join teams as digital colleagues and take on specific tasks at a person\u2019s direction."},
  {n:3, label:"Human-led, agent-operated", text:"People set direction; agents run business processes and workflows, checking in as needed."}
];
var LEVELS = [
  {n:1, label:"Traditional automation", text:"Scripts and rules for repetitive, predictable tasks"},
  {n:2, label:"Digital process automation", text:"Workflows orchestrated across systems and teams"},
  {n:3, label:"Agentic", text:"Agents that plan, reason and act toward a business goal"}
];
function ladder(items, cur, tgt, nowLbl, tgtLbl){
  return h("div",{class:"ladder"}, items.map(function(p){
    var cls = "rung" + (p.n === cur ? " now" : "") + (p.n === tgt ? " target" : "");
    return h("div",{class:cls},
      p.n === cur ? h("span",{class:"pill tag"}, nowLbl) : (p.n === tgt ? h("span",{class:"pill acc tag"}, tgtLbl) : null),
      h("div",{class:"n"}, "Phase " + p.n), h("b",null, p.label), h("span",null, p.text));
  }));
}
function renderOverview(){
  var F = BP.frontier || {};
  var nLead = ALL.filter(function(a){ return a.role === "lead"; }).length, nSpec = ALL.length - nLead;
  var nMvp = ALL.filter(function(a){ return a.mvp; }).length + UCS.filter(function(u){ return u.mvp; }).length;
  var stats = [
    [String(D.length), (M.domain_label_plural || "journeys") + " in scope"],
    [String(nLead), "lead agents (orchestrators)"],
    [String(nSpec), "specialist agents"],
    [String(UCS.length), "use cases in the portfolio"],
    [String(arr(BP.evidence).length), "sources behind the hypothesis"],
    [String(nMvp), "MVP candidates"]
  ];
  var mission = BP.mission || {};
  var hero = h("section",{class:"hero"},
    h("div",{class:"mission"},
      h("div",{class:"small-lbl",style:"margin-top:0"}, mission.label || "Mission"),
      h("q",null, mission.statement || TBC),
      h("div",{class:"who"}, mission.attribution || "", evPills(mission.src)),
      mission.prompt ? h("p",{style:"margin:10px 0 0;font-size:12.5px"}, h("b",null,"Discussion \u00b7 "), mission.prompt) : null),
    h("div",{class:"kpis"}, stats.map(function(x){ return h("div",{class:"kpi"}, h("b",null,x[0]), h("span",null,x[1])); })));
  var out = [h("h2",{class:"sec"}, M.overview_title || ("From " + (M.short || M.customer || "today") + " today to a Frontier company")), M.summary ? h("p",{class:"lead"}, M.summary) : null, hero];
  out.push(h("h3",{class:"sub"},"Where the organisation stands on the Frontier journey", evPills(F.src)));
  out.push(ladder(arr(F.phases).length === 3 ? F.phases.map(function(p,i){ return {n:i+1,label:p.label,text:p.text}; }) : PHASES, F.current_phase || 1, F.target_phase || 3, "Today", "Target"));
  if (F.automation_current || F.automation_target){
    out.push(h("div",{class:"small-lbl"},"Process automation level"));
    out.push(ladder(LEVELS, F.automation_current || 2, F.automation_target || 3, "Today", "Target"));
  }
  if (F.note) out.push(h("p",{class:"note"}, F.note));
  if (arr(BP.outcomes).length){
    out.push(h("h3",{class:"sub"},"Business outcomes"));
    out.push(h("section",{class:"outcomes"},
      h("div",null, h("b",{style:"font-size:14px;display:block"},"Why we build it"), h("span",{class:"note"},"Outcomes the hybrid organisation is measured against")),
      BP.outcomes.map(function(o){ return h("div",{class:"o"}, h("b",null,o.name), h("span",null,o.desc), evPills(o.src)); }),
      BP.measured_by ? h("div",{class:"measure"}, h("b",null,"Measured by \u00b7 "), BP.measured_by) : null));
  }
  if (FL){
    out.push(h("h3",{class:"sub", id:"feedback-loop"}, FL.heading || "Digital feedback loop: signals, actions and outcomes", evPills(FL.src)));
    out = out.concat(flSection());
  }
  out.push(h("h3",{class:"sub"}, (M.domain_label_plural ? M.domain_label_plural.charAt(0).toUpperCase() + M.domain_label_plural.slice(1) : "Journeys") + " in scope"));
  out.push(h("div",{class:"dcards"}, D.map(function(d, i){
    var team = d.agents.length + (d.orchestrator ? 1 : 0);
    return h("button",{type:"button",class:"dcard",style:"--d:" + d.color,onclick:function(){ go("blueprint",{d:i}); }},
      h("b",null, d.name), h("div",{class:"j"}, d.journey_name || ""), h("p",null, d.vision || d.journey_tagline || ""),
      h("div",{class:"meta"}, h("span",{class:"pill"}, team + " agents"), arr(d.use_cases).length ? h("span",{class:"pill"}, arr(d.use_cases).length + " use cases") : null,
        d.agents.some(function(a){ return a.mvp; }) ? h("span",{class:"pill acc"},"MVP candidate") : null));
  })));
  out.push(h("h3",{class:"sub"},"How to read this blueprint"));
  out.push(h("div",{class:"panel"}, h("div",{class:"legend"},
    h("span",{class:"it"}, statusPill("hypothesis"), "Microsoft hypothesis, to validate"),
    h("span",{class:"it"}, statusPill("validated"), "Confirmed by the customer"),
    h("span",{class:"it"}, statusPill("adjusted"), "Confirmed with changes"),
    h("span",{class:"it"}, statusPill("rejected"), "Not pursued"),
    h("span",{class:"it"}, h("span",{class:"pill ev"},"E01"), "Evidence: select to see the source"),
    h("span",{class:"it"}, h("span",{class:"pill acc"},"MVP candidate"), "Proposed first build")),
    h("div",{class:"legend",style:"margin-top:8px"}, AUTONOMY.map(function(a){ return h("span",{class:"it"}, h("span",{class:"pill"}, "Autonomy " + a.n), a.label + ": " + a.meaning); }))));
  return out;
}

/* ---------------- digital feedback loop (Overview, 1.5.0) ----------------
   Microsoft's digital feedback loop (engage customers, empower employees, optimize operations,
   transform products) around Microsoft IQ: Work IQ, Fabric IQ, Foundry IQ and Web IQ.
   Data: BP.feedback_loop (canon.py derives it from the journeys; the frontier-blueprint skill tailors it
   from Work IQ context and workshop transcripts). Each area sends signals to Microsoft IQ, receives a
   proposed action that a person approves, and returns a measured outcome as the next signal.
   Animation: SVG SMIL; paused by the user or under prefers-reduced-motion; readable without it. */
var FL = BP.feedback_loop && typeof BP.feedback_loop === "object" && !Array.isArray(BP.feedback_loop) ? BP.feedback_loop : null;
var RM = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
var PILLARS = {
  engage_customers:{label:"Engage customers", signal:"Customer signal", color:"#0F6CBD",
    glyph:'<path d="M3.5 5.5h10v7.5H8.6l-3.1 2.8V13h-2z"/><path d="M15.6 9h4.9v7.5h-2v2.8l-3-2.8h-4.6v-2"/>'},
  optimize_operations:{label:"Optimize operations", signal:"Operational data", color:"#038387",
    glyph:'<circle cx="12" cy="12" r="3.2"/><path d="M12 3.5v2.6M12 17.9v2.6M3.5 12h2.6M17.9 12h2.6M6 6l1.8 1.8M16.2 16.2L18 18M6 18l1.8-1.8M16.2 7.8L18 6"/>'},
  empower_employees:{label:"Empower employees", signal:"Employee signal", color:"#5C2E91",
    glyph:'<circle cx="10" cy="8" r="3.2"/><path d="M3.5 20c.8-3.6 3.3-5.5 6.5-5.5 1.5 0 2.9.4 4 1.3"/><path d="M18 11.5l1 2.3 2.3 1-2.3 1-1 2.3-1-2.3-2.3-1 2.3-1z"/>'},
  transform_products:{label:"Transform products", signal:"Product telemetry", color:"#C239B3",
    glyph:'<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>'}
};
var PILLAR_ORDER = ["engage_customers","optimize_operations","empower_employees","transform_products"];
var IQ_DEF = {
  work:{name:"Work IQ", desc:"Work signals: how people work in Microsoft 365 \u2014 email, meetings, chats, files, people and collaboration patterns",
    glyph:'<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19c.7-3 2.8-4.6 5.5-4.6s4.8 1.6 5.5 4.6"/><path d="M14.5 4.5h6v5h-2.6l-2 1.8V9.5h-1.4z"/>'},
  fabric:{name:"Fabric IQ", desc:"Business data: a shared semantic foundation in Microsoft Fabric \u2014 semantic models, ontology, metrics and live operational signals",
    glyph:'<circle cx="6" cy="6.5" r="2.2"/><circle cx="18" cy="6.5" r="2.2"/><circle cx="12" cy="18" r="2.2"/><circle cx="12" cy="11.5" r="1.7"/><path d="M7.8 7.8l2.8 2.6M16.2 7.8l-2.8 2.6M12 13.2v2.6"/>'},
  foundry:{name:"Foundry IQ", desc:"Organisational knowledge: permission-aware knowledge bases that ground agents in documents and enterprise sources, with citations",
    glyph:'<path d="M4 5.5C4 4.7 4.7 4 5.5 4H11v15H5.5C4.7 19 4 18.3 4 17.5z"/><path d="M20 5.5c0-.8-.7-1.5-1.5-1.5H13v15h5.5c.8 0 1.5-.7 1.5-1.5z"/><path d="M6.5 8h2.5M15 8h2.5M6.5 11h2.5M15 11h2.5"/>'},
  web:{name:"Web IQ", desc:"World knowledge: fresh, citation-ready grounding from the public web \u2014 news, markets and regulation",
    glyph:'<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.4 3.8 5.2 3.8 8.5s-1.2 6.1-3.8 8.5c-2.6-2.4-3.8-5.2-3.8-8.5s1.2-6.1 3.8-8.5z"/>'}
};
var IQ_ORDER = ["work","fabric","foundry","web"];
var GATE_GLYPH = '<path d="M12 3l7 3v5c0 4.5-3 8.2-7 10-4-1.8-7-5.5-7-10V6z"/><path d="M8.8 12.2l2.2 2.2 4.2-4.4"/>';
var FW = 1200, FH = 700, FCX = 600, FCY = 350, FCR = 160, FQW = 340, FQH = 230, FQM = 16, FT = 8;
var FOFF = [0, 2, 6, 4];   /* clockwise: engage customers, optimize operations, transform products, empower employees */

function iqKey(v){ var t = String(v || "").toLowerCase().replace(/[^a-z]/g, "").replace(/iq$/, ""); return IQ_DEF[t] ? t : String(v || ""); }
function flIqList(){
  var given = arr(FL && FL.iq).filter(function(x){ return x && (x.id || x.name); });
  return (given.length ? given : IQ_ORDER.map(function(k){ return {id:k}; })).map(function(x){
    var k = iqKey(x.id || x.name), d = IQ_DEF[k] || {};
    return {id:k, name:x.name || d.name || k, desc:x.desc || d.desc || "", glyph:d.glyph || IQ_DEF.work.glyph, products:x.products || null};
  });
}
function flIqMap(){ var m = {}; flIqList().forEach(function(x){ m[x.id] = x; }); return m; }
function flQuads(){
  var by = {};
  arr(FL && FL.quadrants).forEach(function(q){ if (q && typeof q === "object" && PILLARS[q.pillar] && !by[q.pillar]) by[q.pillar] = q; });
  return PILLAR_ORDER.map(function(p){ return by[p] || null; });
}
function flJourneys(q){ return arr(q && q.journeys).map(domById).filter(Boolean); }
function flColor(q, i){ var j = flJourneys(q)[0]; return j && j.color ? j.color : PILLARS[PILLAR_ORDER[i]].color; }
function flLine(q, kind){
  if (!q) return "";
  if (typeof q[kind] === "string" && q[kind]) return q[kind];
  var x = arr(q[kind + "s"])[0];
  return x ? (typeof x === "string" ? x : (x.short || x.text || x.kpi || "")) : "";
}
function flUsedIq(q){
  var out = [];
  function push(k){ k = iqKey(k); if (k && out.indexOf(k) < 0) out.push(k); }
  arr(q && q.iq).forEach(push);
  arr(q && q.signals).forEach(function(x){ if (x && typeof x === "object") arr(x.iq).forEach(push); });
  return out;
}
function glyphSpan(g, cls){ var sp = document.createElement("span"); sp.className = cls || "flg"; sp.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (g || "") + '</svg>'; return sp; }
function svgGlyph(g, x, y, size, color){ var n = s("svg",{x:x, y:y, width:size, height:size, viewBox:"0 0 24 24", class:"flgl", style:color ? "color:" + color : null, "aria-hidden":"true"}); n.innerHTML = g || ""; return n; }
function bz(P, t){ var u = 1 - t; return [0, 1].map(function(k){ return u * u * u * P[0][k] + 3 * u * u * t * P[1][k] + 3 * u * t * t * P[2][k] + t * t * t * P[3][k]; }); }
function bzAt(P, f){
  var n = 64, pts = [], L = [0], i;
  for (i = 0; i <= n; i++) pts.push(bz(P, i / n));
  for (i = 1; i <= n; i++) L.push(L[i - 1] + Math.sqrt(Math.pow(pts[i][0] - pts[i - 1][0], 2) + Math.pow(pts[i][1] - pts[i - 1][1], 2)));
  var want = f * L[n];
  for (i = 1; i <= n; i++) if (L[i] >= want){ var r = (want - L[i - 1]) / ((L[i] - L[i - 1]) || 1); return [pts[i - 1][0] + r * (pts[i][0] - pts[i - 1][0]), pts[i - 1][1] + r * (pts[i][1] - pts[i - 1][1])]; }
  return pts[n];
}
function pt(p){ return p[0].toFixed(1) + " " + p[1].toFixed(1); }
function bzD(P){ return "M" + pt(P[0]) + " C" + pt(P[1]) + " " + pt(P[2]) + " " + pt(P[3]); }
function flGeo(i){
  var right = i % 2 === 1, bottom = i > 1;
  function P(x, y){ return [right ? FW - x : x, bottom ? FH - y : y]; }
  function C(deg){ var a = deg * Math.PI / 180; return P(FCX + FCR * Math.cos(a), FCY + FCR * Math.sin(a)); }
  return {x: right ? FW - FQM - FQW : FQM, y: bottom ? FH - FQM - FQH : FQM,
    sig:[P(356, 118), P(410, 118), P(425, 238), C(213)],
    act:[C(196), P(405, 292), P(400, 186), P(356, 186)],
    out:[P(230, 246), P(230, 318), P(330, 334), C(186)]};
}
function anim(tag, el, a){ el.appendChild(s(tag, Object.assign({dur:FT + "s", repeatCount:"indefinite"}, a))); return el; }
function flParts(G, off){
  var g = s("g",{class:"flparts"}), sig = bzD(G.sig), act = bzD(G.act), out = bzD(G.out);
  [0, 0.45].forEach(function(dl, k){
    var c = s("circle",{r:k ? 4 : 5.5, class:"fl-p fl-sig", opacity:"0"});
    anim("animateMotion", c, {path:sig, begin:(off + dl) + "s", calcMode:"linear", keyPoints:"0;1;1", keyTimes:"0;0.25;1"});
    anim("animate", c, {attributeName:"opacity", begin:(off + dl) + "s", values:"0;1;1;0;0", keyTimes:"0;0.02;0.24;0.25;1"});
    g.appendChild(c);
  });
  var pk = s("rect",{x:-6, y:-6, width:12, height:12, rx:3, class:"fl-p fl-act", opacity:"0"});
  anim("animateMotion", pk, {path:act, begin:off + "s", calcMode:"linear", keyPoints:"0;0;0.3;0.3;1;1", keyTimes:"0;0.3;0.4;0.52;0.68;1"});
  anim("animate", pk, {attributeName:"opacity", begin:off + "s", values:"0;0;1;1;0;0", keyTimes:"0;0.3;0.31;0.67;0.68;1"});
  g.appendChild(pk);
  var oc = s("circle",{r:5, class:"fl-p fl-out", opacity:"0"});
  anim("animateMotion", oc, {path:out, begin:off + "s", calcMode:"linear", keyPoints:"0;0;1;1", keyTimes:"0;0.72;0.96;1"});
  anim("animate", oc, {attributeName:"opacity", begin:off + "s", values:"0;0;1;1;0;0", keyTimes:"0;0.72;0.73;0.95;0.96;1"});
  g.appendChild(oc);
  return g;
}
function flRing(){
  var g = s("g",{class:"flringg"}), C = (FL && FL.ring) || {};
  g.appendChild(s("ellipse",{cx:FCX, cy:FCY, rx:470, ry:300, class:"flring"}));
  [[FCX, FCY - 300, 0], [FCX + 470, FCY, 90], [FCX, FCY + 300, 180], [FCX - 470, FCY, 270]].forEach(function(c){
    g.appendChild(s("path",{d:"M-5 -6 L3 0 L-5 6", class:"flchev", transform:"translate(" + c[0] + " " + c[1] + ") rotate(" + c[2] + ")"}));
  });
  g.appendChild(s("text",{x:FCX, y:FCY - 312, "text-anchor":"middle", class:"flringt"}, String(C.label || "Digital feedback loop").toUpperCase()));
  g.appendChild(s("text",{x:FCX, y:FCY + 323, "text-anchor":"middle", class:"flringt"}, String(C.caption || "Every measured outcome becomes the next signal").toUpperCase()));
  return g;
}
function flLinks(i, q, sel){
  var G = flGeo(i), g = s("g",{class:"fllinks"}), on = i === sel ? " on" : "";
  if (!q){ g.appendChild(s("path",{d:bzD(G.sig), class:"flpath idle", "data-q":String(i)})); return g; }
  g.appendChild(s("path",{d:bzD(G.sig), class:"flpath sig" + on, "data-q":String(i)}));
  g.appendChild(s("path",{d:bzD(G.act), class:"flpath act" + on, "data-q":String(i)}));
  g.appendChild(s("path",{d:bzD(G.out), class:"flpath out" + on, "data-q":String(i)}));
  function lbl(p, t, cls){
    var w = t.length * 6.6 + 14, l = s("g",{class:"flpl " + cls, transform:"translate(" + pt(p) + ")"});
    l.appendChild(s("rect",{x:-w / 2, y:-8.5, width:w, height:17, rx:8.5}));
    l.appendChild(s("text",{x:0, y:3.5, "text-anchor":"middle"}, t));
    return l;
  }
  g.appendChild(lbl(bz(G.sig, 0.5), "SIGNAL", "sig"));
  g.appendChild(lbl(bzAt(G.act, 0.66), "ACTION", "act"));
  g.appendChild(lbl(bz(G.out, 0.5), "OUTCOME", "out"));
  var gate = s("g",{class:"flgate", transform:"translate(" + pt(bzAt(G.act, 0.3)) + ")"});
  var halo = s("circle",{r:11, class:"flgate-halo", opacity:"0"});
  anim("animate", halo, {attributeName:"opacity", begin:FOFF[i] + "s", values:"0;0;0.9;0.9;0;0", keyTimes:"0;0.4;0.41;0.52;0.53;1"});
  gate.appendChild(halo);
  gate.appendChild(s("rect",{x:-5.5, y:-5.5, width:11, height:11, rx:2, transform:"rotate(45)", class:"flgate-d"}));
  g.appendChild(gate);
  return g;
}
function flCard(i, q, sel){
  var G = flGeo(i), x = G.x, y = G.y, pk = PILLAR_ORDER[i], pl = PILLARS[pk], col = flColor(q, i), js = flJourneys(q);
  var g = s("g",{class:"flq" + (q ? "" : " empty") + (i === sel ? " sel" : ""), "data-q":String(i), role:"button", tabindex:"0", "aria-pressed":i === sel ? "true" : "false",
    "aria-label":pl.label + (q && q.title ? ": " + q.title : "") + ". Show signals, actions and outcomes"});
  g.appendChild(s("rect",{x:x, y:y, width:FQW, height:FQH, rx:12, class:"flcard"}));
  g.appendChild(s("rect",{x:x + 8, y:y + 14, width:4, height:FQH - 28, rx:2, fill:col}));
  g.appendChild(s("rect",{x:x + 22, y:y + 14, width:30, height:30, rx:8, fill:soft(col, DARK ? .3 : .13)}));
  g.appendChild(svgGlyph(pl.glyph, x + 27, y + 19, 20, col));
  g.appendChild(s("text",{x:x + 62, y:y + 27, class:"fleyb"}, pl.label.toUpperCase()));
  var jl = js.length ? js.map(function(d){ return d.short_name || d.name; }).join(" \u00b7 ") : String((q && q.scope) || "");
  if (jl) g.appendChild(s("text",{x:x + 62, y:y + 42, class:"fljr", fill:"var(--ink-2)"}, wrapWords(jl, 40, 1)[0]));
  if (!q){
    g.appendChild(s("text",{x:x + 22, y:y + 82, class:"fltt"}, "To be discovered"));
    wrapWords("No hypothesis yet: ask in the workshop which " + pl.signal.toLowerCase() + " matters most.", 44, 3).forEach(function(t, k){ g.appendChild(s("text",{x:x + 22, y:y + 108 + k * 16, class:"flrt"}, t)); });
    return g;
  }
  wrapWords(q.title || pl.label, 34, 2).forEach(function(t, k){ g.appendChild(s("text",{x:x + 22, y:y + 70 + k * 18, class:"fltt"}, t)); });
  g.appendChild(s("line",{x1:x + 22, y1:y + 100, x2:x + FQW - 14, y2:y + 100, class:"fldiv"}));
  [["sig","SIGNAL","signal"],["act","ACTION","action"],["out","OUTCOME","outcome"]].forEach(function(r, k){
    var yy = y + 120 + k * 38;
    g.appendChild(s("text",{x:x + 22, y:yy, class:"flrl " + r[0]}, r[1]));
    wrapWords(flLine(q, r[2]) || TBC, 38, 2).forEach(function(t, m){ g.appendChild(s("text",{x:x + 96, y:yy + m * 14, class:"flrt"}, t)); });
  });
  return g;
}
function flCore(sel){
  var g = s("g",{class:"flcorewrap"}), C = (FL && FL.center) || {}, used = flUsedIq(flQuads()[sel]);
  g.appendChild(s("defs",null, s("clipPath",{id:"fl-clip"}, s("circle",{cx:FCX, cy:FCY, r:FCR - 1.5}))));
  g.appendChild(s("circle",{cx:FCX, cy:FCY, r:FCR + 3, class:"flpulse"}));
  g.appendChild(s("circle",{cx:FCX, cy:FCY, r:FCR, class:"flcore"}));
  g.appendChild(s("text",{x:FCX, y:FCY - 90, "text-anchor":"middle", class:"fliqt"}, C.name || "Microsoft IQ"));
  g.appendChild(s("text",{x:FCX, y:FCY - 69, "text-anchor":"middle", class:"fliqs"}, C.tagline || "Enterprise intelligence layer"));
  flIqList().slice(0, 4).forEach(function(x, k){
    var cx = FCX - 128 + (k % 2) * 132, cy = FCY - 54 + Math.floor(k / 2) * 38;
    var c = s("g",{class:"flchip" + (used.length && used.indexOf(x.id) < 0 ? " off" : ""), "data-iq":x.id});
    c.appendChild(s("title",null, x.name + (x.desc ? ": " + x.desc : "")));
    c.appendChild(s("rect",{x:cx, y:cy, width:124, height:30, rx:15}));
    c.appendChild(svgGlyph(x.glyph, cx + 11, cy + 7, 16, "#FFFFFF"));
    c.appendChild(s("text",{x:cx + 33, y:cy + 19.5}, x.name));
    g.appendChild(c);
  });
  g.appendChild(s("rect",{x:FCX - FCR, y:FCY + 28, width:FCR * 2, height:52, "clip-path":"url(#fl-clip)", class:"flappr"}));
  var ap = wrapWords((FL && FL.approval) || "Human approval before every action", 20, 2);
  ap.forEach(function(t, k){ g.appendChild(s("text",{x:FCX, y:FCY + (ap.length > 1 ? 50 : 58) + k * 16, "text-anchor":"middle", class:"flapprt"}, t)); });
  var tr = arr(FL && FL.trust).map(function(t){ return typeof t === "string" ? {name:t} : t; }).filter(function(t){ return t && t.name; });
  var lg = tr.map(function(t){ var L = LOGO[t.logo]; return L && IMG_OK.test(L.uri || "") ? L : null; }).filter(Boolean);
  lg.forEach(function(L, k){ g.appendChild(s("image",{href:L.uri, x:FCX - lg.length * 13 + 4 + k * 26, y:FCY + 88, width:18, height:18})); });
  if (tr.length) g.appendChild(s("text",{x:FCX, y:FCY + 123, "text-anchor":"middle", class:"fltrust"}, tr.map(function(t){ return String(t.short || t.name).replace(/^Microsoft /, ""); }).join(" \u00b7 ")));
  return g;
}
function flSvg(sel){
  var Q = flQuads();
  var svg = s("svg",{viewBox:"0 0 " + FW + " " + FH, class:"flsvg", role:"group", "aria-label":"Digital feedback loop: " + PILLAR_ORDER.map(function(p){ return PILLARS[p].label; }).join(", ") + ", around Microsoft IQ"});
  svg.appendChild(s("title",null, "Digital feedback loop with Microsoft IQ"));
  var deco = s("g",{"aria-hidden":"true"});
  deco.appendChild(flRing());
  Q.forEach(function(q, i){ deco.appendChild(flLinks(i, q, sel)); });
  var parts = s("g",{class:"flanim"});
  Q.forEach(function(q, i){ if (q) parts.appendChild(flParts(flGeo(i), FOFF[i])); });
  deco.appendChild(parts);
  svg.appendChild(deco);
  Q.forEach(function(q, i){
    var c = flCard(i, q, sel);
    c.addEventListener("click", function(){ flSelect(i); });
    c.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " "){ e.preventDefault(); flSelect(i); } });
    svg.appendChild(c);
  });
  var core = flCore(sel); core.setAttribute("aria-hidden", "true");
  svg.appendChild(core);
  return svg;
}
function flSelect(i){
  state.flq = i;
  var w = document.getElementById("flwrap"); if (!w) return;
  var used = flUsedIq(flQuads()[i]);
  Array.prototype.forEach.call(w.querySelectorAll(".flq"), function(g){ var on = +g.getAttribute("data-q") === i; g.classList.toggle("sel", on); g.setAttribute("aria-pressed", on ? "true" : "false"); });
  Array.prototype.forEach.call(w.querySelectorAll(".flpath"), function(p){ p.classList.toggle("on", +p.getAttribute("data-q") === i); });
  Array.prototype.forEach.call(w.querySelectorAll(".flchip"), function(c){ c.classList.toggle("off", used.length > 0 && used.indexOf(c.getAttribute("data-iq")) < 0); });
  var p = document.getElementById("flpanel"); if (p) p.replaceWith(flPanel(i));
}
function flApply(wrap, paused){
  wrap.classList.toggle("paused", paused);
  var svg = wrap.querySelector("svg.flsvg");
  if (svg && typeof svg.pauseAnimations === "function"){ try { if (paused) svg.pauseAnimations(); else svg.unpauseAnimations(); } catch (e) {} }
}
function flIqPill(k){ var x = flIqMap()[iqKey(k)] || IQ_DEF[iqKey(k)] || {name:String(k)}; return h("span",{class:"pill iqp", title:x.desc || null}, glyphSpan(x.glyph, "flg"), x.name); }
function flSig(x){
  if (typeof x === "string") x = {text:x};
  if (!x || typeof x !== "object") return null;
  return h("li",null, h("span",null, x.text || ""), h("span",{class:"flmeta"}, arr(x.iq).map(flIqPill), x.type ? h("span",{class:"pill"}, x.type) : null, evPills(x.src)));
}
function flAct(x){
  if (typeof x === "string") x = {text:x};
  if (!x || typeof x !== "object") return null;
  var ags = arr(x.agents).map(function(id){ return AG[id] || agentByName(id); }).filter(Boolean);
  return h("li",null, h("span",null, x.text || ""),
    ags.length ? h("span",{class:"flags"}, ags.map(function(a){ return agentChip(a, true); })) : null,
    x.approval ? h("div",{class:"flok"}, glyphSpan(GATE_GLYPH, "flg"), h("span",null, h("b",null,"Human approval \u00b7 "), x.approval)) : null,
    evPills(x.src));
}
function flKpi(x, q){
  if (!x.kpi) return null;
  var ids = (x.journey ? [x.journey] : []).concat(arr(q.journeys)), want = String(x.kpi).toLowerCase();
  for (var i = 0; i < ids.length; i++){
    var d = domById(ids[i]); if (!d) continue;
    var m = arr(d.kpis).filter(function(k){ return k && String(k.kpi || "").toLowerCase() === want; })[0];
    if (m) return m;
  }
  return {kpi:x.kpi, baseline:x.baseline, target:x.target};
}
function flOut(x, q){
  if (typeof x === "string") x = {text:x};
  if (!x || typeof x !== "object") return null;
  var k = flKpi(x, q);
  return h("li",null, h("span",null, x.text || (k && k.kpi) || ""),
    k ? h("div",{class:"flkpi"}, h("b",null, k.kpi), (k.baseline || k.target) ? [" \u00b7 ", k.baseline || TBC, " \u2192 ", h("b",null, k.target || TBC)] : null, evPills(k.src)) : null,
    arr(x.assumptions).length ? h("div",{class:"flass"}, h("span",{class:"note"},"Value hypotheses to confirm in the workshop"), arr(x.assumptions).map(function(id){
      var a = ASSM[id], shown = a && presentedAssumption(a);
      return a ? h("span",{class:"flassi", title:shown.question || null}, h("b",null, id), " ", shown.statement || "", " \u00b7 ",
        assumptionWithheld(a) ? withheldAssumptionValue() : fmtA(shown.base, shown.unit), " ", assPill(a), evPills(shown.src)) : h("span",{class:"pill"}, id);
    })) : null,
    evPills(x.src));
}
function flCol(cls, title, sub, items){
  items = items.filter(Boolean);
  return h("div",{class:"flcol " + cls}, h("h4",null, title), h("span",{class:"note"}, sub), items.length ? h("ul",null, items) : h("p",{class:"tbc"}, TBC));
}
function flPanel(i){
  var Q = flQuads(), q = Q[i], pk = PILLAR_ORDER[i], pl = PILLARS[pk], col = flColor(q, i);
  var head = h("div",{class:"flph"},
    h("span",{class:"flpic", style:"background:" + soft(col, DARK ? .3 : .13) + ";color:" + col}, glyphSpan(pl.glyph, "flg")),
    h("div",null, h("div",{class:"small-lbl",style:"margin:0"}, pl.label + " \u00b7 " + ((q && q.signal_type) || pl.signal)), h("h3",null, (q && q.title) || pl.label)),
    q ? h("span",{class:"flps"}, statusPill(note("val|loop|" + pk).status || q.status || "hypothesis"), evPills(q.src)) : null);
  if (!q) return h("div",{class:"flpanel", id:"flpanel", style:"--q:" + col}, head,
    h("p",{class:"note"}, "No hypothesis for this area yet. Ask in the workshop which " + pl.signal.toLowerCase() + " matters most, what should happen with it and how the result would be measured."), valBox("loop", pk));
  var js = flJourneys(q), ucs = arr(q.use_cases).map(ucById).filter(Boolean);
  var lbl = M.domain_label_plural ? M.domain_label_plural.charAt(0).toUpperCase() + M.domain_label_plural.slice(1) : "Journeys";
  return h("div",{class:"flpanel", id:"flpanel", style:"--q:" + col},
    head,
    q.summary ? h("p",{class:"flsum"}, q.summary) : null,
    h("div",{class:"flcols"},
      flCol("sig", "Signals", "What is observed, and through which Microsoft IQ layer", arr(q.signals).map(flSig)),
      flCol("act", "Actions", "What agents propose; a person approves", arr(q.actions).map(flAct)),
      flCol("out", "Outcomes", "What is measured and fed back as the next signal", arr(q.outcomes).map(function(x){ return flOut(x, q); }))),
    (js.length || ucs.length) ? h("div",{class:"flfoot"},
      js.length ? h("span",null, h("b",null, lbl + " \u00b7 "), js.map(function(d){ return h("button",{type:"button", class:"fllink", style:"--d:" + d.color, onclick:function(){ go("blueprint",{d:D.indexOf(d)}); }}, d.name); })) : null,
      ucs.length ? h("span",null, h("b",null,"Use cases \u00b7 "), ucs.map(function(u){ return h("button",{type:"button", class:"fllink", onclick:function(){ state.uc = u.id; go("usecases"); }}, u.id + " \u00b7 " + (u.name || "")); })) : null) : null,
    q.question ? h("p",{class:"flqq"}, h("b",null,"Workshop question \u00b7 "), q.question) : null,
    valBox("loop", pk));
}
function flSection(){
  if (!FL) return [];
  var Q = flQuads(), sel = state.flq;
  if (typeof sel !== "number" || !Q[sel]){ sel = Q.findIndex(function(q){ return !!q; }); if (sel < 0) sel = 0; }
  state.flq = sel;
  var still = RM && !state.flPlay, paused = still || !!state.flPause;
  var btn = h("button",{type:"button", class:"btn flbtn"}, paused ? "\u25b6 Play animation" : "\u275a\u275a Pause animation");
  var steps = arr(FL.flow).length === 5 ? FL.flow : ["Signal","Microsoft IQ","Proposed action","Human approval","Measured outcome"];
  var kinds = ["sig","iq","act","ok","out"];
  var wrap = h("div",{class:"flwrap" + (paused ? " paused" : "") + (still ? " still" : ""), id:"flwrap"},
    h("div",{class:"flfig"}, flSvg(sel)),
    h("div",{class:"flctl"}, btn,
      h("div",{class:"flflow", role:"list", "aria-label":"Reading the loop"}, steps.map(function(t, k){
        return [k ? h("span",{class:"ar", "aria-hidden":"true"}, "\u2192") : null, h("span",{class:"st", role:"listitem"}, h("i",{class:kinds[k]}), String(t))];
      }))),
    h("p",{class:"note flanote"}, h("b",null,"Animation \u00b7 "), FL.animation_note || "Cyan dots are incoming signals; the green packet is a proposed action that waits at the amber gate for human approval; the amber dot returns the measured outcome to Microsoft IQ as the next signal. Motion stops when you pause it or when your device asks for reduced motion."));
  btn.addEventListener("click", function(){
    var nowPaused = !wrap.classList.contains("paused");
    if (!nowPaused){ state.flPlay = true; wrap.classList.remove("still"); }
    state.flPause = nowPaused;
    flApply(wrap, nowPaused);
    btn.textContent = nowPaused ? "\u25b6 Play animation" : "\u275a\u275a Pause animation";
  });
  setTimeout(function(){ if (wrap.isConnected !== false) flApply(wrap, paused); }, 0);
  var srcs = arr(FL.sources).filter(function(x){ return x && /^https:\/\//.test(String(x.url || "")); });
  return [
    h("p",{class:"lead"}, FL.intro || ("Every area sends signals to Microsoft IQ, receives a proposed action back and returns a measured outcome, which becomes the next signal. A person approves before any action leaves " + (M.short || "the company") + ".")),
    wrap,
    h("div",{class:"fliqrow"}, flIqList().map(function(x){
      var pr = arr(x.products);
      return h("div",{class:"fliq"}, glyphSpan(x.glyph, "flg"), h("div",null, h("b",null, x.name), h("span",null, x.desc),
        pr.length ? h("div",{class:"flprod"}, logosFor(pr.join(" "), 16, 3), pr.join(" \u00b7 ")) : null));
    })),
    flPanel(sel),
    FL.note ? h("p",{class:"note"}, FL.note) : null,
    srcs.length ? h("p",{class:"flsrc"}, "Microsoft sources: ", srcs.map(function(x, k){ return [k ? " \u00b7 " : null, h("a",{href:x.url, target:"_blank", rel:"noopener noreferrer"}, x.title || x.url)]; })) : null
  ];
}

/* ---------------- agent workflow (Agents > trigger canvas, 1.6.0) ----------------
   The canvas plan drawn the way the Copilot Studio workflow designer (GitHub Copilot harness) shows a workflow:
   one trigger, typed steps (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable,
   If/Else, Loop, Scope, Note, Respond to the agent) and the desired outcome. Data: agent.canvas.workflow,
   authored or derived from the plan by workflow.py. Dark designer canvas, the Add panel as legend, a
   properties panel for the selected node, zoom controls. */
var WFT = {
  agent:{label:"Agent", kind:"ai", color:"#8B8CF6", desc:"Hands an open-ended task to an agent (a published agent or one defined inline in the node) and reads its answer back.",
    glyph:'<rect x="5" y="7" width="14" height="11" rx="3"/><path d="M12 7V4"/><circle cx="9.5" cy="12.5" r="1.1"/><circle cx="14.5" cy="12.5" r="1.1"/><path d="M2.5 11.5v3M21.5 11.5v3"/>'},
  classify:{label:"Classify", kind:"ai", color:"#5B9BFF", desc:"Routes free-form text to a branch by its meaning: one branch per category, plus Other.",
    glyph:'<path d="M3.5 12.6V5A1.5 1.5 0 0 1 5 3.5h7.6l8 8-9.1 9.1z"/><circle cx="8" cy="8" r="1.6"/>'},
  extract:{label:"Extract", kind:"ai", color:"#6CB6FF", desc:"Reads documents and returns the values and tables you define, for the next steps to use.",
    glyph:'<path d="M13 3H6.5A1.5 1.5 0 0 0 5 4.5v15A1.5 1.5 0 0 0 6.5 21H11"/><path d="M13 3l5 5h-5z"/><circle cx="15.5" cy="15.5" r="3"/><path d="M17.7 17.7L21 21"/>'},
  copilot:{label:"Copilot", kind:"ai", color:"#4FA3FF", desc:"Calls Microsoft Copilot, Cowork or agents such as Researcher and Analyst for a step.",
    glyph:'<rect x="3.5" y="8" width="9" height="9" rx="3"/><rect x="11.5" y="7" width="9" height="9" rx="3"/><path d="M9 4.5h5M10 19.5h5"/>'},
  human_review:{label:"Human review", kind:"human", color:"#C4A5FF", desc:"Pauses the workflow until a person approves, decides or fills in what is missing.",
    glyph:'<circle cx="10" cy="7.5" r="3.5"/><path d="M3.5 20c.8-3.8 3.4-5.8 6.5-5.8 1.4 0 2.7.4 3.8 1.2"/><path d="M14.5 18l2.2 2.2 4.3-4.7"/>'},
  connector:{label:"Connector", kind:"rule", color:"#E07BEA", desc:"Runs an action in a connected service: Microsoft 365, business systems, third-party or custom connectors.",
    glyph:'<path d="M9 3v4M15 3v4"/><path d="M6.5 7h11v3.5a5.5 5.5 0 0 1-11 0z"/><path d="M12 16v5"/>'},
  "function":{label:"Function", kind:"rule", color:"#4FD1C5", desc:"Small deterministic transforms of text, numbers and lists.",
    glyph:'<path d="M14 4.5c-2 0-3 1-3.4 3L8.8 17c-.4 2-1.4 2.8-3.3 2.8"/><path d="M7.5 10h6"/><path d="M15 12.5l5 6.5M20 12.5l-5 6.5"/>'},
  variable:{label:"Variable", kind:"rule", color:"#6CB6FF", desc:"Keeps a value to use further down the workflow.",
    glyph:'<path d="M8 4C6 4 5.5 5 5.5 7v2.2c0 1.3-.8 2.3-2 2.8 1.2.5 2 1.5 2 2.8V17c0 2 .5 3 2.5 3"/><path d="M16 4c2 0 2.5 1 2.5 3v2.2c0 1.3.8 2.3 2 2.8-1.2.5-2 1.5-2 2.8V17c0 2-.5 3-2.5 3"/><path d="M10 9.5l4 5M14 9.5l-4 5"/>'},
  if_else:{label:"If/Else", kind:"rule", color:"#F6A05B", desc:"Splits the workflow on a condition.",
    glyph:'<path d="M12 21v-7.5"/><path d="M12 13.5L6.5 8M12 13.5L17.5 8"/><path d="M5 3.5v5h5M19 3.5v5h-5"/>'},
  loop:{label:"Loop", kind:"rule", color:"#F6A05B", desc:"Repeats its steps for every item of a list, or until a condition is met.",
    glyph:'<path d="M20 12a8 8 0 0 1-13.6 5.7"/><path d="M4 12a8 8 0 0 1 13.6-5.7"/><path d="M18 2.8v3.6h-3.6M6 21.2v-3.6h3.6"/>'},
  scope:{label:"Scope", kind:"rule", color:"#A0A7B4", desc:"Groups steps so they succeed or fail together.",
    glyph:'<path d="M8 4H5.5A1.5 1.5 0 0 0 4 5.5v13A1.5 1.5 0 0 0 5.5 20H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5H16"/>'},
  note:{label:"Note", kind:"note", color:"#4ADE80", desc:"A note on the canvas for the people who build and review the workflow.",
    glyph:'<path d="M5 4h14v10l-5.5 6H5z"/><path d="M13.5 20v-6H19"/>'},
  respond:{label:"Respond to the agent", kind:"rule", color:"#8B8CF6", desc:"Returns the workflow's answer to the agent that called it.",
    glyph:'<path d="M9.5 6.5L4 12l5.5 5.5"/><path d="M4 12h10a6 6 0 0 1 6 6v1.5"/>'}
};
var WF_ADD = ["agent","classify","extract","copilot","human_review","connector","function","variable","if_else","loop","note"];
var WF_TRIG = {
  manual:{label:"Manual", desc:"Run this workflow on demand with a button click."},
  recurrence:{label:"Recurrence", desc:"Runs on a schedule, for example every night or at month-end."},
  connector:{label:"Connector event", desc:"Starts when a connected system raises an event, for example a new email or a changed record."},
  http:{label:"When an HTTP request is received", desc:"Starts when another system calls the workflow's address."},
  agent:{label:"When an agent calls the workflow", desc:"An agent calls the workflow as a tool; the workflow responds to the agent with its result."}
};
var WF_KIND = {ai:["AI step","results can vary"], rule:["Deterministic step","same input, same result"], human:["Human step","a person decides"], note:["Note",""]};
var WF_GLYPH = {
  trigger:'<path d="M13.5 2.5L5 13.5h6.2l-1.2 8 8.5-11h-6.3z"/>',
  outcome:'<path d="M5.5 21V3.5"/><path d="M5.5 4h11.5l-2.2 4.2 2.2 4.3H5.5"/>',
  end:'<rect x="6" y="6" width="12" height="12" rx="2.5"/>'
};
var WFL = {W:196, H:60, G:40, P:28, TOP:118, LANE:118, PH:28, PG:7, OW:250, EW:152, WRAP:960};

function wfT(s){ return s && WFT[s.type] ? s.type : "agent"; }
function wfOf(a){ var w = a && a.canvas && a.canvas.workflow; return w && typeof w === "object" && !Array.isArray(w) && arr(w.steps).length ? w : null; }
function wfAgent(ref){ return ref ? (AG[ref] || agentByName(ref)) : null; }
function wfLogoKey(text){
  var t = String(text || "");
  for (var i = 0; i < LOGO_RULES.length; i++){ var k = LOGO_RULES[i][1]; if (LOGO_RULES[i][0].test(t) && LOGO[k] && IMG_OK.test(LOGO[k].uri || "")) return k; }
  return null;
}
function wfPills(s){
  var t = wfT(s), b = arr(s.branches).filter(function(x){ return x && x.label; }), d = arr(s.defaults).map(String);
  if (["if_else","classify","human_review"].indexOf(t) < 0 || (!b.length && !d.length)) return null;
  if (!d.length) d = [t === "classify" ? "Other" : (t === "human_review" ? "Approved" : "Else")];
  return {branches:b, defaults:d};
}
function wfHead(s){ return wrapWords(String(s.label || ""), 21, 2); }
function wfHeight(s){ var p = wfPills(s); return p ? 22 + wfHead(s).length * 16 + (p.branches.length + p.defaults.length) * (WFL.PH + WFL.PG) + 4 : WFL.H; }
function wfPath(a, b){ var dx = Math.max(26, Math.abs(b[0] - a[0]) / 2); return "M" + a[0].toFixed(1) + " " + a[1].toFixed(1) + " C" + (a[0] + dx).toFixed(1) + " " + a[1].toFixed(1) + " " + (b[0] - dx).toFixed(1) + " " + b[1].toFixed(1) + " " + b[0].toFixed(1) + " " + b[1].toFixed(1); }

/* layout: the main path left to right; loops and scopes as containers; branches on lanes below that rejoin or end.
   wrap > 0 folds the path into rows of at most that width (an overview); 0 keeps one row as in the designer. */
function wfLayout(wf, wrap){
  var L = WFL, nodes = [], edges = [], boxes = [], notes = [], byId = {}, seq = 0, lanes = [], items = [];
  var main = arr(wf.steps).filter(function(s){ return s && typeof s === "object"; });
  var y0 = L.TOP, mainH = L.H;
  main.forEach(function(s){ var t = wfT(s); mainH = Math.max(mainH, t === "loop" || t === "scope" ? L.H + 44 : wfHeight(s)); });
  var laneTop = y0 + mainH + 54, cur = null;
  function put(kind, s, x, y, w, h){
    var o = {kind:kind, s:s, type: kind === "node" ? wfT(s) : kind, x:x, y:y, w:w, h:h};
    o.id = kind === "trigger" || kind === "outcome" ? kind : String(s.id || ("w" + (++seq)));
    if (byId[o.id]) o.id += "-" + (++seq);
    o.inP = [x, y + h / 2]; o.outP = [x + w, y + h / 2];
    nodes.push(o); byId[o.id] = o; if (cur) cur.ids.push(o.id);
    return o;
  }
  function P(p, n){ return {p:p, n:n.id}; }
  function link(froms, to, cls){ froms.forEach(function(f){ edges.push({a:f.p, na:f.n, b:to.inP, nb:to.id, cls:cls || ""}); }); }
  function lane(x1, x2){
    for (var i = 0; i < lanes.length; i++) if (lanes[i] < x1 - 24){ lanes[i] = x2; return i; }
    lanes.push(x2); return lanes.length - 1;
  }
  function item(x){ cur = {x0:x, ids:[]}; items.push(cur); return cur; }
  item(L.P);
  var trig = put("trigger", wf.trigger || {}, L.P, y0, L.W, L.H), pend = [P(trig.outP, trig)], x = L.P + L.W + L.G, last = trig;
  cur.x1 = L.P + L.W;
  main.forEach(function(s){
    var t = wfT(s);
    if (t === "note"){ notes.push({x:last.x + 12, y:y0 - 104, text:String(s.label || s.detail || ""), at:last.id}); return; }
    var it = item(x);
    if (t === "loop" || t === "scope"){
      var box = {kind:"box", s:s, type:t, x:x, y:y0 - 40, w:0, h:L.H + 56, id:String(s.id || ("w" + (++seq)))};
      if (byId[box.id]) box.id += "-" + (++seq);
      boxes.push(box); byId[box.id] = box; nodes.push(box); it.ids.push(box.id);
      var body = arr(s.steps).filter(function(b){ return b && typeof b === "object" && wfT(b) !== "note"; });
      var bx = x + 16, inner = [];
      body.forEach(function(b){ var bn = put("node", b, bx, y0 + 4, L.W, L.H); inner.push(bn); bx += L.W + 32; });
      var w = Math.max(L.W + 32, bx - 32 + 16 - x);
      box.w = w; box.inP = [x, y0 + 4 + L.H / 2]; box.outP = [x + w, y0 + 4 + L.H / 2];
      link(pend, box);
      for (var i = 1; i < inner.length; i++) edges.push({a:inner[i - 1].outP, na:inner[i - 1].id, b:inner[i].inP, nb:inner[i].id, cls:""});
      if (inner.length){ edges.push({a:box.inP, na:box.id, b:inner[0].inP, nb:inner[0].id, cls:"in"}); edges.push({a:inner[inner.length - 1].outP, na:inner[inner.length - 1].id, b:box.outP, nb:box.id, cls:"in"}); }
      pend = [P(box.outP, box)]; last = box; it.x1 = x + w; x += w + L.G; return;
    }
    var nd = put("node", s, x, y0, L.W, wfHeight(s)), p = wfPills(s), next = x + L.W + L.G;
    link(pend, nd);
    if (s.note) notes.push({x:nd.x + 12, y:y0 - 104, text:String(s.note), at:nd.id});
    if (!p){ pend = [P(nd.outP, nd)]; last = nd; it.x1 = x + L.W; x = next; return; }
    var hy = nd.y + 22 + wfHead(s).length * 16, k = 0, outs = [], span = next;
    nd.pills = [];
    p.branches.concat(p.defaults.map(function(lb){ return {label:lb, _default:true}; })).forEach(function(b){
      var py = hy + k * (L.PH + L.PG) + L.PH / 2; k++;
      var pill = {label:String(b.label), y:py, port:[nd.x + nd.w, py], def: !!b._default};
      nd.pills.push(pill);
      var steps = b._default ? [] : arr(b.steps).filter(function(z){ return z && typeof z === "object"; });
      var ends = !b._default && (b.then === "end" || (!!b.end && b.then !== "continue"));
      if (!steps.length && !ends){ outs.push(P(pill.port, nd)); return; }
      var w = steps.length * (L.W + L.G) + (ends ? L.EW + L.G : 0), bx = nd.x + nd.w + L.G;
      var ln = lane(bx, bx + w), ly = laneTop + ln * L.LANE, prev = [P(pill.port, nd)];
      steps.forEach(function(z){ var bn = put("node", z, bx, ly, L.W, L.H); link(prev, bn, "br"); prev = [P(bn.outP, bn)]; bx += L.W + L.G; });
      if (ends){ var en = put("end", {label: b.end || "End", id:(s.id || "x") + "-end-" + k}, bx, ly + (L.H - 44) / 2, L.EW, 44); link(prev, en, "br"); bx += L.EW + L.G; }
      else { outs.push(prev[0]); next = Math.max(next, bx); }
      span = Math.max(span, bx);
    });
    pend = outs; last = nd; it.x1 = Math.max(next, span) - L.G; x = next;
  });
  item(x);
  var oc = put("outcome", {label:"Desired outcome", detail: wf.outcome || ""}, x, y0 - 16, L.OW, L.H + 32);
  cur.x1 = x + L.OW;
  link(pend, oc, "fin");
  var res = {nodes:nodes, edges:edges, boxes:boxes, notes:notes, byId:byId, items:items, w:x + L.OW + L.P, rows:1};
  wfFold(res, wrap);
  var top = Infinity, bottom = 0;
  nodes.forEach(function(n){ top = Math.min(top, n.y); bottom = Math.max(bottom, n.y + n.h); });
  notes.forEach(function(nt){ top = Math.min(top, nt.y); });
  var lift = Math.max(0, top - 18);
  if (lift){
    nodes.forEach(function(n){ n.y -= lift; n.inP = [n.inP[0], n.inP[1] - lift]; n.outP = [n.outP[0], n.outP[1] - lift]; arr(n.pills).forEach(function(p){ p.y -= lift; p.port = [p.port[0], p.port[1] - lift]; }); });
    edges.forEach(function(e){ e.a = [e.a[0], e.a[1] - lift]; e.b = [e.b[0], e.b[1] - lift]; if (e.wrapY) e.wrapY -= lift; });
    notes.forEach(function(nt){ nt.y -= lift; });
    bottom -= lift;
  }
  res.h = bottom + L.P + 6;
  return res;
}
/* fold one long row into rows; edges between rows run below the row and enter the next row from the left */
function wfFold(L, wrap){
  var segs = [], cur = null;
  L.items.forEach(function(it){
    if (!cur || (wrap > 0 && it.x1 - cur.x0 > wrap && cur.items.length)){ cur = {x0:it.x0, items:[]}; segs.push(cur); }
    cur.items.push(it);
  });
  var seg = {}, off = {}, maxW = 0, prevBottom = 0, noteAt = {};
  L.notes.forEach(function(nt){ noteAt[nt.at] = true; });
  segs.forEach(function(sg, si){
    var ids = [], hasNote = false, hasBox = false;
    sg.items.forEach(function(it){ ids = ids.concat(it.ids); });
    ids.forEach(function(id){ if (noteAt[id]) hasNote = true; if (L.byId[id].kind === "box") hasBox = true; });
    var room = hasNote ? 112 : (hasBox ? 52 : 26);
    var dx = WFL.P - sg.x0, dy = si === 0 ? 0 : prevBottom + 34 + room - WFL.TOP, bot = 0, right = 0;
    ids.forEach(function(id){ seg[id] = si; off[id] = [dx, dy]; var n = L.byId[id]; bot = Math.max(bot, n.y + n.h + dy); right = Math.max(right, n.x + n.w + dx); });
    sg.bottom = bot; maxW = Math.max(maxW, right + WFL.P); prevBottom = bot;
  });
  L.rows = segs.length;
  if (segs.length < 2) return;
  function mv(p, id){ var o = off[id] || [0, 0]; return [p[0] + o[0], p[1] + o[1]]; }
  L.nodes.forEach(function(n){
    var o = off[n.id] || [0, 0]; n.x += o[0]; n.y += o[1]; n.inP = mv(n.inP, n.id); n.outP = mv(n.outP, n.id);
    arr(n.pills).forEach(function(p){ p.y += o[1]; p.port = [p.port[0] + o[0], p.port[1] + o[1]]; });
  });
  L.edges.forEach(function(e){
    e.a = mv(e.a, e.na); e.b = mv(e.b, e.nb);
    if (seg[e.na] !== seg[e.nb]) e.wrapY = segs[seg[e.na]].bottom + 22;
  });
  L.notes.forEach(function(nt){ var o = off[nt.at] || [0, 0]; nt.x += o[0]; nt.y += o[1]; });
  L.w = maxW;
  var top = Infinity; L.nodes.forEach(function(n){ top = Math.min(top, n.y); }); L.notes.forEach(function(nt){ top = Math.min(top, nt.y); });
  L.top = top;
}
function wfWrapPath(a, b, yg){
  var r = 10, x1 = a[0] + 18, x2 = b[0] - 20;
  return "M" + a[0] + " " + a[1] + " H" + (x1 - r) + " Q" + x1 + " " + a[1] + " " + x1 + " " + (a[1] + r) + " V" + (yg - r) + " Q" + x1 + " " + yg + " " + (x1 - r) + " " + yg +
    " H" + (x2 + r) + " Q" + x2 + " " + yg + " " + x2 + " " + (yg + r) + " V" + (b[1] - r) + " Q" + x2 + " " + b[1] + " " + (x2 + r) + " " + b[1] + " H" + b[0];
}
function wfIcon(n, x, y, size){
  var st = n.s || {}, t = n.type, k = null, a = null;
  if (t === "agent"){ a = wfAgent(st.agent); if (a && a.identity && ICON_OK.test(a.identity.icon || "")) return s("image",{href:a.identity.icon, x:x, y:y, width:size, height:size}); k = LOGO.copilotstudio ? "copilotstudio" : null; }
  else if (t === "copilot") k = LOGO.m365copilot ? "m365copilot" : null;
  else if (t === "connector" || t === "human_review" || t === "extract" || (t === "trigger" && st.type === "connector")) k = wfLogoKey(st.system);
  if (k && IMG_OK.test(LOGO[k].uri || "")) return s("image",{href:LOGO[k].uri, x:x, y:y, width:size, height:size});
  var g = t === "trigger" ? (st.type === "agent" ? WFT.agent.glyph : WF_GLYPH.trigger) : (WFT[t] ? WFT[t].glyph : WF_GLYPH[t]);
  var col = t === "trigger" || t === "outcome" ? "#4ADE80" : (t === "end" ? "#A0A7B4" : (WFT[t] || {}).color);
  return svgGlyph(g, x, y, size, col);
}
function wfAria(n){
  var s = n.s || {}, t = n.type;
  if (t === "trigger"){ var tl = (WF_TRIG[s.type] || WF_TRIG.manual).label; return "Trigger: " + (s.label && String(s.label).toLowerCase() !== tl.toLowerCase() ? s.label + " (" + tl + ")" : tl); }
  if (t === "outcome") return "Desired outcome: " + (s.detail || "");
  if (t === "end") return "End: " + (s.label || "");
  return (WFT[t] || {label:t}).label + ": " + (s.label || "");
}
function wfSvg(L, sel, wfName){
  var svg = s("svg",{viewBox:"0 0 " + L.w + " " + L.h, width:L.w, height:L.h, class:"wfsvg", role:"group", "aria-label":"Workflow " + wfName});
  var bg = s("g",{class:"wfframes","aria-hidden":"true"});
  L.boxes.forEach(function(b){ bg.appendChild(s("rect",{x:b.x, y:b.y, width:b.w, height:b.h, rx:16, class:"wfcont" + (b.id === sel ? " sel" : ""), "data-t":b.type, "data-box":b.id})); });
  svg.appendChild(bg);
  var eg = s("g",{class:"wfedges","aria-hidden":"true"});
  L.edges.forEach(function(e){ eg.appendChild(s("path",{d:e.wrapY ? wfWrapPath(e.a, e.b, e.wrapY) : wfPath(e.a, e.b), class:"wfe" + (e.cls ? " " + e.cls : "") + (e.wrapY ? " wrap" : "")})); });
  svg.appendChild(eg);
  L.nodes.forEach(function(n){
    if (n.kind === "box"){
      var bgx = s("g",{class:"wfn wfboxg " + n.type + (n.id === sel ? " sel" : ""), "data-n":n.id, "data-t":n.type, role:"button", tabindex:"0", "aria-label":wfAria(n)});
      bgx.appendChild(s("rect",{x:n.x + 1, y:n.y + 1, width:n.w - 2, height:34, rx:15, class:"wfhit"}));
      bgx.appendChild(svgGlyph(WFT[n.type].glyph, n.x + 12, n.y + 9, 18, WFT[n.type].color));
      bgx.appendChild(s("text",{x:n.x + 38, y:n.y + 23, class:"wfct"}, wrapWords((WFT[n.type].label + " \u00b7 " + (n.s.label || "")), Math.floor((n.w - 50) / 6.6), 1)[0]));
      bgx.appendChild(s("circle",{cx:n.inP[0], cy:n.inP[1], r:4.5, class:"wfport"}));
      bgx.appendChild(s("circle",{cx:n.outP[0], cy:n.outP[1], r:4.5, class:"wfport"}));
      svg.appendChild(bgx); return;
    }
    var st = n.s || {}, t = n.type, cls = "wfn " + t + (n.id === sel ? " sel" : "");
    var g = s("g",{class:cls, "data-n":n.id, "data-t":t, role:"button", tabindex:"0", "aria-label":wfAria(n)});
    g.appendChild(s("rect",{x:n.x, y:n.y, width:n.w, height:n.h, rx:t === "end" ? 22 : 16, class:"wfbox"}));
    if (t === "outcome"){
      g.appendChild(wfIcon(n, n.x + 14, n.y + 13, 20));
      g.appendChild(s("text",{x:n.x + 42, y:n.y + 28, class:"wfot"}, "DESIRED OUTCOME"));
      wrapWords(String(st.detail || TBC), 36, 3).forEach(function(tx, i){ g.appendChild(s("text",{x:n.x + 16, y:n.y + 50 + i * 15, class:"wfod"}, tx)); });
      g.appendChild(s("circle",{cx:n.inP[0], cy:n.inP[1], r:4.5, class:"wfport"}));
      svg.appendChild(g); return;
    }
    if (n.pills){
      g.appendChild(wfIcon(n, n.x + 14, n.y + 11, 20));
      wfHead(st).forEach(function(tx, i){ g.appendChild(s("text",{x:n.x + 42, y:n.y + 26 + i * 16, class:"wft"}, tx)); });
      n.pills.forEach(function(p){
        g.appendChild(s("rect",{x:n.x + 14, y:p.y - WFL.PH / 2, width:n.w - 28, height:WFL.PH, rx:WFL.PH / 2, class:"wfpill" + (p.def ? " def" : "")}));
        g.appendChild(s("text",{x:n.x + n.w / 2, y:p.y + 4.5, "text-anchor":"middle", class:"wfpt"}, wrapWords(p.label, 24, 1)[0]));
        g.appendChild(s("circle",{cx:p.port[0], cy:p.port[1], r:4.5, class:"wfport"}));
      });
    } else {
      g.appendChild(wfIcon(n, n.x + 14, n.y + (n.h - 22) / 2, 22));
      var lines = wrapWords(String(st.label || ""), t === "end" ? 15 : 20, 2), ty = n.y + n.h / 2 + (lines.length > 1 ? -3 : 4.5);
      lines.forEach(function(tx, i){ g.appendChild(s("text",{x:n.x + 46, y:ty + i * 15, class:"wft"}, tx)); });
      if (t !== "trigger" && t !== "end") g.appendChild(s("circle",{cx:n.outP[0], cy:n.outP[1], r:4.5, class:"wfport"}));
      if (t === "trigger") g.appendChild(s("circle",{cx:n.outP[0], cy:n.outP[1], r:4.5, class:"wfport"}));
    }
    if (t !== "trigger") g.appendChild(s("circle",{cx:n.inP[0], cy:n.inP[1], r:4.5, class:"wfport"}));
    if (WFT[t] && WFT[t].kind !== "note") g.appendChild(s("circle",{cx:n.x + n.w - 13, cy:n.y + 12, r:4, class:"wfk " + WFT[t].kind}));
    svg.appendChild(g);
  });
  L.notes.forEach(function(nt){
    var g = s("g",{class:"wfnote","aria-hidden":"true"}), lines = wrapWords(nt.text, 30, 3), h = 18 + lines.length * 14;
    g.appendChild(s("path",{d:"M" + nt.x + " " + nt.y + " h184 v" + (h - 12) + " l-12 12 h-172 z", class:"wfnb"}));
    g.appendChild(svgGlyph(WFT.note.glyph, nt.x + 8, nt.y + 7, 14, WFT.note.color));
    lines.forEach(function(tx, i){ g.appendChild(s("text",{x:nt.x + 28, y:nt.y + 18 + i * 14, class:"wfnt"}, tx)); });
    svg.appendChild(g);
  });
  return svg;
}
function wfCount(L){
  var c = {ai:0, rule:0, human:0}, by = {};
  L.nodes.forEach(function(n){ var t = n.type; if (WFT[t]){ by[t] = (by[t] || 0) + 1; if (c[WFT[t].kind] !== undefined) c[WFT[t].kind]++; } });
  by.note = L.notes.length;
  return {kinds:c, by:by};
}
function wfPanel(a, wf, L, id, onClose){
  var n = L.byId[id] || L.byId.trigger, st = n.s || {}, t = n.type, out = [];
  var tri = t === "trigger" ? (WF_TRIG[st.type] || WF_TRIG.manual) : null, info = WFT[t];
  var title = t === "outcome" ? "Desired outcome" : (st.label || (info ? info.label : ""));
  var icon = h("span",{class:"wfpi"}); var isv = s("svg",{viewBox:"0 0 24 24", width:"22", height:"22"}); isv.appendChild(wfIcon({type:t, s:st}, 0, 0, 24)); icon.appendChild(isv);
  out.push(h("div",{class:"wfph"}, icon, h("div",{class:"wfpt2"}, h("b",null, title),
    h("span",{class:"wfptag"}, tri ? "Trigger \u00b7 " + tri.label : (info ? info.label : (t === "end" ? "End of a branch" : "Outcome")), info && WF_KIND[info.kind][0] ? " \u00b7 " + WF_KIND[info.kind][0] : "")),
    onClose ? h("button",{type:"button", class:"wfx", "aria-label":"Close the properties", title:"Close", onclick:onClose}, "\u00d7") : null));
  if (tri) out.push(h("div",{class:"wfps"}, h("h5",null,"Trigger type"), h("div",{class:"wfbox2"}, h("b",null, tri.label), h("span",null, tri.desc))));
  else if (info) out.push(h("div",{class:"wfps"}, h("h5",null,"What this node does"), h("p",null, info.desc), info.kind !== "note" ? h("p",{class:"wfkind " + info.kind}, WF_KIND[info.kind][0] + ": " + WF_KIND[info.kind][1]) : null));
  if (t === "outcome") out.push(h("div",{class:"wfps"}, h("h5",null,"What the workflow delivers"), h("p",null, st.detail || TBC)));
  if (st.detail && t !== "outcome") out.push(h("div",{class:"wfps"}, h("h5",null,"In this workflow"), h("p",null, st.detail)));
  var ag = wfAgent(st.agent);
  if (ag) out.push(h("div",{class:"wfps"}, h("h5",null,"Agent"), agentChip(ag, true)));
  if (st.system) out.push(h("div",{class:"wfps"}, h("h5",null, t === "trigger" ? "Source" : "System"), h("p",{class:"wfsys"}, logosFor(String(st.system), 16, 2), String(st.system))));
  if (st.approver) out.push(h("div",{class:"wfps"}, h("h5",null,"Who decides"), h("p",null, String(st.approver))));
  if (n.pills) out.push(h("div",{class:"wfps"}, h("h5",null,"Branches"), h("ul",{class:"wfbl"}, n.pills.map(function(p){
    var b = arr(st.branches).filter(function(x){ return x && String(x.label) === p.label; })[0];
    var steps = b ? arr(b.steps).map(function(z){ return z && z.label; }).filter(Boolean) : [];
    return h("li",null, h("b",null, p.label), " \u2192 ", p.def ? "continues with the next step" : (steps.length ? steps.join(" \u2192 ") + (b.then === "end" || (b.end && b.then !== "continue") ? " \u2192 ends: " + (b.end || "End") : " \u2192 rejoins") : (b && (b.then === "end" || b.end) ? "ends: " + (b.end || "End") : "continues")));
  }))));
  if (n.kind === "box") out.push(h("div",{class:"wfps"}, h("h5",null, t === "loop" ? "Repeats" : "Groups"), h("ul",{class:"wfbl"}, arr(st.steps).map(function(z){ return z && z.label ? h("li",null, (WFT[wfT(z)] || {}).label + " \u00b7 " + z.label) : null; }))));
  if (arr(st.inputs).length || arr(st.outputs).length) out.push(h("div",{class:"wfps"}, h("h5",null,"Data"), h("p",{class:"wfio"},
    arr(st.inputs).map(function(x){ return h("span",{class:"pill"}, "in \u00b7 " + x); }), arr(st.outputs).map(function(x){ return h("span",{class:"pill"}, "out \u00b7 " + x); }))));
  if (st.note) out.push(h("div",{class:"wfps"}, h("h5",null,"Note"), h("p",{class:"wfnp"}, String(st.note))));
  return h("aside",{class:"wfprops", "aria-live":"polite"}, out);
}
function wfZoom(frame, L, z){
  var svg = frame.querySelector("svg.wfsvg"), cv = frame.querySelector(".wfcanvas");
  if (!svg || !L) return;
  if (z === "fit"){ var cw = cv && cv.clientWidth ? cv.clientWidth - 24 : 900; z = Math.max(0.3, Math.min(1, cw / L.w)); }
  z = Math.max(0.3, Math.min(1.6, z));
  frame._z = z;
  svg.setAttribute("width", String(Math.round(L.w * z))); svg.setAttribute("height", String(Math.round(L.h * z)));
  var lb = frame.querySelector(".wfzl"); if (lb) lb.textContent = Math.round(z * 100) + "%";
}
function wfSection(a){
  var wf = wfOf(a);
  if (!wf) return h("p",{class:"note"}, "No workflow yet: it is drawn from the canvas plan, so add the plan steps (MVP candidates first).");
  var key = a.id, name = String(wf.name || (shortOf(a) + " workflow"));
  var frame = h("div",{class:"wf", id:"wf-" + String(key).replace(/\W/g, "_")});
  var L = wfLayout(wf, state.wfRow ? 0 : WFL.WRAP), sel = (state.wfSel || {})[key] || null;
  if (sel && !L.byId[sel]) sel = null;
  var cnt = wfCount(L);
  function panel(id){ return id ? wfPanel(a, wf, L, id, function(){ select(null); }) : h("aside",{class:"wfprops", hidden:true}); }
  function select(id){
    state.wfSel = state.wfSel || {}; state.wfSel[key] = id; sel = id;
    Array.prototype.forEach.call(frame.querySelectorAll(".wfn"), function(g){ g.classList.toggle("sel", g.getAttribute("data-n") === id); });
    var p = frame.querySelector(".wfprops"); if (p) p.replaceWith(panel(id));
    frame.classList.toggle("open", !!id);
  }
  function hi(t, keep){
    if (!keep) frame._hi = frame._hi === t ? null : t;
    Array.prototype.forEach.call(frame.querySelectorAll(".wfn,.wfcont"), function(g){ g.classList.toggle("dim", !!frame._hi && g.getAttribute("data-t") !== frame._hi); });
    Array.prototype.forEach.call(frame.querySelectorAll(".wfadd button"), function(b){ b.setAttribute("aria-pressed", b.getAttribute("data-t") === frame._hi ? "true" : "false"); });
  }
  function draw(){
    L = wfLayout(wf, state.wfRow ? 0 : WFL.WRAP); frame._L = L; frame._z = 1;
    var svg = wfSvg(L, sel, name);
    Array.prototype.forEach.call(svg.querySelectorAll(".wfn"), function(g){
      var id = g.getAttribute("data-n");
      g.addEventListener("click", function(){ select(id); });
      g.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " "){ e.preventDefault(); select(id); } });
    });
    var old = frame.querySelector("svg.wfsvg"); if (old) old.replaceWith(svg);
    var lb = frame.querySelector(".wfzl"); if (lb) lb.textContent = "100%";
    var lt = frame.querySelector(".wflay"); if (lt){ lt.textContent = state.wfRow ? "Overview" : "Designer row"; lt.title = state.wfRow ? "Fold the workflow into rows to see it on one screen" : "One row from left to right, as in the designer"; }
    frame.classList.toggle("row", !!state.wfRow);
    hi(null, true);
  }
  var add = h("nav",{class:"wfadd", "aria-label":"Workflow node types"}, h("div",{class:"wfaddh"}, "Add"), WF_ADD.map(function(t){
    var c = cnt.by[t] || 0;
    return h("button",{type:"button", class:c ? "" : "unused", "data-t":t, "aria-pressed":"false", title:WFT[t].desc,
      "aria-label":"Highlight " + WFT[t].label + " nodes (" + c + " in this workflow)", onclick:function(){ hi(t); }},
      glyphSpan(WFT[t].glyph, "wfg"), h("span",null, WFT[t].label), c ? h("em",null, String(c)) : null);
  }));
  Array.prototype.forEach.call(add.querySelectorAll(".wfg"), function(sp, i){ sp.style.color = WFT[WF_ADD[i]].color; });
  var canvas = h("div",{class:"wfcanvas"}, s("svg",{class:"wfsvg"}),
    h("div",{class:"wftools", role:"toolbar", "aria-label":"Canvas"},
      h("button",{type:"button", title:"Zoom out", "aria-label":"Zoom out", onclick:function(){ wfZoom(frame, frame._L, (frame._z || 1) - 0.15); }}, "\u2212"),
      h("span",{class:"wfzl"}, "100%"),
      h("button",{type:"button", title:"Zoom in", "aria-label":"Zoom in", onclick:function(){ wfZoom(frame, frame._L, (frame._z || 1) + 0.15); }}, "+"),
      h("button",{type:"button", title:"Fit to the window", onclick:function(){ wfZoom(frame, frame._L, "fit"); }}, "Fit"),
      h("button",{type:"button", class:"wflay", onclick:function(){ state.wfRow = !state.wfRow; draw(); }}, "")));
  frame.appendChild(h("div",{class:"wfbar"},
    h("span",{class:"wfname"}, svgIconInline(), name),
    h("span",{class:"wfstat"}, wf.status && String(wf.status).toLowerCase() !== "draft" ? String(wf.status) : "Draft"),
    wf.derived ? h("span",{class:"wfder"}, "Derived from the plan \u00b7 refine in the workshop") : null,
    h("span",{class:"wfsum"},
      h("span",{class:"wfk2 ai"}, cnt.kinds.ai + " AI"), h("span",{class:"wfk2 rule"}, cnt.kinds.rule + " deterministic"), h("span",{class:"wfk2 human"}, cnt.kinds.human + " human")),
    h("span",{class:"wfh"}, "Copilot Studio workflow \u00b7 GitHub Copilot harness")));
  frame.appendChild(h("div",{class:"wfbody"}, add, h("div",{class:"wfstage"}, canvas, panel(sel))));
  frame.addEventListener("keydown", function(e){ if (e.key === "Escape" && sel){ e.stopPropagation(); select(null); } });
  frame.classList.toggle("open", !!sel);
  draw();
  return [h("p",{class:"note wfintro"}, "The plan as a Copilot Studio workflow: it starts with the trigger, runs each step as a designer node and ends in the desired outcome. AI steps (Agent, Classify, Extract, Copilot) can vary; deterministic steps follow rules; a person approves before anything leaves the company. Select a node for its properties, a node type in Add to highlight it; switch between the overview and the designer row."), frame, evPills(wf.src)];
}
function svgIconInline(){ return glyphSpan('<path d="M4 7h5v4H4zM15 13h5v4h-5z"/><path d="M9 9h3a2 2 0 0 1 2 2v2a2 2 0 0 0 2 2"/>', "wfg"); }

/* ---------------- org model (HAIRO) ---------------- */
function orgSvg(){
  var W = 1000, C = 500, R1 = 165, R2 = 292, R3 = 440;
  function P(r, a){ return [C + r * Math.cos(a), C + r * Math.sin(a)]; }
  function arcPath(r, a0, a1, rev){
    var p0 = P(r, a0), p1 = P(r, a1), large = (a1 - a0) > Math.PI ? 1 : 0;
    return rev ? "M" + p1[0].toFixed(1) + " " + p1[1].toFixed(1) + " A" + r + " " + r + " 0 " + large + " 0 " + p0[0].toFixed(1) + " " + p0[1].toFixed(1)
               : "M" + p0[0].toFixed(1) + " " + p0[1].toFixed(1) + " A" + r + " " + r + " 0 " + large + " 1 " + p1[0].toFixed(1) + " " + p1[1].toFixed(1);
  }
  var svg = s("svg",{viewBox:"0 0 " + W + " " + W, class:"orgsvg", role:"group", "aria-label":"Hybrid organisation model: human leaders in the centre, lead agents in the inner ring, specialist agents in the outer ring, grouped by " + (M.domain_label_plural || "journeys")});
  var gEdges = s("g"), gNodes = s("g"), gLabels = s("g"), gRings = s("g");
  svg.appendChild(gRings); svg.appendChild(gEdges); svg.appendChild(gNodes); svg.appendChild(gLabels);
  gRings.appendChild(s("circle",{cx:C, cy:C, r:R1, fill:"none", stroke:"var(--line-soft)", "stroke-width":1.5}));
  gRings.appendChild(s("circle",{cx:C, cy:C, r:R2, fill:"none", stroke:"var(--line-soft)", "stroke-width":1.5}));
  var nd = D.length || 1, gap = nd > 1 ? 0.07 : 0;
  var weights = D.map(function(d){ return Math.max(2, d.agents.length); });
  var total = weights.reduce(function(a, b){ return a + b; }, 0) || 1;
  var avail = 2 * Math.PI - gap * nd;
  var cur = -Math.PI / 2 - (avail * weights[0] / total) / 2;
  var leaders = arr(BP.leaders);
  var LPOS = {};
  var nl = leaders.length;
  var lr = nl <= 1 ? 0 : (nl <= 3 ? 44 : (nl <= 5 ? 56 : 64)), lnode = nl <= 3 ? 30 : 25;
  leaders.forEach(function(L, i){
    var a = nl === 2 ? (i === 0 ? Math.PI : 0) : (-Math.PI / 2 + i * 2 * Math.PI / Math.max(nl, 1));
    LPOS[L.id || ("L" + i)] = nl === 1 ? [C, C] : P(lr, a);
  });
  function dimmed(d){ return state.orgDomain && state.orgDomain !== d.id; }
  function nodeEvents(g, label, fn){
    g.setAttribute("tabindex","0"); g.setAttribute("role","button"); g.setAttribute("aria-label", label);
    g.addEventListener("click", fn);
    g.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fn(); } });
  }
  function badge(g, x, y, r, a){
    var au = autonomyOf(a);
    if (!state.badges || !au) return;
    var bx = x + r * 0.72, by = y - r * 0.72;
    g.appendChild(s("circle",{cx:bx, cy:by, r:8.5, fill:"var(--ink)", stroke:"var(--panel)", "stroke-width":1.5}));
    g.appendChild(s("text",{x:bx, y:by + 3.6, "text-anchor":"middle", style:"font-size:10px;font-weight:700;fill:var(--bg)"}, String(au.n)));
  }
  function ringStyle(a){
    var lc = String(a.lifecycle || "Planned").toLowerCase();
    var st = String(note("val|agent|" + a.id).status || a.status || "hypothesis").toLowerCase();
    return { dash: (lc === "planned" && st !== "validated") ? "5 4" : null, faded: st === "rejected" || lc === "retired" };
  }
  D.forEach(function(d, i){
    var span = avail * weights[i] / total, a0 = cur, a1 = cur + span, mid = (a0 + a1) / 2;
    cur = a1 + gap;
    var dim = dimmed(d);
    var arcG = s("g",{class: dim ? "dim" : null});
    arcG.appendChild(s("path",{d:arcPath(R3, a0, a1, false), fill:"none", stroke:d.color, "stroke-width":7, "stroke-linecap":"round", opacity:.9}));
    var bottom = Math.sin(mid) > 0.2;
    var pid = "orgarc-" + i;
    arcG.appendChild(s("path",{id:pid, d:arcPath(bottom ? R3 + 26 : R3 + 14, a0, a1, bottom), fill:"none", stroke:"none"}));
    var tp = s("textPath",{href:"#" + pid, startOffset:"50%", "text-anchor":"middle"}, String(d.short_name || d.name).toUpperCase());
    tp.setAttributeNS("http://www.w3.org/1999/xlink", "xlink:href", "#" + pid);
    arcG.appendChild(s("text",{class:"dlabel", "text-anchor":"middle", style:"fill:var(--ink)"}, tp));
    nodeEvents(arcG, "Filter on " + d.name, function(){ state.orgDomain = state.orgDomain === d.id ? null : d.id; render(); });
    arcG.setAttribute("style","cursor:pointer");
    gLabels.appendChild(arcG);
    var o = d.orchestrator;
    var lp = P(R1, mid);
    if (o && state.orgStage >= 2){
      var lid = d.leader || o.leader;
      if (lid && LPOS[lid]) gEdges.appendChild(s("line",{x1:LPOS[lid][0], y1:LPOS[lid][1], x2:lp[0], y2:lp[1], class:"acct" + (dim ? " dim" : "")}));
    }
    var team = d.agents;
    team.forEach(function(a, k){
      if (state.orgStage < 3) return;
      var ang = a0 + span * (k + 0.5) / Math.max(team.length, 1);
      var p = P(R2, ang);
      if (o && state.orgStage >= 2) gEdges.appendChild(s("line",{x1:lp[0], y1:lp[1], x2:p[0], y2:p[1], class:"edge" + (dim ? " dim" : ""), stroke:d.color}));
      var rs = ringStyle(a);
      var g = s("g",{class:"node" + (dim ? " dim" : "") + (rs.faded ? " faded" : "")});
      if (a.mvp) g.appendChild(s("circle",{cx:p[0], cy:p[1], r:27, fill:"none", stroke:"var(--accent)", "stroke-width":3}));
      g.appendChild(s("circle",{class:"ring", cx:p[0], cy:p[1], r:21, fill:"var(--panel)", stroke:d.color, "stroke-width":2.5, "stroke-dasharray":rs.dash}));
      g.appendChild(s("text",{x:p[0], y:p[1] + 4.5, "text-anchor":"middle", style:"font-size:12.5px;font-weight:700;fill:var(--ink)"}, initials(orgLabel(a))));
      badge(g, p[0], p[1], 21, a);
      g.appendChild(s("title",null, nameOf(a) + " \u2014 " + (a.capability || "")));
      nodeEvents(g, nameOf(a) + ", specialist agent in " + d.name, function(){ openAgent(a.id); });
      gNodes.appendChild(g);
      if (state.labels){
        var c = Math.cos(ang), sn = Math.sin(ang);
        var lpp = P(R2 + 31, ang);
        var anchor = c > 0.28 ? "start" : (c < -0.28 ? "end" : "middle");
        var lines = wrapWords(orgLabel(a), 15, 2);
        var y0 = lpp[1] + (anchor === "middle" ? (sn < 0 ? -4 - (lines.length - 1) * 13 : 10) : 4 - (lines.length - 1) * 6.5);
        var t = s("text",{x:lpp[0], y:y0, "text-anchor":anchor, class:"lbl-s" + (dim ? " dim" : ""), style:"paint-order:stroke;stroke:var(--panel);stroke-width:3px"});
        lines.forEach(function(l, li){ t.appendChild(s("tspan",{x:lpp[0], dy: li ? 13 : 0}, l)); });
        gLabels.appendChild(t);
      }
    });
    if (o && state.orgStage >= 2){
      var rs2 = ringStyle(o);
      var g2 = s("g",{class:"node" + (dim ? " dim" : "") + (rs2.faded ? " faded" : "")});
      if (o.mvp) g2.appendChild(s("circle",{cx:lp[0], cy:lp[1], r:38, fill:"none", stroke:"var(--accent)", "stroke-width":3}));
      if (rs2.dash) g2.appendChild(s("circle",{cx:lp[0], cy:lp[1], r:33, fill:"none", stroke:d.color, "stroke-width":2, "stroke-dasharray":"5 4"}));
      g2.appendChild(s("circle",{class:"ring", cx:lp[0], cy:lp[1], r:28, fill:d.color, stroke:"var(--panel)", "stroke-width":2}));
      g2.appendChild(s("text",{x:lp[0], y:lp[1] + 5, "text-anchor":"middle", style:"font-size:14px;font-weight:700;fill:" + onColor(d.color)}, initials(orgLabel(o))));
      badge(g2, lp[0], lp[1], 28, o);
      g2.appendChild(s("title",null, nameOf(o) + " \u2014 " + (o.mission || "")));
      nodeEvents(g2, nameOf(o) + ", lead agent for " + d.name, function(){ openAgent(o.id); });
      gNodes.appendChild(g2);
      if (state.labels){
        /* lead labels sit beside the node on the inner side for top/bottom journeys, below it otherwise,
           so they never cross the specialist ring */
        var s2 = Math.sin(mid);
        var lines2 = wrapWords(orgLabel(o), 18, 2);
        var above = s2 > 0.7;
        var y2 = above ? lp[1] - 40 - (lines2.length - 1) * 13 : lp[1] + 48;
        var t2 = s("text",{x:lp[0], y:y2, "text-anchor":"middle", class:"lbl" + (dim ? " dim" : ""), style:"font-weight:700;paint-order:stroke;stroke:var(--panel);stroke-width:4px"});
        lines2.forEach(function(l, li){ t2.appendChild(s("tspan",{x:lp[0], dy: li ? 13 : 0}, l)); });
        gLabels.appendChild(t2);
      }
    }
  });
  /* centre: human-led */
  if (nl >= 3) gLabels.appendChild(s("text",{x:C, y:C + 4, "text-anchor":"middle", class:"center-lbl", style:"font-size:10.5px;letter-spacing:.04em"}, M.center_label || "Human-led"));
  else gLabels.appendChild(s("text",{x:C, y:C - lnode - 18, "text-anchor":"middle", class:"center-lbl"}, M.center_label || "Human-led"));
  leaders.forEach(function(L, i){
    var p = LPOS[L.id || ("L" + i)];
    var g = s("g",{class:"node"});
    g.appendChild(s("circle",{class:"ring", cx:p[0], cy:p[1], r:lnode, fill:"var(--ink)", stroke:"var(--panel)", "stroke-width":3}));
    g.appendChild(s("text",{x:p[0], y:p[1] + 5, "text-anchor":"middle", style:"font-size:" + (lnode > 26 ? 14 : 12.5) + "px;font-weight:700;fill:var(--bg)"}, L.initials || initials(L.short || L.role || L.name)));
    g.appendChild(s("title",null, (L.name ? L.name + " \u2014 " : "") + (L.role || "")));
    nodeEvents(g, (L.role || L.name) + ", human leader", function(){ openLeader(L); });
    gNodes.appendChild(g);
  });
  if (!leaders.length) gLabels.appendChild(s("text",{x:C, y:C + 5, "text-anchor":"middle", class:"lbl"}, "People set direction"));
  if (state.orgStage < 3){
    var cta = state.orgStage === 1 ? "Delegate management \u2192 lead agents" : "Delegate routine work \u2192 agent teams";
    var gc = s("g",{class:"node"});
    var cy = C + (nl > 1 ? lr + lnode + 44 : lnode + 44);
    gc.appendChild(s("rect",{x:C - 130, y:cy - 16, width:260, height:32, rx:16, fill:"var(--accent)"}));
    gc.appendChild(s("text",{x:C, y:cy + 5, "text-anchor":"middle", style:"font-size:13px;font-weight:700;fill:var(--accent-on)"}, "+ " + cta));
    nodeEvents(gc, cta, function(){ state.orgStage = Math.min(3, state.orgStage + 1); render(); });
    gNodes.appendChild(gc);
  }
  return svg;
}
function renderOrg(){
  var leaders = arr(BP.leaders);
  var stageBtns = h("div",{class:"seg",role:"group","aria-label":"Reveal"},
    [[1,"Human-led"],[2,"+ Lead agents"],[3,"+ Agent teams"]].map(function(x){
      return h("button",{type:"button","aria-pressed": state.orgStage === x[0] ? "true" : "false", onclick:function(){ state.orgStage = x[0]; render(); }}, x[1]);
    }));
  var chips = h("div",{class:"filters",style:"margin-top:8px"},
    h("button",{type:"button",class:"tab",style:domainStyle("#5E5E5E"),"aria-pressed": !state.orgDomain ? "true" : "false", onclick:function(){ state.orgDomain = null; render(); }}, h("span",{class:"num",style:filled("#5E5E5E")},"\u2217"), "All"),
    D.map(function(d){ return h("button",{type:"button",class:"tab",style:domainStyle(d.color),"aria-pressed": state.orgDomain === d.id ? "true" : "false", onclick:function(){ state.orgDomain = state.orgDomain === d.id ? null : d.id; render(); }}, h("span",{class:"num",style:filled(d.color)}, String(D.indexOf(d) + 1)), d.short_name || d.name); }));
  var cb = function(key, label){
    var id = "chk-" + key;
    return h("label",{class:"chk",for:id}, h("input",{type:"checkbox",id:id, checked: state[key] ? true : null, onchange:function(e){ state[key] = e.target.checked; render(); }}), label);
  };
  var nLead = ALL.filter(function(a){ return a.role === "lead"; }).length;
  var side = h("div",{class:"orgside"},
    h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null,"Reveal the organisation")), stageBtns, chips, h("div",{style:"margin-top:8px"}, cb("labels","Show agent names"), cb("badges","Show autonomy level"))),
    h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null, M.center_label || "Human-led"), h("span",null,"accountable leaders")),
      leaders.length ? leaders.map(function(L){ return h("div",{class:"li"}, h("b",null, L.role || L.name), h("span",null, L.direction || L.decides || "")); }) : h("p",{class:"tbc"},TBC)),
    h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null,"Legend")),
      h("div",{class:"li"}, h("b",null,"Filled circle"), h("span",null,"Lead agent: the single point of contact that plans, delegates and reports back")),
      h("div",{class:"li"}, h("b",null,"Outlined circle"), h("span",null,"Specialist agent in the team of a lead agent")),
      h("div",{class:"li"}, h("b",null,"Dashed outline"), h("span",null,"Planned position, not yet validated")),
      h("div",{class:"li"}, h("b",null,"Accent halo"), h("span",null,"MVP candidate")),
      h("div",{class:"li"}, h("b",null,"Number badge"), h("span",null, AUTONOMY.map(function(a){ return a.n + " " + a.label; }).join(" \u00b7 "))),
      h("p",{class:"note"}, nLead + " lead agents \u00b7 " + (ALL.length - nLead) + " specialist agents \u00b7 select any node for its role card")));
  var sys = h("div",{class:"sysgrid"}, D.filter(function(d){ return arr(d.systems).length; }).map(function(d){
    return h("div",{class:"panel",style:"--d:" + d.color}, h("b",null, d.name), h("div",{class:"chips"}, arr(d.systems).map(function(x){ return h("span",{class:"dchip"}, x); })));
  }));
  var table = h("details",{class:"acc",style:"margin-top:12px"}, h("summary",null, h("span",{class:"n"},"\u2261"), "All agents as a list"),
    h("div",{class:"bd"}, h("div",{class:"tscroll"}, h("table",{class:"t"},
      h("thead",null, h("tr",null, ["Agent","Role","Journey","Autonomy","Horizon","Lifecycle","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, ALL.map(function(a){
        var au = autonomyOf(a);
        return h("tr",null, h("td",null, h("button",{type:"button",class:"agentlink",style:"all:unset;cursor:pointer;font-weight:700;color:var(--ink)", onclick:function(){ openAgent(a.id); }}, h("span",{class:"anm",style:"display:inline-flex"}, idIcon(a), nameOf(a)))),
          h("td",null, a.role === "lead" ? "Lead" : "Specialist"), h("td",null, a._d.name), h("td",null, au ? au.label : TBC), h("td",null, a.horizon || TBC), h("td",null, a.lifecycle || "Planned"), h("td",null, statusPill(note("val|agent|" + a.id).status || a.status)));
      }))))));
  return [h("h2",{class:"sec"}, "How " + (M.short || M.customer || "the company") + " could work: human-led, agent-operated"),
    h("p",{class:"lead"}, BP.org_intro || "People set direction and stay accountable in the centre. Each journey gets a lead agent that plans and delegates to a team of specialist agents. Reveal the layers step by step, or select any node to open its role card and role profile."),
    h("div",{class:"orgwrap"}, h("div",null, orgSvg()), side),
    arr(D).some(function(d){ return arr(d.systems).length; }) ? h("h3",{class:"sub"},"Systems and tools the agents work with") : null, sys, table];
}

/* ---------------- blueprint ---------------- */
function renderBlueprint(){
  var d = dom(), o = d.orchestrator || {name:"Lead agent", mission:TBC};
  var G = BP.governance || {}, IR = BP.intelligence_resources || {};
  var outcomesArr = arr(d.outcomes).length ? d.outcomes : arr(BP.outcomes);
  var outcomes = h("section",{class:"outcomes","aria-label":"Business outcomes"},
    h("div",null, h("b",{style:"font-size:14px;display:block"},"Business outcomes"), h("span",{class:"note"},"What the whole picture below is for")),
    outcomesArr.map(function(x){ return h("div",{class:"o"}, h("b",null,x.name), h("span",null,x.desc), evPills(x.src)); }),
    h("div",{class:"measure"}, h("b",null,"Measured by \u00b7 "), d.measured_by || BP.measured_by || TBC));
  var hl = d.human_led || BP.human_led || {};
  var human = h("div",{class:"human"}, h("h3",null,"Human-led"),
    ["Direction","Accountability","Judgement","Relationships"].map(function(k){ return h("div",{class:"hitem"}, h("b",null,k), h("span",null, hl[k] || TBC)); }));
  var others = h("div",{class:"others"}, D.map(function(x, i){
    if (i === state.d || !x.orchestrator) return null;
    return h("button",{type:"button",class:"other",title:"Open the " + x.name + " blueprint",onclick:function(){ state.d = i; render(); }}, h("b",null, shortName(x.orchestrator)), h("span",null, x.orchestrator.mission || ""));
  }));
  var lead = h("button",{type:"button",class:"leadcard",onclick:function(){ if (o.id) openAgent(o.id); }},
    h("span",{class:"anm"}, idIcon(o), h("b",null, nameOf(o))), h("span",null, (o.mission || TBC) + ". The only one people talk to: plans, delegates, brings together, reports back."),
    h("span",{class:"mpg"}, h("span",{class:"pill d"},"Memory"), h("span",{class:"pill d"},"Planning"), h("span",{class:"pill d"},"Goals")));
  var agents = h("div",{class:"agents",style:"--n:" + Math.min(Math.max(d.agents.length,1), 6)}, d.agents.map(function(a){
    var st = String(note("val|agent|" + a.id).status || a.status || "hypothesis").toLowerCase();
    var au = autonomyOf(a);
    return h("button",{type:"button",class:"agent" + (a.mvp ? " mvp" : "") + (st === "hypothesis" ? " hypo" : ""),onclick:function(){ openAgent(a.id); },"aria-label":a.name + " \u2014 open role card"},
      h("span",{class:"anm"}, idIcon(a), h("b",null, shortOf(a))), h("span",{class:"cap"}, String(a.capability || "").split(/;\s/)[0]),
      h("span",{class:"tags"}, a.mvp ? h("span",{class:"pill acc"},"MVP") : null, a.horizon ? h("span",{class:"pill"}, a.horizon) : null, au ? h("span",{class:"pill d",title:au.label}, "A" + au.n) : null));
  }));
  var da = d.data_agent;
  var agentop = h("div",{class:"agentop"}, h("h3",null,"Agent-operated \u00b7 ", d.name),
    D.length > 1 ? h("div",{class:"small-lbl",style:"margin-top:0"},"Other lead agents in the organisation") : null, D.length > 1 ? others : null,
    h("div",{class:"team-lbl"},"Agent team \u00b7 " + (d.journey_name || d.name)), lead, h("div",{class:"connector","aria-hidden":"true"}), agents,
    h("div",{class:"team-lbl",style:"text-transform:none;letter-spacing:0;font-weight:400"},"Select any agent for its role card \u00b7 accent frame = MVP candidate \u00b7 dashed = hypothesis"),
    da ? h("div",{class:"dataagent"}, h("span",{class:"anm"}, idIcon(da), h("b",null, idName(da) ? idName(da) + " \u00b7 data agent" : "Data agent \u00b7 " + (da.name || "Data agent"))), arr(da.products).map(function(p){ return h("span",{class:"dchip"}, p); })) : null);
  var hybrid = h("section",{class:"hybrid","aria-label":"Hybrid workforce"},
    h("div",{class:"ptitle"}, h("b",null,"Hybrid workforce"), h("span",null,"Two halves of one organisation, and the seam where they meet")),
    h("div",{class:"hybrid-grid"}, human, agentop),
    h("div",{class:"seam"}, h("b",null,"Approval \u00b7 the seam \u00b7 "), d.approval_seam || BP.approval_seam || TBC));
  var list = function(title, items, sub){ return h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null,title), sub ? h("span",null,sub) : null), arr(items).length ? arr(items).map(function(x){ return h("div",{class:"li"}, h("b",null,x.name), h("span",null,x.desc)); }) : h("p",{class:"tbc"},TBC)); };
  var lc = arr(IR.lifecycle).length ? IR.lifecycle : ["Planned","Prototype","Pilot","Active","Upskilling","Retired"];
  var intel = h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null, IR.title || "Intelligence Resources"), h("span",null, IR.subtitle || "IT and HR jointly run the agent workforce")),
    h("div",{class:"small-lbl"},"Lifecycle of every agent"),
    h("div",{class:"lifecycle"}, lc.map(function(st, i){ return [i ? h("span",{class:"ar"},"\u2192") : null, h("div",{class:"st" + (st === (IR.highlight || "Active") ? " active" : "")}, st)]; })),
    h("div",{class:"small-lbl"},"Agent record \u00b7 maintained across the lifecycle"),
    h("div",{class:"filechips"}, (arr(IR.agent_file).length ? IR.agent_file : ["Role profile","Instructions, versioned","Feedback log","Access list","KPIs"]).map(function(x){ return h("span",null,x); })),
    h("div",{class:"small-lbl"},"Where agents run and are watched"),
    h("div",{class:"runs"}, (arr(IR.runs_on).length ? IR.runs_on : [{name:"Microsoft Agent 365",desc:"Who the agent is: registry, identity, access"},{name:"Microsoft Foundry",desc:"What it runs on: runtime, models, evaluations"},{name:"Observability",desc:"What every run cost and how well it went"}]).map(function(x){ return h("div",null, h("b",null,x.name), h("span",null,x.desc)); })));
  var row3 = h("section",{class:"row3"}, list("Governance", G.items || BP.governance_items || (Array.isArray(BP.governance) ? BP.governance : null)), h("div",{class:"arrow"}, h("i",null,"\u2192"),"rules"), intel, h("div",{class:"arrow"}, h("i",null,"\u2192"),"evidence"), list("Security & trust", BP.security));
  var K = arr(BP.knowledge);
  var kItem = function(x){ return h("div",{class:"kbox" + (x.scope === "external" ? " ext" : "")}, x.scope === "external" ? h("span",{class:"pill",style:"margin-bottom:3px"},"External") : null, h("b",null,x.name), h("span",null,x.desc)); };
  var know = h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null,"Knowledge"), h("span",null,"Where an agent gets what it knows")),
    K.filter(function(x){ return x.scope !== "external" && x.scope !== "principle"; }).map(kItem),
    K.some(function(x){ return x.scope === "external"; }) ? h("div",{class:"small-lbl"},"External knowledge") : null,
    K.filter(function(x){ return x.scope === "external"; }).map(kItem),
    K.filter(function(x){ return x.scope === "principle"; }).map(function(x){ return h("div",{class:"kprinciple"}, h("b",null, x.name + " \u00b7 "), x.desc); }),
    arr(d.systems).length ? h("div",{class:"small-lbl"},"Systems for this journey") : null,
    arr(d.systems).length ? h("div",{class:"filechips"}, d.systems.map(function(x){ return h("span",null,x); })) : null);
  var ch = d.channels || {};
  var chan = h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null,"Channels"), h("span",null,"How work arrives")),
    h("div",{class:"small-lbl"},"Reached by people"), h("div",{class:"chgrid"}, arr(ch.people).map(function(x){ return h("div",null,x); })),
    h("div",{class:"small-lbl"},"Triggered without a person"), h("div",{class:"chgrid"}, arr(ch.triggered).map(function(x){ return h("div",null,x); })));
  var build = h("div",{class:"panel build"}, h("div",{class:"ptitle"}, h("b",null,"Build & run"), h("span",null,"Microsoft platform")), arr(BP.build_run).map(function(x){ return h("div",null, typeof x === "string" ? x : x.name); }));
  var row4 = h("section",{class:"row4"}, know, chan, build);
  var found = h("section",{class:"foundation"}, h("div",null, h("b",{style:"display:block;font-size:14px"},"Foundation"), h("span",{class:"note"},"Shared by people and agents alike")),
    arr(BP.foundation).map(function(x){ return h("div",{class:"f"}, h("b",null,x.name), h("span",null,x.desc)); }));
  return [h("h2",{class:"sec"}, "Hybrid organisation blueprint \u00b7 " + d.name), BP.blueprint_note ? h("p",{class:"note"}, BP.blueprint_note) : null, outcomes, hybrid, row3, row4, found];
}

/* ---------------- journeys ---------------- */
function renderJourney(){
  var d = dom();
  var head = h("div",{class:"jhead"}, h("div",null, h("h2",null, d.journey_name || d.name), h("p",null, d.journey_tagline || "")), evPills(d.src));
  var vis = h("div",{class:"vision"},
    h("div",{class:"box first"}, h("div",{class:"lbl"},"Vision"), h("span",null, d.vision || TBC)),
    h("div",{class:"box"}, h("div",{class:"lbl"},"AI contribution"), h("span",null, d.ai_contribution || TBC)),
    h("div",{class:"box"}, h("div",{class:"lbl"},"Business impact"), h("span",null, d.business_impact || TBC)));
  var stages = h("div",{class:"stages"}, arr(d.stages).map(function(st, i){
    var ag = agentByName(st.agent);
    return h("div",{class:"stage"},
      h("div",{class:"sh"}, h("span",{class:"n"}, String(i + 1)), st.name),
      h("div",{class:"cell"}, h("span",{class:"k"},"What happens"), st.happens || TBC),
      h("div",{class:"cell pain"}, h("span",{class:"k"},"Pain today"), st.pain || TBC, evPills(st.src)),
      h("div",{class:"cell ai"}, h("span",{class:"k"},"With agents"), st.ai || TBC),
      h("div",{class:"cell"}, h("span",{class:"k"},"Agent"), ag ? h("button",{type:"button",class:"agentlink",onclick:function(){ openAgent(ag.id); }}, h("span",{class:"anm",style:"display:inline-flex"}, idIcon(ag), nameOf(ag))) : (st.agent || h("span",{class:"tbc"},"Workflow / none"))));
  }));
  var personas = h("div",{class:"personas"}, arr(d.personas).map(function(p){
    return h("div",{class:"persona"},
      h("div",{class:"ph"}, h("div",{class:"av"}, initials(p.role || p.name)), h("div",null, h("b",null, p.role || p.name || TBC), h("div",{class:"kind"}, p.kind || "Internal"))),
      ["goal","pain","help","decides"].map(function(k){ return p[k] ? h("div",{class:"fld"}, h("b",null, {goal:"Goal",pain:"Pain",help:"How agents help",decides:"Decides"}[k] + ": "), p[k]) : null; }), evPills(p.src));
  }));
  var kp = arr(d.kpis);
  var kpis = kp.length ? h("div",{class:"tscroll"}, h("table",{class:"t"},
    h("thead",null, h("tr",null, ["KPI","Definition","Baseline","Target","Evidence"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, kp.map(function(k){ return h("tr",null, h("td",null, h("b",null, k.kpi || k.name)), h("td",null, k.definition || TBC), h("td",null, val(k.baseline)), h("td",null, val(k.target)), h("td",null, evPills(k.src) || "\u2014")); })))) : h("p",{class:"tbc"},TBC);
  return [head, vis, h("h3",{class:"sub"},"Journey stages"), stages, h("h3",{class:"sub"},"Personas"), personas, h("h3",{class:"sub"},"KPIs"), kpis];
}

/* ---------------- agents (canvas) ---------------- */
function canvasOf(a){
  var c = a.canvas || {};
  return {
    trigger: c.trigger || a.trigger, instructions: c.instructions, plan: c.plan, outcome: c.outcome || a.outcome,
    data_sources: c.data_sources, connectors: c.connectors || c.tools, approval: c.approval, autonomy: c.autonomy || a.autonomy,
    skills: c.skills, pattern: c.pattern || a.pattern, build: c.build || a.technology
  };
}
function cbox(title, v, cls, lg){ return h("div",{class:"c" + (cls ? " " + cls : "")}, h("h4",null,title), Array.isArray(v) ? (lg ? ulLogos(v) : ul(v)) : (lg && has(v) ? h("span",null, logosFor(String(v), 18), String(v)) : val(v))); }
function valBox(kind, id, onStatusChange){
  var k = "val|" + kind + "|" + id, n = note(k);
  var name = "v-" + kind + "-" + id.replace(/\W/g,"_");
  var opts = [["validated","Validated"],["adjusted","Adjust"],["rejected","Reject"],["open","Open"]];
  var stEl = h("span",{class:"status",role:"status"});
  return h("div",{class:"valbox"},
    h("b",null,"Workshop validation"), h("span",{class:"note"}," \u00b7 saved in this browser; export it from Discovery"),
    h("div",{class:"opts",role:"radiogroup","aria-label":"Validation status"}, opts.map(function(o){
      var rid = name + "-" + o[0];
      return h("label",{class:"opt",for:rid}, h("input",{type:"radio",id:rid,name:name,value:o[0],checked: n.status === o[0] ? true : null,onchange:function(){
        setNote(k,{status:o[0]}); stEl.textContent = "Saved";
        if (onStatusChange) onStatusChange();
      }}), o[1]);
    })),
    h("label",{class:"note",for:name + "-note"},"Notes from the discussion"),
    h("textarea",{id:name + "-note",placeholder:"What changed, what is missing, who owns it",oninput:function(e){ setNote(k,{note:e.target.value}); stEl.textContent = "Saved"; }}, n.note || ""),
    stEl);
}
function renderAgents(){
  var d = dom();
  var team = (d.orchestrator ? [d.orchestrator] : []).concat(d.agents);
  if (!team.length) return [h("p",{class:"tbc"},TBC)];
  var a = AG[state.agent];
  if (!a || a._d !== d) { a = team.filter(function(x){ return x.mvp; })[0] || team[0]; state.agent = a.id; }
  var list = h("nav",{class:"alist","aria-label":"Agents in " + d.name}, team.map(function(x){
    return h("button",{type:"button",class:"aitem","aria-current": x.id === a.id ? "true" : null,onclick:function(){ state.agent = x.id; render(); }},
      h("span",{class:"anm"}, idIcon(x), h("b",{title: idName(x) && x.name !== idName(x) ? x.name : null}, nameOf(x))), h("small",null, (x.role === "lead" ? "Lead agent" : "Specialist") + (x.mvp ? " \u00b7 MVP candidate" : "") + (x.horizon ? " \u00b7 " + x.horizon : "")));
  }));
  var c = canvasOf(a);
  var canvas = h("div",{class:"canvas"},
    cbox("Trigger", arr(c.trigger)),
    cbox("Plan", arr(c.plan), "wide"),
    cbox("Outcome", c.outcome),
    cbox("Instructions", c.instructions, "full inst"),
    cbox("Data & knowledge", arr(c.data_sources), null, true),
    cbox("Tools & connectors", arr(c.connectors), null, true),
    cbox("Human approval", arr(c.approval)),
    cbox("Autonomy", c.autonomy),
    c.skills ? cbox("Skills", arr(c.skills), "wide") : null,
    c.pattern ? cbox("Orchestration pattern", c.pattern) : null,
    c.build ? cbox("Build choice", c.build, null, true) : null);
  var decl = a.declarations || {};
  var nDecl = DECL.filter(function(x){ return has(decl[x[0]]); }).length;
  var declBox = h("div",null,
    h("div",{class:"note"}, nDecl + " of 7 declarations made \u00b7 an agent that cannot answer all seven is not ready to build"),
    h("div",{class:"meter","aria-hidden":"true"}, h("i",{style:"width:" + Math.round(nDecl / 7 * 100) + "%"})),
    h("div",{class:"decl"}, DECL.map(function(x){
      var v = decl[x[0]];
      return h("div",{class:"dc" + (has(v) ? "" : " missing")}, h("h4",null, x[1], has(v) ? h("span",{class:"pill val"},"Declared") : h("span",{class:"pill open"},"Open")), h("div",{class:"note",style:"margin-bottom:4px"}, x[2]), has(v) ? (Array.isArray(v) ? ul(v) : h("span",null, String(v))) : null);
    })));
  var main = h("div",null,
    h("div",{class:"jhead"}, h("div",null, h("h2",{class:"anm"}, idIcon(a, "aicon lg"), nameOf(a)), h("p",null, a.capability || a.mission || "")), agentPills(a)),
    h("div",{class:"btnrow"}, h("button",{type:"button",class:"btn",onclick:function(){ openAgent(a.id); }},"Role card"), h("button",{type:"button",class:"btn",onclick:function(){ openProfile(a); }},"Role profile"), evPills(a.src)),
    a.identity ? [h("h3",{class:"sub"},"Agent identity"), idPanel(a)] : null,
    h("h3",{class:"sub"},"Agentic trigger canvas"), canvas, financialSummary(a));
  var flow = h("div",{class:"agfull"}, h("h3",{class:"sub", id:"workflow"},"Workflow \u00b7 from trigger to outcome"), wfSection(a));
  var rest = h("div",{class:"agrest"},
    h("h3",{class:"sub"},"Readiness \u00b7 the seven declarations"), declBox,
    h("h3",{class:"sub"},"Role profile"), profileSections(a),
    h("h3",{class:"sub"},"Validate in the workshop"), valBox("agent", a.id));
  return [h("h2",{class:"sec"},"Agents \u00b7 " + d.name), h("p",{class:"lead"},"Each agent is described like a role: a trigger canvas for the work it does, its workflow from trigger to outcome, seven declarations that make it governable, and a role profile that becomes its instructions."), h("div",{class:"agwrap"}, h("div",{class:"agtop"}, list, main), flow, rest)];
}

/* ---------------- attendees ---------------- */
function attFocusTarget(f){
  var t = String(f || "").toLowerCase(); if (!t) return null;
  for (var i = 0; i < D.length; i++){ var d = D[i]; if ([d.name, d.short_name, d.journey_name, d.id].some(function(x){ return x && String(x).toLowerCase() === t; })) return {d:i}; }
  var u = UCS.filter(function(x){ return String(x.name || "").toLowerCase() === t || String(x.id || "").toLowerCase() === t; })[0];
  return u ? {uc:u} : null;
}
function renderAttendees(){
  var A = BP.attendees || {}, P = arr(A.people), cust = String(M.short || M.customer || "");
  var orgs = [];
  P.forEach(function(p){ var o = p.org || "Other"; if (orgs.indexOf(o) < 0) orgs.push(o); });
  orgs.sort(function(a, b){ function r(o){ return o === cust || o === M.customer ? 0 : (o === "Microsoft" ? 1 : 2); } return r(a) - r(b); });
  var map = D.map(function(d, i){ var n = P.filter(function(p){ return arr(p.focus).some(function(f){ var t = attFocusTarget(f); return t && ((t.d === i) || (t.uc && t.uc.domain === d.id)); }); }).length; return [d, i, n]; }).filter(function(x){ return x[2] > 0; });
  var out = [h("h2",{class:"sec"}, A.title || "Attendees and their contributions"),
    h("p",{class:"lead"}, [A.date, A.place].filter(Boolean).join(" \u00b7 "), " ", evPills(A.src)),
    A.note ? h("p",{class:"note"}, A.note) : null,
    h("div",{class:"idstrip"}, h("span",{class:"pill acc"}, P.length + " attendees"), orgs.map(function(o){ return h("span",{class:"pill"}, o + " \u00b7 " + P.filter(function(p){ return (p.org || "Other") === o; }).length); }),
      h("span",{class:"pill"}, P.reduce(function(s0, p){ return s0 + arr(p.contributions).length; }, 0) + " contributions"))];
  if (map.length) out.push(h("h3",{class:"sub"},"Who shaped which journey"), h("div",{class:"btnrow"}, map.map(function(x){ return h("button",{type:"button",class:"optchip",style:"--d:" + x[0].color,onclick:function(){ go("journeys",{d:x[1]}); }}, h("span",{class:"dot",style:"background:" + x[0].color}), " " + x[0].name + " \u00b7 " + x[2]); })));
  orgs.forEach(function(o){
    var ppl = P.filter(function(p){ return (p.org || "Other") === o; });
    out.push(h("h3",{class:"sub"}, o + " \u00b7 " + ppl.length));
    out.push(h("div",{class:"people"}, ppl.map(function(p){
      return h("article",{class:"person"},
        h("div",{class:"ph2"}, h("div",{class:"av2" + (o === "Microsoft" ? " ms" : ""),"aria-hidden":"true"}, initials(p.name)), h("div",null, h("h4",null, p.name || TBC), h("div",{class:"role"}, p.role || TBC), (p.where || p.team) ? h("div",{class:"note"}, [p.where, p.team].filter(Boolean).join(" \u00b7 ")) : null)),
        arr(p.focus).length ? h("div",{class:"tags"}, p.focus.map(function(f){ var t = attFocusTarget(f); return t ? h("button",{type:"button",class:"pill linkp",onclick:function(){ if (t.uc) openUseCase(t.uc); else go("journeys",{d:t.d}); }}, f) : h("span",{class:"pill"}, f); })) : null,
        arr(p.contributions).length ? h("ul",{class:"clean contrib"}, p.contributions.filter(Boolean).map(function(c){
          var o = typeof c === "object" ? c : {text:String(c)}, own = srcList(o.src), src = own.length ? own : srcList(p.src);
          return h("li",null, o.text || o.name || "", o.at ? h("span",{class:"tstamp",title:"Time in the recording"}, " " + o.at) : null, " ",
            src.length ? evPills(src) : h("span",{class:"pill open"},"No evidence yet"), own.length || !src.length ? null : h("span",{class:"note"}," (session)"));
        })) : null,
        p.quote ? h("blockquote",{class:"quote"}, "\u201c" + p.quote + "\u201d") : null,
        h("div",null, evPills(p.src)));
    })));
  });
  return out;
}

/* ---------------- Agent Factory: agent workflow, handover, steps ---------------- */
var STAGE_ORDER = ["hypothesis","validated","designed","ready","build","release","operate"];
function rdItems(){ var R = BP.it_readiness || {}; return arr(R.groups).reduce(function(acc, g){ return acc.concat(arr(g.items)); }, []); }
function rdStatus(it, def){ var n = note("val|ready|" + it.id); return String(n.status || it.status || def || "open").toLowerCase(); }
function readinessShare(stages){
  var its = rdItems().filter(function(it){ return !stages || stages.indexOf(String(it.stage || "build")) >= 0; });
  if (!its.length) return 0;
  return its.filter(function(it){ return rdStatus(it) === "done"; }).length / its.length;
}
function agentChecks(a){
  var st = String(note("val|agent|" + a.id).status || a.status || "hypothesis").toLowerCase();
  var c = canvasOf(a), decl = a.declarations || {};
  var nDecl = DECL.filter(function(x){ return has(decl[x[0]]); }).length;
  var vals = UCS.filter(function(u){ return arr(u.agents).some(function(n){ return agentByName(n) === a; }); }).map(valueOf).filter(Boolean);
  var vOk = vals.length && vals.every(function(v){ return v.status === "validated"; }) ? 1 : (vals.some(function(v){ return v.status === "validated" || v.status === "partly validated"; }) ? .5 : 0);
  /* Only generated dated planning evidence supplies this one criterion.
     Legacy F1/F2, raw approval and generic validation.cost notes cannot pass it. */
  var cost = financialEvidence(a) ? 1 : 0;
  var rd = readinessShare(["workshop","prototype","build"]);
  var full = has(c.trigger) && has(c.plan) && has(c.outcome) && has(c.data_sources);
  return {validated: st === "validated" || st === "adjusted" ? 1 : 0, canvas: full ? 1 : (has(c.trigger) || has(c.plan) ? .5 : 0),
          declarations: nDecl === 7 ? 1 : (nDecl > 0 ? .5 : 0), identity: a.identity ? 1 : 0, value: vOk, cost: cost,
          readiness: rd >= 1 ? 1 : (rd > 0 ? .5 : 0), owner: has(a.owner) ? 1 : 0};
}
function agentStage(a){
  var lc = String(a.lifecycle || "").toLowerCase();
  if (/live|in production|operat/.test(lc)) return "operate";
  if (/released|pilot/.test(lc)) return "release";
  if (/in build|building|develop|in test|prototyp/.test(lc)) return "build";
  var c = agentChecks(a), keys = Object.keys(c);
  if (keys.every(function(k){ return c[k] === 1; })) return "ready";
  if (c.validated && c.canvas === 1 && c.declarations === 1 && c.identity) return "designed";
  if (c.validated) return "validated";
  return "hypothesis";
}
function agentChip(a, small){
  var d = a._d || {};
  return h("button",{type:"button",class:"agchip" + (small ? " sm" : ""),style:"--d:" + (d.color || ACCENT),title:(nameOf(a)) + (d.name ? " \u00b7 " + d.name : ""),onclick:function(){ openAgent(a.id); }},
    idIcon(a, "aicon") || h("span",{class:"aicon ini",style:filled(d.color)}, initials(shortOf(a))), h("span",{class:"agn"}, shortOf(a)), isMvp(a) ? h("span",{class:"pill acc"},"MVP") : null);
}
function lifecycleRow(L){
  return h("div",{class:"chev"}, L.map(function(st, i){
    return h("div",{class:"chv"}, h("div",{class:"chn"}, h("span",{class:"no"}, String(i + 1)), st.name), logoRow(st.icons, 20), h("div",{class:"note"}, st.what || ""));
  }));
}
function factoryBoard(L){
  var ags = ALL.filter(function(a){ return !isFactory(a._d); });
  var by = {}; L.forEach(function(st){ by[st.id] = []; });
  ags.forEach(function(a){ var s0 = agentStage(a); (by[s0] || (by[s0] = [])).push(a); });
  return h("div",{class:"fboard",role:"list"}, L.map(function(st){
    var list = by[st.id] || [];
    return h("div",{class:"fcol2 st-" + st.id,role:"listitem"},
      h("div",{class:"fch"}, h("b",null, st.name), h("span",{class:"cnt"}, String(list.length))),
      h("div",{class:"fcards"}, list.length ? list.map(function(a){ return agentChip(a, true); }) : h("span",{class:"note"},"\u2014")),
      st.gate ? h("div",{class:"fgate"}, h("b",null,"Gate \u00b7 "), st.gate) : null);
  }));
}
function handoverTable(){
  var H = handoverDef(); if (!H.length) return null;
  var ags = ALL.filter(function(a){ return !isFactory(a._d) && (isMvp(a) || STAGE_ORDER.indexOf(agentStage(a)) >= 1); });
  if (!ags.length) return h("p",{class:"note"},"No agent is validated yet: the handover check fills once the workshop validates the MVP agents.");
  var mark = function(v){ return v === 1 ? h("span",{class:"hv ok",title:"Done"},"\u2713") : (v ? h("span",{class:"hv part",title:"Partly done"},"\u25d0") : h("span",{class:"hv no",title:"Missing"},"\u2715")); };
  return h("div",{class:"tscroll"}, h("table",{class:"t hand"},
    h("thead",null, h("tr",null, h("th",{scope:"col"},"Agent"), H.map(function(x){ return h("th",{scope:"col"}, x[1]); }), h("th",{scope:"col"},"Ready for build"))),
    h("tbody",null, ags.map(function(a){
      var c = agentChecks(a), ok = H.every(function(x){ return c[x[0]] === 1; });
      return h("tr",null, h("td",null, agentChip(a, true)), H.map(function(x){ return h("td",{class:"c"}, mark(c[x[0]])); }), h("td",null, h("span",{class:"pill " + (ok ? "val" : "open")}, ok ? "Planning checks met" : "Not yet"), c.cost !== 1 ? h("div",{class:"note"},"Financial handover gap") : null));
    }))));
}
function factorySteps(){
  var S = arr(FAC.steps); if (!S.length) return null;
  if (!(state.fstep >= 0 && state.fstep < S.length)) state.fstep = 0;
  var st = S[state.fstep];
  var fa = String(st.agent || "").split(" \u00b7 ").map(function(n){ return agentByName(n.replace(/\s*\(.*\)$/, "")); }).filter(Boolean);
  var LOOP = {plan:"Plan gates", dev:"DEV loop", gate:"Human-in-the-loop gate", ops:"OPS loop"};
  return [h("div",{class:"fsteps",role:"tablist","aria-label":"Idea-to-agent steps"}, S.map(function(x, i){
      return h("button",{type:"button",id:"factory-tab-" + i,role:"tab",class:"fstep lp-" + x.loop,
        "aria-controls":"factory-step-panel","aria-selected": i === state.fstep ? "true" : "false",tabindex:i === state.fstep ? "0" : "-1",
        onclick:function(){ activateTab("factory-tab-" + i,function(){ state.fstep = i; }); }}, h("span",{class:"n"}, x.id), h("span",null, x.name));
    })),
    h("div",{class:"fdetail lp-" + st.loop,id:"factory-step-panel",role:"tabpanel","aria-labelledby":"factory-tab-" + state.fstep},
      h("div",{class:"fdh"}, h("b",null, st.id + " \u00b7 " + st.name), h("span",{class:"pill"}, LOOP[st.loop] || st.loop || "")),
      h("p",null, st.what || ""),
      h("div",{class:"grid2"},
        h("div",null,
          fa.length ? [h("div",{class:"small-lbl"},"Factory agent"), h("div",{class:"btnrow"}, fa.map(function(a){ return agentChip(a); }))] : null,
          arr(st.tools).length ? [h("div",{class:"small-lbl"},"Microsoft and GitHub"), h("ul",{class:"clean tooll"}, st.tools.map(function(t){ return h("li",null, logo(t[0], 22), h("span",null, t[1])); }))] : null),
        h("div",null,
          h("div",{class:"callout"}, h("b",null,"Gate \u00b7 "), st.gate || TBC),
          st.evidence ? h("p",null, h("b",null,"Evidence: "), st.evidence) : null,
          arr(st.cat).length ? [h("div",{class:"small-lbl"},"CAT agent skills"), h("div",{class:"btnrow"}, st.cat.map(function(c){ return h("span",{class:"catc"}, c); }))] : null,
          arr(st.superpowers).length ? [h("div",{class:"small-lbl"},"Superpowers skills (optional)"), h("div",{class:"btnrow"}, st.superpowers.map(function(c){ return h("code",{class:"spc"}, c); }))] : null,
          st.customer ? h("p",{class:"note"}, h("b",null,"At " + (M.short || "the customer") + ": "), st.customer) : null)))];
}
function renderFactorySections(){
  if (!FAC) return [];
  var L = arr(FAC.lifecycle), fd = facDom(), out = [];
  out.push(h("h3",{class:"sub fach"}, logoRow(["github","ghcopilot","copilotstudio"], 20), FAC.title || "Agent Factory"));
  if (FAC.intro) out.push(h("p",{class:"lead"}, FAC.intro, evPills(FAC.src)));
  if (L.length){
    out.push(h("h3",{class:"sub"},"Agent workflow: from hypothesis to handover and production"), lifecycleRow(L));
    out.push(h("p",{class:"note"},"Where each agent of this blueprint stands. The stage follows the workshop verdicts, the canvas and declarations, the identity, the value case, the cost model and IT readiness, so it moves live during the workshop."));
    out.push(factoryBoard(L));
    out.push(h("div",{class:"btnrow"},pageLink("plan")));
  }
  out.push(h("h3",{class:"sub"},"Ready to hand over to build"), handoverTable());
  var steps = factorySteps();
  if (steps) out.push(h("h3",{class:"sub"},"Idea to agent: step by step"), steps);
  if (arr(FAC.controls).length) out.push(h("h3",{class:"sub"},"DevSecOps controls"), h("ul",{class:"clean ctrl"}, FAC.controls.map(function(c){ return h("li",null, logosFor(c, 16, 1), String(c)); })));
  if (arr(FAC.pyramid).length) out.push(h("h3",{class:"sub"},"Evaluation pyramid"), h("div",{class:"pyr"}, FAC.pyramid.slice().reverse().map(function(r, i, all){
    return h("div",{class:"pyrow",style:"--w:" + (52 + 48 * (all.length - 1 - i) / Math.max(1, all.length - 1)) + "%"}, h("b",null, r[0] + " \u00b7 " + r[1]), h("span",null, r[2]), h("em",null, r[3] + " \u00b7 " + r[4]));
  })));
  var roles = arr(FAC.roles).map(function(r){ return [AG[r.id], r.decides]; }).filter(function(x){ return x[0]; });
  if (roles.length) out.push(h("h3",{class:"sub"},"Factory roles: people decide, agents prepare"), h("div",{class:"roleg"}, roles.map(function(x){
    var a = x[0]; return h("button",{type:"button",class:"rolec",onclick:function(){ openAgent(a.id); }}, idIcon(a, "aicon lg") || h("span",{class:"aicon lg ini",style:filled((a._d || {}).color)}, initials(shortOf(a))), h("b",null, nameOf(a)), h("small",null, a.capability || a.mission || ""), h("span",{class:"note"}, h("b",null,"Decides: "), x[1]));
  })));
  if (arr(FAC.phases).length) out.push(h("h3",{class:"sub"},"Roll-out"), h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Phase","When","What"].map(function(c){ return h("th",{scope:"col"}, c); }))), h("tbody",null, FAC.phases.map(function(p){ return h("tr",null, h("td",null, h("b",null, p[0])), h("td",null, p[1]), h("td",null, p[2])); })))));
  var res = arr(FAC.resources).filter(function(r){ return /^https:\/\//.test(r.url || ""); });
  if (res.length) out.push(h("h3",{class:"sub"},"Reusable accelerators"), h("ul",{class:"clean idrules"}, res.map(function(r){ return h("li",null, h("a",{href:r.url,target:"_blank",rel:"noopener"}, r.title || r.url)); })));
  if (FAC.superpowers_note) out.push(h("p",{class:"note"}, FAC.superpowers_note));
  return out;
}

/* ---------------- agent landing zone (CAF design areas; WAF, CAF and Responsible AI) ---------------- */
var LZ = BP.architecture && BP.architecture.landing_zone && typeof BP.architecture.landing_zone === "object" && !Array.isArray(BP.architecture.landing_zone) ? BP.architecture.landing_zone : null;
var LZ_ZONE = {govern:"Environment-group rules and data policies per stage", sec:"Data classes agreed per stage", ops:"DEV, TEST and PROD created from one template", acc:"A lead agent and a human owner per journey", safe:"Promotion only through the Agent Factory"};
function lzZones(){
  var z = arr(LZ && LZ.lz); if (z.length) return z;
  return D.filter(function(d){ return !isFactory(d); }).map(function(d, i){ return {id:"F" + (i + 1), domain:d.id, stages:{DEV:"later", TEST:"later", PROD:"later"}, classes:[]}; });
}
function lzArea(id){ if (!LZ) return null; var a = (LZ.areas || {})[id]; if (a) return a; return lzZones().filter(function(z){ return z.id === id; })[0] || null; }
function lzApplies(id){ var a = lzArea(id) || {}; return a.domain ? (a.applies || LZ.zone_applies || LZ_ZONE) : (a.applies || {}); }
function lzLabel(id){ var a = lzArea(id) || {}; if (a.domain){ var d = domById(a.domain) || {}; return "F \u00b7 " + (d.name || a.domain); } return (a.letter ? a.letter + " \u00b7 " : "") + (a.title || id); }
var PRX = null;
function prIndex(){
  if (PRX) return PRX; PRX = {};
  ["waf","caf","rai"].forEach(function(fw){ var P = ((LZ || {}).principles || {})[fw] || {}; arr(P.items).forEach(function(it){ PRX[it[0]] = {fw:fw, short:P.short || fw.toUpperCase(), id:it[0], name:it[1], desc:it[2] || ""}; }); });
  return PRX;
}
function lzClass(c){ return arr(LZ && LZ.classes).filter(function(x){ return x[0] === c; })[0] || null; }
function lzTeam(z){ var d = domById(z.domain); return d ? (d.orchestrator ? [d.orchestrator] : []).concat(d.agents) : []; }
function lzSystems(){
  var seen = {}, out = [];
  D.forEach(function(d){ if (isFactory(d)) return; arr(d.systems).forEach(function(x){ var t = typeof x === "string" ? x : (x && x.name) || ""; if (t && !seen[t]){ seen[t] = 1; out.push(t); } }); });
  return out;
}
function lzIcon(a, x, y, z, col){
  var src = a && a.identity && a.identity.icon, g = s("g",{class:"lzag"}, s("title",null, nameOf(a) + (isMvp(a) ? " \u00b7 MVP" : "")));
  if (isMvp(a)) g.appendChild(s("rect",{x:x - 2.5, y:y - 2.5, width:z + 5, height:z + 5, rx:8, class:"mvpring"}));
  if (src && ICON_OK.test(src)) g.appendChild(s("image",{href:src, x:x, y:y, width:z, height:z}));
  else { col = hex(col, ACCENT); g.appendChild(s("rect",{x:x, y:y, width:z, height:z, rx:6, fill:col})); g.appendChild(s("text",{x:x + z / 2, y:y + z / 2 + 4, "text-anchor":"middle", class:"lzini",style:"fill:" + onColor(col)}, initials(shortOf(a)))); }
  return g;
}
function lzSvg(){
  var W = 1200, M0 = 16, G = 12, y = M0, kids = [], lens = state.lzLens, sel = state.lz || "P";
  function pick(id){ state.lz = id; state.lzLens = null; render(); var p = document.getElementById("lzpanel"); if (p && p.scrollIntoView) { try { p.scrollIntoView({behavior:"smooth", block:"nearest"}); } catch (e) {} } }
  function hot(id, x, y0, w, hh, body, cls){
    var on = lens ? Object.prototype.hasOwnProperty.call(lzApplies(id), lens) : false;
    var g = s("g",{class:"lzhot" + (cls ? " " + cls : "") + (id === sel && !lens ? " sel" : "") + (lens ? (on ? " on" : " off") : ""), "data-lz":id, role:"button", tabindex:"0", "aria-label":lzLabel(id)});
    g.appendChild(s("rect",{x:x, y:y0, width:w, height:hh, rx:10, class:"lzbox"}));
    add(g, body);
    g.addEventListener("click", function(){ pick(id); });
    g.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " "){ e.preventDefault(); pick(id); } });
    return g;
  }
  function areaBody(id, x, y0, w, hh, noSub){
    var a = lzArea(id) || {}, out = [], tx = x + 12, lw = arr(a.logos).slice(0, 3).length * 27 + 8;
    if (a.letter){ out.push(s("circle",{cx:x + 22, cy:y0 + 22, r:12, class:"lzbadge"}), s("text",{x:x + 22, y:y0 + 26.5, "text-anchor":"middle", class:"lzbadget"}, a.letter)); tx = x + 42; }
    var lines = wrapWords(a.label || a.title || id, Math.max(9, Math.floor((x + w - tx - 10) / 7.4)), w < 200 ? 3 : 2);
    lines.forEach(function(t, i){ out.push(s("text",{x:tx, y:y0 + 22 + i * 15, class:"lzt"}, t)); });
    if (a.sub && !noSub && hh > 70){
      var sl = wrapWords(a.sub, Math.max(10, Math.floor((w - 24 - (hh < 120 ? lw : 0)) / 6.1)), lines.length === 1 && hh >= 90 ? 2 : (w < 200 ? 3 : 1));
      sl.forEach(function(t, i){ out.push(s("text",{x:x + 12, y:y0 + 28 + lines.length * 15 + i * 13, class:"lzs"}, t)); });
    }
    arr(a.logos).slice(0, 3).forEach(function(k, i){ var L = LOGO[k]; if (L && IMG_OK.test(L.uri || "")) out.push(s("image",{href:L.uri, x:x + w - 32 - i * 27, y:y0 + hh - 32, width:22, height:22})); });
    return out;
  }
  var r1 = ["A","B","C","J"].filter(lzArea);
  if (r1.length){ var w1 = (W - 2 * M0 - (r1.length - 1) * G) / r1.length; r1.forEach(function(id, i){ var x = M0 + i * (w1 + G); kids.push(hot(id, x, y, w1, 92, areaBody(id, x, y, w1, 92))); }); y += 92 + 14; }
  var r2 = ["D1","D2","D3","D4"].filter(lzArea);
  if (r2.length){
    kids.push(hot("D", M0, y, W - 2 * M0, 128, [s("text",{x:M0 + 14, y:y + 22, class:"lzh"}, "D \u00b7 " + ((lzArea("D") || {}).title || "Platform landing zone"))], "cont"));
    var w2 = (W - 2 * M0 - 24 - (r2.length - 1) * 10) / r2.length;
    r2.forEach(function(id, i){ var x = M0 + 12 + i * (w2 + 10); kids.push(hot(id, x, y + 34, w2, 82, areaBody(id, x, y + 34, w2, 82))); });
    y += 128 + 14;
  }
  var zones = lzZones(), hasH = !!lzArea("H"), hasI = !!lzArea("I"), sideW = 150;
  var inner = W - 2 * M0 - 24, zx = M0 + 12;
  var zw = (inner - (hasH ? sideW + 10 : 0) - (hasI ? sideW + 10 : 0) - Math.max(0, zones.length - 1) * 8) / Math.max(1, zones.length);
  var cols = Math.max(1, Math.floor((zw - 12) / 32));
  var maxTeam = Math.max.apply(null, zones.map(function(z){ return lzTeam(z).length; }).concat([1]));
  var zh = Math.max(156, 72 + Math.ceil(maxTeam / cols) * 32 + 22), fh = zh + 46;
  kids.push(hot("F", M0, y, W - 2 * M0, fh, [s("text",{x:M0 + 14, y:y + 22, class:"lzh"}, "F \u00b7 " + ((lzArea("F") || {}).title || "Agent landing zones: one per journey"))], "cont"));
  var yy = y + 34;
  if (hasH){ kids.push(hot("H", zx, yy, sideW, zh, areaBody("H", zx, yy, sideW, zh), "side")); zx += sideW + 10; }
  zones.forEach(function(z){
    var d = domById(z.domain) || {}, col = hex(d.color, ACCENT), team = lzTeam(z), x = zx, body = [s("rect",{x:x, y:yy, width:zw, height:6, rx:3, fill:col})];
    wrapWords(d.short_name || d.name || z.id, Math.max(8, Math.floor((zw - 14) / 7.2)), 2).forEach(function(t, i){ body.push(s("text",{x:x + 8, y:yy + 22 + i * 14, class:"lzt"}, t)); });
    var pw = (zw - 16 - 8) / 3;
    ["DEV","TEST","PROD"].forEach(function(k, j){ var st = (z.stages || {})[k] || "later"; body.push(s("rect",{x:x + 8 + j * (pw + 4), y:yy + 48, width:pw, height:15, rx:7, class:"stg " + st}), s("text",{x:x + 8 + j * (pw + 4) + pw / 2, y:yy + 59, "text-anchor":"middle", class:"stgt"}, k), s("title",null, k + ": " + (((LZ || {}).stages || {})[st] || st))); });
    team.forEach(function(a, i){ body.push(lzIcon(a, x + 9 + (i % cols) * 32, yy + 72 + Math.floor(i / cols) * 32, 26, col)); });
    arr(z.classes).forEach(function(c, i){ var C = lzClass(c); body.push(s("circle",{cx:x + 13 + i * 14, cy:yy + zh - 11, r:5, fill:C ? C[2] : "#999"}, s("title",null, C ? C[1] + " data: " + C[3] : c))); });
    if (z.mvp) body.push(s("text",{x:x + zw - 8, y:yy + zh - 7, "text-anchor":"end", class:"lzmvp"}, typeof z.mvp === "string" ? z.mvp : "MVP"));
    kids.push(hot(z.id, x, yy, zw, zh, body, "zone"));
    zx += zw + 8;
  });
  if (hasI){
    var ix = W - M0 - 12 - sideW, ib = areaBody("I", ix, yy, sideW, zh, true), fd = facDom();
    if (fd){ var ft = (fd.orchestrator ? [fd.orchestrator] : []).concat(fd.agents), iy = yy + 30 + wrapWords((lzArea("I") || {}).label || (lzArea("I") || {}).title || "I", Math.max(9, Math.floor((sideW - 52) / 7.4)), 3).length * 15; ft.forEach(function(a, i){ ib.push(lzIcon(a, ix + 10 + (i % 4) * 32, iy + Math.floor(i / 4) * 32, 26, fd.color)); }); }
    kids.push(hot("I", ix, yy, sideW, zh, ib, "side fac"));
  }
  y += fh + 14;
  var r4 = ["E","G","X","R"].filter(lzArea), wt = {E:.42, G:.28, X:.15, R:.15};
  if (r4.length){
    var tot = r4.reduce(function(a0, id){ return a0 + wt[id]; }, 0), avail = W - 2 * M0 - (r4.length - 1) * G, x4 = M0;
    r4.forEach(function(id){
      var w = avail * wt[id] / tot, body = areaBody(id, x4, y, w, 132, id === "E");
      if (id === "E"){
        var sx = x4 + 12, sy = y + 60;
        lzSystems().slice(0, 18).forEach(function(t){ var lab = t.length > 30 ? t.slice(0, 29) + "\u2026" : t, tw = Math.min(w - 24, lab.length * 6.1 + 14); if (sx + tw > x4 + w - 10){ sx = x4 + 12; sy += 22; } if (sy > y + 124) return; body.push(s("rect",{x:sx, y:sy - 13, width:tw, height:18, rx:9, class:"syschip"}), s("text",{x:sx + 8, y:sy, class:"syst"}, lab)); sx += tw + 6; });
      }
      kids.push(hot(id, x4, y, w, 132, body)); x4 += w + G;
    });
    y += 132 + M0;
  }
  return s("svg",{viewBox:"0 0 " + W + " " + y, class:"lzsvg", role:"group", "aria-label":"Agent landing zone. Select an area for its details below."}, kids);
}
function lzLensBar(){
  var P = (LZ || {}).principles || {};
  return h("div",{class:"lzlens"}, ["waf","caf","rai"].map(function(fw){
    var p = P[fw]; if (!p) return null;
    return h("div",{class:"lzfw"}, h("span",{class:"pfw " + fw,title:p.name || ""}, p.short || fw.toUpperCase()),
      arr(p.items).map(function(it){ return h("button",{type:"button",class:"lzlb" + (state.lzLens === it[0] ? " on" : ""),"aria-pressed": state.lzLens === it[0] ? "true" : "false",title:it[2] || "",onclick:function(){ state.lzLens = state.lzLens === it[0] ? null : it[0]; render(); }}, it[1]); }));
  }), h("span",{class:"note"},"Select a principle to see where it applies."));
}
function stagePill(st){ var t = {now:"Exists today", next:"Next step", later:"Later", proposed:"Proposed", agreed:"Agreed"}[st] || st; return h("span",{class:"pill stgp " + st}, t); }
function lzPanel(){
  var lens = state.lzLens;
  if (lens){
    var p = prIndex()[lens] || {name:lens, fw:"", short:""};
    var ids = Object.keys(LZ.areas || {}).concat(lzZones().map(function(z){ return z.id; })).filter(function(id){ return Object.prototype.hasOwnProperty.call(lzApplies(id), lens); });
    return h("div",{class:"lzpanel",id:"lzpanel"}, h("h3",null, h("span",{class:"pfw " + p.fw}, p.short), " " + p.name), p.desc ? h("p",{class:"note"}, p.desc) : null,
      ids.length ? h("ul",{class:"clean prin"}, ids.map(function(id){ return h("li",null, h("button",{type:"button",class:"agentlink",onclick:function(){ state.lzLens = null; state.lz = id; render(); }}, h("b",null, lzLabel(id))), " \u2014 " + lzApplies(id)[lens]); })) : h("p",{class:"tbc"},"Not mapped yet"));
  }
  var id = state.lz || "P", a = lzArea(id); if (!a) return null;
  var A = BP.architecture || {}, P = prIndex(), ap = lzApplies(id);
  if (a.domain){
    var d = domById(a.domain) || {}, di = D.indexOf(d), team = lzTeam(a);
    var ucs = UCS.filter(function(u){ return u.domain === d.id; });
    return h("div",{class:"lzpanel",id:"lzpanel",style:"--d:" + (d.color || ACCENT)},
      h("div",{class:"lzph"}, h("span",{class:"lzbadge2",style:filled(d.color)}, "F"), h("div",null, h("h3",null, (d.name || a.domain) + " landing zone"), h("div",{class:"note"}, d.journey_name || "")), h("button",{type:"button",class:"btn",onclick:function(){ go("journeys",{d:di}); }},"Open journey")),
      h("div",{class:"btnrow"}, ["DEV","TEST","PROD"].map(function(k){ var st = (a.stages || {})[k] || "later"; return h("span",{class:"stgrow"}, h("b",null, k + " "), stagePill(st)); })),
      arr(a.classes).length ? [h("div",{class:"small-lbl"},"Data classes"), h("div",{class:"btnrow"}, a.classes.map(function(c){ var C = lzClass(c); return h("span",{class:"pill"}, h("span",{class:"dot",style:"background:" + (C ? C[2] : "#999")}), " " + (C ? C[1] + " \u00b7 " + C[3] : c)); }))] : null,
      h("div",{class:"small-lbl"},"Agents"), h("div",{class:"btnrow"}, team.map(function(x){ return agentChip(x, true); })),
      ucs.length ? [h("div",{class:"small-lbl"},"Use cases"), h("div",{class:"btnrow"}, ucs.map(function(u){ return h("button",{type:"button",class:"optchip",onclick:function(){ openUseCase(u); }}, u.id + " \u00b7 " + u.name + (u.mvp ? " \u00b7 MVP" : "")); }))] : null,
      h("div",{class:"small-lbl"},"Inherits from the platform"), ul(arr(LZ.common).length ? LZ.common : ["The guardrails of the platform landing zone D and the policies C"]),
      h("div",{class:"small-lbl"},"Principles applied"), h("ul",{class:"clean prin"}, Object.keys(ap).map(function(k){ var p0 = P[k] || {fw:"", short:"", name:k}; return h("li",null, h("span",{class:"pfw " + p0.fw}, p0.short), " ", h("b",null, p0.name), " \u2014 ", ap[k]); })), evPills(a.src));
  }
  var adrs = arr(A.decisions).filter(function(x){ return arr(x.areas).indexOf(id) >= 0 || arr(a.adrs).indexOf(x.id) >= 0; });
  var ods = arr(A.open_decisions).filter(function(x){ return arr(a.ods).indexOf(x.id) >= 0 || arr(x.areas).indexOf(id) >= 0; });
  var kids = id === "D" ? ["D1","D2","D3","D4"].filter(lzArea) : (id === "F" ? lzZones().map(function(z){ return z.id; }) : []);
  return h("div",{class:"lzpanel",id:"lzpanel"},
    h("div",{class:"lzph"}, a.letter ? h("span",{class:"lzbadge2"}, a.letter) : null, h("div",null, h("h3",null, a.title || id), a.sub ? h("div",{class:"note"}, a.sub) : null), logoRow(a.logos, 28)),
    a.status ? stagePill(a.status) : null,
    arr(a.bullets).length ? ul(a.bullets) : null,
    id === "P" ? h("div",{class:"grid3"}, ["waf","caf","rai"].map(function(fw){ var p0 = (LZ.principles || {})[fw]; return p0 ? h("div",null, h("div",{class:"small-lbl"}, h("span",{class:"pfw " + fw}, p0.short), " " + (p0.name || "")), h("ul",{class:"clean"}, arr(p0.items).map(function(it){ return h("li",null, h("b",null, it[1]), it[2] ? " \u2014 " + it[2] : ""); }))) : null; })) : null,
    kids.length ? h("div",{class:"btnrow"}, kids.map(function(k){ return h("button",{type:"button",class:"optchip",onclick:function(){ state.lz = k; render(); }}, lzLabel(k)); })) : null,
    Object.keys(ap).length ? [h("div",{class:"small-lbl"},"Principles applied"), h("ul",{class:"clean prin"}, Object.keys(ap).map(function(k){ var p0 = P[k] || {fw:"", short:"", name:k}; return h("li",null, h("span",{class:"pfw " + p0.fw}, p0.short), " ", h("b",null, p0.name), " \u2014 ", ap[k]); }))] : null,
    adrs.length ? [h("div",{class:"small-lbl"},"Decisions"), h("div",{class:"btnrow"}, adrs.map(function(x){ return h("button",{type:"button",class:"optchip",onclick:function(){ state.archTab = "decisions"; state.adr = x.id; render(); }}, x.id + " \u00b7 " + (x.title || "")); }))] : null,
    ods.length ? [h("div",{class:"small-lbl"},"Open decisions"), ul(ods.map(function(x){ return (x.id ? x.id + " \u00b7 " : "") + (x.question || x.title || ""); }))] : null,
    evPills(a.src));
}
function renderLandingZone(){
  return [h("h3",{class:"sub"}, LZ.title || "Agent landing zone"), LZ.intro ? h("p",{class:"note"}, LZ.intro, evPills(LZ.src)) : null, lzLensBar(),
    h("figure",{class:"lzfig"}, lzSvg(), LZ.caption ? h("figcaption",{class:"note"}, LZ.caption) : null),
    h("div",{class:"lzlegend"}, h("span",null, h("i",{class:"stg now"}), "Exists today"), h("span",null, h("i",{class:"stg next"}), "Next step"), h("span",null, h("i",{class:"stg later"}), "Later"), h("span",null, h("i",{class:"mvpr"}), "MVP agent"),
      arr(LZ.classes).map(function(c){ return h("span",null, h("i",{class:"dot",style:"background:" + c[2]}), c[1] + " data (" + c[3] + ")"); })),
    lzPanel(),
    arr(LZ.sources).length ? h("ul",{class:"clean idrules"}, LZ.sources.filter(function(x){ return /^https:\/\//.test(x.url || ""); }).map(function(x){ return h("li",null, h("a",{href:x.url,target:"_blank",rel:"noopener"}, x.title || x.url)); })) : null];
}
function adrStatus(x){ var n = note("val|adr|" + x.id).status; if (n === "validated") return "agreed"; if (n === "rejected" || n === "adjusted") return n; return String(x.status || "proposed").toLowerCase(); }
function renderDecisions(A){
  var list = arr(A.decisions), f = state.adrFilter || "all", counts = {};
  list.forEach(function(x){ var st = adrStatus(x); counts[st] = (counts[st] || 0) + 1; });
  var shown = list.filter(function(x){ return f === "all" || adrStatus(x) === f; });
  var out = [h("h3",{class:"sub"},"Architecture decision records"),
    h("p",{class:"note"},"Each decision with its context, consequences and alternatives. Decisions marked Hub canon are the Innovation Hub's standard proposals; the workshop agrees, adjusts or rejects them."),
    h("div",{class:"filters"}, [["all","All \u00b7 " + list.length]].concat(Object.keys(counts).map(function(k){ return [k, k.charAt(0).toUpperCase() + k.slice(1) + " \u00b7 " + counts[k]]; })).map(function(x){ return h("button",{type:"button",class:"tab","aria-pressed": f === x[0] ? "true" : "false",onclick:function(){ state.adrFilter = x[0]; render(); }}, x[1]); })),
    h("div",{class:"adrs"}, shown.map(function(x){
      var st = adrStatus(x), dec = x.decision && !/^(proposed|agreed|accepted)$/i.test(String(x.decision)) ? x.decision : null;
      return h("article",{class:"adr" + (state.adr === x.id ? " sel" : ""),id:"adr-" + x.id},
        h("div",{class:"adrh"}, h("b",null, x.id || ""), h("span",{class:"pill " + (st === "agreed" ? "val" : (st === "rejected" ? "int" : (st === "adjusted" ? "adj" : "open")))}, st), x.canon ? h("span",{class:"pill"},"Hub canon") : null),
        h("h4",null, x.title || ""),
        h("dl",{class:"kv"}, x.context ? [h("dt",null,"Context"), h("dd",null, x.context)] : null, dec ? [h("dt",null,"Decision"), h("dd",null, dec)] : null,
          x.rationale ? [h("dt",null,"Rationale"), h("dd",null, x.rationale)] : null, x.consequences ? [h("dt",null,"Consequences"), h("dd",null, x.consequences)] : null,
          x.alternatives ? [h("dt",null,"Alternatives"), h("dd",null, x.alternatives)] : null),
        arr(x.areas).length && LZ ? h("div",{class:"btnrow"}, x.areas.map(function(ar){ return lzArea(ar) ? h("button",{type:"button",class:"optchip",onclick:function(){ state.archTab = "lz"; state.lz = ar; render(); }}, lzLabel(ar)) : null; })) : null,
        evPills(x.src),
        h("details",{class:"adrv"}, h("summary",null,"Workshop verdict"), valBox("adr", x.id)));
    }))];
  var od = arr(A.open_decisions);
  if (od.length) out.push(h("h3",{class:"sub"},"Open decisions"), h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Id","Question","Owner","Note"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, od.map(function(x){ return h("tr",null, h("td",null, h("b",null, x.id || "")), h("td",null, x.question || x.title || "", evPills(x.src)), h("td",null, x.owner || TBC), h("td",null, x.note || "")); })))));
  if (arr(A.sources).length) out.push(h("h3",{class:"sub"},"Sources"), h("ul",{class:"clean note"}, A.sources.map(function(x){ return h("li",null, itemText(x)); })));
  return out;
}
function renderArchitecture(){
  var A = BP.architecture || {}, tabs = [];
  if (LZ) tabs.push(["lz","Landing zone"]);
  if (arr(A.principles).length || arr(A.layers).length || arr(A.patterns).length) tabs.push(["layers","Layers and integrations"]);
  if (arr(A.flows).length) tabs.push(["flows","Flows"]);
  if (arr(A.decisions).length || arr(A.open_decisions).length) tabs.push(["decisions","Decisions (ADRs)"]);
  if (tabs.length < 2 && !LZ) return renderArchitectureClassic();
  if (!tabs.some(function(t){ return t[0] === state.archTab; })) state.archTab = tabs[0][0];
  var out = [h("h2",{class:"sec"}, A.title || "Target architecture"), A.intro ? h("p",{class:"lead"}, A.intro, evPills(A.src)) : null,
    h("div",{class:"atabs",role:"tablist","aria-label":"Target architecture views"}, tabs.map(function(t){ return h("button",{
      type:"button",id:"architecture-tab-" + t[0],role:"tab",class:"atab","aria-controls":"architecture-panel",
      "aria-selected": t[0] === state.archTab ? "true" : "false",tabindex:t[0] === state.archTab ? "0" : "-1",
      onclick:function(){ activateTab("architecture-tab-" + t[0],function(){ state.archTab = t[0]; }); }}, t[1]); }))];
  var content = state.archTab === "lz" ? renderLandingZone()
    : state.archTab === "decisions" ? renderDecisions(A)
    : renderArchitectureClassic(state.archTab);
  return out.concat([h("section",{id:"architecture-panel",role:"tabpanel","aria-labelledby":"architecture-tab-" + state.archTab}, content)]);
}

/* ---------------- use case: Innovation Hub use-case template ---------------- */
var PROV = {workshop:"Workshop", board:"Whiteboard", transcript:"Transcript", customer:"Customer", microsoft:"Microsoft", hypothesis:"Hypothesis"};
function provList(x){
  if (!has(x)) return h("p",{class:"tbc"},"To complete in the workshop");
  if (typeof x === "string") return h("p",null, x);
  return h("ul",{class:"clean prov"}, arr(x).map(function(it){
    if (Array.isArray(it) && it.length === 2) return h("li",null, h("span",{class:"ptag pt-" + it[0]}, it[0] === "customer" ? (M.short || PROV.customer) : (PROV[it[0]] || it[0])), " ", String(it[1]));
    return h("li",null, itemText(it));
  }));
}
function scaleRow(sc, lo, hi){ var n = Math.round(+sc || 0); return h("div",{class:"scale"}, [1,2,3,4,5].map(function(i){ return h("span",{class: i === n ? "on" : null}, String(i)); }), h("em",null, lo + " \u00b7 " + hi)); }
function ucDetail(u){
  var d = domById(u.domain) || {}, v = score(u.value), f = score(u.feasibility);
  var ags = arr(u.agents).map(agentByName).filter(Boolean);
  var SC = BP.uc_scales || {};
  var fld = function(title, hint, body){ return h("div",{class:"fld"}, h("h5",null, title, hint ? h("small",null, " \u2014 " + hint) : null), body); };
  var txt = function(x){ return has(x) ? (Array.isArray(x) ? ul(x) : h("p",null, String(x))) : h("p",{class:"tbc"},"To complete in the workshop"); };
  var tech = [u.tech_fit, u.tech_option].concat(ags.map(function(a){ return a.technology || ""; })).join(" ");
  var tf = String(u.timeframe || "");
  var figs = arr(u.figures);
  var head = h("div",{class:"uchead",style:"--d:" + (d.color || ACCENT)},
    h("span",{class:"n",style:filled(d.color)}, String(u.id)), h("h2",null, u.name || ""),
    h("span",{class:"pill d"}, d.name || ""), h("span",{class:"pill"}, quadrant(v, f) + " \u00b7 V" + v + " / F" + f), u.mvp ? h("span",{class:"pill acc"},"MVP candidate") : null,
    statusPill(note("val|uc|" + u.id).status || u.status), ags.length ? h("span",{class:"btnrow",style:"margin:0"}, ags.map(function(a){ return agentChip(a, true); })) : null);
  var general = h("section",{class:"ucs"}, h("div",{class:"bar gen"},"General"), h("div",{class:"tpl two"},
    h("div",null, fld("Problem to solve or opportunity to realise", "the challenge and how it is solved today", provList(u.problem)),
      has(u.today) ? fld("How it is solved today", null, provList(u.today)) : null,
      has(u.pain) ? fld("Pain points raised in the workshop", null, provList(u.pain)) : null),
    h("div",null, fld("What is the idea?", "the use-case description", txt(u.idea || u.description)), has(u.idea_points) ? ul(u.idea_points) : null)));
  var value = h("section",{class:"ucs"}, h("div",{class:"bar val"},"Value"), h("div",{class:"tpl"},
    fld("Business objective", null, txt(u.objective)),
    fld("Key results", "three to five measurable key results", has(u.key_results) ? ul(u.key_results) : (has(u.kpis) ? ul(u.kpis) : txt(null))),
    h("div",{class:"grid2"}, fld("Alignment to the strategy", null, txt(u.strategy)),
      fld("How does it generate business value?", null, h("div",null, scaleRow(u.value_score || v, SC.value_low || "1 = less than CHF 100k a year", SC.value_high || "5 = more than CHF 10M a year"), has(u.value_text) ? h("p",null, u.value_text) : null,
        figs.length ? h("div",{class:"fig"}, figs.map(function(x){ return [h("b",null, x.amount || ""), h("span",null, x.label || "", x.source ? h("span",{class:"note"}," \u00b7 " + x.source) : null)]; })) : null))),
    h("div",{class:"grid2"}, fld("Key personas", null, txt(u.personas)), fld("How appealing is the value proposition?", null, txt(u.appeal))),
    fld("Primary stakeholder accountable for the key results", null, h("p",null, h("b",null,"Role: "), u.stakeholder_role || TBC, h("br"), h("b",null,"Organisation: "), u.stakeholder_org || TBC))),
    ucValue(u));
  var feas = h("section",{class:"ucs"}, h("div",{class:"bar fea"},"Feasibility"), h("div",{class:"tpl"},
    fld("Technology fit", null, h("div",null, logosFor(tech, 22, 4), txt(u.tech_fit || (ags.length ? ags.map(function(a){ return a.technology; }).filter(Boolean).join("; ") : null)), has(u.tech_points) ? ul(u.tech_points) : null)),
    h("div",{class:"grid2"}, fld("Change resistance", null, txt(u.change_resistance || u.change)),
      fld("Business change-management timeframe", null, h("div",null, h("div",{class:"checks"}, arr(SC.timeframe).concat(arr(SC.timeframe).length ? [] : ["1\u20133 months","4\u20136 months","> 6 months"]).map(function(o){ return h("div",null, (tf === o ? "\u2612 " : "\u2610 ") + o); })), u.timeframe_note ? h("p",{class:"note"}, u.timeframe_note) : null))),
    h("div",{class:"grid2"}, fld("Implementation and operational risks", null, h("div",null, scaleRow(u.risk_score, SC.risk_low || "1 = high risk, more than ten parties", SC.risk_high || "5 = low risk, few parties"), has(u.risk_points) ? ul(u.risk_points) : (has(u.risks) ? ul(u.risks) : txt(null)))),
      fld("Are sufficient safeguards available?", null, h("div",null, txt(u.safeguards), has(u.safeguard_points) ? ul(u.safeguard_points) : null))),
    has(u.dependencies) ? fld("Dependencies", null, ul(u.dependencies)) : null));
  return h("div",{class:"ucdetail",id:"ucdetail"}, head, general, h("div",{class:"grid2 ucgrid"}, value, feas),
    (function(){ var risks = riskItems().filter(function(r){ return arr(r.use_cases).indexOf(u.id) >= 0; });
      return risks.length ? h("div",{class:"btnrow uc-risk-links"},h("b",null,"Risk register"),risks.map(function(r){ return riskLink(r.id); })) : null;
    })(),
    h("p",{class:"note"}, "Evidence: ", evPills(u.src) || "Microsoft hypothesis", u.source_note ? " \u00b7 " + u.source_note : ""), valBox("uc", u.id));
}

/* ---------------- IT readiness ---------------- */
var RSTAGE = {workshop:"Before the workshop", prototype:"Before the prototype", build:"Before the first build", pilot:"Before the pilot"};
function rBox(id, opts, def){
  var k = "val|ready|" + id, n = note(k), name = "r-" + String(id).replace(/\W/g,"_"), st = h("span",{class:"status",role:"status"});
  var cur = n.status || def || "open";
  return h("div",{class:"assbox"},
    h("div",{class:"opts",role:"radiogroup","aria-label":"Status of " + id}, opts.map(function(o){ var rid = name + "-" + o[0].replace(/\W/g,"_"); return h("label",{class:"opt",for:rid}, h("input",{type:"radio",id:rid,name:name,value:o[0],checked: cur === o[0] ? true : null,onchange:function(){ setNote(k,{status:o[0]}); st.textContent = "Saved"; }}), o[1]); })),
    h("input",{type:"text",class:"assnote","aria-label":"Note for " + id,placeholder:"Owner, date, note",value: n.note || null,oninput:function(e){ setNote(k,{note:e.target.value}); st.textContent = "Saved"; }}), st);
}
var R_OPTS = [["open","Open"],["in progress","In progress"],["done","Done"],["blocked","Blocked"]];
function rProgress(list, statusOf){ var done = list.filter(function(x){ return statusOf(x) === "done"; }).length; return h("span",{class:"rprog"}, h("span",{class:"bar2"}, h("i",{style:"width:" + (list.length ? Math.round(done / list.length * 100) : 0) + "%"})), h("span",{class:"note"}, done + " / " + list.length)); }
function renderReadiness(){
  var R = BP.it_readiness || {}, its = rdItems(), stOf = function(it){ return rdStatus(it); };
  var checks = arr(R.checks), qs = arr(R.questions), ds = arr(R.decisions);
  var stageOk = function(stages){ var l = its.filter(function(it){ return stages.indexOf(String(it.stage || "build")) >= 0; }); return l.length && l.every(function(it){ return stOf(it) === "done"; }); };
  var out = [h("h2",{class:"sec"}, R.title || "IT readiness"), R.intro ? h("p",{class:"lead"}, R.intro, evPills(R.src)) : null,
    h("div",{class:"vkpis"},
      vk("Preparation items", its.filter(function(it){ return stOf(it) === "done"; }).length + " / " + its.length, "done"),
      vk("Readiness checks", checks.filter(function(x){ return rdStatus(x) === "done"; }).length + " / " + checks.length, "passed"),
      vk("Questions", qs.filter(function(x){ return rdStatus(x) === "answered"; }).length + " / " + qs.length, "answered"),
      vk("Decisions", ds.filter(function(x){ return rdStatus(x) === "agreed"; }).length + " / " + ds.length, "agreed"),
      vk("Ready for the prototype", stageOk(["workshop","prototype"]) ? "Yes" : "Not yet", "items before the prototype"),
      vk("Ready for the first build", stageOk(["workshop","prototype","build"]) ? "Yes" : "Not yet", "the handover needs it"))];
  if (arr(R.groups).length){
    out.push(h("h3",{class:"sub"},"Preparation by area"));
    out.push(h("div",{class:"rgroups"}, R.groups.map(function(g, gi){
      var gl = arr(g.items);
      return h("details",{class:"acc rgroup",open: gi === 0 ? true : null},
        h("summary",null, logoRow(g.logos, 20) || h("span",{class:"n"}, String(gi + 1)), h("span",{class:"rgt"}, g.title || g.id), rProgress(gl, stOf)),
        h("div",{class:"bd"}, h("div",{class:"tscroll"}, h("table",{class:"t rt"}, h("thead",null, h("tr",null, ["Item","Why","Owner","When","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
          h("tbody",null, gl.map(function(it){ return h("tr",null, h("td",null, h("b",null, it.id + " "), it.item || ""), h("td",{class:"note"}, it.why || ""), h("td",null, it.owner || TBC), h("td",null, RSTAGE[it.stage] || it.stage || ""), h("td",null, rBox(it.id, R_OPTS, it.status))); }))))));
    })));
  }
  if (checks.length){
    out.push(h("h3",{class:"sub"},"Readiness check"));
    [["technical","Technical readiness"],["functional","Functional readiness"]].forEach(function(k){
      var l = checks.filter(function(x){ return (x.kind || "technical") === k[0]; }); if (!l.length) return;
      out.push(h("div",{class:"small-lbl"}, k[1]), h("div",{class:"tscroll"}, h("table",{class:"t rt"}, h("thead",null, h("tr",null, ["Check","Test","Evidence","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
        h("tbody",null, l.map(function(x){ return h("tr",null, h("td",null, h("b",null, x.id + " "), logosFor(x.check + " " + x.test, 16, 2), x.check || ""), h("td",null, x.test || ""), h("td",{class:"note"}, x.evidence || ""), h("td",null, rBox(x.id, [["open","Open"],["done","Passed"],["blocked","Failed"]], x.status))); })))));
    });
  }
  if (arr(R.workstation).length) out.push(h("h3",{class:"sub"}, logoRow(["vscode","ghcopilot","github"], 20), "Developer workstation"), h("div",{class:"tscroll"}, h("table",{class:"t rt"}, h("thead",null, h("tr",null, ["Check","Expected","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, R.workstation.map(function(x){ return h("tr",null, h("td",null, h("b",null, x.id + " "), h("code",null, x.check || "")), h("td",null, x.expected || ""), h("td",null, rBox(x.id, [["open","Open"],["done","Passed"],["blocked","Failed"]], x.status))); })))));
  if (qs.length){
    out.push(h("h3",{class:"sub"},"Questions for the architecture design workshop"));
    var groups = []; qs.forEach(function(q){ var gname = q.group || "Questions"; if (groups.indexOf(gname) < 0) groups.push(gname); });
    groups.forEach(function(gname){ var l = qs.filter(function(q){ return (q.group || "Questions") === gname; });
      out.push(h("div",{class:"small-lbl"}, gname), h("div",{class:"tscroll"}, h("table",{class:"t rt"}, h("thead",null, h("tr",null, ["Question","Who answers","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
        h("tbody",null, l.map(function(q){ return h("tr",null, h("td",null, h("b",null, q.id + " "), q.question || ""), h("td",null, q.who || TBC), h("td",null, rBox(q.id, [["open","Open"],["answered","Answered"]], q.status))); })))));
    });
  }
  if (ds.length) out.push(h("h3",{class:"sub"},"Decisions to take"), h("div",{class:"tscroll"}, h("table",{class:"t rt"}, h("thead",null, h("tr",null, ["Decision","Options","Recommendation","Owner","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, ds.map(function(x){ return h("tr",null, h("td",null, h("b",null, x.id + " "), x.decision || ""), h("td",null, x.options || ""), h("td",null, x.recommendation || ""), h("td",null, x.owner || TBC), h("td",null, rBox(x.id, [["open","Open"],["agreed","Agreed"]], x.status))); })))));
  var CP = R.control_plane || {};
  if (arr(CP.options).length) out.push(h("h3",{class:"sub"},"Engineering control plane"), h("div",{class:"cpopts"}, CP.options.map(function(o){
    return h("div",{class:"cpo"}, h("div",{class:"cph"}, h("span",{class:"n"}, o.id || ""), h("b",null, o.name || ""), logoRow(o.logos, 22)), h("dl",{class:"kv"}, h("dt",null,"Fits when"), h("dd",null, o.fits || TBC), h("dt",null,"Strengths"), h("dd",null, o.strengths || TBC), h("dt",null,"Watch"), h("dd",null, o.watch || TBC)));
  })), arr(CP.criteria).length ? h("div",{class:"btnrow"}, h("span",{class:"small-lbl"},"Criteria"), CP.criteria.map(function(c){ return h("span",{class:"pill"}, c); })) : null);
  if (arr(R.environments).length) out.push(h("h3",{class:"sub"}, logoRow(["copilotstudio","powerapps"], 20), "Environment reference"), h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Environment","Purpose","Type","Region","Owner","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, R.environments.map(function(e){ return h("tr",null, h("td",null, h("b",null, e.name || "")), h("td",null, e.purpose || ""), h("td",null, e.type || ""), h("td",null, e.region || TBC), h("td",null, e.owner || TBC), h("td",null, e.status || "")); })))));
  var W = R.workshop || {};
  if (has(W.outcomes) || has(W.agenda)) out.push(h("h3",{class:"sub"}, W.title || "Architecture design workshop"), h("div",{class:"grid2"},
    h("div",null, h("div",{class:"small-lbl"},"Outcomes"), ul(W.outcomes), h("div",{class:"small-lbl"},"Who should attend"), h("div",{class:"btnrow"}, arr(W.who).map(function(x){ return h("span",{class:"pill"}, x); }))),
    h("div",null, h("div",{class:"small-lbl"},"Agenda"), h("table",{class:"t"}, h("tbody",null, arr(W.agenda).map(function(r){ return h("tr",null, h("td",{class:"nowrap"}, h("b",null, r[0])), h("td",null, r[1])); }))))));
  if (arr(R.timeline).length) out.push(h("h3",{class:"sub"},"Timeline"), h("div",{class:"tl2"}, R.timeline.map(function(r){ return h("div",{class:"tli"}, h("b",null, r[0]), h("span",null, r[1])); })));
  return out;
}

/* ---------------- business value and FinOps ---------------- */
function vk(label, value, sub){ return h("div",{class:"vkpi"}, h("span",{class:"kl"}, label), h("b",null, value), sub ? h("span",{class:"ks"}, sub) : null); }
function verdict(a){ var n = note("val|ass|" + a.id); return n.status || n.value !== undefined ? n : null; }
function assPill(a){
  var n = verdict(a), st = String((n && n.status) || a.status || "open").toLowerCase();
  var m = {validated:["val","Confirmed"], confirmed:["val","Confirmed"], adjusted:["adj","Adjusted"], rejected:["int","Rejected"], open:["open","Open"]}[st] || ["open","Open"];
  return h("span",{class:"pill " + m[0],"data-assumption-status":"val|ass|" + a.id}, m[1] + (n ? " \u00b7 in the workshop" : ""));
}
function syncAssumptionPeers(a, source){
  var k = "val|ass|" + a.id, saved = note(k);
  document.querySelectorAll(".assbox[data-assumption-key]").forEach(function(box){
    if (box === source || box.getAttribute("data-assumption-key") !== k) return;
    box.querySelectorAll('input[type="radio"]').forEach(function(input){ input.checked = input.value === saved.status; });
    var value = box.querySelector(".assval"), text = box.querySelector(".assnote"), status = box.querySelector(".status");
    /* Update only controls already permitted by the presentation gate. Never
       create a numeric input or recover a withheld amount while echoing notes. */
    if (value && !assumptionWithheld(a)) value.value = num(saved.value) ? String(saved.value) : "";
    if (text) text.value = saved.note || "";
    if (status) status.textContent = "Saved";
  });
  var next = assPill(a);
  document.querySelectorAll("[data-assumption-status]").forEach(function(pill){
    if (pill.getAttribute("data-assumption-status") !== k) return;
    pill.className = next.className; pill.textContent = next.textContent;
  });
}
function srcType(a){
  var t = {customer:"Customer-stated", measured:"Measured", benchmark:"Benchmark (prior)", hypothesis:"Hypothesis"}[a.source_type] || a.source_type || "Hypothesis";
  return t + (a.confidence ? " \u00b7 " + a.confidence + " confidence" : "");
}
function assBox(a, instance){
  /* DOM groups belong to a rendering instance; feedback still belongs to the
     stable assumption ID shared by the detail, portfolio and FinOps views. */
  var k = "val|ass|" + a.id, n = note(k), name = "a-" + String(a.id).replace(/\W/g,"_") + "-" + String(instance).replace(/\W/g,"_");
  var st = h("span",{class:"status",role:"status"});
  var opts = [["validated","Confirm"],["adjusted","Adjust"],["rejected","Reject"],["open","Open"]];
  function save(patch){ setNote(k,patch); st.textContent = "Saved"; syncAssumptionPeers(a,box); }
  var box = h("div",{class:"assbox","data-assumption-key":k},
    h("div",{class:"opts",role:"radiogroup","aria-label":"Workshop verdict for " + a.id}, opts.map(function(o){
      var rid = name + "-" + o[0];
      return h("label",{class:"opt",for:rid}, h("input",{type:"radio",id:rid,name:name,value:o[0],checked: n.status === o[0] ? true : null,onchange:function(){ save({status:o[0]}); }}), o[1]);
    })),
    assumptionWithheld(a) ? withheldAssumptionValue() : h("input",{type:"number",step:"any",class:"assval","aria-label":"Agreed value for " + a.id + (a.unit ? " in " + a.unit : ""),placeholder:"Agreed value" + (a.unit === "share" ? " (0-1)" : ""),value: num(n.value) ? String(n.value) : null,
      oninput:function(e){ var v = e.target.value; save({value: v === "" ? null : +v}); }}),
    h("input",{type:"text",class:"assnote","aria-label":"Note for " + a.id,placeholder:"Who said it, source",value: n.note || null,oninput:function(e){ save({note:e.target.value}); }}),
    st);
  return box;
}
function assTable(list, effect, instance){
  if (!list.length) return null;
  return h("div",{class:"tscroll"}, h("table",{class:"t asst"},
    h("thead",null, h("tr",null, ["Assumption","Base (low \u2013 high)","Source","Owner and question"].concat(effect ? ["Effect on NPV"] : []).concat(["Workshop"]).map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, list.map(function(a,i){
      var shown = presentedAssumption(a);
      return h("tr",null,
        h("td",null, h("b",null, a.id + (shown.rank && (previewAcknowledged || !portfolioPreview()) ? " \u00b7 #" + shown.rank : "")), h("div",null, shown.statement || ""), arr(shown.use_cases).length ? h("div",{class:"note"}, shown.use_cases.join(" \u00b7 ")) : null, shown.note ? h("div",{class:"note"}, shown.note) : null),
        h("td",{class:"nowrap"}, assumptionWithheld(a) ? withheldAssumptionValue() : [h("b",null, fmtA(shown.base, shown.unit)), h("div",{class:"note"}, fmtA(shown.low, shown.unit), " \u2013 ", fmtA(shown.high, shown.unit))]),
        h("td",null, srcType(shown), " ", evPills(shown.src)),
        h("td",null, shown.owner ? h("b",null, shown.owner) : null, shown.question ? h("div",{class:"note"}, shown.question) : null),
        effect ? h("td",{class:"nowrap"}, num(shown.swing_npv) && (previewAcknowledged || !portfolioPreview()) ? chf(shown.swing_npv, true) : TBC) : null,
        h("td",null, assPill(a), assBox(a,(instance || "assumptions") + "-" + i)));
    }))));
}
function assList(list, instance){
  return h("div",{class:"asslist"}, list.map(function(a,i){
    var shown = presentedAssumption(a);
    return h("div",{class:"assrow"},
      h("div",null, h("b",null, a.id), " ", shown.statement || "", " ", assPill(a), evPills(shown.src)),
      h("div",{class:"note"}, assumptionWithheld(a) ? withheldAssumptionValue() : ["Base ", h("b",null, fmtA(shown.base, shown.unit)), " (", fmtA(shown.low, shown.unit), " \u2013 ", fmtA(shown.high, shown.unit), ")"],
        " \u00b7 ", srcType(shown), shown.owner ? " \u00b7 owner: " + shown.owner : ""),
      shown.question ? h("div",{class:"note"}, "\u201c" + shown.question + "\u201d") : null,
      assBox(a,(instance || "case") + "-" + i));
  }));
}
function beText(be){
  if (!be) return null;
  var what = "\u201c" + (be.statement || be.assumption) + "\u201d";
  if (be.always_positive) return "Positive across the whole range of " + what + ".";
  if (be.always_positive === false) return "Negative across the whole range of " + what + ".";
  return num(be.value) ? "Breaks even when " + what + " is " + (be.unit === "share" ? pct(be.value, 1) : grp(be.value, be.value % 1 ? 1 : 0) + (be.unit ? " " + be.unit : "")) + "." : null;
}
function ucValue(u){
  var v = valueOf(u); if (!v) return null;
  var ry = v.range_year || {};
  return h("div",{class:"ucval"},
    h("h3",{class:"sub"}, "Business value"),
    h("div",{style:"display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px"}, h("span",{class:"pill " + (v.status === "validated" ? "val" : (v.status === "partly validated" ? "adj" : "open"))}, v.status || "hypothesis"),
      h("span",{class:"pill"}, (v.confidence || "low") + " confidence"), h("span",{class:"pill"}, (v.open_assumptions || 0) + " open assumptions")),
    h("div",{class:"vkpis"}, vk("Value per year", chf(ry.base, true), chf(ry.low, true) + " \u2013 " + chf(ry.high, true)), vk("Cash per year", chf(v.budget_year, true), "budget view"),
      vk("Cost per year", chf(v.cost_year, true), v.build ? "+ " + chf(v.build, true) + " build" : "run cost"), vk("NPV", chf(v.npv, true), "ROI " + (num(v.roi) ? pct(v.roi) : TBC)),
      vk("Payback", num(v.payback_months) ? v.payback_months.toFixed(1) + " months" : TBC, "undiscounted"), v.risk_year ? vk("Risk reduction", chf(v.risk_year, true), "per year, shown separately") : null),
    beText(v.break_even) ? h("p",{class:"note"}, beText(v.break_even)) : null,
    h("div",{class:"small-lbl"},"Value tree"),
    h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Lever","Driver","Category","Per year","Formula"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, arr(v.levers).map(function(l){
        return h("tr",{class: l.booked === false ? "muted" : null}, h("td",null, l.name, l.note ? h("div",{class:"note"}, l.note) : null), h("td",null, l.driver || ""),
          h("td",null, h("span",{class:"pill cat-" + (l.category || "capacity")}, l.category || "")),
          h("td",{class:"nowrap"}, chf(l.annual, true), l.booked === false ? h("div",{class:"note"}, l.rejected ? "left out: assumption rejected" : "shown, not booked") : null),
          h("td",null, h("code",{class:"fx"}, l.formula || "")));
      })))),
    v.agents_missing_cost ? h("p",{class:"note"}, "Cost not modelled yet for: " + arr(v.agents_missing_cost).join(", ")) : null,
    h("div",{class:"small-lbl"},"Assumptions to clarify in the workshop"),
    assList(arr(v.assumptions).map(function(id){ return ASSM[id]; }).filter(Boolean),"usecase-" + u.id));
}
function matrixLegend(){
  return h("p",{class:"note mxlegend"}, h("span",{class:"lg-size"}), "Bubble size = value per year (base case)", h("span",{class:"lg-dash"}), "dashed ring = value still a hypothesis \u00b7 dark ring = MVP candidate \u00b7 use cases without a value case keep the standard size");
}
function valueSection(){
  var T = presentedValue(VC.totals, portfolioPreview()) || {}, q = arr(VC.questions);
  var withheld = !previewAcknowledged && portfolioPreview();
  var rows = UCS.filter(function(u){ return valueOf(u); });
  /* The selected top-question subset is itself a ranking signal. Before viewer
     acknowledgement, present all public inputs in ID order, not a ranked subset. */
  var top = withheld ? arr(VC.assumptions).slice().sort(function(a,b){ return String(a.id).localeCompare(String(b.id)); })
    : q.map(function(id){ return ASSM[id]; }).filter(Boolean);
  var rest = withheld ? [] : arr(VC.assumptions).filter(function(a){ return q.indexOf(a.id) < 0; });
  return [
    h("h3",{class:"sub"},"Business value \u00b7 a hypothesis until the workshop confirms it"),
    h("p",{class:"note"}, "Per year at full adoption, in " + curr() + ". Economic view = cash + realised capacity; the budget view counts cash only; risk reduction is shown separately. NPV over " + (VC.horizon_years || 3) + " years at " + pct(VC.discount_rate, 1) + ". Ranges combine the effects of the individual assumptions."),
    h("div",{class:"vkpis"}, vk("Value per year", chf(T.economic_year, true), "economic view, base"), vk("Cash per year", chf(T.budget_year, true), "budget view"),
      vk("Cost per year", chf(T.cost_year, true), "run cost" + (T.build ? " + " + chf(T.build, true) + " build" : "")), vk("NPV", chf(T.npv, true), (VC.horizon_years || 3) + " years, economic view"),
      vk("NPV, cash only", chf(T.npv_budget, true), "budget view"), T.risk_year ? vk("Risk reduction", chf(T.risk_year, true), "per year, not in the views") : null),
    h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Use case","Value per year (range)","Cash per year","Cost per year","NPV","ROI","Payback","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, rows.map(function(u){
        var v = valueOf(u), ry = v.range_year || {};
        return h("tr",null,
          h("td",null, h("button",{type:"button",class:"agentlink",style:"font-weight:700;color:var(--ink)",onclick:function(){ openUseCase(u); }}, u.id + " " + u.name)),
          h("td",{class:"nowrap"}, h("b",null, chf(ry.base, true)), h("div",{class:"note"}, chf(ry.low, true) + " \u2013 " + chf(ry.high, true))),
          h("td",{class:"nowrap"}, chf(v.budget_year, true)),
          h("td",{class:"nowrap"}, chf(v.cost_year, true), v.build ? h("div",{class:"note"}, "+ " + chf(v.build, true) + " build") : null),
          h("td",{class:"nowrap"}, chf(v.npv, true)), h("td",{class:"nowrap"}, num(v.roi) ? pct(v.roi) : TBC),
          h("td",{class:"nowrap"}, num(v.payback_months) ? v.payback_months.toFixed(1) + " months" : TBC),
          h("td",null, h("span",{class:"pill " + (v.status === "validated" ? "val" : (v.status === "partly validated" ? "adj" : "open"))}, v.status || "hypothesis"), h("div",{class:"note"}, (v.confidence || "low") + " confidence \u00b7 " + (v.open_assumptions || 0) + " open")));
      })))),
    arr(VC.inputs_needed).length ? h("p",{class:"note"}, "Inputs still to collect: " + VC.inputs_needed.map(function(x){ return x.use_case + " (" + arr(x.assumptions).join(", ") + ")"; }).join("; ")) : null,
    h("h3",{class:"sub"},"Assumptions to clarify in the workshop"),
    h("p",{class:"note"}, (portfolioPreview() ? (previewAcknowledged ? "Provisional Preview-derived ranking and NPV effects, not recommendations. " : "Portfolio financial totals, ranking and NPV effects include Preview-derived cases and are withheld until acknowledgement; public case values are not a substitute portfolio total. ") : "Ranked by their effect on the NPV. ") + "Confirm, adjust (enter the agreed value) or reject each one with its owner. Verdicts are saved in this browser and exported from Discovery."),
    assTable(top, true,"value-top"),
    rest.length ? h("details",{class:"acc"}, h("summary",null, h("span",{class:"n"}, String(rest.length)), "More value assumptions"), h("div",{class:"bd"}, assTable(rest, true,"value-more"))) : null,
    arr(VC.discipline).length ? h("details",{class:"acc"}, h("summary",null, h("span",{class:"n"},"\u2713"), "Value discipline and sources"), h("div",{class:"bd"}, ul(VC.discipline),
      h("ul",{class:"clean idrules"}, arr(VC.sources).map(function(x){ return h("li",null, /^https:\/\//.test(x.url || "") ? h("a",{href:x.url,target:"_blank",rel:"noopener"}, x.title || x.url) : (x.title || "")); })))) : null];
}
function mvpValue(m){
  var u = UCS.filter(function(x){ return x.mvp && valueOf(x) && (!m.domain || x.domain === m.domain); })[0];
  if (!u) return null;
  var v = valueOf(u);
  return h("div",{class:"note",style:"margin:2px 0 6px"}, h("b",null,"Value \u00b7 "), chf((v.range_year || {}).base, true) + " per year (" + (v.status || "hypothesis") + ") \u00b7 cost " + chf(v.cost_year, true) + " per year");
}
function agentCell(a){
  var ag = AG[a.id];
  var label = h("span",{class:"anm",style:"display:inline-flex"}, ag ? idIcon(ag) : null, h("b",null, a.name || (ag ? nameOf(ag) : a.id)));
  return ag ? h("button",{type:"button",class:"agentlink",onclick:function(){ openAgent(a.id); }}, label) : label;
}
function renderFinops(){
  if (AF_PRESENT) return renderAgentFinops();
  if (!previewAcknowledged) return [h("h2",{class:"sec"},"FinOps \u00b7 what the agents cost"), h("p",{class:"note"},"Cost figures, purchase comparisons and guardrail settings require viewer acknowledgement. Missing budget evidence remains a gap."), valBox("finops","model")];
  var F = FO || {}, T = F.totals || {}, L = T.lines || {}, agents = arr(F.agents);
  var opts = arr(F.purchase_options), low = opts.filter(function(o){ return o.lowest; })[0];
  var max = Math.max.apply(null, agents.map(function(a){ return a.total_month || 0; }).concat([1]));
  var keys = [["credits","Copilot Credits"],["licences","Licences"],["azure","Azure"],["people","People"]];
  var out = [h("h2",{class:"sec"},"FinOps \u00b7 what the agents cost"),
    h("p",{class:"lead"}, F.intro || ("Cost per agent and month in " + curr() + ": Copilot Credits, licences, Azure and the people who run the agents. List prices and labelled assumptions, until the customer's price sheet and a usage baseline replace them.")),
    h("div",{class:"idstrip"}, h("span",{class:"pill acc"}, String(F.status || "hypothesis")),
      F.rates_version ? h("span",{class:"pill" + (F.verify ? " int" : "")}, "Rates " + F.rates_version + (num(F.rates_age_days) ? " \u00b7 " + F.rates_age_days + " days old" : "") + (F.verify ? " \u00b7 verify before sharing" : "")) : null,
      F.fx && num(F.fx.chf_per_usd) ? h("span",{class:"pill"}, "CHF per USD " + F.fx.chf_per_usd) : null,
      F.purchase && F.purchase.option ? h("span",{class:"pill"}, "Purchase model " + F.purchase.option + " (hypothesis)") : null,
      h("span",{class:"pill"}, agents.length + " agents modelled"), h("span",{class:"pill"}, "List prices, excl. VAT")),
    h("div",{class:"vkpis"}, vk("Run cost per month", chf(T.total_month), "all modelled agents"), vk("Run cost per year", chf(T.annual, true), "at full adoption"),
      vk("Build", chf(T.build, true), "one-time estimate"), vk("Copilot Credits", grp(T.credits_month), "per month \u00b7 " + chf(L.credits, true) + " pay-as-you-go"),
      vk("People share", T.total_month && num(L.people) ? pct(L.people / T.total_month) : TBC, "of the run cost"), low ? vk("Lowest credit option", chf(low.annual_chf, true), low.label + " (provisional comparison)") : null),
    h("h3",{class:"sub"},"Cost per agent and month"),
    h("div",{class:"tscroll"}, h("table",{class:"t finops-agents"},
      h("thead",null, h("tr",null, ["Agent","Harness and audience","Sessions","Credits","Credit cost","Licences","Azure","People","Total","Build","Unit cost"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, agents.map(function(a){
        var ln = a.lines || {}, un = a.unit || {};
        return h("tr",null, h("td",null, agentCell(a)), h("td",null, (a.harness || "") + " \u00b7 " + (a.audience || ""), a.coverage ? h("div",{class:"note"}, a.coverage) : null),
          h("td",{class:"nowrap"}, grp(a.sessions), h("div",{class:"note"}, pct(a.billable_share) + " billed")), h("td",{class:"nowrap"}, grp(a.credits_month)),
          h("td",{class:"nowrap"}, chf(ln.credits)), h("td",{class:"nowrap"}, chf(ln.licences)), h("td",{class:"nowrap"}, chf(ln.azure)), h("td",{class:"nowrap"}, chf(ln.people), num(a.run_hours_month) ? h("div",{class:"note"}, grp(a.run_hours_month) + " h") : null),
          h("td",{class:"nowrap"}, h("b",null, chf(a.total_month))), h("td",{class:"nowrap"}, chf(a.build, true)),
          h("td",{class:"nowrap"}, num(un.per_session) ? chf(un.per_session) + " per session" : TBC, num(un.per_outcome) ? h("div",{class:"note"}, chf(un.per_outcome) + " per " + (un.outcome || "outcome")) : null));
      })))),
    h("div",{class:"cbars",role:"img","aria-label":"Provisional cost composition per agent; unavailable totals omitted"}, agents.filter(function(a){ return num(a.total_month); }).map(function(a){
      var ln = a.lines || {};
      return h("div",{class:"cbar"}, h("span",null, a.name || a.id), h("div",{class:"track",style:"width:" + Math.max(4, Math.round((a.total_month || 0) / max * 100)) + "%"},
        keys.map(function(k){ var v = ln[k[0]] || 0; return v > 0 ? h("span",{class:"seg-" + k[0],style:"width:" + (v / (a.total_month || 1) * 100).toFixed(2) + "%",title:k[1] + " " + chf(v)}) : null; })),
        h("b",null, chf(a.total_month, true)));
    })),
    h("div",{class:"cblegend"}, keys.map(function(k){ return h("span",null, h("i",{class:"seg-" + k[0]}), k[1]); })),
    h("h3",{class:"sub"},"Where the credits come from"),
    h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Agent","Event","Credits each","Credits per month","Share"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, agents.map(function(a){ return arr(a.events).map(function(e, i){
        return h("tr",null, h("td",null, i === 0 ? h("b",null, a.name || a.id) : ""), h("td",null, e.label || e.event), h("td",{class:"nowrap"}, num(e.credits_each) ? grp(e.credits_each, e.credits_each % 1 ? 2 : 0) : ""),
          h("td",{class:"nowrap"}, grp(e.credits_month)), h("td",{class:"nowrap"}, a.credits_month && num(e.credits_month) ? pct(e.credits_month / a.credits_month) : TBC));
      }); })))),
    F.coverage_note ? h("p",{class:"note"}, F.coverage_note) : null,
    h("h3",{class:"sub"},"Purchase options for the credits"),
    h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Option","Per year","Versus pay-as-you-go","Utilisation","Conditions"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, opts.map(function(o){
        return h("tr",null, h("td",null, h("b",null, o.label), o.lowest ? h("span",{class:"pill val",style:"margin-inline-start:6px"},"lowest") : null), h("td",{class:"nowrap"}, chf(o.annual_chf)),
          h("td",{class:"nowrap"}, o.option === "payg" ? "\u2014" : num(o.vs_payg) ? (o.vs_payg > 0 ? "+" : "") + pct(o.vs_payg, 1) : TBC), h("td",{class:"nowrap"}, num(o.utilisation) ? pct(o.utilisation) : TBC), h("td",null, o.note || ""));
      })))),
    h("p",{class:"note"}, (F.purchase && F.purchase.note) || "A hypothesis: commit to packs or P3 only after a usage baseline; P3 purchases cannot be refunded."),
    arr(F.credit_scenarios).length ? [h("h3",{class:"sub"},"Sensitivity of the credit cost"),
      h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Case","Credits per month","Credit cost per month","Change"].map(function(c){ return h("th",{scope:"col"}, c); }))),
        h("tbody",null, [h("tr",null, h("td",null, h("b",null,"Base case")), h("td",{class:"nowrap"}, grp(T.credits_month)), h("td",{class:"nowrap"}, chf(L.credits)), h("td",null,"\u2014"))].concat(F.credit_scenarios.map(function(x){
          return h("tr",null, h("td",null, x.name), h("td",{class:"nowrap"}, grp(x.credits_month)), h("td",{class:"nowrap"}, chf(x.chf_month)),
            h("td",{class:"nowrap"}, num(x.change) ? (x.change > 0 ? "+" : "") + pct(x.change, 1) : TBC, num(x.change) ? h("span",{class:"chg " + (x.change > 0 ? "up" : "down"),style:"width:" + Math.min(80, Math.round(Math.abs(x.change) * 60)) + "px"}) : null));
        })))))] : null,
    arr(F.lessons).length ? [h("h3",{class:"sub"},"What the numbers say"), ul(F.lessons)] : null,
    arr(F.guardrails).length ? [h("h3",{class:"sub"},"Guardrails"),
      h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Control","Where","Setting","Owner"].map(function(c){ return h("th",{scope:"col"}, c); }))),
        h("tbody",null, F.guardrails.map(function(g){ return h("tr",null, h("td",null, h("b",null, g.control || "")), h("td",null, g.where || ""), h("td",null, g.setting || ""), h("td",null, g.owner || TBC)); }))))] : null,
    arr(F.tags).length ? [h("h3",{class:"sub"},"Cost allocation keys (from the agent identity)"),
      h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["agent-id","agent-name","schema","solution","journey","environment","cost-centre"].map(function(c){ return h("th",{scope:"col"}, h("code",null, c)); }))),
        h("tbody",null, F.tags.map(function(t){ return h("tr",null, ["agent-id","agent-name","schema","solution","journey","environment","cost-centre"].map(function(c){ return h("td",null, String(t[c] || "")); })); }))))] : null,
    arr(F.assumptions).length ? [h("h3",{class:"sub"},"Cost assumptions to clarify in the workshop"),
      h("p",{class:"note"}, "Confirm, adjust or reject with the owner; verdicts are exported with the workshop notes and merged into the next version of the cost model."),
      assTable(F.assumptions, false,"finops")] : null,
    h("h3",{class:"sub"},"Rates and sources"),
    arr(F.rates).length ? h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Rate","Value","Source"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, F.rates.map(function(r){ return h("tr",null, h("td",null, r.label || ""), h("td",null, r.value || ""), h("td",null, r.source || "")); })))) : null,
    arr(F.sources).length ? h("ul",{class:"clean idrules"}, F.sources.map(function(x){ return h("li",null, h("b",null, (x.id || "") + " "), /^https:\/\//.test(x.url || "") ? h("a",{href:x.url,target:"_blank",rel:"noopener"}, x.title || x.url) : (x.title || ""), x.date ? " \u00b7 checked " + x.date : ""); })) : null,
    F.note ? h("p",{class:"note"}, F.note) : null,
    h("h3",{class:"sub"},"Validate in the workshop"), valBox("finops","model")];
  return out;
}

/* ---------------- versioned Agent FinOps: projected derivative, never a model ---------------- */
function baselineMoney(value){
  if (!baselineObject(value) || value.amount === null || value.amount === undefined) return "Unavailable";
  return (typeof value.currency === "string" ? value.currency + " " : "") + value.amount;
}
function baselineAmount(value){
  var v = baselineObject(value) ? value : {};
  return h("div",{class:"baseline-money"}, h("b",null, baselineMoney(v)),
    h("span",{class:"note"}," \u00b7 " + (v.status || "unavailable") + (v.reason ? " \u00b7 " + v.reason : "")),
    v.synthetic ? h("span",{class:"pill open"},"synthetic \u00b7 draft only") : null,
    v.denominator !== undefined ? h("div",{class:"note"},"Denominator: " + v.denominator + " " + (v.denominator_unit || "") + " \u00b7 " + (v.period || "")) : null);
}
/* Native text nodes, including authored map keys and evidence references. Do not
   turn opaque URLs into active links, reconstruct withheld context or use HTML. */
function baselineTree(value){
  if (value === null || value === undefined) return h("span",{class:"note"},"Unavailable");
  if (Array.isArray(value)) return value.length ? h("ol",{class:"baseline-list"}, value.map(function(v){ return h("li",null, baselineTree(v)); })) : h("span",{class:"note"},"No projected entries; not zero cost or proof of completeness.");
  if (typeof value !== "object") return String(value);
  if (Object.prototype.hasOwnProperty.call(value,"amount") && typeof value.status === "string" &&
      (Object.prototype.hasOwnProperty.call(value,"basis") || value.status === "withheld")) return baselineAmount(value);
  return h("dl",{class:"baseline-fields"}, Object.keys(value).map(function(k){
    return [h("dt",null,k),h("dd",null,baselineTree(value[k]))];
  }));
}
function baselineDetails(title, value){
  return h("details",{class:"acc baseline-details"}, h("summary",null,title), h("div",{class:"bd"},baselineTree(value)));
}
function baselineContributions(value){
  var v = value || {};
  return h("div",{class:"baseline-contributions"},
    h("div",null,h("b",null,"Verified contributions"),baselineAmount(v.verified_subtotal)),
    h("div",null,h("b",null,"Provisional contributions \u00b7 draft only"),baselineAmount(v.provisional_subtotal)),
    h("p",{class:"note"},"Contributions are not a replacement full total; missing or withheld dependencies are not zero."));
}
function baselineScenario(id, sc){
  var metrics = ["per_run","per_success","per_outcome"], totals = [["annual_recurring","Annual recurring"],["one_time","One-time"],["first_year","First year"]];
  return h("section",{class:"panel baseline-scenario","data-scenario":id},
    h("h4",null,id + " \u00b7 twelve-month scenario"),
    h("div",{class:"grid3"},totals.map(function(k){ return h("div",null,h("b",null,k[1]),baselineAmount(sc[k[0]]),baselineContributions(sc[k[0]])); })),
    h("h5",null,"Unit economics \u00b7 supplied period metrics"),
    dataTable(["Basis","Per attempted run","Per successful run","Per confirmed outcome"],
      ["annual_recurring","first_year"].map(function(basis){
        var units = sc.unit_metrics && sc.unit_metrics[basis] || {};
        return [basis].concat(metrics.map(function(k){ return baselineAmount(units[k]); }));
      })),
    h("h5",null,"Monthly recurring \u00b7 no browser annualisation"),
    dataTable(["Month","Total","Verified contributions","Provisional contributions","Per run","Per success","Per outcome"],
      arr(sc.months).map(function(m){
        m = m || {};
        return [m.period || "Withheld",baselineAmount(m.total),baselineAmount(m.verified_subtotal),baselineAmount(m.provisional_subtotal)]
          .concat(metrics.map(function(k){ return baselineAmount(m[k]); }));
      }),"baseline-months"),
    baselineDetails("Projected line quantities, costs and pricing evidence", {
      months:arr(sc.months).map(function(m){ return {period:m && m.period,lines:m && m.lines}; }),
      one_time_lines:sc.one_time_lines
    }));
}
function baselineProposal(r){
  /* Reuse the free-form FinOps validation note, not a new feedback schema or a
     local owner-review object. The merge/rebuild remains an external new draft. */
  if (!r.agent_id) return h("p",{class:"note"},"Target withheld: obtain an appropriately projected report before proposing target-specific changes.");
  var key = "val|finops|baseline-" + r.agent_id, id = "v-finops-baseline-" + r.agent_id.replace(/\W/g,"_") + "-note";
  var st = h("span",{class:"status",role:"status"});
  return h("div",{class:"valbox baseline-proposal"},
    h("label",{for:id},h("b",null,"Workshop proposal \u00b7 input to a new draft only")),
    h("p",{class:"note"},"Saved locally; not approval. Does not change frozen model, results, review or readiness. Material changes require authoritative sources, a new version and external exact-target review."),
    h("textarea",{id:id,placeholder:"Proposed answer, missing evidence and responsible owner",
      oninput:function(e){ setNote(key,{note:e.target.value}); st.textContent = "Proposal saved locally; not financial approval"; }},note(key).note || ""),st);
}
function baselineMarkdown(r){
  function esc(v){ return String(v === null || v === undefined ? "Unavailable" : v)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/([\\`*_[\]()!#|])/g,"\\$1").replace(/\r?\n/g," / "); }
  var lines = ["# Agent FinOps \u2014 Preview derivative","",esc(FINOPS_NOTICE),"",
    "Not an authoritative model or approval. External review is not authenticated. Renew from authoritative sources for changed inputs or dates.",""];
  function detail(v, path){
    if (v && typeof v === "object") {
      var keys = Object.keys(v).sort();
      if (!keys.length) lines.push("- " + esc(path) + ": No projected entries; incomplete/withheld is not zero.");
      keys.forEach(function(k){ detail(v[k],path ? path + " / " + k : k); });
    } else lines.push("- " + esc(path) + ": " + esc(v));
  }
  detail(r,"report");
  return lines.join("\n") + "\n";
}
function renderAgentFinops(){
  var out = [h("h2",{class:"sec"},"Agent FinOps \u00b7 versioned baseline review"),
    h("p",{class:"lead"},"Preview planning derivatives, not authoritative baselines. External review is not authenticated. No budget, purchase, build or deployment permission. Core drafts and workshops continue with financial gaps.")];
  if (AF.error) return out.concat(h("p",{class:"callout baseline-error",role:"status"},AF.error));
  if (!previewAcknowledged) return out.concat(h("p",{class:"note"},"Financial figures, linked assumptions, proposals and financial exports are withheld until fresh viewer acknowledgement for this document. Reload resets acknowledgement."));
  out.push(h("p",{class:"note"},"Evaluation date: " + BP.agent_finops.as_of + " \u00b7 audience: " + BP.agent_finops.audience + ". " + BP.agent_finops.limitations));
  if (!AF.records.length) out.push(h("p",{class:"callout baseline-gap",role:"status"},"Financial handover gap: no projected records. Supply authoritative per-agent baselines, date, audience/scope, freeze and external review; rebuild. Missing records are not zero cost."));
  AF.records.forEach(function(r,i){
    var st = h("span",{class:"status",role:"status"}), identity = r.agent_id || "withheld-" + (i + 1);
    out.push(h("article",{class:"baseline-record","data-agent":r.agent_id || "withheld"},
      h("h3",{class:"sub"},r.agent_id ? r.agent_id + " \u00b7 " + (r.profile.name || "Agent baseline") : "Target withheld"),
      h("p",{class:"note"},r.notice),
      h("div",{class:"idstrip"},[r.maturity,r.mode,r.status,r.as_of,r.currency || "Currency unavailable",r.distribution].map(function(v){ return h("span",{class:"pill"},v); })),
      h("p",{class:"note"},r.limitations),
      h("h4",null,"Profile and discovery"),baselineTree(r.profile),
      baselineDetails("Baseline version and projected scope / discovery inputs",{baseline:r.baseline,context:r.context,scenario_inputs:r.scenario_inputs}),
      h("h4",null,"Scenarios \u00b7 low / expected / high"),
      ["low","expected","high"].map(function(id){ return r.scenarios[id] ? baselineScenario(id,r.scenarios[id]) : h("p",{class:"baseline-gap callout"},id + ": unavailable or withheld scenario; financial handover gap."); }),
      baselineDetails("Formulas and supplied rounding",r.formulas),
      h("h4",null,"Projected evidence"),h("p",{class:"note"},"Sources, applicable rates and FX as supplied. Provisional and synthetic contributions are draft only, not verified prices or actual provider quotes."),
      baselineDetails("Inspect projected sources, rates and FX",r.evidence),
      h("h4",null,"Validation and external review"),
      r.agent_id ? financialSummary(AG[r.agent_id]) : h("p",{class:"baseline-gap callout"},"Financial handover gap: target and review context withheld."),
      baselineDetails("Dated structural validation, pricing completeness and external review",r.handover),
      baselineDetails("Gaps and incomplete states",r.gaps),
      baselineProposal(r),
      h("h4",null,"Projected exports \u00b7 not a model or approval"),
      h("p",{class:"note"},"Downloads contain this already audience-projected report only. Internal private context is not shareable. Export proposals from Discovery as separate workshop feedback for a new draft, never a replacement frozen model."),
      h("div",{class:"btnrow"},
        h("button",{type:"button",class:"btn baseline-export",onclick:function(){
          if (previewAcknowledged && !AF.error) download(fileSlug() + "-" + identity + "-finops-report.json",JSON.stringify(r,null,2),"application/json",st);
        }},"Download projected report JSON"),
        h("button",{type:"button",class:"btn baseline-export",onclick:function(){
          if (previewAcknowledged && !AF.error) download(fileSlug() + "-" + identity + "-finops-report.md",baselineMarkdown(r),"text/markdown;charset=utf-8",st);
        }},"Download projected report Markdown"),pageLink("discovery"),st)));
  });
  return out;
}

/* ---------------- agent identity ---------------- */
function idStatus(a){
  var i = a.identity || {};
  var c = String(i.status_class || (isMvp(a) ? "mvp" : "")).toLowerCase();
  var lbl = i.status || (typeof a.mvp === "string" ? a.mvp : (a.mvp ? "MVP" : ""));
  if (!lbl) return null;
  var cls = c === "mvp" ? "pill acc" : (c === "validated" ? "pill val" : (c === "adjusted" ? "pill adj" : (c === "deferred" || c === "out-of-scope" ? "pill open" : "pill")));
  return h("span",{class:cls}, String(lbl));
}
function poText(){
  var po = IDN ? arr(IDN.po_areas) : [];
  if (!po.length) return "Process-owner area: the business area that owns the process the agent works in";
  return h("span",null, "Process-owner area: ", po.map(function(p, i){ return [i ? ", " : "", h("b",null, String(p.token || "")), p.owner ? " (" + p.owner + ")" : ""]; }),
    po.some(function(p){ return p.assumed; }) ? h("span",{class:"note"}," \u00b7 assumed, to be confirmed") : null);
}
function idFacts(a){
  var i = a.identity || {}, t = i.tokens || {};
  return [
    envOrder().map(function(e){ return [h("dt",null, e), h("dd",null, (i.names || {})[e] || h("span",{class:"tbc"},"\u2014"))]; }),
    t.po ? [h("dt",null,"Tokens"), h("dd",null, "PO ", h("b",null, String(t.po)), " \u00b7 Domain ", h("b",null, String(t.domain || "")), t.scope ? [" \u00b7 Scope ", h("b",null, String(t.scope))] : null)] : null,
    i.kind ? [h("dt",null,"Kind"), h("dd",null, String(i.kind))] : null,
    i.schema ? [h("dt",null,"Schema name"), h("dd",null, h("code",null, String(i.schema)))] : null,
    i.solution ? [h("dt",null,"Solution"), h("dd",null, h("code",null, String(i.solution)))] : null,
    i.repo ? [h("dt",null,"Repository folder"), h("dd",null, h("code",null, String(i.repo)))] : null,
    i.colour ? [h("dt",null,"Colour"), h("dd",null, h("span",{class:"dot",style:"background:" + hex(i.colour, "#888888")}), " " + i.colour + (i.contrast ? " \u00b7 glyph contrast " + i.contrast + ":1" : ""))] : null,
    i.glyph ? [h("dt",null,"Glyph"), h("dd",null, String(i.glyph))] : null
  ];
}
function idIconRow(a, big){
  var i = a.identity || {};
  return h("div",{class:"idicons"},
    envOrder().map(function(e){ var im = idEnvIcon(a, e, big ? "aicon xl" : "aicon lg"); return im ? h("figure",null, im, h("figcaption",null, e)) : null; }),
    i.outline && ICON_OK.test(i.outline) ? h("figure",null, h("span",{class:"odark" + (big ? "" : " sm")}, h("img",{class:"aicon",src:i.outline,alt:"","aria-hidden":"true"})), h("figcaption",null,"Outline")) : null);
}
function idPanel(a){
  var i = a.identity || {};
  return h("div",{class:"idpanel"},
    idIconRow(a, false),
    h("dl",{class:"kv"}, idFacts(a)),
    h("div",{class:"btnrow"}, h("button",{type:"button",class:"btn",onclick:function(){ go("identity"); }}, "Open the agent identity page"),
      i.short_description ? h("span",{class:"note"}, String(i.short_description)) : null));
}
function openIdentity(a, d){
  var i = a.identity || {};
  openDrawer(nameOf(a), (d ? (d.journey_name || d.name) + " \u00b7 " : "") + (i.kind || (a.role === "lead" ? "Lead agent" : "Agent")), [
    idStatus(a),
    h("div",{style:"height:10px"}),
    idIconRow(a, true),
    h("dl",{class:"kv"}, idFacts(a), a.name && a.name !== idName(a) ? [h("dt",null,"Working name"), h("dd",null, a.name)] : null),
    i.description ? h("p",{class:"note"}, String(i.description)) : null,
    AG[a.id] ? h("div",{class:"btnrow"}, h("button",{type:"button",class:"btn primary",onclick:function(){ closeDrawer(); go("agents",{d:D.indexOf(d), agent:a.id}); }}, "Open agent canvas")) : null
  ]);
}
function renderIdentity(){
  var I = IDN || {};
  var team = idTeam(), envs = idEnvs(), order = envOrder(), prod = prodEnv();
  var nonprod = envs.filter(function(e){ return e.name !== prod; });
  var maxLen = +I.max_length || 30;
  var out = [h("h2",{class:"sec"},"Agent identity"),
    h("p",{class:"lead"}, I.intro || ("One name, one colour and one icon family for every agent, so people recognise " + (M.short || M.customer || "the company") + "\u2019s agents in Teams, Microsoft 365 Copilot and Copilot Studio." + (nonprod.length ? " " + nonprod.map(function(e){ return e.name; }).join(" and ") + " carry a postfix and a coloured band; " + prod + " stays clean." : ""))),
    h("div",{class:"idstrip"},
      I.status ? h("span",{class:"pill acc"}, String(I.status)) : null,
      I.kit ? h("span",{class:"pill"}, String(I.kit)) : null,
      I.date ? h("span",{class:"pill"}, String(I.date)) : null,
      h("span",{class:"pill"}, team.length + " agents"),
      order.length ? h("span",{class:"pill"}, order.join(" \u00b7 ")) : null,
      I.validation ? h("span",{class:"pill " + (+I.validation.errors ? "int" : "val")}, (+I.validation.errors || 0) + " errors \u00b7 " + (+I.validation.warnings || 0) + " warnings") : null)];
  if (!team.length){ out.push(h("div",{class:"empty"}, h("b",null,"No agent identity yet."), h("p",null,"Build the blueprint together with the agent identity kit to show names, colours and icons here."))); return out; }
  var mvSorted = team.filter(function(t){ return isMvp(t.a); }).sort(function(x, y){ return String((x.a.identity || {}).status || x.a.mvp || "").localeCompare(String((y.a.identity || {}).status || y.a.mvp || "")); });
  var ex = mvSorted[0] || team[0];
  out.push(h("h3",{class:"sub"},"Naming rule"),
    h("div",{class:"idrule"},
      h("div",{class:"rulebox"}, h("code",null, I.rule || ("<PO> <Domain> [<Scope>]" + (nonprod.length ? " [" + nonprod.map(function(e){ return e.postfix || e.name; }).join(" | ") + "]" : ""))),
        h("p",{class:"note"}, prod + " carries no postfix \u00b7 at most " + maxLen + " characters \u00b7 technical names never carry an environment"),
        h("div",{class:"idex"}, order.map(function(e){ return h("div",{class:"exr"}, idEnvIcon(ex.a, e, "aicon md"), h("b",null, (ex.a.identity.names || {})[e] || ""), h("span",{class:"note"}, e)); }))),
      h("dl",{class:"kv"},
        h("dt",null,"PO"), h("dd",null, poText()),
        h("dt",null,"Domain"), h("dd",null,"What the agent does, in one or two words"),
        h("dt",null,"Scope"), h("dd",null,"Optional: a country, site or business unit when the same agent exists more than once"),
        h("dt",null,"Environment"), h("dd",null, nonprod.length ? nonprod.map(function(e){ return e.name; }).join(" and ") + " add a postfix and a coloured band; " + prod + " has none" : TBC),
        I.prefix ? [h("dt",null,"Technical names"), h("dd",null, "Publisher prefix ", h("code",null, I.prefix + "_"), I.solution_prefix ? [" \u00b7 solutions ", h("code",null, I.solution_prefix + "\u2026")] : null, I.prefix_note ? h("div",{class:"note"}, String(I.prefix_note)) : null)] : null)));
  var js = arr(I.journeys).length ? I.journeys : D.map(function(d){ return {id:d.id, name:d.journey_name || d.name, colour:d.color}; });
  out.push(h("h3",{class:"sub"},"Journey colours"),
    I.brand && I.brand.source ? h("p",{class:"note"}, "Colours from " + I.brand.source + ".") : null,
    h("div",{class:"swatches"}, js.map(function(j){
      var d = domById(j.id) || {}, c = hex(j.colour, d.color || ACCENT), g = onColor(c);
      return h("div",{class:"sw"},
        h("div",{class:"chip",style:"background:" + c + ";color:" + g}, h("b",null, j.id + " \u00b7 " + (j.name || d.journey_name || d.name || "")), h("span",null, j.po ? "PO area: " + j.po : "")),
        h("div",{class:"meta"}, h("code",null, c), j.colour_name ? h("span",null, String(j.colour_name)) : null, j.contrast ? h("span",{class:"note"}, j.contrast + ":1 with the glyph") : null));
    })),
    nonprod.length ? h("div",{class:"bands"}, order.map(function(e){
      var en = envs.filter(function(x){ return x.name === e; })[0] || {};
      var band = hex(en.band, null);
      return h("div",{class:"band"},
        h("div",{class:"bchip" + (band ? "" : " clean"),style: band ? filled(band) : null}, band ? e : e + " \u00b7 no band"),
        h("div",{class:"note"}, band ? [(en.band_name ? en.band_name + " \u00b7 " : "") + band, en.label_contrast ? " \u00b7 label " + en.label_contrast + ":1" : ""] : "Production stays clean: no postfix, no band"));
    })) : null);
  out.push(h("h3",{class:"sub"},"Agent family"),
    h("div",{class:"family"}, D.map(function(d){
      var mine = team.filter(function(t){ return t.d === d; });
      if (!mine.length) return null;
      var j = js.filter(function(x){ return x.id === d.id; })[0] || {};
      return h("div",{class:"fcol",style:"--fc:" + hex(j.colour, d.color)},
        h("div",{class:"fhead",style:"color:" + onColor(hex(j.colour, d.color))}, h("b",null, d.id + " \u00b7 " + (d.journey_name || d.name)), j.po ? h("span",null, "PO area: " + j.po) : null),
        mine.map(function(t){
          return h("button",{type:"button",class:"fitem",onclick:function(){ openIdentity(t.a, t.d); }},
            idIcon(t.a, "aicon md") || h("span",{class:"aicon md"}), h("span",{class:"fx"}, h("b",null, nameOf(t.a)), idStatus(t.a)));
        }));
    })));
  var mv = mvSorted;
  if (mv.length) out.push(h("h3",{class:"sub"},"MVP identity sheet"),
    h("div",{class:"mvpsheet"}, mv.map(function(t){
      var a = t.a;
      return h("div",{class:"mrow"},
        h("div",null, idStatus(a), h("h4",null, nameOf(a)), a.name && a.name !== idName(a) ? h("div",{class:"note"}, "Working name: " + a.name) : null, h("div",{class:"note"}, t.d.id + " \u00b7 " + (t.d.journey_name || t.d.name))),
        idIconRow(a, true),
        h("dl",{class:"kv"}, idFacts(a)));
    })));
  out.push(h("h3",{class:"sub"},"All names per environment"),
    h("div",{class:"tscroll"}, h("table",{class:"t idt"},
      h("thead",null, h("tr",null, h("th",{scope:"col"},"Agent"), order.map(function(e){ return h("th",{scope:"col"}, e); }), h("th",{scope:"col"},"Kind"), h("th",{scope:"col"},"Schema name"), h("th",{scope:"col"},"Length"), h("th",{scope:"col"},"Status"))),
      h("tbody",null, team.map(function(t){
        var i = t.a.identity || {}, names = i.names || {};
        var longest = Math.max.apply(null, order.map(function(e){ return String(names[e] || "").length; }).concat([0]));
        return h("tr",null,
          h("td",null, h("button",{type:"button",class:"agentlink",onclick:function(){ openIdentity(t.a, t.d); }}, h("span",{class:"anm",style:"display:inline-flex"}, idIcon(t.a), h("span",{class:"note"}, t.a.id || (t.d.id + "-DATA"))))),
          order.map(function(e){ return h("td",null, names[e] || h("span",{class:"tbc"},"\u2014")); }),
          h("td",null, i.kind || TBC), h("td",null, i.schema ? h("code",null, String(i.schema)) : "\u2014"),
          h("td",null, h("span",{class:"pill " + (longest <= maxLen ? "val" : "int")}, longest + " / " + maxLen)),
          h("td",null, idStatus(t.a)));
      })))));
  if (arr(I.decisions).length) out.push(h("h3",{class:"sub"},"Decisions to confirm"),
    h("div",{class:"tscroll"}, h("table",{class:"t"},
      h("thead",null, h("tr",null, ["Decision","Owner","When"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, I.decisions.map(function(x){ return h("tr",null, h("td",null, x.id ? h("b",null, x.id + " ") : null, x.decision || ""), h("td",null, x.owner || TBC), h("td",null, x.when || TBC)); })))));
  if (arr(I.rules).length) out.push(h("h3",{class:"sub"},"Microsoft guidance applied"),
    h("ul",{class:"clean idrules"}, I.rules.map(function(r){ return h("li",null, /^https:\/\//.test(r.url || "") ? h("a",{href:r.url, target:"_blank", rel:"noopener"}, r.title || r.url) : h("b",null, r.title || ""), r.text ? " \u2014 " + r.text : ""); })));
  if (I.package) out.push(h("p",{class:"note"}, "Full kit with PNG icons, cards, catalogue, scripts and pipelines: ", h("b",null, String(I.package)), "."));
  out.push(h("h3",{class:"sub"},"Validate in the workshop"),
    arr(BP.identity_feedback).length ? h("ul",{class:"clean idrules"}, BP.identity_feedback.map(function(f){ return h("li",null, h("b",null, (f.date || "") + (f.status ? " \u00b7 " + f.status : "")), f.note ? " \u2014 " + f.note : "", evPills(f.src)); })) : null,
    valBox("identity","names"));
  return out;
}

/* ---------------- architecture ---------------- */
function renderArchitectureClassic(part){
  var A = BP.architecture || {};
  var out = part ? [] : [h("h2",{class:"sec"}, A.title || "Target architecture"), A.intro ? h("p",{class:"lead"}, A.intro, evPills(A.src)) : null];
  if ((!part || part === "layers") && arr(A.principles).length){
    out.push(h("h3",{class:"sub"},"Architecture principles"));
    out.push(h("div",{class:"principles"}, A.principles.map(function(p){ return h("div",{class:"pr"}, h("b",null, p.name), h("span",null, p.desc), evPills(p.src)); })));
  }
  if ((!part || part === "layers") && arr(A.layers).length){
    out.push(h("h3",{class:"sub"},"Layered target architecture"));
    out.push(h("div",{class:"layers"}, A.layers.map(function(L){
      return h("div",{class:"layer"},
        h("div",{class:"lh"}, h("b",null, L.name), h("span",null, L.purpose || "")),
        h("div",{class:"blks"}, arr(L.blocks).map(function(b){
          return h("div",{class:"blk" + (b.kind ? " " + b.kind : "")}, h("b",null, logosFor(b.name + " " + (b.desc || ""), 16, 3), b.name), b.desc ? h("span",null, b.desc) : null,
            (b.status || b.tag) ? h("span",{class:"tags"}, b.tag ? h("span",{class:"pill acc"}, b.tag) : null, b.status ? h("span",{class:"pill" + (/preview/i.test(b.status) ? " adj" : (/^ga$|generally/i.test(b.status) ? " val" : (/confirm|tbd/i.test(b.status) ? " hyp" : "")))}, b.status) : null) : null);
        })));
    })));
    out.push(h("div",{class:"legend",style:"margin:4px 0 0"},
      h("span",{class:"it"}, h("span",{class:"blk agent",style:"min-width:0;padding:2px 8px;flex:none"},"agent"), "Reasoning step"),
      h("span",{class:"it"}, h("span",{class:"blk workflow",style:"min-width:0;padding:2px 8px;flex:none"},"workflow"), "Deterministic step"),
      h("span",{class:"it"}, h("span",{class:"blk control",style:"min-width:0;padding:2px 8px;flex:none"},"control"), "Governance and control"),
      h("span",{class:"it"}, h("span",{class:"pill acc"},"MVP"), "Needed for the first build")));
  }
  (!part || part === "flows" ? arr(A.flows) : []).forEach(function(f){
    out.push(h("h3",{class:"sub"}, f.name || "Process flow", evPills(f.src)));
    if (f.note) out.push(h("p",{class:"note"}, f.note));
    out.push(h("div",{class:"flow"}, arr(f.steps).map(function(st, i){
      var actor = String(st.actor || "workflow").toLowerCase();
      var cls = actor === "agent" ? "pill acc" : (actor === "human" ? "pill val" : (actor === "system" ? "pill" : "pill adj"));
      return h("div",{class:"fs"}, h("span",{class:"no"}, String(i + 1)), h("span",null, h("span",{class:cls}, actor.charAt(0).toUpperCase() + actor.slice(1))), h("span",null, st.text || ""));
    })));
  });
  if ((!part || part === "layers") && arr(A.patterns).length){
    out.push(h("h3",{class:"sub"},"Orchestration patterns"));
    out.push(h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Pattern","Where","Why"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, A.patterns.map(function(p){ return h("tr",null, h("td",null, h("b",null, p.pattern)), h("td",null, p.where || TBC), h("td",null, p.why || TBC)); })))));
  }
  if (!part && arr(A.decisions).length){
    out.push(h("h3",{class:"sub"},"Architecture decisions"));
    out.push(h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["ID","Decision","Status","Rationale"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, A.decisions.map(function(x){ return h("tr",null, h("td",null, h("b",null, x.id || "")), h("td",null, h("b",null, x.title || ""), h("div",null, x.decision || "")), h("td",null, statusPill(x.status === "accepted" ? "validated" : (x.status || "open"))), h("td",null, x.rationale || TBC)); })))));
  }
  if (arr(A.open_decisions).length){
    out.push(h("h3",{class:"sub"},"Open technical decisions"));
    out.push(h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["ID","Question","Owner"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, A.open_decisions.map(function(x){ return h("tr",null, h("td",null, h("b",null, x.id || "")), h("td",null, x.question || ""), h("td",null, x.owner || TBC)); })))));
  }
  if ((!part || part === "layers") && arr(A.sources).length){
    out.push(h("h3",{class:"sub"},"Grounding"));
    out.push(h("ul",{class:"clean note"}, A.sources.map(function(x){ return h("li",null, x); })));
  }
  return out;
}

/* ---------------- use cases ---------------- */
function quadrant(v, f){ return v >= 3 ? (f >= 3 ? "Quick wins" : "Invest") : (f >= 3 ? "Test and learn" : "Park"); }
function score(x){ if (typeof x === "number") return Math.max(1, Math.min(5, x)); var t = String(x || "").toLowerCase(); return t === "high" ? 4.5 : (t === "medium" ? 3 : (t === "low" ? 1.5 : 3)); }
function openUseCase(u){
  closeDrawer(); state.uc = u.id; state.view = "usecases"; render(false);
  var el = document.getElementById("ucdetail"); if (el && el.scrollIntoView) { try { el.scrollIntoView({behavior:"smooth", block:"start"}); } catch (e) {} }
}
function ucDrawerLegacy(u){
  var d = domById(u.domain) || {};
  var v = score(u.value), f = score(u.feasibility);
  openDrawer(u.id + " \u00b7 " + u.name, (d.name || "") + " \u00b7 " + quadrant(v, f), [
    h("div",{style:"display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px"}, statusPill(note("val|uc|" + u.id).status || u.status), u.mvp ? h("span",{class:"pill acc"},"MVP candidate") : null, u.horizon ? h("span",{class:"pill"}, u.horizon) : null, u.wave ? h("span",{class:"pill"}, u.wave) : null),
    h("dl",{class:"kv"},
      h("dt",null,"Problem"), h("dd",null, val(u.problem)),
      h("dt",null,"Idea"), h("dd",null, val(u.idea || u.description)),
      h("dt",null,"Value"), h("dd",null, String(u.value || TBC) + (u.value_note ? " \u2014 " + u.value_note : "")),
      h("dt",null,"Feasibility"), h("dd",null, String(u.feasibility || TBC) + (u.feasibility_note ? " \u2014 " + u.feasibility_note : "")),
      h("dt",null,"Agents"), h("dd",null, arr(u.agents).length ? h("span",{style:"display:flex;gap:6px;flex-wrap:wrap"}, arr(u.agents).map(function(n){ var ag = agentByName(n); return ag ? h("button",{type:"button",class:"btn",style:"padding:3px 10px",onclick:function(){ openAgent(ag.id); }}, h("span",{class:"anm",style:"display:inline-flex"}, idIcon(ag), nameOf(ag))) : h("span",null,n); })) : h("span",{class:"tbc"},TBC)),
      h("dt",null,"KPIs"), h("dd",null, ul(u.kpis)),
      h("dt",null,"Dependencies"), h("dd",null, ul(u.dependencies)),
      h("dt",null,"Risks"), h("dd",null, ul(u.risks)),
      h("dt",null,"Evidence"), h("dd",null, evPills(u.src) || h("span",{class:"tbc"},"Microsoft hypothesis"))),
    ucValue(u),
    h("div",{style:"height:10px"}), valBox("uc", u.id)
  ]);
}
function matrixSvg(){
  var W = 560, H = 440, L = 56, T = 24, R = 18, B = 50, iw = W - L - R, ih = H - T - B;
  function X(f){ return L + (f - 0.5) / 5 * iw; }
  function Y(v){ return T + ih - (v - 0.5) / 5 * ih; }
  var svg = s("svg",{viewBox:"0 0 " + W + " " + H, class:"matrix", role:"group", "aria-label":"Use case portfolio by value and feasibility"});
  svg.appendChild(s("rect",{x:X(3), y:T, width:L + iw - X(3), height:Y(3) - T, fill:"var(--ok-soft)"}));
  svg.appendChild(s("rect",{x:L, y:T, width:X(3) - L, height:Y(3) - T, fill:"var(--accent-soft)"}));
  svg.appendChild(s("rect",{x:X(3), y:Y(3), width:L + iw - X(3), height:T + ih - Y(3), fill:"var(--warn-soft)"}));
  svg.appendChild(s("rect",{x:L, y:Y(3), width:X(3) - L, height:T + ih - Y(3), fill:"var(--chip)"}));
  [["Invest",L + 8, T + 18,"start"],["Quick wins",L + iw - 8, T + 18,"end"],["Park",L + 8, T + ih - 10,"start"],["Test and learn",L + iw - 8, T + ih - 10,"end"]].forEach(function(q){
    svg.appendChild(s("text",{x:q[1], y:q[2], "text-anchor":q[3], class:"q"}, q[0].toUpperCase()));
  });
  svg.appendChild(s("line",{x1:L, y1:T + ih, x2:L + iw, y2:T + ih, stroke:"var(--grey)"}));
  svg.appendChild(s("line",{x1:L, y1:T, x2:L, y2:T + ih, stroke:"var(--grey)"}));
  for (var i = 1; i <= 5; i++){
    svg.appendChild(s("text",{x:X(i), y:T + ih + 16, "text-anchor":"middle", style:"font-size:11px"}, String(i)));
    svg.appendChild(s("text",{x:L - 10, y:Y(i) + 4, "text-anchor":"end", style:"font-size:11px"}, String(i)));
  }
  svg.appendChild(s("text",{x:L + iw / 2, y:H - 10, "text-anchor":"middle", style:"font-size:12px;font-weight:700"}, "Feasibility \u2192"));
  svg.appendChild(s("text",{x:16, y:T + ih / 2, "text-anchor":"middle", transform:"rotate(-90 16 " + (T + ih / 2) + ")", style:"font-size:12px;font-weight:700"}, "Value \u2192"));
  /* place bubbles at their scores, then relax overlaps so every bubble stays visible */
  var vmax = Math.max.apply(null, UCS.map(function(u){ var v = valueOf(u); return v && v.range_year && num(v.range_year.base) ? v.range_year.base : 0; }).concat([0]));
  var pts = UCS.map(function(u){ var v = valueOf(u), b = v && v.range_year ? v.range_year.base : null; var r = num(b) && b > 0 && vmax > 0 ? 13 + 15 * Math.sqrt(b / vmax) : (u.mvp ? 17 : 14); return {u:u, r:r, x:X(score(u.feasibility)), y:Y(score(u.value))}; });
  for (var it = 0; it < 60; it++){
    var moved = false;
    for (var i2 = 0; i2 < pts.length; i2++) for (var j2 = i2 + 1; j2 < pts.length; j2++){
      var a = pts[i2], b = pts[j2], dx = b.x - a.x, dy = b.y - a.y, dist = Math.sqrt(dx * dx + dy * dy), min = a.r + b.r + 3;
      if (dist < min){
        if (dist < 0.01){ dx = 1; dy = 0.35 * ((i2 + j2) % 2 ? 1 : -1); dist = Math.sqrt(dx * dx + dy * dy); }
        var push = (min - dist) / 2, ux = dx / dist, uy = dy / dist;
        a.x -= ux * push; a.y -= uy * push; b.x += ux * push; b.y += uy * push; moved = true;
      }
    }
    pts.forEach(function(p){ p.x = Math.max(L + p.r, Math.min(L + iw - p.r, p.x)); p.y = Math.max(T + p.r, Math.min(T + ih - p.r, p.y)); });
    if (!moved) break;
  }
  pts.forEach(function(p){
    var u = p.u, cx = p.x, cy = p.y;
    var d = domById(u.domain) || {color:ACCENT};
    var st = String(note("val|uc|" + u.id).status || u.status || "").toLowerCase();
    var g = s("g",{class:"bub" + (st === "rejected" ? " faded" : ""), tabindex:"0", role:"button", "aria-label":u.id + " " + u.name + ", value " + u.value + ", feasibility " + u.feasibility});
    g.appendChild(s("circle",{cx:cx, cy:cy, r:p.r, fill:d.color, stroke: u.mvp ? "var(--ink)" : "var(--panel)", "stroke-width": u.mvp ? 3 : 2}));
    var uv = valueOf(u);
    if (uv && uv.status !== "validated") g.appendChild(s("circle",{cx:cx, cy:cy, r:p.r + 4.5, fill:"none", stroke:"var(--ink)", "stroke-width":1.4, "stroke-dasharray":"3 3", opacity:.75}));
    g.appendChild(s("text",{x:cx, y:cy + 4, "text-anchor":"middle", style:"font-size:" + (String(u.id).length > 4 ? 8.5 : 10) + "px;font-weight:700;fill:" + onColor(d.color)}, String(u.id)));
    g.appendChild(s("title",null, u.id + " \u00b7 " + u.name + (uv ? " \u00b7 value " + chf((uv.range_year || {}).base, true) + " per year (" + (uv.status || "hypothesis") + ")" : "")));
    g.addEventListener("click", function(){ openUseCase(u); });
    g.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openUseCase(u); } });
    svg.appendChild(g);
  });
  return svg;
}
function ucAgentIcons(u){
  var ags = arr(u.agents).map(agentByName).filter(Boolean);
  if (!ags.length) return "\u2014";
  return h("span",{class:"ucags"}, ags.slice(0, 5).map(function(a){ var d = a._d || {};
    return h("button",{type:"button",class:"ucag",title:nameOf(a),"aria-label":nameOf(a),onclick:function(){ openAgent(a.id); }}, idIcon(a, "aicon") || h("span",{class:"aicon ini",style:filled(d.color)}, initials(shortOf(a)))); }),
    ags.length > 5 ? h("span",{class:"small-lbl"}, "+" + (ags.length - 5)) : null);
}
function renderUseCases(){
  var rows = UCS.slice().sort(function(a, b){ return (b.mvp ? 1 : 0) - (a.mvp ? 1 : 0) || score(b.value) * score(b.feasibility) - score(a.value) * score(a.feasibility); });
  var table = h("div",{class:"tscroll"}, h("table",{class:"t"},
    h("thead",null, h("tr",null, ["ID","Use case","Journey","Agents","Value","Feasibility","Horizon","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, rows.map(function(u){
      var d = domById(u.domain) || {};
      return h("tr",null, h("td",null, h("b",null, u.id)), h("td",null, h("button",{type:"button",style:"all:unset;cursor:pointer;font-weight:700;color:var(--ink)",onclick:function(){ openUseCase(u); }}, u.name), u.mvp ? h("span",{class:"pill acc",style:"margin-inline-start:6px"},"MVP") : null, evPills(u.src)),
        h("td",null, d.name || ""), h("td",null, ucAgentIcons(u)), h("td",null, String(u.value || TBC)), h("td",null, String(u.feasibility || TBC)), h("td",null, u.horizon || TBC), h("td",null, statusPill(note("val|uc|" + u.id).status || u.status)));
    }))));
  return [h("h2",{class:"sec"},"Use case portfolio"), h("p",{class:"lead"}, BP.use_case_intro || "Every candidate placed by value and feasibility. Bubble colour = journey, dark ring = MVP candidate. Select a bubble or a row for the detail and to record the workshop verdict."),
    h("div",{class:"ucwrap"}, h("div",{class:"matrixwrap",tabindex:"0",role:"region","aria-label":"Locally scrollable use-case matrix",
      onkeydown:function(e){ if (/^Arrow/.test(e.key)) e.stopPropagation(); }}, matrixSvg()), table), VC ? matrixLegend() : null,
    (function(){ var su = UCS.filter(function(x){ return x.id === state.uc; })[0]; return su ? ucDetail(su) : h("p",{class:"note"},"Select a use case in the matrix or the table to open it in the use-case template: general, value and feasibility, with its agents and the assumptions to clarify."); })(),
    VC ? valueSection() : null];
}

/* ---------------- discovery ---------------- */
function qid(d, cat, i, q){ return q.id || (d.id + "-" + cat.replace(/[^A-Za-z]/g,"").slice(0,4).toUpperCase() + "-" + (i + 1)); }
function questionsOf(d){
  var out = [];
  Object.keys(d.discovery || {}).forEach(function(cat){
    arr(d.discovery[cat]).forEach(function(q, i){
      if (typeof q === "string") q = {q:q};
      out.push({cat:cat, q:q, id:qid(d, cat, i, q)});
    });
  });
  return out;
}
function qStatus(x){ var n = note("q|" + x.id); return String(n.status || x.q.status || "open").toLowerCase(); }
function renderDiscovery(){
  var d = dom(), Q = questionsOf(d);
  var counts = {answered:0, partial:0, open:0};
  Q.forEach(function(x){ var st = qStatus(x); counts[st in counts ? st : "open"]++; });
  var tot = Q.length || 1;
  var filt = h("div",{class:"filters"}, h("span",{class:"lbl note"},"Show"),
    [["all","All"],["open","Open"],["partial","Partly answered"],["answered","Answered"]].map(function(f){
      return h("button",{type:"button",class:"btn",style:state.discFilter === f[0] ? "border-color:var(--accent);color:var(--accent-text)" : null,"aria-pressed": state.discFilter === f[0] ? "true" : "false",onclick:function(){ state.discFilter = f[0]; render(); }}, f[1] + (f[0] === "all" ? " (" + Q.length + ")" : " (" + counts[f[0]] + ")"));
    }));
  var cov = h("div",{class:"covbar","aria-hidden":"true"}, h("i",{style:"width:" + (counts.answered / tot * 100) + "%;background:var(--ok)"}), h("i",{style:"width:" + (counts.partial / tot * 100) + "%;background:var(--warn)"}));
  var groups = {};
  Q.forEach(function(x){ (groups[x.cat] = groups[x.cat] || []).push(x); });
  var body = Object.keys(groups).map(function(cat){
    var items = groups[cat].filter(function(x){ return state.discFilter === "all" || qStatus(x) === state.discFilter; });
    if (!items.length) return null;
    return h("div",{class:"qgroup"}, h("h4",null, cat, h("span",{class:"pill"}, String(items.length))), items.map(function(x){
      var k = "q|" + x.id, n = note(k), st = qStatus(x);
      var sid = "qs-" + x.id.replace(/\W/g,"_"), cid = "qc-" + x.id.replace(/\W/g,"_"), tid = "qt-" + x.id.replace(/\W/g,"_");
      return h("div",{class:"q"},
        h("div",{class:"qt"}, h("b",null, x.q.q || x.q.text || ""), statusPill(st)),
        x.q.why ? h("div",{class:"note"}, "Why it matters: " + x.q.why) : null,
        x.q.answer ? h("div",{class:"ans"}, h("b",null,"What we know \u00b7 "), x.q.answer, evPills(x.q.src)) : null,
        h("div",{class:"row"},
          h("label",{class:"chk",for:cid}, h("input",{type:"checkbox",id:cid,checked: n.discussed ? true : null,onchange:function(e){ setNote(k,{discussed:e.target.checked}); }}), "Discussed"),
          h("label",{class:"chk",for:sid}, "Status ", h("select",{id:sid,onchange:function(e){ setNote(k,{status:e.target.value}); render(); }},
            [["open","Open"],["partial","Partly answered"],["answered","Answered"]].map(function(o){ return h("option",{value:o[0],selected: st === o[0] ? true : null}, o[1]); }))),
          h("span",{class:"note"}, x.id)),
        h("label",{class:"note",for:tid},"Answer or note from the workshop"),
        h("textarea",{id:tid,placeholder:"Capture the answer, numbers, owners",oninput:function(e){ setNote(k,{note:e.target.value}); }}, n.note || ""));
    }));
  });
  var stEl = h("span",{class:"status",role:"status"});
  return [h("h2",{class:"sec"},"Discovery \u00b7 " + d.name),
    h("p",{class:"lead"},"Questions the hypothesis still depends on. Prefilled answers come from the evidence; capture what the workshop confirms. Notes stay in this browser until you export them for the plugin to merge into the next version."),
    h("div",{class:"panel"}, h("div",{class:"ptitle"}, h("b",null,"Coverage"), h("span",null, counts.answered + " answered \u00b7 " + counts.partial + " partly \u00b7 " + counts.open + " open")), cov, filt),
    h("div",{class:"btnrow"},
      h("button",{type:"button",class:"btn primary",onclick:function(){ exportFeedback(stEl); }},"Export workshop feedback (JSON)"),
      h("button",{type:"button",class:"btn",onclick:function(){ copyText(notesText(), stEl); }},"Copy notes as text"),
      h("button",{type:"button",class:"btn",onclick:function(){ if (window.confirm("Clear every note and validation saved in this browser for this blueprint?")) { NOTES = {}; saveNotes(); render(); } }},"Clear local notes"), stEl),
    body];
}
function feedbackObject(){
  var out = {type:"frontier-blueprint-feedback", schema:"1.0", blueprint:M.id || M.customer || "", version:M.version || "", exported:new Date().toISOString(), validations:{}, discovery:{}};
  if (previewPresent()) out.finops_preview_notice = FINOPS_NOTICE;
  Object.keys(NOTES).forEach(function(k){
    var p = k.split("|");
    if (p[0] === "val") out.validations[p[1] + ":" + p.slice(2).join("|")] =
      p[1] === "finops" ? presentedFinopsNote(NOTES[k]) : p[1] === "ass" ? presentedAssumptionVerdict(ASSM[p.slice(2).join("|")], NOTES[k]) : NOTES[k];
    else if (p[0] === "q") out.discovery[p.slice(1).join("|")] = NOTES[k];
  });
  return out;
}
function presentedFinopsNote(n){
  if (!previewAcknowledged) return {note:"Financial proposal withheld until fresh viewer acknowledgement."};
  return Object.assign({},n,{note:"Input to a new draft only; not financial approval. " + (n.note || "")});
}
function notesText(){
  var L = [(M.customer || "Customer") + " \u2014 Frontier blueprint workshop notes", "Exported " + new Date().toLocaleString(), ""];
  if (previewPresent()) L.unshift(FINOPS_NOTICE, previewAcknowledged ? "Provisional Preview figures, not recommendations." : "Preview numeric assumption values withheld until viewer acknowledgement.", "");
  D.forEach(function(d){
    var lines = [];
    questionsOf(d).forEach(function(x){ var n = note("q|" + x.id); if (n.note || n.status || n.discussed) lines.push("- [" + (n.status || "open") + "] " + (x.q.q || "") + (n.note ? "\n    " + n.note : "")); });
    (d.orchestrator ? [d.orchestrator] : []).concat(d.agents).forEach(function(a){ var n = note("val|agent|" + a.id); if (n.status || n.note) lines.push("- Agent " + nameOf(a) + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
    if (lines.length) L.push("## " + d.name, ...lines, "");
  });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|ass|") === 0; }).sort().forEach(function(k){
    var id = k.slice(8), a = ASSM[id] || {}, shown = presentedAssumption(a), n = presentedAssumptionVerdict(a, NOTES[k]);
    if (n.status || n.note || num(n.value) || assumptionWithheld(a)) L.push("- Assumption " + id + (shown.statement ? " (" + shown.statement + ")" : "") + ": " + (n.status || "") + (num(n.value) ? " \u2192 " + n.value + (shown.unit ? " " + shown.unit : "") : "") + (n.note ? " \u2014 " + n.note : ""));
  });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|ready|") === 0; }).sort().forEach(function(k){ var n = NOTES[k]; if (n.status || n.note) L.push("- IT readiness " + k.slice(10) + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|adr|") === 0; }).sort().forEach(function(k){ var n = NOTES[k]; if (n.status || n.note) L.push("- Decision " + k.slice(8) + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
  PILLAR_ORDER.forEach(function(pk){ var n = note("val|loop|" + pk); if (n.status || n.note) L.push("- Feedback loop \u00b7 " + PILLARS[pk].label + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|finops|") === 0; }).sort().forEach(function(k){
    L.push("- FinOps proposal " + k.slice(11) + ": " + presentedFinopsNote(NOTES[k]).note);
  });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|onto|") === 0; }).sort().forEach(function(k){
    var n = NOTES[k], id = k.slice(9);
    L.push("- Ontology " + id + (ontFeedbackIds().indexOf(id) < 0 ? " (unknown feedback ID)" : "") + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : ""));
  });
  var ni = note("val|identity|names"); if (ni.status || ni.note) L.push("- Agent identity (names, colours, icons): " + (ni.status || "") + (ni.note ? " \u2014 " + ni.note : ""));
  var np = note("val|prd|scope"); if (np.status || np.note) L.push("- PRD scope: " + (np.status || "") + (np.note ? " \u2014 " + np.note : ""));
  riskItems().forEach(function(r){ var n = note("val|risk|" + r.id), k = rk(r); if (n.status || n.note || n.likelihood || n.impact) L.push("- Risk " + r.id + " " + r.title + ": " + k.status + " \u00b7 Likelihood " + k.L + ", impact " + k.I + " (score " + k.score + ")" + (n.note ? " \u2014 " + n.note : "")); });
  UCS.forEach(function(u){ var n = note("val|uc|" + u.id); if (n.status || n.note) L.push("- Use case " + u.id + " " + u.name + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
  return L.join("\n");
}
function download(name, text, type, stEl){
  try {
    var blob = new Blob([text], {type:type});
    var url = URL.createObjectURL(blob);
    var a = h("a",{href:url, download:name});
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function(){ URL.revokeObjectURL(url); }, 1500);
    if (stEl) stEl.textContent = "Downloaded " + name;
  } catch (e) { if (stEl) stEl.textContent = "Download is blocked here \u2014 use Copy instead"; }
}
function exportFeedback(stEl){
  var safe = String(M.short || M.customer || "blueprint").replace(/[^A-Za-z0-9]+/g,"-").toLowerCase();
  download(safe + "-workshop-feedback.json", JSON.stringify(feedbackObject(), null, 2), "application/json", stEl);
}
function copyText(t, stEl){
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function(){ if (stEl) stEl.textContent = "Copied"; }, function(){ if (stEl) stEl.textContent = "Copy is blocked here"; });
  else if (stEl) stEl.textContent = "Copy is not available in this browser";
}

/* ---------------- roadmap ---------------- */
function renderRoadmap(){
  var HZ = arr(BP.horizons).length ? BP.horizons : [{h:"H1",label:"Now (0\u20136 months)",meaning:"Quick wins on Microsoft 365 Copilot and Copilot Studio with existing data"},{h:"H2",label:"Next (6\u201318 months)",meaning:"Orchestrated agents integrated with systems of record and data products"},{h:"H3",label:"Later (18+ months)",meaning:"Agent-operated processes with bounded autonomy"}];
  var cols = h("div",{class:"hz"}, HZ.map(function(z){
    var cards = [];
    D.forEach(function(d){
      var hp = d.horizon_plan && d.horizon_plan[z.h];
      if (hp) cards.push(h("div",{class:"card",style:"--d:" + d.color}, h("b",null, d.name), hp));
    });
    UCS.filter(function(u){ return String(u.horizon || "").indexOf(z.h) === 0; }).forEach(function(u){
      var d = domById(u.domain) || {color:ACCENT};
      cards.push(h("div",{class:"card",style:"--d:" + d.color}, h("b",null, u.id + " \u00b7 " + u.name), u.mvp ? h("span",{class:"pill acc"},"MVP candidate") : null));
    });
    return h("div",{class:"col"}, h("h4",null, z.h + " \u00b7 " + (z.label || "")), h("div",{class:"rng"}, z.meaning || ""), cards.length ? cards : h("p",{class:"tbc"},TBC));
  }));
  var out = [h("h2",{class:"sec"},"Roadmap and next steps"), BP.roadmap_intro ? h("p",{class:"lead"}, BP.roadmap_intro) : null, h("div",{class:"btnrow"},pageLink("plan")), cols];
  if (arr(BP.mvp_options).length){
    out.push(h("h3",{class:"sub"},"MVP candidates"));
    out.push(h("div",{class:"mvp"}, BP.mvp_options.map(function(m){
      var d = domById(m.domain) || {color:ACCENT, name:""};
      return h("div",{class:"m",style:"--d:" + d.color}, h("div",{class:"op"}, "Option " + (m.option || "") + " \u00b7 " + d.name), h("b",{style:"display:block;font-size:13.5px;margin:3px 0"}, m.use_case || ""),
        mvpAgents(m).length ? h("div",{class:"mvpag"}, mvpAgents(m).map(function(ag){ return h("button",{type:"button",class:"agentlink",onclick:function(){ openAgent(ag.id); }}, h("span",{class:"anm",style:"display:inline-flex"}, idIcon(ag), nameOf(ag))); })) : null,
        mvpValue(m),
        h("div",null, h("b",null,"Why \u00b7 "), m.why || TBC), h("div",{style:"margin-top:4px"}, h("b",null,"Needs \u00b7 "), m.needs || TBC), evPills(m.src));
    })));
  }
  if (arr(BP.next_steps).length){
    out.push(h("h3",{class:"sub"},"Next steps"));
    out.push(h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Step","Owner","When","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, BP.next_steps.map(function(x){ return h("tr",null, h("td",null, x.step || "", evPills(x.src)), h("td",null, x.owner || TBC), h("td",null, x.when || TBC), h("td",null, h("span",{class:"pill" + (/done/i.test(x.status || "") ? " val" : (/due|next/i.test(x.status || "") ? " adj" : ""))}, x.status || "Planned"))); })))));
  }
  return out;
}

/* ---------------- evidence ---------------- */
function renderEvidence(){
  var E = arr(BP.evidence);
  var byType = {};
  E.forEach(function(e){ byType[e.type] = (byType[e.type] || 0) + 1; });
  var stats = h("div",{class:"evstats"}, Object.keys(byType).map(function(t){ return h("div",{class:"s"}, h("b",null, String(byType[t])), EVT[t] || t); }));
  var internal = E.filter(function(e){ return String(e.visibility || "").toLowerCase() === "internal"; }).length;
  var table = h("div",{class:"tscroll"}, h("table",{class:"t"},
    h("thead",null, h("tr",null, ["ID","Source","Type","Date","Visibility","Informs"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, E.map(function(e){
      return h("tr",null, h("td",null, h("button",{type:"button",class:"pill ev",onclick:function(){ openEvidence(e.id); }}, e.id)),
        h("td",null, h("b",null, e.title || ""), e.summary ? h("div",{class:"note"}, e.summary) : null),
        h("td",null, EVT[e.type] || e.type || ""), h("td",null, e.date || ""),
        h("td",null, String(e.visibility || "").toLowerCase() === "internal" ? h("span",{class:"pill int"},"Internal") : h("span",{class:"pill"},"Shareable")),
        h("td",null, (USED[e.id] || []).length ? (USED[e.id].slice(0,4).join(" \u00b7 ") + (USED[e.id].length > 4 ? " \u00b7 +" + (USED[e.id].length - 4) : "")) : h("span",{class:"tbc"},"Context only")));
    }))));
  return [h("h2",{class:"sec"},"Evidence behind the blueprint"),
    h("p",{class:"lead"}, BP.evidence_intro || "Every statement that is not a Microsoft hypothesis points to a source: meetings and their transcripts, emails, chats and documents found with Work IQ, plus public information. Select an ID anywhere in the blueprint to see the source."),
    stats, internal ? h("p",{class:"note"}, h("span",{class:"pill int"},"Internal"), " " + internal + " source" + (internal === 1 ? " is" : "s are") + " Microsoft-internal. Build the customer version before sharing.") : null, table];
}

/* ---------------- PRD: the shared Python model, not independently numbered requirements ---------------- */
function dataTable(cols, rows, cls){
  return h("div",{class:"tscroll"}, h("table",{class:"t " + (cls || "")},
    h("thead",null, h("tr",null, cols.map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, rows.map(function(row){ return h("tr",null, row.map(function(c){ return h("td",null, c); })); }))));
}
function prdStatus(){
  var st = String(note("val|prd|scope").status || (BP.prd || {}).status || "hypothesis").toLowerCase();
  return {agreed:"validated",draft:"hypothesis"}[st] || st;
}
function prdRequirements(P){ return arr(P.platform).concat(arr(P.agents).reduce(function(out, a){ return out.concat(arr(a.requirements)); }, [])); }
function reqRows(rows){ return arr(rows).map(function(r){ return [r.id, r.text || TBC, r.priority || "Must", r.verify || TBC]; }); }
function prdRelease(P){ var rows = arr(P.release_plan).filter(function(r){ return Array.isArray(r) && r.length >= 3; }); return rows.length ? rows : arr(P.release_plan_default); }
function prdValues(){
  return arr((BP.prd || {}).use_cases).map(function(x){
    var u = ucById(x.id), v = u && valueOf(u), res = v;
    if (!v) return null;
    var st = v.status || "hypothesis", label = (STATUS[String(st).toLowerCase()] || {label:st}).label;
    return {name:x.id + " \u00b7 " + x.name, status:st, statusLabel:label,
      summary:[num(res.npv) ? "NPV " + chf(res.npv, true) : null, num(res.roi) ? "ROI " + pct(res.roi) : null,
        num(res.payback_months) ? "payback " + res.payback_months.toFixed(1) + " months" : null].filter(Boolean).join(" \u00b7 ")};
  }).filter(Boolean);
}
function prdValue(){
  return h("ul",{class:"clean"}, prdValues().map(function(v){
    return h("li",null, h("b",null, v.name), " ", v.summary, " ", statusPill(v.status));
  }));
}
function renderPrd(){
  var P = BP.prd || {}, fr = prdRequirements(P), stEl = h("span",{class:"status",role:"status"});
  var scopeBadge = statusPill(prdStatus());
  scopeBadge.setAttribute("role","status");
  function updateScopeBadge(){
    var next = statusPill(prdStatus());
    scopeBadge.className = next.className;
    scopeBadge.textContent = next.textContent;
  }
  var reqCols = ["ID","Requirement","Priority","Verified by"];
  var out = [h("h2",{class:"sec"}, P.title || "Product requirements (PRD)"),
    h("p",{class:"lead"},"What the first agents must do, from the use cases and business value. The solution design continues with the same FR, NFR and AC requirement IDs. Hypotheses are not approvals. ", evPills(P.src)),
    h("div",{class:"idstrip"}, scopeBadge, P.basis ? h("span",{class:"pill"}, P.basis) : null,
      h("span",{class:"pill acc"}, arr(P.scope).length + " MVP agents"), h("span",{class:"pill"}, fr.length + " functional requirements"),
      h("span",{class:"pill"}, arr(P.nfr).length + " non-functional"), h("span",{class:"pill"}, arr(P.acceptance).length + " acceptance criteria"),
      P.owner ? h("span",{class:"pill"},"Owner \u00b7 " + P.owner) : null),
    h("div",{class:"btnrow"}, h("button",{type:"button",class:"btn",onclick:function(){
      download(fileSlug() + "-prd.md", prdMarkdown(), "text/markdown;charset=utf-8", stEl);
    }},"Download the PRD (Markdown)"), pageLink("risks"), pageLink("plan"), stEl),
    h("h3",{class:"sub"},"1 \u00b7 Problem and vision"), P.problem ? h("p",null, h("b",null, P.problem)) : null,
    h("ul",{class:"clean"}, arr(P.problems).map(function(pr){
      return h("li",null, h("b",null, pr.name || pr.use_case), ul(arr(pr.items).map(function(x){ return x[0] + ": " + x[1]; })), evPills(pr.src));
    })), h("blockquote",{class:"quote"}, P.vision || TBC), ul(arr(P.commitments).map(function(c){ return c.join(" "); })),
    h("h3",{class:"sub"},"2 \u00b7 Goals and how success is measured"),
    h("div",{class:"grid2"}, h("div",null, h("h4",null,"Goals"), ul(P.goals)), h("div",null, h("h4",null,"Non-goals"), ul(P.non_goals))),
    dataTable(["Maturity","Current","Target"], arr(P.maturity)),
    dataTable(["KPI","Journey","Baseline","Target"], arr(P.kpis).map(function(k){ return [h("span",null, h("b",null, k.kpi), k.definition ? h("div",{class:"note"}, k.definition) : null), k.journey_name, k.baseline || TBC, k.target || TBC]; })), prdValue(),
    h("h3",{class:"sub"},"3 \u00b7 Scope of the MVP"),
    dataTable(["Agent","Journey","Autonomy","Horizon","What it proves"], arr(P.scope).map(function(x){ return [AG[x.agent] ? agentChip(AG[x.agent],true) : x.name, x.journey_name, x.autonomy || TBC, x.horizon || TBC, x.proves || TBC]; })),
    h("div",{class:"btnrow"}, arr(P.use_cases).map(function(x){ var u = ucById(x.id); return u ? h("button",{type:"button",class:"pill linkp",onclick:function(){ openUseCase(u); }}, x.id + " \u00b7 " + x.name) : null; })),
    h("div",{class:"grid2"}, h("div",null, h("h4",null,"In scope"), ul(arr(P.scope).map(function(x){ return x.name + ": " + x.capability; }))),
      h("div",null, h("h4",null,"Out of scope"), ul(P.out_of_scope))),
    h("div",{class:"callout"}, h("b",null,"Exit test \u00b7 "), P.exit_test || TBC),
    h("h3",{class:"sub"},"4 \u00b7 Users"), dataTable(["Persona","Journey","Goal","Pain today","Decides"], arr(P.personas).map(function(x){ return [x.role, x.journey_name, x.goal || TBC, x.pain || TBC, x.decides || TBC]; })),
    h("h3",{class:"sub"},"5 \u00b7 Functional requirements"),
    h("details",{class:"prdx"}, h("summary",null,"Platform: " + arr(P.platform).length + " requirements every agent meets"), dataTable(reqCols, reqRows(P.platform), "req"))];
  arr(P.agents).forEach(function(x){
    out.push(h("section",{class:"prdag"}, h("h4",null, x.name), h("div",{class:"btnrow"}, AG[x.agent] ? agentChip(AG[x.agent]) : null),
      h("p",null, x.capability || TBC), dataTable(reqCols, reqRows(x.requirements), "req"),
      h("details",{class:"prdx"}, h("summary",null,"The seven declarations"), dataTable(["Declaration","Mandate"], arr(x.declarations)))));
  });
  out.push(h("h3",{class:"sub"},"6 \u00b7 Non-functional requirements"),
    h("details",{class:"prdx"}, h("summary",null, arr(P.nfr).length + " non-functional requirements"),
      dataTable(["ID","Category","Requirement"], arr(P.nfr).map(function(r){ return [r.id,r.category,r.text]; }), "prd-nfr")),
    h("h3",{class:"sub"},"7 \u00b7 Acceptance criteria"), dataTable(["ID","Agent","Criterion"], arr(P.acceptance).map(function(r){ return [r.id, AG[r.agent] ? agentChip(AG[r.agent],true) : r.agent_name, r.text]; })),
    h("h3",{class:"sub"},"8 \u00b7 Dependencies, risks and open decisions"),
    h("div",{class:"grid3 prd3"}, h("div",{class:"panel"}, h("h4",null,"Dependencies"), ul(P.dependencies)),
      h("div",{class:"panel"}, h("h4",null,"Risks"), h("ul",{class:"clean"}, arr(P.risks).map(function(r){ return h("li",null, riskLink(r.id), " " + r.title, r.score ? h("span",{class:"pill rsc " + riskLevel(r.score)}, String(r.score)) : null); }))),
      h("div",{class:"panel"}, h("h4",null,"Open decisions"), ul(arr(P.decisions).map(function(x){ return x.id + ": " + x.question; })))),
    h("h3",{class:"sub"},"9 \u00b7 Release plan and Definition of Ready"),
    dataTable(["Phase","Scope","Exit criterion"], prdRelease(P)), h("h4",null,"Definition of Ready (before the build)"), ul(P.definition_of_ready), pageLink("plan"),
    h("h3",{class:"sub"},"Workshop verdict on the MVP scope"), valBox("prd","scope",updateScopeBadge));
  return out;
}
function mdTable(cols, rows){
  function esc(x){ return String(x === undefined || x === null || x === "" ? "[To complete]" : x).replace(/\|/g, "\\|").replace(/\r?\n/g, " "); }
  return ["| " + cols.join(" | ") + " |", "|" + cols.map(function(){ return "---"; }).join("|") + "|"]
    .concat(rows.map(function(r){ return "| " + r.map(esc).join(" | ") + " |"; })).concat([""]);
}
function prdMarkdown(){
  var P = BP.prd || {}, L = ["# Product Requirements \u2014 " + (M.customer || "Customer"), "",
    "Status: " + prdStatus(), "Owner: " + (P.owner || TBC), "Basis: " + (P.basis || TBC), "",
    "## 1. Problem and vision", "", P.problem || "", "", P.vision || ""];
  if (previewPresent()) L.unshift(FINOPS_NOTICE, portfolioPreview() ?
    (previewAcknowledged ? "Provisional comparisons, not recommendations." : "Preview-derived figures withheld; viewer acknowledgement required.") :
    "The separate optional FinOps report remains acknowledgement-gated. Ordinary business value is independent, not FinOps Preview.", "");
  function bullets(items){ arr(items).forEach(function(x){ L.push("- " + x); }); L.push(""); }
  function table(cols, rows){ L = L.concat(mdTable(cols, rows)); }
  arr(P.problems).forEach(function(pr){ bullets(arr(pr.items).map(function(x){ return pr.name + " (" + x[0] + "): " + x[1]; })); });
  bullets(arr(P.commitments).map(function(c){ return c.join(" "); }));
  L.push("## 2. Goals and measures", ""); bullets(P.goals); L.push("Non-goals:"); bullets(P.non_goals);
  table(["Maturity","Current","Target"], arr(P.maturity));
  table(["KPI","Definition","Journey","Baseline","Target"], arr(P.kpis).map(function(k){ return [k.kpi,k.definition,k.journey_name,k.baseline,k.target]; }));
  L.push("Business value of the use cases in scope (hypothesis until confirmed):", "");
  bullets(prdValues().map(function(v){ return v.name + " " + v.summary + " " + v.statusLabel; }));
  L.push("## 3. Scope", ""); table(["Agent","Journey","Autonomy","Horizon","What it proves"], arr(P.scope).map(function(x){ return [x.name,x.journey_name,x.autonomy,x.horizon,x.proves]; }));
  L.push("Out of scope:"); bullets(P.out_of_scope); L.push("Exit test: " + (P.exit_test || TBC), "", "## 4. Users", "");
  table(["Persona","Journey","Goal","Pain today","Decides"], arr(P.personas).map(function(x){ return [x.role,x.journey_name,x.goal,x.pain,x.decides]; }));
  L.push("## 5. Functional requirements", "", "### Platform", ""); table(["ID","Requirement","Priority","Verified by"], reqRows(P.platform));
  arr(P.agents).forEach(function(x){ L.push("### " + x.name, "", x.capability || "", ""); table(["ID","Requirement","Priority","Verified by"], reqRows(x.requirements)); table(["Declaration","Mandate"], arr(x.declarations)); });
  L.push("## 6. Non-functional requirements", ""); table(["ID","Category","Requirement"], arr(P.nfr).map(function(r){ return [r.id,r.category,r.text]; }));
  L.push("## 7. Acceptance criteria", ""); table(["ID","Agent","Criterion"], arr(P.acceptance).map(function(r){ return [r.id,r.agent_name,r.text]; }));
  L.push("## 8. Dependencies, risks and open decisions", ""); bullets(P.dependencies);
  bullets(arr(P.risks).map(function(r){ return r.id + ": " + r.title + " (score " + r.score + ")"; }));
  bullets(arr(P.decisions).map(function(x){ return x.id + ": " + x.question; }));
  L.push("## 9. Release plan and Definition of Ready", ""); table(["Phase","Scope","Exit criterion"], prdRelease(P)); bullets(P.definition_of_ready);
  var n = note("val|prd|scope"); if (n.note) L.push("Workshop scope notes: " + n.note, "");
  return L.join("\n") + "\n";
}
function fileSlug(){ return String(M.short || M.customer || "blueprint").replace(/[^A-Za-z0-9]+/g,"-").toLowerCase(); }
function pageLink(id){
  return ORDER.indexOf(id) < 0 ? null : h("button",{type:"button",class:"btn",onclick:function(){ go(id); }}, viewMeta(id).label);
}
/* Restore the logical control after a live update, never a detached old node. */
function refreshControl(id, fallback){
  render();
  var el = document.getElementById(id) || document.getElementById(fallback || "");
  if (el) el.focus({preventScroll:true});
}

/* ---------------- Plan: live Agent Factory checks; CSV is a handover, not a native import ---------------- */
var DEF_PHASES = [{id:"idea",name:"Idea",stages:["hypothesis","validated"],what:"Hypothesis to validated use case"},
  {id:"design",name:"Design",stages:["designed","ready"],what:"Design and Definition of Ready"},
  {id:"build",name:"Build",stages:["build"],what:"Build and evaluate in DEV and TEST"},
  {id:"deploy",name:"Deploy and operate",stages:["release","operate"],what:"Release, measure and improve"}];
var DEF_STAGE = {hypothesis:"Hypothesis",validated:"Validated",designed:"Designed",ready:"Ready for build",build:"In build",release:"Released",operate:"Operate & learn"};
var DEF_HANDOVER = [["validated","Validated in the workshop"],["canvas","Trigger canvas complete"],["declarations","Seven declarations made"],["identity","Identity: display names and icons"],["value","Business value validated"],["cost","Cost envelope modelled"],["readiness","IT readiness for the build stage"],["owner","Agent boss named"]];
function boardCfg(){
  var B = FAC && FAC.board || {}, phases = arr(B.phases).filter(function(p){ return p && arr(p.stages).length; });
  return {title:B.title || "Plan: the Agent Factory board",intro:B.intro || "Every agent from idea to design, build and deploy. Cards follow the live handover checks, not permission to build.",phases:phases.length ? phases : DEF_PHASES,wip:B.wip || {}};
}
function handoverDef(){ return (FAC && arr(FAC.handover).length ? FAC.handover : DEF_HANDOVER).map(function(x){
  return x[0] === "cost" ? ["cost","Financial handover: dated, fully priced and externally reviewed planning evidence"] : x;
}); }
function stageLabel(id){ var st = arr(FAC && FAC.lifecycle).filter(function(x){ return x.id === id; })[0]; return st && st.name || DEF_STAGE[id] || id; }
function nextStep(a){
  var st = agentStage(a), checks = agentChecks(a), miss = handoverDef().filter(function(x){ return checks[x[0]] !== 1; });
  return {build:"Build and evaluate in DEV and TEST",release:"Release through the pipeline; measure the outcome",operate:"Measure, learn and improve"}[st] || (miss.length ? miss[0][1] : "Hand over to build");
}
function planAgents(){
  return D.map(function(d){ return [d,(d.orchestrator ? [d.orchestrator] : []).concat(d.agents).filter(function(a){ return a && (!state.planMvp || isMvp(a)); })]; })
    .filter(function(x){ return (state.planLane === "all" || x[0].id === state.planLane) && x[1].length; });
}
function kanbanCard(a){
  var d = a._d || {}, checks = agentChecks(a), H = handoverDef(), done = H.filter(function(x){ return checks[x[0]] === 1; }).length, au = autonomyOf(a);
  return h("button",{type:"button",class:"kcard",style:domainStyle(d.color),title:nameOf(a) + " \u00b7 next: " + nextStep(a),onclick:function(){ openAgent(a.id); }},
    h("span",{class:"kch"}, idIcon(a) || h("span",{class:"aicon ini",style:filled(d.color)}, initials(shortOf(a))), h("b",null, shortOf(a)), isMvp(a) ? h("span",{class:"pill acc"},"MVP") : null),
    h("span",{class:"kmeta"}, au ? h("span",{class:"pill"},"L" + au.n + " \u00b7 " + au.label) : null, h("span",{class:"note"}, a.owner || TBC)),
    h("span",{class:"kprog","aria-label":done + " of " + H.length + " checks"}, h("i",{style:"width:" + Math.round(done / H.length * 100) + "%"})),
    h("span",{class:"note"},checks.cost === 1 ? "Financial handover: planning evidence, not permission" : "Financial handover gap \u00b7 required before build handover"),
    h("span",{class:"knext"}, h("b",null,"Next \u00b7 "), nextStep(a)));
}
function renderPlan(){
  var cfg = boardCfg(), stages = [].concat.apply([], cfg.phases.map(function(p){ return arr(p.stages); })), lanes = planAgents(), cnt = {}, stEl = h("span",{class:"status",role:"status"});
  stages.forEach(function(k){ cnt[k] = 0; });
  var cells = lanes.map(function(x){
    var by = {}; stages.forEach(function(k){ by[k] = []; });
    x[1].forEach(function(a){ var st = agentStage(a); if (!by[st]) st = stages[0]; by[st].push(a); cnt[st]++; }); return [x[0],by];
  });
  var grid = h("div",{class:"kb",role:"region","aria-label":"Agent Factory board: journeys by stage",style:"--cols:" + stages.length}, h("div",{class:"kbcorner"},"Journey"));
  cfg.phases.forEach(function(p){ grid.appendChild(h("div",{class:"kbph ph-" + p.id,style:"grid-column:span " + arr(p.stages).length}, p.name)); });
  grid.appendChild(h("div",{class:"kbcorner"}));
  stages.forEach(function(k){ var lim = cfg.wip[k], over = num(lim) && cnt[k] > lim;
    grid.appendChild(h("div",{class:"kbst" + (over ? " over" : "")}, h("b",null, stageLabel(k)), h("span",{class:"cnt"}, cnt[k] + (num(lim) ? " / " + lim : "")), over ? h("span",{class:"note"},"Above WIP limit (advisory)") : null));
  });
  cells.forEach(function(x){
    grid.appendChild(h("div",{class:"kblane",style:domainStyle(x[0].color)}, h("b",null, x[0].name), h("span",{class:"note"}, x[0].journey_name || "")));
    stages.forEach(function(k){ grid.appendChild(h("div",{class:"kbcell",role:"group","aria-label":x[0].name + " \u00b7 " + stageLabel(k) + ": " + x[1][k].length + " agents"}, x[1][k].map(kanbanCard))); });
  });
  var fd = facDom();
  return [h("h2",{class:"sec"}, cfg.title), h("p",{class:"lead"}, cfg.intro, " ", evPills(FAC && FAC.src)),
    h("div",{class:"phsum"}, cfg.phases.map(function(p){ return h("div",{class:"phs ph-" + p.id}, h("b",null, String(arr(p.stages).reduce(function(n,k){ return n + (cnt[k] || 0); },0))), h("span",null, p.name), h("em",null, p.what || "")); })),
    h("div",{class:"filters"}, h("span",{class:"lbl note"},"Journey"), [["all","All journeys"]].concat(D.map(function(d){ return [d.id,d.name]; })).map(function(f){ var id = "plan-lane-" + f[0];
      return h("button",{type:"button",id:id,class:"btn","aria-pressed":String(state.planLane === f[0]),onclick:function(){ state.planLane = f[0]; refreshControl(id); }}, f[1]); }),
      h("label",{class:"chk",for:"plan-mvp"}, h("input",{type:"checkbox",id:"plan-mvp",checked:state.planMvp,onchange:function(e){ state.planMvp = e.target.checked; refreshControl("plan-mvp"); }}),"MVP only"),
      h("button",{type:"button",class:"btn",onclick:function(){ download(fileSlug() + "-agent-backlog.csv", planCsv(), "text/csv;charset=utf-8", stEl); }},"Export backlog (CSV)"),
      fd ? h("button",{type:"button",class:"btn",onclick:function(){ go("journeys",{d:D.indexOf(fd)}); }},"How the Agent Factory works") : null, stEl),
    cells.length ? h("div",{class:"kbwrap",tabindex:"0",role:"region","aria-label":"Scrollable agent board",onkeydown:function(e){
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") e.stopPropagation();
    }}, grid) : h("p",{class:"note",role:"status"},"No agent matches the filter."),
    h("h3",{class:"sub"},"What moves a card"), h("ol",{class:"clean dor"}, handoverDef().map(function(x){ return h("li",null, x[1]); })),
    h("p",{class:"note"},"Stages reflect workshop validation, design checks and lifecycle. Financial handover requires dated planning evidence, not approval or permission. Explicit existing build/release/operate stages are preserved even with gaps. Core drafts and workshops continue without FinOps. WIP limits are advisory, not approval. Exported CSV is a handover format: map destination fields explicitly for Azure Boards or GitHub Projects; no native import is performed.")];
}
function csvCell(v){
  var text = String(v === undefined || v === null ? "" : v);
  // Spreadsheet applications may ignore leading whitespace before a formula.
  if (/^[\s]*[=+\-@]/.test(text) || /^[\t\r\n]/.test(text)) text = "'" + text;
  return /[",;\r\n]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
}
function planCsv(){
  var H = handoverDef(), rows = [["ID","Title","Work Item Type","State","Area Path","Tags","Description","Acceptance Criteria","Owner"]];
  planAgents().forEach(function(x){ x[1].forEach(function(a){ var c = agentChecks(a), au = autonomyOf(a);
    rows.push([a.id,nameOf(a),"User Story",stageLabel(agentStage(a)),x[0].name,
      [isMvp(a) ? "MVP" : null,au ? "Autonomy L" + au.n : null,a.horizon || null,isFactory(x[0]) ? "Agent Factory" : null].filter(Boolean).join("; "),
      a.capability || "",H.filter(function(k){ return c[k[0]] !== 1; }).map(function(k){ return k[1]; }).join("; "),a.owner || ""]);
  }); });
  return rows.map(function(r){ return r.map(csvCell).join(","); }).join("\r\n") + "\r\n";
}

/* ---------------- Risks: ratings and verdicts use the existing workshop feedback model ---------------- */
var RCAT = {value:"Business value",adoption:"Adoption and change",data:"Data and integration",security:"Security and compliance",rai:"Responsible AI",technology:"Technology and platform",cost:"Cost",delivery:"Delivery and readiness",people:"People and organisation"};
var RORIGIN = {workshop:"Workshop","use case":"Use case",canon:"Hub canon","IT readiness":"IT readiness",author:"Authored"};
var RSTAT = [["open","Open"],["mitigating","Mitigating"],["accepted","Accepted"],["closed","Closed"],["rejected","Not a risk"]];
function riskLevel(sc){ return sc >= 15 ? "high" : sc >= 8 ? "medium" : "low"; }
function riskRating(v, fallback){ return typeof v === "number" && Number.isInteger(v) && v >= 1 && v <= 5 ? v : fallback; }
function rk(r){
  var n = note("val|risk|" + r.id), L = riskRating(n.likelihood,riskRating(r.likelihood,3)), I = riskRating(n.impact,riskRating(r.impact,3));
  return {L:L,I:I,score:L * I,status:String(n.status || r.status || "open").toLowerCase(),changed:!!(n.status || n.likelihood || n.impact || n.note)};
}
function riskItems(){ return arr(BP.risks && BP.risks.items).filter(function(r){ return r && r.id; }); }
function riskShown(r){ var k = rk(r); return (state.riskCat === "all" || r.category === state.riskCat) && (state.riskStatus === "all" || (k.status !== "closed" && k.status !== "rejected")); }
function openRisk(id){ state.riskSel = id; state.riskCat = "all"; state.riskStatus = "all"; go("risks"); var p = document.getElementById("rpanel"); if (p) p.focus(); }
function riskLink(id){ return riskItems().some(function(r){ return r.id === id; }) ? h("button",{type:"button",class:"pill linkp",onclick:function(){ openRisk(id); }}, id) : h("span",{class:"pill"}, id || TBC); }
function riskLinks(r){
  return h("div",{class:"btnrow rlinks"}, arr(r.journeys).map(function(id){ var d = domById(id); return d ? h("button",{type:"button",class:"optchip",onclick:function(){ go("journeys",{d:D.indexOf(d)}); }}, d.name) : null; }),
    arr(r.use_cases).map(function(id){ var u = ucById(id); return u ? h("button",{type:"button",class:"pill linkp",onclick:function(){ openUseCase(u); }}, id) : null; }),
    arr(r.agents).map(function(id){ return AG[id] ? agentChip(AG[id],true) : null; }));
}
function riskBox(r){
  var key = "val|risk|" + r.id, name = "rk-" + String(r.id).replace(/\W/g,"_"), n = note(key), k = rk(r);
  function update(id, patch){ setNote(key,patch); refreshControl(id,"risk-category"); var status = document.getElementById("risk-save"); if (status) status.textContent = "Saved"; }
  function sel(label,f){
    var id = name + "-" + f;
    return h("label",{class:"chk",for:id}, label + " ", h("select",{id:id,onchange:function(e){ var p = {}; p[f] = Number(e.target.value); update(id,p); }},
      [1,2,3,4,5].map(function(v){ return h("option",{value:String(v),selected:v === (f === "likelihood" ? k.L : k.I)}, String(v)); })));
  }
  return h("div",{class:"valbox"}, h("b",null,"Workshop rating"), h("span",{class:"note"}," \u00b7 saved in this browser; export from Discovery"),
    h("div",{class:"opts",role:"radiogroup","aria-label":"Status of " + r.id}, RSTAT.map(function(o){ var id = name + "-" + o[0];
      return h("label",{class:"opt",for:id}, h("input",{type:"radio",id:id,name:name,value:o[0],checked:k.status === o[0],onchange:function(){ update(id,{status:o[0]}); }}), o[1]); })),
    h("div",{class:"row"},sel("Likelihood","likelihood"),sel("Impact","impact")), h("label",{class:"note",for:name + "-note"},"Notes, owner and next step"),
    h("textarea",{id:name + "-note",oninput:function(e){ setNote(key,{note:e.target.value}); document.getElementById("risk-save").textContent = "Saved"; }}, n.note || ""),
    h("span",{class:"status",id:"risk-save",role:"status"}));
}
function riskPanel(r){
  var k = rk(r);
  return h("div",{class:"panel rpanel",id:"rpanel",tabindex:"-1","data-risk":r.id},
    h("div",{class:"ptitle"}, h("b",null, r.id + " \u00b7 " + r.title), h("span",{class:"pill rsc " + riskLevel(k.score)},"Score " + k.score)),
    h("div",{class:"btnrow"}, h("span",{class:"pill"},RCAT[r.category] || r.category || TBC),h("span",{class:"pill orig"},RORIGIN[r.origin] || r.origin || TBC)),
    r.description ? h("p",null,r.description) : null, h("p",null,h("b",null,"Mitigation \u00b7 "),r.mitigation || TBC),
    h("p",null,h("b",null,"Owner \u00b7 "),r.owner || TBC),riskLinks(r),evPills(r.src),
    arr(r.workshop_notes).length ? h("ul",{class:"clean workshop-risk-notes"},arr(r.workshop_notes).map(function(w){
      return h("li",{class:"note"},(w.date || "") + " \u00b7 " + (w.note || w.text || ""), " ",evPills(w.src));
    })) : null,riskBox(r));
}
function heatMap(items){
  var g = h("div",{class:"heat",role:"group","aria-label":"Risks by likelihood (rows, 5 at the top) and impact (columns)"});
  for (var L = 5; L >= 1; L--){
    g.appendChild(h("div",{class:"hax","aria-hidden":"true"},String(L)));
    for (var I = 1; I <= 5; I++){
      var list = items.filter(function(r){ var k = rk(r); return k.L === L && k.I === I; });
      g.appendChild(h("div",{class:"hc " + riskLevel(L * I),role:"group","aria-label":"Likelihood " + L + ", impact " + I + ": " + list.length + " risks"},
        list.map(function(r){ var id = "heat-" + r.id; return h("button",{type:"button",id:id,class:"hrk","aria-pressed":String(state.riskSel === r.id),title:r.title,onclick:function(){ state.riskSel = r.id; refreshControl(id); }}, r.id); })));
    }
  }
  g.appendChild(h("div",{class:"hax","aria-hidden":"true"}));
  for (var j = 1; j <= 5; j++) g.appendChild(h("div",{class:"hax","aria-hidden":"true"},String(j)));
  return h("div",{class:"heatwrap"},h("div",{class:"hyl"},"Likelihood"),g,h("div",{class:"hxl"},"Impact"));
}
function renderRisks(){
  var R = BP.risks || {}, all = riskItems(), items = all.filter(riskShown), cats = [], lv = {high:0,medium:0,low:0};
  all.forEach(function(r){ if (r.category && cats.indexOf(r.category) < 0) cats.push(r.category); });
  items.forEach(function(r){ lv[riskLevel(rk(r).score)]++; });
  var sel = items.filter(function(r){ return r.id === state.riskSel; })[0] || items[0];
  state.riskSel = sel ? sel.id : null;
  var out = [h("h2",{class:"sec"},R.title || "Risks, assumptions and open decisions"),h("p",{class:"lead"},R.intro || "Rate risks with the customer: likelihood and impact from 1 to 5. The register follows workshop ratings live.", " ",evPills(R.src)),
    h("div",{class:"idstrip"},h("span",{class:"pill acc"},items.length + " risks"),["high","medium","low"].map(function(k){ return h("span",{class:"pill rsc " + k},lv[k] + " " + k); })),
    h("div",{class:"filters"},h("label",{for:"risk-category"},"Category "),h("select",{id:"risk-category",onchange:function(e){ state.riskCat = e.target.value; refreshControl("risk-category"); }},
      [["all","All categories"]].concat(cats.map(function(c){ return [c,RCAT[c] || c]; })).map(function(o){ return h("option",{value:o[0],selected:state.riskCat === o[0]},o[1]); })),
      h("label",{class:"chk",for:"rk-closed"},h("input",{type:"checkbox",id:"rk-closed",checked:state.riskStatus === "all",onchange:function(e){ state.riskStatus = e.target.checked ? "all" : "active"; refreshControl("rk-closed"); }}),"Show closed")),
    h("div",{class:"riskgrid"},heatMap(items),sel ? riskPanel(sel) : h("p",{class:"note",role:"status"},"No risk matches the filter.")),
    h("h3",{class:"sub"},"Risk register"),h("div",{class:"tscroll"},h("table",{class:"t rreg"},h("thead",null,h("tr",null,["ID","Risk","Category","L","I","Score","Owner","Mitigation","Status"].map(function(c){ return h("th",{scope:"col"},c); }))),
      h("tbody",null,items.slice().sort(function(a,b){ return rk(b).score - rk(a).score; }).map(function(r){ var k = rk(r), id = "risk-row-" + r.id;
        return h("tr",{class:"riskrow" + (state.riskSel === r.id ? " sel" : "")},h("td",null,h("button",{type:"button",class:"pill linkp",id:id,"aria-pressed":String(state.riskSel === r.id),onclick:function(){ state.riskSel = r.id; refreshControl(id); }},r.id)),
          h("td",null,h("b",null,r.title),riskLinks(r),evPills(r.src)),h("td",null,RCAT[r.category] || r.category || TBC),h("td",null,String(k.L)),h("td",null,String(k.I)),
          h("td",null,h("span",{class:"pill rsc " + riskLevel(k.score)},String(k.score))),h("td",null,r.owner || TBC),h("td",null,r.mitigation || TBC),
          h("td",null,(RSTAT.filter(function(o){ return o[0] === k.status; })[0] || [0,k.status])[1],k.changed ? h("span",{class:"note"}," \u00b7 workshop") : null));
      }))))];
  var ass = Object.keys(ASSM).map(function(id){ return ASSM[id]; }).filter(function(a){ return String(note("val|ass|" + a.id).status || a.status || "").toLowerCase() !== "validated"; });
  var dec = arr((BP.it_readiness || {}).decisions).filter(function(x){ return rdStatus(x) !== "agreed"; });
  var adr = arr((BP.architecture || {}).decisions).filter(function(x){ return adrStatus(x) !== "agreed"; });
  out.push(h("h3",{class:"sub"},"Assumptions to confirm and decisions to take"),h("div",{class:"grid2"},
    h("div",{class:"panel"},h("h4",null,"Value and cost assumptions still open (" + ass.length + ")"),ul(ass.map(function(a){ var shown = presentedAssumption(a); return a.id + ": " + (shown.statement || shown.name || ""); }))),
    h("div",{class:"panel"},h("h4",null,"Decisions still open (" + (dec.length + adr.length) + ")"),
      ul(dec.map(function(x){ return x.id + ": " + (x.decision || x.q || x.item || x.text || ""); }).concat(adr.map(function(x){ return x.id + ": " + x.title; }))),pageLink("readiness"),pageLink("architecture"))));
  return out;
}

/* ---------------- Ontology: reviewed process projection, never opaque internal notes ---------------- */
function ontEnts(){ return arr(ONT && ONT.entity_types).filter(function(e){ return e && typeof e.id === "string" && e.id; }); }
function ontEnt(id){ return ontEnts().filter(function(e){ return e.id === id; })[0] || null; }
function ontVisible(e){ return !state.ontJourney || state.ontJourney === "all" || arr(e.journeys).indexOf(state.ontJourney) >= 0; }
function ontFeedbackIds(){
  return ["model"].concat(["entity_types","relationship_types","data_agents","operations_agents","data_products"].reduce(function(out, key){
    return out.concat(arr(ONT && ONT[key]).filter(function(x){ return x && x.id; }).map(function(x){ return x.id; }));
  }, []));
}
function ontStatus(x){ return note("val|onto|" + x.id).status || x.status || "hypothesis"; }
function ontChip(id){
  var e = ontEnt(id);
  return e ? h("button",{type:"button",class:"pill linkp",onclick:function(){
    state.ontJourney = "all"; state.ontSel = e.id; render();
    document.getElementById("ontology-node-" + e.id).focus({preventScroll:true});
    document.getElementById("opanel").scrollIntoView({block:"nearest"});
  }},e.name || id) : h("span",{class:"pill"},id);
}
/* A defensive projection for the new presentation/export paths. Do not recover
   redacted information from opaque notes, cached exports or caller metadata. */
function ontSafe(value){
  if (Array.isArray(value)) return value.map(ontSafe);
  if (!value || typeof value !== "object") return value;
  var out = {};
  Object.keys(value).forEach(function(k){
    if (["internal_notes","ttl","kit"].indexOf(k) < 0) out[k] = ontSafe(value[k]);
  });
  return out;
}
function ontFields(value){
  value = ontSafe(value);
  if (Array.isArray(value)) return h("ul",{class:"clean"},value.map(function(v){ return h("li",null,ontFields(v)); }));
  if (!value || typeof value !== "object") return has(value) ? String(value) : TBC;
  return h("dl",{class:"ont-fields"},Object.keys(value).map(function(k){
    return [h("dt",null,k.replace(/_/g," ")),h("dd",null,ontFields(value[k]))];
  }));
}
function ontStdText(st){
  st = st || {}; var en = st.entity == null ? "None" : String(st.entity);
  if (st.standard === "cdm") return "Common Data Model: " + en + (st.table ? " (Dataverse table " + st.table + ")" : "");
  if (st.standard === "dataverse") return "Dataverse, " + (st.folder || "Dynamics 365") + ": " + en + (st.table ? " (" + st.table + ")" : "");
  if (st.standard === "operations") return "Common Data Model, finance and operations: " + en;
  return "Custom extension (no standard entity)";
}
function ontGraph(){
  var ents = ontEnts().filter(ontVisible), width = 1040, positions = {};
  ents.forEach(function(e,i){ positions[e.id] = {x:20 + (i % 5) * 205,y:30 + Math.floor(i / 5) * 90}; });
  var svg = s("svg",{class:"osvg",viewBox:"0 0 " + width + " " + (Math.ceil(ents.length / 5) * 90 + 20),width:width,height:Math.ceil(ents.length / 5) * 90 + 20,role:"group","aria-label":"Ontology entity types and relationships"});
  arr(ONT.relationship_types).forEach(function(r){
    var a = positions[r.from], b = positions[r.to]; if (!a || !b) return;
    svg.appendChild(s("path",{class:"oedge",d:"M" + (a.x + 90) + "," + (a.y + 24) + " L" + (b.x + 90) + "," + (b.y + 24)},
      s("title",null,(r.label || r.name || r.id) + ": " + r.from + " to " + r.to + " (" + (r.cardinality || TBC) + ")")));
  });
  ents.forEach(function(e){
    var p = positions[e.id], id = "ontology-node-" + e.id, selected = state.ontSel === e.id;
    function pick(){ state.ontSel = selected ? null : e.id; refreshControl(id); }
    var g = s("g",{id:id,class:"onode" + (selected ? " sel" : ""),role:"button",tabindex:"0","aria-pressed":String(selected),"data-entity":e.id,
      "aria-label":"Entity type " + (e.name || e.id) + ", " + arr(e.properties).length + " properties, " + ontStatus(e),transform:"translate(" + p.x + "," + p.y + ")"},
      s("rect",{width:180,height:48,rx:6,class:e.source ? "" : "unbound"}),
      s("text",{x:10,y:20},wrapWords(e.name || e.id,24,1)[0]),
      s("text",{x:10,y:38,class:"osub"},arr(e.properties).length + " properties \u00b7 " + (e.source ? "bound" : "to bind")));
    g.addEventListener("click",pick);
    g.addEventListener("keydown",function(ev){ if (ev.key === "Enter" || ev.key === " "){ ev.preventDefault(); ev.stopPropagation(); pick(); } });
    svg.appendChild(g);
  });
  return h("div",{class:"owrap",tabindex:"0",role:"region","aria-label":"Locally scrollable ontology graph",onkeydown:function(ev){ if (/^Arrow/.test(ev.key)) ev.stopPropagation(); }},svg);
}
function ontPanel(e){
  var st = e.standard || {}, columns = st.attributes || {};
  return h("section",{class:"panel opanel",id:"opanel","data-entity":e.id,"aria-label":"Selected entity " + (e.name || e.id)},
    h("h3",null,e.name || e.id),h("p",null,e.description || TBC),statusPill(ontStatus(e)),evPills(e.src),
    h("p",null,ontStdText(st), " \u00b7 ", st.checked ? "checked" : "to verify", " \u00b7 ", e.source && (e.binding || {}).table ? e.binding.table : "Not bound yet \u2014 to bind"),
    dataTable(["Property","Type","Standard column","Key / notes"],arr(e.properties).concat(arr(e.timeseries)).map(function(p){
      return [p.name,p.type,columns[p.name] || TBC,(arr(e.key).indexOf(p.name) >= 0 ? "Key. " : "") + (p.description || "") + (p.unit ? " (" + p.unit + ")" : "")];
    }),"oproperties"),
    ontFields({synonyms:e.synonyms,source:e.source,binding:e.binding,standard:st}),
    h("h4",null,"Relationships"),arr(ONT.relationship_types).filter(function(r){ return r.from === e.id || r.to === e.id; }).map(function(r){
      return h("details",{class:"acc"},h("summary",null,r.label || r.name || r.id),ontChip(r.from)," \u2192 ",ontChip(r.to),ontFields(r),valBox("onto",r.id));
    }),
    valBox("onto",e.id));
}
function ontCards(key, cls){
  return h("div",{class:"ontology-cards"},arr(ONT[key]).map(function(x){
    return h("article",{class:"panel " + (cls || "")},h("h4",null,(x.id ? x.id + " \u00b7 " : "") + (x.name || x.title || x.item || "")),
      x.id ? statusPill(ontStatus(x)) : null,ontFields(x),
      ontFeedbackIds().indexOf(x.id) >= 0 ? h("details",{class:"acc"},h("summary",null,"Workshop verdict"),valBox("onto",x.id)) : null);
  }));
}
function ontLit(value){
  return '"' + String(value == null ? "" : value).replace(/\\/g,"\\\\").replace(/"/g,'\\"').replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t") + '"';
}
/* Mirrors ontology_lib.to_turtle, with parity checked against the actual Python
   artifact, not a second hand-authored golden. No runtime Python or network. */
function ontTurtle(){
  var meta = ONT.meta || {}, uri = meta.namespace_uri;
  if (!/^https?:\/\/[^\s<>"{}|\\^`]+[#/]$/.test(uri || "")){
    var slug = String(meta.short || meta.customer || "customer").trim().toLowerCase().replace(/[^A-Za-z0-9]+/g,"-").replace(/^-+|-+$/g,"") || "x";
    uri = "https://example.org/frontier/" + slug + "/ontology#";
  }
  var title = ONT.title || "Process ontology", version = meta.version === undefined ? "0.1" : meta.version;
  var L = ["@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .","@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .","@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .","@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
    "@prefix : <" + uri + "> .","","# " + title + " v" + version + " (" + (meta.status === undefined ? "hypothesis" : meta.status) + ")",
    "# Generated by the Frontier Envisioning plugin (frontier-process). Import into a new, empty ontology (preview) item.",
    "# Keys, data bindings, rules and metrics are configured in Fabric (see ontology.md).","",
    "<" + uri.replace(/[#/]+$/,"") + "> a owl:Ontology ;","  rdfs:label " + ontLit(title) + " ;","  owl:versionInfo " + ontLit(version) + " .",""];
  ontEnts().forEach(function(e){
    var st = e.standard || {}, parts = [":" + e.id + " a owl:Class","  rdfs:label " + ontLit(e.name || e.id)], desc = String(e.description || "").trim();
    if (arr(e.key).length) desc += (desc ? " " : "") + "Key: " + e.key.join(", ") + ".";
    if (Object.keys(st).length) desc += (desc ? " " : "") + ontStdText(st) + ".";
    if (desc) parts.push("  rdfs:comment " + ontLit(desc));
    var syn = arr(e.synonyms).slice(), short = String(st.entity || "").replace(/\s*\(.*?\)/g,"").trim();
    if (["cdm","dataverse"].indexOf(st.standard) >= 0 && short && syn.concat([e.name,e.id]).map(function(x){ return String(x).toLowerCase(); }).indexOf(short.toLowerCase()) < 0) syn.push(short);
    if (syn.length) parts.push("  skos:altLabel " + syn.map(ontLit).join(", "));
    if (e.base) parts.push("  rdfs:subClassOf :" + e.base);
    L.push(parts.join(" ;\n") + " .");
    arr(e.properties).concat(arr(e.timeseries)).forEach(function(p){
      var types = {string:"string",integer:"integer",double:"double",boolean:"boolean",datetime:"dateTime"};
      var pp = [":" + e.id + "_" + p.name + " a owl:DatatypeProperty","  rdfs:label " + ontLit(p.name),"  rdfs:domain :" + e.id,"  rdfs:range xsd:" + (types[p.type] || "string")];
      var nt = String(p.description || "").trim(), col = (st.attributes || {})[p.name];
      if (col) nt += (nt ? " " : "") + "Standard column: " + col + ".";
      if (arr(e.timeseries).some(function(t){ return JSON.stringify(t) === JSON.stringify(p); })) nt += (nt ? " " : "") + "Time series" + (p.unit ? " (" + p.unit + ")" : "") + ": bind with a timestamp column.";
      if (nt) pp.push("  rdfs:comment " + ontLit(nt));
      L.push(pp.join(" ;\n") + " .");
    }); L.push("");
  });
  arr(ONT.relationship_types).forEach(function(r){
    var desc = String(r.description || "").trim();
    desc += (desc ? " " : "") + "Cardinality " + (r.cardinality === undefined ? "n:1" : r.cardinality) + ".";
    L.push([":" + r.id + " a owl:ObjectProperty","  rdfs:label " + ontLit(r.label || r.name),"  rdfs:domain :" + r.from,"  rdfs:range :" + r.to,"  rdfs:comment " + ontLit(desc)].join(" ;\n") + " .");
  });
  return L.join("\n").trimEnd() + "\n";
}
function ontMarkdown(kind){
  var sections = kind === "data-agents" ? ["sources","sources_doc","entity_types","data_agents","operations_agents"]
    : kind === "data-products" ? ["data_product_standard","domains","semantic_models","data_products","sources","sources_doc"]
    : ["intro","meta","stack","namespaces","entity_types","relationship_types","process","data_architecture","domains","semantic_models","data_product_standard","data_products","sources","sources_doc","rules","metrics","data_agents","operations_agents","build_steps","readiness","risks","decisions"];
  function md(value){ return String(value == null ? TBC : value).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/([\\`*[\]|])/g,"\\$1"); }
  function lines(value, indent){
    if (Array.isArray(value)) return value.map(function(v){ return indent + "-\n" + lines(v,indent + "  "); }).join("\n");
    if (value && typeof value === "object") return Object.keys(value).map(function(k){ return indent + "- **" + md(k) + "**: " + (value[k] && typeof value[k] === "object" ? "\n" + lines(value[k],indent + "  ") : md(value[k]).replace(/\r?\n/g,"\n" + indent + "  ")); }).join("\n");
    return indent + md(value);
  }
  var out = ["# " + md(ONT.title || "Process ontology"),"","Fabric ontology and agent integrations are Preview. Native Fabric import and binding require manual verification; this download is a design handover, not an import success.",""];
  sections.forEach(function(k){ if (has(ONT[k])) out.push("## " + k.replace(/_/g," ").replace(/^\w/,function(c){ return c.toUpperCase(); }),"",lines(ontSafe(ONT[k]),""),""); });
  out.push("Verify standard mappings marked to verify and preserve all source/access restrictions. No budget or purchase approval is implied.");
  return out.join("\n") + "\n";
}
function renderOntology(){
  var ents = ontEnts(), stEl = h("span",{class:"status",role:"status"});
  if (!state.ontJourney) state.ontJourney = "all";
  if (!ontEnt(state.ontSel) || !ontVisible(ontEnt(state.ontSel))) state.ontSel = null;
  var sel = ontEnt(state.ontSel);
  var unknown = Object.keys(NOTES).filter(function(k){ return k.indexOf("val|onto|") === 0 && ontFeedbackIds().indexOf(k.slice(9)) < 0; });
  var out = [h("h2",{class:"sec"},ONT.title || "Process ontology"),h("p",{class:"lead"},ONT.intro || "Business entities, properties and relationships grounded in OneLake."),
    h("p",{class:"ontology-warning",role:"note"},"Fabric ontology and agent integrations are Preview. Native Fabric import is manual: verify mappings, permissions, bindings and provider availability. The GA skill wrapper does not change provider Preview status."),
    unknown.length ? h("p",{role:"status"},"Unknown ontology feedback IDs retained for review: " + unknown.map(function(k){ return k.slice(9); }).join(", ")) : null,
    h("div",{class:"btnrow"},["ontology.ttl","ontology.md","data-agents.md","data-products.md"].map(function(name){
      return h("button",{type:"button",class:"btn",onclick:function(){ download(fileSlug() + "-" + name,name === "ontology.ttl" ? ontTurtle() : ontMarkdown(name.replace(".md","")),name === "ontology.ttl" ? "text/turtle;charset=utf-8" : "text/markdown;charset=utf-8",stEl); }},"Download " + name);
    }),stEl),
    h("h3",{class:"sub"},"Entity types and relationships"),
    h("div",{class:"filters"},[["all","All journeys"]].concat(D.filter(function(d){ return ents.some(function(e){ return arr(e.journeys).indexOf(d.id) >= 0; }); }).map(function(d){ return [d.id,d.name]; })).map(function(f){
      var id = "ontology-journey-" + f[0];
      return h("button",{id:id,type:"button",class:"btn","aria-pressed":String(state.ontJourney === f[0]),onclick:function(){ state.ontJourney = f[0]; refreshControl(id); }},f[1]);
    })),
    ontGraph(),sel ? ontPanel(sel) : h("p",{role:"status"},"No entity type selected."),
    h("h3",{class:"sub"},"Common Data Model table and column mappings"),
    dataTable(["Entity","Standard entity","Table","Match / role","Columns mapped","Checked"],ents.filter(ontVisible).map(function(e){
      var st = e.standard || {};
      return [ontChip(e.id),ontStdText(st),st.table || "custom table",(st.match || TBC) + " / " + (st.role || TBC),String(st.mapped == null ? TBC : st.mapped) + " of " + arr(e.properties).length,
        h("span",{class:st.checked || st.standard === "custom" ? "" : "mapping-gap"},st.standard === "custom" ? "custom" : st.checked ? "checked" : "to verify")];
    }),"ocdm"),
    h("h3",{class:"sub"},"Process and semantic data layer"),ontFields(ONT.process),
    h("div",{class:"olayers"},["Bronze","Silver","Gold"].map(function(layer){ return h("div",{class:"panel"},h("h4",null,layer),layer === "Bronze" ? "Sources as received" : layer === "Silver" ? "Conformed business entities and bindings" : "Semantic models and governed data products"); })),
    ontFields(ONT.data_architecture),h("h3",{class:"sub"},"Fabric and governance domains"),ontCards("domains"),
    h("h3",{class:"sub"},"Semantic models"),ontCards("semantic_models"),
    h("h3",{class:"sub"},"Data product governance"),ontFields(ONT.data_product_standard),ontCards("data_products","oproduct"),
    h("h3",{class:"sub"},"Sources and access restrictions"),ontCards("sources"),ontFields(ONT.sources_doc),
    h("h3",{class:"sub"},"Data agents"),ontCards("data_agents"),
    h("h3",{class:"sub"},"Operations agents"),ontCards("operations_agents"),
    h("h3",{class:"sub"},"Rules"),ontCards("rules"),h("h3",{class:"sub"},"Metrics"),ontCards("metrics"),
    h("h3",{class:"sub"},"Build steps"),ontFields(ONT.build_steps),
    h("h3",{class:"sub"},"Readiness"),ontCards("readiness"),h("h3",{class:"sub"},"Risks and decisions"),ontCards("risks"),ontCards("decisions"),
    h("h3",{class:"sub"},"Workshop verdict on the ontology"),valBox("onto","model")];
  /* Keep the graph and selected card available; substantial design sections use
     native keyboard-accessible disclosures instead of a wall of expanded data. */
  var result = [], section = null;
  out.forEach(function(el){
    if (el && el.tagName === "H3" && el.textContent !== "Entity types and relationships"){
      section = h("details",{class:"acc ontsection"},h("summary",null,el));
      result.push(section);
    } else if (section) add(section,el);
    else result.push(el);
  });
  return result;
}

/* ---------------- render ---------------- */
var RENDER = { overview:renderOverview, org:renderOrg, blueprint:renderBlueprint, journeys:function(){ var o = renderJourney(); return isFactory(dom()) ? o.concat(renderFactorySections()) : o; }, attendees:renderAttendees, readiness:renderReadiness, agents:renderAgents, identity:renderIdentity, architecture:renderArchitecture, usecases:renderUseCases, finops:renderFinops, discovery:renderDiscovery, roadmap:renderRoadmap, evidence:renderEvidence, prd:renderPrd, plan:renderPlan, risks:renderRisks, ontology:renderOntology };
function render(scrollTop){
  if (ORDER.indexOf(state.view) < 0) state.view = ORDER[0];
  if (state.d >= D.length) state.d = 0;
  var d = dom();
  setDomainColor(DOMAIN_VIEWS.indexOf(state.view) >= 0 && d.color ? d.color : ACCENT);
  renderRail(); renderCrumb(); renderSubnav();
  var v = document.getElementById("view");
  var out;
  try { out = RENDER[state.view](); if (previewPresent()) out = [previewNotice()].concat(out); }
  catch (e) { out = [h("div",{class:"empty"}, h("b",null,"This view could not be drawn."), h("p",null, String(e && e.message || e)))]; if (window.console) console.error(e); }
  var selectedJourney = document.querySelector('#subnav [role="tab"][aria-selected="true"]');
  var content = selectedJourney ? h("section",{id:"journey-panel",role:"tabpanel","aria-labelledby":selectedJourney.id}, out) : out;
  v.replaceChildren(); add(v, content); v.appendChild(pager());
  /* Tables without an interactive cell still need keyboard scrolling at 320px.
     Stop arrow navigation here, while preserving the browser's scroll default. */
  v.querySelectorAll(".tscroll").forEach(function(region,i){
    region.tabIndex = 0;
    region.setAttribute("role","region");
    var headers = Array.from(region.querySelectorAll("thead th")).map(function(th){ return th.textContent; });
    region.setAttribute("aria-label","Scrollable table " + (i + 1) + (headers.length ? ": " + headers.join(", ") : ""));
    region.addEventListener("keydown",function(ev){ if (/^Arrow/.test(ev.key)) ev.stopPropagation(); });
  });
  writeHash();
  if (scrollTop) { try { window.scrollTo(0, 0); v.focus({preventScroll:true}); } catch (e) {} }
}
function renderFooter(){
  var f = document.getElementById("footnote");
  f.replaceChildren(h("span",null, M.footnote || ("Prepared by " + (M.prepared_by || "Microsoft") + " for " + (M.customer || "the customer") + ". Hypotheses are starting points for discussion, not commitments.")),
    h("br"), h("span",null, "Generated " + (M.generated || M.date || "") + " with the Frontier Envisioning plugin" + (M.plugin_version ? " v" + M.plugin_version : "") + ". Product names and availability reflect the sources cited; verify before decisions."));
}
window.addEventListener("hashchange", function(){ readHash(); render(true); });
readHash();
renderHeader(); renderBanner(); renderFooter();
render(false);
})();
