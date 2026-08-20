from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from src.extractor import extract_financial_info

app = FastAPI(
    title="Financial Ticket Parser AI Engine",
    description="سرویس هوشمند استخراج اطلاعات مالی تیکت‌های پشتیبانی فارسی و انگلیسی",
    version="1.0.0"
)

class MessageInput(BaseModel):
    sender: str = Field(..., description="فرستنده پیام: customer یا agent")
    text: str = Field(..., description="متن پیام تیکت")
    time: Optional[str] = Field(None, description="زمان ارسال پیام")

class TicketRequest(BaseModel):
    id: Optional[str] = Field(None, description="شناسه تیکت")
    userId: Optional[str] = Field(None, description="شناسه کاربر")
    ticketPostedTime: Optional[str] = Field(None, description="تاریخ و زمان ثبت تیکت")
    messages: List[MessageInput] = Field(..., description="لیست پیام‌های تیکت")

class FinancialOutput(BaseModel):
    amount_toman: Optional[int] = Field(None, description="مبلغ به تومان")
    time: Optional[str] = Field(None, description="ساعت واریز به فرمت HH:MM 24h")
    date: Optional[str] = Field(None, description="تاریخ واریز به شمسی")
    source_card: Optional[str] = Field(None, description="شماره کارت ۱۶ رقمی مبدا")
    destination_card: Optional[str] = Field(None, description="شماره کارت ۱۶ رقمی مقصد")
    destination_holder_name: Optional[str] = Field(None, description="نام صاحب کارت مقصد")
    gateway: str = Field(..., description="نوع درگاه: شاپرک / کاسپین / کارت‌به‌کارت / نامشخص")
    deposit_type: str = Field(..., description="نوع واریزی")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Financial Ticket Parser AI Engine",
        "version": "1.0.0"
    }

@app.post("/api/v1/extract", response_model=FinancialOutput)
def extract_ticket_data(request: TicketRequest):
    try:
        msgs = [msg.model_dump() for msg in request.messages]
        result = extract_financial_info(msgs, ticket_posted_time=request.ticketPostedTime)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
