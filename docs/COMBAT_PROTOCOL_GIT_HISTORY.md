### Commit: da3e7e78e71095520232974c27d2b2c038acfefe
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-25 18:09:09 -0700
**Message:** fix: use environment-aware API URLs for local dev and production

- Replace window.location.origin with conditional check using import.meta.env.DEV
- Development mode: use http://localhost:5001 for local Flask backend
- Production mode: use window.location.origin for deployed site
- Fixes 404 errors when loading fighter data and 3D models in local dev
- Applied to both api.js and ThreeJsViewer.jsx for consistency
- Ensures code works on both Mac (Tinker) and Ubuntu (Sky) dev environments

---

### Commit: cd6ef4b2c69f8d1043a724e9a30e5475d6c65751
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-25 11:58:40 -0700
**Message:** On main: inverse-kinematics-simple


---

### Commit: 282f45f818dd8db536a7310f10917394d7908d7f
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-25 11:58:40 -0700
**Message:** index on main: 818018a remove debug spam


---

### Commit: 44825e79fc282c22164f2a005f53be3213376ab3
**Author:** Jon Goldman <jon.goldman@medtronic.com>
**Date:** 2026-01-25 06:05:38 -0700
**Message:** Configure for production deployment at /v2

- Update API_BASE_URL to use window.location.origin
- Set Vite base path to /v2/
- Ready for deployment to combatprotocol.com/v2/

---

### Commit: 818018ae69294208cde4632327a0254a0e645445
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-24 13:28:12 -0700
**Message:** remove debug spam


---

### Commit: e4618abe37a7c0bbdf0ef61d23a9663b5501c47a
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-24 06:43:04 -0700
**Message:** fix: resolve React StrictMode double-mounting and improve 3D model visibility

- Remove StrictMode wrapper in main.jsx to prevent duplicate Three.js scene initialization
- Move camera closer to fighters (z=8 -> z=4) for better default view
- Increase fighter model scale from 0.5x to 1.0x (full size)
- Update camera reset and auto-rotate to match new positioning
- Keep magenta debug cube as visual reference point

Fixes the issue where fighters appeared as tiny distant figures due to
camera being too far back and models scaled down to 50%. StrictMode was
causing animation loop conflicts by mounting components twice in dev mode.

---

### Commit: 6941f049030b71ea81f9772d8f082443348743f3
**Author:** Jon Goldman <jon.goldman@medtronic.com>
**Date:** 2026-01-24 05:18:45 -0700
**Message:** debug the 3D view


---

### Commit: de97dd0265448a503f5be5621d67c071ce10e793
**Author:** Jon Goldman <jon.goldman@medtronic.com>
**Date:** 2026-01-24 02:51:03 -0700
**Message:** WIP: Add Three.js 3D fighter viewer component

- Add ThreeJsViewer component with GLTFLoader for fighter models
- Implement OrbitControls for camera interaction (debugging in progress)
- Add test cube for render verification
- Configure lighting, ground plane, and scene setup
- Install three.js dependency (v0.182.0)
- Add setup documentation

Known issues:
- Fighter models load but are not visible
- OrbitControls configured but not responding to input

---

### Commit: bc3360c45497c309ed44859ff3db60f4c5f37ab0
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-21 13:53:37 -0700
**Message:** start fight faster


---

### Commit: 66519bf301cd5fb2657a7f824a7da03df6415dd8
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-21 13:39:17 -0700
**Message:** Add real-time fight streaming with SSE and live stat updates


---

### Commit: adfeab80a4b1afd61a56ccea0a3adf02ed24bef8
**Author:** Jon Goldman <goldman@swcp.com>
**Date:** 2026-01-20 17:25:38 -0700
**Message:** Add Combat Protocol fighter card UI with React


---

### Commit: 67afce86df24003212b88299a04b970c617a15dd
**Author:** Jon Goldman <jon.goldman@medtronic.com>
**Date:** 2026-01-20 03:46:49 -0700
**Message:** Initial React frontend scaffolding


---

---

## Repository Statistics

### Frontend
- Total commits: 12
- Total authors:        1
- First commit: 2026-01-20
- Last commit: 2026-01-25

---
**End of Git History Export**
