#!/usr/bin/env python3
"""
ODIN CLI - Command Line Interface for ODIN Protocol
Provides tools for compiling, validating, and inspecting ODIN messages
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Optional

# Import ODIN SDK
try:
    from odin_sdk import OdinSDK, OdinMessage
    from odin_sdk.enhanced import OdinMessageBuilder
except ImportError:
    print("❌ ODIN SDK not found. Please run 'odin-cli compile' first.")
    sys.exit(1)

def compile_proto_files():
    """Compile .proto files to Python SDK"""
    import subprocess
    
    # Check for protoc
    try:
        subprocess.run(['python', '-m', 'grpc_tools.protoc', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ grpc_tools not found. Install with: pip install grpcio-tools")
        return False
    
    # Create SDK directory
    sdk_dir = Path("odin_sdk")
    sdk_dir.mkdir(exist_ok=True)
    
    # Find proto files
    proto_files = list(Path(".").glob("*.proto"))
    if not proto_files:
        print("❌ No .proto files found in current directory")
        return False
    
    print(f"📦 Compiling {len(proto_files)} proto file(s)...")
    
    for proto_file in proto_files:
        print(f"🔨 Compiling {proto_file}...")
        
        try:
            subprocess.run([
                'python', '-m', 'grpc_tools.protoc',
                '--proto_path=.',
                f'--python_out={sdk_dir}',
                f'--pyi_out={sdk_dir}',
                str(proto_file)
            ], check=True)
            
            print(f"✅ Generated {sdk_dir}/{proto_file.stem}_pb2.py")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to compile {proto_file}: {e}")
            return False
    
    print("🎉 ODIN SDK compilation complete!")
    return True

def validate_odin_file(filepath: str) -> bool:
    """Validate a .odin file has required fields and correct types"""
    print(f"🔍 Validating {filepath}...")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    try:
        # Load the message
        message = OdinSDK.load_message(filepath)
        if message is None:
            print("❌ Failed to load ODIN message from file")
            return False
        
        # Validate required fields
        errors = []
        
        if not message.trace_id:
            errors.append("Missing trace_id")
        
        if not message.session_id:
            errors.append("Missing session_id")
        
        if not message.sender_id:
            errors.append("Missing sender_id")
        
        if not message.receiver_id:
            errors.append("Missing receiver_id")
        
        if not message.role:
            errors.append("Missing role")
        
        if not message.raw_output:
            errors.append("Missing raw_output")
        
        if message.timestamp <= 0:
            errors.append("Invalid timestamp")
        
        # Validate ranges
        if not (0.0 <= message.semantic_drift_score <= 1.0):
            errors.append("semantic_drift_score must be between 0.0 and 1.0")
        
        if message.healing_metadata.confidence < 0.0 or message.healing_metadata.confidence > 1.0:
            errors.append("healing_metadata.confidence must be between 0.0 and 1.0")
        
        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"   • {error}")
            return False
        
        print("✅ Validation passed!")
        
        # Print summary
        print(f"📊 Message Summary:")
        print(f"   • Trace ID: {message.trace_id}")
        print(f"   • Session ID: {message.session_id}")
        print(f"   • Sender: {message.sender_id}")
        print(f"   • Receiver: {message.receiver_id}")
        print(f"   • Role: {message.role}")
        print(f"   • Timestamp: {message.timestamp}")
        print(f"   • Semantic Drift: {message.semantic_drift_score:.3f}")
        
        if message.context.conversation_id:
            print(f"   • Conversation: {message.context.conversation_id} (Turn {message.context.turn_number})")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def inspect_odin_file(filepath: str, format_type: str = "json") -> bool:
    """Load and pretty-print a .odin file"""
    print(f"🔍 Inspecting {filepath}...")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    try:
        from google.protobuf.json_format import MessageToJson, MessageToDict
        
        # Load the message
        message = OdinSDK.load_message(filepath)
        if message is None:
            print("❌ Failed to load ODIN message from file")
            return False
        
        if format_type.lower() == "json":
            # Convert to JSON and pretty print
            json_str = MessageToJson(message, indent=2, sort_keys=True)
            print("📄 ODIN Message (JSON format):")
            print(json_str)
        
        elif format_type.lower() == "dict":
            # Convert to dict and pretty print
            msg_dict = MessageToDict(message)
            print("📄 ODIN Message (Dict format):")
            print(json.dumps(msg_dict, indent=2, sort_keys=True))
        
        elif format_type.lower() == "text":
            # Print as protobuf text format
            print("📄 ODIN Message (Text format):")
            print(str(message))
        
        else:
            print(f"❌ Unknown format: {format_type}. Use 'json', 'dict', or 'text'")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Inspection error: {e}")
        return False


def inspect_reflection_file(filepath: str, format_type: str = "json") -> bool:
    """Load and pretty-print a .odinr reflection file"""
    print(f"🔍 Inspecting reflection {filepath}...")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    try:
        from google.protobuf.json_format import MessageToJson, MessageToDict
        from mediator_ai import load_reflection
        
        # Load the reflection
        reflection = load_reflection(filepath)
        if reflection is None:
            print("❌ Failed to load ODIN reflection from file")
            return False
        
        if format_type.lower() == "json":
            # Convert to JSON and pretty print with color coding
            json_str = MessageToJson(reflection, indent=2, sort_keys=True)
            print("📄 ODIN Reflection (JSON format):")
            print(json_str)
            
            # Add color-coded summary
            print("\n" + "="*50)
            action_color = {
                'pass': '🟢',
                'modify': '🟡', 
                'reject': '🔴'
            }
            action_emoji = action_color.get(reflection.action_taken, '⚪')
            print(f"{action_emoji} Action: {reflection.action_taken.upper()}")
            print(f"🤖 Mediator: {reflection.mediator_id}")
            print(f"📊 Confidence: {reflection.confidence_score:.2f}")
            print(f"🔄 Iteration: {reflection.iteration_count}")
            
            if reflection.correction_tags:
                print(f"🏷️  Corrections: {', '.join(reflection.correction_tags)}")
            
            print(f"💭 Explanation: {reflection.explanation}")
            
        elif format_type.lower() == "text":
            # Print as protobuf text format
            print("📄 ODIN Reflection (Text format):")
            print(str(reflection))
        
        else:
            print(f"❌ Unknown format: {format_type}. Use 'json' or 'text'")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reflection inspection error: {e}")
        return False


def show_reflection_stats(log_file: str = "logs/reflections.jsonl") -> bool:
    """Show analytics from reflection log file"""
    print(f"📊 Analyzing reflection statistics from {log_file}...")
    
    try:
        from mediator_ai import ReflectionLogger
        
        logger = ReflectionLogger(log_file)
        stats = logger.get_reflection_stats()
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
            return False
        
        print("\n📈 REFLECTION ANALYTICS")
        print("="*40)
        print(f"Total Reflections: {stats['total_reflections']}")
        print(f"Average Confidence: {stats['avg_confidence']:.3f}")
        print()
        
        # Action breakdown
        print("🎯 ACTION BREAKDOWN:")
        for action, count in stats['actions'].items():
            percentage = (count / stats['total_reflections'] * 100) if stats['total_reflections'] > 0 else 0
            emoji = {'pass': '🟢', 'modify': '🟡', 'reject': '🔴'}.get(action, '⚪')
            print(f"  {emoji} {action.title()}: {count} ({percentage:.1f}%)")
        
        print()
        
        # Top corrections
        if stats['common_corrections']:
            print("🏷️  MOST COMMON CORRECTIONS:")
            sorted_corrections = sorted(stats['common_corrections'].items(), 
                                      key=lambda x: x[1], reverse=True)
            for correction, count in sorted_corrections[:5]:
                print(f"  • {correction}: {count}")
        
        print()
        
        # Mediators
        if stats['mediators']:
            print("🤖 ACTIVE MEDIATORS:")
            for mediator in stats['mediators']:
                print(f"  • {mediator}")
        
        return True
        
    except Exception as e:
        print(f"❌ Stats analysis error: {e}")
        return False

def create_sample_message():
    """Create a sample ODIN message for testing"""
    print("🎯 Creating sample ODIN message...")
    
    try:
        # Create a sample message using the builder
        message = (OdinSDK.create_message()
                  .set_ids("trace-123", "session-456", "gpt-4o", "gemini-1.5-flash")
                  .set_role("assistant")
                  .set_content("Hello, how can I help you today?", "Hello, how can I help you today?")
                  .set_semantic_drift(0.05)
                  .set_healing_metadata("auto_correct", 0.95, "doc-789", "Minor grammar correction")
                  .set_conversation_context("conv-abc", 1, "dialogue", "Customer Support", ["greeting", "assistance"])
                  .set_performance_metrics(1250, 0.92, 0.88, 12, 0.6, "gpt-4o-2024")
                  .build())
        
        # Save to file
        filename = "sample_message.odin"
        if OdinSDK.save_message(message, filename):
            print(f"✅ Sample message saved to {filename}")
            
            # Validate it
            if validate_odin_file(filename):
                print("✅ Sample message validation passed")
            
            return True
        else:
            print("❌ Failed to save sample message")
            return False
            
    except Exception as e:
        print(f"❌ Error creating sample message: {e}")
        return False

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ODIN CLI - Command Line Interface for ODIN Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  odin-cli compile              # Compile .proto files to SDK
  odin-cli validate message.odin  # Validate a .odin file
  odin-cli inspect message.odin   # Inspect a .odin file (JSON format)
  odin-cli inspect message.odin --format text  # Inspect as text
  odin-cli sample               # Create a sample .odin file
  odin-cli inspect-reflection reflection.odinr  # Inspect a reflection file
  odin-cli reflection-stats     # Show reflection analytics
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile .proto files to Python SDK')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a .odin file')
    validate_parser.add_argument('file', help='Path to .odin file to validate')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect and pretty-print a .odin file')
    inspect_parser.add_argument('file', help='Path to .odin file to inspect')
    inspect_parser.add_argument('--format', choices=['json', 'dict', 'text'], default='json',
                               help='Output format (default: json)')
    
    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Create a sample .odin file for testing')
    
    # Inspect reflection command
    inspect_reflection_parser = subparsers.add_parser('inspect-reflection', 
                                                     help='Inspect and pretty-print a .odinr reflection file')
    inspect_reflection_parser.add_argument('file', help='Path to .odinr reflection file to inspect')
    inspect_reflection_parser.add_argument('--format', choices=['json', 'text'], default='json',
                                          help='Output format (default: json)')
    
    # Reflection stats command
    stats_parser = subparsers.add_parser('reflection-stats', help='Show reflection analytics')
    stats_parser.add_argument('--log-file', default='logs/reflections.jsonl', 
                             help='Path to reflection log file (default: logs/reflections.jsonl)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    success = False
    
    if args.command == 'compile':
        success = compile_proto_files()
    
    elif args.command == 'validate':
        success = validate_odin_file(args.file)
    
    elif args.command == 'inspect':
        success = inspect_odin_file(args.file, args.format)
    
    elif args.command == 'sample':
        success = create_sample_message()
    
    elif args.command == 'inspect-reflection':
        success = inspect_reflection_file(args.file, args.format)
    
    elif args.command == 'reflection-stats':
        success = show_reflection_stats(args.log_file)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
