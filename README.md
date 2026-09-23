# Persian Prompt Compiler (Prompt Engine)
> **مترجم و کامپایلر هوشمند پرامپت فارسی به انگلیسی برای مدل‌ها و ایجنت‌های هوش مصنوعی**  
> *Transform natural Persian/Farsi requests into production-grade, executable, anti-hallucinated English prompts for AI coding agents and LLMs.*

---

## 🌐 زبان‌ها / Languages
- [English](#-english-documentation)
- [فارسی (Persian)](#-مستندات-فارسی)

---

# 🇬🇧 English Documentation

## 1. Project Overview

**Persian Prompt Compiler** (Prompt Engine) is an enterprise-grade prompt compilation service and web application built with **FastAPI** and integrated with **Google AI Studio (Gemini)**. 

### Why a "Compiler" and not a "Translator"?
Traditional translation tools convert words literally from Persian to English. When prompting AI coding agents (such as Claude Code, OpenCode, Codex) or large language models (ChatGPT, Gemini, Claude), literal translations frequently result in:
- Missed architectural nuances and vague requirements.
- Hallucinated stacks (e.g., asking for a "simple web app" and having the model inject Docker, PostgreSQL, Redis, and React without consent).
- Loss of explicit negative constraints (e.g., weakening "Do not use PostgreSQL" to "PostgreSQL is not preferred").
- Disconnect between English and Persian specifications.

**Persian Prompt Compiler** solves this by treating prompt generation as a **strict compilation pipeline**:
```text
Persian User Input ──► [Intent Analysis & Classification]
                             │
                             ▼
                     [Canonical english_prompt]  (Single Source of Truth)
                             │
                             ├──────────────► [Faithful persian_prompt Translation]
                             ├──────────────► [Preserved Requirements]
                             ├──────────────► [Assumptions & Missing Info]
                             └──────────────► [Optional Suggestions]
```
The finalized English prompt serves as the canonical baseline. The Persian prompt is translated strictly from the finalized English version, guaranteeing identical scope, structure, constraints, and semantics across both languages.

---

## 2. Features & Problem Solved

### Core Features

- **Strict Requirement Integrity (Zero Hallucination Policy)**:
  - Never fabricates dependencies, frameworks, libraries, databases, or deployment options.
  - If information is missing (e.g. asking for "an e-commerce site" without a stack), it explicitly records the gap under `missing_information` rather than guessing.
- **Negative Constraints Enforcement**:
  - Hard prohibitions (e.g. *"Do not use Docker"*, *"No external CSS frameworks"*) are strictly preserved at full strength in both English and Persian outputs.
- **Requirement Classification**:
  - `preserved_requirements`: What the user explicitly stated or unambiguously implied.
  - `assumptions`: Only assumptions strictly necessary to formulate the prompt.
  - `missing_information`: Critical missing inputs that affect execution.
  - `suggestions`: Optional enhancements, kept strictly outside the prompt body.
- **Categorization & Subcategorization**:
  - Automatic detection of 10 intent categories: `coding`, `debugging`, `research`, `writing`, `image_generation`, `translation`, `data_analysis`, `planning`, `automation`, and `general`.
- **Proportionality Rule**:
  - Output length and detail correspond to the input complexity. Simple text edits produce concise, punchy instructions; complex architectures produce thorough, structured prompts.
- **Gemini Model Catalog & Quota Tracking**:
  - Comprehensive model catalog (`gemini-3.5-flash`, `gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-pro`, etc.).
  - Real-time token usage analytics (Input, Output, Thought tokens) and rolling limits: **RPD** (Requests Per Day), **TPM** (Tokens Per Minute), and **RPM** (Requests Per Minute) with alert indicators.
- **1-Click Agent Integration**:
  - Direct copy-to-clipboard workflows tailored for **Claude Code** and **OpenCode** CLI environments.
- **Modern RTL Web Interface**:
  - Clean, dark-mode dashboard tailored for Persian typography with the embedded Vazirmatn font family.

---

## 3. Project Structure

```text
.
├── prompt_compiler/
│   ├── api/
│   │   └── routes/
│   │       ├── models.py          # GET /models - Gemini catalog metadata
│   │       ├── pages.py           # GET / - Web UI template rendering
│   │       ├── settings.py        # POST /settings - Update config & API key
│   │       ├── translation.py     # POST /translate - Core compilation endpoint
│   │       └── usage.py           # GET /usage - Token and quota telemetry
│   ├── services/
│   │   ├── gemini.py              # Google AI Studio HTTP client (httpx)
│   │   └── usage.py               # Local token tracking & metrics aggregation
│   ├── app.py                     # FastAPI application factory
│   ├── catalog.py                 # Model definitions, rate limits & categories
│   ├── config.py                  # Path management & config.json persistence
│   └── prompt_engine.py           # System policy prompt & response parser
├── static/
│   ├── fonts/                     # Vazirmatn font assets
│   ├── style.css                  # UI styling & responsive dark theme
│   └── script.js                  # Frontend state, API client, & dashboard
├── templates/
│   └── index.html                 # Main Jinja2 application template
├── tests/
│   └── test_prompt_engine.py      # 48-case comprehensive test suite
├── config.json                    # Local configuration (API key, default model)
├── usage.json                     # Rolling 7-day token usage events
├── main.py                        # Alternative entry point
├── requirements.txt               # Python package dependencies
├── run.bat                        # Windows 1-click execution script
└── README.md                      # Project documentation
```

---

## 4. Installation & Setup

### Prerequisites
- **Python 3.10** or higher.
- A **Google AI Studio API Key** (Get one for free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).
- Direct network access to `generativelanguage.googleapis.com`.

### Method A: Automated Start (Windows)
Double-click `run.bat` or run:
```cmd
run.bat
```
*This script automatically creates a `.venv` virtual environment if absent, installs/updates dependencies from `requirements.txt`, and boots the server.*

---

### Method B: Manual Setup (Cross-Platform)

#### 1. Clone or Navigate to the Workspace
```bash
cd /path/to/project
```

#### 2. Create and Activate a Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Run the Application
You can run either with Uvicorn directly:
```bash
python -m uvicorn prompt_compiler.app:app --host 0.0.0.0 --port 8000 --reload
```
Or via the entrypoint script:
```bash
python main.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## 5. Configuration

1. Open the web interface at `http://127.0.0.1:8000`.
2. Click **تنظیمات (Settings)** in the top navigation bar.
3. Enter your **Google AI Studio API Key**.
4. Select your preferred default model (e.g., `Gemini 3.5 Flash`).
5. (Optional) Provide a **System Prompt Override** if you want custom instructions.
6. Click **ذخیره تنظیمات (Save Settings)**.

Configuration values are safely saved in `config.json`:
```json
{
  "gemini_api_key": "AIzaSy...",
  "gemini_model": "gemini-3.5-flash",
  "system_prompt_override": ""
}
```
> [!WARNING]
> Never commit `config.json` containing your production API key to public source repositories. It is included in `.gitignore`.

---

## 6. Usage Guide

### 1. Generating a Prompt
1. Type or paste your prompt in colloquial or technical Persian into the text area.
   *Example:*
   ```text
   یه وب‌سایت مدیریت کارها با پایتون و دیتابیس SQLite بساز. کاربران بتونن تسک اضافه، ویرایش و حذف کنن. از فریم‌ورک فرانت‌اند سنگین جاوااسکریپتی استفاده نکن.
   ```
2. Select your desired Gemini model from the dropdown.
3. Click **تبدیل کن (Compile)**.

### 2. Inspecting Results
- **Category & Purpose**: Shows the detected task category (e.g. `💻 برنامه‌نویسی / web_development`) and purpose summary.
- **Dual Outputs**:
  - **English Prompt**: Canonical, highly structured prompt optimized for AI agents.
  - **Persian Prompt**: 100% faithful Persian counterpart matching the English structure and constraints.
- **Analysis Cards**:
  - **Preserved Requirements**: All detected hard requirements.
  - **Assumptions**: Implicit context identified by the compiler.
  - **Missing Information**: Critical details not provided by the user.
  - **Suggestions**: Optional enhancements that do not pollute the core prompt.

### 3. Copying & Agent Handoff
- Click **کپی انگلیسی** or **کپی فارسی** to copy the prompt to your clipboard.
- Click **استفاده در Claude Code** or **استفاده در OpenCode** for a pre-formatted notification prompt ready to paste in your terminal agent.

### 4. Monitoring Token Quotas
Click **مصرف توکن (Token Usage)** in the top bar to inspect:
- Total daily requests and token breakdown (Input, Output, Thought tokens).
- Per-minute rate limits (**RPM**, **TPM**) and daily limits (**RPD**) for the active model.

---

## 7. API Reference

### `POST /translate`
Compiles a Persian prompt into structured English and translated Persian.
- **Request Body**:
  ```json
  {
    "prompt": "یه API ساده برای ثبت لاگ با FastAPI بنویس",
    "model": "gemini-3.5-flash"
  }
  ```
- **Response**:
  ```json
  {
    "result": "...",
    "parsed": {
      "detected_category": "coding",
      "detected_subcategory": "api",
      "detected_purpose": "Build a simple logging API using FastAPI.",
      "english_prompt": "Build a REST API for logging using FastAPI...",
      "persian_prompt": "یک REST API برای ثبت لاگ با FastAPI بساز...",
      "preserved_requirements": ["Use FastAPI", "Logging API"],
      "assumptions": [],
      "missing_information": ["Storage destination for logs"],
      "suggestions": []
    },
    "usage": {
      "promptTokenCount": 540,
      "candidatesTokenCount": 210,
      "totalTokenCount": 750
    },
    "model": "gemini-3.5-flash"
  }
  ```

### `GET /models`
Returns the catalog of Google AI Studio models with rate limits and availability.

### `GET /usage`
Returns token analytics for the current day and active model metrics.

### `POST /settings`
Updates local configuration (`gemini_api_key`, `gemini_model`, `system_prompt_override`).

---

## 8. Testing

The project includes a comprehensive test suite of 48 automated unit tests verifying:
- Prompt policy safeguards and anti-hallucination rules.
- Negative constraint preservation.
- Proportionality enforcement.
- Schema normalization and Markdown JSON stripping.
- Semantic consistency between English and Persian outputs.

Run the test suite with:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---
---

# 🇮🇷 مستندات فارسی

## ۱. نمای کلی پروژه (Project Overview)

پروژه **کامپایلر پرامپت فارسی (Prompt Engine)** یک وب‌اپلیکیشن قدرتمند و مدرن مبتنی بر **FastAPI** است که درخواست‌های غیررسمی، عامیانه یا کوتاه به زبان فارسی را دریافت کرده و به کمک مدل‌های هوش مصنوعی پیشرفته **Google AI Studio (Gemini)**، آن‌ها را به پرامپت‌های انگلیسی ساختاریافته، شفاف، اجرایی و بدون توهم (Anti-Hallucinated) برای ایجنت‌های کدنویسی و مدل‌های زبانی بزرگ تبدیل می‌کند.

### چرا «کامپایلر» و نه یک «مترجم ساده»؟
مترجم‌های معمولی تنها کلمات را به صورت تحت‌اللفظی ترجمه می‌کنند. مدل‌های هوش مصنوعی و به خصوص ایجنت‌های کدنویسی (نظیر Claude Code، OpenCode، Codex و ChatGPT) با پرامپت‌های فارسی ترجمه‌شده با مشکلاتی چون افت کیفیت، ابهام در مفاهیم مهندسی، نادیده گرفتن محدودیت‌ها و از همه مهم‌تر **توهم در تعریف نیازمندی‌ها** مواجه می‌شوند.

کامپایلر پرامپت فارسی فرآیند تولید پرامپت را بر اساس یک **پایپ‌لاین قطعی** انجام می‌دهد:
```text
ورودی کاربر فارسی ──► [درک قصد و دسته‌بندی موضوع]
                           │
                           ▼
                  [پرامپت نهایی انگلیسی] (منبع اصلی حقیقت / Single Source of Truth)
                           │
                           ├──────────────► [ترجمه دقیق به پرامپت فارسی]
                           ├──────────────► [الزامات و نیازمندی‌های حفظ‌شده]
                           ├──────────────► [فرض‌ها و اطلاعات مفقوده]
                           └──────────────► [پیشنهادهای اختیاری]
```
در این معماری، پرامپت انگلیسی منبع اصلی حقیقت (Canonical Baseline) است و پرامپت فارسی نهایی مستقیماً از روی همان پرامپت نهایی انگلیسی ترجمه می‌شود؛ در نتیجه تناقض مفهومی میان دو نسخه به صفر می‌رسد.

---

## ۲. ویژگی‌ها و حل مسئله (Features & Problem Solved)

### چه مشکلی را حل می‌کند؟
1. **جلوگیری از افزودن تکنولوژی‌های ناخواسته (Zero Hallucination)**: اگر کاربر بگوید «یک سایت فروشگاهی بساز»، ابزار سرخود دیتابیس PostgreSQL، فریم‌ورک React یا داکر را به او تحمیل نمی‌کند.
2. **حفظ کامل محدودیت‌های منفی (Negative Constraints)**: عباراتی مانند «از فریم‌ورک جاوااسکریپت استفاده نکن» یا «داکر استفاده نشود» به صورت دستور قاطع حفظ می‌شوند و هرگز به ترجیحات ضعیف تغییر شکل نمی‌دهند.
3. **تفکیک شفاف جزئیات**: اطلاعات به ۴ بخش مجزا تفکیک می‌شوند:
   - **الزامات حفظ‌شده (`preserved_requirements`)**: مواردی که صراحتاً توسط کاربر بیان شده است.
   - **فرض‌ها (`assumptions`)**: مواردی که بدون آن‌ها فهم درخواست ناممکن بوده است.
   - **اطلاعات ازدست‌رفته (`missing_information`)**: ابهامات اساسی که در صورت نیاز باید از کاربر پرسیده شود.
   - **پیشنهادها (`suggestions`)**: ایده‌های تکمیلی که داخل متن اصلی پرامپت تزریق نمی‌شوند تا پرامپت آلوده نشود.
4. **رعایت اصل تناسب (Proportionality Rule)**: برای یک درخواست ساده ویرایشی، یک پرامپت کوتاه تولید می‌شود؛ اما برای درخواست‌های مهندسی پیچیده، پرامپتی با بخش‌های کامل (زمینه، محدودیت‌ها، رفتار مورد انتظار، تحویل‌شدنی‌ها) ساخته می‌شود.
5. **دسته‌بندی خودکار در ۱۰ گروه**: کدنویسی (`coding`)، رفع باگ (`debugging`)، تحقیق و پژوهش (`research`)، نگارش و متن (`writing`)، تولید تصویر (`image_generation`)، ترجمه (`translation`)، تحلیل داده (`data_analysis`)، برنامه‌ریزی (`planning`)، اتوماسیون (`automation`) و عمومی (`general`).
6. **مدیریت مصرف توکن و سهمیه‌ها (Rate Limits Dashboard)**:
   - نمایش آمار زنده توکن‌های ورودی، خروجی و پردازش درونی (Thoughts).
   - محاسبه محدودیت‌های لحظه‌ای **RPM** (درخواست در دقیقه)، **TPM** (توکن در دقیقه) و **RPD** (درخواست در روز) با نوارهای پیشرفت وضعیت.
7. **انتقال با یک کلیک به ایجنت‌ها**: دکمه‌های آماده جهت کپی پرامپت مناسب برای **Claude Code** و **OpenCode**.

---

## ۳. ساختار پروژه (Project Structure)

```text
.
├── prompt_compiler/
│   ├── api/
│   │   └── routes/
│   │       ├── models.py          # دریافت کاتالوگ مدل‌های پشتیبانی‌شده گوگل
│   │       ├── pages.py           # رندر کردن رابط کاربری تحت وب
│   │       ├── settings.py        # ذخیره‌سازی کلید API و تنظیمات
│   │       ├── translation.py     # اندپوینت اصلی تبدیل و کامپایل پرامپت
│   │       └── usage.py           # آمار و تلمتری مصرف توکن‌ها
│   ├── services/
│   │   ├── gemini.py              # ارتباط با API رسمی Google AI Studio با httpx
│   │   └── usage.py               # ذخیره‌سازی و محاسبه رخدادهای توکن تا ۷ روز
│   ├── app.py                     # کارخانه ساخت اپلیکیشن FastAPI
│   ├── catalog.py                 # کاتالوگ مدل‌ها، محدودیت نرخ و دسته‌ها
│   ├── config.py                  # مدیریت مسیرها و خواندن/نوشتن config.json
│   └── prompt_engine.py           # موتور تدوین سیستم پرامپت و پارسر خروجی
├── static/
│   ├── fonts/                     # فونت زیبای وزیرمتن (Vazirmatn WOFF2)
│   ├── style.css                  # استایل‌های مدرن و تم تاریک (Dark Mode)
│   └── script.js                  # منطق تعاملی فرانت‌اند و به‌روزرسانی داشبورد
├── templates/
│   └── index.html                 # قالب اصلی برنامه با طراحی واکنش‌گرا و راست‌چین
├── tests/
│   └── test_prompt_engine.py      # مجموعه ۴۸ تست خودکار اعتبارسنجی سیستم
├── config.json                    # فایل تنظیمات محلی و کلید API
├── usage.json                     # تاریخچه مصرف توکن‌های ثبت‌شده
├── main.py                        # فایل ورودی کمکی برای اجرای سرور
├── requirements.txt               # وابستگی‌های پایتونی پروژه
├── run.bat                        # اسکریپت اجرای تک‌کلیکه در ویندوز
└── README.md                      # مستندات جامع پروژه
```

---

## ۴. نصب و راه‌اندازی گام به گام (Installation & Setup)

### پیش‌نیازها
- پایتون نسخه **3.10** یا بالاتر.
- کلید رایگان **Google AI Studio API Key** (از آدرس [aistudio.google.com/apikey](https://aistudio.google.com/apikey) دریافت کنید).
- دسترسی به دامنه اینترنتی `generativelanguage.googleapis.com`.

---

### روش اول: اجرای آسان در ویندوز (توصیه‌شده)
کافیست فایل `run.bat` را دو بار کلیک کرده یا در ترمینال اجرا کنید:
```cmd
run.bat
```
این فایل خودکار محیط مجازی پایتون (`venv`) را ایجاد کرده، بسته‌ها را نصب نموده و سرور را اجرا می‌کند.

---

### روش دوم: راه‌اندازی دستی (ویندوز، لینوکس و مک)

#### ۱. رفتن به پوشه پروژه
```bash
cd /path/to/project
```

#### ۲. ساخت و فعال‌سازی محیط مجازی (Virtual Environment)
- **ویندوز (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **لینوکس / مکینتاش**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### ۳. نصب وابستگی‌های پایتون
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### ۴. اجرای برنامه
با دستور Uvicorn سرور را روی پورت ۸۰۰۰ بالا بیاورید:
```bash
python -m uvicorn prompt_compiler.app:app --host 0.0.0.0 --port 8000 --reload
```
یا با اجرای مستقیم فایل `main.py`:
```bash
python main.py
```

سپس در مرورگر آدرس زیر را باز کنید:
```text
http://127.0.0.1:8000
```

---

## ۵. پیکربندی (Configuration)

۱. پس از باز کردن برنامه در مرورگر، روی دکمه **تنظیمات** در گوشه بالا کلیک کنید.  
۲. کلید اختصاصی گوگل خود (**API Key**) را وارد کنید.  
۳. مدل پیش‌فرض مورد نظر خود را انتخاب کنید (به عنوان مثال `Gemini 3.5 Flash` یا `Gemini 3.8 Flash`).  
۴. روی **ذخیره تنظیمات** کلیک کنید.  

تنظیمات در فایل `config.json` ذخیره می‌شوند:
```json
{
  "gemini_api_key": "AIzaSy...",
  "gemini_model": "gemini-3.5-flash",
  "system_prompt_override": ""
}
```
> [!IMPORTANT]
> فایل `config.json` حاوی کلید API شماست. این فایل را در گیت یا مخازن عمومی منتشر نکنید.

---

## ۶. راهنمای استفاده (Usage Guide)

### گام ۱: وارد کردن پرامپت فارسی
در کادر ورودی، درخواست مورد نظر خود را به زبان عامیانه یا رسمی بنویسید.
*نمونه:*
```text
یه سیستم مدیریت رزومه با FastAPI بساز که فایل PDF رو دریافت کنه و مهارت‌ها رو استخراج کنه. از کتابخانه‌های خارجی ناشناخته استفاده نکن. دیتابیس رو SQLite بذار.
```

### گام ۲: انتخاب مدل و تبدیل
مدل مدنظر را انتخاب کرده و روی **تبدیل کن** کلیک کنید. سیستم درخواست را تجزیه، پالایش و ترجمه می‌کند.

### گام ۳: بررسی نتایج
- **نشان دسته‌بندی**: نوع درخواست (کدنویسی، دیباگ، تحقیق و...) را نشان می‌دهد.
- **خروجی دوتایی**:
  - پرامپت انگلیسی (ساختاریافته و استاندارد برای ایجنت).
  - پرامپت فارسی (ترجمه کلمه به کلمه ساختار انگلیسی جهت بازبینی شما).
- **کارت‌های تحلیلی**:
  - الزامات حفظ‌شده
  - فرضیات اعمال‌شده
  - اطلاعات ازدست‌رفته
  - پیشنهادهای تکمیلی اختیاری

### گام ۴: استفاده در ابزارها
- با دکمه **⧉ کپی انگلیسی**، پرامپت استاندارد را کپی کنید.
- با دکمه‌های اختصاصی **استفاده در Claude Code** یا **استفاده در OpenCode**، متن مناسب برای محیط خط فرمان این ابزارها را کپی و پیست کنید.

---

## ۷. مستندات وب‌سرویس (API Endpoints)

| متد | مسیر (Route) | توضیحات |
| :--- | :--- | :--- |
| `GET` | `/` | بارگذاری و رندر رابط کاربری وب |
| `GET` | `/models` | فهرست تمام مدل‌های گوگل و مشخصات سهمیه آن‌ها |
| `GET` | `/usage` | گزارش مصرف توکن امروز و وضعیت لحظه‌ای مدل‌ها |
| `POST` | `/settings` | به‌روزرسانی کلید API و مدل پیش‌فرض |
| `POST` | `/translate` | ارسال پرامپت فارسی و دریافت نتیجه پردازش‌شده |

نمونه درخواست به `/translate`:
```bash
curl -X POST "http://127.0.0.1:8000/translate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "یه اسکریپت پایتون بنویس که فایل‌های یک پوشه رو بر اساس پسوند دسته‌بندی کنه", "model": "gemini-3.5-flash"}'
```

---

## ۸. تست و اعتبارسنجی خودکار (Automated Testing)

این پروژه دارای ۴۸ تست واحد خودکار در فایل `tests/test_prompt_engine.py` است که سیاست‌های عدم توهم، پشتیبانی از دسته‌بندی‌ها، انطباق ترجمه فارسی با انگلیسی و نرمال‌سازی خروجی JSON را بدون نیاز به ارسال درخواست واقعی به گوگل می‌سنجد.

برای اجرای تست‌ها:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📄 License
This project is open-source and available under the standard MIT License.
