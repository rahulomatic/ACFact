import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    
    # Directories
    OUTPUTS_DIR = "outputs"
    LOGS_DIR = "logs"
    
    @classmethod
    def validate(cls):
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        return True