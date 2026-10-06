from __future__ import annotations
import os,requests
from dotenv import load_dotenv
from exceptions import ExternalServiceError
load_dotenv()
class ExchangeRateService:
    def __init__(self,url=None): self.url=url or os.getenv("EXCHANGE_API_URL","https://open.er-api.com/v6/latest/USD")
    def get_usd_ngn_rate(self):
        try:
            r=requests.get(self.url,timeout=10); r.raise_for_status(); d=r.json()
            return {"rate":float(d["rates"]["NGN"]),"updated_at":d.get("time_last_update_utc","Unknown"),"base":d.get("base_code","USD")}
        except (requests.RequestException,ValueError,KeyError) as e: raise ExternalServiceError(f"Exchange-rate service failed: {e}") from e
class GeminiService:
    def __init__(self,api_key=None,model=None):
        self.api_key=api_key or os.getenv("GEMINI_API_KEY"); self.model=model or os.getenv("GEMINI_MODEL","gemini-3.8-flash"); self._client=None
        if self.api_key:
            try:
                from google import genai
                self._client=genai.Client(api_key=self.api_key)
            except Exception: self._client=None
    @property
    def available(self): return self._client is not None
    def get_advice(self,*,state,balance,spent,category_rows,ppa):
        if not self._client: return self._fallback_advice(state,balance,spent,category_rows)
        summary=", ".join(f"{r['Category']}: ₦{r['Spent']:,.0f}/₦{r['Limit']:,.0f}" for r in category_rows)
        prompt=f"You are AllaweeBot, a conservative budgeting copilot for an NYSC corps member in Nigeria. State: {state}. PPA: {ppa or 'Not provided'}. Allowance: ₦{spent+balance:,.2f}. Spent: ₦{spent:,.2f}. Remaining: ₦{balance:,.2f}. Category usage: {summary}. Give a brief status, three actions, and one warning in under 180 words."
        try:
            response=self._client.models.generate_content(model=self.model,contents=prompt)
            return response.text or self._fallback_advice(state,balance,spent,category_rows)
        except Exception: return self._fallback_advice(state,balance,spent,category_rows)
    @staticmethod
    def _fallback_advice(state,balance,spent,category_rows):
        highest=max(category_rows,key=lambda r:r["Used %"]) if category_rows else None
        status="Your spending is above the monthly allowance." if balance<0 else "Your remaining balance is getting tight." if balance<.2*(spent+balance) else "Your remaining balance is still manageable."
        warning=f"Watch {highest['Category']}: it has used {highest['Used %']:.0f}% of its category limit." if highest else "Review each category limit before another expense."
        return f"**Financial status ({state}):** {status} You have ₦{balance:,.0f} left after ₦{spent:,.0f} spent.\n\n**Three actions:**\n1. Protect transport and food money.\n2. Log every purchase immediately.\n3. Reserve what you safely can for Savings.\n\n**Warning:** {warning}"
