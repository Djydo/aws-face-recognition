import boto3
from botocore.exceptions import ClientError
"""
References: 
 1) https://docs.aws.amazon.com/rekognition/latest/dg/collections.html
 2) Shreya Beloor: https://radiostud.io/machine-learning-use-case-facial-recognition-using-amazon-rekognition/     
"""


class FaceRecognition:
    # aws_access_key_id = 'AKI**************I'
    # aws_secret_access_key = 'a*******************************z'
    # region_name = 'us-east-1'

    def __init__(self, collection_id, bucket):
        self.collection_id = collection_id
        self.s3_bucket = bucket
        self.status_code = None
        self.connection = boto3.client('rekognition')

        # hard-code credentials check below (security-wise: not safe)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variables
        # self.connection = boto3.client('rekognition', aws_access_key_id=self.aws_access_key_id,
        #                                aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

    def create_collection(self):
        try:
            print('creating collection ...')
            response = self.connection.create_collection(CollectionId=self.collection_id)
            self.status_code = response['StatusCode']
            print('{} created {}.'.format(self.response_msg(), self.collection_id))
        except ClientError as err:
            err_msg = err.response['Error']['Code']
            self.status_code = err_msg
            print('Sorry, collection {}.'.format(self.response_msg()))

    def delete_collection(self):
        try:
            print('deleting collection ...')
            response = self.connection.delete_collection(CollectionId=self.collection_id)
            self.status_code = response['StatusCode']
            print('{} deleted {}.'.format(self.response_msg(), self.collection_id))
        except ClientError as err:
            err_msg = err.response['Error']['Code']
            self.status_code = err_msg
            print('Sorry, deletion failed! Error {}.'.format(self.response_msg()))

    def index_object(self, img_object):
        try:
            response = self.connection.index_faces(CollectionId=self.collection_id,
                                                   Image={'S3Object': {'Bucket': self.s3_bucket, 'Name': img_object}},
                                                   ExternalImageId=img_object,
                                                   MaxFaces=1,
                                                   QualityFilter="AUTO",
                                                   DetectionAttributes=['ALL'])
            return response['FaceRecords']
        except ClientError as e:
            print("Boto3 Error: " + e.response['Error']['Code'])

    def search_faces_by_image(self, img_object):
        try:
            threshold = 70
            max_faces = 2
            print('searching collection by face images ... ')
            response = self.connection.search_faces_by_image(CollectionId=self.collection_id,
                                                             Image={'S3Object': {'Bucket': self.s3_bucket, 'Name': img_object}},
                                                             FaceMatchThreshold=threshold,
                                                             MaxFaces=max_faces)
            matching_faces = response['FaceMatches']
            for match in matching_faces:
                print('The face ' + img_object + 'matches ' + match['Face']['ExternalImageId'])
                print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                print('Confidence: ' + "{:.2f}".format(match['Confidence']) + "%")
        except ClientError as err:
            err_msg = err.response['Error']['Code']
            self.status_code = err_msg
            print('Error: ' + self.response_msg() + '.')

    def response_msg(self):
        if self.status_code == 'ResourceAlreadyExistsException':
            return "already exists"
        elif self.status_code == 200:
            return "successfully"
        else:
            return self.status_code

    def main(self):
        """
        1) set up connection to resource: s3 bucket
        2) get list of objects in the s3 bucket
             - caveat: method (list_objects_v2) only lists first 1000 objects
             - consider using pagination to handle more than 1000 objects
        3) index image objects in the bucket

        :return:
        """
        resource = boto3.client('s3')
        for item in resource.list_objects_v2(Bucket=self.s3_bucket)['Contents']:
            item_name = item['Key']
            file_ext = ('.jpg', '.png')
            if item_name.endswith(file_ext):
                print('indexing {} ...'.format(item_name))
                self.index_object(item_name)
        print('Done! Finished indexing.')


if __name__ == "__main__":
    collection_ID = 'face-collection'
    s3_bucket_name = 'aws-face-recognition2019'

    face_rec = FaceRecognition(collection_ID, s3_bucket_name)
    face_rec.create_collection()
    face_rec.main()
    # face_rec.delete_collection()
