#!/usr/bin/env node

/**
 * 简单的构建脚本，用于合并模块化的CSS和JS文件
 */

const fs = require('fs');
const path = require('path');

console.log('🔨 开始构建模块化NEXUS...');

// CSS文件列表（按依赖顺序）
const cssFiles = [
    'assets/css/variables.css',
    'assets/css/base.css',
    'assets/css/sidebar.css',
    'assets/css/components.css'
];

// JS文件列表（按依赖顺序）
const jsFiles = [
    'assets/js/core/app.js',
    'assets/js/components/chat.js'
];

/**
 * 合并CSS文件
 */
function buildCSS() {
    console.log('📦 合并CSS文件...');
    
    let combinedCSS = '/* NEXUS 模块化样式 - 自动生成 */\n\n';
    
    cssFiles.forEach(file => {
        if (fs.existsSync(file)) {
            console.log(`  ✓ 添加 ${file}`);
            const content = fs.readFileSync(file, 'utf8');
            combinedCSS += `/* === ${file} === */\n`;
            combinedCSS += content + '\n\n';
        } else {
            console.warn(`  ⚠️  文件不存在: ${file}`);
        }
    });
    
    // 创建构建目录
    if (!fs.existsSync('dist')) {
        fs.mkdirSync('dist');
    }
    
    fs.writeFileSync('dist/nexus.css', combinedCSS);
    console.log('  ✅ CSS构建完成: dist/nexus.css');
}

/**
 * 合并JS文件
 */
function buildJS() {
    console.log('📦 合并JS文件...');
    
    let combinedJS = '/* NEXUS 模块化脚本 - 自动生成 */\n\n';
    
    jsFiles.forEach(file => {
        if (fs.existsSync(file)) {
            console.log(`  ✓ 添加 ${file}`);
            const content = fs.readFileSync(file, 'utf8');
            combinedJS += `/* === ${file} === */\n`;
            combinedJS += content + '\n\n';
        } else {
            console.warn(`  ⚠️  文件不存在: ${file}`);
        }
    });
    
    fs.writeFileSync('dist/nexus.js', combinedJS);
    console.log('  ✅ JS构建完成: dist/nexus.js');
}

/**
 * 创建生产版本HTML
 */
function buildHTML() {
    console.log('📦 创建生产版本HTML...');
    
    const htmlContent = fs.readFileSync('index-modular.html', 'utf8');
    
    // 替换CSS引用
    let productionHTML = htmlContent.replace(
        /<!-- 模块化CSS -->[\s\S]*?<link rel="stylesheet" href="assets\/css\/components\.css">/,
        '<!-- 合并的CSS -->\n    <link rel="stylesheet" href="dist/nexus.css">'
    );
    
    // 替换JS引用
    productionHTML = productionHTML.replace(
        /<script src="assets\/js\/core\/app\.js"><\/script>\s*<script src="assets\/js\/components\/chat\.js"><\/script>/,
        '<script src="dist/nexus.js"></script>'
    );
    
    fs.writeFileSync('index-production.html', productionHTML);
    console.log('  ✅ 生产版本HTML创建完成: index-production.html');
}

/**
 * 生成构建报告
 */
function generateReport() {
    console.log('📊 生成构建报告...');
    
    const report = {
        buildTime: new Date().toISOString(),
        files: {
            css: cssFiles.filter(file => fs.existsSync(file)),
            js: jsFiles.filter(file => fs.existsSync(file))
        },
        sizes: {}
    };
    
    // 计算文件大小
    if (fs.existsSync('dist/nexus.css')) {
        report.sizes.css = fs.statSync('dist/nexus.css').size;
    }
    if (fs.existsSync('dist/nexus.js')) {
        report.sizes.js = fs.statSync('dist/nexus.js').size;
    }
    if (fs.existsSync('index-production.html')) {
        report.sizes.html = fs.statSync('index-production.html').size;
    }
    
    fs.writeFileSync('dist/build-report.json', JSON.stringify(report, null, 2));
    
    console.log('📋 构建报告:');
    console.log(`  CSS: ${(report.sizes.css / 1024).toFixed(2)} KB`);
    console.log(`  JS: ${(report.sizes.js / 1024).toFixed(2)} KB`);
    console.log(`  HTML: ${(report.sizes.html / 1024).toFixed(2)} KB`);
    console.log(`  总计: ${((report.sizes.css + report.sizes.js + report.sizes.html) / 1024).toFixed(2)} KB`);
}

// 执行构建
try {
    buildCSS();
    buildJS();
    buildHTML();
    generateReport();
    
    console.log('🎉 构建完成！');
    console.log('');
    console.log('📁 生成的文件:');
    console.log('  - dist/nexus.css (合并的样式)');
    console.log('  - dist/nexus.js (合并的脚本)');
    console.log('  - index-production.html (生产版本)');
    console.log('  - dist/build-report.json (构建报告)');
    console.log('');
    console.log('🚀 使用方法:');
    console.log('  开发: 使用 index-modular.html');
    console.log('  生产: 使用 index-production.html');
    
} catch (error) {
    console.error('❌ 构建失败:', error.message);
    process.exit(1);
}