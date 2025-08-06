#!/usr/bin/env python3
"""
Demo data generator for the ODIN Protocol self-reflection system.
Creates realistic conversation and reflection data for UI testing.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


class DemoDataGenerator:
    """Generate realistic demo data for conversation and reflection testing."""
    
    def __init__(self):
        self.demo_topics = [
            "The future of artificial intelligence",
            "Climate change solutions and technology",
            "The ethics of genetic engineering",
            "Space exploration and colonization",
            "The impact of social media on society"
        ]
        
        self.demo_models = {
            'model_a': {
                'name': 'GPT-4O',
                'role': 'Critical Analyst',
                'personality': 'analytical, questioning, thorough'
            },
            'model_b': {
                'name': 'Gemini-1.5-Flash', 
                'role': 'Optimistic Supporter',
                'personality': 'creative, encouraging, solution-focused'
            }
        }
        
        self.reflection_scenarios = [
            {
                'action': 'pass',
                'confidence': 0.85,
                'explanation': 'Message meets quality standards with high confidence and clear reasoning.',
                'tags': []
            },
            {
                'action': 'modify',
                'confidence': 0.65,
                'explanation': 'Message contains uncertain language patterns that should be refined for clarity.',
                'tags': ['low-confidence-language', 'clarity-improvement']
            },
            {
                'action': 'reject',
                'confidence': 0.35,
                'explanation': 'Message rejected due to potential hallucination and low confidence indicators.',
                'tags': ['potential-hallucination', 'critical-quality-issues']
            },
            {
                'action': 'modify',
                'confidence': 0.72,
                'explanation': 'High semantic drift detected. Message revised to maintain topic coherence.',
                'tags': ['high-semantic-drift', 'topic-alignment']
            },
            {
                'action': 'pass',
                'confidence': 0.91,
                'explanation': 'Excellent message quality with strong evidence-based reasoning.',
                'tags': []
            }
        ]
    
    def generate_conversation_turn(self, turn_number: int, current_speaker: str, topic: str) -> Dict[str, Any]:
        """Generate a realistic conversation turn."""
        model_info = self.demo_models[current_speaker]
        
        # Generate realistic thought process
        thought_process = {
            'step': f"Analyzing {topic} from {model_info['role'].lower()} perspective",
            'reasoning': f"Considering the {model_info['personality'].split(',')[0]} approach to this topic",
            'confidence': random.uniform(0.7, 0.95),
            'alternatives_considered': [
                "Direct factual approach",
                "Nuanced perspective analysis", 
                "Historical context integration"
            ],
            'decision_rationale': f"Best aligns with {model_info['role'].lower()} methodology"
        }
        
        # Generate message content based on model personality
        messages_pool = {
            'model_a': [
                "While this perspective has merit, we should critically examine the underlying assumptions.",
                "The data suggests a more complex picture than initially apparent.",
                "I question whether this approach adequately addresses the fundamental challenges.",
                "This analysis lacks consideration of potential negative consequences.",
                "We need to scrutinize the methodological rigor of this approach."
            ],
            'model_b': [
                "This presents an exciting opportunity for innovation and positive change.",
                "I see tremendous potential in this approach, building on existing strengths.",
                "The collaborative possibilities here are truly inspiring and worth exploring.",
                "This could be the breakthrough we've been looking for in this field.",
                "The positive implications of this development are far-reaching and encouraging."
            ]
        }
        
        message = random.choice(messages_pool[current_speaker])
        
        return {
            'turn_number': turn_number,
            'current_speaker': current_speaker,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'thought_process': thought_process,
            'model_a': model_info if current_speaker == 'model_a' else None,
            'model_b': model_info if current_speaker == 'model_b' else None,
            'mediator_analysis': {
                'conversation_health': random.choice(['excellent', 'good', 'moderate']),
                'next_direction': random.choice(['deepen analysis', 'explore alternatives', 'seek synthesis']),
                'key_themes': ['innovation', 'analysis', 'collaboration'],
                'intervention': 'none'
            } if random.random() > 0.5 else None
        }
    
    def generate_reflection(self, turn_number: int, iteration: int = 1) -> Dict[str, Any]:
        """Generate a realistic reflection scenario."""
        scenario = random.choice(self.reflection_scenarios)
        
        base_reflection = {
            'action_taken': scenario['action'],
            'mediator_id': 'demo-mediator-ai-v1',
            'confidence_score': scenario['confidence'] + random.uniform(-0.1, 0.1),
            'explanation': scenario['explanation'],
            'correction_tags': scenario['tags'],
            'iteration_count': iteration,
            'reflection_timestamp': int(datetime.now().timestamp() * 1000),
            'turn_reference': turn_number
        }
        
        # Add healed message for modify actions
        if scenario['action'] == 'modify':
            healed_messages = [
                "The research clearly demonstrates significant improvements in efficiency and outcomes.",
                "Evidence strongly supports this approach based on peer-reviewed studies.",
                "Data analysis reveals definitive patterns that support this conclusion.",
                "Empirical results consistently show positive outcomes across multiple trials."
            ]
            base_reflection['healed_message'] = random.choice(healed_messages)
        
        return base_reflection
    
    def generate_demo_conversation(self, num_turns: int = 5) -> Dict[str, Any]:
        """Generate a complete demo conversation with reflections."""
        topic = random.choice(self.demo_topics)
        
        conversation_data = {
            'conversation_id': f'demo-{int(datetime.now().timestamp())}',
            'topic': topic,
            'models': self.demo_models,
            'turns': [],
            'reflections': [],
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        # Generate conversation turns
        for turn in range(1, num_turns + 1):
            current_speaker = 'model_a' if turn % 2 == 1 else 'model_b'
            turn_data = self.generate_conversation_turn(turn, current_speaker, topic)
            conversation_data['turns'].append(turn_data)
            
            # Generate reflections (not every turn gets one)
            if random.random() > 0.3:  # 70% chance of reflection
                reflection = self.generate_reflection(turn)
                conversation_data['reflections'].append(reflection)
                
                # Sometimes generate multiple iterations for rejected messages
                if reflection['action_taken'] == 'reject' and random.random() > 0.5:
                    retry_reflection = self.generate_reflection(turn, 2)
                    retry_reflection['action_taken'] = random.choice(['modify', 'pass'])
                    retry_reflection['confidence_score'] += 0.2
                    conversation_data['reflections'].append(retry_reflection)
        
        return conversation_data


def create_demo_endpoint_data():
    """Create structured demo data for API endpoints."""
    generator = DemoDataGenerator()
    demo_data = generator.generate_demo_conversation(8)
    
    return {
        'conversation': demo_data,
        'summary': {
            'total_turns': len(demo_data['turns']),
            'total_reflections': len(demo_data['reflections']),
            'reflection_actions': {
                'pass': len([r for r in demo_data['reflections'] if r['action_taken'] == 'pass']),
                'modify': len([r for r in demo_data['reflections'] if r['action_taken'] == 'modify']),
                'reject': len([r for r in demo_data['reflections'] if r['action_taken'] == 'reject'])
            },
            'avg_confidence': sum(r['confidence_score'] for r in demo_data['reflections']) / len(demo_data['reflections']) if demo_data['reflections'] else 0,
            'topic': demo_data['topic']
        }
    }


if __name__ == "__main__":
    # Generate and print demo data
    demo = create_demo_endpoint_data()
    print("🎭 Demo Data Generated!")
    print(f"Topic: {demo['summary']['topic']}")
    print(f"Turns: {demo['summary']['total_turns']}")
    print(f"Reflections: {demo['summary']['total_reflections']}")
    print(f"Actions: {demo['summary']['reflection_actions']}")
    print(f"Avg Confidence: {demo['summary']['avg_confidence']:.3f}")
