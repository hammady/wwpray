module.exports = async (dataFilePath, lastUpdatedFilePath, destinationDir) => {
    const fs = require('fs')
    const { execSync } = require('child_process')
    const writableRootDir = '/tmp/generator'
    const svelteDir = writableRootDir + '/svelte'

    // Create destination directory and writable root directory
    fs.mkdirSync(destinationDir, { recursive: true })
    fs.mkdirSync(writableRootDir, { recursive: true })

    // Copy root directory to a writable location
    for (const file of ['svelte', 'package.json', 'package-lock.json', 'node_modules']) {
        fs.cpSync(file, writableRootDir + '/' + file, { recursive: true })
    }
    
    // Copy data files to be used by Svelte
    fs.cpSync(dataFilePath, svelteDir + '/src/routes/notified.json')
    fs.cpSync(lastUpdatedFilePath, svelteDir + '/src/routes/last_updated.txt')
    
    // Generate static site using Svelte
    execSync('npm run build --workspace=svelte --cache=/tmp/cache --loglevel=verbose', { cwd: writableRootDir, stdio: 'inherit' })

    // Copy necessary static files to destination directory
    const svelteBuildDir = svelteDir + '/build'
    for (const file of ['/_app', '/index.html', '/favicon.png']) {
        fs.cpSync(svelteBuildDir + file, destinationDir + file, { recursive: true })
    }
}
