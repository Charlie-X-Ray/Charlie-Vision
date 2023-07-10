from google.cloud import storage

def authenticate_implicit_with_adc(project_id='charlie-x-ray', bucket_name="charlie-x-ray.appspot.com"):
  ORIGINAL_PREFIX = '/original/'
  LEARN_PREFIX = '/learn/'
  BROWSE_PREFIX = '/browse/'
  storage_client = storage.Client(project=project_id)
  buckets = storage_client.list_buckets()
  print("Buckets:")
  for bucket in buckets:
    print(bucket.name)
  print("Listed all storage buckets.")

  bucket = storage_client.bucket(bucket_name)
  


if __name__ == "__main__":
  authenticate_implicit_with_adc()

