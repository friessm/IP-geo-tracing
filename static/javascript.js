$(document).ready(function () {

    $('#domainNameForm').submit(function (event) {

        // Stops form from submitting normally
        event.preventDefault();

        var domainName = $('#domainName').val().toLowerCase();

        $.ajax({
            type: 'POST',
            url: '/domain_name',
            dataType: 'json',
            data: {domainName: domainName},
            success: function(data, textStatus, jqXHR) {
                
                // Do something with them. Log them?
                console.log(textStatus);
                console.log(jqXHR);

                var IPMeta = data

                // Remove source and layers from pervious requests, if needed
                if (map.getSource("IPGeo")) {
                    map.removeLayer("GeoIPPoints");
                    map.removeLayer("GeoIPLineStrig");
                    map.removeSource("IPGeo");
                }

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

                // Empty html form input field
                $('#domainNameForm')[0].reset()

                // Create a popup, but don't add it to the map yet
                var popup = new mapboxgl.Popup({
                    closeButton: false,
                    closeOnClick: false,
                    className: 'popup'
                })

                map.on('mouseenter', 'GeoIPPoints', function (event) {
                    
                    // Change the cursor style as a UI indicator.
                    map.getCanvas().style.cursor = 'pointer';

                    // Get coordinates and properties for the hovered over point
                    var coodinates = event.features[0].geometry.coordinates.slice();
                    var properties = event.features[0].properties
                    
                    // Create html table
                    table = '<table><tr><th>Key</th><th>Value</th></tr>';                   
                    for (const [key, value] of Object.entries(properties)) {
                        table += '<tr><td>' + key + ': ' + '</td>';
                        table += '<td>' + value + '</td></tr>';
                    }
                    table += '</table>';

                    // Populate the popup
                    popup.setLngLat(coodinates)
                        .setHTML(table)
                        .addTo(map)
                })

                map.on('mouseleave', 'GeoIPPoints', function () {
                    map.getCanvas().style.cursor = '';
                    popup.remove();
                });

            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#error').html(errorThrown + ': Try again').fadeIn().delay(2000).fadeOut()
                $('#domainNameForm')[0].reset()
            }
        });
    });
});