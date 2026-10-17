# smoke-hbt

Toolchain smoke bench: one `npn13G2` (native VBIC, no OSDI) with a DC operating
point and a 5 us transient. **Simulated**, corner `hbt_typ`, 27 C, 1.80 V
supply, single corner. That point is inside the HBT model card's validity
window (card: Vce 0.4-2.0 V measured, 1.6 V rated; the DC point has Vce about
1.2 V); no corner here is claimed beyond it. It writes no evidence and states
no spec-row result.

## Cold start (from a clean checkout)

Everything goes into worktree-local, git-ignored paths (`.tools/`); nothing is
installed host-wide.

```bash
# 1. PDK at the pinned commit (sim/pdk-artifact.json: v0.3.0, 5cccb161f749...)
#    Either klayout-tools' fetch script into a PDK_ROOT of your choice, or:
mkdir -p .tools/pdk .tools/dl
curl -L -o .tools/dl/pdk.tar.gz \
  https://github.com/IHP-GmbH/IHP-Open-PDK/archive/5cccb161f7492697cfa52eb14dc03beb00bdca9e.tar.gz
tar -xzf .tools/dl/pdk.tar.gz -C .tools/pdk --strip-components=1 \
  --wildcards '*/ihp-sg13g2/libs.tech/ngspice/models/*'
echo 0.3.0 > .tools/pdk/ihp-sg13g2/.fetched-version   # provenance only

# 2. ngspice 46 (sim/toolchain.json), built locally, no X
curl -L -o .tools/dl/ngspice-46.tar.gz "$(python3 -c "import json;print(json.load(open('sim/toolchain.json'))['ngspice']['source_url'])")"
echo "a0d1699af1940b06649276dcd6ff5a566c8c0cad01b2f7b5e99dedbb4d64c19b  .tools/dl/ngspice-46.tar.gz" | sha256sum -c
mkdir -p .tools/src && tar -xzf .tools/dl/ngspice-46.tar.gz -C .tools/src
(cd .tools/src/ngspice-46 && ./configure --prefix="$PWD/../../ngspice-46" --with-x=no --with-ngshared=no \
   && make -j2 && make install)

# 3. Verify + run (the gate runs first; a mismatch exits non-zero, ngspice never starts)
export PDK_ROOT="$PWD/.tools/pdk" NGSPICE="$PWD/.tools/ngspice-46/bin/ngspice"
sim/smoke-hbt/run.sh        # exits 0 on success

# Negative control (stub ngspice; needs only a populated PDK_ROOT)
python3 -I -m unittest discover -s sim/tools/tests -v
```

The integrity gate decides on file hashes; a missing `.fetched-version` marker
is reported but is provenance only. A non-46 ngspice is reported as a warning.
