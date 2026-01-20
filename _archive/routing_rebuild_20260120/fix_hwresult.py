"""
Fix HwResult parameter name
"""

with open('hardware_executor.py', 'r') as f:
    content = f.read()

# Fix: rc -> remove it (HwResult doesn't have rc field)
content = content.replace('HwResult(ok=False, rc=1, out="", err=str(e))', 
                          'HwResult(ok=False, out="", err=str(e))')
content = content.replace('HwResult(ok=(proc.returncode == 0), rc=proc.returncode, out=out, err=err)',
                          'HwResult(ok=(proc.returncode == 0), out=out, err=err)')

print("✅ Fixed HwResult parameters")

with open('hardware_executor.py', 'w') as f:
    f.write(content)
