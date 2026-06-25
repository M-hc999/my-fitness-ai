import streamlit as st
from openai import OpenAI

# ================= 核心配置 =================
st.set_page_config(page_title="AI 健身饮食助手", page_icon="💪", layout="centered")

# ================= 功能一：女朋友侧边栏互动头像 =================

# 这里使用了一张高质量的二次元可爱女生头像，你可以随时换成你女朋友照片的图床链接
# ================= 功能一：女朋友侧边栏互动头像 =================
st.sidebar.header("💖 专属能量站")

# 替换为了国内访问极其稳定的高颜值大厂图床头像
avatar_url = "log.jpg"
st.sidebar.image(avatar_url, use_container_width=True)

# 侧边栏互动按钮
if st.sidebar.button("🥰 戳戳歪歪（获取每日鼓励）"):
    st.balloons()  # ✨ 核心修复：去掉了 sidebar 且加上了 s！
    st.sidebar.success("今天也要好好吃饭，健康减脂！你是最棒的，贴贴~ 💋")
# ================= 主界面布局 =================
st.title("💪 AI 智能健身饮食计划生成器")
st.write("输入你的身体数据，让 DeepSeek 为你量身定制今日食谱。")

# 从 Streamlit 云端的高级设置（Secrets）中安全读取密钥
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    st.error("未在云端检测到 DEEPSEEK_API_KEY，请检查高级设置。")
    st.stop()

# 初始化 DeepSeek 客户端
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 用户输入表单
with st.form("user_info_form"):
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("体重 (kg)", min_value=30, max_value=200, value=70)
        goal = st.selectbox("核心目标", ["减脂控能", "增肌塑形", "保持健康"])
    with col2:
        height = st.number_input("身高 (cm)", min_value=100, max_value=250, value=175)
        exercise = st.selectbox("运动强度", ["久坐不动", "每周轻度运动", "每周中度运动", "每天高强度"])
    
    extra_notes = st.text_input("忌口或特殊需求（如：不吃香菜、海鲜过敏、预算有限）", value="无")
    submit_btn = st.form_submit_button("🔥 立即一键生成方案")

# 处理大模型请求
if submit_btn:
    prompt = f"你是一位资深的专业健身营养师。请根据以下用户数据制定一份保姆级的饮食计划：\n身高：{height}cm，\n体重：{weight}kg，\n目标：{goal}，\n运动强度：{exercise}，\n特殊需求：{extra_notes}。\n请给出具体的早餐、午餐、加餐、晚餐建议，并包含总热量预估。"
    
    with st.spinner("🧙‍♂️ 营养师正在疯狂计算中，请稍候..."):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的健康饮食AI助手，给出的方案必须条理清晰、排版美观。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            # 获取生成的纯文本方案
            result_text = response.choices[0].message.content
            
            # 展示方案
            st.success("✨ 你的专属定制方案已生成！")
            st.markdown(result_text)
            
            # ================= 功能二：一键下载功能 =================
            st.write("---")
            st.download_button(
                label="📥 一键下载饮食计划 (.md文本)",
                data=result_text,
                file_name="我的专属AI饮食计划.md",
                mime="text/markdown"
            )
            st.caption("💡 提示：下载后的 .md 文件可以直接用电脑或手机自带的文本工具打开，在浏览器或软件里点击“打印 -> 另存为 PDF”即可秒变精美 PDF 报告！")
            
        except Exception as e:
            st.error(f"调用 API 失败了，错误信息：{e}")
