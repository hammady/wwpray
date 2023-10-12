module.exports = async (dataFilePath, lastUpdatedFilePath, destinationDir) => {
    const fs = require('fs')
    const { execSync } = require('child_process')
    const svelteDir = './svelte'
    
    // Copy data files to be used by Svelte
    const notifiedDestinationPath = svelteDir + '/static/data/notified.json'
    const lastUpdatedDestinationPath = svelteDir + '/src/routes/last_updated.txt'

    fs.cpSync(dataFilePath, notifiedDestinationPath)
    fs.cpSync(lastUpdatedFilePath, lastUpdatedDestinationPath)
    
    // Generate static site using Svelte
    execSync('npm install', { cwd: svelteDir, stdio: 'inherit' })
    execSync('npm run build', { cwd: svelteDir, stdio: 'inherit' })

    const svelteBuildDir = svelteDir + '/build'
    fs.mkdirSync(destinationDir, { recursive: true })
    fs.cpSync(svelteBuildDir, destinationDir, { recursive: true })

    // Output HTML file will be on destinationDir/index.html
}
