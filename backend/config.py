import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "AegisChain Supply Intelligence"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # RPC and Web3 Config
    WEB3_PROVIDER_URL: str = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    
    # AI Engine Settings
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    TEMP_THRESHOLD_MAX: float = 8.0  # Cold chain upper boundary (°C)
    TEMP_THRESHOLD_MIN: float = 2.0  # Cold chain lower boundary (°C)

settings = Settings()