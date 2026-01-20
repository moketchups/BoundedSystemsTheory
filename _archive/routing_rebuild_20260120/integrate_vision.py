"""
Integrate vision filter into brain_controller
"""

with open('brain_controller.py', 'r') as f:
    content = f.read()

# Add import
old_imports = '''# Multi-model cognitive
from multi_model_cognitive import MultiModelCognitive'''

new_imports = '''# Multi-model cognitive
from multi_model_cognitive import MultiModelCognitive
from vision_filter import VisionFilter'''

content = content.replace(old_imports, new_imports)
print("✅ Added VisionFilter import")

# Initialize vision after router
old_init = '''    router = RouterEngine()
    analyzer = CodeAnalyzer()'''

new_init = '''    router = RouterEngine()
    analyzer = CodeAnalyzer()
    
    # Vision filter for echo suppression
    vision = VisionFilter(motion_threshold=50000, speaking_persist=0.8)
    if vision.start():
        print("[VISION] Lip detection active")
    else:
        print("[VISION] WARNING: Could not start, echo suppression disabled")
        vision = None'''

content = content.replace(old_init, new_init)
print("✅ Added vision initialization")

# Add vision stop to cleanup
old_cleanup = '''    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Cleanup complete")'''

new_cleanup = '''    finally:
        if vision:
            vision.stop()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[VOICE] Cleanup complete")'''

content = content.replace(old_cleanup, new_cleanup)
print("✅ Added vision cleanup")

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("\n✅ Vision integrated! Now we need to use it in follow-up mode.")
