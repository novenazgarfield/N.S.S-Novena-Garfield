/**
 * ModelLoader - 模型加载器服务
 * 
 * 这是负责从硬盘读取模型文件，并把它"放"到舞台上的"后台装卸工"
 * 支持3D模型(.gltf, .glb)和2D模型(Live2D, Spine)的加载
 * 
 * 技术栈：
 * - 3D模型: GLTFLoader from three/examples/jsm/loaders/GLTFLoader.js
 * - 2D模型: Live2D, Spine
 * - 占位符: Three.js内置几何体
 */

class ModelLoader {
  constructor(renderMode = '3D') {
    this.renderMode = renderMode;
    this.loadedModels = new Map(); // 模型缓存
    this.loadingPromises = new Map(); // 加载中的Promise缓存
    this.onModelLoaded = null; // 模型加载完成回调
    this.onLoadProgress = null; // 加载进度回调
    this.onLoadError = null; // 加载错误回调
    
    console.log(`🔧 ModelLoader 初始化 - 渲染模式: ${renderMode}`);
  }

  /**
   * 动态加载GLTFLoader
   */
  async loadGLTFLoader() {
    try {
      if (!window.GLTFLoader && window.THREE) {
        // 从CDN加载GLTFLoader
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r158/examples/js/loaders/GLTFLoader.js';
        script.async = true;
        
        return new Promise((resolve, reject) => {
          script.onload = () => {
            console.log('✅ GLTFLoader 加载完成');
            resolve(window.THREE.GLTFLoader);
          };
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }
      return window.THREE?.GLTFLoader;
    } catch (error) {
      console.error('❌ GLTFLoader 加载失败:', error);
      throw error;
    }
  }

  /**
   * 加载3D模型 (.gltf, .glb)
   */
  async load3DModel(modelPath) {
    if (!window.THREE) {
      throw new Error('Three.js 未加载');
    }

    // 检查缓存
    if (this.loadedModels.has(modelPath)) {
      console.log(`📦 从缓存加载3D模型: ${modelPath}`);
      return this.loadedModels.get(modelPath).clone();
    }

    // 检查是否正在加载
    if (this.loadingPromises.has(modelPath)) {
      console.log(`⏳ 等待3D模型加载完成: ${modelPath}`);
      return await this.loadingPromises.get(modelPath);
    }

    // 开始加载
    const loadingPromise = this._load3DModelInternal(modelPath);
    this.loadingPromises.set(modelPath, loadingPromise);

    try {
      const model = await loadingPromise;
      this.loadedModels.set(modelPath, model);
      this.loadingPromises.delete(modelPath);
      return model.clone();
    } catch (error) {
      this.loadingPromises.delete(modelPath);
      throw error;
    }
  }

  /**
   * 内部3D模型加载方法
   */
  async _load3DModelInternal(modelPath) {
    const GLTFLoader = await this.loadGLTFLoader();
    if (!GLTFLoader) {
      throw new Error('GLTFLoader 不可用');
    }

    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      
      loader.load(
        modelPath,
        // 加载成功
        (gltf) => {
          console.log(`✅ 3D模型加载成功: ${modelPath}`);
          
          const model = gltf.scene;
          
          // 设置模型属性
          model.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
              child.receiveShadow = true;
            }
          });
          
          // 居中模型
          const box = new window.THREE.Box3().setFromObject(model);
          const center = box.getCenter(new window.THREE.Vector3());
          model.position.sub(center);
          
          // 缩放到合适大小
          const size = box.getSize(new window.THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z);
          const scale = 2 / maxDim; // 缩放到2个单位大小
          model.scale.setScalar(scale);
          
          // 保存动画
          if (gltf.animations && gltf.animations.length > 0) {
            model.userData.animations = gltf.animations;
            model.userData.mixer = new window.THREE.AnimationMixer(model);
          }
          
          if (this.onModelLoaded) {
            this.onModelLoaded(model, 'gltf');
          }
          
          resolve(model);
        },
        // 加载进度
        (progress) => {
          const percent = (progress.loaded / progress.total) * 100;
          console.log(`📊 3D模型加载进度: ${percent.toFixed(1)}%`);
          
          if (this.onLoadProgress) {
            this.onLoadProgress(percent, modelPath);
          }
        },
        // 加载错误
        (error) => {
          console.error(`❌ 3D模型加载失败: ${modelPath}`, error);
          
          if (this.onLoadError) {
            this.onLoadError(error, modelPath);
          }
          
          reject(error);
        }
      );
    });
  }

  /**
   * 加载2D模型 (Live2D, Spine等)
   */
  async load2DModel(modelPath, modelType = 'live2d') {
    if (!window.PIXI) {
      throw new Error('PIXI.js 未加载');
    }

    // 检查缓存
    const cacheKey = `${modelPath}_${modelType}`;
    if (this.loadedModels.has(cacheKey)) {
      console.log(`📦 从缓存加载2D模型: ${modelPath}`);
      return this.loadedModels.get(cacheKey);
    }

    try {
      let model;
      
      switch (modelType.toLowerCase()) {
        case 'live2d':
          model = await this._loadLive2DModel(modelPath);
          break;
        case 'spine':
          model = await this._loadSpineModel(modelPath);
          break;
        case 'sprite':
          model = await this._loadSpriteModel(modelPath);
          break;
        default:
          throw new Error(`不支持的2D模型类型: ${modelType}`);
      }
      
      this.loadedModels.set(cacheKey, model);
      
      if (this.onModelLoaded) {
        this.onModelLoaded(model, modelType);
      }
      
      return model;
    } catch (error) {
      console.error(`❌ 2D模型加载失败: ${modelPath}`, error);
      throw error;
    }
  }

  /**
   * 加载Live2D模型
   */
  async _loadLive2DModel(modelPath) {
    // 这里需要Live2D SDK
    // 暂时返回占位符
    console.log(`🔄 Live2D模型加载 (占位符): ${modelPath}`);
    
    const container = new window.PIXI.Container();
    
    // 创建简单的Live2D风格占位符
    const graphics = new window.PIXI.Graphics();
    graphics.beginFill(0xFFB6C1, 0.8); // 粉色
    graphics.drawEllipse(0, 0, 100, 120);
    graphics.endFill();
    
    // 添加简单的表情
    graphics.beginFill(0x000000);
    graphics.drawCircle(-30, -20, 8); // 左眼
    graphics.drawCircle(30, -20, 8);  // 右眼
    graphics.endFill();
    
    graphics.beginFill(0xFF69B4);
    graphics.drawEllipse(0, 10, 20, 10); // 嘴巴
    graphics.endFill();
    
    container.addChild(graphics);
    container.userData = {
      type: 'live2d',
      animations: ['idle', 'happy', 'blink'],
      currentAnimation: 'idle'
    };
    
    return container;
  }

  /**
   * 加载Spine模型
   */
  async _loadSpineModel(modelPath) {
    // 这里需要Spine运行时
    // 暂时返回占位符
    console.log(`🔄 Spine模型加载 (占位符): ${modelPath}`);
    
    const container = new window.PIXI.Container();
    
    // 创建简单的Spine风格占位符
    const graphics = new window.PIXI.Graphics();
    graphics.beginFill(0x98FB98, 0.8); // 浅绿色
    graphics.drawRoundedRect(-50, -60, 100, 120, 10);
    graphics.endFill();
    
    // 添加骨骼风格的线条
    graphics.lineStyle(2, 0x228B22);
    graphics.moveTo(0, -60);
    graphics.lineTo(0, 60);
    graphics.moveTo(-40, -30);
    graphics.lineTo(40, -30);
    graphics.moveTo(-40, 30);
    graphics.lineTo(40, 30);
    
    container.addChild(graphics);
    container.userData = {
      type: 'spine',
      animations: ['idle', 'walk', 'jump', 'attack'],
      currentAnimation: 'idle'
    };
    
    return container;
  }

  /**
   * 加载精灵图模型
   */
  async _loadSpriteModel(modelPath) {
    return new Promise((resolve, reject) => {
      const texture = window.PIXI.Texture.from(modelPath);
      
      texture.baseTexture.on('loaded', () => {
        const sprite = new window.PIXI.Sprite(texture);
        sprite.anchor.set(0.5);
        sprite.userData = {
          type: 'sprite',
          animations: ['idle'],
          currentAnimation: 'idle'
        };
        
        console.log(`✅ 精灵图加载成功: ${modelPath}`);
        resolve(sprite);
      });
      
      texture.baseTexture.on('error', (error) => {
        console.error(`❌ 精灵图加载失败: ${modelPath}`, error);
        reject(error);
      });
    });
  }

  /**
   * 创建3D占位模型
   */
  create3DPlaceholder(type = 'changlee') {
    if (!window.THREE) {
      throw new Error('Three.js 未加载');
    }

    const THREE = window.THREE;
    const group = new THREE.Group();

    switch (type) {
      case 'changlee':
        // 长离风格的占位模型
        return this._createChangleePlaceholder3D(THREE, group);
      case 'cube':
        return this._createCubePlaceholder3D(THREE, group);
      case 'sphere':
        return this._createSpherePlaceholder3D(THREE, group);
      default:
        return this._createChangleePlaceholder3D(THREE, group);
    }
  }

  /**
   * 创建长离风格的3D占位模型
   */
  _createChangleePlaceholder3D(THREE, group) {
    // 身体 - 圆柱体
    const bodyGeometry = new THREE.CylinderGeometry(0.8, 1.0, 2.0, 8);
    const bodyMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x4a90e2, // 蓝色
      transparent: true,
      opacity: 0.9
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0;
    body.castShadow = true;
    body.receiveShadow = true;
    group.add(body);

    // 头部 - 球体
    const headGeometry = new THREE.SphereGeometry(0.6, 16, 16);
    const headMaterial = new THREE.MeshLambertMaterial({ 
      color: 0xf5a623, // 橙色
      transparent: true,
      opacity: 0.9
    });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.5;
    head.castShadow = true;
    head.receiveShadow = true;
    group.add(head);

    // 眼睛
    const eyeGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const eyeMaterial = new THREE.MeshLambertMaterial({ color: 0x000000 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.2, 1.6, 0.5);
    group.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.2, 1.6, 0.5);
    group.add(rightEye);

    // 耳朵 - 三角锥
    const earGeometry = new THREE.ConeGeometry(0.2, 0.5, 4);
    const earMaterial = new THREE.MeshLambertMaterial({ color: 0xf5a623 });
    
    const leftEar = new THREE.Mesh(earGeometry, earMaterial);
    leftEar.position.set(-0.4, 2.0, 0);
    leftEar.rotation.z = -0.3;
    leftEar.castShadow = true;
    group.add(leftEar);
    
    const rightEar = new THREE.Mesh(earGeometry, earMaterial);
    rightEar.position.set(0.4, 2.0, 0);
    rightEar.rotation.z = 0.3;
    rightEar.castShadow = true;
    group.add(rightEar);

    // 尾巴 - 圆锥
    const tailGeometry = new THREE.ConeGeometry(0.1, 1.0, 6);
    const tailMaterial = new THREE.MeshLambertMaterial({ color: 0xf5a623 });
    const tail = new THREE.Mesh(tailGeometry, tailMaterial);
    tail.position.set(0, 0.5, -1.2);
    tail.rotation.x = Math.PI / 4;
    tail.castShadow = true;
    group.add(tail);

    // 添加用户数据
    group.userData = {
      type: 'changlee_placeholder',
      animations: ['idle', 'happy', 'sleep', 'walk'],
      currentAnimation: 'idle',
      parts: {
        body,
        head,
        leftEye,
        rightEye,
        leftEar,
        rightEar,
        tail
      }
    };

    console.log('✅ 长离3D占位模型创建完成');
    return group;
  }

  /**
   * 创建立方体占位模型
   */
  _createCubePlaceholder3D(THREE, group) {
    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const material = new THREE.MeshLambertMaterial({ 
      color: 0x00ff00,
      transparent: true,
      opacity: 0.8
    });
    const cube = new THREE.Mesh(geometry, material);
    cube.castShadow = true;
    cube.receiveShadow = true;
    group.add(cube);

    group.userData = {
      type: 'cube_placeholder',
      animations: ['rotate'],
      currentAnimation: 'rotate'
    };

    return group;
  }

  /**
   * 创建球体占位模型
   */
  _createSpherePlaceholder3D(THREE, group) {
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshLambertMaterial({ 
      color: 0xff0000,
      transparent: true,
      opacity: 0.8
    });
    const sphere = new THREE.Mesh(geometry, material);
    sphere.castShadow = true;
    sphere.receiveShadow = true;
    group.add(sphere);

    group.userData = {
      type: 'sphere_placeholder',
      animations: ['bounce'],
      currentAnimation: 'bounce'
    };

    return group;
  }

  /**
   * 创建2D占位模型
   */
  create2DPlaceholder(type = 'changlee') {
    if (!window.PIXI) {
      throw new Error('PIXI.js 未加载');
    }

    const container = new window.PIXI.Container();

    switch (type) {
      case 'changlee':
        return this._createChangleePlaceholder2D(container);
      case 'circle':
        return this._createCirclePlaceholder2D(container);
      case 'square':
        return this._createSquarePlaceholder2D(container);
      default:
        return this._createChangleePlaceholder2D(container);
    }
  }

  /**
   * 创建长离风格的2D占位模型
   */
  _createChangleePlaceholder2D(container) {
    const graphics = new window.PIXI.Graphics();

    // 身体
    graphics.beginFill(0x4a90e2, 0.9);
    graphics.drawEllipse(0, 0, 80, 100);
    graphics.endFill();

    // 头部
    graphics.beginFill(0xf5a623, 0.9);
    graphics.drawCircle(0, -80, 60);
    graphics.endFill();

    // 眼睛
    graphics.beginFill(0x000000);
    graphics.drawCircle(-20, -90, 8);
    graphics.drawCircle(20, -90, 8);
    graphics.endFill();

    // 耳朵
    graphics.beginFill(0xf5a623);
    graphics.drawPolygon([-35, -120, -50, -160, -20, -160]);
    graphics.drawPolygon([35, -120, 50, -160, 20, -160]);
    graphics.endFill();

    // 尾巴
    graphics.beginFill(0xf5a623);
    graphics.drawEllipse(-90, 20, 15, 40);
    graphics.endFill();

    container.addChild(graphics);
    container.userData = {
      type: 'changlee_placeholder',
      animations: ['idle', 'happy', 'sleep', 'walk'],
      currentAnimation: 'idle'
    };

    console.log('✅ 长离2D占位模型创建完成');
    return container;
  }

  /**
   * 创建圆形占位模型
   */
  _createCirclePlaceholder2D(container) {
    const graphics = new window.PIXI.Graphics();
    graphics.beginFill(0xff0000, 0.8);
    graphics.drawCircle(0, 0, 50);
    graphics.endFill();

    container.addChild(graphics);
    container.userData = {
      type: 'circle_placeholder',
      animations: ['pulse'],
      currentAnimation: 'pulse'
    };

    return container;
  }

  /**
   * 创建方形占位模型
   */
  _createSquarePlaceholder2D(container) {
    const graphics = new window.PIXI.Graphics();
    graphics.beginFill(0x00ff00, 0.8);
    graphics.drawRect(-50, -50, 100, 100);
    graphics.endFill();

    container.addChild(graphics);
    container.userData = {
      type: 'square_placeholder',
      animations: ['rotate'],
      currentAnimation: 'rotate'
    };

    return container;
  }

  /**
   * 通用模型加载方法
   */
  async loadModel(modelPath, options = {}) {
    const { type = 'auto', cache = true } = options;
    
    try {
      let model;
      
      if (this.renderMode === '3D') {
        if (type === 'placeholder') {
          model = this.create3DPlaceholder(options.placeholderType);
        } else {
          model = await this.load3DModel(modelPath);
        }
      } else {
        if (type === 'placeholder') {
          model = this.create2DPlaceholder(options.placeholderType);
        } else {
          const modelType = type === 'auto' ? this._detectModelType(modelPath) : type;
          model = await this.load2DModel(modelPath, modelType);
        }
      }
      
      return model;
    } catch (error) {
      console.error('❌ 模型加载失败:', error);
      throw error;
    }
  }

  /**
   * 加载占位符模型
   */
  async loadPlaceholder(type = 'changlee') {
    if (this.renderMode === '3D') {
      return this.create3DPlaceholder(type);
    } else {
      return this.create2DPlaceholder(type);
    }
  }

  /**
   * 检测模型类型
   */
  _detectModelType(modelPath) {
    const ext = modelPath.split('.').pop().toLowerCase();
    
    switch (ext) {
      case 'gltf':
      case 'glb':
        return 'gltf';
      case 'json':
        return 'live2d';
      case 'skel':
        return 'spine';
      case 'png':
      case 'jpg':
      case 'jpeg':
        return 'sprite';
      default:
        return 'unknown';
    }
  }

  /**
   * 清理缓存
   */
  clearCache() {
    this.loadedModels.clear();
    this.loadingPromises.clear();
    console.log('🗑️ 模型缓存已清理');
  }

  /**
   * 获取缓存信息
   */
  getCacheInfo() {
    return {
      loadedCount: this.loadedModels.size,
      loadingCount: this.loadingPromises.size,
      models: Array.from(this.loadedModels.keys())
    };
  }

  /**
   * 切换渲染模式
   */
  switchRenderMode(newMode) {
    if (this.renderMode !== newMode) {
      console.log(`🔄 ModelLoader 切换渲染模式: ${this.renderMode} -> ${newMode}`);
      this.renderMode = newMode;
      // 清理不兼容的缓存
      this.clearCache();
    }
  }
}

export { ModelLoader };