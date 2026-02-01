import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync } from 'fs'
import { resolve } from 'path'

// Read version from VERSION_V2 file
const getVersion = () => {
  try {
    const versionPath = resolve(__dirname, '../VERSION_V2')
    return readFileSync(versionPath, 'utf-8').trim()
  } catch (err) {
    return 'unknown'
  }
}

// Custom plugin to display startup banner
const versionBannerPlugin = () => ({
  name: 'version-banner',
  configureServer() {
    const version = getVersion()
    console.log('\n╔══════════════════════════════════════════════════════════╗')
    console.log('║                                                          ║')
    console.log('║            COMBAT PROTOCOL FRONTEND (V2)                 ║')
    console.log('║                                                          ║')
    console.log(`║                   VERSION: v${version.padEnd(27)}  ║`)
    console.log('║                   (REACT SPA + THREE.JS)                 ║')
    console.log('║                   (3D FIGHTER VISUALIZATION)             ║')
    console.log('║                                                          ║')
    console.log('╚══════════════════════════════════════════════════════════╝\n')
  }
})

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), versionBannerPlugin()],
  base: '/v2/',  // ADD THIS LINE for v2
})
