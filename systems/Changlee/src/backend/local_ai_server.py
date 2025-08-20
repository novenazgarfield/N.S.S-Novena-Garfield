"""
本地AI微服务 - FastAPI服务器
为Changlee提供本地化AI API端点
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uvicorn
import logging
import asyncio
import threading
import time
from contextlib import asynccontextmanager

from services.LocalAIService import LocalAIService

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局AI服务实例
ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global ai_service
    
    # 启动时初始化AI服务
    logger.info("启动本地AI服务...")
    ai_service = LocalAIService()
    
    # 在后台线程中加载模型
    def load_model_background():
        try:
            success = ai_service.load_model()
            if success:
                logger.info("✅ AI模型加载成功")
            else:
                logger.error("❌ AI模型加载失败")
        except Exception as e:
            logger.error(f"模型加载异常: {str(e)}")
    
    # 启动后台加载
    model_thread = threading.Thread(target=load_model_background)
    model_thread.daemon = True
    model_thread.start()
    
    yield
    
    # 关闭时清理资源
    if ai_service:
        logger.info("清理AI服务资源...")
        ai_service.unload_model()

# 创建FastAPI应用
app = FastAPI(
    title="Changlee本地AI服务",
    description="为长离的学习胶囊提供本地化AI支持",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="用户输入提示")
    context: str = Field(default="daily_greeting", description="对话上下文")
    max_length: int = Field(default=50, ge=10, le=200, description="最大响应长度")
    use_cache: bool = Field(default=True, description="是否使用缓存")

class WordHintRequest(BaseModel):
    word: str = Field(..., description="目标单词")
    difficulty: str = Field(default="intermediate", description="难度级别")

class EncouragementRequest(BaseModel):
    words_learned: int = Field(default=0, ge=0, description="学习的单词数")
    accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="准确率")
    study_time: int = Field(default=0, ge=0, description="学习时间(分钟)")

class GreetingRequest(BaseModel):
    time_of_day: str = Field(default="morning", description="时间段")

class ExplanationRequest(BaseModel):
    concept: str = Field(..., description="需要解释的概念")
    user_level: str = Field(default="beginner", description="用户水平")

# 响应模型
class AIResponse(BaseModel):
    success: bool
    response: str
    context: Optional[str] = None
    generation_time: Optional[float] = None
    from_cache: Optional[bool] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ServiceStatus(BaseModel):
    service_name: str
    model_name: str
    device: str
    is_loaded: bool
    is_busy: bool
    stats: Dict[str, Any]
    cache_size: int
    supported_contexts: List[str]

# API端点
@app.get("/", summary="服务根路径")
async def root():
    """服务根路径"""
    return {
        "service": "Changlee本地AI服务",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/generate",
            "word_hint": "/word_hint", 
            "encouragement": "/encouragement",
            "greeting": "/greeting",
            "explanation": "/explanation",
            "status": "/status",
            "health": "/health"
        }
    }

@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    global ai_service
    
    if ai_service is None:
        return {"status": "initializing", "message": "AI服务正在初始化"}
    
    if not ai_service.is_loaded:
        return {"status": "loading", "message": "AI模型正在加载"}
    
    return {
        "status": "healthy",
        "message": "AI服务运行正常",
        "model_loaded": ai_service.is_loaded,
        "is_busy": ai_service.is_busy
    }

@app.post("/generate", response_model=AIResponse, summary="生成AI响应")
async def generate_response(request: GenerateRequest):
    """
    生成AI响应
    
    支持的上下文类型:
    - daily_greeting: 日常问候
    - word_learning: 单词学习
    - spelling_practice: 拼写练习
    - encouragement: 学习鼓励
    - explanation: 概念解释
    """
    global ai_service
    
    if ai_service is None or not ai_service.is_loaded:
        raise HTTPException(
            status_code=503, 
            detail="AI服务未就绪，请稍后再试"
        )
    
    try:
        result = ai_service.generate_response(
            prompt=request.prompt,
            context=request.context,
            max_length=request.max_length,
            use_cache=request.use_cache
        )
        
        return AIResponse(**result)
        
    except Exception as e:
        logger.error(f"生成响应失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/word_hint", response_model=AIResponse, summary="生成单词学习提示")
async def generate_word_hint(request: WordHintRequest):
    """为指定单词生成学习提示或记忆方法"""
    global ai_service
    
    if ai_service is None or not ai_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="AI服务未就绪，请稍后再试"
        )
    
    try:
        result = ai_service.generate_word_hint(
            word=request.word,
            difficulty=request.difficulty
        )
        
        return AIResponse(**result)
        
    except Exception as e:
        logger.error(f"生成单词提示失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/encouragement", response_model=AIResponse, summary="生成学习鼓励语")
async def generate_encouragement(request: EncouragementRequest):
    """基于学习进度生成鼓励语"""
    global ai_service
    
    if ai_service is None or not ai_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="AI服务未就绪，请稍后再试"
        )
    
    try:
        learning_progress = {
            'words_learned': request.words_learned,
            'accuracy': request.accuracy,
            'study_time': request.study_time
        }
        
        result = ai_service.generate_encouragement(learning_progress)
        
        return AIResponse(**result)
        
    except Exception as e:
        logger.error(f"生成鼓励语失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/greeting", response_model=AIResponse, summary="生成每日问候语")
async def generate_greeting(request: GreetingRequest):
    """生成不同时段的问候语"""
    global ai_service
    
    if ai_service is None or not ai_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="AI服务未就绪，请稍后再试"
        )
    
    try:
        result = ai_service.generate_daily_greeting(request.time_of_day)
        
        return AIResponse(**result)
        
    except Exception as e:
        logger.error(f"生成问候语失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explanation", response_model=AIResponse, summary="生成概念解释")
async def generate_explanation(request: ExplanationRequest):
    """生成简单易懂的概念解释"""
    global ai_service
    
    if ai_service is None or not ai_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="AI服务未就绪，请稍后再试"
        )
    
    try:
        result = ai_service.generate_explanation(
            concept=request.concept,
            user_level=request.user_level
        )
        
        return AIResponse(**result)
        
    except Exception as e:
        logger.error(f"生成解释失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=ServiceStatus, summary="获取服务状态")
async def get_service_status():
    """获取AI服务的详细状态信息"""
    global ai_service
    
    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI服务未初始化"
        )
    
    try:
        status = ai_service.get_service_status()
        return ServiceStatus(**status)
        
    except Exception as e:
        logger.error(f"获取服务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear", summary="清理响应缓存")
async def clear_cache():
    """清理AI服务的响应缓存"""
    global ai_service
    
    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI服务未初始化"
        )
    
    try:
        ai_service.clear_cache()
        return {"success": True, "message": "缓存已清理"}
        
    except Exception as e:
        logger.error(f"清理缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/optimize", summary="优化内存使用")
async def optimize_memory(background_tasks: BackgroundTasks):
    """优化AI服务的内存使用"""
    global ai_service
    
    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI服务未初始化"
        )
    
    try:
        # 在后台执行内存优化
        background_tasks.add_task(ai_service.optimize_memory)
        
        return {"success": True, "message": "内存优化已启动"}
        
    except Exception as e:
        logger.error(f"内存优化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model/reload", summary="重新加载模型")
async def reload_model(background_tasks: BackgroundTasks):
    """重新加载AI模型"""
    global ai_service
    
    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI服务未初始化"
        )
    
    try:
        # 在后台执行模型重载
        def reload_background():
            success = ai_service.reload_model()
            if success:
                logger.info("✅ 模型重载成功")
            else:
                logger.error("❌ 模型重载失败")
        
        background_tasks.add_task(reload_background)
        
        return {"success": True, "message": "模型重载已启动"}
        
    except Exception as e:
        logger.error(f"模型重载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 批量处理端点
@app.post("/batch/generate", summary="批量生成响应")
async def batch_generate(requests: List[GenerateRequest]):
    """批量生成AI响应"""
    global ai_service
    
    if ai_service is None or not ai_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="AI服务未就绪，请稍后再试"
        )
    
    if len(requests) > 10:  # 限制批量大小
        raise HTTPException(
            status_code=400,
            detail="批量请求数量不能超过10个"
        )
    
    try:
        results = []
        
        for req in requests:
            result = ai_service.generate_response(
                prompt=req.prompt,
                context=req.context,
                max_length=req.max_length,
                use_cache=req.use_cache
            )
            results.append(AIResponse(**result))
        
        return {
            "success": True,
            "results": results,
            "total_requests": len(requests)
        }
        
    except Exception as e:
        logger.error(f"批量生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return {
        "success": False,
        "error": "服务器内部错误",
        "detail": str(exc) if app.debug else "请联系管理员"
    }

# 启动函数
def start_server(host: str = "0.0.0.0", port: int = 8001, reload: bool = False):
    """启动FastAPI服务器"""
    logger.info(f"启动Changlee本地AI服务器: {host}:{port}")
    
    uvicorn.run(
        "local_ai_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Changlee本地AI服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8001, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    if args.debug:
        app.debug = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    start_server(
        host=args.host,
        port=args.port,
        reload=args.reload
    )