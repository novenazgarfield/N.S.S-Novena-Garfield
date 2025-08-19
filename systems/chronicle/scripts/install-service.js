#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

class ServiceInstaller {
  constructor() {
    this.projectRoot = path.join(__dirname, '..');
    this.platform = process.platform;
    this.isRoot = process.getuid && process.getuid() === 0;
  }

  async install() {
    console.log('🔧 Installing Chronicle as a system service...\n');

    try {
      await this.checkPermissions();
      await this.detectServiceManager();
      await this.installService();
      await this.showInstructions();
    } catch (error) {
      console.error('❌ Service installation failed:', error.message);
      process.exit(1);
    }
  }

  async checkPermissions() {
    if (this.platform !== 'linux' && this.platform !== 'darwin') {
      throw new Error(`Service installation is not supported on ${this.platform}`);
    }

    if (!this.isRoot) {
      throw new Error('Service installation requires root privileges. Please run with sudo.');
    }

    console.log('✅ Running with root privileges');
  }

  async detectServiceManager() {
    console.log('🔍 Detecting service manager...\n');

    // Check for systemd
    try {
      execSync('systemctl --version', { stdio: 'ignore' });
      this.serviceManager = 'systemd';
      console.log('✅ Detected: systemd');
      return;
    } catch (error) {
      // systemd not available
    }

    // Check for launchd (macOS)
    if (this.platform === 'darwin') {
      this.serviceManager = 'launchd';
      console.log('✅ Detected: launchd');
      return;
    }

    // Check for init.d
    if (fs.existsSync('/etc/init.d')) {
      this.serviceManager = 'initd';
      console.log('✅ Detected: init.d');
      return;
    }

    throw new Error('No supported service manager found');
  }

  async installService() {
    console.log(`\n🚀 Installing service using ${this.serviceManager}...\n`);

    switch (this.serviceManager) {
      case 'systemd':
        await this.installSystemdService();
        break;
      case 'launchd':
        await this.installLaunchdService();
        break;
      case 'initd':
        await this.installInitdService();
        break;
      default:
        throw new Error(`Unsupported service manager: ${this.serviceManager}`);
    }
  }

  async installSystemdService() {
    const serviceContent = this.generateSystemdService();
    const servicePath = '/etc/systemd/system/chronicle.service';

    // Write service file
    fs.writeFileSync(servicePath, serviceContent);
    console.log(`✅ Created service file: ${servicePath}`);

    // Reload systemd
    execSync('systemctl daemon-reload');
    console.log('✅ Reloaded systemd daemon');

    // Enable service
    execSync('systemctl enable chronicle');
    console.log('✅ Enabled chronicle service');

    this.serviceCommands = {
      start: 'sudo systemctl start chronicle',
      stop: 'sudo systemctl stop chronicle',
      restart: 'sudo systemctl restart chronicle',
      status: 'sudo systemctl status chronicle',
      logs: 'sudo journalctl -u chronicle -f'
    };
  }

  async installLaunchdService() {
    const plistContent = this.generateLaunchdPlist();
    const plistPath = '/Library/LaunchDaemons/com.projectchronicle.daemon.plist';

    // Write plist file
    fs.writeFileSync(plistPath, plistContent);
    console.log(`✅ Created plist file: ${plistPath}`);

    // Set permissions
    execSync(`chown root:wheel ${plistPath}`);
    execSync(`chmod 644 ${plistPath}`);
    console.log('✅ Set plist permissions');

    // Load service
    execSync(`launchctl load ${plistPath}`);
    console.log('✅ Loaded chronicle service');

    this.serviceCommands = {
      start: `sudo launchctl load ${plistPath}`,
      stop: `sudo launchctl unload ${plistPath}`,
      restart: `sudo launchctl unload ${plistPath} && sudo launchctl load ${plistPath}`,
      status: 'sudo launchctl list | grep projectchronicle',
      logs: 'tail -f /var/log/chronicle.log'
    };
  }

  async installInitdService() {
    const scriptContent = this.generateInitdScript();
    const scriptPath = '/etc/init.d/chronicle';

    // Write init script
    fs.writeFileSync(scriptPath, scriptContent);
    console.log(`✅ Created init script: ${scriptPath}`);

    // Set permissions
    execSync(`chmod +x ${scriptPath}`);
    console.log('✅ Set script permissions');

    // Enable service
    try {
      execSync('update-rc.d chronicle defaults');
      console.log('✅ Enabled chronicle service');
    } catch (error) {
      // Try chkconfig for RHEL-based systems
      try {
        execSync('chkconfig --add chronicle');
        execSync('chkconfig chronicle on');
        console.log('✅ Enabled chronicle service (chkconfig)');
      } catch (chkError) {
        console.warn('⚠️  Could not enable service automatically');
      }
    }

    this.serviceCommands = {
      start: 'sudo service chronicle start',
      stop: 'sudo service chronicle stop',
      restart: 'sudo service chronicle restart',
      status: 'sudo service chronicle status',
      logs: `tail -f ${path.resolve(this.projectRoot, 'logs/chronicle.log')}`
    };
  }

  generateSystemdService() {
    const user = this.getServiceUser();
    const group = this.getServiceGroup();

    return `[Unit]
Description=Chronicle - AI-Driven Automated Experiment Recorder
Documentation=https://github.com/your-org/chronicle
After=network.target
Wants=network.target

[Service]
Type=simple
User=${user}
Group=${group}
WorkingDirectory=${this.projectRoot}
ExecStart=${process.execPath} ${path.join(this.projectRoot, 'src/daemon/service.js')} start --no-daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# Output to journald
StandardOutput=journal
StandardError=journal
SyslogIdentifier=chronicle

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${this.projectRoot}
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

# Environment
Environment=NODE_ENV=production
EnvironmentFile=-${this.projectRoot}/.env

[Install]
WantedBy=multi-user.target
`;
  }

  generateLaunchdPlist() {
    const user = this.getServiceUser();

    return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.projectchronicle.daemon</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${process.execPath}</string>
        <string>${path.join(this.projectRoot, 'src/daemon/service.js')}</string>
        <string>start</string>
        <string>--no-daemon</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${this.projectRoot}</string>
    
    <key>UserName</key>
    <string>${user}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/var/log/chronicle.log</string>
    
    <key>StandardErrorPath</key>
    <string>/var/log/chronicle-error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>NODE_ENV</key>
        <string>production</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
`;
  }

  generateInitdScript() {
    const user = this.getServiceUser();
    const pidFile = path.join(this.projectRoot, 'data/chronicle.pid');
    const logFile = path.join(this.projectRoot, 'logs/chronicle.log');

    return `#!/bin/bash
#
# chronicle    Chronicle daemon
#
# chkconfig: 35 80 20
# description: AI-Driven Automated Experiment Recorder
#

. /etc/rc.d/init.d/functions

USER="${user}"
DAEMON="chronicle"
ROOT_DIR="${this.projectRoot}"

SERVER="$ROOT_DIR/src/daemon/service.js"
LOCK_FILE="/var/lock/subsys/chronicle"
PID_FILE="${pidFile}"
LOG_FILE="${logFile}"

start() {
    if [ -f "$PID_FILE" ] && kill -0 \`cat "$PID_FILE"\`; then
        echo 'Service already running' >&2
        return 1
    fi
    echo 'Starting service…' >&2
    local CMD="$SERVER start --no-daemon &> \\"$LOG_FILE\\" & echo \\$!"
    su -c "$CMD" $USER > "$PID_FILE"
    echo 'Service started' >&2
    touch "$LOCK_FILE"
}

stop() {
    if [ ! -f "$PID_FILE" ] || ! kill -0 \`cat "$PID_FILE"\`; then
        echo 'Service not running' >&2
        return 1
    fi
    echo 'Stopping service…' >&2
    kill -15 \`cat "$PID_FILE"\` && rm -f "$PID_FILE"
    echo 'Service stopped' >&2
    rm -f "$LOCK_FILE"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 \`cat "$PID_FILE"\`; then
        echo "Service running (PID: \`cat $PID_FILE\`)"
    else
        echo 'Service not running'
        return 1
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: {start|stop|status|restart}"
        exit 1
        ;;
esac

exit $?
`;
  }

  getServiceUser() {
    // Try to find a suitable non-root user
    const possibleUsers = ['chronicle', 'nodejs', 'www-data', 'nobody'];
    
    for (const user of possibleUsers) {
      try {
        execSync(`id ${user}`, { stdio: 'ignore' });
        return user;
      } catch (error) {
        // User doesn't exist
      }
    }

    // Create chronicle user if none found
    try {
      execSync('useradd -r -s /bin/false -d /nonexistent chronicle', { stdio: 'ignore' });
      console.log('✅ Created chronicle user');
      return 'chronicle';
    } catch (error) {
      console.warn('⚠️  Could not create service user, using root');
      return 'root';
    }
  }

  getServiceGroup() {
    const user = this.getServiceUser();
    
    try {
      const result = execSync(`id -gn ${user}`, { encoding: 'utf8' }).trim();
      return result;
    } catch (error) {
      return user;
    }
  }

  async showInstructions() {
    console.log('\n🎉 Service installation completed!\n');

    console.log('📋 Service Management Commands:\n');
    console.log(`Start:   ${this.serviceCommands.start}`);
    console.log(`Stop:    ${this.serviceCommands.stop}`);
    console.log(`Restart: ${this.serviceCommands.restart}`);
    console.log(`Status:  ${this.serviceCommands.status}`);
    console.log(`Logs:    ${this.serviceCommands.logs}`);

    console.log('\n🚀 To start the service now:');
    console.log(`${this.serviceCommands.start}`);

    console.log('\n📊 To check service status:');
    console.log(`${this.serviceCommands.status}`);

    console.log('\n📝 Configuration:');
    console.log(`Edit: ${path.join(this.projectRoot, '.env')}`);
    console.log('After editing config, restart the service.');

    console.log('\n🔧 Troubleshooting:');
    console.log('- Check logs for errors');
    console.log('- Verify configuration file');
    console.log('- Ensure proper file permissions');
    console.log('- Check network connectivity for AI features');

    console.log('\n✅ Installation complete!');
  }

  async uninstall() {
    console.log('🗑️  Uninstalling Chronicle service...\n');

    try {
      await this.checkPermissions();
      await this.detectServiceManager();
      await this.uninstallService();
      console.log('\n✅ Service uninstalled successfully!');
    } catch (error) {
      console.error('❌ Service uninstallation failed:', error.message);
      process.exit(1);
    }
  }

  async uninstallService() {
    switch (this.serviceManager) {
      case 'systemd':
        try {
          execSync('systemctl stop chronicle', { stdio: 'ignore' });
          execSync('systemctl disable chronicle', { stdio: 'ignore' });
          fs.unlinkSync('/etc/systemd/system/chronicle.service');
          execSync('systemctl daemon-reload');
          console.log('✅ Systemd service removed');
        } catch (error) {
          console.warn('⚠️  Some cleanup steps failed:', error.message);
        }
        break;

      case 'launchd':
        try {
          const plistPath = '/Library/LaunchDaemons/com.projectchronicle.daemon.plist';
          execSync(`launchctl unload ${plistPath}`, { stdio: 'ignore' });
          fs.unlinkSync(plistPath);
          console.log('✅ Launchd service removed');
        } catch (error) {
          console.warn('⚠️  Some cleanup steps failed:', error.message);
        }
        break;

      case 'initd':
        try {
          execSync('service chronicle stop', { stdio: 'ignore' });
          execSync('update-rc.d -f chronicle remove', { stdio: 'ignore' });
          fs.unlinkSync('/etc/init.d/chronicle');
          console.log('✅ Init.d service removed');
        } catch (error) {
          try {
            execSync('chkconfig chronicle off', { stdio: 'ignore' });
            execSync('chkconfig --del chronicle', { stdio: 'ignore' });
          } catch (chkError) {
            // Ignore
          }
          console.warn('⚠️  Some cleanup steps failed:', error.message);
        }
        break;
    }
  }
}

// Command line interface
function main() {
  const installer = new ServiceInstaller();
  const command = process.argv[2];

  switch (command) {
    case 'install':
      installer.install();
      break;
    case 'uninstall':
      installer.uninstall();
      break;
    default:
      console.log(`
Chronicle Service Installer

Usage: sudo node install-service.js <command>

Commands:
  install     Install Chronicle as a system service
  uninstall   Remove the system service

Examples:
  sudo node install-service.js install
  sudo node install-service.js uninstall

Note: This script requires root privileges.
      `);
      process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = ServiceInstaller;