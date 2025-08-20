#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Files to fix
const filesToFix = [
  'src/features/dashboard/SimpleDashboard.tsx',
  'src/features/rag/SimpleRAGSystem.tsx',
  'src/features/changlee/SimpleChangleeAssistant.tsx'
];

// Grid property patterns to fix
const gridPatterns = [
  { from: /xs={(\d+)}/g, to: 'size={{ xs: $1 }}' },
  { from: /xs={(\d+)} sm={(\d+)}/g, to: 'size={{ xs: $1, sm: $2 }}' },
  { from: /xs={(\d+)} md={(\d+)}/g, to: 'size={{ xs: $1, md: $2 }}' },
  { from: /xs={(\d+)} lg={(\d+)}/g, to: 'size={{ xs: $1, lg: $2 }}' },
  { from: /xs={(\d+)} sm={(\d+)} md={(\d+)}/g, to: 'size={{ xs: $1, sm: $2, md: $3 }}' },
  { from: /xs={(\d+)} sm={(\d+)} lg={(\d+)}/g, to: 'size={{ xs: $1, sm: $2, lg: $3 }}' },
  { from: /xs={(\d+)} md={(\d+)} lg={(\d+)}/g, to: 'size={{ xs: $1, md: $2, lg: $3 }}' },
  { from: /xs={(\d+)} sm={(\d+)} md={(\d+)} lg={(\d+)}/g, to: 'size={{ xs: $1, sm: $2, md: $3, lg: $4 }}' }
];

// ListItem button property fix
const listItemPattern = { from: /button={true}/g, to: 'component="div" sx={{ cursor: "pointer" }}' };

function fixFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    return;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  // Fix Grid components
  gridPatterns.forEach(pattern => {
    if (pattern.from.test(content)) {
      content = content.replace(pattern.from, pattern.to);
      modified = true;
    }
  });

  // Fix ListItem components
  if (listItemPattern.from.test(content)) {
    content = content.replace(listItemPattern.from, listItemPattern.to);
    modified = true;
  }

  if (modified) {
    fs.writeFileSync(filePath, content);
    console.log(`Fixed: ${filePath}`);
  } else {
    console.log(`No changes needed: ${filePath}`);
  }
}

// Fix all files
filesToFix.forEach(fixFile);

console.log('Grid component fixes completed!');