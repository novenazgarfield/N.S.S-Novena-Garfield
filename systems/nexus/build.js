#!/usr/bin/env node

// NEXUS Research Workstation - Build Script
// 构建脚本用于优化和压缩资源

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class NexusBuildSystem {
    constructor() {
        this.projectRoot = __dirname;
        this.assetsDir = path.join(this.projectRoot, 'assets');
        this.distDir = path.join(this.projectRoot, 'dist');
        this.buildConfig = {
            minify: true,
            sourcemap: true,
            cssOptimization: true,
            jsOptimization: true
        };
    }
    
    async build() {
        console.log('🚀 Starting NEXUS build process...');
        
        try {
            // 清理dist目录
            await this.cleanDist();
            
            // 创建dist目录结构
            await this.createDistStructure();
            
            // 构建CSS模块
            await this.buildCSS();
            
            // 构建JavaScript模块
            await this.buildJS();
            
            // 构建HTML文件
            await this.buildHTML();
            
            // 复制静态资源
            await this.copyStaticAssets();
            
            // 生成构建报告
            await this.generateBuildReport();
            
            console.log('✅ Build completed successfully!');
            
        } catch (error) {
            console.error('❌ Build failed:', error.message);
            process.exit(1);
        }
    }
    
    async cleanDist() {
        console.log('🧹 Cleaning dist directory...');
        
        if (fs.existsSync(this.distDir)) {
            fs.rmSync(this.distDir, { recursive: true, force: true });
        }
    }
    
    async createDistStructure() {
        console.log('📁 Creating dist directory structure...');
        
        const dirs = [
            this.distDir,
            path.join(this.distDir, 'assets'),
            path.join(this.distDir, 'assets', 'css'),
            path.join(this.distDir, 'assets', 'js'),
            path.join(this.distDir, 'public')
        ];
        
        dirs.forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });
    }
    
    async buildCSS() {
        console.log('🎨 Building CSS modules...');
        
        const cssFiles = [
            'themes.css',
            'layout.css', 
            'components.css'
        ];
        
        let combinedCSS = '';
        
        // 合并CSS文件
        for (const file of cssFiles) {
            const filePath = path.join(this.assetsDir, 'css', file);
            if (fs.existsSync(filePath)) {
                const content = fs.readFileSync(filePath, 'utf8');
                combinedCSS += `/* ${file} */\n${content}\n\n`;
            }
        }
        
        // 写入合并的CSS文件
        const outputPath = path.join(this.distDir, 'assets', 'css', 'nexus.css');
        fs.writeFileSync(outputPath, combinedCSS);
        
        // 如果启用了CSS优化，可以在这里添加压缩逻辑
        if (this.buildConfig.cssOptimization) {
            // 简单的CSS压缩（移除注释和多余空白）
            const minifiedCSS = this.minifyCSS(combinedCSS);
            const minOutputPath = path.join(this.distDir, 'assets', 'css', 'nexus.min.css');
            fs.writeFileSync(minOutputPath, minifiedCSS);
        }
        
        console.log(`   ✓ CSS modules built: ${cssFiles.length} files combined`);
    }
    
    async buildJS() {
        console.log('⚡ Building JavaScript modules...');
        
        const jsFiles = [
            'themes.js',
            'navigation.js',
            'rag.js'
        ];
        
        let combinedJS = '';
        
        // 合并JS文件
        for (const file of jsFiles) {
            const filePath = path.join(this.assetsDir, 'js', file);
            if (fs.existsSync(filePath)) {
                const content = fs.readFileSync(filePath, 'utf8');
                combinedJS += `/* ${file} */\n${content}\n\n`;
            }
        }
        
        // 添加模块初始化代码
        combinedJS += `
/* Module Initialization */
window.addEventListener('DOMContentLoaded', () => {
    if (typeof ThemeManager !== 'undefined') {
        window.themeManager = new ThemeManager();
    }
    if (typeof NavigationManager !== 'undefined') {
        window.navigationManager = new NavigationManager();
    }
    if (typeof RAGManager !== 'undefined') {
        window.ragManager = new RAGManager();
    }
    
    console.log('NEXUS modules initialized');
});
`;
        
        // 写入合并的JS文件
        const outputPath = path.join(this.distDir, 'assets', 'js', 'nexus.js');
        fs.writeFileSync(outputPath, combinedJS);
        
        // 如果启用了JS优化，可以在这里添加压缩逻辑
        if (this.buildConfig.jsOptimization) {
            // 简单的JS压缩（移除注释和多余空白）
            const minifiedJS = this.minifyJS(combinedJS);
            const minOutputPath = path.join(this.distDir, 'assets', 'js', 'nexus.min.js');
            fs.writeFileSync(minOutputPath, minifiedJS);
        }
        
        console.log(`   ✓ JavaScript modules built: ${jsFiles.length} files combined`);
    }
    
    async buildHTML() {
        console.log('📄 Building HTML files...');
        
        const htmlFiles = [
            'nexus-dashboard-restored.html',
            'nexus-dashboard-modular.html',
            'nexus-dashboard-optimized.html'
        ];
        
        for (const file of htmlFiles) {
            const inputPath = path.join(this.projectRoot, file);
            const outputPath = path.join(this.distDir, file);
            
            if (fs.existsSync(inputPath)) {
                let content = fs.readFileSync(inputPath, 'utf8');
                
                // 如果是模块化版本，更新资源路径
                if (file === 'nexus-dashboard-modular.html') {
                    content = this.updateAssetPaths(content);
                }
                
                fs.writeFileSync(outputPath, content);
            }
        }
        
        // 创建优化版本的HTML
        await this.createOptimizedHTML();
        
        console.log(`   ✓ HTML files built: ${htmlFiles.length} files processed`);
    }
    
    async createOptimizedHTML() {
        const templatePath = path.join(this.projectRoot, 'nexus-dashboard-modular.html');
        const outputPath = path.join(this.distDir, 'nexus-dashboard-production.html');
        
        if (fs.existsSync(templatePath)) {
            let content = fs.readFileSync(templatePath, 'utf8');
            
            // 替换为压缩版本的资源
            content = content.replace(
                /href="assets\/css\/(themes|layout|components)\.css"/g,
                'href="assets/css/nexus.min.css"'
            );
            
            content = content.replace(
                /src="assets\/js\/(themes|navigation|rag)\.js"/g,
                'src="assets/js/nexus.min.js"'
            );
            
            // 移除多个CSS链接，只保留一个
            content = content.replace(
                /<link rel="stylesheet" href="assets\/css\/themes\.css">\s*<link rel="stylesheet" href="assets\/css\/layout\.css">\s*<link rel="stylesheet" href="assets\/css\/components\.css">/,
                '<link rel="stylesheet" href="assets/css/nexus.min.css">'
            );
            
            // 移除多个JS脚本，只保留一个
            content = content.replace(
                /<script src="assets\/js\/themes\.js"><\/script>\s*<script src="assets\/js\/navigation\.js"><\/script>\s*<script src="assets\/js\/rag\.js"><\/script>/,
                '<script src="assets/js/nexus.min.js"></script>'
            );
            
            fs.writeFileSync(outputPath, content);
        }
    }
    
    updateAssetPaths(content) {
        // 更新CSS路径为合并版本
        content = content.replace(
            /<link rel="stylesheet" href="assets\/css\/(themes|layout|components)\.css">/g,
            ''
        );
        
        // 添加合并的CSS
        content = content.replace(
            /<link rel="stylesheet" href="assets\/css\/themes\.css">/,
            '<link rel="stylesheet" href="assets/css/nexus.css">'
        );
        
        return content;
    }
    
    async copyStaticAssets() {
        console.log('📋 Copying static assets...');
        
        const staticDirs = ['public'];
        
        for (const dir of staticDirs) {
            const srcDir = path.join(this.projectRoot, dir);
            const destDir = path.join(this.distDir, dir);
            
            if (fs.existsSync(srcDir)) {
                this.copyDirectory(srcDir, destDir);
            }
        }
        
        console.log('   ✓ Static assets copied');
    }
    
    copyDirectory(src, dest) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        const items = fs.readdirSync(src);
        
        for (const item of items) {
            const srcPath = path.join(src, item);
            const destPath = path.join(dest, item);
            
            if (fs.statSync(srcPath).isDirectory()) {
                this.copyDirectory(srcPath, destPath);
            } else {
                fs.copyFileSync(srcPath, destPath);
            }
        }
    }
    
    minifyCSS(css) {
        return css
            .replace(/\/\*[\s\S]*?\*\//g, '') // 移除注释
            .replace(/\s+/g, ' ') // 压缩空白
            .replace(/;\s*}/g, '}') // 移除最后一个分号
            .replace(/\s*{\s*/g, '{') // 压缩大括号
            .replace(/;\s*/g, ';') // 压缩分号
            .trim();
    }
    
    minifyJS(js) {
        return js
            .replace(/\/\*[\s\S]*?\*\//g, '') // 移除块注释
            .replace(/\/\/.*$/gm, '') // 移除行注释
            .replace(/\s+/g, ' ') // 压缩空白
            .replace(/;\s*}/g, '}') // 移除最后一个分号
            .trim();
    }
    
    async generateBuildReport() {
        console.log('📊 Generating build report...');
        
        const report = {
            buildTime: new Date().toISOString(),
            version: '1.0.0',
            modules: {
                css: this.getFileStats(path.join(this.distDir, 'assets', 'css')),
                js: this.getFileStats(path.join(this.distDir, 'assets', 'js')),
                html: this.getFileStats(this.distDir, '.html')
            },
            optimization: this.buildConfig
        };
        
        const reportPath = path.join(this.distDir, 'build-report.json');
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        
        console.log('   ✓ Build report generated');
        console.log(`   📁 Output directory: ${this.distDir}`);
        console.log(`   📊 Total files: ${this.countFiles(this.distDir)}`);
    }
    
    getFileStats(dir, extension = '') {
        if (!fs.existsSync(dir)) return [];
        
        const files = fs.readdirSync(dir)
            .filter(file => extension ? file.endsWith(extension) : true)
            .map(file => {
                const filePath = path.join(dir, file);
                const stats = fs.statSync(filePath);
                return {
                    name: file,
                    size: stats.size,
                    sizeKB: Math.round(stats.size / 1024 * 100) / 100
                };
            });
        
        return files;
    }
    
    countFiles(dir) {
        let count = 0;
        
        const items = fs.readdirSync(dir);
        for (const item of items) {
            const itemPath = path.join(dir, item);
            if (fs.statSync(itemPath).isDirectory()) {
                count += this.countFiles(itemPath);
            } else {
                count++;
            }
        }
        
        return count;
    }
}

// 运行构建
if (import.meta.url === `file://${process.argv[1]}`) {
    const builder = new NexusBuildSystem();
    builder.build();
}

export default NexusBuildSystem;