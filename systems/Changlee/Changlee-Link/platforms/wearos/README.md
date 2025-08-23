# Changlee-Link Wear OS 实现

## 🤖 项目概览

Wear OS 版本的 Changlee-Link，使用 Kotlin 和 Jetpack Compose for Wear OS 构建，为 NEXUS 系统提供现代化的 Android 穿戴设备体验。

## 🎯 技术栈

- **开发语言**: Kotlin 1.9+
- **UI 框架**: Jetpack Compose for Wear OS 1.2+
- **最低版本**: Wear OS 3.0 (API 30)
- **目标设备**: 运行 Wear OS 3+ 的智能手表
- **开发工具**: Android Studio Hedgehog 2023.1.1+

## 📱 支持的设备

| 设备品牌 | 设备型号 | 屏幕形状 | 分辨率 | 支持状态 |
|---------|---------|---------|--------|---------|
| **Samsung** | Galaxy Watch 4 | 圆形 | 450×450 | ✅ 完全支持 |
| **Samsung** | Galaxy Watch 5 | 圆形 | 450×450 | ✅ 完全支持 |
| **Samsung** | Galaxy Watch 6 | 圆形 | 480×480 | ✅ 完全支持 |
| **Google** | Pixel Watch | 圆形 | 384×384 | ✅ 完全支持 |
| **Google** | Pixel Watch 2 | 圆形 | 384×384 | ✅ 完全支持 |
| **Fossil** | Gen 6 Wellness | 圆形 | 416×416 | ✅ 完全支持 |
| **TicWatch** | Pro 5 | 圆形 | 466×466 | ✅ 完全支持 |
| **Mobvoi** | TicWatch E3 | 圆形 | 454×454 | ✅ 完全支持 |

## 🏗️ 项目结构

```
wearos/
├── app/                          # 手机端应用
│   ├── src/main/
│   │   ├── java/com/changlee/link/
│   │   │   ├── MainActivity.kt   # 主活动
│   │   │   ├── services/         # 服务层
│   │   │   │   ├── NEXUSApiService.kt # NEXUS API 服务
│   │   │   │   ├── WearableService.kt # 穿戴设备服务
│   │   │   │   └── BackgroundSyncService.kt # 后台同步
│   │   │   ├── models/           # 数据模型
│   │   │   └── utils/            # 工具类
│   │   └── res/                  # 资源文件
│   └── build.gradle              # 应用构建配置
├── wear/                         # 手表端应用
│   ├── src/main/
│   │   ├── java/com/changlee/link/wear/
│   │   │   ├── MainActivity.kt   # 手表主活动
│   │   │   ├── presentation/     # UI 层
│   │   │   │   ├── dashboard/    # 仪表板界面
│   │   │   │   │   ├── DashboardScreen.kt
│   │   │   │   │   └── DashboardViewModel.kt
│   │   │   │   ├── systems/      # 系统状态界面
│   │   │   │   │   ├── SystemsScreen.kt
│   │   │   │   │   └── SystemsViewModel.kt
│   │   │   │   ├── actions/      # 快速操作界面
│   │   │   │   │   ├── ActionsScreen.kt
│   │   │   │   │   └── ActionsViewModel.kt
│   │   │   │   ├── health/       # 健康监测界面
│   │   │   │   │   ├── HealthScreen.kt
│   │   │   │   │   └── HealthViewModel.kt
│   │   │   │   └── components/   # 通用组件
│   │   │   │       ├── SystemCard.kt
│   │   │   │       ├── ActionButton.kt
│   │   │   │       └── HealthMetric.kt
│   │   │   ├── data/             # 数据层
│   │   │   │   ├── repository/   # 数据仓库
│   │   │   │   ├── local/        # 本地数据
│   │   │   │   └── remote/       # 远程数据
│   │   │   ├── services/         # 服务层
│   │   │   │   ├── WearableDataService.kt # 穿戴数据服务
│   │   │   │   ├── HealthService.kt # 健康服务
│   │   │   │   └── NotificationService.kt # 通知服务
│   │   │   └── utils/            # 工具类
│   │   │       ├── HapticUtils.kt # 触觉反馈
│   │   │       ├── ThemeUtils.kt  # 主题工具
│   │   │       └── Extensions.kt  # 扩展函数
│   │   └── res/                  # 资源文件
│   └── build.gradle              # 手表应用构建配置
├── shared/                       # 共享模块
│   ├── src/main/
│   │   ├── java/com/changlee/link/shared/
│   │   │   ├── models/           # 共享数据模型
│   │   │   ├── protocols/        # 通信协议
│   │   │   └── constants/        # 常量定义
│   │   └── res/                  # 共享资源
│   └── build.gradle              # 共享模块构建配置
├── build.gradle                  # 项目构建配置
├── gradle.properties             # Gradle 属性
└── settings.gradle               # 项目设置
```

## 🔧 核心功能实现

### 1. Wearable Data Layer 通信

```kotlin
import com.google.android.gms.wearable.*

class WearableDataService : WearableListenerService() {
    private lateinit var dataClient: DataClient
    private lateinit var messageClient: MessageClient
    
    override fun onCreate() {
        super.onCreate()
        dataClient = Wearable.getDataClient(this)
        messageClient = Wearable.getMessageClient(this)
    }
    
    // 发送命令到手机
    suspend fun sendCommand(command: CommandRequest): Result<CommandResponse> {
        return try {
            val nodes = Wearable.getNodeClient(this).connectedNodes.await()
            val node = nodes.firstOrNull() ?: return Result.failure(Exception("No connected nodes"))
            
            val message = Json.encodeToString(command).toByteArray()
            val result = messageClient.sendMessage(node.id, "/nexus/command", message).await()
            
            // 等待响应
            val response = waitForResponse(result.requestId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // 同步系统状态
    suspend fun syncSystemStatus(status: SystemsStatusPayload) {
        val dataMap = DataMap().apply {
            putString("type", "system_status")
            putLong("timestamp", System.currentTimeMillis())
            putString("data", Json.encodeToString(status))
        }
        
        val request = PutDataMapRequest.create("/nexus/status").apply {
            this.dataMap = dataMap
        }
        
        dataClient.putDataItem(request.asPutDataRequest()).await()
    }
    
    override fun onMessageReceived(messageEvent: MessageEvent) {
        when (messageEvent.path) {
            "/nexus/response" -> {
                val response = Json.decodeFromString<CommandResponse>(
                    String(messageEvent.data)
                )
                handleCommandResponse(response)
            }
            "/nexus/notification" -> {
                val notification = Json.decodeFromString<NotificationPayload>(
                    String(messageEvent.data)
                )
                showNotification(notification)
            }
        }
    }
    
    override fun onDataChanged(dataEvents: DataEventBuffer) {
        dataEvents.forEach { event ->
            when (event.dataItem.uri.path) {
                "/nexus/status" -> {
                    val dataMap = DataMapItem.fromDataItem(event.dataItem).dataMap
                    val statusJson = dataMap.getString("data")
                    val status = Json.decodeFromString<SystemsStatusPayload>(statusJson)
                    updateSystemStatus(status)
                }
            }
        }
    }
}
```

### 2. Jetpack Compose 主界面

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.wear.compose.foundation.lazy.ScalingLazyColumn
import androidx.wear.compose.foundation.lazy.rememberScalingLazyListState
import androidx.wear.compose.material.*
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.composable
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController

@Composable
fun ChangleeLinkApp() {
    val navController = rememberSwipeDismissableNavController()
    
    ChangleeLinkTheme {
        SwipeDismissableNavHost(
            navController = navController,
            startDestination = "dashboard"
        ) {
            composable("dashboard") {
                DashboardScreen(
                    onNavigateToSystems = { navController.navigate("systems") },
                    onNavigateToActions = { navController.navigate("actions") },
                    onNavigateToHealth = { navController.navigate("health") }
                )
            }
            
            composable("systems") {
                SystemsScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            composable("actions") {
                ActionsScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
            
            composable("health") {
                HealthScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
        }
    }
}

@Composable
fun DashboardScreen(
    onNavigateToSystems: () -> Unit,
    onNavigateToActions: () -> Unit,
    onNavigateToHealth: () -> Unit,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberScalingLazyListState()
    
    Scaffold(
        timeText = {
            TimeText(
                modifier = Modifier.scrollAway(listState)
            )
        },
        vignette = {
            Vignette(vignettePosition = VignettePosition.TopAndBottom)
        },
        positionIndicator = {
            PositionIndicator(scalingLazyListState = listState)
        }
    ) {
        ScalingLazyColumn(
            modifier = Modifier.fillMaxSize(),
            state = listState,
            contentPadding = PaddingValues(
                top = 32.dp,
                start = 8.dp,
                end = 8.dp,
                bottom = 32.dp
            ),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            item {
                Text(
                    text = "NEXUS Control",
                    style = MaterialTheme.typography.title1,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            
            item {
                SystemStatusCard(
                    systemsCount = uiState.systemsStatus,
                    onClick = onNavigateToSystems
                )
            }
            
            item {
                QuickActionsCard(
                    onClick = onNavigateToActions
                )
            }
            
            item {
                HealthStatusCard(
                    healthData = uiState.healthData,
                    onClick = onNavigateToHealth
                )
            }
            
            item {
                ConnectionStatusCard(
                    isConnected = uiState.isConnected,
                    lastSync = uiState.lastSyncTime
                )
            }
        }
    }
}
```

### 3. 系统状态界面

```kotlin
@Composable
fun SystemsScreen(
    onNavigateBack: () -> Unit,
    viewModel: SystemsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberScalingLazyListState()
    
    Scaffold(
        timeText = {
            TimeText(
                modifier = Modifier.scrollAway(listState)
            )
        },
        vignette = {
            Vignette(vignettePosition = VignettePosition.TopAndBottom)
        },
        positionIndicator = {
            PositionIndicator(scalingLazyListState = listState)
        }
    ) {
        ScalingLazyColumn(
            modifier = Modifier.fillMaxSize(),
            state = listState,
            contentPadding = PaddingValues(
                top = 32.dp,
                start = 8.dp,
                end = 8.dp,
                bottom = 32.dp
            ),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            item {
                Text(
                    text = "系统状态",
                    style = MaterialTheme.typography.title1,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            
            // 在线系统
            if (uiState.onlineSystems.isNotEmpty()) {
                item {
                    Text(
                        text = "在线系统 (${uiState.onlineSystems.size})",
                        style = MaterialTheme.typography.title3,
                        color = MaterialTheme.colors.primary,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
                
                items(uiState.onlineSystems) { system ->
                    SystemCard(
                        system = system,
                        onClick = { viewModel.onSystemClick(system) }
                    )
                }
            }
            
            // 离线系统
            if (uiState.offlineSystems.isNotEmpty()) {
                item {
                    Text(
                        text = "离线系统 (${uiState.offlineSystems.size})",
                        style = MaterialTheme.typography.title3,
                        color = MaterialTheme.colors.error,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
                
                items(uiState.offlineSystems) { system ->
                    SystemCard(
                        system = system,
                        onClick = { viewModel.onSystemClick(system) },
                        alpha = 0.6f
                    )
                }
            }
            
            // 受限系统
            if (uiState.restrictedSystems.isNotEmpty()) {
                item {
                    Text(
                        text = "受限系统 (${uiState.restrictedSystems.size})",
                        style = MaterialTheme.typography.title3,
                        color = Color(0xFFFF9800),
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
                
                items(uiState.restrictedSystems) { system ->
                    SystemCard(
                        system = system,
                        onClick = { viewModel.onSystemClick(system) },
                        showLockIcon = true
                    )
                }
            }
            
            item {
                Button(
                    onClick = { viewModel.refreshSystems() },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 8.dp)
                ) {
                    Text("刷新状态")
                }
            }
        }
    }
}

@Composable
fun SystemCard(
    system: SystemInfo,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    alpha: Float = 1f,
    showLockIcon: Boolean = false
) {
    Card(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .alpha(alpha),
        backgroundPainter = CardDefaults.cardBackgroundPainter(
            startBackgroundColor = MaterialTheme.colors.surface.copy(alpha = 0.3f),
            endBackgroundColor = MaterialTheme.colors.surface.copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 系统图标
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .background(
                        color = getSystemColor(system.status),
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = getSystemIcon(system.id),
                    fontSize = 16.sp
                )
            }
            
            Spacer(modifier = Modifier.width(12.dp))
            
            // 系统信息
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = system.name,
                    style = MaterialTheme.typography.body1,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                
                Text(
                    text = getStatusText(system.status),
                    style = MaterialTheme.typography.caption1,
                    color = getSystemColor(system.status),
                    maxLines = 1
                )
                
                system.metrics?.let { metrics ->
                    Text(
                        text = "CPU: ${metrics.cpuUsage?.toInt() ?: 0}%",
                        style = MaterialTheme.typography.caption2,
                        color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
                    )
                }
            }
            
            // 锁定图标
            if (showLockIcon) {
                Icon(
                    imageVector = Icons.Default.Lock,
                    contentDescription = "受限系统",
                    tint = Color(0xFFFF9800),
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}
```

### 4. 快速操作界面

```kotlin
@Composable
fun ActionsScreen(
    onNavigateBack: () -> Unit,
    viewModel: ActionsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberScalingLazyListState()
    
    Scaffold(
        timeText = {
            TimeText(
                modifier = Modifier.scrollAway(listState)
            )
        },
        vignette = {
            Vignette(vignettePosition = VignettePosition.TopAndBottom)
        },
        positionIndicator = {
            PositionIndicator(scalingLazyListState = listState)
        }
    ) {
        ScalingLazyColumn(
            modifier = Modifier.fillMaxSize(),
            state = listState,
            contentPadding = PaddingValues(
                top = 32.dp,
                start = 8.dp,
                end = 8.dp,
                bottom = 32.dp
            ),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            item {
                Text(
                    text = "快速操作",
                    style = MaterialTheme.typography.title1,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            
            items(uiState.quickActions) { action ->
                ActionButton(
                    action = action,
                    onClick = { viewModel.executeAction(action) },
                    isExecuting = uiState.executingActions.contains(action.id)
                )
            }
        }
    }
    
    // 显示执行结果
    uiState.lastResult?.let { result ->
        LaunchedEffect(result) {
            // 显示结果通知
            if (result.success) {
                // 成功触觉反馈
                HapticUtils.playSuccess()
            } else {
                // 失败触觉反馈
                HapticUtils.playError()
            }
        }
    }
}

@Composable
fun ActionButton(
    action: QuickAction,
    onClick: () -> Unit,
    isExecuting: Boolean = false,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        enabled = !isExecuting,
        colors = ButtonDefaults.buttonColors(
            backgroundColor = action.color.copy(alpha = 0.8f)
        )
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            if (isExecuting) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colors.onPrimary
                )
                Spacer(modifier = Modifier.width(8.dp))
            } else {
                Text(
                    text = action.icon,
                    fontSize = 16.sp
                )
                Spacer(modifier = Modifier.width(8.dp))
            }
            
            Text(
                text = action.title,
                style = MaterialTheme.typography.button,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}
```

### 5. 健康监测服务

```kotlin
import androidx.health.services.client.HealthServices
import androidx.health.services.client.data.*

class HealthService @Inject constructor(
    private val context: Context
) {
    private val healthServicesClient = HealthServices.getClient(context)
    private val passiveMonitoringClient = healthServicesClient.passiveMonitoringClient
    private val measureClient = healthServicesClient.measureClient
    
    private val _healthData = MutableStateFlow(HealthData())
    val healthData: StateFlow<HealthData> = _healthData.asStateFlow()
    
    suspend fun startHealthMonitoring() {
        // 检查权限
        if (!hasHealthPermissions()) {
            requestHealthPermissions()
            return
        }
        
        // 启动被动监测
        val passiveDataTypes = setOf(
            DataType.HEART_RATE_BPM,
            DataType.STEPS,
            DataType.CALORIES_TOTAL
        )
        
        val passiveGoals = listOf(
            PassiveGoal(
                dataTypeCondition = DataTypeCondition(
                    dataType = DataType.HEART_RATE_BPM,
                    threshold = Value.ofDouble(100.0),
                    comparisonType = ComparisonType.GREATER_THAN
                )
            )
        )
        
        val config = PassiveMonitoringConfig(
            dataTypes = passiveDataTypes,
            shouldUserActivityInfoBeRequested = true,
            dailyGoals = passiveGoals,
            healthEventTypes = setOf(HealthEvent.Type.FALL_DETECTED)
        )
        
        passiveMonitoringClient.setPassiveListenerService(
            HealthListenerService::class.java,
            config
        )
    }
    
    suspend fun measureHeartRate(): Result<Double> {
        return try {
            val capabilities = measureClient.getCapabilitiesAsync().await()
            
            if (DataType.HEART_RATE_BPM !in capabilities.supportedDataTypesMeasure) {
                return Result.failure(Exception("Heart rate measurement not supported"))
            }
            
            val measureConfig = MeasureConfig(
                dataType = DataType.HEART_RATE_BPM,
                isGolfMode = false
            )
            
            val callback = object : MeasureCallback {
                override fun onAvailabilityChanged(
                    dataType: DataType<*, *>,
                    availability: Availability
                ) {
                    // Handle availability changes
                }
                
                override fun onDataReceived(data: DataPointContainer) {
                    val heartRateData = data.getData(DataType.HEART_RATE_BPM)
                    heartRateData.forEach { dataPoint ->
                        val heartRate = dataPoint.value.asDouble()
                        updateHeartRate(heartRate)
                    }
                }
            }
            
            measureClient.registerMeasureCallback(measureConfig, callback)
            
            // 等待测量结果
            delay(10000) // 10秒测量时间
            measureClient.unregisterMeasureCallbackAsync(measureConfig, callback)
            
            Result.success(_healthData.value.heartRate)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun updateHeartRate(heartRate: Double) {
        _healthData.value = _healthData.value.copy(
            heartRate = heartRate,
            lastUpdated = System.currentTimeMillis()
        )
        
        // 上传到 NEXUS
        uploadHealthData()
    }
    
    private fun uploadHealthData() {
        // 通过 WearableDataService 上传健康数据
        val healthPayload = HealthDataPayload(
            userId = "current_user",
            deviceId = getDeviceId(),
            metrics = listOf(
                HealthMetric(
                    type = HealthMetricType.HEART_RATE,
                    value = _healthData.value.heartRate,
                    unit = "bpm",
                    timestamp = System.currentTimeMillis()
                )
            )
        )
        
        // 发送到手机端
        GlobalScope.launch {
            WearableDataService.instance.uploadHealthData(healthPayload)
        }
    }
}

class HealthListenerService : PassiveListenerService() {
    override fun onNewDataPointsReceived(dataPoints: DataPointContainer) {
        // 处理新的健康数据点
        dataPoints.getData(DataType.HEART_RATE_BPM).forEach { dataPoint ->
            val heartRate = dataPoint.value.asDouble()
            // 更新健康数据
        }
        
        dataPoints.getData(DataType.STEPS).forEach { dataPoint ->
            val steps = dataPoint.value.asLong()
            // 更新步数数据
        }
    }
    
    override fun onGoalCompleted(goal: PassiveGoal) {
        // 处理目标完成事件
        when (goal.dataTypeCondition.dataType) {
            DataType.HEART_RATE_BPM -> {
                // 心率目标完成
                sendNotification("心率警告", "心率过高，请注意休息")
            }
        }
    }
    
    override fun onHealthEventReceived(event: HealthEvent) {
        // 处理健康事件
        when (event.type) {
            HealthEvent.Type.FALL_DETECTED -> {
                // 检测到跌倒
                sendEmergencyNotification("跌倒检测", "检测到可能的跌倒事件")
            }
        }
    }
}
```

## 🔧 构建和部署

### 开发环境要求

```bash
# 检查 Android Studio 版本
# Android Studio Hedgehog 2023.1.1 或更高版本

# 检查 Kotlin 版本
# Kotlin 1.9.0 或更高版本

# 检查 Gradle 版本
./gradlew --version
# Gradle 8.0 或更高版本
```

### 构建配置

```kotlin
// app/build.gradle
android {
    compileSdk 34
    
    defaultConfig {
        applicationId "com.changlee.link"
        minSdk 30
        targetSdk 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildFeatures {
        compose true
    }
    
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.4"
    }
}

dependencies {
    implementation "androidx.wear.compose:compose-material:1.2.1"
    implementation "androidx.wear.compose:compose-foundation:1.2.1"
    implementation "androidx.wear.compose:compose-navigation:1.2.1"
    
    implementation "com.google.android.gms:play-services-wearable:18.1.0"
    implementation "androidx.health:health-services-client:1.0.0-beta03"
    
    implementation "androidx.hilt:hilt-navigation-compose:1.1.0"
    implementation "com.google.dagger:hilt-android:2.48"
    kapt "com.google.dagger:hilt-compiler:2.48"
    
    implementation "org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0"
    implementation "androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0"
}
```

### 权限配置

```xml
<!-- wear/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <!-- Wear OS 权限 -->
    <uses-feature android:name="android.hardware.type.watch" />
    
    <!-- 健康数据权限 -->
    <uses-permission android:name="android.permission.BODY_SENSORS" />
    <uses-permission android:name="android.permission.ACTIVITY_RECOGNITION" />
    <uses-permission android:name="androidx.health.permission.READ_HEART_RATE" />
    <uses-permission android:name="androidx.health.permission.READ_STEPS" />
    
    <!-- 网络权限 -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <!-- 穿戴设备通信权限 -->
    <uses-permission android:name="com.google.android.permission.PROVIDE_BACKGROUND" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    
    <application
        android:name=".ChangleeLinkApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.DeviceDefault">
        
        <activity
            android:name=".presentation.MainActivity"
            android:exported="true"
            android:theme="@android:style/Theme.DeviceDefault">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <service
            android:name=".services.WearableDataService"
            android:exported="false">
            <intent-filter>
                <action android:name="com.google.android.gms.wearable.DATA_CHANGED" />
                <action android:name="com.google.android.gms.wearable.MESSAGE_RECEIVED" />
                <data android:scheme="wear" android:host="*" />
            </intent-filter>
        </service>
        
        <service
            android:name=".services.HealthListenerService"
            android:exported="false"
            android:permission="androidx.health.permission.PASSIVE_DATA_COLLECTION" />
        
    </application>
</manifest>
```

## 🧪 测试

### 单元测试

```kotlin
@RunWith(AndroidJUnit4::class)
class WearableDataServiceTest {
    
    @Mock
    private lateinit var dataClient: DataClient
    
    @Mock
    private lateinit var messageClient: MessageClient
    
    private lateinit var service: WearableDataService
    
    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = WearableDataService()
    }
    
    @Test
    fun testSendCommand() = runTest {
        val command = CommandRequest(
            systemId = "test_system",
            command = "test_command"
        )
        
        // Mock successful message sending
        whenever(messageClient.sendMessage(any(), any(), any()))
            .thenReturn(Tasks.forResult(1))
        
        val result = service.sendCommand(command)
        
        assertTrue(result.isSuccess)
    }
    
    @Test
    fun testHealthDataUpload() = runTest {
        val healthData = HealthDataPayload(
            userId = "test_user",
            deviceId = "test_device",
            metrics = listOf(
                HealthMetric(
                    type = HealthMetricType.HEART_RATE,
                    value = 72.0,
                    unit = "bpm",
                    timestamp = System.currentTimeMillis()
                )
            )
        )
        
        val result = service.uploadHealthData(healthData)
        
        assertTrue(result.isSuccess)
    }
}
```

### UI 测试

```kotlin
@RunWith(AndroidJUnit4::class)
class DashboardScreenTest {
    
    @get:Rule
    val composeTestRule = createComposeRule()
    
    @Test
    fun testDashboardScreenDisplaysCorrectly() {
        composeTestRule.setContent {
            ChangleeLinkTheme {
                DashboardScreen(
                    onNavigateToSystems = {},
                    onNavigateToActions = {},
                    onNavigateToHealth = {}
                )
            }
        }
        
        composeTestRule.onNodeWithText("NEXUS Control").assertIsDisplayed()
        composeTestRule.onNodeWithText("系统状态").assertIsDisplayed()
        composeTestRule.onNodeWithText("快速操作").assertIsDisplayed()
        composeTestRule.onNodeWithText("健康监测").assertIsDisplayed()
    }
    
    @Test
    fun testSystemStatusCardClick() {
        var navigationCalled = false
        
        composeTestRule.setContent {
            ChangleeLinkTheme {
                DashboardScreen(
                    onNavigateToSystems = { navigationCalled = true },
                    onNavigateToActions = {},
                    onNavigateToHealth = {}
                )
            }
        }
        
        composeTestRule.onNodeWithText("系统状态").performClick()
        assertTrue(navigationCalled)
    }
}
```

## 📊 性能优化

### 电池优化

```kotlin
class BatteryOptimizer @Inject constructor(
    private val context: Context
) {
    fun getOptimalSyncInterval(): Long {
        val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        val batteryLevel = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        
        return when {
            batteryLevel > 80 -> 30_000L      // 30秒
            batteryLevel > 50 -> 60_000L      // 1分钟
            batteryLevel > 20 -> 300_000L     // 5分钟
            else -> 600_000L                  // 10分钟
        }
    }
    
    fun shouldReduceAnimations(): Boolean {
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        return powerManager.isPowerSaveMode
    }
}
```

### 内存优化

```kotlin
class ImageCache @Inject constructor() {
    private val cache = LruCache<String, Bitmap>(
        (Runtime.getRuntime().maxMemory() / 1024 / 8).toInt() // 使用可用内存的1/8
    )
    
    fun getBitmap(key: String): Bitmap? = cache.get(key)
    
    fun putBitmap(key: String, bitmap: Bitmap) {
        cache.put(key, bitmap)
    }
    
    fun clearCache() {
        cache.evictAll()
    }
}
```

## 🔐 安全考虑

### 数据加密

```kotlin
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class EncryptionManager @Inject constructor() {
    private val transformation = "AES/GCM/NoPadding"
    private val androidKeyStore = "AndroidKeyStore"
    private val keyAlias = "ChangleeLinkKey"
    
    fun encrypt(data: ByteArray): EncryptedData {
        val keyStore = KeyStore.getInstance(androidKeyStore)
        keyStore.load(null)
        
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance(transformation)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        
        val iv = cipher.iv
        val encryptedData = cipher.doFinal(data)
        
        return EncryptedData(encryptedData, iv)
    }
    
    fun decrypt(encryptedData: EncryptedData): ByteArray {
        val keyStore = KeyStore.getInstance(androidKeyStore)
        keyStore.load(null)
        
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance(transformation)
        val spec = GCMParameterSpec(128, encryptedData.iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)
        
        return cipher.doFinal(encryptedData.data)
    }
}

data class EncryptedData(
    val data: ByteArray,
    val iv: ByteArray
)
```

---

**开发状态**: 🚧 开发中  
**最后更新**: 2025-08-20  
**Kotlin 版本**: 1.9+  
**最低 Wear OS**: 3.0 (API 30)