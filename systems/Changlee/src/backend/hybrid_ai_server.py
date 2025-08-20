#!/usr/bin/env python3
"""
Changlee混合AI服务器
基于FastAPI的高性能异步AI服务
支持本地AI (Gemma 2) + 云端API (Gemini等) 的混合智能对话
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import argparse
from contextlib import asynccontextmanager

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.HybridAIService import HybridAIService, AIServiceType
    HYBRID_AI_AVAILABLE = True
except ImportError:
    # 回退到原始的LocalAIService
    try:
        from services.LocalAIService import LocalAIService
        HybridAIService = LocalAIService
        AIServiceType = None
        HYBRID_AI_AVAILABLE = False
        print("⚠️ 使用原始LocalAIService，混合AI功能不可用")
    except ImportError as e:
        print(f"❌ 导入AI服务失败: {e}")
        print("请确保AI服务文件存在且依赖已安装")
        sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局AI服务实例
ai_service: Optional[HybridAIService] = None

# Pydantic模型
class GenerateRequest(BaseModel):
    """AI生成请求模型"""
    prompt: str = Field(..., description="用户输入提示")
    context: str = Field(default="daily_greeting", description="对话上下文")
    service_type: Optional[str] = Field(default=None, description="指定AI服务类型")
    max_length: int = Field(default=256, description="最大生成长度")
    temperature: float = Field(default=0.7, description="生成温度")

class WordHintRequest(BaseModel):
    """单词提示请求模型"""
    word: str = Field(..., description="需要提示的单词")
    difficulty: str = Field(default="medium", description="难度级别")

class GreetingRequest(BaseModel):
    """问候请求模型"""
    time_of_day: str = Field(default="morning", description="时间段")
    user_name: Optional[str] = Field(default=None, description="用户名称")

class ExplanationRequest(BaseModel):
    """解释请求模型"""
    concept: str = Field(..., description="需要解释的概念")
    level: str = Field(default="beginner", description="解释级别")

class ServiceSwitchRequest(BaseModel):
    """服务切换请求模型"""
    service_type: str = Field(..., description="目标服务类型")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global ai_service
    
    # 启动时初始化AI服务
    logger.info("🚀 启动Changlee混合AI服务器...")
    
    try:
        # 从环境变量获取配置
        preferred_service = os.getenv('PREFERRED_AI_SERVICE', 'auto').lower()
        local_model = os.getenv('LOCAL_MODEL_NAME', 'google/gemma-2-2b')
        max_memory = float(os.getenv('MAX_MEMORY_GB', '4.0'))
        
        # 解析首选服务类型
        if HYBRID_AI_AVAILABLE:
            service_type_map = {
                'local': AIServiceType.LOCAL,
                'gemini': AIServiceType.GEMINI,
                'deepseek': AIServiceType.DEEPSEEK,
                'auto': AIServiceType.AUTO
            }
            preferred_type = service_type_map.get(preferred_service, AIServiceType.AUTO)
        else:
            preferred_type = None
        
        # 初始化AI服务
        if HYBRID_AI_AVAILABLE:
            ai_service = HybridAIService(
                preferred_service=preferred_type,
                local_model_name=local_model,
                max_memory_gb=max_memory
            )
        else:
            ai_service = LocalAIService(
                model_name=local_model,
                max_memory_gb=max_memory
            )
        
        logger.info("✅ AI服务初始化完成")
        
    except Exception as e:
        logger.error(f"❌ AI服务初始化失败: {e}")
        ai_service = None
    
    yield
    
    # 关闭时清理资源
    logger.info("🛑 关闭Changlee混合AI服务器...")
    if ai_service:
        try:
            if hasattr(ai_service, 'optimize_memory'):
                ai_service.optimize_memory()
        except Exception as e:
            logger.error(f"❌ 资源清理失败: {e}")

# 创建FastAPI应用
app = FastAPI(
    title="Changlee混合AI服务",
    description="支持本地AI和云端API的混合智能对话服务",
    version="2.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Changlee混合AI服务",
        "version": "2.0.0",
        "status": "running",
        "hybrid_ai": HYBRID_AI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        if hasattr(ai_service, 'health_check'):
            status = await ai_service.health_check()
        else:
            status = {
                "healthy": True,
                "service": "local_only",
                "timestamp": datetime.now().isoformat()
            }
        
        return JSONResponse(
            status_code=200 if status.get("healthy", True) else 503,
            content=status
        )
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        raise HTTPException(status_code=503, detail=f"健康检查失败: {str(e)}")

@app.get("/status")
async def get_status():
    """获取服务状态"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        if hasattr(ai_service, 'get_service_status'):
            status = ai_service.get_service_status()
        else:
            status = {
                "service_name": "Changlee本地AI服务",
                "version": "1.0.0",
                "model_loaded": hasattr(ai_service, 'model') and ai_service.model is not None,
                "timestamp": datetime.now().isoformat()
            }
        
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@app.post("/generate")
async def generate_response(request: GenerateRequest):
    """通用AI生成接口"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        # 解析服务类型
        service_type = None
        if HYBRID_AI_AVAILABLE and request.service_type:
            service_type_map = {
                'local': AIServiceType.LOCAL,
                'gemini': AIServiceType.GEMINI,
                'deepseek': AIServiceType.DEEPSEEK
            }
            service_type = service_type_map.get(request.service_type.lower())
        
        # 生成回复
        if hasattr(ai_service, 'generate'):
            result = await ai_service.generate(
                prompt=request.prompt,
                context=request.context,
                service_type=service_type
            )
        else:
            # 回退到原始方法
            result = await ai_service.generate_response(
                prompt=request.prompt,
                context=request.context,
                max_length=request.max_length,
                temperature=request.temperature
            )
        
        if result.get("success", True):
            return {
                "success": True,
                "response": result.get("response", result.get("text", "")),
                "metadata": {
                    "service": result.get("service", "unknown"),
                    "model": result.get("model", "unknown"),
                    "generation_time": result.get("generation_time", 0),
                    "context": request.context,
                    "fallback": result.get("fallback", False)
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))
            
    except Exception as e:
        logger.error(f"❌ 生成回复失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成回复失败: {str(e)}")

@app.post("/word_hint")
async def get_word_hint(request: WordHintRequest):
    """获取单词学习提示"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        prompt = f"请为单词 '{request.word}' 提供学习提示，包括词根、记忆方法、例句等。难度级别：{request.difficulty}"
        
        if hasattr(ai_service, 'generate'):
            result = await ai_service.generate(prompt, "word_learning")
        else:
            result = await ai_service.generate_response(prompt, "word_learning")
        
        if result.get("success", True):
            return {
                "success": True,
                "word": request.word,
                "hint": result.get("response", result.get("text", "")),
                "difficulty": request.difficulty
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成提示失败"))
            
    except Exception as e:
        logger.error(f"❌ 生成单词提示失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成单词提示失败: {str(e)}")

@app.post("/encouragement")
async def get_encouragement():
    """获取学习鼓励语"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        prompt = "用户在学习过程中遇到困难，需要鼓励和支持。"
        
        if hasattr(ai_service, 'generate'):
            result = await ai_service.generate(prompt, "encouragement")
        else:
            result = await ai_service.generate_response(prompt, "encouragement")
        
        if result.get("success", True):
            return {
                "success": True,
                "encouragement": result.get("response", result.get("text", "")),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成鼓励语失败"))
            
    except Exception as e:
        logger.error(f"❌ 生成鼓励语失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成鼓励语失败: {str(e)}")

@app.post("/greeting")
async def get_greeting(request: GreetingRequest):
    """获取个性化问候语"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        user_part = f"，{request.user_name}" if request.user_name else ""
        prompt = f"现在是{request.time_of_day}时段{user_part}，请给出一句温暖的问候。"
        
        if hasattr(ai_service, 'generate'):
            result = await ai_service.generate(prompt, "daily_greeting")
        else:
            result = await ai_service.generate_response(prompt, "daily_greeting")
        
        if result.get("success", True):
            return {
                "success": True,
                "greeting": result.get("response", result.get("text", "")),
                "time_of_day": request.time_of_day,
                "user_name": request.user_name
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成问候语失败"))
            
    except Exception as e:
        logger.error(f"❌ 生成问候语失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成问候语失败: {str(e)}")

@app.post("/explanation")
async def get_explanation(request: ExplanationRequest):
    """获取概念解释"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        prompt = f"请解释概念 '{request.concept}'，解释级别：{request.level}。请用简单易懂的方式，可以使用比喻和例子。"
        
        if hasattr(ai_service, 'generate'):
            result = await ai_service.generate(prompt, "explanation")
        else:
            result = await ai_service.generate_response(prompt, "explanation")
        
        if result.get("success", True):
            return {
                "success": True,
                "concept": request.concept,
                "explanation": result.get("response", result.get("text", "")),
                "level": request.level
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成解释失败"))
            
    except Exception as e:
        logger.error(f"❌ 生成解释失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成解释失败: {str(e)}")

@app.get("/services")
async def list_services():
    """列出可用的AI服务"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        if hasattr(ai_service, 'available_services'):
            services = [s.value for s in ai_service.available_services]
            current = ai_service.current_service.value if ai_service.current_service else None
        else:
            services = ["local"]
            current = "local"
        
        return {
            "success": True,
            "available_services": services,
            "current_service": current,
            "hybrid_ai_enabled": HYBRID_AI_AVAILABLE
        }
    except Exception as e:
        logger.error(f"❌ 获取服务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取服务列表失败: {str(e)}")

@app.post("/switch_service")
async def switch_service(request: ServiceSwitchRequest):
    """切换AI服务"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    if not HYBRID_AI_AVAILABLE:
        raise HTTPException(status_code=400, detail="混合AI功能不可用")
    
    try:
        service_type_map = {
            'local': AIServiceType.LOCAL,
            'gemini': AIServiceType.GEMINI,
            'deepseek': AIServiceType.DEEPSEEK,
            'auto': AIServiceType.AUTO
        }
        
        target_service = service_type_map.get(request.service_type.lower())
        if not target_service:
            raise HTTPException(status_code=400, detail=f"不支持的服务类型: {request.service_type}")
        
        success = ai_service.switch_service(target_service)
        
        return {
            "success": success,
            "current_service": ai_service.current_service.value if success else None,
            "message": f"已切换到 {request.service_type} 服务" if success else "切换失败"
        }
        
    except Exception as e:
        logger.error(f"❌ 切换服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换服务失败: {str(e)}")

@app.post("/cache/clear")
async def clear_cache(background_tasks: BackgroundTasks):
    """清理缓存"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        if hasattr(ai_service, 'clear_cache'):
            background_tasks.add_task(ai_service.clear_cache)
        
        return {
            "success": True,
            "message": "缓存清理任务已启动",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 清理缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")

@app.post("/memory/optimize")
async def optimize_memory(background_tasks: BackgroundTasks):
    """优化内存使用"""
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI服务未初始化")
    
    try:
        if hasattr(ai_service, 'optimize_memory'):
            background_tasks.add_task(ai_service.optimize_memory)
        
        return {
            "success": True,
            "message": "内存优化任务已启动",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 内存优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"内存优化失败: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Changlee混合AI服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8001, help="服务器端口")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--log-level", default="info", help="日志级别")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 启动Changlee混合AI服务器...")
    logger.info(f"   地址: http://{args.host}:{args.port}")
    logger.info(f"   混合AI: {'启用' if HYBRID_AI_AVAILABLE else '禁用'}")
    
    # 启动服务器
    uvicorn.run(
        "hybrid_ai_server:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()