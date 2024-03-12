import hashlib
import time

# test values
new_proof = 1
previous_proof = 2

start_time = time.time()



while True:
    # operation 
    data = str((new_proof ** 3) + (previous_proof ** 3) - (previous_proof ** 2))


    hash_operation = hashlib.sha256(data.encode()).hexdigest()
    
    # ierations 
    for _ in range(1000):
        hash_operation = hashlib.sha256(hash_operation.encode()).hexdigest()

    current_time = time.time() - start_time

    print(f"tiempo corriedno: {current_time} + {hash_operation}")

    #check for the condition
    if hash_operation[:1] == "0":
        print("Nonce encontrado:", new_proof)
        print("Tiempo transcurrido:", time.time() - start_time, "segundos")
        break
    else:
        new_proof += 1
