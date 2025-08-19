/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 音乐模块测试脚本
 */

const MusicScanner = require('./src/backend/services/musicScanner');
const MusicService = require('./src/backend/services/musicService');
const path = require('path');
const fs = require('fs');

async function testMusicModule() {
  console.log('🎵 Changlee\'s Groove 音乐模块测试');
  console.log('=====================================\n');

  try {
    // 测试音乐扫描器
    console.log('1. 测试音乐扫描器...');
    const scanner = new MusicScanner();
    
    // 创建测试音乐文件夹
    const testMusicDir = path.join(__dirname, 'test_music');
    if (!fs.existsSync(testMusicDir)) {
      fs.mkdirSync(testMusicDir, { recursive: true });
      console.log(`   创建测试目录: ${testMusicDir}`);
    }

    // 创建一些测试文件（空文件，仅用于测试扫描功能）
    const testFiles = [
      'Artist1 - Song1.mp3',
      'Artist2 - Song2.wav',
      'Artist1 - Song3.flac',
      'Unknown Song.m4a'
    ];

    testFiles.forEach(filename => {
      const filePath = path.join(testMusicDir, filename);
      if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, ''); // 创建空文件
      }
    });

    // 设置音乐文件夹并扫描
    scanner.setMusicFolders([testMusicDir]);
    const scannedFiles = await scanner.scanAllFolders();
    
    console.log(`   ✅ 扫描完成，发现 ${scannedFiles.length} 个音频文件`);
    scannedFiles.forEach(file => {
      console.log(`      - ${file.artist} - ${file.title} (${file.format})`);
    });

    // 测试统计信息
    const stats = scanner.getStats();
    console.log(`   📊 统计信息:`);
    console.log(`      总文件数: ${stats.totalFiles}`);
    console.log(`      总大小: ${stats.totalSizeFormatted}`);
    console.log(`      艺术家数: ${stats.totalArtists}`);
    console.log(`      支持格式: ${stats.formats.join(', ')}`);

    // 测试搜索功能
    console.log('\n2. 测试搜索功能...');
    const searchResults = scanner.search('Artist1');
    console.log(`   🔍 搜索 "Artist1" 结果: ${searchResults.length} 个文件`);

    // 测试按艺术家分组
    console.log('\n3. 测试艺术家分组...');
    const groupedByArtist = scanner.groupByArtist();
    console.log(`   👥 按艺术家分组:`);
    Object.keys(groupedByArtist).forEach(artist => {
      console.log(`      ${artist}: ${groupedByArtist[artist].length} 首歌`);
    });

    // 测试音乐服务
    console.log('\n4. 测试音乐服务...');
    const musicService = new MusicService();
    
    // 等待服务初始化
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 设置音乐文件夹
    const setFoldersResult = await musicService.setMusicFolders([testMusicDir]);
    console.log(`   📁 设置文件夹: ${setFoldersResult.success ? '成功' : '失败'}`);

    // 扫描音乐
    const scanResult = await musicService.scanMusic();
    console.log(`   🔍 扫描音乐: ${scanResult.success ? '成功' : '失败'}`);
    if (scanResult.success) {
      console.log(`      发现 ${scanResult.data.totalFiles} 个文件`);
    }

    // 获取播放列表
    const playlistResult = musicService.getPlaylist();
    console.log(`   📋 获取播放列表: ${playlistResult.success ? '成功' : '失败'}`);
    if (playlistResult.success) {
      console.log(`      播放列表包含 ${playlistResult.data.playlist.length} 首歌`);
    }

    // 测试播放控制（模拟）
    console.log('\n5. 测试播放控制...');
    if (playlistResult.success && playlistResult.data.playlist.length > 0) {
      const firstTrack = playlistResult.data.playlist[0];
      const playResult = musicService.playTrack(firstTrack.id);
      console.log(`   ▶️  播放音乐: ${playResult.success ? '成功' : '失败'}`);
      
      const pauseResult = musicService.pauseTrack();
      console.log(`   ⏸️  暂停播放: ${pauseResult.success ? '成功' : '失败'}`);
      
      const resumeResult = musicService.resumeTrack();
      console.log(`   ▶️  恢复播放: ${resumeResult.success ? '成功' : '失败'}`);
    }

    // 测试音量和播放模式
    console.log('\n6. 测试音量和播放模式...');
    const volumeResult = await musicService.setVolume(0.8);
    console.log(`   🔊 设置音量: ${volumeResult.success ? '成功' : '失败'}`);
    
    const modeResult = await musicService.setPlayMode('random');
    console.log(`   🔀 设置播放模式: ${modeResult.success ? '成功' : '失败'}`);

    // 获取播放状态
    const stateResult = musicService.getPlaybackState();
    console.log(`   📊 获取播放状态: ${stateResult.success ? '成功' : '失败'}`);
    if (stateResult.success) {
      const state = stateResult.data;
      console.log(`      当前音乐: ${state.currentTrack ? state.currentTrack.title : '无'}`);
      console.log(`      播放状态: ${state.isPlaying ? '播放中' : '已暂停'}`);
      console.log(`      音量: ${Math.round(state.volume * 100)}%`);
      console.log(`      播放模式: ${state.playMode}`);
    }

    console.log('\n✅ 音乐模块测试完成！');
    console.log('\n🎵 Changlee\'s Groove 音乐模块功能正常');
    
    // 清理测试文件
    console.log('\n🧹 清理测试文件...');
    testFiles.forEach(filename => {
      const filePath = path.join(testMusicDir, filename);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    });
    if (fs.existsSync(testMusicDir)) {
      fs.rmdirSync(testMusicDir);
    }
    console.log('   测试文件清理完成');

  } catch (error) {
    console.error('❌ 测试过程中出现错误:', error);
  }
}

// 运行测试
if (require.main === module) {
  testMusicModule();
}

module.exports = { testMusicModule };