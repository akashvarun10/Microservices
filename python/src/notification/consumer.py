import sys
import os
import time
from kafka import KafkaConsumer
from send import email

def main():
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        os.environ.get("MP3_QUEUE"),
        bootstrap_servers='kafka:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=False,  # Disable auto commit to manually handle message acknowledgements
        value_deserializer=lambda v: v.decode('utf-8')
    )

    print("Waiting for messages. To exit press CTRL+C")

    for message in consumer:
        err = email.notification(message.value)
        if err:
            consumer.seek(message.partition, message.offset)  # Manually seek to the message offset
        else:
            consumer.commit()  # Commit the message offset

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
