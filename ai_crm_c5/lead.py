import gradio as gr
import pandas as pd
import yaml
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager
from qualification_engine import QualificationEngine
import io
import csv

class LeadQualificationApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.qualification_engine = QualificationEngine()
        self.current_user = None
        self.login_attempts = {}
        
        # Load configuration
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Handle user login"""
        if not email or not password:
            return False, "Please enter both email and password"
        
        # Check login attempts
        if email in self.login_attempts:
            if self.login_attempts[email] >= self.config['system']['max_login_attempts']:
                return False, "Too many failed attempts. Account locked."
        
        # Authenticate user
        user = self.db.authenticate_user(email, password)
        if user:
            self.current_user = user
            self.login_attempts[email] = 0
            self.db.log_audit(user['user_id'], 'login', {'email': email})
            return True, f"Welcome, {user['email']}!"
        else:
            self.login_attempts[email] = self.login_attempts.get(email, 0) + 1
            return False, f"Invalid credentials. Attempts: {self.login_attempts[email]}"
    
    def logout(self):
        """Handle user logout"""
        if self.current_user:
            self.db.log_audit(self.current_user['user_id'], 'logout')
        self.current_user = None
        return "Logged out successfully"
    
    def get_lead_queue(self, status_filter: str = "all") -> pd.DataFrame:
        """Get leads for the queue display"""
        if status_filter == "all":
            leads = self.db.get_leads(limit=100)
        else:
            leads = self.db.get_leads(status=status_filter, limit=100)
        
        if not leads:
            return pd.DataFrame(columns=['ID', 'Name', 'Program', 'Intent Snippet', 'Score', 'Status', 'Created'])
        
        # Process leads for display
        display_data = []
        for lead in leads:
            # Get latest decision if exists
            decisions = self.db.get_decisions(lead_id=lead['lead_id'], limit=1)
            score = "N/A"
            if decisions:
                factors = decisions[0].get('factors', {})
                score = f"{factors.get('total_score', 0):.1f}"
            
            # Truncate intent text
            intent_snippet = lead.get('intent_text', '')[:50] + "..." if len(lead.get('intent_text', '')) > 50 else lead.get('intent_text', '')
            
            display_data.append({
                'ID': lead['lead_id'],
                'Name': lead['name'],
                'Program': lead['program'],
                'Intent Snippet': intent_snippet,
                'Score': score,
                'Status': lead['status'],
                'Created': lead['created_at'][:10]  # Just the date
            })
        
        return pd.DataFrame(display_data)
    
    def get_lead_details(self, lead_id: int) -> Tuple[Dict, str]:
        """Get detailed lead information and qualification result"""
        if not lead_id:
            return {}, "Please select a lead"
        
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {}, "Lead not found"
        
        # Get qualification result
        qualification_result = self.qualification_engine.qualify_lead(lead)
        
        # Get decision history
        decisions = self.db.get_decisions(lead_id=lead_id)
        
        # Format decision history
        history_text = "No previous decisions"
        if decisions:
            history_lines = []
            for decision in decisions:
                history_lines.append(
                    f"{decision['decided_at'][:16]} - {decision['status'].upper()} "
                    f"(Confidence: {decision['confidence']:.2f}) by {decision['decided_by_email']}"
                )
                if decision['notes']:
                    history_lines.append(f"  Notes: {decision['notes']}")
            history_text = "\n".join(history_lines)
        
        return lead, qualification_result, history_text
    
    def make_decision(self, lead_id: int, decision_status: str, notes: str, override: bool = False) -> str:
        """Make a decision on a lead"""
        if not self.current_user:
            return "Please log in first"
        
        if not lead_id:
            return "Please select a lead"
        
        # Get current qualification result
        lead = self.db.get_lead(lead_id)
        if not lead:
            return "Lead not found"
        
        qualification_result = self.qualification_engine.qualify_lead(lead)
        
        # Create decision record
        decision_data = {
            'lead_id': lead_id,
            'decided_by': self.current_user['user_id'],
            'status': decision_status,
            'rationale': "\n".join(qualification_result['rationale']),
            'confidence': qualification_result['confidence'],
            'factors': qualification_result['factors'],
            'override_flag': override,
            'notes': notes
        }
        
        # Save decision
        decision_id = self.db.add_decision(decision_data)
        
        # Update lead status
        self.db.update_lead_status(lead_id, decision_status)
        
        # Log audit
        self.db.log_audit(
            self.current_user['user_id'], 
            'decision_made', 
            {
                'lead_id': lead_id,
                'decision_id': decision_id,
                'status': decision_status,
                'override': override
            }
        )
        
        return f"Decision saved: {decision_status.upper()}"
    
    def import_csv(self, csv_file) -> str:
        """Import leads from CSV file"""
        if not self.current_user:
            return "Please log in first"
        
        if not csv_file:
            return "Please upload a CSV file"
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file.name)
            
            # Validate required columns
            required_columns = ['name', 'email', 'program']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return f"Missing required columns: {', '.join(missing_columns)}"
            
            # Import leads
            imported_count = 0
            for _, row in df.iterrows():
                lead_data = {
                    'name': str(row.get('name', '')),
                    'email': str(row.get('email', '')),
                    'phone': str(row.get('phone', '')),
                    'program': str(row.get('program', '')),
                    'role': str(row.get('role', '')),
                    'experience_years': int(row.get('experience_years', 0)) if pd.notna(row.get('experience_years')) else 0,
                    'budget_band': str(row.get('budget_band', '')),
                    'region': str(row.get('region', '')),
                    'intent_text': str(row.get('intent_text', '')),
                    'source': str(row.get('source', 'csv_import'))
                }
                
                self.db.add_lead(lead_data)
                imported_count += 1
            
            # Log audit
            self.db.log_audit(
                self.current_user['user_id'], 
                'csv_import', 
                {'file': csv_file.name, 'count': imported_count}
            )
            
            return f"Successfully imported {imported_count} leads"
            
        except Exception as e:
            return f"Error importing CSV: {str(e)}"
    
    def get_kpi_data(self) -> Dict:
        """Get KPI data for dashboard"""
        kpi_data = self.db.get_kpi_data(self.config['system']['kpi_days'])
        
        # Create charts
        status_counts = kpi_data['decisions_by_status']
        if status_counts:
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Decisions by Status (Last 7 Days)"
            )
        else:
            fig_pie = go.Figure()
            fig_pie.add_annotation(text="No data available", showarrow=False)
        
        return {
            'total_leads': kpi_data['total_leads'],
            'avg_confidence': kpi_data['avg_confidence'],
            'override_rate': kpi_data['override_rate'],
            'pie_chart': fig_pie
        }
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="Lead Qualification Dashboard", theme=gr.themes.Soft()) as app:
            gr.Markdown("# 🎯 Lead Qualification Dashboard")
            
            # Login Section
            with gr.Tab("Login"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Team Login")
                        email_input = gr.Textbox(label="Email", placeholder="your.email@company.com")
                        password_input = gr.Textbox(label="Password", type="password")
                        login_btn = gr.Button("Login", variant="primary")
                        logout_btn = gr.Button("Logout")
                        login_status = gr.Textbox(label="Status", interactive=False)
            
            # Lead Queue Section
            with gr.Tab("Lead Queue"):
                with gr.Row():
                    with gr.Column(scale=3):
                        gr.Markdown("### Lead Queue")
                        status_filter = gr.Dropdown(
                            choices=["all", "new", "pursue", "review", "drop"],
                            value="all",
                            label="Filter by Status"
                        )
                        queue_table = gr.Dataframe(
                            headers=['ID', 'Name', 'Program', 'Intent Snippet', 'Score', 'Status', 'Created'],
                            interactive=False,
                            wrap=True
                        )
                        refresh_queue_btn = gr.Button("Refresh Queue")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Actions")
                        csv_upload = gr.File(label="Import CSV", file_types=[".csv"])
                        import_btn = gr.Button("Import Leads")
                        import_status = gr.Textbox(label="Import Status", interactive=False)
            
            # Lead Review Section
            with gr.Tab("Lead Review"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Lead Details")
                        lead_id_input = gr.Number(label="Lead ID", value=0)
                        load_lead_btn = gr.Button("Load Lead", variant="primary")
                        
                        lead_details = gr.JSON(label="Lead Information")
                        decision_history = gr.Textbox(label="Decision History", lines=5, interactive=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### AI Qualification")
                        qualification_result = gr.JSON(label="Qualification Result")
                        
                        gr.Markdown("### Decision")
                        decision_status = gr.Dropdown(
                            choices=["pursue", "review", "drop"],
                            label="Decision Status"
                        )
                        decision_notes = gr.Textbox(label="Notes", lines=3)
                        override_checkbox = gr.Checkbox(label="Override AI Recommendation")
                        make_decision_btn = gr.Button("Save Decision", variant="primary")
                        decision_status_output = gr.Textbox(label="Decision Status", interactive=False)
            
            # KPI Dashboard Section
            with gr.Tab("KPI Dashboard"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Key Performance Indicators")
                        kpi_metrics = gr.JSON(label="KPI Metrics")
                        kpi_chart = gr.Plot(label="Decisions by Status")
                        refresh_kpi_btn = gr.Button("Refresh KPI Data")
            
            # Event Handlers
            login_btn.click(
                self.login,
                inputs=[email_input, password_input],
                outputs=[login_status, login_status]
            )
            
            logout_btn.click(
                self.logout,
                outputs=login_status
            )
            
            refresh_queue_btn.click(
                self.get_lead_queue,
                inputs=status_filter,
                outputs=queue_table
            )
            
            status_filter.change(
                self.get_lead_queue,
                inputs=status_filter,
                outputs=queue_table
            )
            
            import_btn.click(
                self.import_csv,
                inputs=csv_upload,
                outputs=import_status
            )
            
            load_lead_btn.click(
                self.get_lead_details,
                inputs=lead_id_input,
                outputs=[lead_details, qualification_result, decision_history]
            )
            
            make_decision_btn.click(
                self.make_decision,
                inputs=[lead_id_input, decision_status, decision_notes, override_checkbox],
                outputs=decision_status_output
            )
            
            refresh_kpi_btn.click(
                self.get_kpi_data,
                outputs=[kpi_metrics, kpi_chart]
            )
            
            # Initialize with default data
            app.load(
                self.get_lead_queue,
                inputs=status_filter,
                outputs=queue_table
            )
            
            app.load(
                self.get_kpi_data,
                outputs=[kpi_metrics, kpi_chart]
            )
        
        return app

def main():
    """Main function to run the application"""
    app_instance = LeadQualificationApp()
    app = app_instance.create_interface()
    
    print("Starting Lead Qualification Dashboard...")
    print("Default login credentials:")
    print("  admin@company.com / admin123")
    print("  enrollment@company.com / enroll123")
    print("  manager@company.com / manager123")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()






