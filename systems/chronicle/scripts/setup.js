#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

class ProjectSetup {
  constructor() {
    this.projectRoot = path.join(__dirname, '..');
    this.config = {};
  }

  async run() {
    console.log('🚀 Chronicle Setup\n');
    console.log('This script will help you set up Chronicle on your system.\n');

    try {
      await this.checkPrerequisites();
      await this.collectConfiguration();
      await this.createDirectories();
      await this.generateConfiguration();
      await this.installDependencies();
      await this.initializeDatabase();
      await this.createSystemdService();
      await this.showCompletionMessage();
    } catch (error) {
      console.error('❌ Setup failed:', error.message);
      process.exit(1);
    } finally {
      rl.close();
    }
  }

  async checkPrerequisites() {
    console.log('📋 Checking prerequisites...\n');

    // Check Node.js version
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    if (majorVersion < 16) {
      throw new Error(`Node.js 16+ is required. Current version: ${nodeVersion}`);
    }
    console.log(`✅ Node.js ${nodeVersion}`);

    // Check npm
    try {
      const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
      console.log(`✅ npm ${npmVersion}`);
    } catch (error) {
      throw new Error('npm is not installed or not in PATH');
    }

    // Check git (optional)
    try {
      const gitVersion = execSync('git --version', { encoding: 'utf8' }).trim();
      console.log(`✅ ${gitVersion}`);
    } catch (error) {
      console.log('⚠️  Git not found (optional)');
    }

    // Check platform-specific tools
    const platform = process.platform;
    console.log(`✅ Platform: ${platform}`);

    if (platform === 'linux') {
      // Check if systemd is available
      try {
        execSync('systemctl --version', { stdio: 'ignore' });
        console.log('✅ systemd available');
        this.config.hasSystemd = true;
      } catch (error) {
        console.log('⚠️  systemd not available');
        this.config.hasSystemd = false;
      }
    }

    console.log('\n✅ Prerequisites check completed\n');
  }

  async collectConfiguration() {
    console.log('⚙️  Configuration Setup\n');

    // Server configuration
    this.config.port = await this.prompt('Server port (3000): ') || '3000';
    this.config.host = await this.prompt('Server host (localhost): ') || 'localhost';

    // AI configuration
    const useAI = await this.prompt('Enable AI analysis? (y/N): ');
    if (useAI.toLowerCase() === 'y' || useAI.toLowerCase() === 'yes') {
      this.config.aiEnabled = true;
      this.config.aiProvider = await this.prompt('AI provider (gemini/openai) [gemini]: ') || 'gemini';
      this.config.aiApiKey = await this.prompt('AI API key: ');
      
      if (this.config.aiProvider === 'gemini') {
        this.config.aiModel = await this.prompt('Gemini model [gemini-pro]: ') || 'gemini-pro';
      } else {
        this.config.aiModel = await this.prompt('OpenAI model [gpt-3.5-turbo]: ') || 'gpt-3.5-turbo';
      }
    } else {
      this.config.aiEnabled = false;
    }

    // Security configuration
    const useApiKey = await this.prompt('Require API key authentication? (y/N): ');
    if (useApiKey.toLowerCase() === 'y' || useApiKey.toLowerCase() === 'yes') {
      this.config.apiKeyRequired = true;
      this.config.apiKey = await this.prompt('API key (leave empty to generate): ') || this.generateApiKey();
    } else {
      this.config.apiKeyRequired = false;
    }

    // Data directory
    this.config.dataDir = await this.prompt('Data directory [./data]: ') || './data';
    this.config.logDir = await this.prompt('Log directory [./logs]: ') || './logs';

    console.log('\n✅ Configuration collected\n');
  }

  async createDirectories() {
    console.log('📁 Creating directories...\n');

    const directories = [
      this.config.dataDir,
      this.config.logDir,
      path.join(this.config.dataDir, 'backups'),
      path.join(this.config.logDir, 'archive')
    ];

    for (const dir of directories) {
      const fullPath = path.resolve(this.projectRoot, dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
        console.log(`✅ Created: ${fullPath}`);
      } else {
        console.log(`✅ Exists: ${fullPath}`);
      }
    }

    console.log('\n✅ Directories created\n');
  }

  async generateConfiguration() {
    console.log('📝 Generating configuration files...\n');

    // Generate .env file
    const envContent = this.generateEnvFile();
    const envPath = path.join(this.projectRoot, '.env');
    fs.writeFileSync(envPath, envContent);
    console.log(`✅ Created: ${envPath}`);

    // Generate ecosystem.config.js for PM2
    const pm2Config = this.generatePM2Config();
    const pm2Path = path.join(this.projectRoot, 'ecosystem.config.js');
    fs.writeFileSync(pm2Path, pm2Config);
    console.log(`✅ Created: ${pm2Path}`);

    // Generate docker-compose.yml
    const dockerCompose = this.generateDockerCompose();
    const dockerPath = path.join(this.projectRoot, 'docker-compose.yml');
    fs.writeFileSync(dockerPath, dockerCompose);
    console.log(`✅ Created: ${dockerPath}`);

    console.log('\n✅ Configuration files generated\n');
  }

  async installDependencies() {
    console.log('📦 Installing dependencies...\n');

    try {
      console.log('Installing production dependencies...');
      execSync('npm install --production', { 
        cwd: this.projectRoot, 
        stdio: 'inherit' 
      });

      console.log('\nInstalling development dependencies...');
      execSync('npm install --only=dev', { 
        cwd: this.projectRoot, 
        stdio: 'inherit' 
      });

      console.log('\n✅ Dependencies installed\n');
    } catch (error) {
      throw new Error(`Failed to install dependencies: ${error.message}`);
    }
  }

  async initializeDatabase() {
    console.log('🗄️  Initializing database...\n');

    try {
      // Run database initialization
      const initScript = path.join(this.projectRoot, 'scripts', 'init-db.js');
      if (fs.existsSync(initScript)) {
        execSync(`node ${initScript}`, { 
          cwd: this.projectRoot, 
          stdio: 'inherit' 
        });
      } else {
        // Initialize database directly
        const database = require('../src/collector/database');
        await database.init();
        console.log('✅ Database initialized');
      }

      console.log('\n✅ Database setup completed\n');
    } catch (error) {
      console.warn(`⚠️  Database initialization warning: ${error.message}`);
    }
  }

  async createSystemdService() {
    if (!this.config.hasSystemd) {
      console.log('⏭️  Skipping systemd service (not available)\n');
      return;
    }

    const createService = await this.prompt('Create systemd service? (y/N): ');
    if (createService.toLowerCase() !== 'y' && createService.toLowerCase() !== 'yes') {
      console.log('⏭️  Skipping systemd service creation\n');
      return;
    }

    console.log('🔧 Creating systemd service...\n');

    const serviceContent = this.generateSystemdService();
    const servicePath = '/tmp/chronicle.service';
    
    fs.writeFileSync(servicePath, serviceContent);
    console.log(`✅ Service file created: ${servicePath}`);

    console.log('\nTo install the service, run as root:');
    console.log(`sudo cp ${servicePath} /etc/systemd/system/`);
    console.log('sudo systemctl daemon-reload');
    console.log('sudo systemctl enable chronicle');
    console.log('sudo systemctl start chronicle');

    console.log('\n✅ Systemd service prepared\n');
  }

  async showCompletionMessage() {
    console.log('🎉 Setup completed successfully!\n');

    console.log('📋 Next steps:\n');

    console.log('1. Start the service:');
    console.log('   npm start');
    console.log('   # or');
    console.log('   node src/daemon/service.js start');
    console.log('');

    console.log('2. Test the API:');
    console.log(`   curl http://${this.config.host}:${this.config.port}/health`);
    console.log('');

    console.log('3. Start a recording session:');
    const curlCommand = this.config.apiKeyRequired 
      ? `curl -X POST -H "Content-Type: application/json" -H "X-API-Key: ${this.config.apiKey}" -d '{"project_name": "test", "project_path": "/path/to/project"}' http://${this.config.host}:${this.config.port}/sessions/start`
      : `curl -X POST -H "Content-Type: application/json" -d '{"project_name": "test", "project_path": "/path/to/project"}' http://${this.config.host}:${this.config.port}/sessions/start`;
    console.log(`   ${curlCommand}`);
    console.log('');

    console.log('4. View logs:');
    console.log(`   tail -f ${path.resolve(this.config.logDir, 'chronicle.log')}`);
    console.log('');

    if (this.config.hasSystemd) {
      console.log('5. Install as system service (optional):');
      console.log('   sudo cp /tmp/chronicle.service /etc/systemd/system/');
      console.log('   sudo systemctl daemon-reload');
      console.log('   sudo systemctl enable chronicle');
      console.log('   sudo systemctl start chronicle');
      console.log('');
    }

    console.log('📚 Documentation: https://github.com/your-org/chronicle');
    console.log('🐛 Issues: https://github.com/your-org/chronicle/issues');
    console.log('');
    console.log('Happy experimenting! 🔬✨');
  }

  generateEnvFile() {
    return `# Chronicle Configuration
# Generated on ${new Date().toISOString()}

# Server Configuration
PORT=${this.config.port}
HOST=${this.config.host}
NODE_ENV=production

# Database Configuration
DB_PATH=${path.resolve(this.config.dataDir, 'chronicle.db')}

# AI Configuration
AI_PROVIDER=${this.config.aiProvider || 'gemini'}
AI_MODEL=${this.config.aiModel || 'gemini-pro'}
${this.config.aiApiKey ? `AI_API_KEY=${this.config.aiApiKey}` : '# AI_API_KEY=your_api_key_here'}

# Security Configuration
API_KEY_REQUIRED=${this.config.apiKeyRequired || false}
${this.config.apiKey ? `API_KEY=${this.config.apiKey}` : '# API_KEY=your_api_key_here'}
ENABLE_CORS=true
CORS_ORIGINS=*

# Logging Configuration
LOG_LEVEL=info
LOG_FILE=${path.resolve(this.config.logDir, 'chronicle.log')}

# Monitoring Configuration
FS_MONITOR_ENABLED=true
WINDOW_MONITOR_ENABLED=true
CMD_MONITOR_ENABLED=true

# Performance Configuration
ENABLE_COMPRESSION=true
MAX_REQUEST_SIZE=10mb
REQUEST_TIMEOUT=30000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=900000
`;
  }

  generatePM2Config() {
    return `module.exports = {
  apps: [{
    name: 'chronicle',
    script: 'src/api/server.js',
    cwd: '${this.projectRoot}',
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: ${this.config.port}
    },
    log_file: '${path.resolve(this.config.logDir, 'pm2.log')}',
    out_file: '${path.resolve(this.config.logDir, 'pm2-out.log')}',
    error_file: '${path.resolve(this.config.logDir, 'pm2-error.log')}',
    time: true,
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
`;
  }

  generateDockerCompose() {
    return `version: '3.8'

services:
  chronicle:
    build: .
    container_name: chronicle
    restart: unless-stopped
    ports:
      - "${this.config.port}:${this.config.port}"
    environment:
      - NODE_ENV=production
      - PORT=${this.config.port}
      - HOST=0.0.0.0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - chronicle-network

networks:
  chronicle-network:
    driver: bridge
`;
  }

  generateSystemdService() {
    const user = process.env.USER || 'chronicle';
    const group = process.env.USER || 'chronicle';

    return `[Unit]
Description=Chronicle - AI-Driven Automated Experiment Recorder
Documentation=https://github.com/your-org/chronicle
After=network.target

[Service]
Type=simple
User=${user}
Group=${group}
WorkingDirectory=${this.projectRoot}
ExecStart=${process.execPath} src/daemon/service.js start --no-daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=chronicle

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${this.projectRoot}

# Environment
Environment=NODE_ENV=production
EnvironmentFile=${this.projectRoot}/.env

[Install]
WantedBy=multi-user.target
`;
  }

  generateApiKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 32; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  prompt(question) {
    return new Promise((resolve) => {
      rl.question(question, resolve);
    });
  }
}

// Run setup if called directly
if (require.main === module) {
  const setup = new ProjectSetup();
  setup.run().catch(error => {
    console.error('Setup failed:', error);
    process.exit(1);
  });
}

module.exports = ProjectSetup;