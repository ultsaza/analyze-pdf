import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
import os

class GeminiDocumentAnalyzer:
    def __init__(
            self, 
            api_key=None, 
            model_name="gemini-2.0-flash", 
            temperature=0, 
            top_p=0.95, 
            top_k=40, 
            max_output_tokens=8192,
            response_mime_type="application/json"
        ):

        load_dotenv()
        # NOTE: .envファイルを作成して GENAI_API_KEY=... の形式で環境変数を設定してください
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": response_mime_type,
            },
        )
        
        self.chat_session = None
        self.files = []

    def upload_file(self, path, mime_type=None):
        """
        Upload a file to Gemini API.
        """
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        self.files.append(file)
        return file

    def wait_for_files_active(self):
        """Wait for all uploaded files to be processed."""
        print("Waiting for file processing...")
        for name in (file.name for file in self.files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")
        print("...all files ready")
        print()

    def initialize_chat(self):
        """Initialize a chat session with uploaded files."""
        if not self.files:
            raise ValueError("No files have been uploaded yet")
            
        self.chat_session = self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": self.files,
                }
            ]
        )

    def analyze_statement(self, custom_prompt=None, output_structure=None):
        """
        Analyze the uploaded statement with a custom prompt and output structure.
        
        Args:
            custom_prompt (str, optional): Custom prompt to analyze the document.
            output_structure (dict, optional): Structure specification for the output.
        """
        if not self.chat_session:
            raise ValueError("Chat session not initialized. Call initialize_chat() first")
        
        # Default prompt if none provided
        default_prompt = """
        prompt
        """
        
        prompt = custom_prompt if custom_prompt else default_prompt
        
        # Add output structure specification if provided
        if output_structure:
            structure_prompt = f"\n出力は以下の構造に従ってください: {output_structure}"
            prompt += structure_prompt
        
        response = self.chat_session.send_message(prompt)
        return response.text

    def reset(self):
        """Reset file list and chat session."""
        self.files = []
        self.chat_session = None

    def process_documents(self, file_paths, mime_type="application/pdf", custom_prompt=None, output_structure=None):
        """
        Process multiple documents in one go with optional custom prompt and output structure.
        
        Args:
            file_paths (list): List of file paths to process
            mime_type (str, optional): MIME type of the files. Defaults to "application/pdf".
            custom_prompt (str, optional): Custom prompt to analyze the document.
            output_structure (dict/str, optional): Structure specification for the output.
        """
        # Reset previous state to avoid data contamination
        self.reset()
        
        # Upload all files
        for path in file_paths:
            self.upload_file(path, mime_type=mime_type)
        
        # Wait for processing
        self.wait_for_files_active()
        
        # Initialize chat
        self.initialize_chat()
        
        # Return analysis with custom prompt and structure if provided
        return self.analyze_statement(custom_prompt, output_structure)
