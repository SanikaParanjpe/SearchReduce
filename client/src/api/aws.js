import AWS from 'aws-sdk';

const S3_BUCKET ='eccproject-iub';
const REGION ='us-east-1';

AWS.config.update({
    accessKeyId: 'my-access-key',
    secretAccessKey: 'my-secret-key'
});

const myBucket = new AWS.S3({
    params: { Bucket: S3_BUCKET},
    region: REGION,
});
 
export async function uploadFile (file) {
    const fileName = (new Date().getTime()) + "_" + file.name;

    const params = {
        ACL: 'public-read',
        Body: file,
        Bucket: S3_BUCKET,
        Key: fileName,
        ContentDisposition:'inline',
        ContentType: file.type,
    };

    const response = await myBucket.upload(params).promise();

    try {

        console.log("response: ", response)
        return {
            success: true,
            fileName: fileName
        }
    } catch (error) {
        return { 
            success: false,
            error: error,
        }
    }
}