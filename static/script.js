ymaps.ready(function () {

    let myMap = new ymaps.Map('map-test', {
        center: [43.58104455459508, 39.71904255493954],
        zoom: 15,
        controls: ['routePanelControl']
    });

    let control = myMap.controls.get('routePanelControl');

    control.routePanel.state.set({
        type: 'masstransit',
        fromEnabled: true,
        toEnabled: false,
        to: document.getElementById("location").innerHTML
    });
});