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
var ASSM = {};
arr(VC && VC.assumptions).concat(arr(FO && FO.assumptions)).forEach(function(a){ if (a && a.id && !ASSM[a.id]) ASSM[a.id] = a; });
function num(x){ return typeof x === "number" && isFinite(x); }
function grp(n, dec){ var p = Math.abs(n).toFixed(dec || 0).split("."); p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ","); return (n < 0 ? "\u2212" : "") + p.join("."); }
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
function valueOf(u){ var b = u && u.business_value; return b && typeof b === "object" && !Array.isArray(b) ? b : null; }
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
function icon(k){ var sp = document.createElement("span"); sp.className = "ic-wrap"; sp.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (ICON[k] || "") + '</svg>'; return sp; }

/* ---------------- views and state ---------------- */
var VIEWS = [
  {id:"overview", label:"Overview", part:"Vision"},
  {id:"org", label:"Org model", part:"Vision"},
  {id:"blueprint", label:"Blueprint", part:"Vision"},
  {id:"journeys", label:"Journeys", part:"Vision"},
  {id:"attendees", label:"Attendees", part:"Vision", need:function(){ return has(BP.attendees && BP.attendees.people); }},
  {id:"agents", label:"Agents", part:"Design"},
  {id:"identity", label:"Agent identity", part:"Design", need:function(){ return hasIdentity(); }},
  {id:"architecture", label:"Target architecture", part:"Design", need:function(){ return has(BP.architecture); }},
  {id:"usecases", label:"Use cases", part:"Design", need:function(){ return UCS.length > 0; }},
  {id:"readiness", label:"IT readiness", part:"Design", need:function(){ return !!(BP.it_readiness && typeof BP.it_readiness === "object"); }},
  {id:"finops", label:"FinOps", part:"Design", need:function(){ return !!FO; }},
  {id:"discovery", label:"Discovery", part:"Workshop", need:function(){ return D.some(function(d){ return has(d.discovery); }); }},
  {id:"roadmap", label:"Roadmap", part:"Workshop", need:function(){ return has(BP.next_steps) || has(BP.mvp_options) || D.some(function(d){ return has(d.horizon_plan); }); }},
  {id:"evidence", label:"Evidence", part:"Workshop", need:function(){ return has(BP.evidence); }}
];
var PARTS = {Vision:"Part 1 \u00b7 Vision", Design:"Part 2 \u00b7 Design", Workshop:"Part 3 \u00b7 Workshop"};
var ORDER = VIEWS.filter(function(v){ return !v.need || v.need(); }).map(function(v){ return v.id; });
function viewMeta(id){ for (var i = 0; i < VIEWS.length; i++) if (VIEWS[i].id === id) return VIEWS[i]; return VIEWS[0]; }
var state = { view:"overview", d:0, agent:null, uc:null, archTab:null, lz:"P", lzLens:null, fstep:0, adrFilter:"all", adr:null, orgStage:3, orgDomain:null, labels:true, badges:true, discFilter:"all" };
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
  st.setProperty("--domain", c);
  st.setProperty("--domain-soft", DARK ? soft(c, .2) : soft(c, .1));
}

/* ---------------- chrome ---------------- */
function renderRail(){
  var r = document.getElementById("rail");
  r.replaceChildren();
  var lastPart = null;
  ORDER.forEach(function(id){
    var vm = viewMeta(id);
    if (vm.part !== lastPart){ r.appendChild(h("div",{class:"grp"}, PARTS[vm.part])); lastPart = vm.part; }
    r.appendChild(h("button",{type:"button","aria-current": state.view === id ? "page" : null, onclick:function(){ go(id); }}, icon(id), h("span",null, vm.label)));
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
  c.replaceChildren(h("span",null, PARTS[vm.part]), h("span",{"aria-hidden":"true"},"\u203a"), h("b",null, vm.label), h("span",{class:"note"}, "(" + (i + 1) + " of " + ORDER.length + " \u00b7 arrow keys to move)"));
}
function renderSubnav(){
  var t = document.getElementById("subnav");
  t.replaceChildren();
  if (DOMAIN_VIEWS.indexOf(state.view) < 0 || D.length < 1) return;
  t.appendChild(h("span",{class:"lbl"}, M.domain_label || "Journey"));
  D.forEach(function(d, i){
    t.appendChild(h("button",{type:"button",role:"tab",class:"tab",style:"--d:" + d.color,"aria-selected": i === state.d ? "true" : "false",
      onclick:function(){ state.d = i; if (state.view === "agents") state.agent = null; render(); }},
      h("span",{class:"num",style:"background:" + d.color}, String(i + 1)), d.name));
  });
}
function pager(){
  var i = ORDER.indexOf(state.view), prev = ORDER[i-1], next = ORDER[i+1];
  return h("div",{class:"pager"},
    prev ? h("button",{type:"button",class:"btn",onclick:function(){ go(prev); }}, "\u2190 " + viewMeta(prev).label) : h("span"),
    next ? h("button",{type:"button",class:"btn primary",onclick:function(){ go(next); }}, viewMeta(next).label + " \u2192") : h("span"));
}

/* ---------------- drawer ---------------- */
var drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim"), lastFocus = null;
function openDrawer(title, sub, body){
  lastFocus = document.activeElement;
  document.getElementById("drawer-title").textContent = title || "";
  document.getElementById("drawer-sub").textContent = sub || "";
  var b = document.getElementById("drawer-body");
  b.replaceChildren(); add(b, body);
  b.scrollTop = 0;
  drawer.classList.add("open"); scrim.classList.add("open"); drawer.setAttribute("aria-hidden","false");
  setTimeout(function(){ try { document.getElementById("drawer-close").focus(); } catch (e) {} }, 30);
}
function closeDrawer(){
  drawer.classList.remove("open"); scrim.classList.remove("open"); drawer.setAttribute("aria-hidden","true");
  if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (e) {}
}
document.getElementById("drawer-close").addEventListener("click", closeDrawer);
scrim.addEventListener("click", closeDrawer);
document.addEventListener("keydown", function(e){
  if (e.key === "Escape" && drawer.classList.contains("open")) { closeDrawer(); return; }
  var tg = e.target && e.target.tagName;
  if (tg === "INPUT" || tg === "TEXTAREA" || tg === "SELECT" || drawer.classList.contains("open")) return;
  if (e.altKey || e.ctrlKey || e.metaKey) return;
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
      idIcon(a, "avatar idicon") || h("div",{class:"avatar",style:"background:" + (d.color || ACCENT)}, initials(orgLabel(a)))),
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

/* ---------------- org model (HAIRO) ---------------- */
function orgSvg(){
  var W = 1000, C = 500, R1 = 165, R2 = 292, R3 = 440;
  function P(r, a){ return [C + r * Math.cos(a), C + r * Math.sin(a)]; }
  function arcPath(r, a0, a1, rev){
    var p0 = P(r, a0), p1 = P(r, a1), large = (a1 - a0) > Math.PI ? 1 : 0;
    return rev ? "M" + p1[0].toFixed(1) + " " + p1[1].toFixed(1) + " A" + r + " " + r + " 0 " + large + " 0 " + p0[0].toFixed(1) + " " + p0[1].toFixed(1)
               : "M" + p0[0].toFixed(1) + " " + p0[1].toFixed(1) + " A" + r + " " + r + " 0 " + large + " 1 " + p1[0].toFixed(1) + " " + p1[1].toFixed(1);
  }
  var svg = s("svg",{viewBox:"0 0 " + W + " " + W, class:"orgsvg", role:"img", "aria-label":"Hybrid organisation model: human leaders in the centre, lead agents in the inner ring, specialist agents in the outer ring, grouped by " + (M.domain_label_plural || "journeys")});
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
    arcG.appendChild(s("text",{class:"dlabel", "text-anchor":"middle", style:"fill:" + d.color}, tp));
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
      var g = s("g",{class:"node" + (dim ? " dim" : ""), opacity: rs.faded ? .35 : null});
      if (a.mvp) g.appendChild(s("circle",{cx:p[0], cy:p[1], r:27, fill:"none", stroke:"var(--accent)", "stroke-width":3}));
      g.appendChild(s("circle",{class:"ring", cx:p[0], cy:p[1], r:21, fill:"var(--panel)", stroke:d.color, "stroke-width":2.5, "stroke-dasharray":rs.dash}));
      g.appendChild(s("text",{x:p[0], y:p[1] + 4.5, "text-anchor":"middle", style:"font-size:12.5px;font-weight:700;fill:" + d.color}, initials(orgLabel(a))));
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
      var g2 = s("g",{class:"node" + (dim ? " dim" : ""), opacity: rs2.faded ? .35 : null});
      if (o.mvp) g2.appendChild(s("circle",{cx:lp[0], cy:lp[1], r:38, fill:"none", stroke:"var(--accent)", "stroke-width":3}));
      if (rs2.dash) g2.appendChild(s("circle",{cx:lp[0], cy:lp[1], r:33, fill:"none", stroke:d.color, "stroke-width":2, "stroke-dasharray":"5 4"}));
      g2.appendChild(s("circle",{class:"ring", cx:lp[0], cy:lp[1], r:28, fill:d.color, stroke:"var(--panel)", "stroke-width":2}));
      g2.appendChild(s("text",{x:lp[0], y:lp[1] + 5, "text-anchor":"middle", style:"font-size:14px;font-weight:700;fill:#fff"}, initials(orgLabel(o))));
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
    gc.appendChild(s("text",{x:C, y:cy + 5, "text-anchor":"middle", style:"font-size:13px;font-weight:700;fill:#fff"}, "+ " + cta));
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
    h("button",{type:"button",class:"tab",style:"--d:var(--ink)","aria-selected": !state.orgDomain ? "true" : "false", onclick:function(){ state.orgDomain = null; render(); }}, h("span",{class:"num",style:"background:var(--grey)"},"\u2217"), "All"),
    D.map(function(d){ return h("button",{type:"button",class:"tab",style:"--d:" + d.color,"aria-selected": state.orgDomain === d.id ? "true" : "false", onclick:function(){ state.orgDomain = state.orgDomain === d.id ? null : d.id; render(); }}, h("span",{class:"num",style:"background:" + d.color}, String(D.indexOf(d) + 1)), d.short_name || d.name); }));
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
        return h("tr",null, h("td",null, h("button",{type:"button",class:"agentlink",style:"all:unset;cursor:pointer;font-weight:700;color:" + a._d.color, onclick:function(){ openAgent(a.id); }}, h("span",{class:"anm",style:"display:inline-flex"}, idIcon(a), nameOf(a)))),
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
function valBox(kind, id){
  var k = "val|" + kind + "|" + id, n = note(k);
  var name = "v-" + kind + "-" + id.replace(/\W/g,"_");
  var opts = [["validated","Validated"],["adjusted","Adjust"],["rejected","Reject"],["open","Open"]];
  var stEl = h("span",{class:"status",role:"status"});
  return h("div",{class:"valbox"},
    h("b",null,"Workshop validation"), h("span",{class:"note"}," \u00b7 saved in this browser; export it from Discovery"),
    h("div",{class:"opts",role:"radiogroup","aria-label":"Validation status"}, opts.map(function(o){
      var rid = name + "-" + o[0];
      return h("label",{class:"opt",for:rid}, h("input",{type:"radio",id:rid,name:name,value:o[0],checked: n.status === o[0] ? true : null,onchange:function(){ setNote(k,{status:o[0]}); stEl.textContent = "Saved"; }}), o[1]);
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
    h("h3",{class:"sub"},"Agentic trigger canvas"), canvas,
    h("h3",{class:"sub"},"Readiness \u00b7 the seven declarations"), declBox,
    h("h3",{class:"sub"},"Role profile"), profileSections(a),
    h("h3",{class:"sub"},"Validate in the workshop"), valBox("agent", a.id));
  return [h("h2",{class:"sec"},"Agents \u00b7 " + d.name), h("p",{class:"lead"},"Each agent is described like a role: a trigger canvas for the work it does, seven declarations that make it governable, and a role profile that becomes its instructions."), h("div",{class:"agwrap"}, list, main)];
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
        arr(p.contributions).length ? h("ul",{class:"clean contrib"}, p.contributions.map(function(c){ return h("li",null, itemText(c)); })) : null,
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
  var cost = FO && arr(FO.agents).some(function(x){ return x.id === a.id; }) ? (FO.verify ? .5 : 1) : 0;
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
    idIcon(a, "aicon") || h("span",{class:"aicon ini",style:"background:" + (d.color || ACCENT)}, initials(shortOf(a))), h("span",{class:"agn"}, shortOf(a)), isMvp(a) ? h("span",{class:"pill acc"},"MVP") : null);
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
  var H = arr(FAC.handover); if (!H.length) return null;
  var ags = ALL.filter(function(a){ return !isFactory(a._d) && (isMvp(a) || STAGE_ORDER.indexOf(agentStage(a)) >= 1); });
  if (!ags.length) return h("p",{class:"note"},"No agent is validated yet: the handover check fills once the workshop validates the MVP agents.");
  var mark = function(v){ return v === 1 ? h("span",{class:"hv ok",title:"Done"},"\u2713") : (v ? h("span",{class:"hv part",title:"Partly done"},"\u25d0") : h("span",{class:"hv no",title:"Missing"},"\u2715")); };
  return h("div",{class:"tscroll"}, h("table",{class:"t hand"},
    h("thead",null, h("tr",null, h("th",{scope:"col"},"Agent"), H.map(function(x){ return h("th",{scope:"col"}, x[1]); }), h("th",{scope:"col"},"Ready for build"))),
    h("tbody",null, ags.map(function(a){
      var c = agentChecks(a), ok = H.every(function(x){ return c[x[0]] === 1; });
      return h("tr",null, h("td",null, agentChip(a, true)), H.map(function(x){ return h("td",{class:"c"}, mark(c[x[0]])); }), h("td",null, h("span",{class:"pill " + (ok ? "val" : "open")}, ok ? "Ready" : "Not yet")));
    }))));
}
function factorySteps(){
  var S = arr(FAC.steps); if (!S.length) return null;
  if (!(state.fstep >= 0 && state.fstep < S.length)) state.fstep = 0;
  var st = S[state.fstep];
  var fa = String(st.agent || "").split(" \u00b7 ").map(function(n){ return agentByName(n.replace(/\s*\(.*\)$/, "")); }).filter(Boolean);
  var LOOP = {plan:"Plan gates", dev:"DEV loop", gate:"Human-in-the-loop gate", ops:"OPS loop"};
  return [h("div",{class:"fsteps",role:"tablist","aria-label":"Idea-to-agent steps"}, S.map(function(x, i){
      return h("button",{type:"button",role:"tab",class:"fstep lp-" + x.loop,"aria-selected": i === state.fstep ? "true" : "false",onclick:function(){ state.fstep = i; render(); }}, h("span",{class:"n"}, x.id), h("span",null, x.name));
    })),
    h("div",{class:"fdetail lp-" + st.loop},
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
    var a = x[0]; return h("button",{type:"button",class:"rolec",onclick:function(){ openAgent(a.id); }}, idIcon(a, "aicon lg") || h("span",{class:"aicon lg ini",style:"background:" + ((a._d || {}).color || ACCENT)}, initials(shortOf(a))), h("b",null, nameOf(a)), h("small",null, a.capability || a.mission || ""), h("span",{class:"note"}, h("b",null,"Decides: "), x[1]));
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
  else { g.appendChild(s("rect",{x:x, y:y, width:z, height:z, rx:6, fill:col || ACCENT})); g.appendChild(s("text",{x:x + z / 2, y:y + z / 2 + 4, "text-anchor":"middle", class:"lzini"}, initials(shortOf(a)))); }
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
      h("div",{class:"lzph"}, h("span",{class:"lzbadge2",style:"background:" + (d.color || ACCENT)}, "F"), h("div",null, h("h3",null, (d.name || a.domain) + " landing zone"), h("div",{class:"note"}, d.journey_name || "")), h("button",{type:"button",class:"btn",onclick:function(){ go("journeys",{d:di}); }},"Open journey")),
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
    h("div",{class:"filters"}, [["all","All \u00b7 " + list.length]].concat(Object.keys(counts).map(function(k){ return [k, k.charAt(0).toUpperCase() + k.slice(1) + " \u00b7 " + counts[k]]; })).map(function(x){ return h("button",{type:"button",class:"tab","aria-selected": f === x[0] ? "true" : "false",onclick:function(){ state.adrFilter = x[0]; render(); }}, x[1]); })),
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
    h("div",{class:"atabs",role:"tablist","aria-label":"Target architecture views"}, tabs.map(function(t){ return h("button",{type:"button",role:"tab",class:"atab","aria-selected": t[0] === state.archTab ? "true" : "false",onclick:function(){ state.archTab = t[0]; render(); }}, t[1]); }))];
  if (state.archTab === "lz") return out.concat(renderLandingZone());
  if (state.archTab === "decisions") return out.concat(renderDecisions(A));
  return out.concat(renderArchitectureClassic(state.archTab));
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
    h("span",{class:"n",style:"background:" + (d.color || ACCENT)}, String(u.id)), h("h2",null, u.name || ""),
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
  return h("span",{class:"pill " + m[0]}, m[1] + (n ? " \u00b7 in the workshop" : ""));
}
function srcType(a){
  var t = {customer:"Customer-stated", measured:"Measured", benchmark:"Benchmark (prior)", hypothesis:"Hypothesis"}[a.source_type] || a.source_type || "Hypothesis";
  return t + (a.confidence ? " \u00b7 " + a.confidence + " confidence" : "");
}
function assBox(a){
  var k = "val|ass|" + a.id, n = note(k), name = "a-" + String(a.id).replace(/\W/g,"_");
  var st = h("span",{class:"status",role:"status"});
  var opts = [["validated","Confirm"],["adjusted","Adjust"],["rejected","Reject"],["open","Open"]];
  return h("div",{class:"assbox"},
    h("div",{class:"opts",role:"radiogroup","aria-label":"Workshop verdict for " + a.id}, opts.map(function(o){
      var rid = name + "-" + o[0];
      return h("label",{class:"opt",for:rid}, h("input",{type:"radio",id:rid,name:name,value:o[0],checked: n.status === o[0] ? true : null,onchange:function(){ setNote(k,{status:o[0]}); st.textContent = "Saved"; }}), o[1]);
    })),
    h("input",{type:"number",step:"any",class:"assval","aria-label":"Agreed value for " + a.id + (a.unit ? " in " + a.unit : ""),placeholder:"Agreed value" + (a.unit === "share" ? " (0-1)" : ""),value: num(n.value) ? String(n.value) : null,
      oninput:function(e){ var v = e.target.value; setNote(k,{value: v === "" ? null : +v}); st.textContent = "Saved"; }}),
    h("input",{type:"text",class:"assnote","aria-label":"Note for " + a.id,placeholder:"Who said it, source",value: n.note || null,oninput:function(e){ setNote(k,{note:e.target.value}); st.textContent = "Saved"; }}),
    st);
}
function assTable(list, effect){
  if (!list.length) return null;
  return h("div",{class:"tscroll"}, h("table",{class:"t asst"},
    h("thead",null, h("tr",null, ["Assumption","Base (low \u2013 high)","Source","Owner and question"].concat(effect ? ["Effect on NPV"] : []).concat(["Workshop"]).map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, list.map(function(a){
      return h("tr",null,
        h("td",null, h("b",null, a.id + (a.rank ? " \u00b7 #" + a.rank : "")), h("div",null, a.statement || ""), arr(a.use_cases).length ? h("div",{class:"note"}, a.use_cases.join(" \u00b7 ")) : null, a.note ? h("div",{class:"note"}, a.note) : null),
        h("td",{class:"nowrap"}, h("b",null, fmtA(a.base, a.unit)), h("div",{class:"note"}, fmtA(a.low, a.unit), " \u2013 ", fmtA(a.high, a.unit))),
        h("td",null, srcType(a), " ", evPills(a.src)),
        h("td",null, a.owner ? h("b",null, a.owner) : null, a.question ? h("div",{class:"note"}, a.question) : null),
        effect ? h("td",{class:"nowrap"}, num(a.swing_npv) ? chf(a.swing_npv, true) : "\u2014") : null,
        h("td",null, assPill(a), assBox(a)));
    }))));
}
function assList(list){
  return h("div",{class:"asslist"}, list.map(function(a){
    return h("div",{class:"assrow"},
      h("div",null, h("b",null, a.id), " ", a.statement || "", " ", assPill(a)),
      h("div",{class:"note"}, "Base ", h("b",null, fmtA(a.base, a.unit)), " (", fmtA(a.low, a.unit), " \u2013 ", fmtA(a.high, a.unit), ") \u00b7 ", srcType(a), a.owner ? " \u00b7 owner: " + a.owner : ""),
      a.question ? h("div",{class:"note"}, "\u201c" + a.question + "\u201d") : null,
      assBox(a));
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
    assList(arr(v.assumptions).map(function(id){ return ASSM[id]; }).filter(Boolean)));
}
function matrixLegend(){
  return h("p",{class:"note mxlegend"}, h("span",{class:"lg-size"}), "Bubble size = value per year (base case)", h("span",{class:"lg-dash"}), "dashed ring = value still a hypothesis \u00b7 dark ring = MVP candidate \u00b7 use cases without a value case keep the standard size");
}
function valueSection(){
  var T = VC.totals || {}, q = arr(VC.questions);
  var rows = UCS.filter(function(u){ return valueOf(u); });
  var top = q.map(function(id){ return ASSM[id]; }).filter(Boolean);
  var rest = arr(VC.assumptions).filter(function(a){ return q.indexOf(a.id) < 0; });
  return [
    h("h3",{class:"sub"},"Business value \u00b7 a hypothesis until the workshop confirms it"),
    h("p",{class:"note"}, "Per year at full adoption, in " + curr() + ". Economic view = cash + realised capacity; the budget view counts cash only; risk reduction is shown separately. NPV over " + (VC.horizon_years || 3) + " years at " + pct(VC.discount_rate, 1) + ". Ranges combine the effects of the individual assumptions."),
    h("div",{class:"vkpis"}, vk("Value per year", chf(T.economic_year, true), "economic view, base"), vk("Cash per year", chf(T.budget_year, true), "budget view"),
      vk("Cost per year", chf(T.cost_year, true), "run cost" + (T.build ? " + " + chf(T.build, true) + " build" : "")), vk("NPV", chf(T.npv, true), (VC.horizon_years || 3) + " years, economic view"),
      vk("NPV, cash only", chf(T.npv_budget, true), "budget view"), T.risk_year ? vk("Risk reduction", chf(T.risk_year, true), "per year, not in the views") : null),
    h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Use case","Value per year (range)","Cash per year","Cost per year","NPV","ROI","Payback","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, rows.map(function(u){
        var v = valueOf(u), d = domById(u.domain) || {}, ry = v.range_year || {};
        return h("tr",null,
          h("td",null, h("button",{type:"button",class:"agentlink",style:"font-weight:700;color:" + (d.color || ACCENT),onclick:function(){ openUseCase(u); }}, u.id + " " + u.name)),
          h("td",{class:"nowrap"}, h("b",null, chf(ry.base, true)), h("div",{class:"note"}, chf(ry.low, true) + " \u2013 " + chf(ry.high, true))),
          h("td",{class:"nowrap"}, chf(v.budget_year, true)),
          h("td",{class:"nowrap"}, chf(v.cost_year, true), v.build ? h("div",{class:"note"}, "+ " + chf(v.build, true) + " build") : null),
          h("td",{class:"nowrap"}, chf(v.npv, true)), h("td",{class:"nowrap"}, num(v.roi) ? pct(v.roi) : TBC),
          h("td",{class:"nowrap"}, num(v.payback_months) ? v.payback_months.toFixed(1) + " months" : TBC),
          h("td",null, h("span",{class:"pill " + (v.status === "validated" ? "val" : (v.status === "partly validated" ? "adj" : "open"))}, v.status || "hypothesis"), h("div",{class:"note"}, (v.confidence || "low") + " confidence \u00b7 " + (v.open_assumptions || 0) + " open")));
      })))),
    arr(VC.inputs_needed).length ? h("p",{class:"note"}, "Inputs still to collect: " + VC.inputs_needed.map(function(x){ return x.use_case + " (" + arr(x.assumptions).join(", ") + ")"; }).join("; ")) : null,
    h("h3",{class:"sub"},"Assumptions to clarify in the workshop"),
    h("p",{class:"note"}, "Ranked by their effect on the NPV. Confirm, adjust (enter the agreed value) or reject each one with its owner. Verdicts are saved in this browser, exported from Discovery and merged into the next version of the value case, which is then recalculated."),
    assTable(top, true),
    rest.length ? h("details",{class:"acc"}, h("summary",null, h("span",{class:"n"}, String(rest.length)), "More value assumptions"), h("div",{class:"bd"}, assTable(rest, true))) : null,
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
    h("div",{class:"vkpis"}, vk("Run cost per month", chf(T.total_month, true), "all modelled agents"), vk("Run cost per year", chf(T.annual, true), "at full adoption"),
      vk("Build", chf(T.build, true), "one-time estimate"), vk("Copilot Credits", grp(T.credits_month || 0), "per month \u00b7 " + chf(L.credits, true) + " pay-as-you-go"),
      vk("People share", T.total_month ? pct((L.people || 0) / T.total_month) : TBC, "of the run cost"), low ? vk("Lowest credit option", chf(low.annual_chf, true), low.label) : null),
    h("h3",{class:"sub"},"Cost per agent and month"),
    h("div",{class:"tscroll"}, h("table",{class:"t"},
      h("thead",null, h("tr",null, ["Agent","Harness and audience","Sessions","Credits","Credit cost","Licences","Azure","People","Total","Build","Unit cost"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, agents.map(function(a){
        var ln = a.lines || {}, un = a.unit || {};
        return h("tr",null, h("td",null, agentCell(a)), h("td",null, (a.harness || "") + " \u00b7 " + (a.audience || ""), a.coverage ? h("div",{class:"note"}, a.coverage) : null),
          h("td",{class:"nowrap"}, grp(a.sessions || 0), h("div",{class:"note"}, pct(a.billable_share) + " billed")), h("td",{class:"nowrap"}, grp(a.credits_month || 0)),
          h("td",{class:"nowrap"}, chf(ln.credits)), h("td",{class:"nowrap"}, chf(ln.licences)), h("td",{class:"nowrap"}, chf(ln.azure)), h("td",{class:"nowrap"}, chf(ln.people), num(a.run_hours_month) ? h("div",{class:"note"}, grp(a.run_hours_month) + " h") : null),
          h("td",{class:"nowrap"}, h("b",null, chf(a.total_month))), h("td",{class:"nowrap"}, chf(a.build, true)),
          h("td",{class:"nowrap"}, num(un.per_session) ? chf(un.per_session) + " per session" : TBC, num(un.per_outcome) ? h("div",{class:"note"}, chf(un.per_outcome) + " per " + (un.outcome || "outcome")) : null));
      })))),
    h("div",{class:"cbars",role:"img","aria-label":"Cost composition per agent"}, agents.map(function(a){
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
          h("td",{class:"nowrap"}, grp(e.credits_month || 0)), h("td",{class:"nowrap"}, a.credits_month ? pct((e.credits_month || 0) / a.credits_month) : ""));
      }); })))),
    F.coverage_note ? h("p",{class:"note"}, F.coverage_note) : null,
    h("h3",{class:"sub"},"Purchase options for the credits"),
    h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Option","Per year","Versus pay-as-you-go","Utilisation","Conditions"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, opts.map(function(o){
        return h("tr",null, h("td",null, h("b",null, o.label), o.lowest ? h("span",{class:"pill val",style:"margin-inline-start:6px"},"lowest") : null), h("td",{class:"nowrap"}, chf(o.annual_chf)),
          h("td",{class:"nowrap"}, o.option === "payg" ? "\u2014" : (o.vs_payg > 0 ? "+" : "") + pct(o.vs_payg, 1)), h("td",{class:"nowrap"}, num(o.utilisation) ? pct(o.utilisation) : ""), h("td",null, o.note || ""));
      })))),
    h("p",{class:"note"}, (F.purchase && F.purchase.note) || "A hypothesis: commit to packs or P3 only after a usage baseline; P3 purchases cannot be refunded."),
    arr(F.credit_scenarios).length ? [h("h3",{class:"sub"},"Sensitivity of the credit cost"),
      h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Case","Credits per month","Credit cost per month","Change"].map(function(c){ return h("th",{scope:"col"}, c); }))),
        h("tbody",null, [h("tr",null, h("td",null, h("b",null,"Base case")), h("td",{class:"nowrap"}, grp(T.credits_month || 0)), h("td",{class:"nowrap"}, chf(L.credits)), h("td",null,"\u2014"))].concat(F.credit_scenarios.map(function(x){
          return h("tr",null, h("td",null, x.name), h("td",{class:"nowrap"}, grp(x.credits_month || 0)), h("td",{class:"nowrap"}, chf(x.chf_month)),
            h("td",{class:"nowrap"}, (x.change > 0 ? "+" : "") + pct(x.change, 1), h("span",{class:"chg " + (x.change > 0 ? "up" : "down"),style:"width:" + Math.min(80, Math.round(Math.abs(x.change) * 60)) + "px"})));
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
      assTable(F.assumptions, false)] : null,
    h("h3",{class:"sub"},"Rates and sources"),
    arr(F.rates).length ? h("div",{class:"tscroll"}, h("table",{class:"t"}, h("thead",null, h("tr",null, ["Rate","Value","Source"].map(function(c){ return h("th",{scope:"col"}, c); }))),
      h("tbody",null, F.rates.map(function(r){ return h("tr",null, h("td",null, r.label || ""), h("td",null, r.value || ""), h("td",null, r.source || "")); })))) : null,
    arr(F.sources).length ? h("ul",{class:"clean idrules"}, F.sources.map(function(x){ return h("li",null, h("b",null, (x.id || "") + " "), /^https:\/\//.test(x.url || "") ? h("a",{href:x.url,target:"_blank",rel:"noopener"}, x.title || x.url) : (x.title || ""), x.date ? " \u00b7 checked " + x.date : ""); })) : null,
    F.note ? h("p",{class:"note"}, F.note) : null,
    h("h3",{class:"sub"},"Validate in the workshop"), valBox("finops","model")];
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
      var d = domById(j.id) || {}, c = hex(j.colour, d.color || ACCENT), g = hex(j.glyph, "#FFFFFF");
      return h("div",{class:"sw"},
        h("div",{class:"chip",style:"background:" + c + ";color:" + g}, h("b",null, j.id + " \u00b7 " + (j.name || d.journey_name || d.name || "")), h("span",null, j.po ? "PO area: " + j.po : "")),
        h("div",{class:"meta"}, h("code",null, c), j.colour_name ? h("span",null, String(j.colour_name)) : null, j.contrast ? h("span",{class:"note"}, j.contrast + ":1 with the glyph") : null));
    })),
    nonprod.length ? h("div",{class:"bands"}, order.map(function(e){
      var en = envs.filter(function(x){ return x.name === e; })[0] || {};
      var band = hex(en.band, null);
      return h("div",{class:"band"},
        h("div",{class:"bchip" + (band ? "" : " clean"),style: band ? "background:" + band + ";color:" + hex(en.label, "#FFFFFF") : null}, band ? e : e + " \u00b7 no band"),
        h("div",{class:"note"}, band ? [(en.band_name ? en.band_name + " \u00b7 " : "") + band, en.label_contrast ? " \u00b7 label " + en.label_contrast + ":1" : ""] : "Production stays clean: no postfix, no band"));
    })) : null);
  out.push(h("h3",{class:"sub"},"Agent family"),
    h("div",{class:"family"}, D.map(function(d){
      var mine = team.filter(function(t){ return t.d === d; });
      if (!mine.length) return null;
      var j = js.filter(function(x){ return x.id === d.id; })[0] || {};
      return h("div",{class:"fcol",style:"--fc:" + hex(j.colour, d.color)},
        h("div",{class:"fhead",style:"color:" + hex(j.glyph, "#FFFFFF")}, h("b",null, d.id + " \u00b7 " + (d.journey_name || d.name)), j.po ? h("span",null, "PO area: " + j.po) : null),
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
  var svg = s("svg",{viewBox:"0 0 " + W + " " + H, class:"matrix", role:"img", "aria-label":"Use case portfolio by value and feasibility"});
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
    var g = s("g",{class:"bub", tabindex:"0", role:"button", "aria-label":u.id + " " + u.name + ", value " + u.value + ", feasibility " + u.feasibility, opacity: st === "rejected" ? .35 : null});
    g.appendChild(s("circle",{cx:cx, cy:cy, r:p.r, fill:d.color, stroke: u.mvp ? "var(--ink)" : "var(--panel)", "stroke-width": u.mvp ? 3 : 2}));
    var uv = valueOf(u);
    if (uv && uv.status !== "validated") g.appendChild(s("circle",{cx:cx, cy:cy, r:p.r + 4.5, fill:"none", stroke:"var(--ink)", "stroke-width":1.4, "stroke-dasharray":"3 3", opacity:.75}));
    g.appendChild(s("text",{x:cx, y:cy + 4, "text-anchor":"middle", style:"font-size:" + (String(u.id).length > 4 ? 8.5 : 10) + "px;font-weight:700;fill:#fff"}, String(u.id)));
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
    return h("button",{type:"button",class:"ucag",title:nameOf(a),"aria-label":nameOf(a),onclick:function(){ openAgent(a.id); }}, idIcon(a, "aicon") || h("span",{class:"aicon ini",style:"background:" + (d.color || ACCENT)}, initials(shortOf(a)))); }),
    ags.length > 5 ? h("span",{class:"small-lbl"}, "+" + (ags.length - 5)) : null);
}
function renderUseCases(){
  var rows = UCS.slice().sort(function(a, b){ return (b.mvp ? 1 : 0) - (a.mvp ? 1 : 0) || score(b.value) * score(b.feasibility) - score(a.value) * score(a.feasibility); });
  var table = h("div",{class:"tscroll"}, h("table",{class:"t"},
    h("thead",null, h("tr",null, ["ID","Use case","Journey","Agents","Value","Feasibility","Horizon","Status"].map(function(c){ return h("th",{scope:"col"}, c); }))),
    h("tbody",null, rows.map(function(u){
      var d = domById(u.domain) || {};
      return h("tr",null, h("td",null, h("b",null, u.id)), h("td",null, h("button",{type:"button",style:"all:unset;cursor:pointer;font-weight:700;color:" + (d.color || ACCENT),onclick:function(){ openUseCase(u); }}, u.name), u.mvp ? h("span",{class:"pill acc",style:"margin-inline-start:6px"},"MVP") : null, evPills(u.src)),
        h("td",null, d.name || ""), h("td",null, ucAgentIcons(u)), h("td",null, String(u.value || TBC)), h("td",null, String(u.feasibility || TBC)), h("td",null, u.horizon || TBC), h("td",null, statusPill(note("val|uc|" + u.id).status || u.status)));
    }))));
  return [h("h2",{class:"sec"},"Use case portfolio"), h("p",{class:"lead"}, BP.use_case_intro || "Every candidate placed by value and feasibility. Bubble colour = journey, dark ring = MVP candidate. Select a bubble or a row for the detail and to record the workshop verdict."),
    h("div",{class:"ucwrap"}, matrixSvg(), table), VC ? matrixLegend() : null,
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
  Object.keys(NOTES).forEach(function(k){
    var p = k.split("|");
    if (p[0] === "val") out.validations[p[1] + ":" + p.slice(2).join("|")] = NOTES[k];
    else if (p[0] === "q") out.discovery[p.slice(1).join("|")] = NOTES[k];
  });
  return out;
}
function notesText(){
  var L = [(M.customer || "Customer") + " \u2014 Frontier blueprint workshop notes", "Exported " + new Date().toLocaleString(), ""];
  D.forEach(function(d){
    var lines = [];
    questionsOf(d).forEach(function(x){ var n = note("q|" + x.id); if (n.note || n.status || n.discussed) lines.push("- [" + (n.status || "open") + "] " + (x.q.q || "") + (n.note ? "\n    " + n.note : "")); });
    (d.orchestrator ? [d.orchestrator] : []).concat(d.agents).forEach(function(a){ var n = note("val|agent|" + a.id); if (n.status || n.note) lines.push("- Agent " + nameOf(a) + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
    if (lines.length) L.push("## " + d.name, ...lines, "");
  });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|ass|") === 0; }).sort().forEach(function(k){ var n = NOTES[k], id = k.slice(8), a = ASSM[id] || {}; if (n.status || n.note || num(n.value)) L.push("- Assumption " + id + (a.statement ? " (" + a.statement + ")" : "") + ": " + (n.status || "") + (num(n.value) ? " \u2192 " + n.value + (a.unit ? " " + a.unit : "") : "") + (n.note ? " \u2014 " + n.note : "")); });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|ready|") === 0; }).sort().forEach(function(k){ var n = NOTES[k]; if (n.status || n.note) L.push("- IT readiness " + k.slice(10) + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
  Object.keys(NOTES).filter(function(k){ return k.indexOf("val|adr|") === 0; }).sort().forEach(function(k){ var n = NOTES[k]; if (n.status || n.note) L.push("- Decision " + k.slice(8) + ": " + (n.status || "") + (n.note ? " \u2014 " + n.note : "")); });
  var nf = note("val|finops|model"); if (nf.status || nf.note) L.push("- FinOps model: " + (nf.status || "") + (nf.note ? " \u2014 " + nf.note : ""));
  var ni = note("val|identity|names"); if (ni.status || ni.note) L.push("- Agent identity (names, colours, icons): " + (ni.status || "") + (ni.note ? " \u2014 " + ni.note : ""));
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
  var out = [h("h2",{class:"sec"},"Roadmap and next steps"), BP.roadmap_intro ? h("p",{class:"lead"}, BP.roadmap_intro) : null, cols];
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

/* ---------------- render ---------------- */
var RENDER = { overview:renderOverview, org:renderOrg, blueprint:renderBlueprint, journeys:function(){ var o = renderJourney(); return isFactory(dom()) ? o.concat(renderFactorySections()) : o; }, attendees:renderAttendees, readiness:renderReadiness, agents:renderAgents, identity:renderIdentity, architecture:renderArchitecture, usecases:renderUseCases, finops:renderFinops, discovery:renderDiscovery, roadmap:renderRoadmap, evidence:renderEvidence };
function render(scrollTop){
  if (ORDER.indexOf(state.view) < 0) state.view = ORDER[0];
  if (state.d >= D.length) state.d = 0;
  var d = dom();
  setDomainColor(DOMAIN_VIEWS.indexOf(state.view) >= 0 && d.color ? d.color : ACCENT);
  renderRail(); renderCrumb(); renderSubnav();
  var v = document.getElementById("view");
  var out;
  try { out = RENDER[state.view](); }
  catch (e) { out = [h("div",{class:"empty"}, h("b",null,"This view could not be drawn."), h("p",null, String(e && e.message || e)))]; if (window.console) console.error(e); }
  v.replaceChildren(); add(v, out); v.appendChild(pager());
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
