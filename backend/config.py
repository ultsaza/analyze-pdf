import os
from dotenv import load_dotenv

def setGeminiAPI():
    # Load environment variables from .env file
    load_dotenv()

    # Get the API key from the environment variable
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set in .env file.")
    return API_KEY

def setModel():
    load_dotenv()
    # Get the model ID from the environment variable
    model_id = os.environ.get("model_id")
    return model_id

def setDirectory():
    # config.py がある src/ フォルダから見て、一つ上 (../) の階層にあるテスト明細フォルダーへ行く
    base_dir = os.path.dirname(__file__)            # src/ の絶対パスを取得
    parent_dir = os.path.join(base_dir, '..')       # src/ の上位フォルダ
    target_dir = os.path.join(parent_dir, 'テスト明細フォルダー') 
    return os.path.abspath(target_dir)

def setOutputDirectory():
    # config.py がある src/ フォルダから見て、一つ上 (../) の階層にある出力フォルダーへ行く
    base_dir = os.path.dirname(__file__)            # src/ の絶対パスを取得
    parent_dir = os.path.join(base_dir, '..')       # src/ の上位フォルダ
    target_dir = os.path.join(parent_dir, '出力フォルダー') 
    return os.path.abspath(target_dir)