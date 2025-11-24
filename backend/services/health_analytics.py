"""
Health Analytics Service using Claude AI via LiteLLM
Provides AI-powered insights for menstrual health tracking
"""

from litellm import completion
import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import db

class HealthAnalyticsService:
    """LLM-powered health analytics service using Claude 3.5 Sonnet via LiteLLM"""

    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not set. AI insights will be unavailable.")

        # LiteLLM will use the ANTHROPIC_API_KEY from environment

    async def analyze_period_patterns(self, user_id: int) -> Dict:
        """Analyze period patterns and generate AI-powered insights"""

        # Get period data from database
        period_data = self._get_period_data(user_id)

        if len(period_data) < 2:
            return {
                "insights": ["Not enough data for analysis. Track at least 2 cycles for AI insights."],
                "predictions": None,
                "recommendations": ["Continue logging your periods to get personalized insights"],
                "cycle_stats": None,
                "ai_powered": False
            }

        # Calculate basic statistics
        cycle_stats = self._calculate_cycle_stats(period_data)

        # If no API key, return basic rule-based insights
        if not self.api_key:
            return self._get_basic_insights(cycle_stats, period_data)

        # Generate AI-powered insights using Claude via LiteLLM
        try:
            prompt = self._build_analysis_prompt(period_data, cycle_stats)

            # Use LiteLLM's completion function with Claude
            response = completion(
                model="claude-3-5-sonnet-20241022",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for consistent medical insights
                api_key=self.api_key
            )

            analysis = response.choices[0].message.content
            parsed_insights = self._parse_llm_response(analysis, cycle_stats)
            parsed_insights["ai_powered"] = True

            return parsed_insights

        except Exception as e:
            print(f"Error generating AI insights: {e}")
            # Fallback to basic insights
            return self._get_basic_insights(cycle_stats, period_data)

    def _get_period_data(self, user_id: int) -> List[Dict]:
        """Retrieve period log data from database"""
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT id, start_date, end_date, flow_level, symptoms, notes
               FROM period_logs
               WHERE user_id = ?
               ORDER BY start_date DESC
               LIMIT 12''',  # Last 12 cycles
            (user_id,)
        )

        logs = cursor.fetchall()
        conn.close()

        return [dict(log) for log in logs]

    def _calculate_cycle_stats(self, period_data: List[Dict]) -> Dict:
        """Calculate statistical metrics from period data"""
        if len(period_data) < 2:
            return {}

        # Calculate cycle lengths
        cycle_lengths = []
        for i in range(len(period_data) - 1):
            current = datetime.strptime(period_data[i]['start_date'], '%Y-%m-%d')
            next_period = datetime.strptime(period_data[i + 1]['start_date'], '%Y-%m-%d')
            cycle_length = (current - next_period).days
            if cycle_length > 0:
                cycle_lengths.append(cycle_length)

        # Calculate period durations
        period_durations = []
        for log in period_data:
            if log['end_date']:
                start = datetime.strptime(log['start_date'], '%Y-%m-%d')
                end = datetime.strptime(log['end_date'], '%Y-%m-%d')
                duration = (end - start).days + 1
                period_durations.append(duration)

        # Collect symptoms
        all_symptoms = []
        for log in period_data:
            if log['symptoms']:
                all_symptoms.extend(log['symptoms'].split(','))

        # Calculate statistics
        avg_cycle = sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else 0
        avg_duration = sum(period_durations) / len(period_durations) if period_durations else 0

        # Determine regularity
        if cycle_lengths:
            std_dev = (sum((x - avg_cycle) ** 2 for x in cycle_lengths) / len(cycle_lengths)) ** 0.5
            if std_dev <= 3:
                regularity = "regular"
            elif std_dev <= 7:
                regularity = "somewhat irregular"
            else:
                regularity = "irregular"
        else:
            regularity = "unknown"

        # Find common symptoms
        symptom_counts = {}
        for symptom in all_symptoms:
            symptom = symptom.strip()
            if symptom:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

        common_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        common_symptoms = [s[0] for s in common_symptoms]

        return {
            "avg_cycle_length": round(avg_cycle, 1),
            "avg_period_duration": round(avg_duration, 1),
            "regularity": regularity,
            "common_symptoms": common_symptoms,
            "total_cycles_tracked": len(period_data),
            "cycle_lengths": cycle_lengths
        }

    def _build_analysis_prompt(self, period_data: List[Dict], cycle_stats: Dict) -> str:
        """Build prompt for Claude AI analysis"""

        # Anonymize and format period data
        formatted_logs = []
        for i, log in enumerate(period_data[:6]):  # Last 6 cycles
            formatted_logs.append({
                "cycle": i + 1,
                "start_date": log['start_date'],
                "end_date": log.get('end_date', 'ongoing'),
                "flow_level": log.get('flow_level', 'unknown'),
                "symptoms": log.get('symptoms', 'none')
            })

        prompt = f"""You are a women's health data analyst specializing in menstrual health patterns. Analyze the following menstrual cycle data and provide insights.

**User's Period History (last {len(formatted_logs)} cycles):**
{json.dumps(formatted_logs, indent=2)}

**Calculated Statistics:**
- Average cycle length: {cycle_stats['avg_cycle_length']} days
- Cycle regularity: {cycle_stats['regularity']}
- Average period duration: {cycle_stats['avg_period_duration']} days
- Most common symptoms: {', '.join(cycle_stats['common_symptoms']) if cycle_stats['common_symptoms'] else 'none reported'}

Please provide analysis in JSON format with the following structure:
{{
  "cycle_regularity": {{
    "status": "regular|irregular|variable",
    "explanation": "Brief explanation of cycle pattern"
  }},
  "next_period_prediction": {{
    "estimated_date": "YYYY-MM-DD",
    "confidence": "high|medium|low",
    "reasoning": "Why this prediction"
  }},
  "insights": [
    "Key insight 1",
    "Key insight 2",
    "Key insight 3"
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "health_flags": [
    "Any concerning patterns if found, otherwise empty"
  ],
  "lifestyle_tips": [
    "Lifestyle tip 1",
    "Lifestyle tip 2"
  ]
}}

Important guidelines:
- Be supportive and informative, not alarming
- If patterns suggest medical consultation, mention it gently
- Keep insights practical and actionable
- Focus on patterns, not individual cycles
- Do not diagnose medical conditions
"""

        return prompt

    def _parse_llm_response(self, response_text: str, cycle_stats: Dict) -> Dict:
        """Parse Claude's JSON response"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)

                # Add cycle stats
                analysis['cycle_stats'] = cycle_stats

                return analysis
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Return basic structure if parsing fails
            return {
                "insights": ["Unable to generate detailed insights. Please try again later."],
                "recommendations": ["Continue tracking your cycles"],
                "cycle_stats": cycle_stats,
                "ai_powered": False
            }

    def _get_basic_insights(self, cycle_stats: Dict, period_data: List[Dict]) -> Dict:
        """Generate basic rule-based insights when AI is unavailable"""

        insights = []
        recommendations = []
        health_flags = []

        # Cycle regularity insight
        if cycle_stats['regularity'] == 'regular':
            insights.append(f"Your cycles are regular with an average length of {cycle_stats['avg_cycle_length']} days.")
        elif cycle_stats['regularity'] == 'irregular':
            insights.append(f"Your cycles show irregularity. Average length is {cycle_stats['avg_cycle_length']} days with high variation.")
            health_flags.append("Irregular cycles - consider consulting a healthcare provider if this persists")

        # Period duration insight
        if cycle_stats['avg_period_duration'] > 0:
            if cycle_stats['avg_period_duration'] <= 7:
                insights.append(f"Your period duration averages {cycle_stats['avg_period_duration']} days, which is within normal range.")
            else:
                insights.append(f"Your periods last {cycle_stats['avg_period_duration']} days on average, which is longer than typical.")
                health_flags.append("Extended period duration - may want to discuss with doctor")

        # Symptom insight
        if cycle_stats['common_symptoms']:
            insights.append(f"Common symptoms you experience: {', '.join(cycle_stats['common_symptoms'])}")
            recommendations.append("Consider lifestyle adjustments to manage symptoms (exercise, diet, stress management)")

        # General recommendations
        recommendations.append("Continue tracking your cycles for better insights")
        recommendations.append("Maintain a healthy lifestyle with regular exercise and balanced nutrition")

        # Next period prediction (simple calculation)
        if period_data and cycle_stats['avg_cycle_length'] > 0:
            last_period = datetime.strptime(period_data[0]['start_date'], '%Y-%m-%d')
            predicted_date = last_period + timedelta(days=int(cycle_stats['avg_cycle_length']))

            prediction = {
                "estimated_date": predicted_date.strftime('%Y-%m-%d'),
                "confidence": "medium" if cycle_stats['regularity'] == 'regular' else "low",
                "reasoning": f"Based on your average cycle length of {cycle_stats['avg_cycle_length']} days"
            }
        else:
            prediction = None

        return {
            "insights": insights,
            "recommendations": recommendations,
            "health_flags": health_flags,
            "lifestyle_tips": [
                "Stay hydrated throughout your cycle",
                "Track your symptoms to identify patterns"
            ],
            "cycle_stats": cycle_stats,
            "next_period_prediction": prediction,
            "ai_powered": False
        }

# Global analytics service instance
health_analytics = HealthAnalyticsService()
