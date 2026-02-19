"""
Generate synthetic transaction data with known money muling patterns for testing
"""
import pandas as pd
from datetime import datetime, timedelta
import random
import uuid

def generate_test_transactions():
    transactions = []
    tx_id = 1
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    
    # Pattern 1: Circular Fund Routing (Cycle of 3)
    # A → B → C → A
    cycle_3_accounts = ['ACC_001', 'ACC_002', 'ACC_003']
    for i in range(3):
        sender = cycle_3_accounts[i]
        receiver = cycle_3_accounts[(i + 1) % 3]
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': sender,
            'receiver_id': receiver,
            'amount': random.uniform(5000, 15000),
            'timestamp': (base_time + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Pattern 2: Circular Fund Routing (Cycle of 4)
    # D → E → F → G → D
    cycle_4_accounts = ['ACC_011', 'ACC_012', 'ACC_013', 'ACC_014']
    for i in range(4):
        sender = cycle_4_accounts[i]
        receiver = cycle_4_accounts[(i + 1) % 4]
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': sender,
            'receiver_id': receiver,
            'amount': random.uniform(8000, 20000),
            'timestamp': (base_time + timedelta(hours=5 + i)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Pattern 3: Smurfing - Fan-In (Multiple senders → 1 aggregator)
    aggregator = 'ACC_101'
    senders = [f'ACC_{200 + i}' for i in range(15)]
    
    for i, sender in enumerate(senders):
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': sender,
            'receiver_id': aggregator,
            'amount': random.uniform(2000, 5000),
            'timestamp': (base_time + timedelta(hours=10, minutes=i*20)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Pattern 4: Smurfing - Fan-Out (1 disperser → Multiple receivers)
    disperser = 'ACC_301'
    receivers = [f'ACC_{400 + i}' for i in range(12)]
    
    for i, receiver in enumerate(receivers):
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': disperser,
            'receiver_id': receiver,
            'amount': random.uniform(3000, 7000),
            'timestamp': (base_time + timedelta(hours=15, minutes=i*15)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Pattern 5: Layered Shell Network (Chain of 4 hops through low-activity accounts)
    # Source → Shell1 → Shell2 → Shell3 → Destination
    shell_chain = ['ACC_501', 'ACC_502', 'ACC_503', 'ACC_504', 'ACC_505']
    
    for i in range(len(shell_chain) - 1):
        sender = shell_chain[i]
        receiver = shell_chain[i + 1]
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': sender,
            'receiver_id': receiver,
            'amount': random.uniform(10000, 25000),
            'timestamp': (base_time + timedelta(hours=20 + i)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Make shell accounts have only 2-3 transactions (low activity)
    # Add one more transaction for each shell account (except endpoints)
    for i in range(1, len(shell_chain) - 1):
        shell_account = shell_chain[i]
        # Add a small outgoing transaction to a random account
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': shell_account,
            'receiver_id': f'ACC_{600 + i}',
            'amount': random.uniform(100, 500),
            'timestamp': (base_time + timedelta(hours=25 + i)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Pattern 6: Another cycle of 5 for variety
    cycle_5_accounts = ['ACC_701', 'ACC_702', 'ACC_703', 'ACC_704', 'ACC_705']
    for i in range(5):
        sender = cycle_5_accounts[i]
        receiver = cycle_5_accounts[(i + 1) % 5]
        transactions.append({
            'transaction_id': f'TX_{tx_id:06d}',
            'sender_id': sender,
            'receiver_id': receiver,
            'amount': random.uniform(6000, 18000),
            'timestamp': (base_time + timedelta(hours=30 + i)).strftime('%Y-%m-%d %H:%M:%S')
        })
        tx_id += 1
    
    # Add some legitimate transactions (non-suspicious)
    legitimate_accounts = [f'ACC_{800 + i}' for i in range(20)]
    
    for i in range(30):
        sender = random.choice(legitimate_accounts)
        receiver = random.choice(legitimate_accounts)
        if sender != receiver:
            transactions.append({
                'transaction_id': f'TX_{tx_id:06d}',
                'sender_id': sender,
                'receiver_id': receiver,
                'amount': random.uniform(100, 1000),
                'timestamp': (base_time + timedelta(hours=random.randint(0, 48), 
                                                   minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
            })
            tx_id += 1
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Save to CSV
    output_file = 'backend/test_transactions.csv'
    df.to_csv(output_file, index=False)
    print(f"Generated {len(transactions)} transactions")
    print(f"Saved to: {output_file}")
    print("\nExpected patterns:")
    print("1. Cycle of 3: ACC_001, ACC_002, ACC_003")
    print("2. Cycle of 4: ACC_011, ACC_012, ACC_013, ACC_014")
    print("3. Fan-In (15 senders → ACC_101)")
    print("4. Fan-Out (ACC_301 → 12 receivers)")
    print("5. Shell Chain: ACC_501 → ACC_502 → ACC_503 → ACC_504 → ACC_505")
    print("6. Cycle of 5: ACC_701, ACC_702, ACC_703, ACC_704, ACC_705")
    print("\nTotal expected fraud rings: 6")
    
    return df

if __name__ == "__main__":
    generate_test_transactions()
