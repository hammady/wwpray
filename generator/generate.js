module.exports = async (dataFilePath, lastUpdatedFilePath, destinationDir) => {
    // TODO: dummy implementation, replace with actual generator code

    // make sure destinationDir exists
    const fs = require('fs')
    if (!fs.existsSync(destinationDir)) {
        fs.mkdirSync(destinationDir)
    }

    var data = JSON.parse(fs.readFileSync(dataFilePath, 'utf8')).masjids
    const filePath = destinationDir + '/index.html'
    fs.writeFileSync(filePath, JSON.stringify(data))
    const lastUpdatedDestinationPath = destinationDir + '/last_updated.txt'
    fs.copyFileSync(lastUpdatedFilePath, lastUpdatedDestinationPath)
}
