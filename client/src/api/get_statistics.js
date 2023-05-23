import { baseUrl } from "./base";


export async function getStatistics(name) {
    const response = await fetch(baseUrl + '/get_statistics', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const json = await response.json();
    if (json.success) {
        return json.data;
    }
    else {
        alert(json.data);
    }
}