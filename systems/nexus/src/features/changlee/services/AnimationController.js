/**
 * AnimationController - 动画控制器服务
 * 
 * 这是控制"长离"所有动作的"小脑"
 * 负责播放、停止、切换各种动画，支持3D和2D两种模式
 * 
 * 功能：
 * - 播放指定动画 (行走、睡觉、揣手手等)
 * - 动画队列管理
 * - 动画混合和过渡
 * - 表情和动作同步
 */

class AnimationController {
  constructor(renderMode = '3D') {
    this.renderMode = renderMode;
    this.currentModel = null;
    this.currentAnimation = null;
    this.animationMixer = null; // Three.js AnimationMixer
    this.animationActions = new Map(); // 动画动作缓存
    this.animationQueue = []; // 动画队列
    this.isPlaying = false;
    this.isPaused = false;
    this.animationTime = 0;
    this.animationSpeed = 1.0;
    
    // 回调函数
    this.onAnimationStart = null;
    this.onAnimationComplete = null;
    this.onAnimationLoop = null;
    
    // 内置动画定义
    this.builtInAnimations = this._initBuiltInAnimations();
    
    console.log(`🎭 AnimationController 初始化 - 渲染模式: ${renderMode}`);
  }

  /**
   * 初始化内置动画定义
   */
  _initBuiltInAnimations() {
    return {
      // 基础动画
      idle: {
        name: 'idle',
        displayName: '待机',
        duration: 2000,
        loop: true,
        priority: 0
      },
      
      // 情绪动画
      happy: {
        name: 'happy',
        displayName: '开心',
        duration: 1500,
        loop: false,
        priority: 2
      },
      
      sad: {
        name: 'sad',
        displayName: '难过',
        duration: 2000,
        loop: false,
        priority: 2
      },
      
      angry: {
        name: 'angry',
        displayName: '生气',
        duration: 1000,
        loop: false,
        priority: 3
      },
      
      surprised: {
        name: 'surprised',
        displayName: '惊讶',
        duration: 800,
        loop: false,
        priority: 2
      },
      
      // 动作动画
      walk: {
        name: 'walk',
        displayName: '行走',
        duration: 1000,
        loop: true,
        priority: 1
      },
      
      run: {
        name: 'run',
        displayName: '奔跑',
        duration: 600,
        loop: true,
        priority: 1
      },
      
      jump: {
        name: 'jump',
        displayName: '跳跃',
        duration: 1200,
        loop: false,
        priority: 2
      },
      
      sleep: {
        name: 'sleep',
        displayName: '睡觉',
        duration: 3000,
        loop: true,
        priority: 1
      },
      
      eat: {
        name: 'eat',
        displayName: '吃饭',
        duration: 2000,
        loop: false,
        priority: 2
      },
      
      // 特殊动画
      wave: {
        name: 'wave',
        displayName: '挥手',
        duration: 1500,
        loop: false,
        priority: 2
      },
      
      dance: {
        name: 'dance',
        displayName: '跳舞',
        duration: 4000,
        loop: true,
        priority: 2
      },
      
      stretch: {
        name: 'stretch',
        displayName: '伸懒腰',
        duration: 2500,
        loop: false,
        priority: 1
      },
      
      // 长离特有动画
      changlee_thinking: {
        name: 'changlee_thinking',
        displayName: '思考',
        duration: 3000,
        loop: true,
        priority: 1
      },
      
      changlee_cute: {
        name: 'changlee_cute',
        displayName: '卖萌',
        duration: 2000,
        loop: false,
        priority: 2
      },
      
      changlee_magic: {
        name: 'changlee_magic',
        displayName: '施法',
        duration: 2500,
        loop: false,
        priority: 3
      }
    };
  }

  /**
   * 设置当前模型
   */
  setModel(model) {
    this.currentModel = model;
    
    if (this.renderMode === '3D' && model && window.THREE) {
      // 初始化3D动画混合器
      this._init3DAnimationMixer(model);
    } else if (this.renderMode === '2D' && model) {
      // 初始化2D动画系统
      this._init2DAnimationSystem(model);
    }
    
    console.log(`🎯 AnimationController 设置模型:`, model?.userData?.type || 'unknown');
  }

  /**
   * 初始化3D动画混合器
   */
  _init3DAnimationMixer(model) {
    if (this.animationMixer) {
      this.animationMixer.stopAllAction();
    }
    
    this.animationMixer = new window.THREE.AnimationMixer(model);
    this.animationActions.clear();
    
    // 如果模型有内置动画
    if (model.userData.animations && model.userData.animations.length > 0) {
      model.userData.animations.forEach((clip) => {
        const action = this.animationMixer.clipAction(clip);
        this.animationActions.set(clip.name, action);
        console.log(`📽️ 注册3D动画: ${clip.name}`);
      });
    }
    
    console.log('✅ 3D动画混合器初始化完成');
  }

  /**
   * 初始化2D动画系统
   */
  _init2DAnimationSystem(model) {
    // 为2D模型设置动画系统
    if (!model.userData.animationSystem) {
      model.userData.animationSystem = {
        currentAnimation: 'idle',
        animationTime: 0,
        animationSpeed: 1.0,
        animations: new Map()
      };
    }
    
    console.log('✅ 2D动画系统初始化完成');
  }

  /**
   * 播放动画
   */
  playAnimation(animationName, options = {}) {
    if (!this.currentModel) {
      console.warn('⚠️ 没有设置模型，无法播放动画');
      return false;
    }

    const {
      loop = null,
      speed = 1.0,
      fadeIn = 0.3,
      fadeOut = 0.3,
      priority = 1,
      queue = false
    } = options;

    // 获取动画定义
    const animationDef = this.builtInAnimations[animationName];
    if (!animationDef) {
      console.warn(`⚠️ 未知的动画: ${animationName}`);
      return false;
    }

    // 检查优先级
    if (this.currentAnimation && 
        this.builtInAnimations[this.currentAnimation]?.priority > priority) {
      if (queue) {
        this.animationQueue.push({ animationName, options });
        console.log(`📋 动画已加入队列: ${animationName}`);
        return true;
      } else {
        console.log(`⏭️ 动画优先级不足，跳过: ${animationName}`);
        return false;
      }
    }

    try {
      if (this.renderMode === '3D') {
        return this._play3DAnimation(animationName, animationDef, options);
      } else {
        return this._play2DAnimation(animationName, animationDef, options);
      }
    } catch (error) {
      console.error(`❌ 播放动画失败: ${animationName}`, error);
      return false;
    }
  }

  /**
   * 播放3D动画
   */
  _play3DAnimation(animationName, animationDef, options) {
    const { loop, speed, fadeIn, fadeOut } = options;
    
    // 检查是否有对应的动画动作
    if (this.animationActions.has(animationName)) {
      // 播放模型自带的动画
      const action = this.animationActions.get(animationName);
      
      // 停止当前动画
      if (this.currentAnimation && this.animationActions.has(this.currentAnimation)) {
        const currentAction = this.animationActions.get(this.currentAnimation);
        currentAction.fadeOut(fadeOut);
      }
      
      // 设置新动画
      action.reset();
      action.setLoop(loop !== null ? 
        (loop ? window.THREE.LoopRepeat : window.THREE.LoopOnce) : 
        (animationDef.loop ? window.THREE.LoopRepeat : window.THREE.LoopOnce)
      );
      action.timeScale = speed;
      action.fadeIn(fadeIn);
      action.play();
      
      console.log(`🎬 播放3D模型动画: ${animationName}`);
    } else {
      // 播放程序化动画
      this._playProcedural3DAnimation(animationName, animationDef, options);
    }
    
    this.currentAnimation = animationName;
    this.isPlaying = true;
    this.animationTime = 0;
    this.animationSpeed = speed;
    
    if (this.onAnimationStart) {
      this.onAnimationStart(animationName, animationDef);
    }
    
    return true;
  }

  /**
   * 播放程序化3D动画
   */
  _playProcedural3DAnimation(animationName, animationDef, options) {
    if (!this.currentModel.userData.proceduralAnimation) {
      this.currentModel.userData.proceduralAnimation = {
        name: animationName,
        startTime: Date.now(),
        duration: animationDef.duration,
        loop: animationDef.loop,
        speed: options.speed || 1.0
      };
    } else {
      // 更新动画参数
      Object.assign(this.currentModel.userData.proceduralAnimation, {
        name: animationName,
        startTime: Date.now(),
        duration: animationDef.duration,
        loop: animationDef.loop,
        speed: options.speed || 1.0
      });
    }
    
    console.log(`🎨 播放程序化3D动画: ${animationName}`);
  }

  /**
   * 播放2D动画
   */
  _play2DAnimation(animationName, animationDef, options) {
    const { loop, speed } = options;
    
    if (this.currentModel.userData.animationSystem) {
      const animSystem = this.currentModel.userData.animationSystem;
      animSystem.currentAnimation = animationName;
      animSystem.animationTime = 0;
      animSystem.animationSpeed = speed;
      animSystem.loop = loop !== null ? loop : animationDef.loop;
      animSystem.duration = animationDef.duration;
    }
    
    this.currentAnimation = animationName;
    this.isPlaying = true;
    this.animationTime = 0;
    this.animationSpeed = speed;
    
    if (this.onAnimationStart) {
      this.onAnimationStart(animationName, animationDef);
    }
    
    console.log(`🎨 播放2D动画: ${animationName}`);
    return true;
  }

  /**
   * 停止动画
   */
  stopAnimation() {
    if (!this.isPlaying) return;
    
    if (this.renderMode === '3D' && this.animationMixer) {
      this.animationMixer.stopAllAction();
    }
    
    if (this.currentModel?.userData?.proceduralAnimation) {
      delete this.currentModel.userData.proceduralAnimation;
    }
    
    if (this.currentModel?.userData?.animationSystem) {
      this.currentModel.userData.animationSystem.currentAnimation = 'idle';
      this.currentModel.userData.animationSystem.animationTime = 0;
    }
    
    this.isPlaying = false;
    this.currentAnimation = null;
    
    console.log('⏹️ 动画已停止');
  }

  /**
   * 暂停动画
   */
  pauseAnimation() {
    if (!this.isPlaying || this.isPaused) return;
    
    if (this.renderMode === '3D' && this.animationMixer) {
      this.animationMixer.timeScale = 0;
    }
    
    this.isPaused = true;
    console.log('⏸️ 动画已暂停');
  }

  /**
   * 恢复动画
   */
  resumeAnimation() {
    if (!this.isPlaying || !this.isPaused) return;
    
    if (this.renderMode === '3D' && this.animationMixer) {
      this.animationMixer.timeScale = this.animationSpeed;
    }
    
    this.isPaused = false;
    console.log('▶️ 动画已恢复');
  }

  /**
   * 更新动画 (每帧调用)
   */
  update(deltaTime = 0.016) {
    if (!this.isPlaying || this.isPaused || !this.currentModel) return;
    
    this.animationTime += deltaTime * 1000; // 转换为毫秒
    
    if (this.renderMode === '3D') {
      this._update3DAnimation(deltaTime);
    } else {
      this._update2DAnimation(deltaTime);
    }
    
    // 检查动画是否完成
    this._checkAnimationComplete();
    
    // 处理动画队列
    this._processAnimationQueue();
  }

  /**
   * 更新3D动画
   */
  _update3DAnimation(deltaTime) {
    // 更新动画混合器
    if (this.animationMixer) {
      this.animationMixer.update(deltaTime);
    }
    
    // 更新程序化动画
    if (this.currentModel.userData.proceduralAnimation) {
      this._updateProcedural3DAnimation(deltaTime);
    }
  }

  /**
   * 更新程序化3D动画
   */
  _updateProcedural3DAnimation(deltaTime) {
    const procAnim = this.currentModel.userData.proceduralAnimation;
    const elapsed = Date.now() - procAnim.startTime;
    const progress = (elapsed / procAnim.duration) * procAnim.speed;
    
    switch (procAnim.name) {
      case 'idle':
        this._animateIdle3D(progress);
        break;
      case 'happy':
        this._animateHappy3D(progress);
        break;
      case 'sleep':
        this._animateSleep3D(progress);
        break;
      case 'walk':
        this._animateWalk3D(progress);
        break;
      case 'jump':
        this._animateJump3D(progress);
        break;
      case 'wave':
        this._animateWave3D(progress);
        break;
      case 'dance':
        this._animateDance3D(progress);
        break;
      case 'changlee_thinking':
        this._animateChangleeThinking3D(progress);
        break;
      case 'changlee_cute':
        this._animateChangleeCute3D(progress);
        break;
      case 'changlee_magic':
        this._animateChangleeMagic3D(progress);
        break;
    }
  }

  /**
   * 3D待机动画
   */
  _animateIdle3D(progress) {
    if (!this.currentModel) return;
    
    // 轻微的呼吸效果
    const breathScale = 1 + Math.sin(progress * Math.PI * 2) * 0.02;
    this.currentModel.scale.setScalar(breathScale);
    
    // 轻微的左右摇摆
    this.currentModel.rotation.y = Math.sin(progress * Math.PI) * 0.1;
  }

  /**
   * 3D开心动画
   */
  _animateHappy3D(progress) {
    if (!this.currentModel) return;
    
    // 快速跳跃
    const jumpHeight = Math.abs(Math.sin(progress * Math.PI * 4)) * 0.5;
    this.currentModel.position.y = jumpHeight;
    
    // 快速旋转
    this.currentModel.rotation.y = progress * Math.PI * 2;
    
    // 缩放变化
    const scale = 1 + Math.sin(progress * Math.PI * 8) * 0.1;
    this.currentModel.scale.setScalar(scale);
  }

  /**
   * 3D睡觉动画
   */
  _animateSleep3D(progress) {
    if (!this.currentModel) return;
    
    // 慢慢躺下
    const rotationX = Math.min(progress * Math.PI / 2, Math.PI / 2);
    this.currentModel.rotation.x = rotationX;
    
    // 慢慢缩小
    const scale = Math.max(1 - progress * 0.2, 0.8);
    this.currentModel.scale.setScalar(scale);
    
    // 轻微的呼吸
    const breathOffset = Math.sin(progress * Math.PI * 4) * 0.01;
    this.currentModel.scale.y = scale + breathOffset;
  }

  /**
   * 3D行走动画
   */
  _animateWalk3D(progress) {
    if (!this.currentModel) return;
    
    // 上下起伏
    const bobHeight = Math.sin(progress * Math.PI * 4) * 0.1;
    this.currentModel.position.y = bobHeight;
    
    // 左右摇摆
    const sway = Math.sin(progress * Math.PI * 2) * 0.05;
    this.currentModel.rotation.z = sway;
    
    // 前后倾斜
    const lean = Math.sin(progress * Math.PI * 4) * 0.1;
    this.currentModel.rotation.x = lean;
  }

  /**
   * 3D跳跃动画
   */
  _animateJump3D(progress) {
    if (!this.currentModel) return;
    
    // 抛物线跳跃
    const jumpHeight = Math.sin(progress * Math.PI) * 2;
    this.currentModel.position.y = jumpHeight;
    
    // 空中旋转
    if (progress > 0.2 && progress < 0.8) {
      this.currentModel.rotation.y = (progress - 0.2) * Math.PI * 2;
    }
    
    // 起跳和落地时的压缩
    let scaleY = 1;
    if (progress < 0.1) {
      scaleY = 1 - progress * 2; // 压缩
    } else if (progress > 0.9) {
      scaleY = 1 - (1 - progress) * 2; // 压缩
    }
    this.currentModel.scale.y = Math.max(scaleY, 0.5);
  }

  /**
   * 3D挥手动画
   */
  _animateWave3D(progress) {
    if (!this.currentModel) return;
    
    // 整体轻微摇摆
    const sway = Math.sin(progress * Math.PI * 6) * 0.1;
    this.currentModel.rotation.z = sway;
    
    // 如果有手臂部件，可以单独控制
    if (this.currentModel.userData.parts?.rightEar) {
      const ear = this.currentModel.userData.parts.rightEar;
      ear.rotation.z = 0.3 + Math.sin(progress * Math.PI * 8) * 0.5;
    }
  }

  /**
   * 3D跳舞动画
   */
  _animateDance3D(progress) {
    if (!this.currentModel) return;
    
    // 复杂的舞蹈动作
    const time = progress * Math.PI * 2;
    
    // 旋转
    this.currentModel.rotation.y = Math.sin(time) * 0.5;
    
    // 上下跳动
    this.currentModel.position.y = Math.abs(Math.sin(time * 2)) * 0.3;
    
    // 左右摇摆
    this.currentModel.rotation.z = Math.sin(time * 1.5) * 0.2;
    
    // 缩放变化
    const scale = 1 + Math.sin(time * 3) * 0.05;
    this.currentModel.scale.setScalar(scale);
  }

  /**
   * 长离思考动画
   */
  _animateChangleeThinking3D(progress) {
    if (!this.currentModel) return;
    
    // 头部轻微点头
    if (this.currentModel.userData.parts?.head) {
      const head = this.currentModel.userData.parts.head;
      head.rotation.x = Math.sin(progress * Math.PI * 2) * 0.1;
    }
    
    // 耳朵轻微摆动
    if (this.currentModel.userData.parts?.leftEar) {
      const leftEar = this.currentModel.userData.parts.leftEar;
      leftEar.rotation.z = -0.3 + Math.sin(progress * Math.PI * 3) * 0.1;
    }
    
    if (this.currentModel.userData.parts?.rightEar) {
      const rightEar = this.currentModel.userData.parts.rightEar;
      rightEar.rotation.z = 0.3 + Math.sin(progress * Math.PI * 3 + Math.PI) * 0.1;
    }
  }

  /**
   * 长离卖萌动画
   */
  _animateChangleeCute3D(progress) {
    if (!this.currentModel) return;
    
    // 快速眨眼效果 (通过缩放眼睛)
    if (this.currentModel.userData.parts?.leftEye && this.currentModel.userData.parts?.rightEye) {
      const blinkTime = Math.sin(progress * Math.PI * 10);
      const eyeScale = blinkTime > 0.8 ? 0.1 : 1;
      
      this.currentModel.userData.parts.leftEye.scale.y = eyeScale;
      this.currentModel.userData.parts.rightEye.scale.y = eyeScale;
    }
    
    // 头部倾斜
    if (this.currentModel.userData.parts?.head) {
      const head = this.currentModel.userData.parts.head;
      head.rotation.z = Math.sin(progress * Math.PI) * 0.3;
    }
    
    // 整体轻微跳动
    this.currentModel.position.y = Math.abs(Math.sin(progress * Math.PI * 6)) * 0.1;
  }

  /**
   * 长离施法动画
   */
  _animateChangleeMagic3D(progress) {
    if (!this.currentModel) return;
    
    // 神秘的旋转
    this.currentModel.rotation.y = progress * Math.PI * 4;
    
    // 上升效果
    this.currentModel.position.y = Math.sin(progress * Math.PI) * 0.5;
    
    // 魔法光环效果 (通过缩放和透明度变化)
    const glowScale = 1 + Math.sin(progress * Math.PI * 8) * 0.2;
    this.currentModel.scale.setScalar(glowScale);
    
    // 耳朵和尾巴的特殊动作
    if (this.currentModel.userData.parts?.tail) {
      const tail = this.currentModel.userData.parts.tail;
      tail.rotation.x = Math.PI / 4 + Math.sin(progress * Math.PI * 6) * 0.3;
    }
  }

  /**
   * 更新2D动画
   */
  _update2DAnimation(deltaTime) {
    if (!this.currentModel?.userData?.animationSystem) return;
    
    const animSystem = this.currentModel.userData.animationSystem;
    animSystem.animationTime += deltaTime * 1000 * animSystem.animationSpeed;
    
    const progress = (animSystem.animationTime / animSystem.duration) % 1;
    
    switch (animSystem.currentAnimation) {
      case 'idle':
        this._animateIdle2D(progress);
        break;
      case 'happy':
        this._animateHappy2D(progress);
        break;
      case 'sleep':
        this._animateSleep2D(progress);
        break;
      case 'walk':
        this._animateWalk2D(progress);
        break;
      // 可以添加更多2D动画...
    }
  }

  /**
   * 2D待机动画
   */
  _animateIdle2D(progress) {
    if (!this.currentModel) return;
    
    // 轻微的呼吸效果
    const breathScale = 1 + Math.sin(progress * Math.PI * 2) * 0.02;
    this.currentModel.scale.set(breathScale, breathScale);
    
    // 轻微的左右摇摆
    this.currentModel.rotation = Math.sin(progress * Math.PI) * 0.05;
  }

  /**
   * 2D开心动画
   */
  _animateHappy2D(progress) {
    if (!this.currentModel) return;
    
    // 快速跳跃
    const jumpHeight = Math.abs(Math.sin(progress * Math.PI * 4)) * 20;
    this.currentModel.y = this.currentModel.userData.originalY - jumpHeight;
    
    // 快速旋转
    this.currentModel.rotation = progress * Math.PI * 2;
    
    // 缩放变化
    const scale = 1 + Math.sin(progress * Math.PI * 8) * 0.1;
    this.currentModel.scale.set(scale, scale);
  }

  /**
   * 2D睡觉动画
   */
  _animateSleep2D(progress) {
    if (!this.currentModel) return;
    
    // 慢慢倾斜
    this.currentModel.rotation = Math.min(progress * Math.PI / 4, Math.PI / 4);
    
    // 慢慢缩小
    const scale = Math.max(1 - progress * 0.2, 0.8);
    this.currentModel.scale.set(scale, scale);
    
    // 透明度变化 (模拟睡意)
    this.currentModel.alpha = Math.max(1 - progress * 0.3, 0.7);
  }

  /**
   * 2D行走动画
   */
  _animateWalk2D(progress) {
    if (!this.currentModel) return;
    
    // 上下起伏
    const bobHeight = Math.sin(progress * Math.PI * 4) * 5;
    this.currentModel.y = this.currentModel.userData.originalY + bobHeight;
    
    // 左右摇摆
    this.currentModel.rotation = Math.sin(progress * Math.PI * 2) * 0.1;
    
    // 水平移动 (如果需要)
    // this.currentModel.x += Math.cos(progress * Math.PI * 2) * 2;
  }

  /**
   * 检查动画是否完成
   */
  _checkAnimationComplete() {
    if (!this.currentAnimation || !this.isPlaying) return;
    
    const animationDef = this.builtInAnimations[this.currentAnimation];
    if (!animationDef) return;
    
    // 检查非循环动画是否完成
    if (!animationDef.loop && this.animationTime >= animationDef.duration) {
      console.log(`🏁 动画完成: ${this.currentAnimation}`);
      
      if (this.onAnimationComplete) {
        this.onAnimationComplete(this.currentAnimation, animationDef);
      }
      
      // 回到待机状态
      this.playAnimation('idle');
    }
  }

  /**
   * 处理动画队列
   */
  _processAnimationQueue() {
    if (this.animationQueue.length === 0) return;
    
    // 如果当前没有高优先级动画在播放，播放队列中的下一个
    const currentPriority = this.currentAnimation ? 
      this.builtInAnimations[this.currentAnimation]?.priority || 0 : 0;
    
    if (currentPriority <= 1) { // 只有在播放低优先级动画时才处理队列
      const nextAnimation = this.animationQueue.shift();
      if (nextAnimation) {
        console.log(`📋 从队列播放动画: ${nextAnimation.animationName}`);
        this.playAnimation(nextAnimation.animationName, nextAnimation.options);
      }
    }
  }

  /**
   * 获取可用动画列表
   */
  getAvailableAnimations() {
    return Object.keys(this.builtInAnimations).map(name => ({
      name,
      ...this.builtInAnimations[name]
    }));
  }

  /**
   * 获取当前动画状态
   */
  getAnimationStatus() {
    return {
      currentAnimation: this.currentAnimation,
      isPlaying: this.isPlaying,
      isPaused: this.isPaused,
      animationTime: this.animationTime,
      animationSpeed: this.animationSpeed,
      queueLength: this.animationQueue.length,
      renderMode: this.renderMode
    };
  }

  /**
   * 清空动画队列
   */
  clearAnimationQueue() {
    this.animationQueue = [];
    console.log('🗑️ 动画队列已清空');
  }

  /**
   * 设置动画速度
   */
  setAnimationSpeed(speed) {
    this.animationSpeed = Math.max(0.1, Math.min(speed, 5.0)); // 限制在0.1-5.0之间
    
    if (this.renderMode === '3D' && this.animationMixer) {
      this.animationMixer.timeScale = this.animationSpeed;
    }
    
    if (this.currentModel?.userData?.animationSystem) {
      this.currentModel.userData.animationSystem.animationSpeed = this.animationSpeed;
    }
    
    console.log(`⚡ 动画速度设置为: ${this.animationSpeed}x`);
  }

  /**
   * 切换渲染模式
   */
  switchRenderMode(newMode) {
    if (this.renderMode !== newMode) {
      console.log(`🔄 AnimationController 切换渲染模式: ${this.renderMode} -> ${newMode}`);
      
      // 停止当前动画
      this.stopAnimation();
      
      // 清理旧的动画系统
      if (this.animationMixer) {
        this.animationMixer.stopAllAction();
        this.animationMixer = null;
      }
      
      this.animationActions.clear();
      this.renderMode = newMode;
      
      // 如果有模型，重新初始化动画系统
      if (this.currentModel) {
        this.setModel(this.currentModel);
      }
    }
  }

  /**
   * 销毁动画控制器
   */
  destroy() {
    this.stopAnimation();
    this.clearAnimationQueue();
    
    if (this.animationMixer) {
      this.animationMixer.stopAllAction();
      this.animationMixer = null;
    }
    
    this.animationActions.clear();
    this.currentModel = null;
    
    console.log('🗑️ AnimationController 已销毁');
  }
}

export { AnimationController };