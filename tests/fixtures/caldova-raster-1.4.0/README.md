# Verified 1.4.0 raster inputs

These unmodified PNGs come from the original Caldova identity ZIP whose SHA-256
matches the [1.4.0 release record](../../../releases/1.4.0/manifest.json).
They are historical build inputs, not a copy of the complete golden ZIP.

The profile contains 223 PNGs and hashes for all 205 generated non-raster files,
excluding the README's documented PNG/SVG presentation choice. The build
regenerates those files, validates their inventory and bytes, replays the PNGs,
regenerates the PNG-mode README from the original code, then builds the archive.
Its complete ZIP hash must still match the immutable release record.

The supplied 1.5.0 and 1.6.0 records expect this same identity ZIP hash. Their
reuse is explicit and checks the current release record as well as every
generated input. A later version is not enabled automatically.

The 1.6.1 layout-fix preview is explicitly enabled for unchanged identity inputs.
While its release record is absent, the 1.6.0 identity record supplies provenance.
If a current record exists, it must match; no other future patch is enabled.

This avoids an undeclared converter/font dependency and preserves two
platform-sensitive outline images. The report records `restored`, not a claim
that a live converter rendered those pixels. A changed input or tampered asset
fails the build. Other versions do not automatically inherit this profile.

Preserve the [plugin notices](../../../plugin/THIRD-PARTY-NOTICES.md) and the
notices regenerated inside the identity package. Fictitious Caldova data only;
this fixture does not imply wider publication approval.
