$(document).ready(function() {
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/client_users", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            { "data": "first_name" }, 
            { "data": "last_name" },
            { "data": "personal_id" }, 
            { "data": "email" },
            { "data": "palga" }, 
            { "data": "team" }
        ]
    });
});