import streamlit as st
from openai import OpenAI

# ================= 核心配置 =================
st.set_page_config(page_title="AI 健身饮食助手", page_icon="💪", layout="centered")

# ================= 功能一：专属能量站（已修复全屏气球） =================
st.sidebar.header("💖 专属能量站")

# 采用国内访问极其稳定的高颜值大厂图床头像
avatar_url = "log.jpg"
st.sidebar.image(avatar_url, use_container_width=True)

# 侧边栏互动按钮
if st.sidebar.button("🥰 戳戳歪歪（获取每日鼓励）"):
    st.balloons()  # 触发全屏放气球的炫酷特效！
    st.sidebar.success("今天也要好好吃饭，健康减脂！你是最棒的，贴贴~ 💋")

# ================= 主界面标题 =================
st.title("💪 健身饮食计划生成器")
st.write("生成最接地气的饮食方案")

# 从 Streamlit 云端安全读取密钥
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    st.error("未在云端检测到 DEEPSEEK_API_KEY，请检查高级设置。")
    st.stop()

# 初始化 DeepSeek 客户端
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ================= 用户表单输入部分 =================
st.header("第一步：填写身体数据")
# 升级为4列布局，完美并排容纳性别
col1, col2, col3, col4 = st.columns(4)
with col1:
    gender = st.selectbox("性别", ["男 (Male)", "女 (Female)"])
with col2:
    height = st.number_input("身高 (cm)", min_value=100, max_value=250, value=175)
with col3:
    weight = st.number_input("体重 (kg)", min_value=30, max_value=200, value=70)
with col4:
    age = st.number_input("年龄", min_value=1, max_value=120, value=20)

st.header("第二步：明确你的目标与身份")
goal = st.selectbox(
    "你的健身目标", 
    ["增肌 (Gain Muscle)", "减脂控能 (Lose Weight)", "保持健康 (Stay Healthy)"]
)

identity = st.selectbox(
    "你的身份/场景", 
    [
        "学生党（主要吃食堂、校园超市、网购囤货）",
        "上班族（常吃外卖、久坐不动、偶尔做饭）",
        "居家党（时间充裕、自己做饭、食材自由）"
    ]
)

extra_notes = st.text_input("忌口或额外需求（如：不吃香菜、海鲜过敏等）", value="无")

# 开始生成按钮
submit_btn = st.button("🚀 开始生成我的专属饮食计划")

# ================= 业务逻辑：动态性别提示词 =================
# ================= 业务逻辑：流式响应升级版 =================
if submit_btn:
    
    # 根据不同性别，动态注入完全不同的专业营养学侧重点
    if gender == "男 (Male)":
        gender_prompt = """
- 针对【男性】生理特点：考虑到男性通常有更高的基础代谢和肌肉合成需求。请合理规划碳水和优质蛋白质的比例，注重肌肉修复，并确保提供充足的力量训练能量支持，避免肌肉流失。"""
    else:
        gender_prompt = """
- 针对【女性】生理特点：考虑到女性的内分泌与激素健康至关重要。请特别注重优质脂肪（如坚果、蛋黄、牛油果）的合理搭配，确保摄入充足的铁元素与微量元素，强调科学减脂或塑形，切记严禁开出极端低热量、低碳水的极端口粮单，保护经期和代谢健康。"""

    # 组合成最终发送给 DeepSeek 的总提示词
    prompt = f"""你是一位资深的专业健身营养师。请根据以下用户数据制定一份保姆级的饮食计划：
- 性别：{gender} {gender_prompt}
- 身高：{height}cm
- 体重：{weight}kg
- 年龄：{age}岁
- 健身目标：{goal}
- 身份场景：{identity} （如果是学生党，请多推荐高校食堂、校园便利店容易获取的经济实惠的食材和菜品）
- 额外需求：{extra_notes}

请给出具体的早餐、午餐、加餐、晚餐建议，并包含总热量预估。排版请保持条理清晰、美观，多用表格或列表展示。"""
    
    # 使用占位符，让体验更丝滑
    with st.spinner("🧙‍♂️ 营养师正在针对你的性别进行精确计算..."):
        try:
            # 🚀 核心改变一：将 stream 设置为 True
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "你是一个专业的健康饮食AI助手，懂得男女生理代谢差异，给出的方案必须条理清晰、排版美观。\n"
                            "⚠️【重要排版要求】：在生成的 Markdown 表格中，如果单元格内部需要换行，"
                            "请务必直接使用最原始的 <br> 标签，绝对不要加反斜杠转义（不要写成 \\<br\\>），"
                            "也绝对不要写成转义字符（如 &lt;br&gt;），确保前端能够直接解析并完美换行！"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                stream=True 
            )
            
            st.success("✨ 你的专属定制方案已生成！")
            
            # 🚀 核心改变二：创建一个干净的文本流生成器
            def generate_chunks():
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        yield content
            
            # 🚀 核心改变三：使用 st.write_stream 现场表演“打字机效果”
            # 它不仅能一边吐字一边显示，还能自动把最终的完整文本存进 result_text 供下载！
            result_text = st.write_stream(generate_chunks())
            
            # ================= 功能：一键下载功能 =================
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
