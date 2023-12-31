module.exports.handler = async (event, context) => {
  console.log(`Your s3 triggered function ${context.functionName} ran at ${new Date()}`)

  // prepare s3 client
  const {
    S3Client,
    GetObjectCommand,
    PutObjectCommand,
  } = require("@aws-sdk/client-s3");
  const s3_client = new S3Client({});

  // get bucket name from environment variable
  const bucketName = process.env.S3_BUCKET
  if (!bucketName) {
    throw new Error('No S3 bucket set, please set S3_BUCKET environment variable')
  }
  dataFileKey = 'data/notified.json'
  dataFilePath = '/tmp/notified.json'
  dataFileKeyUploaded = 'static/data.json'

  const { writeFile, readFile } = require("node:fs/promises");

  const downloadFile = async (key, path) => {
    const get_command = new GetObjectCommand({
      Bucket: bucketName,
      Key: key
    });
    const { Body } = await s3_client.send(get_command);
    await writeFile(path, Body);
  }

  const getMimeType = (filePath) => {
    const ext = require('path').extname(filePath)
    switch (ext) {
      case '.html':
      case '':
        return 'text/html; charset=utf-8'
      case '.css':
        return 'text/css; charset=utf-8'
      case '.js':
        return 'application/javascript; charset=utf-8'
      case '.json':
        return 'application/json; charset=utf-8'
      case '.png':
        return 'image/png'
      default:
        return 'application/octet-stream'
    }
  }

  const uploadFile = async (filePath, fileKey) => {
    const file = require('fs').createReadStream(filePath)
    const put_command = new PutObjectCommand({
      Bucket: bucketName,
      Key: fileKey,
      Body: file,
      ContentType: getMimeType(filePath)
    });
    await s3_client.send(put_command);
  }

  const uploadDirectory = async (directoryPath, directoryKey) => {
    const { glob } = require('glob')
    const files = await glob(directoryPath + '/**/*', { nodir: true })
    for (const filePath of files) {
      const fileKey = filePath.replace(directoryPath, directoryKey)
      await uploadFile(filePath, fileKey)
    }
  }

  // download data file
  console.log(`Downloading ${dataFileKey} from s3...`)
  await downloadFile(dataFileKey, dataFilePath)
  console.log(await readFile(dataFilePath, 'utf8'))

  // generate data
  const destinationDir = '/tmp/dist'
  const generate = require('./generate')
  console.log(`Generating data into ${destinationDir}...`)
  await generate(dataFilePath, destinationDir)

  // upload data
  console.log(`Uploading ${destinationDir} to s3...`)
  await uploadDirectory(destinationDir, 'static')

  // upload data file
  console.log(`Uploading ${dataFilePath} to s3...`)
  await uploadFile(dataFilePath, dataFileKeyUploaded)

  return true
};
