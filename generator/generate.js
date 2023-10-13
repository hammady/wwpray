module.exports = async (dataFilePath, lastUpdatedFilePath, destinationDir) => {
    const fs = require('fs')
    const { execSync } = require('child_process')
    const svelteDir = './svelte'
    const writableSvelteDir = '/tmp/svelte'

    // Create destination directory and writable Svelte directory
    fs.mkdirSync(destinationDir, { recursive: true })
    fs.mkdirSync(writableSvelteDir, { recursive: true })

    // Copy Svlete directory to a writable location
    fs.cpSync(svelteDir, writableSvelteDir, { recursive: true })
    
    // Copy data files to be used by Svelte
    fs.cpSync(dataFilePath, writableSvelteDir + '/src/routes/notified.json')
    fs.cpSync(lastUpdatedFilePath, writableSvelteDir + '/src/routes/last_updated.txt')
    
    // Generate static site using Svelte
    execSync('npm install', { cwd: writableSvelteDir, stdio: 'inherit' })
    execSync('npm run build', { cwd: writableSvelteDir, stdio: 'inherit' })

    // Copy necessary static files to destination directory
    const svelteBuildDir = writableSvelteDir + '/build'
    for (const file of ['/_app', '/index.html', '/favicon.png']) {
        fs.cpSync(svelteBuildDir + file, destinationDir + file, { recursive: true })
    }
}
