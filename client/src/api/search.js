import { baseUrl } from "./base";


export async function search(query) {
    const response = await fetch(baseUrl + '/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'search_string': query,
        }),
    });

    const json = await response.json();
    if (json.success) {
        return json.data;
    }
    else {
        alert(json.data);
    }
}