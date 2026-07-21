import streamlit as st
import pandas as pd
from PIL import Image
from openai import OpenAI
import base64
import os

#  Streamlit Page Setting & Background Layout
st.set_page_config(page_title="Pesticide & Medicine Verifier", page_icon="🌾", layout="centered")


LANGUAGES = {
    "မြန်မာ": {
        "sidebar_title": " Navigation Menu",
        "page_main": " Main Page",
        "page_manage": "Pesticide Management",
        "page_chat": "AI Chatbot",
        "main_title": "ပိုးသတ်ဆေး ခွင့်ပြုချက် စစ်ဆေးရေး စနစ်",
        "tab_search": "ဆေးအမည် ရိုက်ရှာရန်",
        "tab_upload": "ဆေးဘူးပုံ တင်စစ်ရန်",
        "search_desc": "စိုက်ပျိုးရေးဌာနတွင် မှတ်ပုံတင်ထားခြင်း ရှိ/မရှိ စစ်ဆေးရန် ဆေးအမည်ကို ရိုက်ထည့်ပါ။",
        "search_label": "ပိုးသတ်ဆေးအမည် (Trade Name သို့မဟုတ် Active Ingredient သို့မဟုတ် Reg Number):",
        "not_found": "⚠️ ရှာမတွေ့ပါ။ စိုက်ပျိုးရေးဌာနတွင် မှတ်ပုံတင်ထားခြင်း မရှိသေးပါ။",
        "upload_desc": "ဆေးဘူး သို့မဟုတ် စိုက်ပျိုးရေးဆေးပုံကို Upload တင်ပြီး စစ်ဆေးပါ။",
        "upload_label": "ကြိုက်နှစ်သက်ရာ ဆေးဘူးပုံကို ရွေးချယ်တင်ပါ...",
        "verify_btn": "စစ်ဆေးမည်",
        "spinner_ocr": " ဆေးဘူးပုံကို စစ်ဆေးပြီး အချက်အလက်များ ဖော်ထုတ်နေပါသည်...",
        "ocr_result": "🔍 **ဖတ်မိသော အမည်/စာသား:**",
        "dataset_result": " ရလဒ်(Result)",
        "ai_header": "🤖 AI ၏ ဆေးဝါးအသေးစိတ် ရှင်းလင်းချက်",
        
        # CRUD Labels
        "crud_title": "ပိုးသတ်ဆေး  စီမံခန့်ခွဲခြင်း ",
        "crud_select_action": "လုပ်ဆောင်လိုသည့် လုပ်ငန်းစဉ်ကို ရွေးချယ်ပါ -",
        "action_insert": "ဆေးအသစ် ထည့်သွင်းရန် ",
        "action_update": "ရှိပြီးသားဆေး ပြင်ဆင်ရန် ",
        "action_delete": "ဆေးအချက်အလက် ပယ်ဖျက်ရန် ",
        "select_pesticide": "ပိုးသတ်ဆေး ရွေးချယ်ရန် -",
        
        # Form Fields
        "form_trade": "ဆေးအမည် (Trade Name) *",
        "form_active": "ပါဝင်ပစ္စည်း (Active Ingredient) *",
        "form_company": "တင်သွင်းသည့် ကုမ္ပဏီ (Company)",
        "form_distributor": "ဖြန့်ဝေသည့် ကုမ္ပဏီ (Distributor)",
        "form_reg": "မှတ်ပုံတင်နံပါတ် (Registration Number) *",
        "form_status": "ခွင့်ပြုချက် အခြေအနေ (Status) *",
        
        # Buttons
        "btn_insert": "ဆေးအသစ် သိမ်းဆည်းမည်",
        "btn_update": "အချက်အလက်များ ပြင်ဆင်မည်",
        "btn_delete": "ဤဆေးကို စနစ်ထဲမှ ဖျက်ပစ်မည်",
        
        "form_error": "⚠️ ကျေးပြု၍ ကြယ်ပွင့် (*) ပြထားသော နေရာများကို မဖြစ်မနေ ဖြည့်စွက်ပေးပါ။",
        "success_insert": " ဆေးအချက်အလက်ကို `final.csv` ထဲသို့ အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ။",
        "success_update": " ဆေးအချက်အလက်များကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ။",
        "success_delete": "🗑️ ဆေးအချက်အလက်ကို ဒေတာဗေ့စ်ထဲမှ ဖျက်သိမ်းပြီးပါပြီ။",
        "confirm_delete": "⚠️ ဤဆေးအချက်အလက်ကို ဖျက်ပစ်ရန် သေချာပါသလား?",
        
        "dataset_count": "Dataset ထဲတွင် စုစုပေါင်း ပိုးသတ်ဆေး **{}** မျိုး မှတ်ပုံတင်ထားပြီး ဖြစ်သည်။",
        "chat_title": "AI ဆေးဝါးနှင့် ပိုးသတ်ဆေး အကြံပေး Chatbot",
        "chat_desc": "ပိုးသတ်ဆေးများ၊ ဓာတ်မြေဩဇာများနှင့် စိုက်ပျိုးရေးဆိုင်ရာ မေးခွန်းများကို AI ထံ လွတ်လပ်စွာ မေးမြန်းနိုင်ပါသည်။",
        "chat_welcome": "မင်္ဂလာပါဗျာ။ စိုက်ပျိုးရေးဆေးဝါးများနှင့် ပတ်သက်ပြီး သိလိုသည်များကို မေးမြန်းနိုင်ပါတယ်!",
        "chat_placeholder": "ဤနေရာတွင် မေးခွန်းရိုက်ပါ...",
        "ai_prompt_lang": "မြန်မာဘာသာဖြင့် သေချာကျနစွာ ရှင်းပြပေးပါ။"
    },
    "English": {
        "sidebar_title": "Navigation Menu",
        "page_main": "Main Page",
        "page_manage": "Manage Database (CRUD)",
        "page_chat": "AI Chatbot",
        "main_title": "Legitimate Pest Residue Detection",
        "tab_search": "Search by Name",
        "tab_upload": "Upload Image",
        "search_desc": "Enter the pesticide name to check its registration status with the Department of Agriculture.",
        "search_label": "Pesticide Name (Trade Name, Active Ingredient, or Reg Number):",
        "not_found": "⚠️ Not Found. This pesticide is not registered in the database.",
        "upload_desc": "Upload a pesticide bottle image to verify and analyze.",
        "upload_label": "Choose a pesticide image...",
        "verify_btn": "Verify Now",
        "spinner_ocr": "AI is examining the image and extracting information...",
        "ocr_result": "🔍 **Extracted Text/Name:**",
        "dataset_result": " Verification Result",
        "ai_header": "🤖 AI Detailed Medical Explanation",
        
        # CRUD Labels
        "crud_title": "Pesticide  Management",
        "crud_select_action": "Select Action:",
        "action_insert": "Add New Pesticide (Insert)",
        "action_update": "Edit Existing Pesticide (Update)",
        "action_delete": "Remove Pesticide (Delete)",
        "select_pesticide": "Select Pesticide to Modify:",
        
        # Form Fields
        "form_trade": "Trade Name *",
        "form_active": "Active Ingredient *",
        "form_company": "Importing Company (Company)",
        "form_distributor": "Distributor Company",
        "form_reg": "Registration Number *",
        "form_status": "Status *",
        
        # Buttons
        "btn_insert": "Save New Record",
        "btn_update": "Update Information",
        "btn_delete": "Delete Record From System",
        
        "form_error": "⚠️ Please fill in all mandatory fields marked with an asterisk (*).",
        "success_insert": " Pesticide data has been successfully added to `final.csv`.",
        "success_update": " Pesticide data has been successfully updated.",
        "success_delete": "🗑️ Pesticide record has been removed from the database.",
        "confirm_delete": "⚠️ Are you sure you want to delete this record?",
        
        "dataset_count": "Total registered pesticides in dataset: **{}** entries.",
        "chat_title": "AI Agriculture & Pesticide Chatbot",
        "chat_desc": "Feel free to ask AI any questions regarding pesticides, fertilizers, and farming tips.",
        "chat_welcome": "Hello! I am your AI agricultural expert. How can I help you today?",
        "chat_placeholder": "Type your question here...",
        "ai_prompt_lang": "Please explain everything clearly in English."
    }
}

#  LANGUAGE SELECTOR 
lang_choice = st.sidebar.selectbox("Language / ဘာသာစကား", ["မြန်မာ", "English"])
text = LANGUAGES[lang_choice]

# UI
st.markdown(
    f"""
    <style>
   
    .page-title {{
        text-align: center !important;   
        font-size: 32px !important;      
        font-weight: bold !important;
        color: #1E3A8A !important;      
        line-height: 1.3 !important;
        margin-top: 10px !important;
        margin-bottom: 35px !important;
    }}
    [data-testid="stFileUploader"] > section {{
        padding: 10px 20px !important;   
        min-height: 80px !important;     
        border-radius: 8px !important;
    }}
    .stImage img {{
        max-width: 250px !important;    
        height: auto !important;
        border-radius: 8px;
    }}
    .stMarkdown p {{
        white-space: pre-wrap !important;
        word-break: break-word !important;
        line-height: 1.6 !important;
    }}
    
  
    div.stButton > button, div.stFormSubmitButton > button {{
        background-color: #2563EB !important;  /* Royal Blue */
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 22px !important;
        border: none !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }}
    
   
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
        background-color: #1D4ED8 !important; 
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-1px) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Data Load &Save
CSV_PATH = "final.csv"

def load_data(csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=['trade_name', 'active_ingredient', 'company', 'Distributor', 'registration_number', 'status'])
        df.to_csv(csv_path, index=False, encoding='utf-8')
        return df
        
    encodings = ['utf-8', 'latin1', 'cp1252', 'utf-8-sig']
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            df['trade_name'] = df['trade_name'].fillna("-")
            df['active_ingredient'] = df['active_ingredient'].fillna("-")
            df['company'] = df['company'].fillna("-")
            df['Distributor'] = df['Distributor'].fillna("-")
            df['registration_number'] = df['registration_number'].fillna("-")
            df['status'] = df['status'].fillna("Pending")
            
            df['trade_name_clean'] = df['trade_name'].astype(str).str.strip().str.lower()
            df['active_clean'] = df['active_ingredient'].astype(str).str.strip().str.lower()
            df['reg_clean'] = df['registration_number'].astype(str).str.strip().str.lower()
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("ဖိုင်ကို ဖတ်လို့မရပါ။ CSV ရဲ့ Encoding ကို စစ်ဆေးပေးပါ။")

def save_data(dataframe, csv_path=CSV_PATH):
    cols_to_save = ['trade_name', 'active_ingredient', 'company', 'Distributor', 'registration_number', 'status']
    dataframe[cols_to_save].to_csv(csv_path, index=False, encoding='utf-8')

df = load_data()

# API KEY & OpenRouter
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
client = None
if OPENROUTER_API_KEY:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

def extract_medicine_name(base64_image, file_type):
    if not client: return None
    try:
        prompt = "Identify the main chemical name, active ingredient, or trade name of the pesticide/medicine shown in this image. Return ONLY the extracted name in plain text. No extra words."
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash", 
            max_tokens=500,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{file_type};base64,{base64_image}"}}]}]
        )
        return response.choices[0].message.content.strip()
    except: return None

def explain_medicine_details(base64_image, file_type, target_lang):
    if not client: return "API Client မရှိပါ။"
    try:
        lang_prompt = "မြန်မာဘာသာဖြင့် အသေးစိတ် သေချာစွာ ရှင်းပြပေးပါ" if target_lang == "မြန်မာ" else "Detailed explanation in English"
        prompt = f"ပေးထားသော ဆေးဘူးပုံကို သေချာကြည့်ပြီး အောက်ပါအချက်အလက်များကို {lang_prompt} -\n၁။ ဆေးအမည်\n၂။ ပါဝင်ပစ္စည်းနှင့် အချိုးအစား\n၃။ ဆေး၏ အာနိသင်နှင့် အသုံးပြုပုံ\n၄။ အသုံးမပြုသင့်သူများနှင့် သတိပြုရန်အချက်များ"
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            max_tokens=1500, 
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{file_type};base64,{base64_image}"}}]}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e: return f"Error: {e}"

def check_status_logic(search_text, dataframe):
    query_clean = search_text.strip().lower()
    result = dataframe[(dataframe['trade_name_clean'] == query_clean) | (dataframe['active_clean'] == query_clean) | (dataframe['reg_clean'] == query_clean)]
    if result.empty:
        result = dataframe[dataframe['trade_name_clean'].str.contains(query_clean, na=False) | dataframe['active_clean'].str.contains(query_clean, na=False) | dataframe['reg_clean'].str.contains(query_clean, na=False)]
    return result

#  SIDEBAR 
st.sidebar.title(text["sidebar_title"])
page = st.sidebar.radio("Menu:", [text["page_main"], text["page_manage"], text["page_chat"]])

# Main Page
if page == text["page_main"]:
    # Home Page ဖြစ်၍ ခေါင်းစဉ်ကို page-title class သုံးကာ အလယ်တွင် ပြသသည်
    st.markdown(f'<div class="page-title">{text["main_title"]}</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([text["tab_search"], text["tab_upload"]])

    with tab1:
        st.write(text["search_desc"])
        search_query = st.text_input(text["search_label"])

        if search_query:
            res_df = check_status_logic(search_query, df)
            if not res_df.empty:
                row = res_df.iloc[0]
                st.subheader(f"Result - {row['trade_name']}")
                status = str(row['status']).strip()
                if status.lower() == "approved":
                    st.success("✅ APPROVED" if lang_choice == "English" else "✅ APPROVED (ခွင့်ပြုထားသောဆေး)")
                elif status.lower() == "banned":
                    st.error("❌ BANNED" if lang_choice == "English" else "❌ BANNED (ပိတ်ပင်ထားသောဆေး)")
                else:
                    st.warning(f"⚠️ STATUS: {status.upper()}")
                
                st.write(f"**{'Active Ingredient' if lang_choice == 'English' else 'ပါဝင်ပစ္စည်း'}:** {row.get('active_ingredient', '-')}")
                st.write(f"**{'Import Company' if lang_choice == 'English' else 'တင်သွင်းသည့်ကုမ္ပဏီ'}:** {row.get('company', '-')}")
                st.write(f"**{'Distributor' if lang_choice == 'English' else 'ဖြန့်ဝေသည့်ကုမ္ပဏီ'}:** {row.get('Distributor', '-')}")
                st.write(f"**{'Registration No.' if lang_choice == 'English' else 'မှတ်ပုံတင်နံပါတ်'}:** {row.get('registration_number', '-')}")
            else:
                st.warning(text["not_found"])

    with tab2:
        st.write(text["upload_desc"])
        uploaded_file = st.file_uploader(text["upload_label"], type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image") 
            
            if st.button(text["verify_btn"]):
                with st.spinner(text["spinner_ocr"]):
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")
                    
                    detected_name = extract_medicine_name(base64_image, uploaded_file.type)
                    if detected_name:
                        st.info(f"{text['ocr_result']} {detected_name}")
                        res_df = check_status_logic(detected_name, df)
                        
                        if not res_df.empty:
                            row = res_df.iloc[0]
                            st.subheader(f"{text['dataset_result']} - {row['trade_name']}")
                            
                            status = str(row['status']).strip()
                            if status.lower() == "approved": 
                                st.success("✅ APPROVED" if lang_choice == "English" else "✅ APPROVED (ခွင့်ပြုထားသောဆေး)")
                            elif status.lower() == "banned": 
                                st.error("❌ BANNED" if lang_choice == "English" else "❌ BANNED (ပိတ်ပင်ထားသောဆေး)")
                            else:
                                st.warning(f"⚠️ STATUS: {status.upper()}")
                            
                            st.write(f"**{'Active Ingredient' if lang_choice == 'English' else 'ပါဝင်ပစ္စည်း'}:** {row.get('active_ingredient', '-')}")
                            st.write(f"**{'Import Company' if lang_choice == 'English' else 'တင်သွင်းသည့်ကုမ္ပဏီ'}:** {row.get('company', '-')}")
                            st.write(f"**{'Distributor' if lang_choice == 'English' else 'ဖြန့်ဝေသည့်ကုမ္ပဏီ'}:** {row.get('Distributor', '-')}")
                            st.write(f"**{'Registration No.' if lang_choice == 'English' else 'မှတ်ပုံတင်နံပါတ်'}:** {row.get('registration_number', '-')}")
                        else:
                            st.warning(f"⚠️ NOT FOUND: '{detected_name}'")

# Data Management
elif page == text["page_manage"]:
   
    st.markdown(f'<div class="page-title">{text["crud_title"]}</div>', unsafe_allow_html=True)
    
   # label_visibility="collapsed" ထည့်ပေးခြင်းဖြင့် ခေါင်းစဉ်စာသား လုံးဝ မပေါ်တော့ပါ
    action = st.radio(
    "", 
    [text["action_insert"], text["action_update"], text["action_delete"]],
    label_visibility="collapsed"
)

    # insert
    if action == text["action_insert"]:
        with st.form("insert_form", clear_on_submit=True):
            trade_name = st.text_input(text["form_trade"])
            active_ingredient = st.text_input(text["form_active"])
            company = st.text_input(text["form_company"])
            distributor = st.text_input(text["form_distributor"])
            reg_number = st.text_input(text["form_reg"])
            status = st.selectbox(text["form_status"], ["Approved", "Banned", "Pending"])
            
            submit_btn = st.form_submit_button(text["btn_insert"])
            
            if submit_btn:
                if not trade_name or not active_ingredient or not reg_number:
                    st.error(text["form_error"])
                else:
                    new_row = {
                        'trade_name': trade_name.strip(),
                        'active_ingredient': active_ingredient.strip(),
                        'company': company.strip() if company else "-",
                        'Distributor': distributor.strip() if distributor else "-",
                        'registration_number': reg_number.strip(),
                        'status': status
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success(text["success_insert"])
                    st.rerun()

    #Update
    elif action == text["action_update"]:
        if df.empty:
            st.warning("Database ထဲတွင် မည်သည့်ဒေတာမှ မရှိသေးပါ။")
        else:
            pesticide_list = df['trade_name'].tolist()
            selected_pesticide = st.selectbox(text["select_pesticide"], pesticide_list)
            
            pesticide_idx = df[df['trade_name'] == selected_pesticide].index[0]
            current_row = df.loc[pesticide_idx]
            
            with st.form("update_form"):
                u_trade = st.text_input(text["form_trade"], value=current_row['trade_name'])
                u_active = st.text_input(text["form_active"], value=current_row['active_ingredient'])
                u_company = st.text_input(text["form_company"], value=current_row['company'])
                u_dist = st.text_input(text["form_distributor"], value=current_row['Distributor'])
                u_reg = st.text_input(text["form_reg"], value=current_row['registration_number'])
                
                status_options = ["Approved", "Banned", "Pending"]
                status_idx = status_options.index(current_row['status']) if current_row['status'] in status_options else 0
                u_status = st.selectbox(text["form_status"], status_options, index=status_idx)
                
                update_btn = st.form_submit_button(text["btn_update"])
                
                if update_btn:
                    if not u_trade or not u_active or not u_reg:
                        st.error(text["form_error"])
                    else:
                        df.loc[pesticide_idx, 'trade_name'] = u_trade.strip()
                        df.loc[pesticide_idx, 'active_ingredient'] = u_active.strip()
                        df.loc[pesticide_idx, 'company'] = u_company.strip() if u_company else "-"
                        df.loc[pesticide_idx, 'Distributor'] = u_dist.strip() if u_dist else "-"
                        df.loc[pesticide_idx, 'registration_number'] = u_reg.strip()
                        df.loc[pesticide_idx, 'status'] = u_status
                        
                        save_data(df)
                        st.success(text["success_update"])
                        st.rerun()

    # Delete
    elif action == text["action_delete"]:
        if df.empty:
            st.warning("Database ထဲတွင် ဖျက်ရန် ဒေတာမရှိသေးပါ။")
        else:
            pesticide_list = df['trade_name'].tolist()
            selected_pesticide = st.selectbox(text["select_pesticide"], pesticide_list)
            pesticide_idx = df[df['trade_name'] == selected_pesticide].index[0]
            
            st.warning(text["confirm_delete"])
            st.info(f"**Trade Name:** {df.loc[pesticide_idx, 'trade_name']} | **Reg No:** {df.loc[pesticide_idx, 'registration_number']}")
            
            delete_btn = st.button(text["btn_delete"], type="primary")
            
            if delete_btn:
                df = df.drop(pesticide_idx).reset_index(drop=True)
                save_data(df)
                st.success(text["success_delete"])
                st.rerun()

    st.divider()
    st.write(text["dataset_count"].format(len(df)))

# Chatbot
elif page == text["page_chat"]:
   
    st.markdown(f'<div class="page-title">{text["chat_title"]}</div>', unsafe_allow_html=True)
    st.write(text["chat_desc"])

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": text["chat_welcome"]}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.write(message["content"])

    if user_query := st.chat_input(text["chat_placeholder"]):
        with st.chat_message("user"): st.write(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.chat_message("assistant"):
            with st.spinner("..." if lang_choice == "English" else "......"):
                if client:
                    try:
                        system_instruction = f"You are an expert in agricultural pesticides and medicines. {text['ai_prompt_lang']}"
                        response = client.chat.completions.create(
                            model="google/gemini-2.5-flash",
                            max_tokens=3000, 
                            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_query}]
                        )
                        ai_response = response.choices[0].message.content.strip()
                        st.write(ai_response)
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    except Exception as e: st.error(f"Chatbot Error: {e}")
                else:
                    st.error("🔑 Error: `OPENROUTER_API_KEY` missing.")