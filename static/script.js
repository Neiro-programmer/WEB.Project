function init() {
    let map = new ymaps.Map('map-test', {
        center: [43.58085614796446, 39.71855162229773],
        zoom: 16,
        controls: ['routePanelControl']
    });

    let control = map.controls.get('routePanelControl');
    let city = 'Сочи';

    // let location = ymaps.geolocation.get();

    // location.then(function (res) {
    //     let locationText = res.geoObjects.get(0).properties.get('text');
    //     console.log(locationText)
    // });

    const options = {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    };

    function success(pos) {
        const crd = pos.coords;

        console.log(`Latitude : ${crd.latitude}`);
        console.log(`Longitude: ${crd.longitude}`);


        let reverseGeocoder = ymaps.geocode([crd.latitude, crd.longitude]);
        let locationText = null;
        reverseGeocoder.then(function (res) {
            locationText = res.geoObjects.get(0).properties.get('text')
            console.log(locationText)

            control.routePanel.state.set({
                type: 'masstransit',
                fromEnabled: false,
                from: locationText,
                toEnabled: true,
                to: `${city}, Невский проспект 146`,
            });
        });

        console.log(locationText)


        control.routePanel.state.set({
            type: 'masstransit',
            fromEnabled: true,
            toEnabled: false,
            to: `${city}, роз 48`
        });
    }

    ymaps.ready(init);
