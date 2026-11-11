"""
GHOST Configuration Module
Loads operational parameters, security profiles, and AI model configurations.
"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GhostSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Operational Identity
    callsign: str = Field(default="GHOST", alias="GHOST_CALLSIGN")
    operator_name: str = Field(default="Sir", alias="GHOST_OPERATOR_NAME")
    security_level: str = Field(default="DEFCON_3", alias="GHOST_SECURITY_LEVEL")

    # API Keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    # Model Profiles
    claude_model: str = Field(default="claude-3-7-sonnet-20250219", alias="CLAUDE_MODEL")
    gemini_model: str = Field(default="gemini-3.1-flash-lite", alias="GEMINI_MODEL")

    # Network & Gateway Server
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8080, alias="PORT")
    gateway_secret: str = Field(default="ghost_alpha_clearance", alias="GHOST_GATEWAY_SECRET")

    # Paths & Storage
    base_dir: Path = Path(__file__).resolve().parent
    database_path: Path = base_dir / "database" / "ghost.db"
    log_dir: Path = base_dir / "logs"

    # Execution Permissions
    default_permission_level: str = Field(default="LEVEL_2_EXECUTE", alias="DEFAULT_PERMISSION_LEVEL")
    require_confirmation_level_3: bool = Field(default=True, alias="REQUIRE_CONFIRMATION_LEVEL_3")

    # Voice & Audio
    wake_word: str = Field(default="ghost", alias="WAKE_WORD")
    tts_engine: str = Field(default="edge-tts", alias="TTS_ENGINE")
    stt_engine: str = Field(default="faster-whisper", alias="STT_ENGINE")
    voice_name: str = Field(default="en-US-ChristopherNeural", alias="VOICE_NAME")

    # Multi-Device Integration
    windows_agent_enabled: bool = Field(default=True, alias="WINDOWS_AGENT_ENABLED")
    android_gateway_enabled: bool = Field(default=True, alias="ANDROID_GATEWAY_ENABLED")


settings = GhostSettings()

# Ensure critical directories exist
settings.database_path.parent.mkdir(parents=True, exist_ok=True)
settings.log_dir.mkdir(parents=True, exist_ok=True)

