$(document).ready(function() {
    var table = $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/amplifier_tracking_todo", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            { "data": "name" }, 
            { "data": "category" },
            { "data": "color" },
            { "data": "palga" }, 
            { "data": "mami_serial" },
            { "data": "description" },
            { "data": "test_type"},
            { "data": "interval"},
            { "data": "results"},
            { "data": "last_updated"},
            { "data": "days_passed"}
        ]
    });
});