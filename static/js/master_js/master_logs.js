$(document).ready(function() {
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/logs", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            { "data": "action" }, 
            { "data": "description" },
            { "data": "date" }
        ]
    });
});