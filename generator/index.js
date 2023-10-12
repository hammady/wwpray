module.exports.handler = async (event, context) => {
  console.log(`Your s3 triggered function ${context.functionName} ran at ${new Date()}`)

  // prepare s3 client
  const {
    S3
  } = require("@aws-sdk/client-s3")
  const s3 = new S3()

  // get bucket name from environment variable
  const bucketName = process.env.S3_BUCKET
  if (!bucketName) {
    throw new Error('No S3 bucket set, please set S3_BUCKET environment variable')
  }
  dataFileKey = 'data/notified.json'
  dataFilePath = '/tmp/notified.json'
  lastUpdatedFileKey = 'data/last_updated.txt'
  lastUpdatedFilePath = '/tmp/last_updated.txt'

  function downloadFile(key, path) {
    return new Promise((resolve, reject) => {
      const params = {
        Bucket: bucketName,
        Key: key
      }
      const file = require('fs').createWriteStream(path)
      const stream = s3.getObject(params).createReadStream()
      stream.on('error', reject)
      file.on('error', reject)
      file.on('finish', resolve)
      stream.pipe(file)
    })
  }

  function uploadDirectory(directoryPath, directoryKey) {
    return new Promise((resolve, reject) => {
      const walk = require('walk')
      const walker = walk.walk(directoryPath)
      walker.on('file', (root, fileStats, next) => {
        const filePath = root + '/' + fileStats.name
        const fileKey = directoryKey + filePath.replace(directoryPath, '')
        const file = require('fs').createReadStream(filePath)
        const params = {
          Bucket: bucketName,
          Key: fileKey,
          Body: file
        }
        s3.putObject(params, (err, data) => {
          if (err) {
            reject(err)
          } else {
            next()
          }
        })
      })
      walker.on('end', resolve)
    })
  }

  // download data file
  console.log(`Downloading ${dataFileKey} from s3...`)
  await downloadFile(dataFileKey, dataFilePath)
  // download last updated file
  console.log(`Downloading ${lastUpdatedFileKey} from s3...`)
  await downloadFile(lastUpdatedFileKey, lastUpdatedFilePath)

  // generate data
  const destinationDir = '/tmp/dist/'
  const generate = require('./generate')
  console.log(`Generating data into ${destinationDir}...`)
  await generate(dataFilePath, lastUpdatedFilePath, destinationDir)

  // upload data
  console.log(`Uploading ${destinationDir} to s3...`)
  await uploadDirectory(destinationDir, 'static')

  return true
};
