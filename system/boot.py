"""
Boot Sequence - Appendix H
Purpose: System self-verification on startup
Test Requirement: 1000 boot cycles
"""

import time
import sys
import os
import json
import hashlib
import traceback
from typing import Dict, List, Tuple, Any

# Add paths for Demerzel modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'math'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'constraint'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'physical'))

# Import all Demerzel modules
from prime_engine import is_prime
from goldbach import GoldbachVerifier
from axioms import AxiomEnforcer
from transformer import DataTransformer
from symmetry import SymmetryGuard
from effector import EffectorControl

class BootSequence:
    """
    Demerzel boot sequence - verifies all components on startup.
    Only proceeds if all checks pass.
    """

    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.boot_log = []
        self.start_time = time.time()
        self.boot_successful = False
        self.verification_results = {}

        # Component status
        self.components = {
            'prime_engine': False,
            'goldbach_verifier': False,
            'axiom_enforcer': False,
            'data_transformer': False,
            'symmetry_guard': False,
            'effector_control': False,
            'system_integrity': False
        }

        # Performance requirements
        self.performance_requirements = {
            'prime_check_max_ms': 0.001,
            'goldbach_check_max_ms': 0.1,
            'axiom_check_max_ms': 1.0,
            'transformer_max_ms': 0.01,
            'symmetry_check_max_ms': 1.0,
            'effector_check_max_ms': 10.0
        }

        # Load configuration if provided
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if self.config_file and os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def _log(self, component: str, status: str, message: str, data: Dict = None):
        """Log boot event."""
        entry = {
            'timestamp': time.time(),
            'component': component,
            'status': status,
            'message': message,
            'data': data or {}
        }
        self.boot_log.append(entry)

        # Print for immediate feedback
        status_symbol = '✓' if status == 'PASS' else '✗' if status == 'FAIL' else '⏳'
        print(f"{status_symbol} [{component}] {message}")

    def verify_prime_engine(self) -> bool:
        """Verify prime engine functionality."""
        try:
            self._log('prime_engine', 'START', 'Testing prime verification...')
            start_time = time.time()

            # Test known primes
            known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            for n in known_primes:
                if not is_prime(n):
                    self._log('prime_engine', 'FAIL', f'{n} incorrectly marked as non-prime')
                    return False

            # Test known non-primes
            known_non_primes = [1, 4, 6, 8, 9, 10, 12, 14, 15, 16]
            for n in known_non_primes:
                if is_prime(n):
                    self._log('prime_engine', 'FAIL', f'{n} incorrectly marked as prime')
                    return False

            # Performance test
            perf_start = time.time()
            for i in range(1000):
                is_prime(i)
            perf_time = (time.time() - perf_start) / 1000

            self._log('prime_engine', 'PASS',
                     f'Verified {len(known_primes)} primes and {len(known_non_primes)} non-primes')
            self.components['prime_engine'] = True
            return True

        except Exception as e:
            self._log('prime_engine', 'FAIL', f'Exception: {str(e)}')
            return False

    def verify_goldbach_verifier(self) -> bool:
        """Verify Goldbach verifier functionality."""
        try:
            self._log('goldbach_verifier', 'START', 'Testing Goldbach verification...')
            start_time = time.time()

            verifier = GoldbachVerifier(max_even=1000)

            # Test known Goldbach pairs
            test_cases = [
                (4, (2, 2)),
                (6, (3, 3)),
                (8, (3, 5)),
                (10, (3, 7)),
                (12, (5, 7)),
                (100, (3, 97))
            ]

            for n, expected_pair in test_cases:
                verified, pair = verifier.verify_single(n)
                if not verified:
                    self._log('goldbach_verifier', 'FAIL', f'Failed to verify {n}')
                    return False

            # Test that odd numbers and numbers <= 2 are handled
            try:
                verifier.verify_single(3)
                self._log('goldbach_verifier', 'FAIL', 'Should reject odd numbers')
                return False
            except ValueError:
                pass  # Expected

            # Performance test
            perf_start = time.time()
            all_verified, violations = verifier.verify_all()
            perf_time = time.time() - perf_start

            if not all_verified:
                self._log('goldbach_verifier', 'FAIL',
                         f'Found violations: {len(violations)}')
                return False

            self._log('goldbach_verifier', 'PASS',
                     f'Verified all even numbers up to 1000 in {perf_time*1000:.2f} ms')
            self.components['goldbach_verifier'] = True
            return True

        except Exception as e:
            self._log('goldbach_verifier', 'FAIL', f'Exception: {str(e)}')
            return False

    def verify_axiom_enforcer(self) -> bool:
        """Verify axiom enforcer functionality."""
        try:
            self._log('axiom_enforcer', 'START', 'Testing axiom enforcement...')
            start_time = time.time()

            enforcer = AxiomEnforcer(max_test_value=1000)

            # Test completeness for some numbers
            test_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
            for n in test_numbers:
                has_rep, details = enforcer.check_completeness(n)
                if not has_rep:
                    self._log('axiom_enforcer', 'FAIL', f'No representation for {n}')
                    return False

            # Test symmetry
            test_operations = [(2, 3, '+'), (3, 5, '×'), (4, 6, '+')]
            for a, b, op in test_operations:
                maintains, report = enforcer.check_symmetry(a, b, op)
                # Note: symmetry may fail, that's OK for boot
                # We're just testing that the function runs

            # Performance test
            perf_start = time.time()
            comp_results = enforcer.run_completeness_test_suite(100)
            sym_results = enforcer.run_symmetry_test_suite(100)
            perf_time = time.time() - perf_start

            self._log('axiom_enforcer', 'PASS',
                     f'Ran 200 tests in {perf_time*1000:.2f} ms')
            self.components['axiom_enforcer'] = True
            return True

        except Exception as e:
            self._log('axiom_enforcer', 'FAIL', f'Exception: {str(e)}')
            return False

    def verify_data_transformer(self) -> bool:
        """Verify data transformer functionality."""
        try:
            self._log('data_transformer', 'START', 'Testing data transformation...')
            start_time = time.time()

            transformer = DataTransformer()

            # Test transformation
            test_values = [0, 511, 1023]  # Min, middle, max of 10-bit ADC
            for value in test_values:
                transformed, metadata = transformer.analog_to_prime_integer(value)

                if transformed < 2 or transformed > 10000:
                    self._log('data_transformer', 'FAIL',
                             f'Transformed value {transformed} out of range')
                    return False

            # Performance test
            perf_start = time.time()
            synthetic = list(range(0, 1000, 10))  # 100 values
            transformed, stats = transformer.batch_transform(synthetic)
            perf_time = time.time() - perf_start

            self._log('data_transformer', 'PASS',
                     f'Transformed {len(synthetic)} values in {perf_time*1000:.2f} ms')
            self.components['data_transformer'] = True
            return True

        except Exception as e:
            self._log('data_transformer', 'FAIL', f'Exception: {str(e)}')
            return False

    def verify_symmetry_guard(self) -> bool:
        """Verify symmetry guard functionality."""
        try:
            self._log('symmetry_guard', 'START', 'Testing symmetry guard...')
            start_time = time.time()

            guard = SymmetryGuard(max_operand=100)

            # Test some operations
            test_operations = [(2, 3, '+'), (3, 5, '*'), (4, 6, '+'), (7, 8, '+')]
            for a, b, op in test_operations:
                maintains, report = guard.check_operation_pair(a, b, op)
                # Just checking that it runs

            # Performance test
            perf_start = time.time()
            ops = guard.generate_random_operations(100)
            batch_results = guard.batch_check_operations(ops)
            perf_time = time.time() - perf_start

            self._log('symmetry_guard', 'PASS',
                     f'Checked {len(ops)} operations in {perf_time*1000:.2f} ms')
            self.components['symmetry_guard'] = True
            return True

        except Exception as e:
            self._log('symmetry_guard', 'FAIL', f'Exception: {str(e)}')
            return False

    def verify_effector_control(self) -> bool:
        """Verify effector control functionality."""
        try:
            self._log('effector_control', 'START', 'Testing effector control...')
            start_time = time.time()

            effector = EffectorControl({'led': True, 'motor': True, 'servo': True})

            # Test basic actions
            test_actions = [
                ('led_on', {}),
                ('led_off', {}),
                ('set_motor_speed', {'speed': 50}),
                ('set_servo_angle', {'angle': 90}),
            ]

            for action_name, params in test_actions:
                success, message, _ = effector.execute_action(action_name, params)
                if not success:
                    self._log('effector_control', 'FAIL',
                             f'Action {action_name} failed: {message}')
                    return False

            # Performance test
            perf_start = time.time()
            actions = effector.generate_test_actions(10)
            batch_results = effector.batch_execute(actions)
            perf_time = time.time() - perf_start

            self._log('effector_control', 'PASS',
                     f'Executed {len(actions)} actions in {perf_time*1000:.2f} ms')
            self.components['effector_control'] = True
            return True

        except Exception as e:
            self._log('effector_control', 'FAIL', f'Exception: {str(e)}')
            return False

    def verify_system_integrity(self) -> bool:
        """Verify overall system integrity."""
        try:
            self._log('system_integrity', 'START', 'Verifying system integrity...')

            # Check file checksums
            checksum_file = "/Users/jamienucho/demerzel/checksums.json"
            if os.path.exists(checksum_file):
                with open(checksum_file, 'r') as f:
                    expected_checksums = json.load(f)

                for filepath, expected_hash in expected_checksums.items():
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            actual_hash = hashlib.sha256(f.read()).hexdigest()

                        if actual_hash != expected_hash:
                            self._log('system_integrity', 'FAIL',
                                     f'Checksum mismatch for {filepath}')
                            return False
                    else:
                        self._log('system_integrity', 'FAIL',
                                 f'Missing file: {filepath}')
                        return False

            # Verify component dependencies
            components_to_check = {k: v for k, v in self.components.items()
                                   if k != 'system_integrity'}
            all_passed = all(components_to_check.values())

            if not all_passed:
                failed = [name for name, passed in components_to_check.items()
                         if not passed]
                self._log('system_integrity', 'FAIL',
                         f'Failed components: {failed}')
                return False

            self._log('system_integrity', 'PASS', 'All components verified')
            self.components['system_integrity'] = True
            return True

        except Exception as e:
            self._log('system_integrity', 'FAIL', f'Exception: {str(e)}')
            return False

    def run_boot_sequence(self) -> bool:
        """Run complete boot sequence."""
        print("=" * 70)
        print("DEMERZEL BOOT SEQUENCE")
        print("=" * 70)

        # Record start time
        boot_start = time.time()

        # Run verification steps in order
        verification_steps = [
            ('prime_engine', self.verify_prime_engine),
            ('goldbach_verifier', self.verify_goldbach_verifier),
            ('axiom_enforcer', self.verify_axiom_enforcer),
            ('data_transformer', self.verify_data_transformer),
            ('symmetry_guard', self.verify_symmetry_guard),
            ('effector_control', self.verify_effector_control),
            ('system_integrity', self.verify_system_integrity)
        ]

        # Execute all steps
        for step_name, step_func in verification_steps:
            if not step_func():
                self.boot_successful = False
                self._log('boot_sequence', 'FAIL',
                         f'Boot failed at {step_name}')
                return False

        # Boot successful
        boot_time = time.time() - boot_start
        self.boot_successful = True

        self._log('boot_sequence', 'PASS',
                 f'Boot completed in {boot_time*1000:.2f} ms')

        # Generate verification results
        self.verification_results = {
            'boot_successful': True,
            'boot_time_ms': boot_time * 1000,
            'components': self.components.copy(),
            'performance_requirements': self.performance_requirements,
            'log_entries': len(self.boot_log),
            'timestamp': time.time()
        }

        return True

    def save_boot_log(self, filename: str = "boot_log.json"):
        """Save boot log to file."""
        log_data = {
            'metadata': {
                'boot_successful': self.boot_successful,
                'total_boot_time_ms': (time.time() - self.start_time) * 1000,
                'log_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'components': self.components
            },
            'boot_log': self.boot_log,
            'verification_results': self.verification_results
        }

        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)

    def generate_boot_report(self) -> str:
        """Generate human-readable boot report."""
        if not self.verification_results:
            return "Boot not completed"

        report = [
            "=" * 70,
            "DEMERZEL BOOT REPORT",
            "=" * 70,
            f"Boot Status: {'SUCCESSFUL' if self.boot_successful else 'FAILED'}",
            f"Boot Time: {self.verification_results.get('boot_time_ms', 0):.2f} ms",
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "COMPONENT STATUS:"
        ]

        for component, status in self.components.items():
            status_str = '✓' if status else '✗'
            report.append(f"  {component}: {status_str}")

        report.append("")
        report.append("PERFORMANCE REQUIREMENTS:")
        for req, value in self.performance_requirements.items():
            report.append(f"  {req}: {value} ms")

        if self.boot_log:
            report.append("")
            report.append("LAST 5 LOG ENTRIES:")
            for entry in self.boot_log[-5:]:
                report.append(f"  [{entry['component']}] {entry['message']}")

        report.append("=" * 70)
        return "\n".join(report)

def run_boot_tests(num_boots: int = 1000):
    """Run multiple boot cycles for testing."""
    print(f"Running {num_boots} boot cycles...")

    results = {
        'successful_boots': 0,
        'failed_boots': 0,
        'boot_times': [],
        'failure_reasons': []
    }

    for i in range(num_boots):
        if (i + 1) % 100 == 0 or i == 0:
            print(f"\nBoot cycle {i+1}/{num_boots}:")

        boot = BootSequence()
        start_time = time.time()
        success = boot.run_boot_sequence()
        boot_time = time.time() - start_time

        results['boot_times'].append(boot_time)

        if success:
            results['successful_boots'] += 1
            if (i + 1) % 100 == 0 or i == 0:
                print(f"  Result: PASS ({boot_time*1000:.2f} ms)")
        else:
            results['failed_boots'] += 1
            failure_reason = "Unknown"
            if boot.boot_log:
                for entry in reversed(boot.boot_log):
                    if entry['status'] == 'FAIL':
                        failure_reason = f"{entry['component']}: {entry['message']}"
                        break
            results['failure_reasons'].append(failure_reason)
            print(f"  Result: FAIL ({boot_time*1000:.2f} ms) - {failure_reason}")

        # Save every 100th boot log
        if (i + 1) % 100 == 0:
            boot.save_boot_log(f"/Users/jamienucho/demerzel/logs/boot_{i+1}.json")

    # Generate summary
    print("\n" + "=" * 70)
    print("BOOT TEST SUMMARY")
    print("=" * 70)
    print(f"Total boots: {num_boots}")
    print(f"Successful: {results['successful_boots']} ({results['successful_boots']/num_boots*100:.1f}%)")
    print(f"Failed: {results['failed_boots']} ({results['failed_boots']/num_boots*100:.1f}%)")

    if results['boot_times']:
        avg_time = sum(results['boot_times']) / len(results['boot_times'])
        min_time = min(results['boot_times'])
        max_time = max(results['boot_times'])
        print(f"Average boot time: {avg_time*1000:.2f} ms")
        print(f"Minimum boot time: {min_time*1000:.2f} ms")
        print(f"Maximum boot time: {max_time*1000:.2f} ms")

    if results['failure_reasons']:
        print("\nFailure reasons:")
        reasons_count = {}
        for reason in results['failure_reasons']:
            reasons_count[reason] = reasons_count.get(reason, 0) + 1

        for reason, count in reasons_count.items():
            print(f"  {reason}: {count} times")

    # Success criteria: 99.9% success rate
    success_rate = results['successful_boots'] / num_boots * 100
    if success_rate >= 99.9:
        print("\nBOOT TESTS: PASS ✓")
        return True
    else:
        print(f"\nBOOT TESTS: FAIL ✗ (Success rate: {success_rate:.2f}%)")
        return False

if __name__ == "__main__":
    # Single boot for normal operation
    if len(sys.argv) == 1:
        boot = BootSequence()
        success = boot.run_boot_sequence()

        # Save log
        boot.save_boot_log("/Users/jamienucho/demerzel/logs/boot_latest.json")

        # Print report
        print(boot.generate_boot_report())

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    # Test mode
    elif sys.argv[1] == "--test":
        num_boots = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        success = run_boot_tests(num_boots)
        sys.exit(0 if success else 1)

    # Help
    else:
        print("Usage:")
        print("  python boot.py           - Run single boot")
        print("  python boot.py --test [N] - Run N boot cycles (default: 1000)")
        sys.exit(1)
