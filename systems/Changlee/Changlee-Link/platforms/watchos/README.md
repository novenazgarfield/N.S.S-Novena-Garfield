# Changlee-Link Apple Watch 实现

## 🍎 项目概览

Apple Watch 版本的 Changlee-Link，使用 Swift 和 SwiftUI 构建，为 NEXUS 系统提供原生的 watchOS 体验。

## 🎯 技术栈

- **开发语言**: Swift 5.9+
- **UI 框架**: SwiftUI 4.0+
- **最低版本**: watchOS 9.0
- **目标设备**: Apple Watch Series 4 及更新型号
- **开发工具**: Xcode 15.0+

## 📱 支持的设备

| 设备型号 | 屏幕尺寸 | 分辨率 | 支持状态 |
|---------|---------|--------|---------|
| Apple Watch Series 4 | 40mm/44mm | 324×394 / 368×448 | ✅ 完全支持 |
| Apple Watch Series 5 | 40mm/44mm | 324×394 / 368×448 | ✅ 完全支持 |
| Apple Watch Series 6 | 40mm/44mm | 324×394 / 368×448 | ✅ 完全支持 |
| Apple Watch Series 7 | 41mm/45mm | 352×430 / 396×484 | ✅ 完全支持 |
| Apple Watch Series 8 | 41mm/45mm | 352×430 / 396×484 | ✅ 完全支持 |
| Apple Watch Series 9 | 41mm/45mm | 352×430 / 396×484 | ✅ 完全支持 |
| Apple Watch Ultra | 49mm | 410×502 | ✅ 完全支持 |
| Apple Watch Ultra 2 | 49mm | 410×502 | ✅ 完全支持 |

## 🏗️ 项目结构

```
watchos/
├── ChangleeLink.xcodeproj           # Xcode 项目文件
├── ChangleeLink WatchKit App/       # Watch App 目标
│   ├── ContentView.swift           # 主界面
│   ├── Views/                      # 视图组件
│   │   ├── DashboardView.swift     # 仪表板视图
│   │   ├── SystemStatusView.swift  # 系统状态视图
│   │   ├── QuickActionsView.swift  # 快速操作视图
│   │   ├── HealthMonitorView.swift # 健康监测视图
│   │   └── NotificationView.swift  # 通知视图
│   ├── Models/                     # 数据模型
│   │   ├── SystemModel.swift       # 系统模型
│   │   ├── HealthModel.swift       # 健康数据模型
│   │   └── NotificationModel.swift # 通知模型
│   ├── Services/                   # 服务层
│   │   ├── WatchConnectivityService.swift # 连接服务
│   │   ├── HealthKitService.swift  # 健康数据服务
│   │   └── NotificationService.swift # 通知服务
│   ├── Utils/                      # 工具类
│   │   ├── HapticManager.swift     # 触觉反馈管理
│   │   ├── ThemeManager.swift      # 主题管理
│   │   └── Extensions.swift        # 扩展方法
│   └── Assets.xcassets             # 资源文件
├── ChangleeLink WatchKit Extension/ # Watch Extension 目标
│   ├── ExtensionDelegate.swift     # 扩展委托
│   ├── ComplicationController.swift # 复杂功能控制器
│   └── IntentHandler.swift         # Siri 意图处理
├── ChangleeLink iOS/               # iOS 伴侣应用
│   ├── ContentView.swift           # iOS 主界面
│   ├── Services/                   # iOS 服务
│   │   ├── NEXUSAPIService.swift   # NEXUS API 服务
│   │   ├── WatchConnectivityManager.swift # Watch 连接管理
│   │   └── BackgroundTaskManager.swift # 后台任务管理
│   └── Models/                     # 共享数据模型
└── Shared/                         # 共享代码
    ├── NEXUSProtocol.swift         # NEXUS 协议定义
    ├── DataModels.swift            # 数据模型
    └── Constants.swift             # 常量定义
```

## 🔧 核心功能实现

### 1. WatchConnectivity 通信

```swift
import WatchConnectivity

class WatchConnectivityService: NSObject, ObservableObject {
    private let session = WCSession.default
    @Published var isConnected = false
    @Published var systemStatus: [SystemInfo] = []
    
    override init() {
        super.init()
        if WCSession.isSupported() {
            session.delegate = self
            session.activate()
        }
    }
    
    // 发送命令到 iPhone
    func sendCommand(_ command: CommandRequest) {
        guard session.isReachable else { return }
        
        let message: [String: Any] = [
            "type": "command",
            "payload": command.toDictionary(),
            "timestamp": Date().timeIntervalSince1970
        ]
        
        session.sendMessage(message, replyHandler: { reply in
            DispatchQueue.main.async {
                self.handleCommandResponse(reply)
            }
        }) { error in
            print("发送命令失败: \(error.localizedDescription)")
        }
    }
    
    // 更新应用上下文
    func updateContext(_ context: [String: Any]) {
        do {
            try session.updateApplicationContext(context)
        } catch {
            print("更新上下文失败: \(error.localizedDescription)")
        }
    }
}

extension WatchConnectivityService: WCSessionDelegate {
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        DispatchQueue.main.async {
            self.isConnected = activationState == .activated
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        DispatchQueue.main.async {
            self.handleReceivedMessage(message)
        }
    }
    
    func session(_ session: WCSession, didReceiveApplicationContext applicationContext: [String : Any]) {
        DispatchQueue.main.async {
            self.handleContextUpdate(applicationContext)
        }
    }
}
```

### 2. SwiftUI 主界面

```swift
import SwiftUI

struct ContentView: View {
    @StateObject private var connectivityService = WatchConnectivityService()
    @StateObject private var healthService = HealthKitService()
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tag(0)
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("主页")
                }
            
            SystemStatusView(systems: connectivityService.systemStatus)
                .tag(1)
                .tabItem {
                    Image(systemName: "server.rack")
                    Text("系统")
                }
            
            QuickActionsView(connectivityService: connectivityService)
                .tag(2)
                .tabItem {
                    Image(systemName: "bolt.fill")
                    Text("操作")
                }
            
            HealthMonitorView(healthService: healthService)
                .tag(3)
                .tabItem {
                    Image(systemName: "heart.fill")
                    Text("健康")
                }
        }
        .environmentObject(connectivityService)
        .environmentObject(healthService)
        .onAppear {
            requestHealthPermissions()
        }
    }
    
    private func requestHealthPermissions() {
        healthService.requestAuthorization()
    }
}
```

### 3. 系统状态视图

```swift
import SwiftUI

struct SystemStatusView: View {
    let systems: [SystemInfo]
    @EnvironmentObject var connectivityService: WatchConnectivityService
    
    var body: some View {
        NavigationView {
            List {
                // 状态摘要
                Section("系统概览") {
                    StatusSummaryCard(systems: systems)
                }
                
                // 在线系统
                if !onlineSystems.isEmpty {
                    Section("在线系统") {
                        ForEach(onlineSystems, id: \.id) { system in
                            SystemRowView(system: system)
                                .onTapGesture {
                                    showSystemDetails(system)
                                }
                        }
                    }
                }
                
                // 离线系统
                if !offlineSystems.isEmpty {
                    Section("离线系统") {
                        ForEach(offlineSystems, id: \.id) { system in
                            SystemRowView(system: system)
                                .opacity(0.6)
                        }
                    }
                }
                
                // 受限系统
                if !restrictedSystems.isEmpty {
                    Section("受限系统") {
                        ForEach(restrictedSystems, id: \.id) { system in
                            SystemRowView(system: system)
                                .overlay(
                                    Image(systemName: "lock.fill")
                                        .foregroundColor(.orange)
                                        .font(.caption),
                                    alignment: .topTrailing
                                )
                        }
                    }
                }
            }
            .navigationTitle("系统状态")
            .refreshable {
                refreshSystemStatus()
            }
        }
    }
    
    private var onlineSystems: [SystemInfo] {
        systems.filter { $0.status == .online }
    }
    
    private var offlineSystems: [SystemInfo] {
        systems.filter { $0.status == .offline }
    }
    
    private var restrictedSystems: [SystemInfo] {
        systems.filter { $0.status == .restricted }
    }
    
    private func showSystemDetails(_ system: SystemInfo) {
        // 显示系统详情
        HapticManager.shared.playSuccess()
    }
    
    private func refreshSystemStatus() {
        connectivityService.sendCommand(
            CommandRequest(
                systemId: "nexus_core",
                command: "get_systems_status"
            )
        )
    }
}
```

### 4. 快速操作视图

```swift
import SwiftUI

struct QuickActionsView: View {
    @ObservedObject var connectivityService: WatchConnectivityService
    @State private var showingActionSheet = false
    @State private var selectedAction: QuickAction?
    
    let quickActions: [QuickAction] = [
        QuickAction(id: "remote_control", title: "远程控制", icon: "antenna.radiowaves.left.and.right", color: .blue),
        QuickAction(id: "rag_query", title: "AI问答", icon: "brain.head.profile", color: .purple),
        QuickAction(id: "wake_changlee", title: "唤醒长离", icon: "cat.fill", color: .orange),
        QuickAction(id: "system_logs", title: "查看日志", icon: "doc.text", color: .green),
        QuickAction(id: "health_sync", title: "同步健康", icon: "heart.fill", color: .red),
        QuickAction(id: "emergency_stop", title: "紧急停止", icon: "stop.circle.fill", color: .red)
    ]
    
    var body: some View {
        NavigationView {
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                ForEach(quickActions, id: \.id) { action in
                    QuickActionButton(action: action) {
                        executeAction(action)
                    }
                }
            }
            .padding()
            .navigationTitle("快速操作")
        }
        .confirmationDialog(
            selectedAction?.title ?? "",
            isPresented: $showingActionSheet,
            titleVisibility: .visible
        ) {
            Button("确认执行") {
                if let action = selectedAction {
                    performAction(action)
                }
            }
            Button("取消", role: .cancel) { }
        } message: {
            Text("确定要执行 \(selectedAction?.title ?? "") 操作吗？")
        }
    }
    
    private func executeAction(_ action: QuickAction) {
        if action.id == "emergency_stop" {
            selectedAction = action
            showingActionSheet = true
        } else {
            performAction(action)
        }
    }
    
    private func performAction(_ action: QuickAction) {
        HapticManager.shared.playImpact()
        
        let command = CommandRequest(
            systemId: getSystemId(for: action.id),
            command: getCommand(for: action.id),
            parameters: getParameters(for: action.id)
        )
        
        connectivityService.sendCommand(command)
    }
    
    private func getSystemId(for actionId: String) -> String {
        switch actionId {
        case "remote_control": return "nexus_remote"
        case "rag_query": return "rag_system"
        case "wake_changlee": return "changlee"
        case "system_logs": return "nexus_core"
        case "health_sync": return "nexus_core"
        case "emergency_stop": return "nexus_core"
        default: return "nexus_core"
        }
    }
    
    private func getCommand(for actionId: String) -> String {
        switch actionId {
        case "remote_control": return "open_control_panel"
        case "rag_query": return "start_conversation"
        case "wake_changlee": return "wake_pet"
        case "system_logs": return "get_recent_logs"
        case "health_sync": return "sync_health_data"
        case "emergency_stop": return "emergency_shutdown"
        default: return "ping"
        }
    }
    
    private func getParameters(for actionId: String) -> [String: Any]? {
        switch actionId {
        case "health_sync":
            return ["include_heart_rate": true, "include_activity": true]
        case "emergency_stop":
            return ["confirm": true, "reason": "watch_emergency_button"]
        default:
            return nil
        }
    }
}

struct QuickActionButton: View {
    let action: QuickAction
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 8) {
                Image(systemName: action.icon)
                    .font(.title2)
                    .foregroundColor(.white)
                
                Text(action.title)
                    .font(.caption)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity, minHeight: 80)
            .background(action.color)
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}
```

### 5. 健康监测服务

```swift
import HealthKit

class HealthKitService: NSObject, ObservableObject {
    private let healthStore = HKHealthStore()
    
    @Published var heartRate: Double = 0
    @Published var bloodOxygen: Double = 0
    @Published var stressLevel: Double = 0
    @Published var activityLevel: String = "unknown"
    
    private let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
    private let bloodOxygenType = HKQuantityType.quantityType(forIdentifier: .oxygenSaturation)!
    
    func requestAuthorization() {
        let typesToRead: Set<HKObjectType> = [
            heartRateType,
            bloodOxygenType,
            HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!,
            HKObjectType.activitySummaryType()
        ]
        
        healthStore.requestAuthorization(toShare: nil, read: typesToRead) { success, error in
            if success {
                self.startHealthMonitoring()
            }
        }
    }
    
    private func startHealthMonitoring() {
        startHeartRateMonitoring()
        startBloodOxygenMonitoring()
        startActivityMonitoring()
    }
    
    private func startHeartRateMonitoring() {
        let query = HKAnchoredObjectQuery(
            type: heartRateType,
            predicate: nil,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { query, samples, deletedObjects, anchor, error in
            guard let samples = samples as? [HKQuantitySample] else { return }
            
            DispatchQueue.main.async {
                if let latestSample = samples.last {
                    self.heartRate = latestSample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
                }
            }
        }
        
        query.updateHandler = { query, samples, deletedObjects, anchor, error in
            guard let samples = samples as? [HKQuantitySample] else { return }
            
            DispatchQueue.main.async {
                if let latestSample = samples.last {
                    self.heartRate = latestSample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
                    self.uploadHealthData()
                }
            }
        }
        
        healthStore.execute(query)
    }
    
    private func uploadHealthData() {
        let healthData = HealthDataPayload(
            userId: "current_user",
            deviceId: WKInterfaceDevice.current().name,
            metrics: [
                HealthMetric(
                    type: .heartRate,
                    value: heartRate,
                    unit: "bpm",
                    timestamp: Date().timeIntervalSince1970
                ),
                HealthMetric(
                    type: .bloodOxygen,
                    value: bloodOxygen,
                    unit: "%",
                    timestamp: Date().timeIntervalSince1970
                )
            ]
        )
        
        // 通过 WatchConnectivity 发送到 iPhone
        NotificationCenter.default.post(
            name: .healthDataUpdated,
            object: healthData
        )
    }
}
```

## 🔧 构建和部署

### 开发环境要求

```bash
# 检查 Xcode 版本
xcodebuild -version
# Xcode 15.0 或更高版本

# 检查 Swift 版本
swift --version
# Swift 5.9 或更高版本
```

### 构建步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Changlee-Link/platforms/watchos
```

2. **打开 Xcode 项目**
```bash
open ChangleeLink.xcodeproj
```

3. **配置开发者账号**
   - 在 Xcode 中选择项目
   - 在 "Signing & Capabilities" 中配置开发者账号
   - 确保 Watch App 和 iOS App 都正确配置

4. **构建项目**
   - 选择目标设备或模拟器
   - 按 Cmd+B 构建项目
   - 按 Cmd+R 运行项目

### 发布配置

```swift
// Release 配置
#if DEBUG
let apiBaseURL = "https://nexus-dev.example.com"
let logLevel = "debug"
#else
let apiBaseURL = "https://nexus.example.com"
let logLevel = "error"
#endif
```

## 🧪 测试

### 单元测试

```swift
import XCTest
@testable import ChangleeLink_WatchKit_Extension

class WatchConnectivityServiceTests: XCTestCase {
    var service: WatchConnectivityService!
    
    override func setUp() {
        super.setUp()
        service = WatchConnectivityService()
    }
    
    func testCommandSending() {
        let command = CommandRequest(
            systemId: "test_system",
            command: "test_command"
        )
        
        // 测试命令发送逻辑
        XCTAssertNoThrow(service.sendCommand(command))
    }
    
    func testHealthDataProcessing() {
        let healthData = HealthDataPayload(
            userId: "test_user",
            deviceId: "test_device",
            metrics: []
        )
        
        // 测试健康数据处理
        XCTAssertNotNil(healthData)
    }
}
```

### UI 测试

```swift
import XCTest

class ChangleeLinkUITests: XCTestCase {
    func testMainInterface() {
        let app = XCUIApplication()
        app.launch()
        
        // 测试主界面元素
        XCTAssertTrue(app.tabBars.buttons["主页"].exists)
        XCTAssertTrue(app.tabBars.buttons["系统"].exists)
        XCTAssertTrue(app.tabBars.buttons["操作"].exists)
        XCTAssertTrue(app.tabBars.buttons["健康"].exists)
    }
    
    func testQuickActions() {
        let app = XCUIApplication()
        app.launch()
        
        app.tabBars.buttons["操作"].tap()
        
        // 测试快速操作按钮
        XCTAssertTrue(app.buttons["远程控制"].exists)
        XCTAssertTrue(app.buttons["AI问答"].exists)
        XCTAssertTrue(app.buttons["唤醒长离"].exists)
    }
}
```

## 📊 性能优化

### 电池优化

```swift
// 智能更新频率
class BatteryOptimizer {
    static func getOptimalUpdateInterval() -> TimeInterval {
        let batteryLevel = WKInterfaceDevice.current().batteryLevel
        
        switch batteryLevel {
        case 0.8...1.0: return 5.0    // 高电量：5秒更新
        case 0.5...0.8: return 10.0   // 中电量：10秒更新
        case 0.2...0.5: return 30.0   // 低电量：30秒更新
        default: return 60.0          // 极低电量：1分钟更新
        }
    }
}
```

### 内存优化

```swift
// 图片缓存管理
class ImageCache {
    private let cache = NSCache<NSString, UIImage>()
    
    init() {
        cache.countLimit = 20  // 限制缓存数量
        cache.totalCostLimit = 10 * 1024 * 1024  // 限制缓存大小 10MB
    }
    
    func setImage(_ image: UIImage, forKey key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
    
    func image(forKey key: String) -> UIImage? {
        return cache.object(forKey: key as NSString)
    }
}
```

## 🔐 安全考虑

### 数据加密

```swift
import CryptoKit

class SecurityManager {
    private let key = SymmetricKey(size: .bits256)
    
    func encrypt(_ data: Data) throws -> Data {
        let sealedBox = try AES.GCM.seal(data, using: key)
        return sealedBox.combined!
    }
    
    func decrypt(_ encryptedData: Data) throws -> Data {
        let sealedBox = try AES.GCM.SealedBox(combined: encryptedData)
        return try AES.GCM.open(sealedBox, using: key)
    }
}
```

### 生物识别认证

```swift
import LocalAuthentication

class BiometricAuth {
    func authenticate() async -> Bool {
        let context = LAContext()
        var error: NSError?
        
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return false
        }
        
        do {
            let result = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: "验证身份以访问 NEXUS 系统"
            )
            return result
        } catch {
            return false
        }
    }
}
```

---

**开发状态**: 🚧 开发中  
**最后更新**: 2025-08-20  
**Swift 版本**: 5.9+  
**最低 watchOS**: 9.0