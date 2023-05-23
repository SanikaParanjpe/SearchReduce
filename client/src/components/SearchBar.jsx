import { useEffect } from 'react';
import { useState } from 'react';
import { search } from '../api/search';
import './Style.css';

export function SearchBar({onSearchResults}) {
    const [query, setQuery] = useState("");

    async function getSearch() {
        if (!query) return;
        const response = await search(query);
        if (response) {
            const docs = [];
            response.forEach(doc => {
                const splits = doc.split(".");
                const ext = splits.pop();
                const fileName = splits.join();
                docs.push({
                    name: fileName,
                    extension: ext,
                })
            });
            onSearchResults(docs);
        }
    }

    return (
        <div className="searchbar-container">
            <input className="searchbar-input" onChange={(e) => setQuery(e.target.value)} type="text" placeholder='Search document here' />
            <div className="searchbar-button" onClick={getSearch}>Search</div>
        </div>
    );
}