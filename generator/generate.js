module.exports = async (dataFilePath, destinationDir) => {
  const fs = require("fs");
  const { build } = require("vite");
  const path = require("path");
  const writableRootDir = "/tmp/generator";
  const svelteDir = path.join(writableRootDir, "svelte");

  const cleanAndCreateDir = (dir) => {
    if (fs.existsSync(dir)) {
      console.log(`Deleting directory: ${dir}...`);
      fs.rmSync(dir, { recursive: true });
    }
    console.log(`Creating directory: ${dir}...`);
    fs.mkdirSync(dir, { recursive: true });
  }

  // Create destination directory and writable root directory
  cleanAndCreateDir(destinationDir);
  cleanAndCreateDir(writableRootDir);

  // Copy necessary files to writable root directory
  console.log(`Copying code files from current directory ${process.cwd()} to writable root directory: ${writableRootDir}...`);
  for (const file of [
    "svelte",
    "package.json",
    "package-lock.json",
    "node_modules",
  ]) {
    fs.cpSync(file, path.join(writableRootDir, file), { recursive: true });
  }

  // Copy data files to be used by Svelte
  console.log(`Copying data file to svelte directory: ${svelteDir}...`);
  fs.cpSync(
    dataFilePath,
    path.join(svelteDir, "src/routes/notified.json"));

  console.log(`Changing directory to svelte directory: ${svelteDir}...`);
  process.chdir(svelteDir);

  // Generate static site using vite
  console.log(`Building static site using vite...`);
  await build();

  // Copy necessary static files to destination directory
  console.log(`Copying generated static files to destination directory: ${destinationDir}...`);
  const svelteBuildDir = path.join(svelteDir, "build");
  for (const file of ["_app", "index.html", "favicon.png"]) {
    fs.cpSync(path.join(svelteBuildDir, file), path.join(destinationDir, file), {
      recursive: true,
    });
  }
};
