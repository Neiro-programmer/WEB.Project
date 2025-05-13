function init() {
    let map = new ymaps.Map('map-test', {
        center: [43.58085614796446, 39.71855162229773],
        zoom: 16
    });

    let placemark = new ymaps.Placemark([43.58085614796446, 39.71855162229773], {}, {

    })

    map.geoObjects.add(placemark);
}


ymaps.ready(init);
