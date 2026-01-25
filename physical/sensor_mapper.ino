/*
Sensor Mapper - Appendix F
Purpose: Convert voltage readings to prime-aware integers
Hardware: Arduino with 10-bit ADC
*/

// ===== CONFIGURATION =====
#define SERIAL_BAUD 115200
#define ADC_PIN A0
#define LED_PIN 13

// Mathematical constants
#define MAX_ANALOG 1023
#define MAX_INTEGER 10000
#define CALIBRATION_SAMPLES 100

// Prime verification memory (first 168 primes up to 997)
const unsigned int FIRST_168_PRIMES[] = {
  2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
  73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
  157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
  239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
  331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
  421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
  509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
  613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
  709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
  821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
  919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
};

#define PRIME_COUNT 168

// ===== MATHEMATICAL FUNCTIONS =====

// Check if number is prime (optimized for small numbers)
bool is_prime(unsigned int n) {
  if (n <= 1) return false;
  if (n <= 3) return true;
  if (n % 2 == 0 || n % 3 == 0) return false;

  for (unsigned int i = 5; i * i <= n; i += 6) {
    if (n % i == 0 || n % (i + 2) == 0) {
      return false;
    }
  }
  return true;
}

// Find nearest prime to a given number
unsigned int nearest_prime(unsigned int n) {
  if (n <= 2) return 2;

  // Check if already prime
  if (is_prime(n)) return n;

  // Search upwards and downwards
  for (unsigned int offset = 1; offset <= 100; offset++) {
    if (is_prime(n + offset)) return n + offset;
    if (n > offset && is_prime(n - offset)) return n - offset;
  }

  return 2;  // Fallback
}

// Check Goldbach condition for even number
bool has_goldbach_pair(unsigned int n) {
  if (n <= 2 || n % 2 != 0) return false;

  for (unsigned int p = 2; p <= n / 2; p++) {
    if (is_prime(p) && is_prime(n - p)) {
      return true;
    }
  }
  return false;
}

// Ensure mathematical properties
unsigned int ensure_mathematical_properties(unsigned int value) {
  unsigned int result = value;

  // Ensure positive
  if (result < 2) result = 2;

  // If even, check Goldbach
  if (result > 2 && result % 2 == 0) {
    if (!has_goldbach_pair(result)) {
      // Find nearest even with Goldbach pair
      for (unsigned int offset = 2; offset <= 100; offset += 2) {
        unsigned int candidate = result + offset;
        if (candidate <= MAX_INTEGER && has_goldbach_pair(candidate)) {
          return candidate;
        }
        if (result > offset) {
          candidate = result - offset;
          if (candidate > 2 && has_goldbach_pair(candidate)) {
            return candidate;
          }
        }
      }
    }
  }

  // Ensure has prime factorization representation
  unsigned int temp = result;
  bool has_factorization = false;

  // Check if divisible by any prime
  for (unsigned int i = 0; i < PRIME_COUNT && FIRST_168_PRIMES[i] * FIRST_168_PRIMES[i] <= temp; i++) {
    if (temp % FIRST_168_PRIMES[i] == 0) {
      has_factorization = true;
      break;
    }
  }

  if (!has_factorization && temp > 1) {
    // Number is prime itself - has factorization (itself)
    has_factorization = is_prime(temp);
  }

  return result;
}

// ===== SENSOR PROCESSING =====

// Read and transform sensor value
unsigned int read_and_transform() {
  // Read analog value (10-bit, 0-1023)
  unsigned int analog_value = analogRead(ADC_PIN);

  // Normalize to 0-1.0 range
  float normalized = (float)analog_value / MAX_ANALOG;

  // Scale to integer range
  unsigned int scaled = (unsigned int)(normalized * MAX_INTEGER);

  // Ensure in range
  if (scaled > MAX_INTEGER) scaled = MAX_INTEGER;

  // Apply mathematical constraints
  unsigned int transformed = ensure_mathematical_properties(scaled);

  return transformed;
}

// ===== COMMUNICATION PROTOCOL =====

// Send data in structured format
void send_transformed_data(unsigned int transformed, unsigned int analog) {
  Serial.print("DATA:");
  Serial.print(millis());
  Serial.print(",");
  Serial.print(analog);
  Serial.print(",");
  Serial.print(transformed);
  Serial.print(",");
  Serial.print(is_prime(transformed) ? "PRIME" : "COMPOSITE");
  Serial.print(",");
  Serial.print((transformed % 2 == 0) ? "EVEN" : "ODD");
  Serial.println();
}

// Send heartbeat
void send_heartbeat() {
  Serial.print("HEARTBEAT:");
  Serial.println(millis());
}

// Send error
void send_error(const char* message) {
  Serial.print("ERROR:");
  Serial.println(message);
}

// ===== CALIBRATION =====

// Run calibration sequence
void run_calibration() {
  Serial.println("CALIBRATION_START");

  unsigned int samples[CALIBRATION_SAMPLES];
  unsigned long sum = 0;

  for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
    samples[i] = analogRead(ADC_PIN);
    sum += samples[i];
    delay(10);
  }

  unsigned int avg = sum / CALIBRATION_SAMPLES;

  Serial.print("CALIBRATION_AVG:");
  Serial.println(avg);
  Serial.println("CALIBRATION_END");
}

// ===== SETUP =====

void setup() {
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(ADC_PIN, INPUT);

  // Initialize serial
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    ; // Wait for serial port
  }

  // Blink LED to indicate startup
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }

  // Send startup message
  Serial.println("DEMERZEL_SENSOR_MAPPER_START");
  Serial.print("FIRMWARE_VERSION:");
  Serial.println("1.0");
  Serial.print("MAX_INTEGER:");
  Serial.println(MAX_INTEGER);
  Serial.print("PRIME_COUNT:");
  Serial.println(PRIME_COUNT);

  // Run self-test
  run_self_test();
}

// ===== SELF-TEST =====

void run_self_test() {
  Serial.println("SELF_TEST_START");

  // Test prime function
  unsigned int test_primes[] = {2, 3, 5, 7, 11, 13};
  unsigned int test_non_primes[] = {1, 4, 6, 8, 9, 10};

  bool prime_test_pass = true;
  for (unsigned int i = 0; i < 6; i++) {
    if (!is_prime(test_primes[i])) {
      prime_test_pass = false;
      break;
    }
  }
  for (unsigned int i = 0; i < 6; i++) {
    if (is_prime(test_non_primes[i])) {
      prime_test_pass = false;
      break;
    }
  }

  // Test Goldbach
  bool goldbach_test_pass = true;
  unsigned int goldbach_tests[] = {4, 6, 8, 10, 12, 100};
  for (unsigned int i = 0; i < 6; i++) {
    if (!has_goldbach_pair(goldbach_tests[i])) {
      goldbach_test_pass = false;
      break;
    }
  }

  // Test mathematical properties
  bool math_test_pass = true;
  unsigned int math_tests[] = {1, 2, 3, 4, 100, 101};
  for (unsigned int i = 0; i < 6; i++) {
    unsigned int transformed = ensure_mathematical_properties(math_tests[i]);
    if (transformed < 2) {
      math_test_pass = false;
      break;
    }
  }

  // Send results
  Serial.print("PRIME_TEST:");
  Serial.println(prime_test_pass ? "PASS" : "FAIL");
  Serial.print("GOLDBACH_TEST:");
  Serial.println(goldbach_test_pass ? "PASS" : "FAIL");
  Serial.print("MATH_TEST:");
  Serial.println(math_test_pass ? "PASS" : "FAIL");

  if (prime_test_pass && goldbach_test_pass && math_test_pass) {
    Serial.println("SELF_TEST:PASS");
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
  } else {
    Serial.println("SELF_TEST:FAIL");
    // Blink error pattern
    for (int i = 0; i < 10; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
      delay(100);
    }
  }

  Serial.println("SELF_TEST_END");
}

// ===== MAIN LOOP =====

void loop() {
  static unsigned long last_heartbeat = 0;
  static unsigned long last_reading = 0;
  static unsigned int reading_count = 0;

  unsigned long current_time = millis();

  // Send heartbeat every 5 seconds
  if (current_time - last_heartbeat >= 5000) {
    send_heartbeat();
    last_heartbeat = current_time;
  }

  // Take reading every 100ms
  if (current_time - last_reading >= 100) {
    // Read analog value
    unsigned int analog_value = analogRead(ADC_PIN);

    // Transform with mathematical constraints
    unsigned int transformed = read_and_transform();

    // Send data
    send_transformed_data(transformed, analog_value);

    // Update counters
    last_reading = current_time;
    reading_count++;

    // Blink LED every 10 readings
    if (reading_count % 10 == 0) {
      digitalWrite(LED_PIN, HIGH);
      delay(10);
      digitalWrite(LED_PIN, LOW);
    }
  }

  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "CALIBRATE") {
      run_calibration();
    } else if (command == "SELFTEST") {
      run_self_test();
    } else if (command == "STATUS") {
      Serial.print("STATUS:READY|READINGS:");
      Serial.print(reading_count);
      Serial.print("|TIME:");
      Serial.println(millis());
    } else if (command == "RESET") {
      Serial.println("RESETTING");
      reading_count = 0;
      last_heartbeat = millis();
      last_reading = millis();
    } else if (command.startsWith("TEST_PRIME:")) {
      unsigned int test_num = command.substring(11).toInt();
      bool result = is_prime(test_num);
      Serial.print("PRIME_RESULT:");
      Serial.print(test_num);
      Serial.print(":");
      Serial.println(result ? "PRIME" : "NOT_PRIME");
    } else {
      Serial.print("UNKNOWN_COMMAND:");
      Serial.println(command);
    }
  }

  // Small delay to prevent watchdog issues
  delay(1);
}
