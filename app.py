import streamlit as st
from openai import OpenAI

# 1. 网页基础配置
st.set_page_config(page_title="AI 智能健身饮食助手", layout="centered", page_icon="🍎")

st.title("健身饮食计划生成器")
st.caption("生成最接地气的饮食方案")

# 2. 核心：无感读取本地配置的 API Key（最高效！）
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    st.error("❌ 未检测到 secrets.toml 配置文件，请检查配置。")
    st.stop()

# 3. 用户数据输入界面
with st.form("user_info_form"):
    st.subheader("第一步：填写身体数据")
    col1, col2, col3 = st.columns(3)
    with col1:
        height = st.number_input("身高 (cm)", min_value=100, max_value=250, value=175)
    with col2:
        weight = st.number_input("体重 (kg)", min_value=30, max_value=200, value=70)
    with col3:
        age = st.number_input("年龄", min_value=1, max_value=100, value=20)

    st.subheader("第二步：明确你的目标与身份")
    goal = st.selectbox("你的健身目标", ["增肌 (Gain Muscle)", "减脂 (Lose Fat)", "保持体型 (Maintain)"])

    identity = st.selectbox("你的身份/场景", [
        "学生党（主要吃食堂、校园超市、网购囤货）",
        "上班族（外卖为主，无法自己做饭）",
        "上班族（可以自己做饭，追求高效批量备餐）"
    ])

    submit_button = st.form_submit_button("开始生成我的专属饮食计划 🚀")

# 4. 大模型调用逻辑
if submit_button:
    system_prompt = """
    你是一个精通运动营养学和大众饮食习惯的 AI 健身教练。
    你需要根据用户提供的身体数据（身高、体重、年龄、目标、身份场景），给出一套极具操作性的饮食建议。

    回答必须严格包含以下两部分：

    ## 📊 第一部分：每日宏量营养素目标
    - 总热量（kcal）
    - 蛋白质（g）
    - 碳水化合物（g）
    - 脂肪（g）
    (请给出明确的数值或范围，并简要说明为什么这样设计)

    ## 🍳 第二部分：场景化食谱推荐
    根据用户的身份场景进行针对性推荐：
    - 如果是学生党：必须围绕【食堂打饭攻略】、【校园超市/便利店精选】、【网购囤货（如即食鸡胸肉、全麦面包、燕麦）】来写。
    - 如果是无法做饭的上班族：着重写【外卖如何聪明单点】和【便利店应急组合】。
    - 如果是可以做饭的上班族：着重写【高效批量备餐 (Meal Prep) 方案】。
    """

    user_prompt = f"身高：{height}cm, 体重：{weight}kg, 年龄：{age}岁, 目标：{goal}, 身份：{identity}"

    with st.spinner("DeepSeek 正在为你疯狂计算，请稍候..."):
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            st.success("✨ 你的专属饮食计划已生成！")
            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f"DeepSeek 连接失败。错误信息: {e}")