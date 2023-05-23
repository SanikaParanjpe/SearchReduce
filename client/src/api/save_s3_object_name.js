import { baseUrl } from "./base";


export async function saveS3ObjectName(name) {
    const response = await fetch(baseUrl + '/save_s3_object_name', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            's3_object_name': name,
        }),
    });

    const json = await response.json();
    if (json.success) {
        return json.data;
    }
}