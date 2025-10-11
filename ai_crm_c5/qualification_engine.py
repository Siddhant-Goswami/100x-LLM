import yaml
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime

class QualificationEngine:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Initialize sentence transformer for intent scoring
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer model: {e}")
            self.model = None
        
        self.qualification_config = self.config['qualification']
        self.programs_config = self.config['programs']
        self.intent_seeds = self.config['intent_seeds']
    
    def qualify_lead(self, lead_data: Dict) -> Dict:
        """
        Main qualification function that returns a complete qualification result
        """
        # Check hard fails first
        hard_fail_result = self._check_hard_fails(lead_data)
        if hard_fail_result['failed']:
            return {
                'status': 'drop',
                'confidence': 1.0,
                'rationale': hard_fail_result['reason'],
                'factors': {
                    'intent_score': 0,
                    'fit_score': 0,
                    'ability_to_pay': 0,
                    'completion_score': 0,
                    'priority_bonus': 0,
                    'total_score': 0
                },
                'hard_fail': True
            }
        
        # Calculate individual scores
        intent_score = self._calculate_intent_score(lead_data.get('intent_text', ''))
        fit_score = self._calculate_fit_score(lead_data)
        ability_to_pay = self._calculate_ability_to_pay_score(lead_data)
        completion_score = self._calculate_completion_score(lead_data)
        priority_bonus = self._calculate_priority_bonus(lead_data)
        
        # Calculate weighted total score
        weights = self.qualification_config['factor_weights']
        total_score = (
            intent_score * weights['intent_score'] +
            fit_score * weights['fit_score'] +
            ability_to_pay * weights['ability_to_pay'] +
            completion_score * weights['completion_score'] +
            priority_bonus * weights['priority_bonus']
        )
        
        # Determine status based on thresholds
        pursue_threshold = self.qualification_config['pursue_threshold']
        review_threshold = self.qualification_config['review_threshold']
        
        if total_score >= pursue_threshold:
            status = 'pursue'
            confidence = min(0.9, 0.6 + (total_score - pursue_threshold) / 40)
        elif total_score >= review_threshold:
            status = 'review'
            confidence = 0.5 + (total_score - review_threshold) / 30
        else:
            status = 'drop'
            confidence = 0.7 + (50 - total_score) / 50
        
        # Generate rationale
        rationale = self._generate_rationale(
            status, total_score, intent_score, fit_score, 
            ability_to_pay, completion_score, priority_bonus
        )
        
        return {
            'status': status,
            'confidence': round(confidence, 2),
            'rationale': rationale,
            'factors': {
                'intent_score': round(intent_score, 1),
                'fit_score': round(fit_score, 1),
                'ability_to_pay': round(ability_to_pay, 1),
                'completion_score': round(completion_score, 1),
                'priority_bonus': round(priority_bonus, 1),
                'total_score': round(total_score, 1)
            },
            'hard_fail': False
        }
    
    def _check_hard_fails(self, lead_data: Dict) -> Dict:
        """Check for hard fail conditions"""
        hard_fails = self.qualification_config['hard_fails']
        
        # Missing contact info
        if hard_fails['missing_contact']:
            if not lead_data.get('email') and not lead_data.get('phone'):
                return {'failed': True, 'reason': 'Missing contact information (email and phone)'}
        
        # Irrelevant program
        if hard_fails['irrelevant_program']:
            program = lead_data.get('program', '').lower()
            valid_programs = [p['name'].lower() for p in self.programs_config]
            if program and program not in valid_programs:
                return {'failed': True, 'reason': f'Irrelevant program: {program}'}
        
        # Budget below minimum
        budget_band = lead_data.get('budget_band', '').lower()
        if budget_band:
            # Extract numeric value from budget band
            budget_match = re.search(r'(\d+)', budget_band)
            if budget_match:
                budget_value = int(budget_match.group(1))
                if budget_value < hard_fails['budget_below_minimum']:
                    return {'failed': True, 'reason': f'Budget too low: ${budget_value}'}
        
        # Disallowed regions
        region = lead_data.get('region', '').lower()
        if region in [r.lower() for r in hard_fails['disallowed_regions']]:
            return {'failed': True, 'reason': f'Disallowed region: {region}'}
        
        return {'failed': False, 'reason': ''}
    
    def _calculate_intent_score(self, intent_text: str) -> float:
        """Calculate intent score based on text similarity to seed phrases"""
        if not intent_text or not self.model:
            return 50.0  # Neutral score if no text or model
        
        try:
            # Encode the intent text
            intent_embedding = self.model.encode([intent_text])
            
            # Calculate similarity to positive seeds
            positive_seeds = self.intent_seeds['positive']
            positive_embeddings = self.model.encode(positive_seeds)
            positive_similarities = np.dot(intent_embedding, positive_embeddings.T).flatten()
            max_positive_sim = np.max(positive_similarities)
            
            # Calculate similarity to negative seeds
            negative_seeds = self.intent_seeds['negative']
            negative_embeddings = self.model.encode(negative_seeds)
            negative_similarities = np.dot(intent_embedding, negative_embeddings.T).flatten()
            max_negative_sim = np.max(negative_similarities)
            
            # Score based on difference between positive and negative similarities
            score = 50 + (max_positive_sim - max_negative_sim) * 50
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Error calculating intent score: {e}")
            return 50.0
    
    def _calculate_fit_score(self, lead_data: Dict) -> float:
        """Calculate fit score based on program, role, and experience alignment"""
        program = lead_data.get('program', '').lower()
        role = lead_data.get('role', '').lower()
        experience_years = lead_data.get('experience_years', 0)
        
        # Find matching program
        matching_program = None
        for prog in self.programs_config:
            if prog['name'].lower() == program:
                matching_program = prog
                break
        
        if not matching_program:
            return 30.0  # Low score for unknown program
        
        score = 50.0  # Base score
        
        # Role alignment
        target_roles = [r.lower() for r in matching_program['target_roles']]
        if any(target_role in role for target_role in target_roles):
            score += 25
        elif role:  # Some role mentioned but not a perfect match
            score += 10
        
        # Experience alignment
        min_experience = matching_program['min_experience']
        if experience_years >= min_experience:
            score += 20
        elif experience_years > 0:
            score += 10
        
        return min(100, score)
    
    def _calculate_ability_to_pay_score(self, lead_data: Dict) -> float:
        """Calculate ability to pay score based on budget band"""
        budget_band = lead_data.get('budget_band', '').lower()
        
        if not budget_band:
            return 30.0  # Low score for missing budget info
        
        # Extract numeric value from budget band
        budget_match = re.search(r'(\d+)', budget_band)
        if not budget_match:
            return 30.0
        
        budget_value = int(budget_match.group(1))
        
        # Score based on budget ranges
        if budget_value >= 15000:
            return 100.0
        elif budget_value >= 10000:
            return 85.0
        elif budget_value >= 8000:
            return 70.0
        elif budget_value >= 5000:
            return 50.0
        else:
            return 20.0
    
    def _calculate_completion_score(self, lead_data: Dict) -> float:
        """Calculate completion score based on data completeness"""
        required_fields = ['name', 'email', 'phone', 'program', 'role', 'budget_band']
        optional_fields = ['experience_years', 'region', 'intent_text', 'source']
        
        completed_required = sum(1 for field in required_fields if lead_data.get(field))
        completed_optional = sum(1 for field in optional_fields if lead_data.get(field))
        
        # Weight required fields more heavily
        score = (completed_required / len(required_fields)) * 70 + (completed_optional / len(optional_fields)) * 30
        return score
    
    def _calculate_priority_bonus(self, lead_data: Dict) -> float:
        """Calculate priority bonus based on special flags"""
        bonus = 0.0
        priority_flags = self.qualification_config['priority_flags']
        
        # Check for alumni referral
        source = lead_data.get('source', '').lower()
        if 'alumni' in source or 'referral' in source:
            bonus += priority_flags['alumni_referral']
        
        # Check for strong program match (already calculated in fit score)
        program = lead_data.get('program', '').lower()
        role = lead_data.get('role', '').lower()
        for prog in self.programs_config:
            if prog['name'].lower() == program:
                target_roles = [r.lower() for r in prog['target_roles']]
                if any(target_role in role for target_role in target_roles):
                    bonus += priority_flags['strong_program_match']
                break
        
        # Check for prior engagement (simplified)
        intent_text = lead_data.get('intent_text', '').lower()
        if any(word in intent_text for word in ['attended', 'participated', 'enrolled', 'previous']):
            bonus += priority_flags['prior_engagement']
        
        return min(100, bonus)
    
    def _generate_rationale(self, status: str, total_score: float, intent_score: float, 
                          fit_score: float, ability_to_pay: float, completion_score: float, 
                          priority_bonus: float) -> List[str]:
        """Generate human-readable rationale for the decision"""
        rationale = []
        
        # Overall assessment
        if status == 'pursue':
            rationale.append(f"Strong candidate with {total_score:.1f}% qualification score")
        elif status == 'review':
            rationale.append(f"Borderline candidate requiring manual review ({total_score:.1f}% score)")
        else:
            rationale.append(f"Low qualification score ({total_score:.1f}%) - not recommended")
        
        # Key factors
        if intent_score >= 70:
            rationale.append("High intent signals detected in communication")
        elif intent_score <= 30:
            rationale.append("Low intent signals - may not be serious about enrollment")
        
        if fit_score >= 70:
            rationale.append("Strong program and role alignment")
        elif fit_score <= 40:
            rationale.append("Weak program or role fit")
        
        if ability_to_pay >= 70:
            rationale.append("Budget appears sufficient for program")
        elif ability_to_pay <= 40:
            rationale.append("Budget concerns - may need financial assistance")
        
        if priority_bonus > 0:
            rationale.append(f"Priority bonus applied (+{priority_bonus:.1f} points)")
        
        return rationale[:3]  # Limit to 3 bullet points






