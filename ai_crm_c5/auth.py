import streamlit as st
from supabase_service import SupabaseService
import os

class AuthManager:
    """Simple authentication manager for Streamlit app"""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
    
    def login(self, email: str, password: str) -> bool:
        """Login user with email and password"""
        try:
            # For now, we'll use a simple check against environment variables
            # In a real app, you'd use Supabase Auth
            admin_email = os.getenv("ADMIN_EMAIL", "admin@100xengineers.com")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            if email == admin_email and password == admin_password:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return False
    
    def logout(self):
        """Logout user"""
        st.session_state.authenticated = False
        st.session_state.user_email = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_user_email(self) -> str:
        """Get current user email"""
        return st.session_state.get('user_email', '')
    
    def show_login_form(self):
        """Show login form"""
        st.title("100xEngineers CRM - Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if self.login(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        
        # Show default credentials for demo
        st.info("""
        **Demo Credentials:**
        - Email: admin@100xengineers.com
        - Password: admin123
        
        *You can change these in your environment variables ADMIN_EMAIL and ADMIN_PASSWORD*
        """)

def require_auth(func):
    """Decorator to require authentication for Streamlit pages"""
    def wrapper(*args, **kwargs):
        auth_manager = AuthManager()
        
        if not auth_manager.is_authenticated():
            auth_manager.show_login_form()
            return
        
        return func(*args, **kwargs)
    
    return wrapper

