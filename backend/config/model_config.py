"""Model configuration - 模型配置

统一管理所有 Agent 使用的模型配置。
修改此文件即可切换所有 Agent 使用的模型。

对于 GPT-5 模型，SDK 会自动设置 reasoning.effort="low" 和 verbosity="low"。
如果想要更低延迟，可以使用 reasoning.effort="minimal"（但某些工具不支持）。
"""

from agents import ModelSettings

try:
    from openai.types.shared import Reasoning
    from agents.models import get_default_model_settings
    HAS_REASONING_SUPPORT = True
    HAS_GET_DEFAULT_MODEL_SETTINGS = True
except ImportError:
    HAS_REASONING_SUPPORT = False
    HAS_GET_DEFAULT_MODEL_SETTINGS = False
    Reasoning = None


# 默认模型配置 - 所有 Agent 默认使用此模型
DEFAULT_MODEL = "gpt-5-mini-2025-08-07"

# Reasoning effort 配置
# - "low": 默认设置，平衡质量和速度（推荐用于大多数场景）
# - "minimal": 最低延迟，但某些工具（如文件搜索、图像生成）不支持
# 注意：某些模型（如 gpt-5-mini）不支持 reasoning.effort 参数
REASONING_EFFORT = "low"  # 可选: "low" 或 "minimal"

# Verbosity 配置
# - "low": 默认设置，输出简洁
# - "medium": 中等详细程度
# - "high": 高详细程度
VERBOSITY = "low"  # 可选: "low", "medium", "high"

# 不支持 reasoning.effort 的模型列表
# 这些模型将只使用 verbosity，不设置 reasoning.effort
MODELS_WITHOUT_REASONING = [
    "gpt-5-mini-2025-08-07",
    "gpt-5-mini",
]

# 模型特定的 verbosity 配置
# 某些模型只支持特定的 verbosity 值
MODEL_VERBOSITY_CONFIG = {
    # GPT-4.1 系列只支持 "medium"
    "gpt-4.1": "medium",
    "gpt-4.1-2025-04-14": "medium",
    # GPT-5 系列支持 "low", "medium", "high"
    "gpt-5": "low",
    "gpt-5-mini": "low",
    "gpt-5-mini-2025-08-07": "low",
}

# 模型配置字典 - 可以为不同类型的 Agent 配置不同的模型
MODEL_CONFIG = {
    # 默认模型（所有 Agent 使用）
    "default": DEFAULT_MODEL,
    
    # 可以为特定类型的 Agent 配置不同的模型
    # "top_level": "gpt-5-mini-2025-08-07",
    # "master": "gpt-5-mini-2025-08-07",
    # "notebook": "gpt-5-mini-2025-08-07",
    # "specialized": "gpt-5-mini-2025-08-07",
}


def get_model_settings(model_name: str = None, reasoning_effort: str = None, verbosity: str = None) -> ModelSettings:
    """
    获取模型设置
    
    Args:
        model_name: 模型名称，如果为 None 则使用默认模型
        reasoning_effort: Reasoning effort ("low" 或 "minimal")，如果为 None 则使用默认配置
        verbosity: Verbosity ("low", "medium", "high")，如果为 None 则使用默认配置
        
    Returns:
        ModelSettings 对象
    """
    if model_name is None:
        model_name = MODEL_CONFIG.get("default", DEFAULT_MODEL)
    
    # Debug: Print model being used
    print(f"[model_config.get_model_settings] 使用模型: {model_name} (DEFAULT_MODEL={DEFAULT_MODEL}, MODEL_CONFIG.default={MODEL_CONFIG.get('default', 'N/A')})")
    
    # 检查模型是否支持 reasoning.effort
    supports_reasoning = (
        HAS_REASONING_SUPPORT and 
        model_name.startswith("gpt-5") and 
        model_name not in MODELS_WITHOUT_REASONING
    )
    
    # 如果提供了自定义的 verbosity，则使用；否则根据模型类型选择合适的 verbosity
    if verbosity is None:
        # 检查模型是否有特定的 verbosity 配置
        verbosity = _get_model_verbosity(model_name)
    
    # 对于支持 reasoning 的模型，尝试设置 reasoning.effort
    if supports_reasoning:
        try:
            # 如果提供了自定义的 reasoning_effort，则使用；否则使用默认配置
            if reasoning_effort is None:
                reasoning_effort = REASONING_EFFORT
            
            # 构建 ModelSettings（包含 reasoning）
            # 注意：ModelSettings 不接受 model 参数，模型名称通过 Agent 的 model 参数传递
            if reasoning_effort:
                return ModelSettings(
                    reasoning=Reasoning(effort=reasoning_effort),
                    verbosity=verbosity
                )
            else:
                return ModelSettings(
                    verbosity=verbosity
                )
        except Exception as e:
            # 如果构建失败（例如模型不支持 reasoning），回退到只使用 verbosity
            print(f"[model_config] 模型 {model_name} 不支持 reasoning.effort，回退到基本设置: {e}")
            return ModelSettings(
                verbosity=verbosity
            )
    
    # 对于不支持 reasoning 的模型，只使用 verbosity
    # 确保 verbosity 已根据模型类型设置
    if verbosity is None:
        verbosity = _get_model_verbosity(model_name)
    
    # ModelSettings 不接受 model 参数，模型名称应该直接传递给 Agent 的 __init__
    # ModelSettings 只用于设置 verbosity 和 reasoning 等参数
    if verbosity:
        return ModelSettings(verbosity=verbosity)
    
    # 如果没有 verbosity，返回空的 ModelSettings（模型名称通过 Agent 的 model 参数传递）
    return ModelSettings()


def _get_model_verbosity(model_name: str) -> str:
    """
    根据模型名称获取合适的 verbosity 值
    
    Args:
        model_name: 模型名称
        
    Returns:
        verbosity 值
    """
    # 检查是否有精确匹配
    if model_name in MODEL_VERBOSITY_CONFIG:
        return MODEL_VERBOSITY_CONFIG[model_name]
    
    # 检查是否有前缀匹配（例如 gpt-4.1 匹配所有 gpt-4.1-* 模型）
    for model_prefix, verbosity_value in MODEL_VERBOSITY_CONFIG.items():
        if model_name.startswith(model_prefix + "-") or model_name == model_prefix:
            return verbosity_value
    
    # 默认使用配置的 verbosity
    return VERBOSITY


def get_model_name() -> str:
    """
    获取默认模型名称（用于直接传递 model 参数）
    
    Returns:
        默认模型名称字符串
    """
    return MODEL_CONFIG.get("default", DEFAULT_MODEL)


def get_section_maker_model_settings() -> ModelSettings:
    """
    获取 Section Maker 专用的模型设置（使用 minimal reasoning effort 以降低延迟）
    
    Returns:
        ModelSettings 对象，使用 minimal reasoning effort（如果模型支持）
    """
    model_name = MODEL_CONFIG.get("default", DEFAULT_MODEL)
    
    # 检查模型是否支持 reasoning.effort
    supports_reasoning = (
        HAS_REASONING_SUPPORT and 
        model_name.startswith("gpt-5") and 
        model_name not in MODELS_WITHOUT_REASONING
    )
    
    if supports_reasoning:
        try:
            # Section maker 使用 minimal reasoning effort 以降低延迟
            return ModelSettings(
                reasoning=Reasoning(effort="minimal"),
                verbosity="low"
            )
        except Exception as e:
            # 如果设置失败（例如模型不支持 minimal），回退到基本设置
            print(f"[model_config] Section maker: 模型 {model_name} 不支持 minimal reasoning.effort，回退到基本设置: {e}")
            return ModelSettings(
                verbosity="low"
            )
    
    # 对于不支持 reasoning 的模型，只使用 verbosity
    # 根据模型类型选择合适的 verbosity
    verbosity = _get_model_verbosity(model_name)
    return ModelSettings(
        verbosity=verbosity
    )


def get_default_model() -> str:
    """
    获取默认模型名称
    
    Returns:
        默认模型名称字符串
    """
    return MODEL_CONFIG.get("default", DEFAULT_MODEL)

