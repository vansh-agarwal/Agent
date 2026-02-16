"""
ML Service for ARIA
Loads and serves predictions from ML models:
- Career Income Prediction (XGBoost)
- HR Productivity Analysis (RandomForest)
- Customer Segmentation (KMeans)
"""

import os
import pickle
import joblib
import numpy as np
from typing import Dict, Any, Optional, List

# Get the ML directory path
ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml')


class MLService:
    """Centralized ML model service for ARIA"""
    
    def __init__(self):
        self.career_model = None
        self.hr_model = None
        self.retail_model = None
        self.retail_scaler = None
        
        # Career model feature mappings
        self.career_features = [
            'age', 'workclass', 'education', 'education-num', 'marital-status',
            'occupation', 'relationship', 'race', 'sex', 'capital-gain',
            'capital-loss', 'hours-per-week', 'native-country'
        ]
        
        # Categorical mappings for career model
        self.workclass_map = {
            'Private': 0, 'Self-emp-not-inc': 1, 'Self-emp-inc': 2,
            'Federal-gov': 3, 'Local-gov': 4, 'State-gov': 5,
            'Without-pay': 6, 'Never-worked': 7
        }
        
        self.education_map = {
            'Bachelors': 0, 'Some-college': 1, '11th': 2, 'HS-grad': 3,
            'Prof-school': 4, 'Assoc-acdm': 5, 'Assoc-voc': 6, '9th': 7,
            '7th-8th': 8, '12th': 9, 'Masters': 10, '1st-4th': 11,
            '10th': 12, 'Doctorate': 13, '5th-6th': 14, 'Preschool': 15
        }
        
        self.marital_map = {
            'Married-civ-spouse': 0, 'Divorced': 1, 'Never-married': 2,
            'Separated': 3, 'Widowed': 4, 'Married-spouse-absent': 5,
            'Married-AF-spouse': 6
        }
        
        self.occupation_map = {
            'Tech-support': 0, 'Craft-repair': 1, 'Other-service': 2,
            'Sales': 3, 'Exec-managerial': 4, 'Prof-specialty': 5,
            'Handlers-cleaners': 6, 'Machine-op-inspct': 7, 'Adm-clerical': 8,
            'Farming-fishing': 9, 'Transport-moving': 10, 'Priv-house-serv': 11,
            'Protective-serv': 12, 'Armed-Forces': 13
        }
        
        self.relationship_map = {
            'Wife': 0, 'Own-child': 1, 'Husband': 2, 'Not-in-family': 3,
            'Other-relative': 4, 'Unmarried': 5
        }
        
        self.race_map = {
            'White': 0, 'Asian-Pac-Islander': 1, 'Amer-Indian-Eskimo': 2,
            'Other': 3, 'Black': 4
        }
        
        self.sex_map = {'Male': 0, 'Female': 1}
        
        self.country_map = {
            'United-States': 0, 'Cambodia': 1, 'England': 2, 'Puerto-Rico': 3,
            'Canada': 4, 'Germany': 5, 'Outlying-US(Guam-USVI-etc)': 6,
            'India': 7, 'Japan': 8, 'Greece': 9, 'South': 10, 'China': 11,
            'Cuba': 12, 'Iran': 13, 'Honduras': 14, 'Philippines': 15,
            'Italy': 16, 'Poland': 17, 'Jamaica': 18, 'Vietnam': 19,
            'Mexico': 20, 'Portugal': 21, 'Ireland': 22, 'France': 23,
            'Dominican-Republic': 24, 'Laos': 25, 'Ecuador': 26, 'Taiwan': 27,
            'Haiti': 28, 'Columbia': 29, 'Hungary': 30, 'Guatemala': 31,
            'Nicaragua': 32, 'Scotland': 33, 'Thailand': 34, 'Yugoslavia': 35,
            'El-Salvador': 36, 'Trinadad&Tobago': 37, 'Peru': 38, 'Hong': 39,
            'Holand-Netherlands': 40, 'Other': 41
        }
        
        # HR model feature order
        self.hr_features = ['Satisfaction Rate', 'Salary', 'Age', 'Position', 'Years at Company', 'Projects Completed']
        
        self.position_map = {
            'Junior': 1, 'Mid': 2, 'Senior': 3, 'Lead': 4, 'Manager': 5, 'Director': 6
        }
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load all ML models from pickle files"""
        
        # Career Income Model (XGBoost)
        try:
            career_path = os.path.join(ML_DIR, 'career_income_brain.pkl')
            if os.path.exists(career_path):
                with open(career_path, 'rb') as f:
                    self.career_model = pickle.load(f)
                print("✅ Career Income model loaded")
        except Exception as e:
            print(f"⚠️ Career model loading failed: {e}")
        
        # HR Productivity Model (RandomForest)
        try:
            hr_path = os.path.join(ML_DIR, 'hr_productivity_brain_demo.pkl')
            if os.path.exists(hr_path):
                self.hr_model = joblib.load(hr_path)
                print("✅ HR Productivity model loaded")
        except Exception as e:
            print(f"⚠️ HR model loading failed: {e}")
        
        # Retail Segmentation Model (KMeans)
        try:
            retail_path = os.path.join(ML_DIR, 'retail_segmentation_brain.pkl')
            scaler_path = os.path.join(ML_DIR, 'retail_scaler.pkl')
            if os.path.exists(retail_path):
                self.retail_model = joblib.load(retail_path)
                print("✅ Retail Segmentation model loaded")
            if os.path.exists(scaler_path):
                self.retail_scaler = joblib.load(scaler_path)
                print("✅ Retail Scaler loaded")
        except Exception as e:
            print(f"⚠️ Retail model loading failed: {e}")
    
    def predict_career_income(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict income bracket based on demographic and work data.
        
        Args:
            data: Dictionary with keys: age, workclass, education, marital_status,
                  occupation, relationship, race, sex, capital_gain, capital_loss,
                  hours_per_week, native_country
        
        Returns:
            Dictionary with prediction (0 = <=50K, 1 = >50K) and confidence
        """
        if self.career_model is None:
            return {'error': 'Career model not available', 'success': False}
        
        try:
            # Build feature array
            features = np.array([[
                int(data.get('age', 30)),
                self.workclass_map.get(data.get('workclass', 'Private'), 0),
                self.education_map.get(data.get('education', 'Bachelors'), 0),
                int(data.get('education_num', 13)),
                self.marital_map.get(data.get('marital_status', 'Never-married'), 2),
                self.occupation_map.get(data.get('occupation', 'Prof-specialty'), 5),
                self.relationship_map.get(data.get('relationship', 'Not-in-family'), 3),
                self.race_map.get(data.get('race', 'White'), 0),
                self.sex_map.get(data.get('sex', 'Male'), 0),
                int(data.get('capital_gain', 0)),
                int(data.get('capital_loss', 0)),
                int(data.get('hours_per_week', 40)),
                self.country_map.get(data.get('native_country', 'United-States'), 0)
            ]])
            
            # Get prediction
            prediction = self.career_model.predict(features)[0]
            
            # Try to get probability
            confidence = 0.85
            if hasattr(self.career_model, 'predict_proba'):
                proba = self.career_model.predict_proba(features)[0]
                confidence = float(max(proba))
            
            income_bracket = '>50K' if prediction == 1 else '<=50K'
            
            return {
                'success': True,
                'prediction': int(prediction),
                'income_bracket': income_bracket,
                'confidence': round(confidence * 100, 1),
                'interpretation': f"Based on your profile, the predicted annual income is {income_bracket} with {round(confidence * 100, 1)}% confidence.",
                'factors': self._get_career_factors(data)
            }
        
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _get_career_factors(self, data: Dict) -> List[str]:
        """Generate insights about career prediction factors"""
        factors = []
        
        age = int(data.get('age', 30))
        if age < 25:
            factors.append("📊 Young age may limit income initially, but growth potential is high")
        elif age >= 45:
            factors.append("📊 Experience and seniority typically correlate with higher income")
        
        education = data.get('education', '')
        if education in ['Bachelors', 'Masters', 'Doctorate', 'Prof-school']:
            factors.append("🎓 Higher education significantly boosts earning potential")
        
        hours = int(data.get('hours_per_week', 40))
        if hours > 45:
            factors.append("⏰ Working >45 hours/week shows dedication, often linked to higher pay")
        
        occupation = data.get('occupation', '')
        if occupation in ['Exec-managerial', 'Prof-specialty', 'Tech-support']:
            factors.append("💼 Professional/managerial roles typically command higher salaries")
        
        return factors
    
    def predict_hr_productivity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict employee productivity score based on HR metrics.
        
        Args:
            data: Dictionary with keys: satisfaction_rate, salary, age, 
                  position, years_at_company, projects_completed
        
        Returns:
            Dictionary with productivity score and analysis
        """
        if self.hr_model is None:
            return {'error': 'HR model not available', 'success': False}
        
        try:
            # Build feature array in correct order
            features = np.array([[
                float(data.get('satisfaction_rate', 0.7)),
                float(data.get('salary', 50000)),
                int(data.get('age', 30)),
                self.position_map.get(data.get('position', 'Mid'), 2),
                int(data.get('years_at_company', 2)),
                int(data.get('projects_completed', 5))
            ]])
            
            # Get prediction (productivity score)
            productivity_score = float(self.hr_model.predict(features)[0])
            
            # Normalize to 0-100 if needed
            if productivity_score > 1:
                productivity_score = min(productivity_score, 100)
            else:
                productivity_score = productivity_score * 100
            
            # Determine category
            if productivity_score >= 80:
                category = 'High Performer'
                emoji = '🌟'
                recommendation = 'Consider for leadership roles and challenging projects'
            elif productivity_score >= 60:
                category = 'Good Performer'
                emoji = '✅'
                recommendation = 'Provide growth opportunities and mentorship'
            elif productivity_score >= 40:
                category = 'Average Performer'
                emoji = '📊'
                recommendation = 'Identify areas for skill development and support'
            else:
                category = 'Needs Improvement'
                emoji = '⚠️'
                recommendation = 'Consider additional training and regular check-ins'
            
            # Mental health & wellbeing indicator
            satisfaction = float(data.get('satisfaction_rate', 0.7))
            wellbeing = 'Good' if satisfaction >= 0.7 else ('Moderate' if satisfaction >= 0.4 else 'At Risk')
            
            return {
                'success': True,
                'productivity_score': round(productivity_score, 1),
                'category': category,
                'emoji': emoji,
                'recommendation': recommendation,
                'wellbeing_indicator': wellbeing,
                'analysis': self._analyze_hr_factors(data, productivity_score)
            }
        
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _analyze_hr_factors(self, data: Dict, score: float) -> Dict:
        """Analyze HR factors affecting productivity"""
        analysis = {
            'strengths': [],
            'areas_for_improvement': [],
            'mental_health_notes': []
        }
        
        satisfaction = float(data.get('satisfaction_rate', 0.7))
        if satisfaction >= 0.8:
            analysis['strengths'].append('High job satisfaction - great for retention')
        elif satisfaction < 0.5:
            analysis['areas_for_improvement'].append('Low satisfaction - investigate causes')
            analysis['mental_health_notes'].append('⚠️ Low satisfaction can impact mental wellbeing')
        
        projects = int(data.get('projects_completed', 5))
        years = int(data.get('years_at_company', 2))
        if years > 0 and projects / years >= 3:
            analysis['strengths'].append('Strong project completion rate')
        
        position = data.get('position', 'Mid')
        age = int(data.get('age', 30))
        if position in ['Senior', 'Lead', 'Manager'] and age < 35:
            analysis['strengths'].append('Early career advancement - high potential')
        
        if satisfaction < 0.5 and score < 50:
            analysis['mental_health_notes'].append('🧠 Consider wellness check-in and support resources')
        
        return analysis
    
    def predict_customer_segment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Segment customer based on RFM (Recency, Frequency, Monetary) analysis.
        
        Args:
            data: Dictionary with keys: recency, frequency, monetary
        
        Returns:
            Dictionary with segment and recommendations
        """
        if self.retail_model is None:
            return {'error': 'Retail model not available', 'success': False}
        
        try:
            # Build feature array
            features = np.array([[
                float(data.get('recency', 30)),
                float(data.get('frequency', 5)),
                float(data.get('monetary', 100))
            ]])
            
            # Scale if scaler is available
            if self.retail_scaler is not None:
                features = self.retail_scaler.transform(features)
            
            # Get cluster prediction
            cluster = int(self.retail_model.predict(features)[0])
            
            # Segment interpretations (4 clusters)
            segments = {
                0: {
                    'name': 'Champions',
                    'emoji': '🏆',
                    'description': 'Best customers - high value, frequent, recent',
                    'strategy': 'Reward loyalty, early access to new products, VIP treatment'
                },
                1: {
                    'name': 'Loyal Customers',
                    'emoji': '💎',
                    'description': 'Regular customers with good engagement',
                    'strategy': 'Upsell premium products, loyalty program benefits'
                },
                2: {
                    'name': 'Potential Loyalists',
                    'emoji': '📈',
                    'description': 'Recent customers with growth potential',
                    'strategy': 'Onboarding emails, membership offers, engagement campaigns'
                },
                3: {
                    'name': 'At Risk',
                    'emoji': '⚠️',
                    'description': 'Previously good customers who are slipping away',
                    'strategy': 'Win-back campaigns, special discounts, personalized outreach'
                }
            }
            
            segment_info = segments.get(cluster, segments[3])
            
            return {
                'success': True,
                'cluster': cluster,
                'segment': segment_info['name'],
                'emoji': segment_info['emoji'],
                'description': segment_info['description'],
                'recommended_strategy': segment_info['strategy'],
                'rfm_analysis': {
                    'recency_days': data.get('recency', 30),
                    'purchase_frequency': data.get('frequency', 5),
                    'monetary_value': data.get('monetary', 100)
                }
            }
        
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get status of all loaded models"""
        return {
            'career_income': self.career_model is not None,
            'hr_productivity': self.hr_model is not None,
            'retail_segmentation': self.retail_model is not None
        }


# Singleton instance
_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """Get or create the ML service instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service
