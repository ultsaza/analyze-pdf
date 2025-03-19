import os
import time
import threading

class RateLimiter:
    def __init__(self, min_interval):
        self.min_interval = min_interval
        self.lock = threading.Lock()
        self.last_time = 0

    def wait(self):
        with self.lock:
            now = time.time()
            wait_time = self.min_interval - (now - self.last_time)
            if wait_time > 0:
                time.sleep(wait_time)
            self.last_time = time.time()

class InvoiceExtractor:
    def __init__(self, model, rate_limiter):
        self.model = model
        self.rate_limiter = rate_limiter

    def extract_invoice_data(self, pdf_path):
        print(f"Processing PDF: {pdf_path}")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        with open(pdf_path, "rb") as f:
            file_bytes = f.read()
        prompt = [
            {"mime_type": "application/pdf", "data": file_bytes},
            {"text": """
             Extract all structured invoice data from each page.
             Output the results as a JSON array, where each element represents one page.
             Do not include any explanations; output only valid JSON.
             The output must be in Japanese and monetary values should include their units.
            """},
        ]
        # Wait before making the API call.
        self.rate_limiter.wait()
        response_stream = self.model.generate_content(prompt, stream=True)
        full_text = "".join(token.text for token in response_stream)
        return {"filename": base_name, "data": full_text}