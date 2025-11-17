import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import backend as db
from datetime import datetime
import time
import base64

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="StockFlow Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------
st.markdown("""
<style>
    .main {background-color:#f8f9fa;padding:20px;}
    .block-container {padding-top:2rem;padding-bottom:2rem;max-width:100%;}
    .dashboard-header{
        background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
        padding:30px;border-radius:15px;color:white;margin-bottom:30px;
        box-shadow:0 4px 15px rgba(0,0,0,0.1);
    }
    .dashboard-title{font-size:32px;font-weight:700;margin:0;}
    .dashboard-subtitle{font-size:16px;opacity:0.9;margin-top:5px;}
    .metric-card{
        background:white;border-radius:12px;padding:20px;
        box-shadow:0 2px 8px rgba(0,0,0,0.08);transition:transform .2s;
        margin-bottom:20px;height:100%;min-height:140px;
    }
    .metric-card:hover{transform:translateY(-5px);box-shadow:0 4px 12px rgba(0,0,0,0.12);}
    .metric-value{font-size:32px;font-weight:700;color:#2c3e50;margin:10px 0;}
    .metric-label{font-size:14px;color:#7f8c8d;font-weight:500;text-transform:uppercase;letter-spacing:.5px;}
    .metric-change{font-size:13px;padding:4px 8px;border-radius:6px;display:inline-block;margin-top:8px;}
    .metric-change.positive{background:#d4edda;color:#155724;}
    .section-header{font-size:20px;font-weight:600;color:#2c3e50;margin:30px 0 15px 0;padding-bottom:10px;border-bottom:2px solid #e9ecef;}
    .stButton>button{border-radius:8px;padding:8px 20px;font-weight:500;transition:all .3s;border:none;}
    .status-badge{padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600;}
    .status-instock{background:#d4edda;color:#155724;}
    .status-outofstock{background:#f8d7da;color:#721c24;}
    .status-lowstock{background:#fff3cd;color:#856404;}
    #MainMenu,footer{visibility:hidden;}
    .low-stock-warning{background:#fff3cd;color:#856404;padding:8px;border-radius:6px;font-size:13px;margin-top:5px;}
    .voice-btn{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:10px 20px;border-radius:25px;cursor:pointer;transition:all .3s;}
    .voice-btn:hover{transform:scale(1.05);box-shadow:0 4px 12px rgba(102,126,234,0.3);}
    .voice-response{
        background:#e3f2fd;
        padding:15px;
        border-radius:10px;
        border-left:4px solid #2196f3;
        margin:10px 0;
        color:#333 !important;
        font-size:16px;
        line-height:1.5;
    }
    .voice-response strong {
        color:#1565c0 !important;
    }
    .chat-container{background:#f8f9fa;border-radius:15px;padding:20px;margin-bottom:20px;}
    .chat-message{max-width:80%;margin-bottom:15px;padding:12px 16px;border-radius:18px;line-height:1.4;color:#333;}
    .user-message{background:#667eea;color:white;margin-left:auto;border-bottom-right-radius:5px;}
    .assistant-message{background:white;color:#333;border:1px solid #e1e5e9;border-bottom-left-radius:5px;}
    .chat-timestamp{font-size:11px;color:#7f8c8d;margin-top:5px;}
    .chat-input-container{background:white;border-radius:25px;padding:10px;border:1px solid #e1e5e9;}
    
    /* Fix for Streamlit markdown text color */
    .stMarkdown {
        color: #333 !important;
    }
    .stMarkdown p {
        color: #333 !important;
    }
    .stAlert {
        color: #333 !important;
    }
    /* Fix for radio buttons */
    .stRadio > div {
        flex-direction: column;
    }
    .stRadio > div > label {
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        transition: all 0.3s;
    }
    .stRadio > div > label:hover {
        background-color: #f8f9fa;
    }
    .stRadio > div > label[data-testid="stRadioLabel"] > div:first-child {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------------------------
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'voice_listening' not in st.session_state:
    st.session_state.voice_listening = False
if 'last_voice_response' not in st.session_state:
    st.session_state.last_voice_response = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chat_assistant' not in st.session_state:
    st.session_state.chat_assistant = None
if 'chat_input_key' not in st.session_state:
    st.session_state.chat_input_key = 0

# ----------------------------------------------------------------------
# LOGIN PAGE WITH REGISTRATION
# ----------------------------------------------------------------------
if st.session_state.user is None:
    st.markdown("""
        <div style='text-align:center;padding:50px;'>
            <h1 style='color:#667eea;font-size:48px;'>StockFlow</h1>
            <p style='font-size:18px;color:#7f8c8d;'>Modern Inventory Management System</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("<div style='background:white;padding:40px;border-radius:15px;box-shadow:0 4px 20px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)

            # Tabs: Login | Register
            tab1, tab2 = st.tabs(["Login", "Create Account"])

            # ------------------- LOGIN -------------------
            with tab1:
                st.markdown("<h3 style='text-align:center;margin-bottom:30px;'>Login to Dashboard</h3>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Enter your username", key="login_user")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

                c1, c2, c3 = st.columns([1, 2, 1])
                with c2:
                    if st.button("Login", use_container_width=True, type="primary"):
                        if username and password:
                            user = db.verify_user(username, password)
                            if user:
                                st.session_state.user = user
                                st.success("Login successful!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Invalid credentials")
                                st.info("Try: admin/admin123, emp1/emp123, cust1/cust123")
                        else:
                            st.warning("Please enter username and password")

            # ------------------- REGISTER -------------------
            with tab2:
                st.markdown("<h3 style='text-align:center;margin-bottom:30px;'>Create New Account</h3>", unsafe_allow_html=True)
                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                new_password = st.text_input("Password", type="password", placeholder="Create password", key="reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
                role = st.selectbox("Role", ["customer", "employee"], key="reg_role")

                c1, c2, c3 = st.columns([1, 2, 1])
                with c2:
                    if st.button("Register", use_container_width=True, type="primary"):
                        if not new_username or not new_password:
                            st.error("Please fill all fields")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(new_password) < 4:
                            st.error("Password must be at least 4 characters")
                        else:
                            success, msg = db.register_user(new_username, new_password, role)
                            if success:
                                st.success(msg)
                                # Auto-login after registration
                                user = db.verify_user(new_username, new_password)
                                st.session_state.user = user
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("""
                <div style='text-align:center;margin-top:20px;color:#7f8c8d;'>
                    <small>Demo Accounts:<br>
                    Admin: admin/admin123 | Employee: emp1/emp123 | Customer: cust1/cust123</small>
                </div>
            """, unsafe_allow_html=True)

    st.stop()

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
user = st.session_state.user
role = user.get("role", "customer").lower()

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:20px;'><h2 style='color:#667eea;'>StockFlow</h2></div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                    padding:20px;border-radius:10px;color:white;margin-bottom:20px;'>
            <div style='font-size:14px;opacity:.9;'>Welcome,</div>
            <div style='font-size:20px;font-weight:600;'>{user.get('username','User')}</div>
            <div style='font-size:12px;opacity:.8;margin-top:5px;'>Role: {role.capitalize()}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    
    # Define navigation options based on role
    if role == "admin":
        nav_options = ["Dashboard", "Products", "Orders", "Users", "Admin Panel", "Team Analytics", "Voice Assistant", "Chat Assistant"]
        icons = ["📊", "📦", "🛒", "👥", "⚙", "📈", "🎤", "💬"]
    elif role == "employee":
        nav_options = ["Dashboard", "Products", "Orders", "Voice Assistant", "Chat Assistant"]
        icons = ["📊", "📦", "🛒", "🎤", "💬"]
    else:  # customer
        nav_options = ["Products", "Purchase History", "Favorites", "Feedback", "Voice Assistant", "Chat Assistant"]
        icons = ["📦", "📋", "❤", "💬", "🎤", "💬"]
    
    # Create navigation with icons
    nav_with_icons = [f"{icons[i]} {option}" for i, option in enumerate(nav_options)]
    
    # Get current page index
    current_index = 0
    if st.session_state.current_page in nav_options:
        current_index = nav_options.index(st.session_state.current_page)
    
    selected_nav = st.radio("Go to", nav_with_icons, index=current_index, label_visibility="collapsed")
    
    # Extract page name from selected navigation
    selected_page = selected_nav.split(" ", 1)[1]
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    st.markdown("---")
    
    # Assistant Buttons in Sidebar
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Voice", use_container_width=True, key="sidebar_voice"):
            st.session_state.current_page = "Voice Assistant"
            st.rerun()
    with col2:
        if st.button("💬 Chat", use_container_width=True, key="sidebar_chat"):
            st.session_state.current_page = "Chat Assistant"
            st.rerun()
    
    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ----------------------------------------------------------------------
# VOICE ASSISTANT PAGE
# ----------------------------------------------------------------------
if st.session_state.current_page == "Voice Assistant":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Voice Assistant</div>
            <div class='dashboard-subtitle'>Ask me about stock, prices, sales, and more!</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎤 Voice Commands")
        st.markdown("""
        Try saying:
        - *"What's our current stock?"*
        - *"How many low stock items?"*
        - *"What's the price of iPhone?"*
        - *"Show me sales information"*
        - *"What can you do?"*
        """)
        
        # Voice input button
        if st.button("🎤 Start Listening", key="voice_listen", use_container_width=True, type="primary"):
            st.session_state.voice_listening = True
            st.info("🎤 Listening... Speak now!")
            
            # Use a spinner while listening
            with st.spinner("Processing your voice command..."):
                command = db.voice_assistant.listen()
                
                if command in ["timeout", "unknown", "error"]:
                    responses = {
                        "timeout": "I didn't hear anything. Please try again.",
                        "unknown": "I didn't understand that. Please try again.",
                        "error": "There was an error with voice recognition. Please try again."
                    }
                    st.session_state.last_voice_response = responses[command]
                else:
                    products_df = db.get_products()
                    response = db.voice_assistant.process_voice_command(command, products_df, role)
                    st.session_state.last_voice_response = response
                    
                    # Speak the response
                    db.voice_assistant.speak(response)
            
            st.session_state.voice_listening = False
            st.rerun()
    
    with col2:
        st.markdown("### 🔍 Quick Actions")
        quick_actions = [
            "Check total stock",
            "View low stock items", 
            "iPhone price",
            "Sales summary"
        ]
        
        for action in quick_actions:
            if st.button(action, key=f"qa_{action}", use_container_width=True):
                products_df = db.get_products()
                response = db.voice_assistant.process_voice_command(action, products_df, role)
                st.session_state.last_voice_response = response
                db.voice_assistant.speak(response)
                st.rerun()
    
    # Display voice response - FIXED VISIBILITY
    if st.session_state.last_voice_response:
        st.markdown("### 💬 Response")
        # Use st.info for better visibility
        st.info(st.session_state.last_voice_response)
        
        # Also show in the styled box
        st.markdown(f"""
        <div class='voice-response'>
            <strong>Assistant:</strong> {st.session_state.last_voice_response}
        </div>
        """, unsafe_allow_html=True)
    
    # Voice settings
    with st.expander("Voice Settings"):
        st.info("Voice features require microphone access. Make sure to allow microphone permissions in your browser.")
        if st.button("Test Voice Output", key="test_voice"):
            db.voice_assistant.speak("Voice assistant is working properly!")
            st.success("Voice test completed! You should have heard the message.")

# ----------------------------------------------------------------------
# CHAT ASSISTANT PAGE - FIXED VERSION
# ----------------------------------------------------------------------
elif st.session_state.current_page == "Chat Assistant":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Chat Assistant</div>
            <div class='dashboard-subtitle'>Get instant help with stock, prices, and sales information</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat assistant in session state
    if st.session_state.chat_assistant is None:
        st.session_state.chat_assistant = db.ChatAssistant()
    
    # Display chat messages
    st.markdown("### 💬 Conversation")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        conversation_history = st.session_state.chat_assistant.get_conversation_history()
        
        if not conversation_history:
            # Welcome message
            st.markdown("""
            <div style='text-align:center;padding:40px;color:#7f8c8d;'>
                <h3>👋 Hello! I'm your StockFlow Assistant</h3>
                <p>I can help you with stock information, product prices, sales data, and more!</p>
                <p><strong>Try asking:</strong></p>
                <ul style='text-align:left;display:inline-block;'>
                    <li>"Show me low stock items"</li>
                    <li>"What's the price of iPhone?"</li>
                    <li>"How are our sales?"</li>
                    <li>"My purchase history"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display all messages in the conversation
            for msg in conversation_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div style='display:flex;justify-content:flex-end;margin-bottom:10px;'>
                        <div class='chat-message user-message'>
                            {msg['message']}
                            <div class='chat-timestamp'>{msg['timestamp'].strftime('%H:%M')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Use st.markdown for assistant messages to ensure visibility
                    st.markdown(f"""
                    <div style='display:flex;justify-content:flex-start;margin-bottom:10px;'>
                        <div class='chat-message assistant-message'>
                            {msg['message']}
                            <div class='chat-timestamp'>{msg['timestamp'].strftime('%H:%M')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat input at the bottom - FIXED VERSION
    st.markdown("---")
    st.markdown("### 💭 Ask me anything")
    
    # Use a form to handle chat input properly
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "Type your message...", 
                placeholder="Ask about stock, prices, sales, etc...",
                label_visibility="collapsed",
                key=f"chat_input_{st.session_state.chat_input_key}"
            )
        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True, type="primary")
    
    # Quick action buttons
    st.markdown("**Quick Questions:**")
    quick_questions = [
        "Show low stock items",
        "What's the price of iPhone?",
        "Sales summary",
        "My purchase history",
        "Help"
    ]
    
    cols = st.columns(len(quick_questions))
    for i, question in enumerate(quick_questions):
        with cols[i]:
            if st.button(question, key=f"qq_{i}", use_container_width=True):
                # Process the quick question
                products_df = db.get_products()
                user_id = user.get("id")
                response = st.session_state.chat_assistant.get_response(
                    question, products_df, role, user_id
                )
                st.rerun()
    
    # Process user input from form
    if submitted and user_input.strip():
        products_df = db.get_products()
        user_id = user.get("id")
        
        # Get response from chat assistant
        response = st.session_state.chat_assistant.get_response(
            user_input, products_df, role, user_id
        )
        
        # Increment the key to reset the input field
        st.session_state.chat_input_key += 1
        st.rerun()
    
    # Clear conversation button
    st.markdown("---")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.chat_assistant.clear_history()
        st.rerun()

# ----------------------------------------------------------------------
# TEAM ANALYTICS PAGE (ADMIN ONLY)
# ----------------------------------------------------------------------
elif st.session_state.current_page == "Team Analytics" and role == "admin":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Team Analytics</div>
            <div class='dashboard-subtitle'>Manage and analyze your team and customers</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Get users data
    users_df = db.get_users()
    
    if users_df.empty:
        st.info("No users found in the system.")
    else:
        # User statistics
        total_users = len(users_df)
        employees = len(users_df[users_df['role'] == 'employee'])
        customers = len(users_df[users_df['role'] == 'customer'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Employees", employees)
        with col3:
            st.metric("Customers", customers)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # User role distribution chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### User Role Distribution")
            role_counts = users_df['role'].value_counts()
            fig = px.pie(
                values=role_counts.values,
                names=role_counts.index,
                color_discrete_sequence=['#667eea', '#4a90e2', '#5cb3cc']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### User Registration Trend")
            # Convert created_at to datetime and count by month
            users_df['created_at'] = pd.to_datetime(users_df['created_at'])
            monthly_registrations = users_df.groupby(users_df['created_at'].dt.to_period('M')).size()
            
            fig = px.bar(
                x=monthly_registrations.index.astype(str),
                y=monthly_registrations.values,
                labels={'x': 'Month', 'y': 'Registrations'},
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### User Details")
        
        # Filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            search_user = st.text_input("Search users...", placeholder="Search by username")
        with col2:
            filter_role = st.selectbox("Filter by role", ["All", "admin", "employee", "customer"])
        
        # Apply filters
        filtered_users = users_df.copy()
        if search_user:
            filtered_users = filtered_users[filtered_users['username'].str.contains(search_user, case=False, na=False)]
        if filter_role != "All":
            filtered_users = filtered_users[filtered_users['role'] == filter_role]
        
        # Display user table
        if not filtered_users.empty:
            for _, user_row in filtered_users.iterrows():
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    with c1:
                        st.markdown(f"**{user_row['username']}**")
                        st.caption(f"ID: {user_row['id']} | Registered: {user_row['created_at']}")
                    with c2:
                        role_color = "primary" if user_row['role'] == 'admin' else "secondary" if user_row['role'] == 'employee' else "success"
                        st.markdown(f"<span class='status-badge status-{role_color}'>{user_row['role'].capitalize()}</span>", unsafe_allow_html=True)
                    with c3:
                        # Show user activity based on role
                        if user_row['role'] == 'customer':
                            purchases = db.get_purchase_history(user_row['id'])
                            total_spent = (purchases['price'] * purchases['quantity']).sum() if not purchases.empty else 0
                            st.markdown(f"**Total Spent:** ₹{total_spent:,.0f}")
                        elif user_row['role'] == 'employee':
                            st.markdown("**Employee**")
                        else:
                            st.markdown("**Administrator**")
                    with c4:
                        if user_row['role'] != 'admin':  # Prevent deleting admin
                            if st.button("Delete", key=f"del_team_{user_row['id']}"):
                                if db.delete_user(user_row['id']):
                                    st.success("User deleted!")
                                    st.rerun()
                                else:
                                    st.error("Cannot delete this user")
                    st.divider()
        else:
            st.info("No users match the current filters.")

# ----------------------------------------------------------------------
# CUSTOMER PAGES
# ----------------------------------------------------------------------
elif role == "customer":
    user_id = user.get("id", 1)

    # ----- PRODUCTS -----
    if st.session_state.current_page == "Products":
        st.markdown("""
            <div class='dashboard-header'>
                <div class='dashboard-title'>Welcome to StockFlow Store</div>
                <div class='dashboard-subtitle'>Browse our premium products</div>
            </div>
        """, unsafe_allow_html=True)

        prods = db.get_products()
        # Filter only available products (stock > 0)
        avail = prods[prods['stock'] > 0].copy()
        
        if avail.empty:
            st.info("All products are currently out of stock. Please check back later.")
        else:
            cats = ["All"] + list(avail['category'].unique())
            sel = st.selectbox("Filter by Category", cats, key="cust_cat")
            df = avail if sel=="All" else avail[avail['category']==sel]

            st.markdown(f"*Showing {len(df)} products*")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display products in cards (3 columns)
            cols = st.columns(3)
            for i, (_, r) in enumerate(df.iterrows()):
                with cols[i % 3]:
                    low_stock = r['stock'] < 10
                    out_of_stock = r['stock'] == 0
                    
                    st.markdown(f"""
                        <div class='metric-card'>
                            <h4>{r['name']}</h4>
                            <p style='color:#7f8c8d;font-size:14px;margin:5px 0;'>{r['brand']} | {r['category']}</p>
                            <div style='font-size:22px;font-weight:700;color:#667eea;margin:10px 0;'>
                                ₹{r['price']:,.0f}
                            </div>
                            <div style='margin-bottom:8px;'>
                                Stock: <strong style='color:{"orange" if low_stock else "green" if not out_of_stock else "red"}'>
                                {r['stock']}</strong>
                            </div>
                            {f"<div class='low-stock-warning'>⚠ Low stock - Order soon!</div>" if low_stock and not out_of_stock else ""}
                        </div>
                    """, unsafe_allow_html=True)

                    # Buttons for favorite and purchase
                    fcol, bcol = st.columns(2)
                    with fcol:
                        fav = db.is_favorite(user_id, r['id'])
                        lbl = "❤ Remove" if fav else "🤍 Favorite"
                        if st.button(lbl, key=f"f_{r['id']}", use_container_width=True):
                            if fav:
                                db.remove_favorite(user_id, r['id'])
                            else:
                                db.add_favorite(user_id, r['id'], r['name'], r['price'])
                            st.rerun()
                    with bcol:
                        if st.button("🛒 Buy Now", key=f"b_{r['id']}", type="primary", use_container_width=True):
                            if db.purchase_product(user_id, r['id'], r['name'], r['price'], 1):
                                st.success(f"Successfully purchased {r['name']}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("Failed to complete purchase")

    # ----- PURCHASE HISTORY -----
    elif st.session_state.current_page == "Purchase History":
        st.markdown("""
            <div class='dashboard-header'>
                <div class='dashboard-title'>Purchase History</div>
                <div class='dashboard-subtitle'>Your order history and past purchases</div>
            </div>
        """, unsafe_allow_html=True)
        
        hist = db.get_purchase_history(user_id)
        if hist.empty:
            st.info("No purchases yet. Start shopping to see your history here!")
        else:
            total_spent = (hist['price'] * hist['quantity']).sum()
            st.metric("Total Spent", f"₹{total_spent:,.0f}")
            
            for _,r in hist.iterrows():
                st.markdown(f"""
                    <div style='background:#f8f9fa;padding:15px;border-radius:8px;margin-bottom:10px;
                               border-left:4px solid #667eea;'>
                        <div style='font-weight:600;font-size:16px;'>{r['product_name']}</div>
                        <div style='color:#667eea;font-weight:500;margin:5px 0;'>
                            ₹{r['price']:,.0f} × {r['quantity']} = ₹{r['price'] * r['quantity']:,.0f}
                        </div>
                        <div style='font-size:12px;color:#7f8c8d;margin-top:5px;'>
                            Purchased on: {r['purchase_date']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # ----- FAVORITES -----
    elif st.session_state.current_page == "Favorites":
        st.markdown("""
            <div class='dashboard-header'>
                <div class='dashboard-title'>Your Favorites</div>
                <div class='dashboard-subtitle'>Products you've added to your wishlist</div>
            </div>
        """, unsafe_allow_html=True)
        
        favs = db.get_favorites(user_id)
        if favs.empty:
            st.info("No favorites yet. Add some products to your favorites from the Products page!")
        else:
            for _,r in favs.iterrows():
                c1,c2,c3 = st.columns([3,2,2])
                with c1:
                    st.markdown(f"{r['product_name']}")
                    st.caption(f"₹{r['price']:,.0f}")
                with c2:
                    if st.button("Remove", key=f"rf_{r['product_id']}", use_container_width=True):
                        db.remove_favorite(user_id, r['product_id'])
                        st.rerun()
                with c3:
                    if st.button("Buy Now", key=f"bf_{r['product_id']}", type="primary", use_container_width=True):
                        db.purchase_product(user_id, r['product_id'], r['product_name'], r['price'], 1)
                        st.success("Purchased successfully!")
                        st.rerun()

    # ----- FEEDBACK -----
    elif st.session_state.current_page == "Feedback":
        st.markdown("""
            <div class='dashboard-header'>
                <div class='dashboard-title'>Customer Feedback</div>
                <div class='dashboard-subtitle'>We value your opinion</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("feedback_form"):
            rating = st.slider("Rate your experience", 1, 5, 4, 
                              help="1 = Very Poor, 5 = Excellent")
            text = st.text_area("Your feedback", placeholder="Tell us about your experience...", height=100)
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                if text.strip():
                    db.save_feedback(user_id, rating, text)
                    st.success("Thank you for your feedback! We appreciate your input.")
                    st.balloons()
                else:
                    st.warning("Please enter your feedback before submitting.")

# ----------------------------------------------------------------------
# EMPLOYEE DASHBOARD
# ----------------------------------------------------------------------
elif role == "employee" and st.session_state.current_page == "Dashboard":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Employee Dashboard</div>
            <div class='dashboard-subtitle'>Manage daily operations and inventory</div>
        </div>
    """, unsafe_allow_html=True)

    prods = db.get_products()
    c1,c2,c3 = st.columns(3)
    with c1: 
        st.metric("Total Products", len(prods))
    with c2: 
        low_stock = len(prods[prods['stock']<10])
        st.metric("Low Stock (<10)", low_stock, delta=f"-{low_stock}" if low_stock > 0 else None)
    with c3: 
        out_of_stock = len(prods[prods['stock']==0])
        st.metric("Out of Stock", out_of_stock)

    st.markdown("<h3 class='section-header'>Low Stock Alerts</h3>", unsafe_allow_html=True)
    low = prods[prods['stock']<10]
    if not low.empty:
        for _,r in low.iterrows():
            if r['stock'] == 0:
                st.error(f"{r['name']}** - OUT OF STOCK!")
            else:
                st.warning(f"{r['name']}** - only {r['stock']} left in stock!")
    else:
        st.success("All items sufficiently stocked")

    st.markdown("<h3 class='section-header'>Report Issue to Admin</h3>", unsafe_allow_html=True)
    with st.form("issue_form"):
        message = st.text_area("Describe the issue", placeholder="What issue are you facing?")
        submitted = st.form_submit_button("Send Message to Admin")
        if submitted:
            if message.strip():
                db.send_message(user['username'], message)
                st.success("Message sent to admin!")
            else:
                st.warning("Please describe the issue before sending.")

# ----------------------------------------------------------------------
# ADMIN DASHBOARD
# ----------------------------------------------------------------------
elif role == "admin" and st.session_state.current_page == "Dashboard":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Welcome back, admin!</div>
            <div class='dashboard-subtitle'>Here's what's happening with your inventory today.</div>
        </div>
    """, unsafe_allow_html=True)

    metrics = db.get_dashboard_metrics()
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex;align-items:center;justify-content:space-between;'>
                    <div style='flex:1;'>
                        <div class='metric-label'>Total Products</div>
                        <div class='metric-value'>{metrics['total_products']:,}</div>
                        <div class='metric-change positive'>+{metrics['products_change']}%</div>
                    </div>
                    <div style='font-size:40px;margin-left:10px;'>📦</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex;align-items:center;justify-content:space-between;'>
                    <div style='flex:1;'>
                        <div class='metric-label'>Total Orders</div>
                        <div class='metric-value'>{metrics['total_orders']:,}</div>
                        <div class='metric-change positive'>+{metrics['orders_change']}%</div>
                    </div>
                    <div style='font-size:40px;margin-left:10px;'>🛒</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex;align-items:center;justify-content:space-between;'>
                    <div style='flex:1;'>
                        <div class='metric-label'>Active Customers</div>
                        <div class='metric-value'>{metrics['active_customers']:,}</div>
                        <div class='metric-change positive'>+{metrics['customers_change']}%</div>
                    </div>
                    <div style='font-size:40px;margin-left:10px;'>👥</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex;align-items:center;justify-content:space-between;'>
                    <div style='flex:1;'>
                        <div class='metric-label'>Revenue</div>
                        <div class='metric-value'>₹{metrics['revenue']:,.0f}</div>
                        <div class='metric-change positive'>+{metrics['revenue_change']}%</div>
                    </div>
                    <div style='font-size:40px;margin-left:10px;'>💰</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns([3,2])
    with col_chart1:
        st.markdown("### Sales Overview")
        sales = db.get_sales_overview()
        fig = go.Figure(data=[go.Bar(
            x=sales['month'],
            y=sales['sales'],
            text=sales['sales'],
            textposition='outside',
            marker_color='#667eea'
        )])
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("### Product Categories")
        cat = db.get_product_categories()
        fig = px.pie(cat, values='count', names='category', hole=0.5,
                     color_discrete_sequence=['#667eea','#4a90e2','#5cb3cc','#7ed8d8'])
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_act, col_prod = st.columns([2,3])
    with col_act:
        st.markdown("### Recent Activity")
        for a in db.get_recent_activity():
            st.markdown(f"""
                <div style='background:#f8f9fa;padding:15px;border-radius:8px;margin-bottom:12px;border-left:4px solid #667eea;'>
                    <div style='display:flex;align-items:center;'>
                        <span style='font-size:24px;margin-right:12px;'>{a['icon']}</span>
                        <div>
                            <div style='font-weight:500;color:#2c3e50;'>{a['text']}</div>
                            <div style='font-size:12px;color:#7f8c8d;margin-top:3px;'>{a['time']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    with col_prod:
        st.markdown("### Top Products")
        for _,r in db.get_top_products().iterrows():
            st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                           padding:15px;background:#f8f9fa;border-radius:8px;margin-bottom:10px;
                           border-left:4px solid #667eea;'>
                    <div style='font-weight:500;color:#2c3e50;font-size:15px;'>{r['product']}</div>
                    <div style='color:#667eea;font-weight:700;font-size:16px;'>₹{r['price']:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>Quick Actions</h3>", unsafe_allow_html=True)
    ca1,ca2,ca3 = st.columns(3)
    with ca1:
        if st.button("Add New Product", use_container_width=True, type="primary"):
            st.session_state.current_page = "Products"
            st.session_state.show_add_form = True
            st.rerun()
    with ca2:
        if st.button("View All Orders", use_container_width=True):
            st.session_state.current_page = "Orders"
            st.rerun()
    with ca3:
        if st.button("Team Analytics", use_container_width=True):
            st.session_state.current_page = "Team Analytics"
            st.rerun()

# ----------------------------------------------------------------------
# PRODUCTS PAGE – ADMIN / EMPLOYEE
# ----------------------------------------------------------------------
elif st.session_state.current_page == "Products" and role in ["admin","employee"]:
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Product Management</div>
            <div class='dashboard-subtitle'>Manage your inventory and product listings</div>
        </div>
    """, unsafe_allow_html=True)

    # ---- ADD FORM (admin only) ----
    if role == "admin":
        expand = st.session_state.get("show_add_form", False)
        with st.expander("➕ Add New Product", expanded=expand):
            c1,c2,c3 = st.columns(3)
            with c1:
                brand = st.text_input("Brand Name", placeholder="e.g., Samsung", key="add_brand")
                model = st.text_input("Model", placeholder="e.g., Galaxy S24", key="add_model")
            with c2:
                price = st.number_input("Price (₹)", min_value=0.0, format="%.2f", key="add_price")
                stock = st.number_input("Stock Qty", min_value=0, value=1, step=1, key="add_stock")
            with c3:
                cat = st.selectbox("Category",["Mobile","Laptop","TV","Camera","Tablet","Appliance","Others"], key="add_cat")
                sup = st.number_input("Supplier ID", min_value=1, value=1, key="add_sup")
            b1,b2,_ = st.columns([1,1,4])
            with b1:
                if st.button("Add Product", type="primary", use_container_width=True):
                    if brand and model and price>0 and stock>0:
                        if db.add_product(brand, model, price, cat, stock, sup):
                            st.success("Product added!")
                            if "show_add_form" in st.session_state:
                                del st.session_state.show_add_form
                            st.rerun()
                        else:
                            st.error("Failed to add product")
                    else:
                        st.warning("Please fill all fields with valid values")
            with b2:
                if st.button("Cancel", use_container_width=True):
                    if "show_add_form" in st.session_state:
                        del st.session_state.show_add_form
                    st.rerun()
        if "show_add_form" in st.session_state:
            st.session_state.show_add_form = False

    # ---- INVENTORY TABLE ----
    st.markdown("<h3 class='section-header'>Product Inventory</h3>", unsafe_allow_html=True)
    products = db.get_products()
    if products.empty:
        st.info("No products found")
    else:
        cs, cf = st.columns([2,1])
        with cs:
            search = st.text_input("Search products...", placeholder="Search by name, brand, or category")
        with cf:
            filt = st.selectbox("Filter by category",["All"]+list(products['category'].unique()))
        
        df = products.copy()
        if search:
            mask = (df['name'].str.contains(search, case=False, na=False) |
                    df['brand'].str.contains(search, case=False, na=False) |
                    df['category'].str.contains(search, case=False, na=False))
            df = df[mask]
        if filt != "All":
            df = df[df['category']==filt]

        m1,m2,m3 = st.columns(3)
        with m1: 
            st.metric("Total Products", len(df))
        with m2: 
            total_value = (df['price'] * df['stock']).sum()
            st.metric("Inventory Value", f"₹{total_value:,.0f}")
        with m3: 
            low_stock_count = len(df[df['stock']<10])
            st.metric("Low Stock (<10)", low_stock_count, delta=f"-{low_stock_count}" if low_stock_count > 0 else None)
        
        st.markdown("<br>", unsafe_allow_html=True)

        for _,r in df.iterrows():
            with st.container():
                c1,c2,c3,c4,c5 = st.columns([3,2,2,2,2])
                with c1:
                    st.markdown(f"{r['name']}")
                    st.caption(f"{r['brand']} | {r['category']}")
                with c2:
                    st.markdown(f"*₹{r['price']:,.0f}*")
                with c3:
                    col = "green" if r['stock']>10 else "orange" if r['stock']>0 else "red"
                    st.markdown(f"<span style='color:{col};font-weight:600;'>Stock: {r['stock']}</span>", unsafe_allow_html=True)
                with c4:
                    sts = r.get('stock_status','In Stock')
                    if sts == 'In Stock':
                        cls = 'status-instock'
                    elif sts == 'Low Stock':
                        cls = 'status-lowstock'
                    else:
                        cls = 'status-outofstock'
                    st.markdown(f"<span class='status-badge {cls}'>{sts}</span>", unsafe_allow_html=True)
                with c5:
                    if role=="admin":
                        a1,a2 = st.columns(2)
                        with a1:
                            if st.button("🔄", key=f"t_{r['id']}", help="Toggle Status"):
                                st.info("Toggle functionality would be implemented here")
                        with a2:
                            if st.button("🗑", key=f"d_{r['id']}", help="Delete Product"):
                                if db.delete_product(r['id']):
                                    st.success("Product deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete product")
                    elif role=="employee":
                        new_stock = st.number_input("New Stock", min_value=0, value=int(r['stock']), key=f"ns_{r['id']}", label_visibility="collapsed")
                        if st.button("Update", key=f"up_{r['id']}"):
                            if db.update_product_stock_qty(r['id'], new_stock):
                                st.success("Stock updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update stock")
                st.divider()

# ----------------------------------------------------------------------
# ORDERS / USERS / ADMIN PANEL
# ----------------------------------------------------------------------
elif st.session_state.current_page == "Orders" and role in ["admin", "employee"]:
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Order Management</div>
            <div class='dashboard-subtitle'>Track and manage customer orders</div>
        </div>
    """, unsafe_allow_html=True)
    
    orders = db.get_all_purchases()
    if orders.empty:
        st.info("No orders found.")
    else:
        st.markdown("<h3 class='section-header'>All Customer Purchases</h3>", unsafe_allow_html=True)
        
        # Order statistics
        total_orders = len(orders)
        total_revenue = (orders['price'] * orders['quantity']).sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Orders", total_orders)
        with col2:
            st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
        
        for idx, r in orders.iterrows():
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3,2,2,2,2])
                with c1:
                    st.markdown(f"{r['product_name']}")
                    st.caption(f"User ID: {r['user_id']}")
                with c2:
                    st.markdown(f"*₹{r['price']:,.0f}*")
                with c3:
                    st.markdown(f"Quantity: {r['quantity']}")
                with c4:
                    st.markdown(f"Date: {r['purchase_date']}")
                with c5:
                    if role in ["admin", "employee"]:
                        if st.button("Delete", key=f"del_ord_{idx}"):
                            if db.delete_order(idx):
                                st.success("Order deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete order")
                st.divider()

elif st.session_state.current_page == "Users" and role == "admin":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>User Management</div>
            <div class='dashboard-subtitle'>Manage employees and customers</div>
        </div>
    """, unsafe_allow_html=True)
    
    users = db.get_users()
    if users.empty:
        st.info("No users found.")
    else:
        st.markdown("<h3 class='section-header'>All Users</h3>", unsafe_allow_html=True)
        
        # User statistics
        employees = len(users[users['role'] == 'employee'])
        customers = len(users[users['role'] == 'customer'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Employees", employees)
        with col2:
            st.metric("Total Customers", customers)
        
        for _, r in users.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3,2,2,2])
                with c1:
                    st.markdown(f"{r['username']}** (ID: {r['id']})")
                    st.caption(f"Registered: {r['created_at']}")
                with c2:
                    role_badge = "primary" if r['role'] == 'admin' else "secondary" if r['role'] == 'employee' else "success"
                    st.markdown(f"<span class='status-badge status-{role_badge}'>{r['role'].capitalize()}</span>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"Role: *{r['role'].capitalize()}*")
                with c4:
                    if st.button("Delete", key=f"del_u_{r['id']}"):
                        if db.delete_user(r['id']):
                            st.success("User deleted!")
                            st.rerun()
                        else:
                            st.error("Cannot delete demo users or operation failed")
                st.divider()

elif st.session_state.current_page == "Admin Panel" and role == "admin":
    st.markdown("""
        <div class='dashboard-header'>
            <div class='dashboard-title'>Admin Panel</div>
            <div class='dashboard-subtitle'>Advanced settings and system configuration</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 class='section-header'>System Overview</h3>", unsafe_allow_html=True)
    metrics = db.get_dashboard_metrics()
    users_df = db.get_users()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", len(users_df))
    with col2:
        st.metric("Total Orders", metrics['total_orders'])
    with col3:
        st.metric("Total Products", metrics['total_products'])
    with col4:
        st.metric("Total Revenue", f"₹{metrics['revenue']:,.0f}")
    
    st.markdown("<h3 class='section-header'>Messages from Employees</h3>", unsafe_allow_html=True)
    messages = db.get_messages()
    if messages.empty:
        st.info("No messages received from employees.")
    else:
        for _, r in messages.iterrows():
            st.markdown(f"""
                <div style='background:#f8f9fa;padding:15px;border-radius:8px;margin-bottom:10px;
                           border-left:4px solid #667eea;'>
                    <div style='font-weight:600;color:#2c3e50;'>{r['sender']}</div>
                    <div style='font-size:12px;color:#7f8c8d;margin-top:3px;'>{r['timestamp']}</div>
                    <div style='margin-top:8px;color:#555;'>{r['message']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<h3 class='section-header'>System Actions</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Clear All Messages", use_container_width=True):
            db.clear_messages()
            st.success("All messages cleared!")
            st.rerun()
    with col2:
        if st.button("Generate Report", use_container_width=True):
            st.info("Report generation feature would be implemented here")
    with col3:
        if st.button("System Backup", use_container_width=True):
            st.info("Backup functionality would be implemented here")

# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align:center;color:#7f8c8d;font-size:14px;padding:20px;'>
        <strong>StockFlow</strong> - Modern Inventory Management System | 
        Built with Streamlit & MySQL | © 2024
    </div>
""", unsafe_allow_html=True)