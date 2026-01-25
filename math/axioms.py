"""
Axiom Enforcement Engine - Appendix C
Mathematical Basis: Axioms 2 and 3 (Completeness and Symmetry)
Test Requirement: 10,000 random integer operations
"""

import random
import time
import hashlib
from typing import Dict, List, Tuple, Any, Set
from prime_engine import is_prime
from goldbach import GoldbachVerifier

class AxiomEnforcer:
    """
    Enforces Axioms 2 (Completeness) and 3 (Symmetry) for all operations.
    """

    def __init__(self, max_test_value: int = 10000):
        self.max_test_value = max_test_value
        self.completeness_violations = []
        self.symmetry_violations = []
        self.operation_log = []
        self.goldbach_verifier = GoldbachVerifier(max_test_value)

    # AXIOM 2: COMPLETENESS
    def check_completeness(self, n: int) -> Tuple[bool, Dict]:
        """
        Axiom 2: System is informationally complete and consistent.
        No output exists in isolation.

        For an integer n, check if it has a representation in the atomic base:
        1. As a single prime (only valid for primes)
        2. As sum of primes (Goldbach for evens > 2)
        3. As product of primes (prime factorization)
        """
        result = {
            'number': n,
            'has_representation': False,
            'representations': [],
            'violation_type': None,
            'timestamp': time.time()
        }

        # Representation 1: Single prime
        if is_prime(n):
            result['representations'].append({
                'type': 'single_prime',
                'value': n,
                'description': f'{n} is itself a prime atom'
            })
            result['has_representation'] = True

        # Representation 2: Sum of primes (for even numbers > 2)
        if n > 2 and n % 2 == 0:
            verified, pair = self.goldbach_verifier.verify_single(n)
            if verified and pair:
                p1, p2 = pair
                result['representations'].append({
                    'type': 'sum_of_primes',
                    'values': (p1, p2),
                    'description': f'{n} = {p1} + {p2}'
                })
                result['has_representation'] = True

        # Representation 3: Product of primes (prime factorization)
        factors = self.prime_factorization(n)
        if factors and len(factors) > 0:
            # Format as product string
            factor_str = ' × '.join(f'{p}^{e}' if e > 1 else str(p)
                                  for p, e in factors.items())
            result['representations'].append({
                'type': 'product_of_primes',
                'values': factors,
                'description': f'{n} = {factor_str}'
            })
            result['has_representation'] = True

        # Check if number has NO representation (violates Axiom 2)
        if not result['has_representation']:
            result['violation_type'] = 'completeness'
            self.completeness_violations.append(result)

        return result['has_representation'], result

    def prime_factorization(self, n: int) -> Dict[int, int]:
        """Return prime factorization of n as {prime: exponent} dict"""
        if n <= 1:
            return {}

        factors = {}
        temp = abs(n)

        # Handle 2 separately
        while temp % 2 == 0:
            factors[2] = factors.get(2, 0) + 1
            temp //= 2

        # Check odd factors
        p = 3
        while p * p <= temp:
            while temp % p == 0:
                factors[p] = factors.get(p, 0) + 1
                temp //= p
            p += 2

        # If anything remains, it's prime
        if temp > 1:
            factors[temp] = factors.get(temp, 0) + 1

        return factors

    # AXIOM 3: SYMMETRY
    def check_symmetry(self, a: int, b: int, operation: str) -> Tuple[bool, Dict]:
        """
        Axiom 3: Additive and multiplicative operations are symmetric
        expressions of the same informational substrate.

        Check if operation maintains symmetry between addition and multiplication.
        """
        result = {
            'operation': f'{a} {operation} {b}',
            'maintains_symmetry': False,
            'symmetry_check': {},
            'violation_type': None,
            'timestamp': time.time()
        }

        if operation == '+':
            # For addition: check if there's a corresponding multiplicative structure
            sum_result = a + b

            # Check 1: Can the sum be represented as product of primes?
            sum_factors = self.prime_factorization(sum_result)
            result['symmetry_check']['sum_as_product'] = {
                'value': sum_result,
                'factors': sum_factors,
                'has_representation': len(sum_factors) > 0
            }

            # Check 2: Do the operands have multiplicative relationships?
            # Check if a and b share prime factors (suggests common substrate)
            a_factors = set(self.prime_factorization(a).keys())
            b_factors = set(self.prime_factorization(b).keys())
            common_factors = a_factors.intersection(b_factors)
            result['symmetry_check']['common_prime_factors'] = {
                'a_factors': list(a_factors),
                'b_factors': list(b_factors),
                'common': list(common_factors)
            }

            # Symmetry is maintained if:
            # 1. Sum has prime factorization, AND
            # 2. Operands share some prime structure
            maintains = (len(sum_factors) > 0 and len(common_factors) > 0)

        elif operation == '×':
            # For multiplication: check if there's a corresponding additive structure
            product = a * b

            # Check 1: Can the product be represented as sum of primes?
            # Try to find Goldbach-like representation (for even products)
            if product > 2 and product % 2 == 0:
                verified, pair = self.goldbach_verifier.verify_single(product)
                result['symmetry_check']['product_as_sum'] = {
                    'value': product,
                    'has_goldbach_pair': verified,
                    'pair': pair if verified else None
                }
            else:
                result['symmetry_check']['product_as_sum'] = {
                    'value': product,
                    'has_goldbach_pair': False,
                    'pair': None
                }

            # Check 2: Are the operands prime? (atomic units)
            a_is_prime = is_prime(a)
            b_is_prime = is_prime(b)
            result['symmetry_check']['operands_prime'] = {
                'a_is_prime': a_is_prime,
                'b_is_prime': b_is_prime
            }

            # Symmetry is maintained if:
            # 1. Product can be represented as sum of primes (for even products), OR
            # 2. Operands are prime atoms
            maintains = (
                (result['symmetry_check']['product_as_sum']['has_goldbach_pair']) or
                (a_is_prime and b_is_prime)
            )

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        result['maintains_symmetry'] = maintains

        if not maintains:
            result['violation_type'] = 'symmetry'
            self.symmetry_violations.append(result)

        return maintains, result

    def run_completeness_test_suite(self, num_tests: int = 10000) -> Dict:
        """Test Axiom 2 with random numbers"""
        print(f"Running Completeness Test ({num_tests} random numbers)...")

        start_time = time.time()
        test_results = {
            'total_tests': num_tests,
            'completeness_violations': 0,
            'numbers_without_representation': [],
            'execution_time': 0
        }

        for i in range(num_tests):
            # Generate random number (positive and negative)
            n = random.randint(-self.max_test_value, self.max_test_value)

            has_representation, details = self.check_completeness(abs(n))

            if not has_representation:
                test_results['completeness_violations'] += 1
                test_results['numbers_without_representation'].append({
                    'number': n,
                    'details': details
                })

            # Log every 1000th operation
            if i % 1000 == 0:
                self.operation_log.append({
                    'test_type': 'completeness',
                    'iteration': i,
                    'timestamp': time.time(),
                    'violations_so_far': test_results['completeness_violations']
                })

        end_time = time.time()
        test_results['execution_time'] = end_time - start_time

        return test_results

    def run_symmetry_test_suite(self, num_tests: int = 10000) -> Dict:
        """Test Axiom 3 with random operations"""
        print(f"Running Symmetry Test ({num_tests} random operations)...")

        start_time = time.time()
        test_results = {
            'total_tests': num_tests,
            'symmetry_violations': 0,
            'failed_operations': [],
            'execution_time': 0
        }

        operations = ['+', '×']

        for i in range(num_tests):
            # Generate random operands
            a = random.randint(1, self.max_test_value // 10)  # Keep smaller for multiplication
            b = random.randint(1, self.max_test_value // 10)
            op = random.choice(operations)

            maintains_symmetry, details = self.check_symmetry(a, b, op)

            if not maintains_symmetry:
                test_results['symmetry_violations'] += 1
                test_results['failed_operations'].append(details)

            # Log every 1000th operation
            if i % 1000 == 0:
                self.operation_log.append({
                    'test_type': 'symmetry',
                    'iteration': i,
                    'timestamp': time.time(),
                    'violations_so_far': test_results['symmetry_violations']
                })

        end_time = time.time()
        test_results['execution_time'] = end_time - start_time

        return test_results

    def generate_axiom_report(self) -> str:
        """Generate comprehensive axiom enforcement report"""
        completeness_results = self.run_completeness_test_suite(10000)
        symmetry_results = self.run_symmetry_test_suite(10000)

        report = [
            "=" * 70,
            "AXIOM ENFORCEMENT ENGINE REPORT",
            "=" * 70,
            f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Max Test Value: {self.max_test_value}",
            "",
            "AXIOM 2 - COMPLETENESS:",
            f"  Tests Run: {completeness_results['total_tests']}",
            f"  Violations Found: {completeness_results['completeness_violations']}",
            f"  Execution Time: {completeness_results['execution_time']:.4f}s",
            "",
            "AXIOM 3 - SYMMETRY:",
            f"  Tests Run: {symmetry_results['total_tests']}",
            f"  Violations Found: {symmetry_results['symmetry_violations']}",
            f"  Execution Time: {symmetry_results['execution_time']:.4f}s",
            ""
        ]

        # Show sample violations if any
        if completeness_results['completeness_violations'] > 0:
            report.append("COMPLETENESS VIOLATIONS (first 5):")
            for i, violation in enumerate(completeness_results['numbers_without_representation'][:5]):
                report.append(f"  {i+1}. Number {violation['number']} has no representation")

        if symmetry_results['symmetry_violations'] > 0:
            report.append("\nSYMMETRY VIOLATIONS (first 5):")
            for i, violation in enumerate(symmetry_results['failed_operations'][:5]):
                report.append(f"  {i+1}. Operation {violation['operation']} breaks symmetry")

        # Performance check
        total_time = (completeness_results['execution_time'] +
                     symmetry_results['execution_time'])
        avg_time_per_test = total_time / 20000  # 10000 + 10000 tests

        report.append(f"\nPERFORMANCE SUMMARY:")
        report.append(f"  Total Execution Time: {total_time:.4f}s")
        report.append(f"  Average Time per Test: {avg_time_per_test * 1000:.6f}ms")

        if avg_time_per_test < 0.001:  # < 1ms per test
            report.append("  Performance: PASS")
        else:
            report.append("  Performance: FAIL")

        report.append("=" * 70)
        return "\n".join(report)

    def save_axiom_data(self, filename: str = "axiom_enforcement_data.json"):
        """Save all axiom enforcement data"""
        data = {
            'metadata': {
                'max_test_value': self.max_test_value,
                'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'axioms_enforced': ['Axiom 2 (Completeness)', 'Axiom 3 (Symmetry)']
            },
            'completeness_violations': self.completeness_violations[:100],  # Limit to 100
            'symmetry_violations': self.symmetry_violations[:100],  # Limit to 100
            'operation_log': self.operation_log,
            'checksums': {
                'completeness_violations_hash': hashlib.sha256(
                    str(self.completeness_violations).encode()
                ).hexdigest(),
                'symmetry_violations_hash': hashlib.sha256(
                    str(self.symmetry_violations).encode()
                ).hexdigest()
            }
        }

        import json
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

def run_axiom_tests():
    """Main test function for axiom enforcement"""
    print("Starting Axiom Enforcement Tests...")

    enforcer = AxiomEnforcer(max_test_value=10000)
    report = enforcer.generate_axiom_report()
    print(report)

    # Save results
    enforcer.save_axiom_data("/Users/jamienucho/demerzel/results/axiom_enforcement.json")

    # Check for violations
    completeness_results = enforcer.run_completeness_test_suite(1000)  # Quick check
    symmetry_results = enforcer.run_symmetry_test_suite(1000)  # Quick check

    if completeness_results['completeness_violations'] > 0:
        print(f"WARNING: {completeness_results['completeness_violations']} completeness violations found")

    if symmetry_results['symmetry_violations'] > 0:
        print(f"WARNING: {symmetry_results['symmetry_violations']} symmetry violations found")

    # Performance check
    total_time = (completeness_results['execution_time'] +
                 symmetry_results['execution_time'])
    avg_time = total_time / 2000

    if avg_time < 0.001:  # < 1ms per test
        print(f"Performance PASS: {avg_time * 1000:.6f} ms per test")
        return True
    else:
        print(f"Performance FAIL: {avg_time * 1000:.6f} ms per test")
        return False

if __name__ == "__main__":
    success = run_axiom_tests()
    if success:
        print("\nAxiom enforcement tests completed successfully.")
        exit(0)
    else:
        print("\nAxiom enforcement tests failed.")
        exit(1)
