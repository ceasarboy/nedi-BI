"""
系统设置API接口
支持UI风格、AI配置、第三方平台模型选择
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import json

from src.core.database import SessionLocal, Base, engine
from src.models.settings import SystemSettings, AIProvider
from src.api.auth import get_current_user_optional
from src.core.crypto import encrypt_value, decrypt_value, is_encrypted

router = APIRouter(prefix="/api/settings", tags=["settings"])

Base.metadata.create_all(bind=engine)


class UISettingsRequest(BaseModel):
    style: Optional[str] = Field(None, description="UI风格: bloomberg-dark/modern-light")
    primary_color: Optional[str] = Field(None, description="主色调")
    font_size: Optional[str] = Field(None, description="字体大小: small/medium/large")
    dark_mode: Optional[bool] = Field(None, description="暗黑模式")


class AISettingsRequest(BaseModel):
    provider: Optional[str] = Field(None, description="AI提供商")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=32000, description="最大token数")


class SettingsResponse(BaseModel):
    ui_style: str
    ui_primary_color: str
    ui_font_size: str
    ui_dark_mode: bool
    ai_provider: str
    ai_model: str
    ai_temperature: str
    ai_max_tokens: int
    has_api_key: bool
    updated_at: str


class ProviderModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class ProviderResponse(BaseModel):
    name: str
    display_name: str
    base_url: str
    models: List[ProviderModel]
    default_model: str
    icon: Optional[str] = None
    description: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_create_settings(db: Session) -> SystemSettings:
    """获取或创建系统设置"""
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def _init_providers(db: Session):
    """初始化AI提供商数据"""
    providers_data = [
        {
            "name": "deepseek",
            "display_name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "models": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "通用对话模型", "price_input": 0.001, "price_output": 0.002, "price_unit": "¥/千tokens"},
                {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "代码专用模型", "price_input": 0.001, "price_output": 0.002, "price_unit": "¥/千tokens"}
            ],
            "default_model": "deepseek-chat",
            "icon": "🧠",
            "description": "DeepSeek AI - 高性能开源大模型"
        },
        {
            "name": "openai",
            "display_name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "models": [
                {"id": "gpt-4o", "name": "GPT-4o", "description": "最新多模态模型", "price_input": 0.035, "price_output": 0.105, "price_unit": "$/千tokens"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "高性能对话模型", "price_input": 0.01, "price_output": 0.03, "price_unit": "$/千tokens"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "快速经济模型", "price_input": 0.0005, "price_output": 0.0015, "price_unit": "$/千tokens"}
            ],
            "default_model": "gpt-4o",
            "icon": "🤖",
            "description": "OpenAI - GPT系列模型"
        },
        {
            "name": "siliconflow",
            "display_name": "硅基流动",
            "base_url": "https://api.siliconflow.cn/v1",
            "models": [
                {"id": "Qwen/Qwen2.5-72B-Instruct", "name": "Qwen2.5-72B", "description": "通义千问72B", "price_input": 0.004, "price_output": 0.004, "price_unit": "¥/千tokens"},
                {"id": "Qwen/Qwen2.5-32B-Instruct", "name": "Qwen2.5-32B", "description": "通义千问32B", "price_input": 0.0016, "price_output": 0.0016, "price_unit": "¥/千tokens"},
                {"id": "deepseek-ai/DeepSeek-V2.5", "name": "DeepSeek-V2.5", "description": "DeepSeek V2.5", "price_input": 0.0014, "price_output": 0.0014, "price_unit": "¥/千tokens"},
                {"id": "meta-llama/Meta-Llama-3.1-70B-Instruct", "name": "Llama-3.1-70B", "description": "Meta Llama 70B", "price_input": 0.004, "price_output": 0.004, "price_unit": "¥/千tokens"}
            ],
            "default_model": "Qwen/Qwen2.5-72B-Instruct",
            "icon": "💎",
            "description": "硅基流动 - 多模型聚合平台"
        },
        {
            "name": "zhipu",
            "display_name": "智谱AI",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": [
                {"id": "glm-4-plus", "name": "GLM-4 Plus", "description": "智谱最新旗舰模型", "price_input": 0.05, "price_output": 0.05, "price_unit": "¥/千tokens"},
                {"id": "glm-4-0520", "name": "GLM-4", "description": "智谱通用模型", "price_input": 0.1, "price_output": 0.1, "price_unit": "¥/千tokens"},
                {"id": "glm-3-turbo", "name": "GLM-3 Turbo", "description": "快速经济模型", "price_input": 0.001, "price_output": 0.001, "price_unit": "¥/千tokens"}
            ],
            "default_model": "glm-4-plus",
            "icon": "🔮",
            "description": "智谱AI - GLM系列模型"
        }
    ]
    
    for data in providers_data:
        existing = db.query(AIProvider).filter(AIProvider.name == data["name"]).first()
        if not existing:
            provider = AIProvider(
                name=data["name"],
                display_name=data["display_name"],
                base_url=data["base_url"],
                models=json.dumps(data["models"]),
                default_model=data["default_model"],
                icon=data.get("icon"),
                description=data.get("description")
            )
            db.add(provider)
    
    db.commit()


@router.get("", response_model=SettingsResponse)
async def get_settings(db: Session = Depends(get_db)):
    _init_providers(db)
    settings = _get_or_create_settings(db)
    return settings.to_dict()


@router.put("/ui", response_model=SettingsResponse)
async def update_ui_settings(
    request: UISettingsRequest,
    db: Session = Depends(get_db)
):
    settings = _get_or_create_settings(db)
    
    if request.style:
        settings.ui_style = request.style
    if request.primary_color:
        settings.ui_primary_color = request.primary_color
    if request.font_size:
        settings.ui_font_size = request.font_size
    if request.dark_mode is not None:
        settings.ui_dark_mode = request.dark_mode
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return settings.to_dict()


@router.put("/ai", response_model=SettingsResponse)
async def update_ai_settings(
    request: AISettingsRequest,
    db: Session = Depends(get_db)
):
    settings = _get_or_create_settings(db)
    
    if request.provider:
        provider = db.query(AIProvider).filter(AIProvider.name == request.provider).first()
        if provider:
            settings.ai_provider = request.provider
            settings.ai_base_url = provider.base_url
            if not request.model:
                settings.ai_model = provider.default_model
    
    if request.api_key is not None:
        encrypted_key = encrypt_value(request.api_key)
        settings.ai_api_key = encrypted_key
    
    if request.base_url:
        settings.ai_base_url = request.base_url
    
    if request.model:
        settings.ai_model = request.model
    
    if request.temperature is not None:
        settings.ai_temperature = str(request.temperature)
    
    if request.max_tokens is not None:
        settings.ai_max_tokens = request.max_tokens
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return settings.to_dict()


@router.get("/providers", response_model=List[ProviderResponse])
async def get_providers(db: Session = Depends(get_db)):
    _init_providers(db)
    
    providers = db.query(AIProvider).all()
    
    result = []
    for p in providers:
        models = json.loads(p.models) if p.models else []
        result.append(ProviderResponse(
            name=p.name,
            display_name=p.display_name,
            base_url=p.base_url,
            models=[ProviderModel(**m) for m in models],
            default_model=p.default_model,
            icon=p.icon,
            description=p.description
        ))
    
    return result


@router.get("/providers/{provider_name}/models", response_model=List[ProviderModel])
async def get_provider_models(
    provider_name: str,
    db: Session = Depends(get_db)
):
    provider = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="提供商不存在")
    
    models = json.loads(provider.models) if provider.models else []
    return [ProviderModel(**m) for m in models]


@router.get("/providers/{provider_name}/available-models")
async def get_available_models(
    provider_name: str,
    db: Session = Depends(get_db)
):
    """动态获取用户账号下可用的模型列表"""
    import httpx
    
    settings = _get_or_create_settings(db)
    
    provider = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    if not provider:
        raise HTTPException(status_code=404, detail="提供商不存在")
    
    if not settings.ai_api_key:
        return {
            "success": False,
            "message": "请先设置API密钥",
            "models": []
        }
    
    api_key = decrypt_value(settings.ai_api_key) if is_encrypted(settings.ai_api_key) else settings.ai_api_key
    
    try:
        async with httpx.AsyncClient() as client:
            if provider_name == "siliconflow":
                response = await client.get(
                    "https://api.siliconflow.cn/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={"type": "text"},
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        model_name = model_id.split("/")[-1] if "/" in model_id else model_id
                        models.append({
                            "id": model_id,
                            "name": model_name,
                            "description": model.get("owned_by", "SiliconFlow")
                        })
                    models.sort(key=lambda x: x["name"])
                    return {
                        "success": True,
                        "models": models,
                        "count": len(models)
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API返回错误: {response.status_code}",
                        "models": []
                    }
            
            elif provider_name == "openai":
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        if model_id.startswith("gpt"):
                            models.append({
                                "id": model_id,
                                "name": model_id,
                                "description": model.get("owned_by", "OpenAI")
                            })
                    return {
                        "success": True,
                        "models": models
                    }
            
            elif provider_name == "deepseek":
                response = await client.get(
                    "https://api.deepseek.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model in data.get("data", []):
                        models.append({
                            "id": model.get("id"),
                            "name": model.get("id"),
                            "description": model.get("owned_by", "DeepSeek")
                        })
                    return {
                        "success": True,
                        "models": models
                    }
            
            elif provider_name == "zhipu":
                return {
                    "success": True,
                    "models": [
                        {"id": "glm-4-plus", "name": "GLM-4 Plus", "description": "智谱最新旗舰模型"},
                        {"id": "glm-4-0520", "name": "GLM-4", "description": "智谱通用模型"},
                        {"id": "glm-3-turbo", "name": "GLM-3 Turbo", "description": "快速经济模型"}
                    ]
                }
            
            return {
                "success": False,
                "message": "不支持的提供商",
                "models": []
            }
            
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": "请求超时，请检查网络连接",
            "models": []
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取模型列表失败: {str(e)}",
            "models": []
        }


@router.get("/styles", response_model=List[Dict])
async def get_ui_styles():
    """获取可用的UI风格列表"""
    return [
        {
            "id": "bloomberg-dark",
            "name": "Bloomberg终端",
            "description": "极简暗色调、等宽字体、橙绿配色、专业金融风格",
            "preview": {
                "primary_color": "#ff6600",
                "background": "#000000",
                "card_style": "bg-black border border-gray-900 font-mono"
            }
        },
        {
            "id": "modern-light",
            "name": "现代专业",
            "description": "简洁明亮、专业配色、清晰层次",
            "preview": {
                "primary_color": "#2563eb",
                "background": "#f8fafc",
                "card_style": "bg-white shadow-md rounded-lg"
            }
        }
    ]


@router.get("/colors", response_model=List[Dict])
async def get_color_palettes():
    """获取可用的颜色方案"""
    return [
        {"id": "#3b82f6", "name": "蓝色", "description": "专业、可信赖"},
        {"id": "#8b5cf6", "name": "紫色", "description": "创意、优雅"},
        {"id": "#10b981", "name": "绿色", "description": "自然、健康"},
        {"id": "#f59e0b", "name": "橙色", "description": "活力、热情"},
        {"id": "#ef4444", "name": "红色", "description": "激情、重要"},
        {"id": "#06b6d4", "name": "青色", "description": "清新、科技"},
        {"id": "#ec4899", "name": "粉色", "description": "温柔、浪漫"},
        {"id": "#6366f1", "name": "靛蓝", "description": "智慧、深邃"}
    ]
