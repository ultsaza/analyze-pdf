import json

DESIRED_COLUMNS = {
    'N番号': 'n_number',
    '企業名': 'compnay_name',
    '供給地点番号': 'supply_point_identification_number',
    '契約種別': 'contract_type',
    '見積提出会社': 'quotation_submission_company',
    'プラン名': 'plan_name',
    '都道府県': 'prefecture',
    '市区町村': 'city',
    '請求書発行日': 'invoice_issue_date',
    '請求金額': 'billing_amount',
    '電力使用量': 'electricity_usage',
    '基本料金単価': 'basic_unit_price',
    '燃料費調整額': 'fuel_cost_adjustment',
    '電力調達費': 'power_procurement_cost',
    '再エネ賦課金': 'renewable_energy_surcharge',
    '需給管理費': 'demand_supply_management_cost',
    '使用料料金単価': 'usage_fee_unit_price',
    '夏季使用量料金': 'summer_usage_fee',
    '冬季使用量利用金': 'winter_usage_fee',
    '他季使用量料金': 'other_season_usage_fee',
    '夏季昼間使用量料金': 'summer_daytime_usage_fee',
    '夏季夜間使用量料金': 'summer_late_night_usage_fee',
    '冬季昼間使用量料金': 'winter_daytime_usage_fee',
    '冬季夜間使用量料金': 'winter_late_night_usage_fee',
    '他季昼間使用量料金': 'other_season_daytime_usage_fee',
    '他季夜間使用量料金': 'other_season_late_night_usage_fee',
    'ピーク時使用量料金': 'peak_time_usage_fee',
    '備考': 'remarks',
}

COLUMN_INSTRUCTIONS = {
    "N番号": "Extract the N number if available. This is unique to each invoice and written on the filename inside brackets like 【Nxxxx】 or 【Nxxxx-x】 (x is an integer).",
    "企業名": "Extract the company name (typically fixed across pages). There is always written '様' or '御中' at the end of the company name.",
    "供給地点番号": "Extract the supply point identification number (usually fixed).",
    "契約種別": "Extract the contract type as indicated on the invoice.",
    "見積提出会社": "Extract the quotation submission company, which is typically mentioned on the invoice.",
    "プラン名": "Extract the plan name (usually indicating the electricity billing plan).",
    "都道府県": "Extract the prefecture name from the address field.",
    "市区町村": "Extract the city name from the address field.",
    "請求書発行日": "Extract the invoice issue date in the format 'YYYY年M月D日'.",
    "請求金額": "Extract the billing amount with the currency unit (e.g., '100,000円').",
    "電力使用量": "Extract the electricity usage, typically presented in kWh.",
    "基本料金単価": "Extract the basic unit price in yen.",
    "燃料費調整額": "Extract the fuel cost adjustment amount, including the unit if applicable.",
    "電力調達費": "Extract the power procurement cost, including the unit if applicable.",
    "再エネ賦課金": "Extract the renewable energy surcharge amount, including the unit if applicable.",
    "需給管理費": "Extract the demand supply management cost, including the unit if applicable.",
    "使用料料金単価": "Extract the usage fee unit price in yen per kWh.",
    "夏季使用量料金": "Extract the overall summer usage fee, including the unit if applicable.",
    "冬季使用量利用金": "Extract the overall winter usage fee, including the unit if applicable.",
    "他季使用量料金": "Extract the overall other season usage fee, including the unit if applicable.",
    "夏季昼間使用量料金": "Extract the summer daytime usage fee, including the unit if applicable.",
    "夏季夜間使用量料金": "Extract the summer nighttime usage fee, including the unit if applicable.",
    "冬季昼間使用量料金": "Extract the winter daytime usage fee, including the unit if applicable.",
    "冬季夜間使用量料金": "Extract the winter nighttime usage fee, including the unit if applicable.",
    "他季昼間使用量料金": "Extract the other season daytime usage fee, including the unit if applicable.",
    "他季夜間使用量料金": "Extract the other season nighttime usage fee, including the unit if applicable.",
    "ピーク時使用量料金": "Extract the peak time usage fee, including the necessary unit.",
    "備考": "Extract any remarks if present."
}

MAX_RAW_LENGTH = 1000000

def clean_json_output(raw_text):
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text

class ColumnMatcher:
    def __init__(self, llm_model):
        self.llm_model = llm_model
        self.desired_columns = DESIRED_COLUMNS
        self.column_instructions = COLUMN_INSTRUCTIONS

    def match_columns(self, raw_json):
        if not raw_json.strip():
            return json.dumps({key: None for key in self.desired_columns})
        
        truncated_raw = (raw_json if len(raw_json) <= MAX_RAW_LENGTH 
                         else raw_json[:MAX_RAW_LENGTH] + "\n...[truncated]")
        
        instructions_lines = []
        for key in self.desired_columns.keys():
            instruction = self.column_instructions.get(key, "No instruction provided.")
            instructions_lines.append(f'- "{key}": {instruction}')
        instructions = "\n".join(instructions_lines)
        
        desired_keys = list(self.desired_columns.keys())
        prompt_text = f"""
        The following is structured JSON data extracted from a PDF file. It is a JSON array where each element represents the data extracted from one page of the document.

        Please extract data for the desired columns according to the following instructions.
        Important: Make sure to include data from every page (for example, one full year of data from December to November) without omitting any values.

        For each desired column, follow these instructions:
        {instructions}

        For each desired column:
        - If the value is identical across all pages, output that single value.
        - If the value differs among pages, output an array of all unique values.
        - If a column is not found in any page, output null for that column.

        Output only a pure JSON object with exactly the following keys:
        {', '.join('"' + key + '"' for key in desired_keys)}.

        Structured JSON Data (may be truncated):
        {truncated_raw}
        """
        prompt = [{"text": prompt_text}]
        response_stream = self.llm_model.generate_content(prompt, stream=True)
        
        result_text = "".join(token.text for token in response_stream).strip()
        cleaned_text = clean_json_output(result_text)
        if not cleaned_text:
            return json.dumps({key: None for key in self.desired_columns})
        return cleaned_text