# Analyzes HLL accuracy with chaotic data (random UUIDs in random batches).

import redis
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import random
import uuid

# --- CONFIGURATION ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
HLL_KEY = "hll_chaotic_test"
TARGET_ELEMENTS = 1_000_000
MIN_BATCH_SIZE = 500
MAX_BATCH_SIZE = 15_000

def run_chaotic_test():
    """Runs the HLL analysis with chaotic data insertion."""
    
    # --- 1. CONNECT TO REDIS ---
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print(f"✅ Successfully connected to Redis ({REDIS_HOST}:{REDIS_PORT})")
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        return

    # --- 2. SETUP TEST ---
    x_steps, real_counts, estimated_counts, percentage_errors = [], [], [], []
    total_elements_added = 0
    r.delete(HLL_KEY)

    print("\n--- Starting Chaotic HLL Accuracy Test ---\n")
    print(f"{'Batch Size':<15} | {'Total Items':<15} | {'HLL Estimate':<15} | {'Error (%)':<15}")
    print("-" * 70)
    
    start_time = time.time()

    # --- 3. RUN TEST AND COLLECT DATA ---
    while total_elements_added < TARGET_ELEMENTS:
        batch_size = random.randint(MIN_BATCH_SIZE, MAX_BATCH_SIZE)
        batch = [str(uuid.uuid4()) for _ in range(batch_size)]
        
        r.pfadd(HLL_KEY, *batch)
        total_elements_added += batch_size

        hll_estimate = r.pfcount(HLL_KEY)
        absolute_error = abs(hll_estimate - total_elements_added)
        percentage_error = (absolute_error / total_elements_added) * 100

        x_steps.append(total_elements_added)
        real_counts.append(total_elements_added)
        estimated_counts.append(hll_estimate)
        percentage_errors.append(percentage_error)
        print(f"{batch_size:<15,} | {total_elements_added:<15,} | {hll_estimate:<15,} | {percentage_error:<15.4f}")

    end_time = time.time()
    print(f"\n--- Test complete in {end_time - start_time:.2f}s. Generating charts... ---")

    # --- 4. GENERATE CHARTS ---
    plt.figure("Chaotic Test - Accuracy", figsize=(12, 7))
    plt.plot(x_steps, real_counts, label='Real Count', color='blue', linestyle='--')
    plt.plot(x_steps, estimated_counts, label='HLL Estimate', color='red', marker='o', markersize=4, linestyle='None')
    plt.title('HLL Accuracy with Chaotic Insertion', fontsize=16)
    plt.xlabel('Number of Unique Items', fontsize=12)
    plt.ylabel('Cardinality Count', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    ax1 = plt.gca()
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    plt.savefig('chaotic_accuracy_chart.png')

    plt.figure("Chaotic Test - Error Trend", figsize=(12, 7))
    plt.plot(x_steps, percentage_errors, label='Measured Error', color='green', marker='.')
    plt.axhline(y=0.81, color='orange', linestyle='--', label='Theoretical Standard Error (0.81%)')
    plt.title('HLL Percentage Error with Chaotic Insertion', fontsize=16)
    plt.xlabel('Number of Unique Items', fontsize=12)
    plt.ylabel('Relative Error (%)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    ax2 = plt.gca()
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter())
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig('chaotic_error_chart.png')
    
    print("✅ Charts saved to 'chaotic_accuracy_chart.png' and 'chaotic_error_chart.png'")
    plt.show()

    r.delete(HLL_KEY)

if __name__ == "__main__":
    run_chaotic_test()