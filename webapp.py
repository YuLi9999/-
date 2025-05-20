import streamlit as st
import csv # 我们可能需要直接在这里操作CSV，或者调用您修改后的函数
import os  # 用于检查文件是否存在

# 导入您在 password_logic.py 中定义的函数
# 请确保 password_logic.py 和这个 webapp.py 文件在同一个文件夹内
try:
    from password_logic import (
        generate_password,
        FIELD_NAMES,        # 从您的脚本导入CSV的字段名
        PASSWORD_FILE       # 从您的脚本导入CSV文件名
        # 我们需要重构或包装原始的 add_password_entry, view_all_entries, search_entries
        # 因为它们包含 input() 和 print()，不适合直接在Streamlit中使用
    )
except ImportError:
    st.error("错误：无法导入 password_logic.py。请确保该文件存在于同一目录下，并且文件名正确（无空格）。")
    st.stop() # 如果导入失败，停止应用

# --- Streamlit 界面 ---
st.set_page_config(page_title="密码管理器 MVP", layout="wide") # 设置页面标题和布局
st.title("🚀 AI军团安全密码库 MVP V0.1 (网页版) 🚀")
st.markdown("---")

# --- 辅助函数 (用于Streamlit界面与您的核心逻辑交互) ---

def streamlit_add_entry(platform, username, password_to_save):
    """
    适用于Streamlit的添加条目逻辑。
    直接将数据写入CSV文件，并返回成功或失败信息。
    """
    try:
        file_exists = os.path.isfile(PASSWORD_FILE)
        with open(PASSWORD_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            if not file_exists or csvfile.tell() == 0: # 如果文件不存在或是空的，写入表头
                writer.writeheader()
            writer.writerow({"platform": platform, "username": username, "password": password_to_save})
        return True, f"成功为 '{platform}' 添加条目！"
    except IOError:
        return False, f"错误：无法写入密码文件 '{PASSWORD_FILE}'。"
    except Exception as e:
        return False, f"发生意外错误：{e}"

def streamlit_get_all_entries():
    """
    适用于Streamlit的查看所有条目逻辑。
    读取CSV文件并返回条目列表（字典的列表）。
    """
    entries = []
    try:
        with open(PASSWORD_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entries.append(row)
        if not entries:
            return None, "保险库中没有条目，或文件不存在。"
        return entries, None # 返回条目列表和空错误信息
    except FileNotFoundError:
        return None, f"密码文件 '{PASSWORD_FILE}' 未找到。请先添加一个条目来创建它。"
    except IOError:
        return None, f"错误：无法读取密码文件 '{PASSWORD_FILE}'。"
    except Exception as e:
        return None, f"发生意外错误：{e}"

def streamlit_search_entries(search_term):
    """
    适用于Streamlit的搜索条目逻辑。
    根据平台名称搜索并返回匹配的条目列表。
    """
    if not search_term:
        return None, "搜索词不能为空。"
    
    found_entries = []
    try:
        with open(PASSWORD_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row_dict in reader:
                if search_term.lower() in row_dict['platform'].lower():
                    found_entries.append(row_dict)
            
            if not found_entries:
                return None, f"没有找到与 '{search_term}' 匹配的条目。"
            return found_entries, None
    except FileNotFoundError:
        return None, f"密码文件 '{PASSWORD_FILE}' 未找到，无法搜索。"
    except IOError:
        return None, f"错误：无法读取密码文件 '{PASSWORD_FILE}'。"
    except Exception as e:
        return None, f"发生意外错误：{e}"

# --- 使用侧边栏进行功能选择 ---
menu_choice = st.sidebar.radio(
    "选择操作:",
    ("新增密码条目", "查看所有条目", "搜索密码条目", "独立生成密码")
)
st.sidebar.markdown("---")
st.sidebar.info("由AI军团总司令斩天_与Gemini联手打造！")


# --- 根据选择显示不同的界面 ---

if menu_choice == "新增密码条目":
    st.subheader("🔑 新增密码条目")

    with st.form("add_entry_form", clear_on_submit=True): # clear_on_submit=True 表示提交后清空表单
        platform = st.text_input("平台/服务名称:", placeholder="例如：Google, Facebook")
        username = st.text_input("用户名/账号:", placeholder="例如：your_email@example.com")
        
        st.write("密码选项:")
        password_option = st.radio(
            "选择密码来源:",
            ("自动生成一个新密码", "手动输入已有密码"),
            key="password_source_option", # 给radio一个唯一的key
            index=0 # 默认选择第一个选项
        )
        
        # 用于存储最终要保存的密码
        password_to_save_on_submit = "" 

        if password_option == "自动生成一个新密码":
            st.markdown("---") 
            st.write("自动生成参数:")
            # 这些输入小部件现在是表单的一部分
            pw_length_add = st.number_input("密码长度:", min_value=8, max_value=128, value=16, step=1, key="pw_len_add_form")
            use_uppercase_add = st.checkbox("包含大写字母 (A-Z)", value=True, key="uc_add_form")
            use_digits_add = st.checkbox("包含数字 (0-9)", value=True, key="dg_add_form")
            # 注意：您的 password_logic.py 中的 generate_password 目前只接受这几个参数
            # 如果您增加了对小写字母(可选)或符号的支持，这里也需要对应添加 st.checkbox
            st.caption("密码将在点击“保存条目”后根据以上参数生成并显示。")

        else: # 手动输入
            # 这个输入框也是表单的一部分
            password_to_save_on_submit = st.text_input("请输入密码:", type="password", key="manual_pw_add_form")

        # 表单的提交按钮
        submitted = st.form_submit_button("💾 保存条目")

        if submitted: # 只有当点击了 "保存条目" 按钮后，这里的代码才会执行
            if not platform or not username:
                st.error("平台名称和用户名不能为空！")
            else:
                actual_password_to_save = ""
                if password_option == "自动生成一个新密码":
                    # 在表单提交后，根据表单内获取的参数生成密码
                    # 确保您的 generate_password 函数能处理这些参数
                    # 您的 generate_password 默认包含小写字母，所以这里我们检查大写和数字是否至少选一个
                    if not (use_uppercase_add or use_digits_add): 
                        st.error("自动生成密码时，请至少选择一种字符类型（大写字母或数字）！")
                    else:
                        actual_password_to_save = generate_password(
                            length=pw_length_add, 
                            use_uppercase=use_uppercase_add, 
                            use_digits=use_digits_add
                        )
                        st.info(f"为 {platform} 生成并保存的密码是: {actual_password_to_save}") # 提交后显示密码
                else: # 手动输入
                    actual_password_to_save = password_to_save_on_submit 
                
                # 再次检查密码是否为空（特别是手动输入时）
                if not actual_password_to_save and password_option == "手动输入已有密码":
                    st.error("手动输入的密码不能为空！")
                elif actual_password_to_save: # 确保有密码可保存
                    success, message = streamlit_add_entry(platform, username, actual_password_to_save)
                    if success:
                        st.success(message)
                        # 为刚刚保存的条目提供一个即时下载的选项
                        entry_details_to_download = f"Platform: {platform}\nUsername: {username}\nPassword: {actual_password_to_save}"
                        st.download_button(
                            label="📥 下载此条目信息 (txt)",
                            data=entry_details_to_download,
                            file_name=f"{platform}_credentials.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error(message)

elif menu_choice == "查看所有条目":
    st.subheader("📖 查看所有密码条目")
    if st.button("🔄 刷新/显示所有条目"):
        entries, error_message = streamlit_get_all_entries()
        if error_message:
            st.warning(error_message)
        elif entries:
            st.info(f"共找到 {len(entries)} 个条目。")
            # 为了安全，我们不在网页上直接明文显示所有密码
            # 您可以选择用更安全的方式展示，或者只展示平台和用户名
            # 这里我们用 st.expander 来逐条显示，并默认隐藏密码
            for i, entry in enumerate(entries):
                with st.expander(f"条目 {i+1}: {entry['platform']} - 用户名: {entry['username']}"):
                    st.write(f"**平台:** {entry['platform']}")
                    st.write(f"**用户名:** {entry['username']}")
                    # 在真实应用中，直接显示密码非常不安全！
                    # 这里仅为演示MVP功能，真实应用需要加密存储和更安全的展示方式。
                    st.write(f"**密码:** {entry['password']}") 
                    st.caption("警告：直接显示密码不安全，请谨慎操作！")
            st.balloons() # 来点庆祝！
        else: # 正常情况下streamlit_get_all_entries会返回None和提示信息
            st.info("保险库中没有条目。")


elif menu_choice == "搜索密码条目":
    st.subheader("🔍 搜索密码条目")
    search_term = st.text_input("输入平台名称进行搜索 (不区分大小写):", key="search_term")
    if st.button("开始搜索", key="search_button"):
        entries, error_message = streamlit_search_entries(search_term)
        if error_message:
            st.warning(error_message)
        elif entries:
            st.info(f"为 '{search_term}' 找到 {len(entries)} 个匹配条目。")
            for i, entry in enumerate(entries):
                with st.expander(f"匹配 {i+1}: {entry['platform']} - 用户名: {entry['username']}"):
                    st.write(f"**平台:** {entry['platform']}")
                    st.write(f"**用户名:** {entry['username']}")
                    st.write(f"**密码:** {entry['password']}") # 同样，注意安全风险
                    st.caption("警告：直接显示密码不安全，请谨慎操作！")
        # else分支由streamlit_search_entries的error_message处理


elif menu_choice == "独立生成密码":
    st.subheader("✨ 独立生成一个新密码")
    pw_length_gen = st.number_input("设置密码长度:", min_value=8, max_value=128, value=16, step=1, key="pw_len_gen")
    use_uppercase_gen = st.checkbox("包含大写字母 (A-Z)", value=True, key="uc_gen")
    use_digits_gen = st.checkbox("包含数字 (0-9)", value=True, key="dg_gen")
    # 您的原始 generate_password 似乎没有小写和符号的选项，这里保持一致
    # 如果 password_logic.py 中的 generate_password 更新了，这里也要对应更新

    if st.button("🚀 生成独立密码", key="gen_standalone"):
        if not (use_uppercase_gen or use_digits_gen): # 假设您的函数至少需要一种字符
             st.error("请至少选择一种字符类型 (大写字母或数字)！")
        else:
            try:
                standalone_password = generate_password(
                    length=pw_length_gen, 
                    use_uppercase=use_uppercase_gen, 
                    use_digits=use_digits_gen
                )
                st.write("生成的密码是:")
                st.code(standalone_password, language=None)
                st.success("独立密码已生成！")

                # 提供下载按钮
                st.download_button(
                    label="📥 下载这个密码 (txt)",
                    data=standalone_password,
                    file_name="standalone_password.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"生成独立密码时发生错误: {e}")