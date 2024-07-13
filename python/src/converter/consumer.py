import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3

def main():
    # Establish a connection to the MongoDB instance
    client = MongoClient("host.minikube.internal", 27017)
    db_videos = client.videos  # Access the videos database
    db_mp3s = client.mp3s  # Access the mp3s database
    
    # Initialize GridFS for both databases
    fs_videos = gridfs.GridFS(db_videos) 
    fs_mp3s = gridfs.GridFS(db_mp3s)  

    # Establishing a connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel() 

    # Define the callback function for processing messages
    def callback(ch, method, properties, body):
        # Convert video to mp3 and handle errors
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            # If an error occurs, send a negative acknowledgment
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # If successful, send a positive acknowledgment
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # Start consuming messages from the queue specified by the VIDEO_QUEUE environment variable
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    # Enter a consuming loop
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Handle graceful exit upon KeyboardInterrupt (CTRL+C)
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)