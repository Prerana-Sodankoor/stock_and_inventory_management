import mysql.connector
import pandas as pd
from mysql.connector import Error
import traceback
import hashlib
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import time

# ==================================================
# Database connection
# ==================================================
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Soda@2005",
            database="shopDB",
            auth_plugin='mysql_native_password'
        )
        return conn
    except Error as e:
        print("❌ DB connection failed:", e)
        traceback.print_exc()
        return None

# ==================================================
# Security & Hashing
# ==================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================================================
# User Authentication & Management
# ==================================================
def verify_user(username, password):
    try:
        conn = get_connection()
        if conn is None:
            return None
        
        # Use SHA2 comparison for passwords
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=SHA2(%s, 256)", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception as e:
        print("❌ verify_user error:", e)
        traceback.print_exc()
        return None

def register_user(username, password, role):
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
        
        # Check if username exists
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "Username already exists"
        
        # Insert new user with SHA2 hashing
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, SHA2(%s, 256), %s)", 
                   (username, password, role))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Registration successful!"
    except Exception as e:
        print("❌ register_user error:", e)
        traceback.print_exc()
        return False, f"Registration failed: {str(e)}"

def get_users():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        
        query = "SELECT id, username, role, created_at FROM users WHERE role != 'admin'"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_users error:", e)
        traceback.print_exc()
        return pd.DataFrame()

def delete_user(user_id):
    try:
        if user_id in [1, 2, 3]:  # Prevent deleting demo users
            return False
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ delete_user error:", e)
        traceback.print_exc()
        return False

# ==================================================
# Dashboard Analytics
# ==================================================
def get_dashboard_metrics():
    try:
        conn = get_connection()
        if conn is None:
            return default_metrics()
        
        cur = conn.cursor()
        
        # Total products
        cur.execute("SELECT COUNT(*) FROM product")
        total_products = cur.fetchone()[0]
        
        # Total orders
        cur.execute("SELECT COUNT(*) FROM orders")
        total_orders = cur.fetchone()[0]
        
        # Active customers
        cur.execute("SELECT COUNT(DISTINCT Customer_ID) FROM orders WHERE Order_Status='Completed'")
        active_customers = cur.fetchone()[0]
        
        # Revenue
        cur.execute("SELECT COALESCE(SUM(Total_Price), 0) FROM orders WHERE Order_Status='Completed'")
        revenue = cur.fetchone()[0] or 0
        
        cur.close()
        conn.close()
        
        return {
            'total_products': total_products,
            'total_orders': total_orders,
            'active_customers': active_customers,
            'revenue': revenue,
            'products_change': 12,
            'orders_change': 8,
            'customers_change': 5,
            'revenue_change': 15
        }
    except Exception as e:
        print("❌ get_dashboard_metrics error:", e)
        traceback.print_exc()
        return default_metrics()

def default_metrics():
    return {
        'total_products': 15,
        'total_orders': 15,
        'active_customers': 12,
        'revenue': 1250000,
        'products_change': 12,
        'orders_change': 8,
        'customers_change': 5,
        'revenue_change': 15
    }

def get_sales_overview():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame({'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 
                               'sales': [12000, 19000, 15000, 25000, 22000, 30000]})
        
        # Get sales data from orders
        query = """
        SELECT MONTHNAME(Date_Order) as month, SUM(Total_Price) as sales
        FROM orders 
        WHERE Order_Status = 'Completed'
        GROUP BY MONTH(Date_Order)
        ORDER BY MONTH(Date_Order)
        LIMIT 6
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_sales_overview error:", e)
        return pd.DataFrame({'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 
                           'sales': [12000, 19000, 15000, 25000, 22000, 30000]})

def get_product_categories():
    try:
        conn = get_connection()
        if conn is None:
            return default_categories()
        
        query = "SELECT Unit_Type as category, COUNT(*) as count FROM product GROUP BY Unit_Type"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_product_categories error:", e)
        return default_categories()

def default_categories():
    return pd.DataFrame({
        'category': ['Mobile', 'Laptop', 'TV', 'Camera', 'Tablet', 'Appliance'],
        'count': [5, 6, 2, 2, 1, 1]
    })

def get_recent_activity():
    activities = [
        {'icon': '📦', 'text': 'New order #1016 placed', 'time': '2 mins ago'},
        {'icon': '💰', 'text': 'Payment received for order #1015', 'time': '15 mins ago'},
        {'icon': '🔄', 'text': 'Stock updated for Galaxy S24', 'time': '1 hour ago'},
        {'icon': '👤', 'text': 'New customer registered', 'time': '2 hours ago'},
        {'icon': '📊', 'text': 'Monthly report generated', 'time': '5 hours ago'}
    ]
    return activities

def get_top_products():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame({
                'product': ['iPhone 15 Pro', 'Galaxy S24 Ultra', 'MacBook Pro', 'Sony Bravia', 'Canon R5'],
                'price': [129999, 89999, 199999, 149999, 329999]
            })
        
        query = """
        SELECT Model as product, Total_Price as price 
        FROM product 
        ORDER BY Total_Price DESC 
        LIMIT 5
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_top_products error:", e)
        return pd.DataFrame({
            'product': ['iPhone 15', 'Galaxy S24', 'ROG Zephyrus', 'ThinkPad X1', 'EOS R5'],
            'price': [129999, 79999, 149999, 134999, 329999]
        })

# ==================================================
# Product Management
# ==================================================
def get_products():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()

        query = """
        SELECT p.Product_ID AS id,
               p.Model AS name,
               b.Brand_name AS brand,
               p.Total_Price AS price,
               CASE 
                   WHEN p.Stock_Qty > 10 THEN 'In Stock'
                   WHEN p.Stock_Qty > 0 THEN 'Low Stock'
                   ELSE 'Out of Stock'
               END AS stock_status,
               p.Stock_Qty AS stock,
               p.Unit_Type AS category
        FROM product p
        LEFT JOIN brand b ON p.Brand_ID = b.Brand_ID
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_products SQL error:", e)
        traceback.print_exc()
        return pd.DataFrame()

def add_product(brand_name, model, price, category, stock, supplier_id):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        
        # First, get or create brand
        cur.execute("SELECT Brand_ID FROM brand WHERE Brand_name = %s", (brand_name,))
        result = cur.fetchone()
        if result:
            brand_id = result[0]
        else:
            cur.execute("INSERT INTO brand (Brand_name, Date_Rec) VALUES (%s, %s)", 
                       (brand_name, datetime.now().date()))
            brand_id = cur.lastrowid
        
        # Add product
        availability = 'In Stock' if stock > 0 else 'Out of Stock'
        cur.execute("""
            INSERT INTO product (Brand_ID, Model, Total_Price, Availability, Stock_Qty, Unit_Type, Supplier_ID, Date_Rec)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (brand_id, model, price, availability, stock, category, supplier_id, datetime.now().date()))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ add_product error:", e)
        traceback.print_exc()
        return False

def update_product_stock_qty(product_id, new_qty):
    try:
        conn = get_connection()
        cur = conn.cursor()
        availability = 'In Stock' if new_qty > 0 else 'Out of Stock'
        cur.execute("UPDATE product SET Stock_Qty = %s, Availability = %s WHERE Product_ID = %s", 
                   (new_qty, availability, product_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ update_product_stock_qty error:", e)
        traceback.print_exc()
        return False

def delete_product(product_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM product WHERE Product_ID = %s", (product_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ delete_product error:", e)
        traceback.print_exc()
        return False

# ==================================================
# Purchase Management
# ==================================================
def purchase_product(user_id, product_id, product_name, price, quantity):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        
        # Create purchase record
        cur.execute("""
            INSERT INTO purchases (user_id, product_id, product_name, price, quantity, purchase_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, product_id, product_name, price, quantity, datetime.now()))
        
        # Update stock
        cur.execute("SELECT Stock_Qty FROM product WHERE Product_ID = %s", (product_id,))
        result = cur.fetchone()
        if result:
            current_stock = result[0]
            new_stock = current_stock - quantity
            if new_stock < 0:
                conn.rollback()
                return False
            update_product_stock_qty(product_id, new_stock)
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ purchase_product error:", e)
        traceback.print_exc()
        return False

def get_purchase_history(user_id):
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        
        query = """
        SELECT product_name, price, quantity, purchase_date 
        FROM purchases 
        WHERE user_id = %s 
        ORDER BY purchase_date DESC
        """
        df = pd.read_sql(query, conn, params=[user_id])
        conn.close()
        return df
    except Exception as e:
        print("❌ get_purchase_history error:", e)
        return pd.DataFrame()

def get_all_purchases():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        
        query = """
        SELECT p.user_id, p.product_name, p.price, p.quantity, p.purchase_date
        FROM purchases p
        ORDER BY p.purchase_date DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_all_purchases error:", e)
        return pd.DataFrame()

def delete_order(order_id):
    try:
        # For demo - in real app, you'd delete from orders table
        print(f"Order {order_id} delete requested")
        return True
    except Exception as e:
        print("❌ delete_order error:", e)
        return False

# ==================================================
# Favorites Management
# ==================================================
def get_favorites(user_id):
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        
        query = """
        SELECT product_id, product_name, price 
        FROM favorites 
        WHERE user_id = %s
        """
        df = pd.read_sql(query, conn, params=[user_id])
        conn.close()
        return df
    except Exception as e:
        print("❌ get_favorites error:", e)
        return pd.DataFrame()

def add_favorite(user_id, product_id, product_name, price):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        cur.execute("""
            INSERT IGNORE INTO favorites (user_id, product_id, product_name, price)
            VALUES (%s, %s, %s, %s)
        """, (user_id, product_id, product_name, price))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ add_favorite error:", e)
        traceback.print_exc()
        return False

def remove_favorite(user_id, product_id):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        cur.execute("DELETE FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ remove_favorite error:", e)
        traceback.print_exc()
        return False

def is_favorite(user_id, product_id):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None
    except Exception as e:
        print("❌ is_favorite error:", e)
        return False

# ==================================================
# Feedback & Messaging
# ==================================================
def save_feedback(user_id, rating, feedback_text):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        cur.execute("INSERT INTO feedback (user_id, rating, feedback) VALUES (%s, %s, %s)", 
                   (user_id, rating, feedback_text))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ save_feedback error:", e)
        traceback.print_exc()
        return False

def send_message(sender, message):
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (sender, message) VALUES (%s, %s)", (sender, message))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ send_message error:", e)
        traceback.print_exc()
        return False

def get_messages():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        
        query = "SELECT sender, message, timestamp FROM messages ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ get_messages error:", e)
        return pd.DataFrame()

def clear_messages():
    try:
        conn = get_connection()
        if conn is None:
            return False
        
        cur = conn.cursor()
        cur.execute("DELETE FROM messages")
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ clear_messages error:", e)
        traceback.print_exc()
        return False

# ==================================================
# VOICE ASSISTANT FEATURE
# ==================================================
class VoiceAssistant:
    def __init__(self):
        try:
            self.recognizer = sr.Recognizer()
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            # Set voice properties
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  # Female voice if available
        except Exception as e:
            print("❌ Voice assistant initialization error:", e)
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print("❌ Text-to-speech error:", e)
    
    def listen(self):
        """Listen for voice input"""
        try:
            with sr.Microphone() as source:
                print("🔊 Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🎤 Listening... Speak now!")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio)
            print(f"👂 You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unknown"
        except Exception as e:
            print("❌ Speech recognition error:", e)
            return "error"
    
    def process_voice_command(self, command, products_df, user_role):
        """Process voice commands and return response"""
        command = command.lower()
        response = ""
        
        if any(word in command for word in ['stock', 'inventory', 'available']):
            # Stock enquiry
            if 'low' in command:
                low_stock = products_df[products_df['stock'] < 10]
                count = len(low_stock)
                if count > 0:
                    product_names = ", ".join(low_stock['name'].head(3).tolist())
                    response = f"You have {count} products with low stock. Including: {product_names}"
                else:
                    response = "No products are low on stock. All items are sufficiently stocked."
            else:
                total_stock = products_df['stock'].sum()
                total_products = len(products_df)
                out_of_stock = len(products_df[products_df['stock'] == 0])
                response = f"You have {total_products} products with total {total_stock} items in stock. {out_of_stock} products are out of stock."
                
        elif any(word in command for word in ['price', 'cost', 'how much']):
            # Price enquiry
            for product in ['iphone', 'samsung', 'macbook', 'tv', 'camera', 'laptop']:
                if product in command:
                    matching = products_df[products_df['name'].str.contains(product, case=False, na=False)]
                    if not matching.empty:
                        price = matching.iloc[0]['price']
                        name = matching.iloc[0]['name']
                        stock = matching.iloc[0]['stock']
                        response = f"{name} costs ₹{price:,.0f}. There are {stock} units in stock."
                        break
            if not response:
                response = "Please specify which product price you want to know. For example: 'What is the price of iPhone?'"
                
        elif any(word in command for word in ['order', 'sales', 'revenue']):
            # Sales enquiry
            if user_role in ['admin', 'employee']:
                metrics = get_dashboard_metrics()
                response = f"Total revenue is ₹{metrics['revenue']:,.0f} from {metrics['total_orders']} orders. You have {metrics['active_customers']} active customers."
            else:
                response = "Sales information is available for administrators and employees only."
                
        elif any(word in command for word in ['help', 'what can you do', 'assistant']):
            response = "I can help you check stock levels, product prices, sales information, and more. Try asking me about stock, prices, orders, or sales data!"
            
        elif any(word in command for word in ['hello', 'hi', 'hey']):
            response = "Hello! I'm your StockFlow assistant. How can I help you today?"
            
        else:
            response = "I'm not sure I understand. Try asking me about stock levels, product prices, or sales information. Say 'help' for more options."
            
        return response

# Global voice assistant instance
voice_assistant = VoiceAssistant()

# ==================================================
# CHAT ASSISTANT FEATURE
# ==================================================
class ChatAssistant:
    def __init__(self):
        self.conversation_history = []
    
    def get_response(self, message, products_df, user_role, user_id=None):
        """Process chat message and return response"""
        message_lower = message.lower()
        response = ""
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "message": message, "timestamp": datetime.now()})
        
        # Process the message
        if any(word in message_lower for word in ['stock', 'inventory', 'available']):
            if 'low' in message_lower:
                low_stock = products_df[products_df['stock'] < 10]
                count = len(low_stock)
                if count > 0:
                    product_list = "\n".join([f"• {row['name']} ({row['stock']} left)" for _, row in low_stock.head(5).iterrows()])
                    response = f"**Low Stock Alert!**\n\nYou have {count} products with low stock:\n\n{product_list}"
                    if count > 5:
                        response += f"\n\n... and {count - 5} more products."
                else:
                    response = "✅ All products are sufficiently stocked! No low stock items."
            else:
                total_stock = products_df['stock'].sum()
                total_products = len(products_df)
                out_of_stock = len(products_df[products_df['stock'] == 0])
                in_stock = len(products_df[products_df['stock'] > 0])
                
                response = f"**Inventory Summary:**\n\n• **Total Products:** {total_products}\n• **Total Stock Quantity:** {total_stock}\n• **In Stock Products:** {in_stock}\n• **Out of Stock Products:** {out_of_stock}"
                
        elif any(word in message_lower for word in ['price', 'cost', 'how much']):
            product_found = False
            for product in ['iphone', 'samsung', 'macbook', 'tv', 'camera', 'laptop', 'galaxy', 'thinkpad', 'rog', 'sony', 'canon']:
                if product in message_lower:
                    matching = products_df[products_df['name'].str.contains(product, case=False, na=False)]
                    if not matching.empty:
                        product_info = matching.iloc[0]
                        price = product_info['price']
                        name = product_info['name']
                        stock = product_info['stock']
                        brand = product_info['brand']
                        category = product_info['category']
                        
                        stock_status = "✅ In Stock" if stock > 10 else "⚠️ Low Stock" if stock > 0 else "❌ Out of Stock"
                        
                        response = f"**{name}**\n\n• **Brand:** {brand}\n• **Category:** {category}\n• **Price:** ₹{price:,.0f}\n• **Stock:** {stock} units\n• **Status:** {stock_status}"
                        product_found = True
                        break
            
            if not product_found:
                # Show all products if no specific product mentioned
                top_products = products_df.head(5)
                product_list = "\n".join([f"• {row['name']} - ₹{row['price']:,.0f}" for _, row in top_products.iterrows()])
                response = f"**Available Products:**\n\n{product_list}\n\n*Ask about a specific product for more details!*"
                
        elif any(word in message_lower for word in ['order', 'sales', 'revenue', 'purchase']):
            if user_role in ['admin', 'employee']:
                metrics = get_dashboard_metrics()
                response = f"**Sales Dashboard:**\n\n• **Total Revenue:** ₹{metrics['revenue']:,.0f}\n• **Total Orders:** {metrics['total_orders']}\n• **Active Customers:** {metrics['active_customers']}\n• **Total Products:** {metrics['total_products']}"
            else:
                # For customers, show their purchase history
                if user_id:
                    purchases = get_purchase_history(user_id)
                    if not purchases.empty:
                        total_spent = (purchases['price'] * purchases['quantity']).sum()
                        purchase_list = "\n".join([f"• {row['product_name']} - ₹{row['price']:,.0f} x {row['quantity']}" for _, row in purchases.head(5).iterrows()])
                        response = f"**Your Purchase History:**\n\n{purchase_list}\n\n**Total Spent:** ₹{total_spent:,.0f}"
                    else:
                        response = "You haven't made any purchases yet. Browse our products to get started!"
                else:
                    response = "Sales information is available for administrators and employees only."
                    
        elif any(word in message_lower for word in ['help', 'what can you do', 'commands']):
            response = """**I can help you with:**

• **Stock Information** - Ask about current stock levels, low stock items
• **Product Prices** - Inquire about specific product prices and details  
• **Sales Data** - Get sales statistics and revenue information
• **Purchase History** - View your order history (customers)
• **General Assistance** - Ask questions about the system

*Try asking:*
- *"Show me low stock items"*
- *"What's the price of iPhone?"*  
- *"How are our sales?"*
- *"My purchase history"*"""

        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            response = f"Hello! 👋 I'm your StockFlow Assistant. I can help you with stock information, product prices, sales data, and more. How can I assist you today?"

        elif any(word in message_lower for word in ['thank', 'thanks']):
            response = "You're welcome! 😊 Is there anything else I can help you with?"

        elif any(word in message_lower for word in ['bye', 'goodbye', 'exit']):
            response = "Goodbye! 👋 Feel free to reach out if you need any more assistance."

        else:
            response = "I'm not sure I understand. I can help you with stock information, product prices, sales data, and more. Try asking about our products or say **help** to see what I can do!"

        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "message": response, "timestamp": datetime.now()})
        
        # Keep only last 20 messages to prevent memory issues
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
            
        return response
    
    def get_conversation_history(self):
        """Return the conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return "Conversation history cleared!"

# Global chat assistant instance
chat_assistant = ChatAssistant()