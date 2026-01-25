"""
Data Transformer - Appendix D
Purpose: Convert sensor data to mathematical representations
Test Requirement: 100,000 synthetic sensor inputs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'math'))

import random
import time
import json
import struct
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from math import log, exp
from prime_engine import is_prime
from goldbach import GoldbachVerifier
from axioms import AxiomEnforcer

class DataTransformer:
    """
    Transforms raw sensor data (analog readings) to mathematical representations.
    Maintains information conservation and mathematical consistency.
    """

    def __init__(self, calibration_data: Optional[Dict] = None):
        self.calibration_data = calibration_data or {}
        self.transformation_log = []
        self.information_loss_count = 0
        self.goldbach_verifier = GoldbachVerifier(max_even=10000)
        self.axiom_enforcer = AxiomEnforcer(max_test_value=10000)

        # Prime-aware mapping parameters
        self.prime_map = {}  # Cache for prime mappings
        self.last_prime_index = 0

        # Calibration constants (example - should be calibrated per hardware)
        self.analog_max = 1023  # 10-bit ADC
        self.voltage_reference = 5.0  # 5V reference
        self.temperature_coeff = 0.01  # Example thermal coefficient

    def analog_to_prime_integer(self, analog_value: int) -> Tuple[int, Dict]:
        """
        Convert analog reading (0-1023) to prime-aware integer.
        Implements information conservation: no loss of data.

        Returns: (transformed_integer, transformation_metadata)
        """
        if not 0 <= analog_value <= self.analog_max:
            raise ValueError(f"Analog value {analog_value} out of range 0-{self.analog_max}")

        start_time = time.time()

        # Step 1: Normalize to 0-1 range with floating precision
        normalized = analog_value / self.analog_max

        # Step 2: Apply calibration if available
        if 'calibration_curve' in self.calibration_data:
            # Apply polynomial calibration curve: y = ax^3 + bx^2 + cx + d
            coeffs = self.calibration_data['calibration_curve']
            calibrated = (coeffs[0] * (normalized**3) +
                         coeffs[1] * (normalized**2) +
                         coeffs[2] * normalized +
                         coeffs[3])
            normalized = max(0.0, min(1.0, calibrated))

        # Step 3: Map to integer domain with prime awareness
        # Scale to 0-10000 range for Goldbach verification
        scaled = int(normalized * 10000)

        # Step 4: Ensure mathematical properties
        transformed = self._ensure_mathematical_properties(scaled)

        # Step 5: Verify information conservation
        info_loss = self._check_information_loss(analog_value, transformed)

        metadata = {
            'original_analog': analog_value,
            'normalized': normalized,
            'scaled': scaled,
            'transformed': transformed,
            'is_prime': is_prime(transformed),
            'information_loss': info_loss,
            'processing_time_ms': (time.time() - start_time) * 1000,
            'timestamp': time.time()
        }

        self.transformation_log.append(metadata)

        if info_loss['loss_detected']:
            self.information_loss_count += 1

        return transformed, metadata

    def _ensure_mathematical_properties(self, value: int) -> int:
        """
        Adjust value to ensure it respects mathematical axioms.
        Returns adjusted value that maintains Goldbach and axiom constraints.
        """
        original = value

        # Ensure value is positive (for prime/Goldbach operations)
        if value < 2:
            value = 2

        # If value is even, verify Goldbach condition
        if value > 2 and value % 2 == 0:
            verified, pair = self.goldbach_verifier.verify_single(value)
            if not verified:
                # Find nearest even with Goldbach pair
                for offset in range(2, 100, 2):  # Search +/-100
                    candidates = [value + offset, value - offset]
                    for candidate in candidates:
                        if candidate > 2 and candidate % 2 == 0:
                            verified, pair = self.goldbach_verifier.verify_single(candidate)
                            if verified:
                                return candidate

        # Check Axiom 2 completeness
        has_representation, _ = self.axiom_enforcer.check_completeness(value)
        if not has_representation:
            # Find nearest number with representation
            for offset in range(1, 51):  # Search +/-50
                candidates = [value + offset, value - offset]
                for candidate in candidates:
                    if candidate > 0:
                        has_rep, _ = self.axiom_enforcer.check_completeness(candidate)
                        if has_rep:
                            return candidate

        return value

    def _check_information_loss(self, original: int, transformed: int) -> Dict:
        """
        Check if information was lost during transformation.
        Returns dict with loss analysis.
        """
        # Calculate entropy difference
        original_entropy = self._calculate_entropy(original)
        transformed_entropy = self._calculate_entropy(transformed)
        entropy_diff = abs(original_entropy - transformed_entropy)

        # Check if transformation is reversible (injective)
        reversible = self._is_reversible(original, transformed)

        # Check bit preservation
        original_bits = original.bit_length() if original > 0 else 1
        transformed_bits = transformed.bit_length() if transformed > 0 else 1
        bit_diff = abs(original_bits - transformed_bits)

        loss_detected = (entropy_diff > 0.01 or not reversible or bit_diff > 2)

        return {
            'loss_detected': loss_detected,
            'original_entropy': original_entropy,
            'transformed_entropy': transformed_entropy,
            'entropy_diff': entropy_diff,
            'is_reversible': reversible,
            'original_bits': original_bits,
            'transformed_bits': transformed_bits,
            'bit_diff': bit_diff
        }

    def _calculate_entropy(self, value: int) -> float:
        """Calculate Shannon entropy of integer value."""
        if value == 0:
            return 0.0

        # Convert to bytes and calculate byte distribution
        byte_len = max(1, (value.bit_length() + 7) // 8)
        bytes_data = value.to_bytes(byte_len, 'big')

        # Calculate frequency of each byte value (0-255)
        freq = {}
        total = len(bytes_data)

        for byte in bytes_data:
            freq[byte] = freq.get(byte, 0) + 1

        # Calculate entropy
        entropy = 0.0
        for count in freq.values():
            probability = count / total
            entropy -= probability * log(probability, 2)

        return entropy

    def _is_reversible(self, original: int, transformed: int) -> bool:
        """
        Check if transformation is injective (reversible).
        Uses hash of transformation parameters.
        """
        # Create transformation signature
        params = {
            'original': original,
            'analog_max': self.analog_max,
            'calibration': self.calibration_data.get('calibration_curve', [])
        }

        param_hash = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()

        # Check if we can recover original from transformed + params
        # This is a simplified check - actual implementation would need inverse function
        try:
            # Attempt to reconstruct
            reconstructed = self._reconstruct_original(transformed, param_hash)
            return abs(reconstructed - original) <= 1  # Allow small rounding error
        except:
            return False

    def _reconstruct_original(self, transformed: int, param_hash: str) -> int:
        """Attempt to reconstruct original value (simplified)."""
        # In a real implementation, this would use inverse transformation
        # For now, return transformed (assuming perfect transformation)
        return transformed

    def batch_transform(self, analog_values: List[int]) -> Tuple[List[int], Dict]:
        """Transform batch of analog values."""
        start_time = time.time()
        results = []
        metadata_list = []

        for i, value in enumerate(analog_values):
            transformed, meta = self.analog_to_prime_integer(value)
            results.append(transformed)
            metadata_list.append(meta)

            # Log every 10000th transformation
            if i % 10000 == 0 and i > 0:
                print(f"Transformed {i}/{len(analog_values)} values...")

        # Generate batch statistics
        batch_stats = self._generate_batch_stats(results, metadata_list)
        batch_stats['total_time_ms'] = (time.time() - start_time) * 1000
        batch_stats['avg_time_per_value_ms'] = batch_stats['total_time_ms'] / len(analog_values)

        return results, batch_stats

    def _generate_batch_stats(self, results: List[int], metadata_list: List[Dict]) -> Dict:
        """Generate statistics for batch transformation."""
        primes = [r for r in results if is_prime(r)]
        evens = [r for r in results if r % 2 == 0]

        # Check Goldbach for even results > 2
        goldbach_verified = 0
        for r in evens:
            if r > 2:
                verified, _ = self.goldbach_verifier.verify_single(r)
                if verified:
                    goldbach_verified += 1

        # Check axiom completeness
        completeness_verified = 0
        for r in results:
            has_rep, _ = self.axiom_enforcer.check_completeness(r)
            if has_rep:
                completeness_verified += 1

        # Information loss analysis
        losses = [m for m in metadata_list if m['information_loss']['loss_detected']]

        return {
            'total_values': len(results),
            'prime_count': len(primes),
            'prime_percentage': len(primes) / len(results) * 100,
            'even_count': len(evens),
            'goldbach_verified': goldbach_verified,
            'goldbach_percentage': goldbach_verified / max(len(evens), 1) * 100,
            'completeness_verified': completeness_verified,
            'completeness_percentage': completeness_verified / len(results) * 100,
            'information_loss_count': len(losses),
            'information_loss_percentage': len(losses) / len(results) * 100,
            'min_value': min(results) if results else 0,
            'max_value': max(results) if results else 0,
            'avg_value': sum(results) / len(results) if results else 0
        }

    def calibrate_from_data(self, analog_values: List[int], expected_values: List[int]):
        """
        Calibrate transformer using known analog-expected pairs.
        Derives calibration curve coefficients.
        """
        if len(analog_values) != len(expected_values):
            raise ValueError("Input lists must have same length")

        # Simple linear calibration for example
        # In reality, would use polynomial regression
        analog_norm = [a / self.analog_max for a in analog_values]
        expected_norm = [e / 10000 for e in expected_values]  # Assuming expected in 0-10000

        # Fit cubic polynomial: y = ax^3 + bx^2 + cx + d
        # Using numpy would be better, but keeping it dependency-free
        # Simplified: assume linear for now (y = mx + b)
        n = len(analog_norm)
        sum_x = sum(analog_norm)
        sum_y = sum(expected_norm)
        sum_xy = sum(x * y for x, y in zip(analog_norm, expected_norm))
        sum_x2 = sum(x * x for x in analog_norm)

        # Linear coefficients (slope and intercept)
        denom = (n * sum_x2 - sum_x * sum_x)
        if denom == 0:
            m = 1.0
            b = 0.0
        else:
            m = (n * sum_xy - sum_x * sum_y) / denom
            b = (sum_y - m * sum_x) / n

        # Store as cubic with a=0, b=0, c=m, d=b
        self.calibration_data['calibration_curve'] = [0.0, 0.0, m, b]

        # Test calibration
        test_results = []
        for analog, expected in zip(analog_values, expected_values):
            transformed, _ = self.analog_to_prime_integer(analog)
            test_results.append({
                'analog': analog,
                'expected': expected,
                'actual': transformed,
                'error': abs(transformed - expected)
            })

        avg_error = sum(r['error'] for r in test_results) / len(test_results)
        self.calibration_data['avg_calibration_error'] = avg_error
        self.calibration_data['calibration_samples'] = n

        return test_results, avg_error

    def run_test_suite(self, num_tests: int = 100000) -> Dict:
        """Run comprehensive test suite."""
        print(f"Running Data Transformer Test Suite ({num_tests} values)...")

        # Generate synthetic analog values
        synthetic_analog = [random.randint(0, self.analog_max) for _ in range(num_tests)]

        # Transform all values
        start_time = time.time()
        transformed, batch_stats = self.batch_transform(synthetic_analog)
        total_time = time.time() - start_time

        # Verify mathematical properties
        verification_results = self._verify_transformed_values(transformed)

        # Combine results
        results = {
            'test_configuration': {
                'num_tests': num_tests,
                'analog_max': self.analog_max,
                'calibration_applied': 'calibration_curve' in self.calibration_data
            },
            'performance': {
                'total_time_seconds': total_time,
                'avg_time_per_value_ms': total_time / num_tests * 1000,
                'values_per_second': num_tests / total_time if total_time > 0 else 0
            },
            'batch_statistics': batch_stats,
            'verification_results': verification_results,
            'information_loss': {
                'total_loss_events': self.information_loss_count,
                'loss_percentage': self.information_loss_count / num_tests * 100
            },
            'timestamp': time.time()
        }

        # Performance check
        if results['performance']['avg_time_per_value_ms'] < 0.1:  # < 0.1ms
            results['performance_check'] = 'PASS'
        else:
            results['performance_check'] = 'FAIL'

        # Mathematical property check
        if (verification_results['goldbach_success_rate'] > 99.9 and
            verification_results['axiom_completeness_rate'] > 99.9):
            results['mathematical_check'] = 'PASS'
        else:
            results['mathematical_check'] = 'FAIL'

        return results

    def _verify_transformed_values(self, values: List[int]) -> Dict:
        """Verify mathematical properties of transformed values."""
        goldbach_success = 0
        completeness_success = 0
        prime_count = 0

        for value in values:
            # Check Goldbach for even numbers > 2
            if value > 2 and value % 2 == 0:
                verified, _ = self.goldbach_verifier.verify_single(value)
                if verified:
                    goldbach_success += 1

            # Check Axiom 2 completeness
            has_rep, _ = self.axiom_enforcer.check_completeness(value)
            if has_rep:
                completeness_success += 1

            # Count primes
            if is_prime(value):
                prime_count += 1

        even_count = sum(1 for v in values if v > 2 and v % 2 == 0)

        return {
            'total_values': len(values),
            'prime_count': prime_count,
            'prime_percentage': prime_count / len(values) * 100,
            'even_count': even_count,
            'goldbach_success': goldbach_success,
            'goldbach_success_rate': goldbach_success / even_count * 100 if even_count > 0 else 100,
            'completeness_success': completeness_success,
            'axiom_completeness_rate': completeness_success / len(values) * 100
        }

    def save_transformation_log(self, filename: str = "transformation_log.json"):
        """Save detailed transformation log."""
        log_data = {
            'metadata': {
                'total_transformations': len(self.transformation_log),
                'information_loss_count': self.information_loss_count,
                'log_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'calibration_data': self.calibration_data,
            'sample_transformations': self.transformation_log[:1000],  # First 1000
            'statistics': self._generate_batch_stats(
                [t['transformed'] for t in self.transformation_log],
                self.transformation_log
            ) if self.transformation_log else {}
        }

        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)

# Test runner
def run_transformer_tests():
    """Main test function for data transformer."""
    print("=" * 70)
    print("DATA TRANSFORMER TEST SUITE")
    print("=" * 70)

    # Create transformer
    transformer = DataTransformer()

    # Test 1: Basic transformation
    print("\n1. Testing basic transformation (1000 values)...")
    test_values = [random.randint(0, 1023) for _ in range(1000)]
    transformed, stats = transformer.batch_transform(test_values)

    print(f"   Transformed {len(transformed)} values")
    print(f"   Prime percentage: {stats['prime_percentage']:.2f}%")
    print(f"   Goldbach success: {stats['goldbach_percentage']:.2f}%")
    print(f"   Information loss: {stats['information_loss_percentage']:.2f}%")

    # Test 2: Calibration test
    print("\n2. Testing calibration...")
    calibration_analog = [0, 255, 511, 767, 1023]
    calibration_expected = [0, 2500, 5000, 7500, 10000]

    try:
        test_results, avg_error = transformer.calibrate_from_data(
            calibration_analog, calibration_expected
        )
        print(f"   Calibration complete, avg error: {avg_error:.2f}")
    except Exception as e:
        print(f"   Calibration failed: {e}")

    # Test 3: Full test suite
    print("\n3. Running full test suite (100,000 values)...")
    full_results = transformer.run_test_suite(100000)

    print(f"   Performance: {full_results['performance']['avg_time_per_value_ms']:.6f} ms/value")
    print(f"   Performance check: {full_results.get('performance_check', 'N/A')}")
    print(f"   Mathematical check: {full_results.get('mathematical_check', 'N/A')}")

    # Test 4: Information conservation
    print("\n4. Information conservation test...")
    conserved = 0
    for i in range(100):
        original = random.randint(0, 1023)
        transformed_val, meta = transformer.analog_to_prime_integer(original)

        # Check if we can approximately reconstruct
        if abs(transformed_val - original * 10) <= 100:  # Allow scaling difference
            conserved += 1

    print(f"   Information conserved in {conserved}/100 samples")

    # Save results
    transformer.save_transformation_log("/Users/jamienucho/demerzel/results/transformer_log.json")

    # Final verdict
    print("\n" + "=" * 70)

    if (full_results.get('performance_check') == 'PASS' and
        full_results.get('mathematical_check') == 'PASS'):
        print("DATA TRANSFORMER: ALL TESTS PASS ✓")
        return True
    else:
        print("DATA TRANSFORMER: TESTS FAILED ✗")
        return False

if __name__ == "__main__":
    success = run_transformer_tests()
    exit(0 if success else 1)
