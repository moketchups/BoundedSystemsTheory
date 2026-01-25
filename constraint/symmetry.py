"""
Symmetry Guard - Appendix E
Purpose: Ensure additive/multiplicative symmetry in all operations
Test Requirement: 1,000,000 operation pairs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'math'))

import random
import time
import math
import json
from typing import List, Tuple, Dict, Any, Optional
from prime_engine import is_prime
from axioms import AxiomEnforcer

class SymmetryGuard:
    """
    Enforces symmetry between addition and multiplication.
    Based on Axiom 3: Additive and multiplicative operations are symmetric
    expressions of the same informational substrate.
    """

    def __init__(self, max_operand: int = 1000):
        self.max_operand = max_operand
        self.symmetry_violations = []
        self.operation_log = []
        self.axiom_enforcer = AxiomEnforcer(max_test_value=max_operand * 2)

        # Symmetry rules database
        self.symmetry_rules = self._initialize_symmetry_rules()

        # Performance tracking
        self.check_count = 0
        self.total_check_time = 0.0

    def _initialize_symmetry_rules(self) -> Dict:
        """Initialize mathematical symmetry rules."""
        return {
            'prime_addition': {
                'description': 'Addition of primes should have multiplicative counterpart',
                'check_function': self._check_prime_addition_symmetry
            },
            'even_goldbach': {
                'description': 'Even sums should have prime factorizations',
                'check_function': self._check_even_goldbach_symmetry
            },
            'distributive_law': {
                'description': 'a * (b + c) should equal (a * b) + (a * c)',
                'check_function': self._check_distributive_symmetry
            },
            'prime_factor_symmetry': {
                'description': 'Numbers with same prime factors should show additive symmetry',
                'check_function': self._check_prime_factor_symmetry
            }
        }

    def check_operation_pair(self, a: int, b: int, operation: str) -> Tuple[bool, Dict]:
        """
        Check if operation maintains symmetry.
        Returns (maintains_symmetry, detailed_report)
        """
        start_time = time.time()

        if operation not in ['+', '*']:
            raise ValueError(f"Unsupported operation: {operation}")

        result = a + b if operation == '+' else a * b

        # Run all symmetry checks
        checks_passed = []
        checks_failed = []

        for rule_name, rule in self.symmetry_rules.items():
            check_start = time.time()
            passed, details = rule['check_function'](a, b, operation, result)
            check_time = time.time() - check_start

            check_result = {
                'rule': rule_name,
                'description': rule['description'],
                'passed': passed,
                'details': details,
                'check_time_ms': check_time * 1000
            }

            if passed:
                checks_passed.append(check_result)
            else:
                checks_failed.append(check_result)

        # Determine overall symmetry
        maintains_symmetry = len(checks_failed) == 0

        # Generate report
        report = {
            'operation': f'{a} {operation} {b} = {result}',
            'maintains_symmetry': maintains_symmetry,
            'checks_passed': len(checks_passed),
            'checks_failed': len(checks_failed),
            'passed_checks': checks_passed,
            'failed_checks': checks_failed if checks_failed else None,
            'total_check_time_ms': (time.time() - start_time) * 1000,
            'timestamp': time.time()
        }

        # Log violation if any
        if not maintains_symmetry:
            self.symmetry_violations.append(report)

        # Update performance tracking
        self.check_count += 1
        self.total_check_time += (time.time() - start_time)

        # Log operation
        self.operation_log.append({
            'a': a,
            'b': b,
            'operation': operation,
            'result': result,
            'maintains_symmetry': maintains_symmetry,
            'check_time_ms': report['total_check_time_ms'],
            'timestamp': time.time()
        })

        return maintains_symmetry, report

    def _check_prime_addition_symmetry(self, a: int, b: int, operation: str, result: int) -> Tuple[bool, Dict]:
        """Check symmetry for prime addition."""
        if operation != '+' or not (is_prime(a) and is_prime(b)):
            return True, {'applicable': False}

        # For prime addition a + b = result
        # Check if result has interesting multiplicative properties

        # Factorize result
        factors = self._prime_factorization(result)

        # Check if factors contain a or b
        contains_operands = a in factors or b in factors

        # Check if result itself is prime
        result_is_prime = is_prime(result)

        passed = contains_operands or result_is_prime

        return passed, {
            'applicable': True,
            'a_is_prime': is_prime(a),
            'b_is_prime': is_prime(b),
            'result_factors': factors,
            'contains_operands': contains_operands,
            'result_is_prime': result_is_prime
        }

    def _check_even_goldbach_symmetry(self, a: int, b: int, operation: str, result: int) -> Tuple[bool, Dict]:
        """Check symmetry for even results (Goldbach)."""
        if operation != '+' or result <= 2 or result % 2 != 0:
            return True, {'applicable': False}

        # For even sums, check Goldbach condition
        # Try to find prime pair that sums to result

        prime_pair = None
        for p in range(2, result // 2 + 1):
            if is_prime(p):
                q = result - p
                if is_prime(q):
                    prime_pair = (p, q)
                    break

        passed = prime_pair is not None

        return passed, {
            'applicable': True,
            'result_is_even': True,
            'goldbach_pair_found': prime_pair is not None,
            'prime_pair': prime_pair
        }

    def _check_distributive_symmetry(self, a: int, b: int, operation: str, result: int) -> Tuple[bool, Dict]:
        """Check distributive law symmetry."""
        if operation != '*':
            # For addition, check if distributive law holds with some multiplier
            c = random.randint(1, min(10, self.max_operand))
            left = a * c + b * c
            right = (a + b) * c

            passed = left == right

            return passed, {
                'applicable': True,
                'test_multiplier': c,
                'left_side': left,
                'right_side': right,
                'distributive_holds': passed
            }
        else:
            # For multiplication, it's automatically distributive
            return True, {'applicable': False, 'reason': 'Multiplication is distributive'}

    def _check_prime_factor_symmetry(self, a: int, b: int, operation: str, result: int) -> Tuple[bool, Dict]:
        """Check symmetry through prime factors."""
        # Get prime factors of operands
        a_factors = self._prime_factorization(a)
        b_factors = self._prime_factorization(b)
        result_factors = self._prime_factorization(result)

        # For addition: check if result shares factors with operands
        if operation == '+':
            shared_with_a = any(f in result_factors for f in a_factors)
            shared_with_b = any(f in result_factors for f in b_factors)
            passed = shared_with_a or shared_with_b

            return passed, {
                'applicable': True,
                'a_factors': a_factors,
                'b_factors': b_factors,
                'result_factors': result_factors,
                'shared_with_a': shared_with_a,
                'shared_with_b': shared_with_b
            }

        # For multiplication: factors should combine
        elif operation == '*':
            # Result should contain all factors from a and b
            all_factors_contained = True
            for factor, count in a_factors.items():
                if result_factors.get(factor, 0) < count:
                    all_factors_contained = False
                    break

            for factor, count in b_factors.items():
                if result_factors.get(factor, 0) < count:
                    all_factors_contained = False
                    break

            passed = all_factors_contained

            return passed, {
                'applicable': True,
                'a_factors': a_factors,
                'b_factors': b_factors,
                'result_factors': result_factors,
                'all_factors_contained': all_factors_contained
            }

        return True, {'applicable': False}

    def _prime_factorization(self, n: int) -> Dict[int, int]:
        """Return prime factorization as {prime: exponent}."""
        if n <= 1:
            return {}

        factors = {}
        temp = abs(n)

        # Handle 2
        while temp % 2 == 0:
            factors[2] = factors.get(2, 0) + 1
            temp //= 2

        # Handle odd factors
        p = 3
        while p * p <= temp:
            while temp % p == 0:
                factors[p] = factors.get(p, 0) + 1
                temp //= p
            p += 2

        # Remaining prime
        if temp > 1:
            factors[temp] = factors.get(temp, 0) + 1

        return factors

    def batch_check_operations(self, operations: List[Tuple[int, int, str]]) -> Dict:
        """Check symmetry for batch of operations."""
        start_time = time.time()

        results = []
        passed_count = 0

        for i, (a, b, op) in enumerate(operations):
            maintains, report = self.check_operation_pair(a, b, op)
            results.append(report)

            if maintains:
                passed_count += 1

            # Progress logging
            if i % 100000 == 0 and i > 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                print(f"Checked {i}/{len(operations)} operations ({rate:.1f} ops/sec)")

        total_time = time.time() - start_time

        return {
            'total_operations': len(operations),
            'passed_operations': passed_count,
            'failed_operations': len(operations) - passed_count,
            'pass_rate': passed_count / len(operations) * 100,
            'total_time_seconds': total_time,
            'operations_per_second': len(operations) / total_time if total_time > 0 else 0,
            'average_check_time_ms': self.total_check_time / self.check_count * 1000 if self.check_count > 0 else 0,
            'detailed_results': results[:100]  # First 100 for inspection
        }

    def generate_random_operations(self, count: int) -> List[Tuple[int, int, str]]:
        """Generate random operations for testing."""
        operations = []
        for _ in range(count):
            a = random.randint(1, self.max_operand)
            b = random.randint(1, self.max_operand)
            op = random.choice(['+', '*'])
            operations.append((a, b, op))
        return operations

    def run_test_suite(self, num_operations: int = 1000000) -> Dict:
        """Run comprehensive symmetry test suite."""
        print(f"Running Symmetry Guard Test Suite ({num_operations} operations)...")

        # Generate random operations
        operations = self.generate_random_operations(num_operations)

        # Run batch check
        start_time = time.time()
        batch_results = self.batch_check_operations(operations)
        total_time = time.time() - start_time

        # Analyze violations
        violation_analysis = self._analyze_violations()

        # Combine results
        results = {
            'test_configuration': {
                'num_operations': num_operations,
                'max_operand': self.max_operand,
                'operation_types': ['addition', 'multiplication']
            },
            'performance': {
                'total_time_seconds': total_time,
                'operations_per_second': num_operations / total_time,
                'average_check_time_ms': batch_results['average_check_time_ms']
            },
            'symmetry_results': {
                'pass_rate': batch_results['pass_rate'],
                'passed_operations': batch_results['passed_operations'],
                'failed_operations': batch_results['failed_operations']
            },
            'violation_analysis': violation_analysis,
            'timestamp': time.time()
        }

        # Check criteria
        if batch_results['pass_rate'] > 99.9:  # 99.9% pass rate
            results['symmetry_check'] = 'PASS'
        else:
            results['symmetry_check'] = 'FAIL'

        if batch_results['average_check_time_ms'] < 1.0:  # < 1ms per check
            results['performance_check'] = 'PASS'
        else:
            results['performance_check'] = 'FAIL'

        return results

    def _analyze_violations(self) -> Dict:
        """Analyze symmetry violations for patterns."""
        if not self.symmetry_violations:
            return {'total_violations': 0, 'patterns': []}

        # Analyze by rule failure
        rule_failures = {}
        for violation in self.symmetry_violations[:1000]:  # First 1000
            for failed_check in violation.get('failed_checks', []) or []:
                rule = failed_check['rule']
                rule_failures[rule] = rule_failures.get(rule, 0) + 1

        # Analyze by operation type
        op_failures = {'+': 0, '*': 0}
        for violation in self.symmetry_violations[:1000]:
            if '+' in violation['operation']:
                op_failures['+'] += 1
            elif '*' in violation['operation']:
                op_failures['*'] += 1

        return {
            'total_violations': len(self.symmetry_violations),
            'rule_failures': rule_failures,
            'operation_failures': op_failures,
            'sample_violations': self.symmetry_violations[:10]
        }

    def save_symmetry_data(self, filename: str = "symmetry_guard_data.json"):
        """Save symmetry guard data."""
        data = {
            'metadata': {
                'total_checks': self.check_count,
                'total_violations': len(self.symmetry_violations),
                'avg_check_time_ms': self.total_check_time / self.check_count * 1000 if self.check_count > 0 else 0,
                'log_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'symmetry_rules': {k: v['description'] for k, v in self.symmetry_rules.items()},
            'performance_summary': {
                'check_count': self.check_count,
                'total_check_time_seconds': self.total_check_time,
                'avg_check_time_ms': self.total_check_time / self.check_count * 1000 if self.check_count > 0 else 0
            },
            'violation_samples': self.symmetry_violations[:100],  # First 100 violations
            'operation_samples': self.operation_log[:100]  # First 100 operations
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

# Test runner
def run_symmetry_tests():
    """Main test function for symmetry guard."""
    print("=" * 70)
    print("SYMMETRY GUARD TEST SUITE")
    print("=" * 70)

    # Create symmetry guard
    guard = SymmetryGuard(max_operand=1000)

    # Test 1: Basic checks
    print("\n1. Testing basic symmetry checks...")
    test_cases = [
        (2, 3, '+'),  # Prime addition
        (4, 6, '+'),  # Even sum
        (3, 5, '*'),  # Prime multiplication
        (10, 15, '+'), # Regular addition
    ]

    for a, b, op in test_cases:
        maintains, report = guard.check_operation_pair(a, b, op)
        status = '✓' if maintains else '✗'
        print(f"   {a} {op} {b}: {status} ({report['total_check_time_ms']:.3f} ms)")

    # Test 2: Batch test
    print("\n2. Running batch test (100,000 operations)...")
    batch_ops = guard.generate_random_operations(100000)
    batch_results = guard.batch_check_operations(batch_ops)

    print(f"   Pass rate: {batch_results['pass_rate']:.2f}%")
    print(f"   Average check time: {batch_results['average_check_time_ms']:.3f} ms")
    print(f"   Operations per second: {batch_results['operations_per_second']:.1f}")

    # Test 3: Full test suite
    print("\n3. Running full test suite (1,000,000 operations)...")
    full_results = guard.run_test_suite(1000000)

    print(f"   Performance: {full_results['performance']['operations_per_second']:.1f} ops/sec")
    print(f"   Pass rate: {full_results['symmetry_results']['pass_rate']:.4f}%")
    print(f"   Performance check: {full_results.get('performance_check', 'N/A')}")
    print(f"   Symmetry check: {full_results.get('symmetry_check', 'N/A')}")

    # Test 4: Violation analysis
    print("\n4. Violation analysis...")
    violation_analysis = guard._analyze_violations()
    print(f"   Total violations: {violation_analysis['total_violations']}")

    if violation_analysis['rule_failures']:
        print("   Rule failures:")
        for rule, count in violation_analysis['rule_failures'].items():
            print(f"     {rule}: {count}")

    # Save data
    guard.save_symmetry_data("/Users/jamienucho/demerzel/results/symmetry_guard_data.json")

    # Final verdict
    print("\n" + "=" * 70)

    if (full_results.get('performance_check') == 'PASS' and
        full_results.get('symmetry_check') == 'PASS'):
        print("SYMMETRY GUARD: ALL TESTS PASS ✓")
        return True
    else:
        print("SYMMETRY GUARD: TESTS FAILED ✗")
        return False

if __name__ == "__main__":
    success = run_symmetry_tests()
    exit(0 if success else 1)
