const { build } = require("vite");
const path = require("path");

module.exports = async (dataFilePath, lastUpdatedFilePath, destinationDir) => {
  const fs = require("fs");
  const { execSync } = require("child_process");
  const writableRootDir = "/tmp/generator";
  const svelteDir = "./svelte";

  // Create destination directory and writable root directory
  fs.mkdirSync(destinationDir, { recursive: true });
  fs.mkdirSync(writableRootDir, { recursive: true });

  // Copy necessary files to writable root directory
  for (const file of [
    "svelte",
    "package.json",
    "package-lock.json",
    "node_modules",
  ]) {
    fs.cpSync(file, path.join(writableRootDir, file), { recursive: true });
  }

  process.chdir(writableRootDir);

  // Copy data files to be used by Svelte
  fs.cpSync(dataFilePath, svelteDir + "/src/routes/notified.json");
  fs.cpSync(lastUpdatedFilePath, svelteDir + "/src/routes/last_updated.txt");

  // Generate static site using vite
  execSync("npm install", { stdio: "inherit" }) // Do we need this?
  await build();

  // Copy necessary static files to destination directory
  const svelteBuildDir = path.join(svelteDir, "build");
  for (const file of ["/_app", "/index.html", "/favicon.png"]) {
    fs.cpSync(svelteBuildDir + file, destinationDir + file, {
      recursive: true,
    });
  }
};
