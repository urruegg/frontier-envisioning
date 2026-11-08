# Release manifests

`<version>/manifest.json` records the SHA-256 of every artefact published for a release (plugin package, demo blueprint, identity kit, catalogue). While the plugin carries a released version, `python tools/dev.py check` rebuilds the artefacts and compares them (`tools/verify_release.py`). After publishing a release, the release manager adds its manifest from the release asset `release-manifest.json`. Files here are maintained by people.
