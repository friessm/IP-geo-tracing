$(document).ready(function () {

    $('#hostnameForm').submit(function (event) {

        // Stops form from submitting normally
        event.preventDefault();

        var hostName = $('#hostname').val();

        // TODO: Ensure that double entries cannot be done. Meaning, that one request needs to be completed before the 
        // second one can be started, otherwise too many calls to ipinfo.io and the load time increases.

        // TODO: Implement proper error handling and use RESTful API responses (HTTP)

        // TODO: Fix: Error: There is already a source with this ID

        // TODO: Clear input field after output (ip address route) was displayed

        $.ajax({
            type: 'POST',
            url: '/hostname',
            dataType: 'json',
            data: {hostname: hostName},
            success: function(data) {
                
                var IPMeta = data
                
                map.addSource("IPGeo", {
                    "type": "geojson",
                        "data": IPMeta
                });
    
                map.addLayer({
                    "id": "GeoIPPoints",
                    "type": "circle",
                    "source": "IPGeo",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "blue",
                        "circle-opacity": 0.7
                    },
                    "filter": ["==", "$type", "Point"]
                });
                
                map.addLayer({
                    "id": "GeoIPLineStrig",
                    "type": "line",
                    "source": "IPGeo",
                    "paint": {
                        "line-color": "blue",
                        "line-width": 2
                    },
                    "filer": ["==", "$type", "LineString"]
                });
            },
            error: function() {
                console.log('Error.');
            }
        });
    });
});


