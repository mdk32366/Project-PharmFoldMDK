# D-175 restore kit (executor could not push 70KB+ files without laptop Shell)

## Blocker
Kaylee executor subagent was NOT bound to MDKDevLaptop machineId `7b562e61-a91d-4fb8-8879-1f77f0f88bdf`.
Shell schema for this executor omits `machineId`, so all Shell ran on the box VM.
CloudAgent PARKED per Spec.

## Already on this branch
- tests/test_d175_census_header_polish.py
- ui/src/components/CensusTable.d175.test.jsx
- ui/src/components/CensusTable.d173.test.jsx (updated for headerLines)
- tests/test_d173 restored after accidental placeholder

## Broken
- ui/src/components/CensusTable.jsx is a STUB — restore tip c1bd609 then apply `docs/D175-RESTORE-CensusTable.patch`.

## Laptop restore (PowerShell; use `;` not `&&`)
```powershell
cd C:/Projects/Project-PharmFoldMDK
git fetch origin
git checkout feat/d175-census-header-polish
git checkout c1bd609 -- ui/src/components/CensusTable.jsx
git apply docs/D175-RESTORE-CensusTable.patch
# Also land styles.css / docs/decisions.md / docs/RESERVED.md / cascade tests from box kit /tmp/d175
```
