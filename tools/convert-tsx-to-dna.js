#!/usr/bin/env node
/**
 * convert-tsx-to-dna.js
 * Recursively find .tsx files, rename to .dna and update imports/references.
 * Safe by default: supports --dry-run, --backup, --verbose, --path, --exclude
 */

const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
const glob = require('glob');
const argv = require('yargs')
  .option('dry-run', { type: 'boolean', default: true })
  .option('backup', { type: 'boolean', default: true })
  .option('path', { type: 'string', default: process.cwd() })
  .option('verbose', { type: 'boolean', default: false })
  .option('exclude', { type: 'array', default: ['node_modules', '.git', 'dist', 'build'] })
  .help()
  .argv;

const ROOT = path.resolve(argv.path);
const DRY_RUN = argv['dry-run'];
const BACKUP = argv.backup;
const VERBOSE = argv.verbose;
const EXCLUDES = argv.exclude.map(d => path.join(ROOT, d));

function log(...args){ if(VERBOSE) console.log(...args); }

function isExcluded(file){
  return EXCLUDES.some(ex => file.startsWith(ex));
}

async function run(){
  console.log(`Scanning ${ROOT} for .tsx files... (dry-run=${DRY_RUN})`);

  // find all .tsx files
  const pattern = path.join(ROOT, '**/*.tsx');
  const files = glob.sync(pattern, { nodir: true, ignore: EXCLUDES.map(e => `${e}/**`) });

  if(files.length === 0){
    console.log('No .tsx files found.');
    return;
  }

  // mapping old->new
  const mapping = {};
  for(const f of files){
    if(isExcluded(f)) continue;
    const newPath = f.replace(/\.tsx$/i, '.dna');
    mapping[f] = newPath;
  }

  if(BACKUP && !DRY_RUN){
    const backupFile = path.join(ROOT, `.convert-backup-${Date.now()}.json`);
    await fsp.writeFile(backupFile, JSON.stringify({mapping, timestamp: new Date().toISOString()}, null, 2));
    console.log(`Backup mapping written to ${backupFile}`);
  }

  // Update references across project files
  const allFiles = glob.sync(path.join(ROOT, '**/*.*'), { nodir: true, ignore: EXCLUDES.map(e => `${e}/**`) });
  const textFiles = allFiles.filter(p => !Object.keys(mapping).includes(p) && !p.endsWith('.dna'));

  // Prepare regexes for replacements
  const replacements = Object.entries(mapping).map(([oldP, newP]) => {
    const relOld = './' + path.relative(ROOT, oldP).split(path.sep).join('/');
    const relNew = './' + path.relative(ROOT, newP).split(path.sep).join('/');
    const oldBase = path.basename(oldP);
    const newBase = path.basename(newP);
    return {oldP, newP, relOld, relNew, oldBase, newBase};
  });

  // Function to update content
  async function updateFile(file){
    let content = await fsp.readFile(file, 'utf8');
    let orig = content;
    for(const r of replacements){
      // update import paths that explicitly include .tsx
      const escapedOldBase = r.oldBase.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&');
      // patterns: './foo.tsx', "../bar.tsx", /foo.tsx'
      const regex1 = new RegExp(escapedOldBase, 'g');
      content = content.replace(regex1, r.newBase);

      // update path segments with .tsx
      const escapedRelOld = r.relOld.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&');
      const regex2 = new RegExp(escapedRelOld, 'g');
      content = content.replace(regex2, r.relNew);
    }

    if(content !== orig){
      if(DRY_RUN){
        log(`[dry-run] Would update references in ${file}`);
      } else {
        await fsp.writeFile(file, content, 'utf8');
        log(`Updated references in ${file}`);
      }
    }
  }

  // Update references
  console.log(`Updating references in ${textFiles.length} files...`);
  for(const tf of textFiles){
    if(isExcluded(tf)) continue;
    try{ await updateFile(tf); }catch(e){ console.error('Error updating', tf, e.message); }
  }

  // Finally rename files
  console.log(`Renaming ${Object.keys(mapping).length} files...`);
  for(const [oldF, newF] of Object.entries(mapping)){
    if(DRY_RUN){
      console.log(`[dry-run] would rename ${oldF} → ${newF}`);
    } else {
      await fsp.mkdir(path.dirname(newF), { recursive: true });
      await fsp.rename(oldF, newF);
      console.log(`Renamed ${oldF} → ${newF}`);
    }
  }

  console.log('Conversion complete.');
  if(DRY_RUN) console.log('Dry-run mode: no files were changed. Rerun with --no-dry-run to apply changes.');
}

run().catch(err => { console.error(err); process.exit(1); });
