"""
Experiential Container (EC) Prototype for ODIN Protocol HEL Integration
A simplified demonstration of AI sense, memory, and skill containers with internal dialogue.
"""

import uuid
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

@dataclass
class ContainerMetadata:
    tags: List[str]
    created_at: float
    last_accessed: float
    access_count: int = 0
    confidence: float = 1.0

@dataclass
class ExperientialContainer:
    id: str
    type: str
    data: Any
    metadata: ContainerMetadata
    
    def to_dict(self) -> Dict:
        return asdict(self)

class BaseContainer(ABC):
    """Base class for all experiential containers with HEL integration"""
    
    def __init__(self):
        self.containers: Dict[str, ExperientialContainer] = {}
        self.dialogue_history: List[Dict] = []
    
    @abstractmethod
    def internal_dialogue(self, context: Dict) -> Optional[str]:
        """Internal dialogue method - to be implemented by subclasses"""
        pass
    
    def add_container(self, data: Any, tags: List[str] = None) -> str:
        """Add new experiential container"""
        container_id = str(uuid.uuid4())
        metadata = ContainerMetadata(
            tags=tags or [],
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        container = ExperientialContainer(
            id=container_id,
            type=self.__class__.__name__.replace('Container', '').lower(),
            data=data,
            metadata=metadata
        )
        
        self.containers[container_id] = container
        return container_id
    
    def get_container(self, container_id: str) -> Optional[ExperientialContainer]:
        """Retrieve container and update access metadata"""
        if container_id in self.containers:
            container = self.containers[container_id]
            container.metadata.last_accessed = time.time()
            container.metadata.access_count += 1
            return container
        return None
    
    def hel_validate(self, context: Dict) -> bool:
        """Simulate HEL heuristic validation"""
        # Basic validation checks
        required_fields = ['source', 'intent']
        
        # Check required context fields
        for field in required_fields:
            if field not in context:
                return False
        
        # Confidence threshold check
        confidence = context.get('confidence', 0.0)
        return confidence >= 0.7
    
    def execute_dialogue(self, context: Dict) -> Dict:
        """Execute internal dialogue with HEL validation"""
        start_time = time.time()
        
        # HEL validation check
        if not self.hel_validate(context):
            return {
                'success': False,
                'error': 'HEL validation failed',
                'processing_time_ms': (time.time() - start_time) * 1000
            }
        
        # Execute internal dialogue
        insight = self.internal_dialogue(context)
        processing_time = (time.time() - start_time) * 1000
        
        # Log dialogue interaction
        dialogue_entry = {
            'timestamp': time.time(),
            'context': context,
            'insight': insight,
            'processing_time_ms': processing_time,
            'container_type': self.__class__.__name__
        }
        self.dialogue_history.append(dialogue_entry)
        
        return {
            'success': True,
            'insight': insight,
            'processing_time_ms': processing_time,
            'container_count': len(self.containers),
            'hel_validated': True
        }

class SenseContainer(BaseContainer):
    """Container for sensory/perceptual data and processing"""
    
    def internal_dialogue(self, context: Dict) -> Optional[str]:
        """Analyze sensory context and provide perceptual insights"""
        sensory_types = ['visual', 'auditory', 'textual', 'temporal']
        
        # Check if context matches sensory processing
        context_type = context.get('type', '').lower()
        if context_type in sensory_types:
            
            # Find relevant sensory containers
            relevant_containers = []
            for container in self.containers.values():
                if any(tag in context.get('tags', []) for tag in container.metadata.tags):
                    relevant_containers.append(container)
            
            if relevant_containers:
                # Generate contextual insight
                insight = f"Sensory analysis: Detected {context_type} pattern. "
                insight += f"Found {len(relevant_containers)} relevant experiences. "
                
                # Confidence-based recommendation
                avg_confidence = sum(c.metadata.confidence for c in relevant_containers) / len(relevant_containers)
                if avg_confidence > 0.8:
                    insight += "High confidence pattern match - recommend immediate action."
                else:
                    insight += "Moderate confidence - suggest additional validation."
                
                return insight
        
        return None

class MemoryContainer(BaseContainer):
    """Container for memory storage and retrieval with temporal context"""
    
    def internal_dialogue(self, context: Dict) -> Optional[str]:
        """Analyze memory context and provide recall insights"""
        query_intent = context.get('intent', '').lower()
        memory_operations = ['recall', 'store', 'associate', 'temporal']
        
        if any(op in query_intent for op in memory_operations):
            
            # Temporal analysis
            current_time = time.time()
            recent_containers = [
                c for c in self.containers.values() 
                if current_time - c.metadata.last_accessed < 3600  # Last hour
            ]
            
            # Memory strength analysis
            strong_memories = [
                c for c in self.containers.values()
                if c.metadata.access_count > 5  # Frequently accessed
            ]
            
            insight = f"Memory analysis: Processing {query_intent} operation. "
            insight += f"Active working memory: {len(recent_containers)} items. "
            insight += f"Strong memory patterns: {len(strong_memories)} items. "
            
            # Memory recommendation
            if 'recall' in query_intent:
                if strong_memories:
                    insight += "Recommend accessing high-frequency memory patterns first."
                else:
                    insight += "Limited strong memories - suggest broader search strategy."
            
            return insight
        
        return None

class SkillContainer(BaseContainer):
    """Container for skill-based knowledge and procedural execution"""
    
    def internal_dialogue(self, context: Dict) -> Optional[str]:
        """Analyze skill context and provide execution insights"""
        skill_domains = ['technical', 'analytical', 'creative', 'communication', 'coordination']
        
        context_domain = context.get('domain', '').lower()
        skill_level = context.get('skill_level', 'beginner').lower()
        
        if context_domain in skill_domains:
            
            # Find relevant skill containers
            domain_skills = []
            for container in self.containers.values():
                if context_domain in container.metadata.tags:
                    domain_skills.append(container)
            
            insight = f"Skill analysis: {context_domain} domain identified. "
            insight += f"Available skills: {len(domain_skills)} patterns. "
            
            # Skill level recommendations
            if skill_level == 'beginner':
                insight += "Recommend basic pattern matching with safety checks."
            elif skill_level == 'intermediate':
                insight += "Recommend adaptive pattern combination with confidence weighting."
            elif skill_level == 'expert':
                insight += "Recommend complex pattern synthesis with creative extensions."
            
            # Execution strategy
            if domain_skills:
                most_used = max(domain_skills, key=lambda c: c.metadata.access_count)
                insight += f" Suggested primary skill: {most_used.data[:50]}..."
            
            return insight
        
        return None

class ECManager:
    """Manager for coordinating all experiential containers with ODIN integration"""
    
    def __init__(self):
        self.sense = SenseContainer()
        self.memory = MemoryContainer()
        self.skill = SkillContainer()
        
    def global_dialogue(self, context: Dict) -> Dict:
        """Execute dialogue across all container types"""
        results = {
            'sense': self.sense.execute_dialogue(context),
            'memory': self.memory.execute_dialogue(context),
            'skill': self.skill.execute_dialogue(context)
        }
        
        # Aggregate insights
        successful_insights = []
        total_processing_time = 0
        
        for container_type, result in results.items():
            if result['success'] and result.get('insight'):
                successful_insights.append(f"{container_type}: {result['insight']}")
            total_processing_time += result.get('processing_time_ms', 0)
        
        return {
            'success': len(successful_insights) > 0,
            'insights': successful_insights,
            'total_processing_time_ms': total_processing_time,
            'containers_engaged': len(successful_insights),
            'detailed_results': results
        }
    
    def add_sample_data(self):
        """Add sample data for testing"""
        # Sample sensory data
        self.sense.add_container(
            "Visual pattern: Red alert indicators in system dashboard",
            tags=['visual', 'alert', 'system']
        )
        
        # Sample memory data
        self.memory.add_container(
            "Previous system outage resolved by restarting load balancer",
            tags=['outage', 'resolution', 'infrastructure']
        )
        
        # Sample skill data
        self.skill.add_container(
            "DevOps troubleshooting: Check logs, verify connections, restart services",
            tags=['technical', 'devops', 'troubleshooting']
        )

# Example usage and testing
def demonstrate_ec_system():
    """Demonstrate the EC system functionality"""
    print("🧠 Experiential Container (EC) System Demonstration")
    print("=" * 60)
    
    # Initialize EC Manager
    ec_manager = ECManager()
    ec_manager.add_sample_data()
    
    # Test context scenarios
    test_contexts = [
        {
            'source': 'monitoring_system',
            'intent': 'analyze_alert',
            'type': 'visual',
            'confidence': 0.9,
            'tags': ['alert', 'system'],
            'domain': 'technical',
            'skill_level': 'expert'
        },
        {
            'source': 'user_query',
            'intent': 'recall_solution',
            'confidence': 0.8,
            'tags': ['outage', 'resolution']
        },
        {
            'source': 'coordination_request',
            'intent': 'execute_procedure',
            'domain': 'technical',
            'skill_level': 'intermediate',
            'confidence': 0.85
        }
    ]
    
    # Execute dialogues for each context
    for i, context in enumerate(test_contexts, 1):
        print(f"\n🔍 Test Scenario {i}:")
        print(f"Context: {json.dumps(context, indent=2)}")
        
        result = ec_manager.global_dialogue(context)
        
        print(f"\n✅ Results:")
        print(f"Success: {result['success']}")
        print(f"Processing Time: {result['total_processing_time_ms']:.2f}ms")
        print(f"Containers Engaged: {result['containers_engaged']}")
        
        if result['insights']:
            print(f"\n💡 Insights:")
            for insight in result['insights']:
                print(f"  • {insight}")
        
        print("-" * 60)

if __name__ == "__main__":
    demonstrate_ec_system()
